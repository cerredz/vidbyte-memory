"""Stop hook: block the end of a turn while a guarantee is unmet.

Checks, in order: the test suite passes (G-001), no feedback is pending (G-003), and nothing in the
repo is uncommitted or unpushed (G-004). When a check fails it tells the harness to keep the turn going, up
to MAX_ROUNDS times in a row within one session; after that it lets the turn end and reports the unmet
guarantees, so a check that cannot pass does not hold the session forever. The round counter lives in
.claude/.guard_state.json with the session id that owns it, so a new session starts at round 1.

The guard checks the project the agent works in, not the folder this script sits in: the nearest folder with
memory/MAP.md, searched upward from CLAUDE_PROJECT_DIR, the hook's cwd, or the current directory. So the same
script runs from a task repo or from a plugin cache. A project without memory/MAP.md has no memory to guard,
and the guard does nothing there. When it runs from a plugin and the project's own .claude/settings.json
already runs scripts/guard.py, it also does nothing, so the checks never run twice.

Output formats (--format), one per hook protocol:
  claude       {"decision": "block", "reason": ...}     Claude Code, Codex, Copilot, Cursor, Devin CLI, Grok Build, Factory
  gemini       {"decision": "deny", "reason": ...}      Gemini CLI (AfterAgent)
  antigravity  {"decision": "continue", "reason": ...}  Antigravity (Stop in .agents/hooks.json)
  exit2        the reason on stderr, exit code 2        harnesses that read only the exit code

Usage: python scripts/guard.py [--format claude|gemini|antigravity|exit2]
       (reads the hook JSON on stdin when present; works without it)
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
MAX_ROUNDS = 5
DECISIONS = {"claude": "block", "gemini": "deny", "antigravity": "continue"}


def project_root(payload: dict) -> Path | None:
    """The nearest folder with memory/MAP.md, upward from the project dir the harness reports."""
    start = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()).resolve()
    for folder in (start, *start.parents):
        if (folder / "memory" / "MAP.md").is_file():
            return folder
    return None


def project_runs_its_own_guard(root: Path) -> bool:
    """True when this copy runs from elsewhere (a plugin) and the project already wires its own guard."""
    if root == HERE:
        return False
    try:
        return "scripts/guard.py" in (root / ".claude" / "settings.json").read_text(encoding="utf-8")
    except OSError:
        return False


def run(cmd: list[str], root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=root, text=True, capture_output=True)


def check_tests(root: Path) -> str | None:
    result = run([sys.executable, "-m", "pytest", "-q", "tests"], root)
    if result.returncode == 0:
        return None
    tail = "\n".join((result.stdout or result.stderr).strip().splitlines()[-15:])
    return f"G-001: tests fail. Fix the artifact or the entry, never the test.\n{tail}"


def check_pending_feedback(root: Path) -> str | None:
    log = root / "memory" / "feedback-log.md"
    if not log.exists():
        return None
    pending = [line for line in log.read_text(encoding="utf-8").splitlines() if line.startswith("disposition: pending")]
    if not pending:
        return None
    return f"G-003: {len(pending)} feedback entries still have `disposition: pending`. Finish skills/handle-feedback."


def check_committed(root: Path) -> str | None:
    if run(["git", "rev-parse", "--is-inside-work-tree"], root).returncode != 0:
        return None
    status = run(["git", "status", "--porcelain"], root).stdout.strip()
    if status:
        return "G-004: changes are uncommitted. Run `python scripts/footprint.py --commit --title \"<request>\"`; it appends the run-log line, commits everything and pushes."
    upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], root)
    if upstream.returncode != 0:
        return None
    ahead = run(["git", "rev-list", "--count", "@{u}..HEAD"], root).stdout.strip()
    if ahead and ahead != "0":
        return f"G-004: {ahead} commit(s) not pushed. Run `git push`."
    return None


def load_rounds(state: Path, session: str) -> int:
    """Rounds already spent in this session; a different session id in the state file means zero."""
    try:
        data = json.loads(state.read_text(encoding="utf-8"))
        return int(data.get("rounds", 0)) if data.get("session") == session else 0
    except (OSError, ValueError, AttributeError):
        return 0


def save_rounds(state: Path, session: str, rounds: int) -> None:
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"session": session, "rounds": rounds}), encoding="utf-8")


def read_payload() -> dict:
    """The hook JSON from stdin when a harness runs the hook; empty when run by hand."""
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}
    return payload if isinstance(payload, dict) else {}


def block(fmt: str, reason: str) -> int:
    if fmt == "exit2":
        print(reason, file=sys.stderr)
        return 2
    print(json.dumps({"decision": DECISIONS[fmt], "reason": reason}))
    return 0


def give_up(fmt: str, message: str) -> int:
    if fmt in ("claude", "gemini"):
        print(json.dumps({"systemMessage": message}))
    else:
        print(message, file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Block the end of a turn while a memory guarantee is unmet.")
    parser.add_argument("--format", choices=["claude", "gemini", "antigravity", "exit2"], default="claude")
    fmt = parser.parse_args(argv).format
    payload = read_payload()
    root = project_root(payload)
    if root is None or project_runs_its_own_guard(root):
        return 0
    session = str(payload.get("session_id") or payload.get("sessionId") or "manual")
    state = root / ".claude" / ".guard_state.json"
    problems = [p for p in (check_tests(root), check_pending_feedback(root), check_committed(root)) if p]
    if not problems:
        save_rounds(state, session, 0)
        return 0
    rounds = load_rounds(state, session) + 1
    save_rounds(state, session, rounds)
    reason = "Unmet guarantees before ending this request:\n\n" + "\n\n".join(problems)
    if rounds <= MAX_ROUNDS:
        return block(fmt, f"{reason}\n\n(guard round {rounds} of {MAX_ROUNDS})")
    save_rounds(state, session, 0)
    return give_up(fmt, f"guard gave up after {MAX_ROUNDS} rounds; the request is NOT finished:\n{reason}")


if __name__ == "__main__":
    sys.exit(main())
