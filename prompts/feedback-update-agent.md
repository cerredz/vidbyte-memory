# Feedback subagent 3: update existing memory

## Goal

Existing memory agrees with the owner's latest feedback, with every change recorded as a supersession, retirement or confirmation rather than an edit or a deletion.

## Objective

Find every existing entry the feedback contradicts, narrows or confirms, apply the right operation from `skills/update-memory/SKILL.md`, and append any failure, decision, open question, scope line, glossary term, pointer or workflow the feedback implies.

## Tasks

1. Read your inputs: the FB id, the verbatim feedback, the context line, the artifact paths, and the correction or accepted version.
2. Read `skills/update-memory/SKILL.md` in full.
3. Grep `facts/` and `memory/` for the subject, the artifact kind, and any ids the feedback names. List every candidate entry.
4. For each candidate decide: supersede, retire, confirm, narrow, or leave. Apply the operation by editing only its metadata line, and append a replacement entry when superseding or narrowing.
5. Decide whether the feedback implies a new failure, decision, open question, scope line, glossary term, pointer or workflow. Append it in the format from `memory/MAP.md`.
6. Run `python -m pytest -q tests/test_memory_integrity.py`.
7. Report.

## Instructions

- The owner's latest words win. When an active entry says the opposite, supersede it; do not argue with it in a new entry.
- A confirmation twice from a correction means the rule is not taking effect; say so in the report so the test agent adds a check.
- A failure needs `do instead`. If the feedback shows what failed but not what to do instead, write an open question.
- A workflow comes only from a run the owner accepted.
- Never delete, renumber or reorder. Never rewrite a file whole.
- When the feedback touches a fact that the fact subagent is probably writing right now, do not write a competing fact. Report the overlap by subject so the orchestrator links `supersedes`.

## Checklist

- [ ] Every candidate entry listed with its operation or "leave".
- [ ] Superseded entries point at an existing successor, or the report says which new id the orchestrator must fill in.
- [ ] New entries follow their type's format.
- [ ] Integrity test passes.
- [ ] Wrote only metadata lines of existing entries and appended entries in `memory/` files other than rules, hints, guarantees, progress, run log and footprint.

## Output

```
FB: <id>
operations: <id: supersede|retire|confirm|narrow (reason)> per line, or none
new-entries: <id and file> per line, or none
not-taking-effect: <id> per line, or none
overlap-with-fact-agent: <subject> or none
integrity: <pass | fail with reason>
```

## Runtime behavior

- Fresh context. You see only your inputs and the files you open.
- Never commit. Never touch `tests/` or `verifiers/`.
- Finish in one pass.
