# Verifier: <name>

## Goal

<Two to four sentences in the owner's terms: what this verifier protects, which correction it exists to keep from recurring, and why no deterministic test can check it.>

## Objective

Check the artifact against rule <ids> and return `PASS` or `FAIL` with a quoted location for every failure. Judge from the artifact, the rule restatements and the examples named in this file, and nothing else. Return `FAIL` with the reason for anything you cannot check.

## Tasks

1. Read the artifact paths you were given, in full, and nothing else outside this file's list.
2. Read the rule restatements below; open `memory/rules.md` or the fact file only when a restatement says the full text is needed.
3. Read the approved examples named below, if any, as positive examples of a pass.
4. Check each rule against each artifact in turn, and note the location of every violation as you go.
5. Report in the output block.

## Instructions

- **Rules checked:** <ids, each with a one-line restatement, so the verifier does not need to open memory>.
- **Approved examples:** <paths under memory/examples/, or none>.
- **What counts as a failure:** <concrete, observable description: what a reader could point at in the artifact>.
- **What does not count:** <the boundary, so the verifier does not over-apply the rule to artifacts the owner never meant>.
- **Judge from the artifact alone.** The author's intent, plan or explanation is not available and would not change the verdict. An artifact that needs an explanation to pass fails.
- **A property you cannot check is a `FAIL` with the reason, never a pass.** A pass you cannot justify is the same as no verifier.

## Checklist

- [ ] Every artifact read in full, with no skimming of long files.
- [ ] Every rule checked against every artifact, and the rule ids listed in the output.
- [ ] Every failure has a quoted location and a rule id, so the generating agent can fix from that line alone.

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
- One pass. Do not negotiate with the artifact's author; the generating agent fixes and re-runs the round.
- Launched by `skills/verify-generation/SKILL.md` on every round for artifacts matching this verifier's trigger in `verifiers/INDEX.md`.
