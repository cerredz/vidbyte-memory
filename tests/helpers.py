"""Shared helpers for the tests in this folder.

Locates the repo, reads files, parses frontmatter and memory entries, and counts sentences, so every
feedback test reads artifacts the same way. Standard library only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENTRY_RE = re.compile(r"^### ([A-Z]{1,2})-(\d{3,}): (.+?)\s*$")
META_RE = re.compile(r"^-- (.+?)\s*$")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def text(rel_path: str) -> str:
    """Read a repo file as UTF-8 text with newlines normalized to \\n."""
    return (ROOT / rel_path).read_text(encoding="utf-8")


def files(pattern: str) -> list[Path]:
    """Repo files matching a glob relative to the repo root, sorted."""
    return sorted(p for p in ROOT.glob(pattern) if p.is_file())


def rel(path: Path) -> str:
    """A repo-relative POSIX path, the form used in indexes and metadata lines."""
    return path.relative_to(ROOT).as_posix()


def frontmatter(src: str) -> dict[str, str]:
    """The YAML-ish frontmatter block as a flat dict; empty when the file has none."""
    src = src.replace("\r\n", "\n")
    if not src.startswith("---\n"):
        return {}
    end = src.find("\n---", 4)
    if end == -1:
        return {}
    out: dict[str, str] = {}
    for line in src[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip()
    return out


def parse_meta(line: str) -> dict[str, str]:
    """Parse `key: value | key: value` from a metadata line (without the leading `-- `)."""
    out: dict[str, str] = {}
    for part in line.split(" | "):
        if ": " in part:
            key, value = part.split(": ", 1)
            out[key.strip()] = value.strip()
        elif part.strip():
            out[part.strip()] = ""
    return out


@dataclass
class Entry:
    """One memory entry: heading id and subject, body text, parsed metadata, and where it lives."""

    id: str
    prefix: str
    number: int
    subject: str
    body: str
    meta: dict[str, str] = field(default_factory=dict)
    line: int = 0
    file: str = ""
    has_meta: bool = False


def without_fences(lines: list[str]) -> list[str]:
    """The same lines with everything inside ``` or ~~~ code fences blanked, so examples never count as entries."""
    out: list[str] = []
    in_fence = False
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return out


def entries(src: str, file: str = "") -> list[Entry]:
    """All `### PREFIX-nnn: subject` entries in a file, each ending at the next entry or `## ` heading."""
    lines = without_fences(src.splitlines())
    found: list[Entry] = []
    i = 0
    while i < len(lines):
        match = ENTRY_RE.match(lines[i])
        if not match:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not ENTRY_RE.match(lines[j]) and not lines[j].startswith("## "):
            j += 1
        block = lines[i + 1 : j]
        meta: dict[str, str] = {}
        body_lines = block
        has_meta = False
        for k in range(len(block) - 1, -1, -1):
            meta_match = META_RE.match(block[k])
            if meta_match:
                meta = parse_meta(meta_match.group(1))
                body_lines = block[:k]
                has_meta = True
                break
        prefix, number, subject = match.group(1), int(match.group(2)), match.group(3)
        found.append(
            Entry(
                id=f"{prefix}-{match.group(2)}",
                prefix=prefix,
                number=number,
                subject=subject,
                body="\n".join(body_lines).strip(),
                meta=meta,
                line=i + 1,
                file=file,
                has_meta=has_meta,
            )
        )
        i = j
    return found


def sentences(body: str) -> list[str]:
    """Sentences in a body, split on terminal punctuation followed by whitespace."""
    flat = " ".join(line.strip() for line in body.splitlines() if line.strip())
    return [s for s in SENTENCE_SPLIT_RE.split(flat) if s.strip()]


def all_entries(patterns: tuple[str, ...] = ("facts/*.md", "memory/*.md"), skip: tuple[str, ...] = ()) -> list[Entry]:
    """Entries across the memory files, excluding the repo-relative paths in `skip`."""
    out: list[Entry] = []
    for pattern in patterns:
        for path in files(pattern):
            name = rel(path)
            if name in skip:
                continue
            out.extend(entries(path.read_text(encoding="utf-8"), name))
    return out
