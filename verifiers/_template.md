# Verifier: <name>

## Goal

<One sentence: what this verifier protects, in the owner's terms.>

## Objective

Check the artifact against rule <ids> and return `PASS` or `FAIL` with a quoted location for every failure.

## Tasks

1. Read the artifact paths you were given, and nothing else outside this file's list.
2. Read the rule text for <ids> from `memory/rules.md` or `facts/<file>.md`.
3. Read the approved examples named below, if any.
4. Check each rule against each artifact in turn.
5. Report.

## Instructions

- Rules checked: <ids and one-line restatement of each>.
- Approved examples: <paths under memory/examples/, or none>.
- What counts as a failure: <concrete, observable description>.
- What does not count: <the boundary, so the verifier does not over-apply>.
- A property you cannot check is a `FAIL` with the reason, never a pass.

## Checklist

- [ ] Every artifact read in full.
- [ ] Every rule checked against every artifact.
- [ ] Every failure has a quoted location and a rule id.

## Output

```
verifier: <name>
artifacts: <paths>
verdict: PASS | FAIL
failures:
- <path>:<location> | <rule id> | <quoted text> | <what is wrong>
```

## Runtime behavior

- Fresh context. Read only. No edits, no commits, no fixes.
- One pass. Do not negotiate with the artifact's author; the generating agent fixes and re-runs.
