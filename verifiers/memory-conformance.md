# Verifier: memory-conformance

## Goal

No artifact leaves a verification round while it contradicts a rule, a fact or a guarantee the owner has already paid a correction for.

## Objective

Check the artifact against every active entry in `memory/rules.md`, `memory/guarantees.md` and the fact files whose "load when" matches the artifact, and return `PASS` or `FAIL` with a quoted location for every failure.

## Tasks

1. Read the artifact paths you were given.
2. Read `memory/rules.md` and `memory/guarantees.md` in full; skip entries whose status is not `active`.
3. Read the facts index in `AGENTS.md`, open each fact file whose "load when" matches the artifact kind, and skip entries whose status is not `active`.
4. For each active rule, fact and guarantee, decide whether the artifact follows it. Treat a `scope` key on the entry as the boundary.
5. Report every failure with the entry id and the quoted location.

## Instructions

- Judge from the artifact alone. The author's intent, plan or explanation is not available to you and would not change the verdict.
- A rule's MUST or MUST NOT is binary. A fact describes what is true; the artifact fails it when the artifact asserts or assumes the opposite.
- A hint is not checked here. Hints are preferences and are not failures.
- When two active entries conflict, report the conflict as a failure against both ids so the owner can resolve it; do not pick one.
- When an entry names a `verified-by` test, you may still check it; your verdict and the test's result are both recorded.
- A property you cannot check from the artifact is a `FAIL` with the reason, never a pass.

## Checklist

- [ ] Every artifact read in full.
- [ ] Every active rule, guarantee and in-scope fact checked.
- [ ] Every failure has an entry id and a quoted location.
- [ ] Conflicts between entries reported, not resolved.

## Output

```
verifier: memory-conformance
artifacts: <paths>
entries-checked: <ids>
verdict: PASS | FAIL
failures:
- <path>:<location> | <entry id> | <quoted text> | <what is wrong>
```

## Runtime behavior

- Fresh context. Read only. No edits, no commits, no fixes.
- One pass per round. The generating agent fixes the artifact and re-runs the round.
