---
name: create-verifier
description: Use when a rule needs judgment a deterministic test cannot encode, such as tone or fit to the owner's taste. Writes a verification agent in verifiers/, registers it in verifiers/INDEX.md, and records the way to verify.
---

# Create a verifier

## Goal

Every rule that no test can check still gets checked on every verification round, by a fresh-context agent that sees only the artifact and returns a binary verdict with a location.

## Objective

Write a verifier prompt from `verifiers/_template.md` for one rule or one kind of artifact, register its trigger, and link it from the entry it enforces.

## Tasks

1. Confirm with `skills/create-test/SKILL.md` that no deterministic check covers the property.
2. Copy `verifiers/_template.md` to `verifiers/<slug>.md` and fill every section. Name the rule ids it enforces and the examples it may read.
3. Add a row to `verifiers/INDEX.md`: name, file, trigger (glob or artifact kind), rule ids.
4. Add a `V` entry to `memory/verification.md` naming the verifier.
5. Report the file path so the orchestrator can set `verified-by` on the entry.

## Instructions

- A verifier sees only the artifact under review, the rule text, and the approved examples named in its file. It never sees the generating conversation.
- The verdict is `PASS` or `FAIL`, never a score. A `FAIL` quotes the location and the rule id. A property it cannot check is a `FAIL` with the reason, never a pass.
- Keep the prompt under 80 lines. The sections are fixed: goal, objective, tasks, instructions, checklist, output, runtime behavior.
- Prefer one verifier per rule family over one verifier for everything, so a change to one rule does not touch the others.
- When a mechanical proxy becomes available later, the feedback-test subagent writes the test and the verifier is retired with `reason` on its row in the index.

## Checklist

- [ ] No deterministic check covers the property.
- [ ] Every section of the template is filled; the rule ids are named.
- [ ] Trigger in `verifiers/INDEX.md` matches the artifacts it should run on.
- [ ] `memory/verification.md` has the `V` entry.
- [ ] Verifier path reported for `verified-by`.

## Output

The verifier path, its trigger, the rule ids it enforces, and the `V` entry id.

## Runtime behavior

- Writes only to `verifiers/` and `memory/verification.md`.
- Verifiers run through `skills/verify-generation/SKILL.md`, never on their own.
