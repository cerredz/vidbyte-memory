"""Integrity of the memory itself.

These tests are the deterministic half of the memory system. They fail when an entry breaks the shared
format, when an index drifts from its folder, when a fact is not 4 to 5 sentences, when a rule names no
check, when a supersession points nowhere, when feedback is left pending, when the footprint is stale, or
when a secret or a relative date enters memory. Source of truth for the format: memory/MAP.md.
"""

from __future__ import annotations

import importlib.util
import re

import helpers as h

FACT_FILES = "facts/*.md"
MEMORY_FILES = "memory/*.md"
NO_ENTRY_FILES = (
    "memory/MAP.md",
    "memory/progress.md",
    "memory/run-log.md",
    "memory/footprint.md",
    "memory/owner-profile.md",
)
PREFIX_BY_FILE = {
    "memory/rules.md": "R",
    "memory/hints.md": "H",
    "memory/guarantees.md": "G",
    "memory/failures.md": "X",
    "memory/verification.md": "V",
    "memory/decisions.md": "D",
    "memory/open-questions.md": "Q",
    "memory/workflows.md": "W",
    "memory/scope.md": "S",
    "memory/glossary.md": "T",
    "memory/pointers.md": "P",
    "memory/feedback-log.md": "FB",
}
STATUSES = {"active", "superseded", "retired"}
META_KEYS = {"added", "source", "status", "verified-by", "supersedes", "superseded-by", "confirmed", "reason", "scope"}
NEEDS_CHECK = {"F", "R", "G"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_RE = re.compile(r"^(owner|collect|run|FB-\d{3,})$")
RELATIVE_DATE_RE = re.compile(r"\b(yesterday|tomorrow|last week|last month|next week|recently|the other day)\b", re.I)
SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"])",
    re.I,
)


def _typed_entries() -> list[h.Entry]:
    return h.all_entries((FACT_FILES, MEMORY_FILES), skip=NO_ENTRY_FILES)


def _expected_prefix(file: str) -> str | None:
    if file.startswith("facts/") and file != "facts/README.md":
        return "F"
    return PREFIX_BY_FILE.get(file)


def test_memory_and_fact_files_have_frontmatter():
    missing = []
    for path in h.files(FACT_FILES) + h.files(MEMORY_FILES):
        name = h.rel(path)
        if name == "facts/README.md":
            continue
        fm = h.frontmatter(path.read_text(encoding="utf-8"))
        if not fm.get("title") or not fm.get("description"):
            missing.append(name)
    assert not missing, f"files without title/description frontmatter: {missing}"


def test_agents_index_covers_every_memory_file():
    agents = h.text("AGENTS.md")
    missing = [h.rel(p) for p in h.files(MEMORY_FILES) if f"`{h.rel(p)}`" not in agents]
    if "`memory/examples/`" not in agents:
        missing.append("memory/examples/")
    assert not missing, f"memory files missing from the AGENTS.md memory index: {missing}"
    dangling = [m for m in re.findall(r"`(memory/[^`]+\.md)`", agents) if not (h.ROOT / m).exists()]
    assert not dangling, f"AGENTS.md names memory files that do not exist: {dangling}"


def test_facts_index_covers_every_fact_file():
    agents = h.text("AGENTS.md")
    missing = [h.rel(p) for p in h.files(FACT_FILES) if h.rel(p) != "facts/README.md" and f"`{h.rel(p)}`" not in agents]
    assert not missing, f"fact files missing from the AGENTS.md facts index: {missing}"
    dangling = [m for m in re.findall(r"`(facts/[^`]+\.md)`", agents) if not (h.ROOT / m).exists()]
    assert not dangling, f"AGENTS.md names fact files that do not exist: {dangling}"


def test_no_entries_in_untyped_files():
    stray = []
    for name in NO_ENTRY_FILES:
        if (h.ROOT / name).exists() and h.entries(h.text(name), name):
            stray.append(name)
    assert not stray, f"entries found in files that must not hold entries: {stray}"


def test_entry_ids_are_unique_and_match_their_file():
    seen: dict[str, str] = {}
    problems = []
    for entry in _typed_entries():
        expected = _expected_prefix(entry.file)
        if expected is None:
            problems.append(f"{entry.file}: not a typed memory file but holds {entry.id}")
        elif entry.prefix != expected:
            problems.append(f"{entry.file}:{entry.line} {entry.id} should use prefix {expected}")
        if entry.id in seen:
            problems.append(f"{entry.id} appears in both {seen[entry.id]} and {entry.file}")
        seen[entry.id] = entry.file
    assert not problems, "\n".join(problems)


def test_entry_metadata_is_complete_and_valid():
    problems = []
    for entry in _typed_entries():
        where = f"{entry.file}:{entry.line} {entry.id}"
        if not entry.has_meta:
            problems.append(f"{where}: missing the `-- ` metadata line")
            continue
        unknown = set(entry.meta) - META_KEYS
        if unknown:
            problems.append(f"{where}: unknown metadata keys {sorted(unknown)}")
        for key in ("added", "source", "status"):
            if key not in entry.meta:
                problems.append(f"{where}: missing `{key}`")
        if "added" in entry.meta and not DATE_RE.match(entry.meta["added"]):
            problems.append(f"{where}: `added` is not an ISO date")
        if "confirmed" in entry.meta and not DATE_RE.match(entry.meta["confirmed"]):
            problems.append(f"{where}: `confirmed` is not an ISO date")
        if entry.meta.get("status") not in STATUSES:
            problems.append(f"{where}: status must be one of {sorted(STATUSES)}")
        if entry.meta.get("status") == "retired" and not entry.meta.get("reason"):
            problems.append(f"{where}: a retired entry needs a `reason`")
    assert not problems, "\n".join(problems)


def test_entries_cite_a_source():
    log_ids = {e.id for e in h.entries(h.text("memory/feedback-log.md"), "memory/feedback-log.md")}
    problems = []
    for entry in _typed_entries():
        source = entry.meta.get("source", "")
        if not SOURCE_RE.match(source):
            problems.append(f"{entry.file}:{entry.line} {entry.id}: source must be owner, collect, run or an FB id")
        elif source.startswith("FB-") and source not in log_ids:
            problems.append(f"{entry.file}:{entry.line} {entry.id}: source {source} is not in memory/feedback-log.md")
    assert not problems, "\n".join(problems)


def test_facts_have_four_to_five_sentences():
    problems = []
    for entry in _typed_entries():
        if entry.prefix != "F":
            continue
        count = len(h.sentences(entry.body))
        if not 4 <= count <= 5:
            problems.append(f"{entry.file}:{entry.line} {entry.id}: {count} sentences, needs 4 to 5")
        if re.search(r"https?://|/[A-Za-z0-9_.-]+\.(py|md|json|yml|yaml|html|txt)\b", entry.body):
            problems.append(f"{entry.file}:{entry.line} {entry.id}: paths and URLs belong on the metadata line")
    assert not problems, "\n".join(problems)


def test_facts_rules_and_guarantees_name_a_check():
    problems = []
    for entry in _typed_entries():
        if entry.prefix not in NEEDS_CHECK or entry.meta.get("status") != "active":
            continue
        value = entry.meta.get("verified-by", "")
        where = f"{entry.file}:{entry.line} {entry.id}"
        if not value or value == "pending":
            problems.append(f"{where}: `verified-by` must name a check or `none (<reason>)`")
            continue
        if value.startswith("none ("):
            continue
        path, _, func = value.partition("::")
        if not (h.ROOT / path).exists():
            problems.append(f"{where}: verified-by path {path} does not exist")
        elif func and f"def {func}(" not in (h.ROOT / path).read_text(encoding="utf-8"):
            problems.append(f"{where}: {path} has no function {func}")
    assert not problems, "\n".join(problems)


def test_superseded_entries_point_to_a_successor():
    ids = {e.id for e in _typed_entries()}
    problems = []
    for entry in _typed_entries():
        where = f"{entry.file}:{entry.line} {entry.id}"
        if entry.meta.get("status") == "superseded":
            successor = entry.meta.get("superseded-by", "")
            if successor not in ids:
                problems.append(f"{where}: superseded-by {successor!r} is not an existing entry")
            elif successor == entry.id:
                problems.append(f"{where}: an entry cannot supersede itself")
        if "supersedes" in entry.meta and entry.meta["supersedes"] not in ids:
            problems.append(f"{where}: supersedes {entry.meta['supersedes']!r} is not an existing entry")
    assert not problems, "\n".join(problems)


def test_feedback_entries_have_a_disposition():
    problems = []
    for entry in h.entries(h.text("memory/feedback-log.md"), "memory/feedback-log.md"):
        where = f"memory/feedback-log.md:{entry.line} {entry.id}"
        if "> verbatim:" not in entry.body:
            problems.append(f"{where}: missing the `> verbatim:` quote")
        if not re.search(r"^disposition: \S", entry.body, re.M):
            problems.append(f"{where}: missing the `disposition:` line")
    assert not problems, "\n".join(problems)


def test_no_feedback_is_pending():
    pending = [e.id for e in h.entries(h.text("memory/feedback-log.md"), "memory/feedback-log.md") if re.search(r"^disposition: pending", e.body, re.M)]
    assert not pending, f"feedback still pending at the end of the request: {pending}"


def test_verifier_index_matches_files():
    index = h.text("verifiers/INDEX.md")
    skip = {"verifiers/README.md", "verifiers/INDEX.md", "verifiers/_template.md"}
    missing = [h.rel(p) for p in h.files("verifiers/*.md") if h.rel(p) not in skip and f"`{h.rel(p)}`" not in index]
    assert not missing, f"verifiers missing from verifiers/INDEX.md: {missing}"
    dangling = [m for m in re.findall(r"`(verifiers/[^`]+\.md)`", index) if not (h.ROOT / m).exists()]
    assert not dangling, f"verifiers/INDEX.md names files that do not exist: {dangling}"


def test_footprint_is_current():
    spec = importlib.util.spec_from_file_location("footprint", h.ROOT / "scripts" / "footprint.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    expected = module.render(module.scan())
    actual = h.text("memory/footprint.md")
    assert actual == expected, "memory/footprint.md is stale; run `python scripts/footprint.py --write`"


def test_no_secrets_in_memory():
    hits = []
    for path in h.files(FACT_FILES) + h.files(MEMORY_FILES) + h.files("memory/examples/*.md") + h.files("tests/**/*"):
        name = h.rel(path)
        if name == "tests/test_memory_integrity.py" or path.suffix in {".pyc"}:
            continue
        try:
            src = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if SECRET_RE.search(src):
            hits.append(name)
    assert not hits, f"possible secrets found in: {hits}"


def test_no_relative_dates_in_entries():
    problems = [f"{e.file}:{e.line} {e.id}" for e in _typed_entries() if RELATIVE_DATE_RE.search(e.body)]
    assert not problems, f"entries with relative dates (write an ISO date instead): {problems}"


def test_agents_md_is_under_200_lines():
    count = len(h.text("AGENTS.md").splitlines())
    assert count <= 200, f"AGENTS.md is {count} lines; keep it under 200 so it stays an index"


def test_feedback_tests_name_their_feedback():
    problems = []
    for path in h.files("tests/test_*.py"):
        name = h.rel(path)
        if name == "tests/test_memory_integrity.py":
            continue
        head = path.read_text(encoding="utf-8")[:1500]
        if not re.search(r"\bFB-\d{3,}\b", head):
            problems.append(name)
    assert not problems, f"feedback tests must name their FB id in the module docstring: {problems}"
