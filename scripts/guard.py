"""Stop hook: block the end of a turn while a guarantee is unmet.

Checks, in order: the test suite passes (G-001), no feedback is pending (G-003), and no change under
memory/, facts/, tests/, verifiers/ or AGENTS.md is uncommitted or unpushed (G-004). When a check fails it
prints {"decision": "block", "reason": ...} so Claude Code keeps the turn going, up to MAX_ROUNDS times in
a row; after that it lets the turn end and reports the unmet guarantees in a systemMessage, so a check
that cannot pass does not hold the session forever.

Usage: python scripts/guard.py      (reads the hook JSON on stdin when present; works without it)
Standard library only.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".claude" / ".guard_state.json"
MAX_ROUNDS = 5
WATCHED = ["memory", "facts", "tests", "verifiers", "AGENTS.md"]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def check_tests() -> str | None:
    result = run([sys.executable, "-m", "pytest", "-q", "tests"])
    if result.returncode == 0:
        return None
    tail = "\n".join((result.stdout or result.stderr).strip().splitlines()[-15:])
    return f"G-001: tests fail. Fix the artifact or the entry, never the test.\n{tail}"


def check_pending_feedback() -> str | None:
    log = ROOT / "memory" / "feedback-log.md"
    if not log.exists():
        return None
    pending = [line for line in log.read_text(encoding="utf-8").splitlines() if line.startswith("disposition: pending")]
    if not pending:
        return None
    return f"G-003: {len(pending)} feedback entries still have `disposition: pending`. Finish skills/handle-feedback."


def check_committed() -> str | None:
    if run(["git", "rev-parse", "--is-inside-work-tree"]).returncode != 0:
        return None
    status = run(["git", "status", "--porcelain", "--", *WATCHED]).stdout.strip()
    if status:
        return "G-004: memory changes are uncommitted. Append the run-log line and run `python scripts/footprint.py --commit --title \"<request>\"`."
    upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if upstream.returncode != 0:
        return None
    ahead = run(["git", "rev-list", "--count", "@{u}..HEAD"]).stdout.strip()
    if ahead and ahead != "0":
        return f"G-004: {ahead} commit(s) not pushed. Run `git push`."
    return None


def load_rounds() -> int:
    try:
        return int(json.loads(STATE.read_text(encoding="utf-8")).get("rounds", 0))
    except (OSError, ValueError):
        return 0


def save_rounds(rounds: int) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"rounds": rounds}), encoding="utf-8")


def main() -> int:
    if not sys.stdin.isatty():
        try:
            json.loads(sys.stdin.read() or "{}")  # the hook payload; read so the pipe closes cleanly
        except ValueError:
            pass
    problems = [p for p in (check_tests(), check_pending_feedback(), check_committed()) if p]
    if not problems:
        save_rounds(0)
        return 0
    rounds = load_rounds() + 1
    save_rounds(rounds)
    reason = "Unmet guarantees before ending this request:\n\n" + "\n\n".join(problems)
    if rounds <= MAX_ROUNDS:
        print(json.dumps({"decision": "block", "reason": f"{reason}\n\n(guard round {rounds} of {MAX_ROUNDS})"}))
        return 0
    save_rounds(0)
    print(json.dumps({"systemMessage": f"guard gave up after {MAX_ROUNDS} rounds; the request is NOT finished:\n{reason}"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
