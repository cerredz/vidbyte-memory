"""Install vidbyte-memory into an existing repo and wire the coding agents it finds.

Copies the memory protocol (AGENTS.md, CLAUDE.md, memory/, facts/, skills/, prompts/, verifiers/, tests/,
scripts/, .claude/agents/ and the skill mirrors) into the target repo without overwriting any file. An existing
AGENTS.md is folded into the new one's Task section, or kept as AGENTS.previous.md when it is long. Then, for
each agent found in the repo or on this machine, it writes that agent's Stop hook and skill folder, so the
memory guarantees are enforced there too. Every write is listed in .vidbyte-memory/install.json, and every
existing file it changes is first copied to <file>.vidbyte-memory-backup.

Source: the template this script sits in when that is the published template (a clone or a plugin cache), or
the GitHub tarball of --ref otherwise, so a task repo's own memory is never copied into another repo:
  curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -

Usage: python scripts/install.py [--target DIR] [--ref main] [--agents codex,gemini | --all] [--dry-run]
Standard library only.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

REPO = "cerredz/vidbyte-memory"
COPY_DIRS = ("memory", "facts", "skills", "prompts", "verifiers", "tests", "scripts", ".claude/agents", ".agents/skills", ".claude/skills")
SKIP_PARTS = {"__pycache__", ".pytest_cache"}
# Files the memory tests and hooks import by name: a different file at the same path breaks them.
CRITICAL = ("tests/helpers.py", "tests/test_memory_integrity.py", "scripts/guard.py", "scripts/footprint.py")
GUARD = "python scripts/guard.py"
MAX_AGENTS_LINES = 200
BACKUP_SUFFIX = ".vidbyte-memory-backup"

# Agents that need more than AGENTS.md, CLAUDE.md, .claude/ and the .agents/skills mirror, which every install
# writes. markers: paths in the repo; home: folders under ~; bins: commands on PATH.
AGENTS = {
    "codex": {"markers": [".codex"], "home": [".codex"], "bins": ["codex"]},
    "copilot": {"markers": [".github/copilot-instructions.md", ".github/agents", ".github/skills", ".github/hooks"], "home": [".copilot"], "bins": ["copilot"]},
    "gemini": {"markers": [".gemini", "GEMINI.md"], "home": [".gemini"], "bins": ["gemini"]},
    "antigravity": {"markers": [".agents/hooks.json", ".agents/rules", ".agent"], "home": [".gemini/antigravity"], "bins": ["agy"]},
    "kiro": {"markers": [".kiro"], "home": [".kiro"], "bins": ["kiro", "kiro-cli"]},
    "qoder": {"markers": [".qoder"], "home": [".qoder"], "bins": ["qoder", "qodercli"]},
}


class Plan:
    """The writes an install makes, collected first so --dry-run can print them without touching anything."""

    def __init__(self, target: Path, dry_run: bool) -> None:
        self.target = target
        self.dry_run = dry_run
        self.actions: list[dict] = []
        self.conflicts: list[str] = []
        self.notes: list[str] = []

    def rel(self, path: Path) -> str:
        return path.relative_to(self.target).as_posix()

    def write(self, path: Path, text: str, action: str) -> None:
        self.actions.append({"path": self.rel(path), "action": action})
        if self.dry_run:
            return
        if path.exists() and action != "create":
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if not backup.exists():
                shutil.copy2(path, backup)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as out:  # write_text(newline=) needs Python 3.10
            out.write(text)

    def copy(self, src: Path, dst: Path) -> None:
        if dst.exists():
            if dst.read_bytes() != src.read_bytes():
                self.conflicts.append(self.rel(dst))
            return
        self.actions.append({"path": self.rel(dst), "action": "create"})
        if not self.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def is_template(folder: Path) -> bool:
    return (folder / "AGENTS.md").is_file() and (folder / "memory" / "MAP.md").is_file() and (folder / "scripts" / "guard.py").is_file()


def is_pristine_template(folder: Path) -> bool:
    """The published template (a clone or a plugin cache), not a task repo whose memory holds someone's feedback."""
    log = folder / "memory" / "feedback-log.md"
    has_feedback = log.is_file() and re.search(r"\bFB-\d{3,}", log.read_text(encoding="utf-8"))
    return is_template(folder) and (folder / ".claude-plugin" / "plugin.json").is_file() and not has_feedback


def safe_extract(data: bytes, dest: Path) -> Path:
    """Extract a GitHub tarball into dest, refusing links and paths that leave dest; return its top folder."""
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            path = (dest / member.name).resolve()
            if member.issym() or member.islnk() or not str(path).startswith(str(dest.resolve())):
                raise SystemExit(f"refusing unsafe path in the template tarball: {member.name}")
        tar.extractall(dest)
    tops = [p for p in dest.iterdir() if p.is_dir()]
    if len(tops) != 1:
        raise SystemExit("unexpected template tarball layout")
    return tops[0]


def find_source(ref: str, workdir: Path) -> Path:
    here = Path(__file__).resolve().parents[1] if "__file__" in globals() and Path(__file__).is_file() else None
    if here and is_pristine_template(here):
        return here
    url = f"https://codeload.github.com/{REPO}/tar.gz/{ref}"
    print(f"downloading the template from {url}")
    with urllib.request.urlopen(url, timeout=60) as response:
        source = safe_extract(response.read(), workdir)
    if not is_template(source):
        raise SystemExit(f"{url} does not contain the vidbyte-memory template")
    return source


def detect_agents(target: Path) -> dict[str, str]:
    """Agent name -> why it was detected (a repo marker, a home folder or a command on PATH)."""
    found = {}
    home = Path.home()
    for name, signals in AGENTS.items():
        marker = next((m for m in signals["markers"] if (target / m).exists()), None)
        folder = next((h for h in signals["home"] if (home / h).is_dir()), None)
        binary = next((b for b in signals["bins"] if shutil.which(b)), None)
        if marker:
            found[name] = f"repo has {marker}"
        elif folder:
            found[name] = f"~/{folder} exists"
        elif binary:
            found[name] = f"`{binary}` is on PATH"
    return found


def demote_headings(text: str) -> str:
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        out.append("##" + line if line.startswith("#") and not fenced else line)
    return "\n".join(out)


def install_agents_md(plan: Plan, source: Path) -> None:
    dst = plan.target / "AGENTS.md"
    template = (source / "AGENTS.md").read_text(encoding="utf-8")
    if not dst.exists():
        plan.write(dst, template, "create")
        return
    old = dst.read_text(encoding="utf-8")
    if "## Memory index" in old and "memory/MAP.md" in old:
        return
    placeholder = re.search(r"(?m)^\(Replace this paragraph.*\)$", template)
    if not placeholder:
        raise SystemExit("the template AGENTS.md has no Task placeholder to fold the existing AGENTS.md into")
    intro = "(The paragraphs below came from this repo's AGENTS.md before vidbyte-memory was installed. Rewrite them as the recurring task this repo serves: what is produced, for whom, from what inputs, and where it goes.)"
    folded = template.replace(placeholder.group(0), intro + "\n\n" + demote_headings(old.strip()))
    if len(folded.splitlines()) > MAX_AGENTS_LINES:
        keep = plan.target / "AGENTS.previous.md"
        plan.write(keep, old, "create" if not keep.exists() else "update")
        note = "(This repo's agent instructions from before vidbyte-memory was installed are in AGENTS.previous.md; read it on every request. Rewrite this paragraph as the recurring task this repo serves: what is produced, for whom, from what inputs, and where it goes.)"
        folded = template.replace(placeholder.group(0), note)
    plan.write(dst, folded, "fold existing AGENTS.md")


def install_claude_md(plan: Plan) -> None:
    dst = plan.target / "CLAUDE.md"
    if not dst.exists():
        plan.write(dst, "@AGENTS.md\n", "create")
    elif "@AGENTS.md" not in dst.read_text(encoding="utf-8"):
        plan.write(dst, dst.read_text(encoding="utf-8").rstrip() + "\n\n@AGENTS.md\n", "add @AGENTS.md import")


def merge_json(plan: Plan, path: Path, update, label: str) -> None:
    """Load a JSON settings file (or start empty), apply update(data) -> changed?, and write it back."""
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except ValueError:
        plan.notes.append(f"{plan.rel(path)} is not valid JSON; add the vidbyte-memory hook to it by hand")
        return
    if not isinstance(data, dict):
        data = {}
    if update(data):
        plan.write(path, json.dumps(data, indent=2) + "\n", label if path.exists() else "create")


def nested_stop_hook(event: str, command: str, timeout: int):
    """The Claude Code hook shape, which Codex and Gemini CLI share: hooks.<event>[].hooks[] command entries."""
    def update(data: dict) -> bool:
        if GUARD in json.dumps(data):
            return False
        groups = data.setdefault("hooks", {}).setdefault(event, [])
        groups.append({"hooks": [{"type": "command", "command": command, "timeout": timeout}]})
        return True
    return update


def wire_agent(plan: Plan, name: str, source: Path) -> None:
    t = plan.target
    if name == "codex":
        merge_json(plan, t / ".codex" / "hooks.json", nested_stop_hook("Stop", GUARD, 180), "add Stop hook")
        plan.notes.append("Codex: open /hooks once and trust the vidbyte-memory Stop hook; project hooks are skipped until trusted")
    elif name == "copilot":
        hook = {"version": 1, "hooks": {"agentStop": [{"type": "command", "bash": "python3 scripts/guard.py", "powershell": GUARD, "timeoutSec": 180}]}}
        dst = t / ".github" / "hooks" / "vidbyte-memory.json"
        if not dst.exists():
            plan.write(dst, json.dumps(hook, indent=2) + "\n", "create")
    elif name == "gemini":
        merge_json(plan, t / ".gemini" / "settings.json", nested_stop_hook("AfterAgent", GUARD + " --format gemini", 180000), "add AfterAgent hook")
        gemini_md = t / "GEMINI.md"
        if not gemini_md.exists():
            plan.write(gemini_md, "@AGENTS.md\n", "create")
        elif "AGENTS.md" not in gemini_md.read_text(encoding="utf-8"):
            plan.write(gemini_md, gemini_md.read_text(encoding="utf-8").rstrip() + "\n\n@AGENTS.md\n", "add @AGENTS.md import")
    elif name == "antigravity":
        def update(data: dict) -> bool:
            if GUARD in json.dumps(data):
                return False
            data["vidbyte-memory"] = {"Stop": [{"type": "command", "command": GUARD + " --format antigravity", "timeout": 180}]}
            return True
        merge_json(plan, t / ".agents" / "hooks.json", update, "add Stop hook")
    elif name in ("kiro", "qoder"):
        for skill in sorted(p.parent for p in (source / "skills").glob("*/SKILL.md")):
            for src in sorted(p for p in skill.rglob("*") if p.is_file()):
                plan.copy(src, t / f".{name}" / "skills" / skill.name / src.relative_to(skill))


def install(source: Path, plan: Plan, agents: list[str]) -> None:
    for folder in COPY_DIRS:
        root = source / folder
        if not root.is_dir():
            continue
        for src in sorted(p for p in root.rglob("*") if p.is_file()):
            if SKIP_PARTS & set(src.relative_to(source).parts) or src.suffix == ".pyc" or src.name.endswith(BACKUP_SUFFIX):
                continue
            plan.copy(src, plan.target / src.relative_to(source))
    install_agents_md(plan, source)
    install_claude_md(plan)
    merge_json(plan, plan.target / ".claude" / "settings.json", nested_stop_hook("Stop", GUARD, 180), "add Stop hook")
    gitignore = plan.target / ".gitignore"
    wanted = [".claude/.guard_state.json", "__pycache__/", ".pytest_cache/"]
    have = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
    missing = [line for line in wanted if line not in have]
    if missing:
        plan.write(gitignore, "\n".join(have + missing).strip() + "\n", "update" if gitignore.exists() else "create")
    for name in agents:
        wire_agent(plan, name, source)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install vidbyte-memory into an existing repo and wire its coding agents.")
    parser.add_argument("--target", default=".", help="the repo to install into (default: the current directory)")
    parser.add_argument("--ref", default="main", help="branch or tag to download when not run from a template")
    parser.add_argument("--agents", help="comma-separated agents to wire, instead of detecting them: " + ", ".join(AGENTS))
    parser.add_argument("--all", action="store_true", help="wire every agent the installer knows")
    parser.add_argument("--dry-run", action="store_true", help="print the plan without writing anything")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    if not target.is_dir():
        raise SystemExit(f"{target} is not a folder")
    if is_template(target) and (target / ".claude-plugin").is_dir():
        raise SystemExit("this is the vidbyte-memory template itself; run the installer from the repo you want to give memory")

    with tempfile.TemporaryDirectory() as tmp:
        source = find_source(args.ref, Path(tmp))
        if args.agents:
            unknown = [a for a in args.agents.split(",") if a and a not in AGENTS]
            if unknown:
                raise SystemExit(f"unknown agents: {', '.join(unknown)}; known: {', '.join(AGENTS)}")
            agents = {a: "named with --agents" for a in args.agents.split(",") if a}
        elif args.all:
            agents = {a: "--all" for a in AGENTS}
        else:
            agents = detect_agents(target)
        plan = Plan(target, args.dry_run)
        install(source, plan, list(agents))
        if not args.dry_run and plan.actions and (target / "scripts" / "footprint.py").is_file():
            # The footprint counts the repo's own tests too, so the template's copy is stale until regenerated.
            subprocess.run([sys.executable, "scripts/footprint.py", "--write"], cwd=target, capture_output=True, text=True)
        if not args.dry_run and plan.actions:
            manifest = target / ".vidbyte-memory" / "install.json"
            record = {"template": REPO, "source": "local" if source.parent != Path(tmp) else f"github:{args.ref}", "agents": agents, "actions": plan.actions}
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    verb = "would write" if args.dry_run else "wrote"
    print(f"vidbyte-memory {verb} {len(plan.actions)} files in {target}")
    print("always wired: AGENTS.md, CLAUDE.md, .claude/ (Claude Code, Cursor, Devin CLI, Grok Build read it) and .agents/skills (Codex, Copilot, OpenCode, Pi, Goose and about 20 more)")
    for name, why in agents.items():
        print(f"  + {name} ({why})")
    for note in plan.notes:
        print(f"note: {note}")
    if plan.conflicts:
        print(f"kept {len(plan.conflicts)} existing files that differ from the template:")
        for path in plan.conflicts:
            print(f"  ! {path}")
        broken = [p for p in plan.conflicts if p in CRITICAL]
        if broken:
            print("The memory tests and hooks need the template's copy of " + ", ".join(broken) + "; move yours aside and run the installer again.")
            return 1
    if not args.dry_run:
        print("next: fill the ## Task section of AGENTS.md, run `python -m pytest -q tests`, and commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
