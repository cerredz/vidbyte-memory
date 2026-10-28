# Verifier: memory-conformance

## Goal

No artifact leaves a verification round while it contradicts a rule, a fact or a guarantee the owner has already paid a correction for. Every active entry in memory exists because the owner corrected the agent once, and an artifact that ignores one is the same correction about to happen again. This verifier is the general check that runs on every artifact in every round, alongside the tests and the narrower verifiers, so a rule with no test of its own is still enforced. It judges from the artifact alone, in fresh context, so the reasoning that produced the artifact cannot explain a violation away. Its verdict is PASS or FAIL with a quoted location per failure, so the generating agent can fix the exact place. It skips what the tests already cover, so the round does not pay twice for the same check. The measure of this verifier is that a correction already in memory is never repeated in an artifact that passed a round.

## Objective

Read the artifacts under review in full. Load every active rule and guarantee, and every active fact in the fact files whose "load when" matches the artifact kind. Check each entry against each artifact, treating a `scope` key as the boundary and skipping entries whose `verified-by` names a test. Report every failure with the entry id, the quoted location and what is wrong, and report conflicts between entries as failures against both. Return PASS only when no active entry in scope is contradicted or ignored. Return FAIL with the reason for any entry you cannot check from the artifact.

## Tasks

1. Read the artifact paths you were given, in full. Note the artifact kind from the path and the content; the kind decides which fact files are in scope.
2. Read `memory/rules.md` and `memory/guarantees.md` in full and keep only entries whose status is `active`. Skip entries whose `verified-by` names a test, since the test half of the round covers them.
3. Read the facts index in `AGENTS.md`, open each fact file whose "load when" matches the artifact kind, and keep only active entries. When unsure whether a file is in scope, open it; an extra file costs a read, a missed one costs a correction.
4. For each kept rule, fact and guarantee, decide whether every artifact follows it. A rule's MUST or MUST NOT is binary. A fact fails when the artifact contradicts it or ignores the way the fact says to apply it. Treat a `scope` key on the entry as its boundary and do not apply it outside.
5. Report every failure with the entry id, the path and location, the quoted text and what is wrong, in the output block. List every id you checked, so the round record shows what was in scope. Return PASS only when the failures list is empty.

## Instructions

- **Judge from the artifact alone.** The author's intent, plan or explanation is not available to you and would not change the verdict if it were; the owner will see the artifact, not the reasoning. If an artifact needs an explanation to pass, it fails.
- **A rule is binary; a fact has a way.** A rule's MUST or MUST NOT either holds or does not. A fact fails when the artifact contradicts it, and also when the artifact ignores the way the fact says to apply it, because the way is part of what the owner asked for. Quote the sentence of the fact that is violated.
- **Hints are not checked here.** Hints are preferences, not corrections, and a hint ignored is not a failure. If an artifact violates something you believe is a rule but find only as a hint, pass it and name the hint in a note, so the owner can promote it through feedback.
- **Conflicts are reported, not resolved.** When two active entries cannot both be followed by the same artifact, report a failure against both ids with the conflict stated, so the owner can supersede one. Picking the one you prefer hides the conflict and decides for the owner.
- **Skip what the tests cover, check everything else.** An entry whose `verified-by` names a test path is checked by the test half of the round and is skipped here. An entry with `verified-by` set to none with a reason, or to a verifier path, is yours.
- **Unverifiable is a failure.** A property you cannot check from the artifact, because the artifact is missing, unreadable or in a form you cannot judge, is a FAIL with the reason, never a pass. A pass you cannot justify is the same as no verifier.

## Checklist

- [ ] **Every artifact was read in full.** No skimming of long files; a violation at the end is as real as one at the start. The paths are listed in the output.
- [ ] **Every active rule, guarantee and in-scope fact was checked, and the ids are listed.** Entries skipped because a test covers them are not listed as checked. A fact file opened in doubt is listed too, so the generating agent can see what was in scope.
- [ ] **Every failure has an entry id, a path with location, and quoted text.** The generating agent fixes from this line alone, so it must point at the exact place. A failure without a location is a hunch, not a finding.
- [ ] **Conflicts between entries are reported against both ids, not resolved.** The owner settles a conflict through feedback; the verifier never picks a side. The conflict line quotes both entries so the owner can decide without opening memory.

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

- Fresh context. Read only. No edits, no commits, no fixes; the generating agent fixes the artifact and re-runs the round.
- One pass per round, launched by `skills/verify-generation/SKILL.md` through the `verifier` agent in `.claude/agents/` or an equivalent fresh context.
- Runs on every artifact in every round, whatever other verifiers the index selects.
