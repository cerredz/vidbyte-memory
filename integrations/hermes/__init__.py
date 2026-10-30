"""Hermes Agent plugin for vidbyte-memory: the turn-end gate.

Hermes fires ``pre_verify`` when the agent is about to finish a turn in which write_file or patch
changed files. This plugin then runs the project's own ``scripts/guard.py``, the script the Claude Code
Stop hook runs, and when the guard answers ``{"decision": "block", "reason": ...}`` it returns
``{"action": "continue", "message": reason}``: Hermes appends the message as a user turn and runs the
loop again. Hermes allows ``agent.max_verify_nudges`` such continues per turn (default 3); guard.py
allows 5 blocking rounds per session and then lets the turn end.

A project without ``memory/MAP.md`` and ``scripts/guard.py`` has no memory to guard, so the hook
returns None. Any failure (no interpreter, timeout, unreadable output) also returns None: the gate
fails open, as Hermes does with a hook that times out. Standard library only.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional

logger = logging.getLogger(__name__)

HERMES_HOOK_TIMEOUT = 30.0  # plugins.hook_callback_timeout default; Hermes abandons a slower hook
UNBOUNDED_GUARD_TIMEOUT = 180.0  # the Claude Code Stop hook's timeout, used when Hermes sets no limit


def _session_cwd() -> Optional[Path]:
    """The session's working directory as Hermes resolves it, else this process's cwd."""
    try:
        from agent.runtime_cwd import resolve_agent_cwd  # public Hermes API; absent outside Hermes

        return Path(resolve_agent_cwd())
    except Exception:
        pass
    try:
        return Path(os.getcwd())
    except OSError:
        return None


def project_root(changed_paths: Iterable[str] = ()) -> Optional[Path]:
    """Nearest folder with memory/MAP.md and scripts/guard.py, upward from the session cwd and then
    from each edited file (absolute paths only), so the gate still finds the project when the plugin
    runs in a separate plugin host whose cwd is not the session's."""
    starts: List[Optional[Path]] = [_session_cwd()]
    starts += [Path(p).parent for p in changed_paths if isinstance(p, str) and os.path.isabs(p)]
    for start in starts:
        if start is None:
            continue
        try:
            start = start.resolve()
        except OSError:
            continue
        for folder in (start, *start.parents):
            if (folder / "memory" / "MAP.md").is_file() and (folder / "scripts" / "guard.py").is_file():
                return folder
    return None


def project_python(root: Path) -> str:
    """The interpreter guard.py runs under, which is also the one it runs pytest with: the project's
    virtualenv, else python on PATH (what the Claude Code hook runs), else Hermes's own interpreter,
    which usually has no pytest."""
    for rel in (".venv/Scripts/python.exe", ".venv/bin/python", "venv/Scripts/python.exe", "venv/bin/python"):
        candidate = root / rel
        if candidate.is_file():
            return str(candidate)
    for name in ("python", "python3") if os.name == "nt" else ("python3", "python"):
        found = shutil.which(name)
        if found:
            return found
    return sys.executable


def guard_timeout() -> float:
    """Seconds guard.py may run: just under Hermes's hook timeout, so the plugin stops the guard and
    its pytest child itself instead of Hermes abandoning the hook with them still running."""
    try:
        from hermes_cli.config import load_config_readonly  # public Hermes API; absent outside Hermes

        raw = ((load_config_readonly() or {}).get("plugins") or {}).get("hook_callback_timeout")
        hook = HERMES_HOOK_TIMEOUT if raw is None else float(raw)
    except Exception:
        hook = HERMES_HOOK_TIMEOUT
    if hook < 0:
        hook = HERMES_HOOK_TIMEOUT  # Hermes treats a negative value as the default
    if hook == 0:
        return UNBOUNDED_GUARD_TIMEOUT  # 0 disables Hermes's limit
    return max(1.0, min(hook, 600.0) - 3.0)


def _stop(proc: subprocess.Popen) -> None:
    """Kill guard.py and the pytest it started."""
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, timeout=10)
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except Exception:
        pass
    try:
        proc.kill()
        proc.communicate(timeout=5)
    except Exception:
        pass


def run_guard(root: Path, session_id: str, timeout: float) -> dict:
    """guard.py's JSON verdict for *root*, or {} when it is silent, fails or runs out of time."""
    payload = json.dumps({"hook_event_name": "Stop", "session_id": session_id, "cwd": str(root)})
    # guard.py reads CLAUDE_PROJECT_DIR before the payload cwd: pin it to this project, so a value
    # inherited from an outer Claude Code session cannot point the guard at another repo.
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
    # Hermes runs from its own venv, and on Windows that venv's launcher exports PYTHONHOME (its base
    # interpreter). Inherited by the project's Python, it loads Hermes's stdlib and dies before the guard
    # runs, so the gate would fail open. The project's interpreter finds its own home: drop the binding.
    for name in ("PYTHONHOME", "__PYVENV_LAUNCHER__"):
        env.pop(name, None)
    try:
        proc = subprocess.Popen(
            [project_python(root), str(root / "scripts" / "guard.py"), "--format", "claude"],
            cwd=str(root), env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", start_new_session=os.name != "nt",
        )
    except OSError as exc:
        logger.warning("vidbyte-memory: could not start scripts/guard.py: %s", exc)
        return {}
    try:
        out, _err = proc.communicate(payload, timeout=timeout)
    except subprocess.TimeoutExpired:
        _stop(proc)
        logger.warning("vidbyte-memory: scripts/guard.py ran past %.0fs; letting the turn end", timeout)
        return {}
    for line in reversed((out or "").splitlines()):
        try:
            verdict = json.loads(line)
        except ValueError:
            continue
        if isinstance(verdict, dict):
            return verdict
    return {}


def pre_verify(session_id: str = "", changed_paths: Optional[list] = None, **_kwargs) -> Optional[dict]:
    """Keep the turn going while guard.py reports an unmet guarantee."""
    root = project_root(changed_paths or [])
    if root is None:
        return None
    verdict = run_guard(root, session_id or "hermes", guard_timeout())
    reason = verdict.get("reason")
    if verdict.get("decision") == "block" and isinstance(reason, str) and reason.strip():
        return {"action": "continue", "message": reason.strip()}
    if verdict.get("systemMessage"):  # guard gave up after its round cap: the turn ends unfinished
        logger.warning("vidbyte-memory: %s", verdict["systemMessage"])
    return None


def register(ctx) -> None:
    """Hermes entry point."""
    ctx.register_hook("pre_verify", pre_verify)
