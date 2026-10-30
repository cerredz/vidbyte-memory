"""Mirror skills/ into the folders coding agents scan for project skills.

skills/ is the source of truth, but no harness scans a root skills/ folder inside a project. About 25 harnesses
(Codex, Copilot, Cursor, Gemini CLI, Antigravity, OpenCode, Pi, Goose, Junie, Zed and others) read
.agents/skills/, and Claude Code and Cline read .claude/skills/. This script copies every skills/<name>/ folder
into both, and removes mirrored skills that no longer exist in skills/.

Usage: python scripts/sync_skills.py           (write the mirrors)
       python scripts/sync_skills.py --check   (exit 1 and list the differences when a mirror is stale)
Standard library only.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"
MIRRORS = (ROOT / ".agents" / "skills", ROOT / ".claude" / "skills")


def source_skills() -> list[Path]:
    return sorted(p.parent for p in SOURCE.glob("*/SKILL.md"))


def differences() -> list[str]:
    """Every way the mirrors differ from skills/, as repo-relative descriptions."""
    out = []
    names = {skill.name for skill in source_skills()}
    for mirror in MIRRORS:
        for skill in source_skills():
            target = mirror / skill.name
            for src in sorted(p for p in skill.rglob("*") if p.is_file()):
                dst = target / src.relative_to(skill)
                if not dst.is_file() or not filecmp.cmp(src, dst, shallow=False):
                    out.append(f"{dst.relative_to(ROOT).as_posix()} differs from {src.relative_to(ROOT).as_posix()}")
        if mirror.is_dir():
            for stale in sorted(p for p in mirror.iterdir() if p.is_dir() and p.name not in names):
                out.append(f"{stale.relative_to(ROOT).as_posix()} has no source in skills/")
    return out


def sync() -> None:
    names = {skill.name for skill in source_skills()}
    for mirror in MIRRORS:
        mirror.mkdir(parents=True, exist_ok=True)
        for stale in (p for p in mirror.iterdir() if p.is_dir() and p.name not in names and (p / "SKILL.md").exists()):
            shutil.rmtree(stale)
        for skill in source_skills():
            target = mirror / skill.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(skill, target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mirror skills/ into .agents/skills/ and .claude/skills/.")
    parser.add_argument("--check", action="store_true", help="report stale mirrors instead of writing them")
    if parser.parse_args(argv).check:
        problems = differences()
        print("\n".join(problems) if problems else "skill mirrors are in sync")
        return 1 if problems else 0
    sync()
    print(f"mirrored {len(source_skills())} skills into " + ", ".join(m.relative_to(ROOT).as_posix() for m in MIRRORS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
