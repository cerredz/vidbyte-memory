# Verifier index

One row per verifier. `trigger` is a glob or an artifact kind; `*` means every artifact. `skills/verify-generation/SKILL.md` runs every verifier whose trigger matches, plus `memory-conformance` always. A retired verifier keeps its row with `status: retired` and a reason.

| name | file | trigger | rules | status |
|---|---|---|---|---|
| memory-conformance | `verifiers/memory-conformance.md` | `*` | all active rules, facts and guarantees in scope | active |
