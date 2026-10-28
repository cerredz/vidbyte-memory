---
title: Guarantees
description: What the agent guarantees before ending any request, and what enforces each guarantee. Load on every request.
write: The owner, or an agent carrying out a decision entry. Every guarantee names what enforces it.
---

# Guarantees

Format: "Before ending, the agent ..." plus how it is enforced, then the metadata line. See `memory/MAP.md`.

### G-001: all tests pass before ending
Before ending, the agent runs `python -m pytest -q tests` and every test passes. It never deletes, skips or weakens a test to get there; a test that cannot pass means the request is reported as unfinished.
-- added: 2026-10-27 | source: owner | status: active | verified-by: scripts/guard.py

### G-002: every generative step is verified in rounds
Before ending, every generative step has had at least 3 and at most 5 verification rounds with the full suite, and the report names any step that had fewer and why.
-- added: 2026-10-27 | source: owner | status: active | verified-by: none (the rounds table in memory/progress.md is the evidence; no script counts rounds yet)

### G-003: no feedback is left pending
Before ending, every entry in `memory/feedback-log.md` has a disposition other than `pending`, so each piece of feedback became a fact, a test, an update, or a logged decision not to keep it.
-- added: 2026-10-27 | source: owner | status: active | verified-by: scripts/guard.py

### G-004: the footprint change is committed and pushed
Before ending, `memory/footprint.md` is regenerated, every change is committed with the footprint delta in the message, and the commit is pushed to `origin`.
-- added: 2026-10-27 | source: owner | status: active | verified-by: scripts/guard.py

### G-005: secrets never enter memory
Before ending, no file under `memory/`, `facts/` or `tests/` contains a credential, token or key; the integrity test scans for them.
-- added: 2026-10-27 | source: owner | status: active | verified-by: tests/test_memory_integrity.py::test_no_secrets_in_memory

### G-006: memory changes only through feedback handling
Before ending, no fact, rule or test was added or changed as a side effect of generation; every change traces to a feedback entry, a "collect facts" request, or the owner's own edit.
-- added: 2026-10-27 | source: owner | status: active | verified-by: tests/test_memory_integrity.py::test_entries_cite_a_source
