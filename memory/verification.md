---
title: Ways to verify
description: How each kind of claim or artifact is verified in this repo, and which test or verifier does it. Load before each verification round.
write: skills/create-verifier, only when a verifier checks a kind of claim no existing entry names. verifiers/INDEX.md is the registry of verifiers.
---

# Ways to verify

Format: `claim type:` / `how to verify:` / `command or verifier:` on three lines, then the metadata line. See `memory/MAP.md`.

### V-001: artifact properties a script can read
claim type: any property of a file or output that code can observe, such as casing, length, structure, forbidden strings, required sections, numeric limits or link targets
how to verify: a deterministic test in `tests/` written with `skills/create-test`, run on every verification round
command or verifier: `python -m pytest -q tests`
-- added: 2026-10-27 | source: owner | status: active

### V-002: judgments a test cannot encode
claim type: tone, fit to the owner's taste, whether an output follows a rule that has no mechanical proxy yet
how to verify: a verifier agent in fresh context that sees only the artifact, the rule and the examples, and returns pass or fail with a quoted location
command or verifier: the matching entries in `verifiers/INDEX.md`, run through `skills/verify-generation`
-- added: 2026-10-27 | source: owner | status: active

### V-003: the memory itself
claim type: ids unique, metadata complete, facts 4 to 5 sentences, indexes current, no secrets, footprint current
how to verify: the integrity test, which runs with the rest of the suite
command or verifier: `python -m pytest -q tests/test_memory_integrity.py`
-- added: 2026-10-27 | source: owner | status: active

### V-004: claims of completion
claim type: "done", "passes", "works"
how to verify: the command that was run and its output, or the verifier's verdict with its quoted location; a claim without one counts as unverified
command or verifier: recorded in `memory/progress.md` under the verification rounds table
-- added: 2026-10-27 | source: owner | status: active
