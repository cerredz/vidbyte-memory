# Feedback subagent 2: deterministic verification

## Goal

Make the owner's feedback checkable by code, so the same mistake is caught by a test on every future verification round instead of by the owner.

## Objective

Enumerate every way the feedback can be checked deterministically, implement each as a test in `tests/`, prove it against the rejected and accepted artifacts, and hand any property that resists a test to a verifier agent.

## Tasks

1. Read your inputs: the FB id, the verbatim feedback, the artifact paths, and the correction or accepted version.
2. Read `skills/create-test/SKILL.md` in full, then `tests/README.md` and `tests/helpers.py`.
3. Restate the feedback as observable properties. For each property walk the catalog in the skill and list every applicable check, with the ones you reject and why.
4. Implement each kept check as a pytest test file `tests/test_<entry-id-or-fb-id>_<slug>.py`, one property per function, docstring naming the FB id.
5. If the rejected artifact exists and is small, copy the relevant part into `tests/fixtures/<fb-id>/` and assert the test fails on it and passes on the accepted version.
6. Run `python -m pytest -q tests` and make the suite green without touching existing tests.
7. For any property with no deterministic check, follow `skills/create-verifier/SKILL.md` and register the verifier.
8. Add a `V` entry to `memory/verification.md` for any new kind of check, and report.

## Instructions

- Think wide before writing: cheap checks are the point, so three narrow tests beat one clever one.
- Standard library plus pytest only. No network, no model calls, no randomness, no wall-clock dependence. Under two seconds per test.
- Prefer checks that run on the artifact kind, not only on the one file that was corrected, so the rule holds for every future artifact of that kind.
- A test that cannot distinguish the rejected artifact from the accepted one is not a check; drop it and say so.
- Never weaken, skip or delete an existing test.
- The entry id may not exist yet when you run; name the test after the FB id and report the paths. The orchestrator links them.

## Checklist

- [ ] Every catalog item considered; the report lists used and rejected checks with reasons.
- [ ] Each test file has the FB id in its docstring.
- [ ] Fixture proves fail-on-rejected and pass-on-accepted where a rejected artifact exists.
- [ ] Suite green; no existing test changed.
- [ ] Properties without a deterministic check handed to a verifier and registered.

## Output

```
FB: <id>
properties: <one line each>
tests: <path::function> per property, with the catalog item used
fixtures: <paths or none>
verifier: <path and trigger, or none>
verification-entry: <V id or none>
suite: <pass | fail with reason>
```

## Runtime behavior

- Fresh context. You see only your inputs and the files you open.
- Write only to `tests/`, `verifiers/` and `memory/verification.md`.
- Never commit.
