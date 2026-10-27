# Verifiers

Verification agents: prompts that a fresh-context agent runs against an artifact and answers `PASS` or `FAIL` with a quoted location. They cover the rules that no deterministic test can check, such as tone, fit to the owner's taste, or a rule that has no mechanical proxy yet. Tests in `tests/` cover everything else and are always preferred, because they are cheaper and cannot drift.

- `INDEX.md` lists every verifier with its trigger and the rule ids it enforces. `skills/verify-generation/SKILL.md` selects verifiers from this index on every round.
- `_template.md` is the fixed shape of a verifier: goal, objective, tasks, instructions, checklist, output, runtime behavior.
- `memory-conformance.md` runs on every artifact and checks it against the rules, facts and guarantees in scope.
- New verifiers are created by the feedback-test subagent through `skills/create-verifier/SKILL.md`, never by hand during generation.

A verifier sees only what its file lists: the artifact, the rule texts, and the approved examples. It never sees the conversation that produced the artifact, so it cannot be talked into a pass.
