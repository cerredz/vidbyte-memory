# Feedback subagent 3: update existing memory

## Goal

Existing memory agrees with the owner's latest feedback, with every change recorded as a supersession, retirement or confirmation rather than an edit or a deletion.

## Objective

Find every existing entry the feedback contradicts, narrows or confirms, decide the right operation from `skills/update-memory/SKILL.md`, apply it inside your own files and report it for the files the other two subagents are writing, and append any failure, decision, open question, scope line, glossary term, pointer or workflow the feedback implies.

## Tasks

1. Read your inputs: the FB id, the verbatim feedback, the context line, the artifact paths, and the correction or accepted version.
2. Read `skills/update-memory/SKILL.md` in full.
3. Grep `facts/` and `memory/` for the subject, the artifact kind, and any ids the feedback names. List every candidate entry.
4. For each candidate decide: supersede, retire, confirm, narrow, or leave. For an entry in `memory/failures.md`, `memory/decisions.md`, `memory/open-questions.md`, `memory/scope.md`, `memory/glossary.md`, `memory/pointers.md` or `memory/workflows.md`, apply it by editing only its metadata line and appending the replacement entry. For an entry in `facts/`, `memory/rules.md`, `memory/hints.md`, `memory/guarantees.md` or `memory/verification.md`, do not edit: list the operation under `for-orchestrator` in your output, because the fact and test subagents are writing those files right now.
5. Decide whether the feedback implies a new failure, decision, open question, scope line, glossary term, pointer or workflow. Append it in the format from `memory/MAP.md`.
6. Run the mid-feedback suite, `python -m pytest -q tests -k "not test_no_feedback_is_pending and not test_footprint_is_current"`, which leaves out the two tests that fail by design until the orchestrator finishes.
7. Report.

## Instructions

- The owner's latest words win. When an active entry says the opposite, supersede it; do not argue with it in a new entry.
- A confirmation twice from a correction means the rule is not taking effect; say so in the report so the test agent adds a check.
- A failure needs `do instead`. If the feedback shows what failed but not what to do instead, write an open question.
- A workflow comes only from a run the owner accepted.
- Never delete, renumber or reorder. Never rewrite a file whole.
- When the feedback contradicts an existing fact, rule or hint, the fact subagent writes the replacement with `supersedes`; you report `supersede` for the old id and never write a competing entry.

## Checklist

- [ ] Every candidate entry listed with its operation or "leave".
- [ ] Superseded entries point at an existing successor, or the report says which new id the orchestrator must fill in.
- [ ] New entries follow their type's format.
- [ ] Integrity test passes.
- [ ] Wrote only to `memory/failures.md`, `memory/decisions.md`, `memory/open-questions.md`, `memory/scope.md`, `memory/glossary.md`, `memory/pointers.md` and `memory/workflows.md`; every other operation is in the output, not applied.

## Output

```
FB: <id>
applied: <id: supersede|retire|confirm|narrow (reason)> per line, or none
for-orchestrator: <id: supersede|retire|confirm|narrow (reason)> per line, for entries in facts, rules, hints, guarantees and verification, or none
new-entries: <id and file> per line, or none
not-taking-effect: <id> per line, or none
overlap-with-fact-agent: <subject> or none
integrity: <pass | fail with reason>
```

## Runtime behavior

- Fresh context. You see only your inputs and the files you open.
- Never commit. Never touch `tests/`, `verifiers/`, `facts/`, `memory/rules.md`, `memory/hints.md`, `memory/guarantees.md` or `memory/verification.md`.
- Finish in one pass.
