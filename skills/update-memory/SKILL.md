---
name: update-memory
description: Use when an existing memory entry must be superseded, retired, merged or confirmed, or when a run produced a failure, decision, open question, scope boundary, glossary term, pointer or workflow. Keeps history: nothing is deleted.
---

# Update memory

## Goal

Memory stays consistent with the owner's latest words, and every change leaves a trail: the old entry, the new entry, and the link between them.

## Objective

Apply one of five operations to existing entries, or append one entry to a non-fact memory file, in the shared format, without rewriting any file whole.

## Tasks

1. Find the entries the new information touches: grep `facts/` and `memory/` for the subject, the artifact and the ids named in the feedback.
2. Pick the operation per entry: supersede, retire, confirm, narrow, or leave.
3. Apply it by editing only the metadata line of the old entry and, when needed, appending a new entry.
4. For a failure, decision, open question, scope line, glossary term, pointer or workflow, append an entry to the matching file in its format from `memory/MAP.md`.
5. Report every id touched and the operation.

## Instructions

- **Supersede** when the new information contradicts the entry: set `status: superseded` and `superseded-by: <new id>` on the old entry, and `supersedes: <old id>` on the new one. The old text stays.
- **Retire** when the entry no longer applies to anything: set `status: retired` and `reason: <why>`. The text stays.
- **Confirm** when the feedback restates an entry: set `confirmed: YYYY-MM-DD`. If the same entry is confirmed by a correction twice, report it as not taking effect, so the orchestrator adds a check through `skills/create-test/SKILL.md`.
- **Narrow** when the feedback shows the entry over-applies: supersede it with a narrower entry and set `scope`.
- **Leave** when nothing touches it.
- A workflow is written only from a run the owner accepted and has at least two steps with `{placeholders}` for the values that vary.
- A failure entry needs `do instead`; without it, write an open question instead.
- An open question closes by `superseded-by` pointing at the fact or decision that answered it.
- Never delete an entry, never renumber, never reorder.

## Checklist

- [ ] Every touched entry has one operation and its metadata keys are valid.
- [ ] Superseded entries point at an existing successor.
- [ ] New entries follow their type's body format.
- [ ] `python -m pytest -q tests/test_memory_integrity.py` passes.

## Output

A list of `id: operation (reason)` lines, and the ids of any new entries.

## Runtime behavior

- Edits only metadata lines of existing entries; appends new entries at the end of the file.
- Writes only to `memory/` files other than `rules.md`, `hints.md`, `guarantees.md`, `progress.md`, `run-log.md` and `footprint.md`, plus metadata lines in `facts/`, `memory/rules.md` and `memory/hints.md` when superseding, retiring or confirming.
- Inside feedback handling, the feedback-update subagent reports those metadata edits for the orchestrator instead of making them, because the fact and test subagents write the same files at the same time.
