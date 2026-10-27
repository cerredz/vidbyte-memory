---
name: create-test
description: Use when turning human feedback into a deterministic test in tests/. Lists the ways a rule can be checked by code, the constraints a test must meet, and how to register it on the entry it enforces.
---

# Create a test

## Goal

Every rule the owner cares about has a cheap, deterministic check that runs on every verification round, so the agent cannot drift from it unnoticed.

## Objective

Find every way the feedback can be checked by code, implement each as a pytest test using the standard library, make sure it fails on the rejected artifact and passes on the accepted one, and register it.

## Tasks

1. Restate the feedback as one or more observable properties of an artifact.
2. Walk the catalog below and list every check that applies. Deterministic checks are cheap, so prefer several narrow tests over one broad one.
3. Write each test in `tests/test_<entry-id>_<slug>.py` with a docstring naming the FB id and the entry id.
4. If the rejected artifact exists and is small, copy the relevant part into `tests/fixtures/` and assert the test fails on it; assert it passes on the accepted version.
5. Run `python -m pytest -q tests`.
6. Report the test paths so the orchestrator can set `verified-by` on the entry, and add a `V` entry to `memory/verification.md` when the check is a new kind.

## Instructions

### Catalog of deterministic checks

- Forbidden or required strings and regular expressions in an artifact, including casing, wording and punctuation.
- Required sections, headings or fields, and their order.
- Length limits: words, sentences, lines, characters, duration, file size.
- Numeric thresholds read from the artifact or from a tool's output, such as loudness, dimensions, counts, ratios.
- File presence, naming patterns, and folder structure.
- Frontmatter or schema validity for markdown, JSON, YAML and CSV.
- Links and references that resolve: paths exist, anchors exist, ids exist.
- Command exit codes: a build, a lint, a formatter or a renderer runs clean.
- Snapshot comparison against an approved example in `memory/examples/`, exact or normalized.
- Ordering and consistency across files, such as an index that matches a folder.
- Diff-scoped checks that only inspect files changed in the current request, via `git diff --name-only`.
- Idempotency: running a step twice yields the same output.
- Absence checks: no placeholder text, no TODO markers, no secrets, no leftover debug output.
- Metadata of media read through a local tool, such as image dimensions or video duration, when that tool is already installed.

### Constraints

- Standard library only, plus pytest. No network, no model calls, no randomness, no wall-clock dependence.
- Under two seconds per test. Read artifacts through `tests/helpers.py`.
- One property per test function; the name says what it checks.
- A test never asserts on the memory files' contents except through `test_memory_integrity.py`.
- Never weaken or delete an existing test to make a new one pass.

### When no deterministic check exists

Say so in the report and hand the property to `skills/create-verifier/SKILL.md`. Do not write a test that calls a model.

## Checklist

- [ ] Every applicable catalog item considered; the report lists the ones used and the ones rejected with a reason.
- [ ] Each test has a docstring with the FB id and the entry id.
- [ ] Fails on the rejected sample when one exists; passes on the accepted one.
- [ ] Suite runs green.
- [ ] Test paths reported for `verified-by`.

## Output

The list of test files and functions, which catalog items each uses, the fixture paths, and any property that needs a verifier instead.

## Runtime behavior

- Writes only to `tests/` and `memory/verification.md`.
- Runs inside the feedback-test subagent or on the owner's direct request.
