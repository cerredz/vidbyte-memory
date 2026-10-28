"""Stop hook: block the end of a turn while a guarantee is unmet.

Checks, in order: the test suite passes (G-001), no feedback is pending (G-003), and nothing in the
repo is uncommitted or unpushed (G-004). When a check fails it prints {"decision": "block", "reason": ...}
so Claude Code keeps the turn going, up to MAX_ROUNDS times in a row within one session; after that it lets
the turn end and reports the unmet guarantees in a systemMessage, so a check that cannot pass does not hold
the session forever. The round counter lives in .claude/.guard_state.json with the session id that owns it,
so a new session starts at round 1.

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
    status = run(["git", "status", "--porcelain"]).stdout.strip()
    if status:
        return "G-004: changes are uncommitted. Run `python scripts/footprint.py --commit --title \"<request>\"`; it appends the run-log line, commits everything and pushes."
    upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if upstream.returncode != 0:
        return None
    ahead = run(["git", "rev-list", "--count", "@{u}..HEAD"]).stdout.strip()
    if ahead and ahead != "0":
        return f"G-004: {ahead} commit(s) not pushed. Run `git push`."
    return None


def load_rounds(session: str) -> int:
    """Rounds already spent in this session; a different session id in the state file means zero."""
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        return int(state.get("rounds", 0)) if state.get("session") == session else 0
    except (OSError, ValueError, AttributeError):
        return 0


def save_rounds(session: str, rounds: int) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"session": session, "rounds": rounds}), encoding="utf-8")


def read_payload() -> dict:
    """The hook JSON from stdin when the hook runs under Claude Code; empty when run by hand."""
    if sys.stdin.isatty():
        return {}
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}
    return payload if isinstance(payload, dict) else {}


def main() -> int:
    session = str(read_payload().get("session_id", "manual"))
    problems = [p for p in (check_tests(), check_pending_feedback(), check_committed()) if p]
    if not problems:
        save_rounds(session, 0)
        return 0
    rounds = load_rounds(session) + 1
    save_rounds(session, rounds)
    reason = "Unmet guarantees before ending this request:\n\n" + "\n\n".join(problems)
    if rounds <= MAX_ROUNDS:
        print(json.dumps({"decision": "block", "reason": f"{reason}\n\n(guard round {rounds} of {MAX_ROUNDS})"}))
        return 0
    save_rounds(session, 0)
    print(json.dumps({"systemMessage": f"guard gave up after {MAX_ROUNDS} rounds; the request is NOT finished:\n{reason}"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
