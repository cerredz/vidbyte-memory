# Tests

Deterministic checks. Every rule the owner has corrected the agent on gets at least one test here, written by the feedback-test subagent through `skills/create-test/SKILL.md`, so the next verification round catches the mistake instead of the owner. `AGENTS.md` requires the whole suite to pass before any request ends, and `scripts/guard.py` blocks the end of a turn in Claude Code until it does.

Run: `python -m pytest -q tests`. Requirements: Python 3.9 or later and pytest. The tests use only the standard library.

## Files

| File | Role |
|---|---|
| `helpers.py` | Reads repo files, parses frontmatter and memory entries, counts sentences. Every test imports from it. |
| `test_memory_integrity.py` | Checks the memory itself: frontmatter, indexes, ids, metadata, fact length, checks named, supersession links, dispositions, footprint current, no secrets, no relative dates. |
| `feedback_test_template.py` | A worked example of a feedback test. Not collected by pytest. Copy it to `test_<id>_<slug>.py`. |
| `fixtures/` | Small copies of rejected and accepted artifacts that feedback tests assert against. |

## How feedback becomes a test

1. The feedback-test subagent restates the feedback as observable properties of an artifact.
2. For each property it walks the catalog in `skills/create-test/SKILL.md` and writes one test function per property in `tests/test_<entry-id-or-fb-id>_<slug>.py`.
3. The module docstring names the FB id and the entry id. The function name says what it checks.
4. When the rejected artifact exists and is small, the relevant part goes into `fixtures/<fb-id>/` and the test proves it fails on the rejected version and passes on the accepted one.
5. The orchestrator writes the test path into the entry's `verified-by`.

## Rules for every test

- Standard library plus pytest. No network, no model calls, no randomness, no wall-clock dependence.
- Under two seconds. One property per function.
- Reads artifacts through `helpers.py` so paths and encodings are handled once.
- Never asserts on memory file contents; `test_memory_integrity.py` owns that.
- Never weakened, skipped or deleted to make a run pass. A test that is wrong is superseded by a better test, with the FB id that said so.
