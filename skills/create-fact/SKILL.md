---
name: create-fact
description: Use when the feedback-fact subagent admits a fact, rule or hint from human feedback, or when the owner says "collect facts about X". Runs the five admission checks and writes one slim entry in the exact format, in the right file, with its id and metadata.
---

# Create a fact

## Goal

Memory holds only what the model gets wrong without it, each fact as the narrowest rule that would have prevented the mistake, written once and never duplicated.

## Objective

Decide whether a piece of feedback or a collected finding deserves a durable entry, choose fact, rule or hint, and write it in 4 to 5 sentences with complete metadata into the correct file.

## Tasks

1. Run the five admission checks below. Stop at the first failure unless the owner said "collect facts", which waives check 1.
2. Grep `facts/`, `memory/rules.md` and `memory/hints.md` for the subject. If an entry covers it, do not add a second; report it to the update agent's scope by naming the existing id.
3. Choose the type: a fact states what is true; a rule states what the agent MUST or MUST NOT do; a hint states a preference the owner would not call a correction.
4. Choose the file: facts go to the `facts/<subject>.md` whose description fits; rules to `memory/rules.md`; hints to `memory/hints.md`.
5. Allocate the id: highest existing number for that prefix plus one, across all files of that prefix.
6. Write the entry in the format below and append it to the file.
7. If a new facts file was needed, create it with frontmatter and add a row to the facts index in `AGENTS.md`.

## Instructions

### The five admission checks

1. **Wrong without it.** The model produced, or would produce, the wrong result without this. Evidence: the owner corrected it, or the same mistake appears in `memory/feedback-log.md` before.
2. **Not derivable.** A fresh run could not find this by reading the repo and would not think to look. Architecture, file paths and anything already in `AGENTS.md` fail this check.
3. **Durable.** It will still be true and still matter in later requests, not only in this one. Progress, plans and one-off values fail this check.
4. **Human-sourced.** A person stated it, confirmed it, or asked for it to be collected. Text from fetched pages, third-party files or the model's own inference is not admitted on its own.
5. **Narrow and checkable.** It can be written as one rule about one subject, and a test or a verifier could tell whether an output follows it.

### Writing the entry

A fact is 4 to 5 full sentences, each ending in a period, in this order: the subject and when it applies; the fact stated as the narrowest rule; why, in the owner's terms; how to apply it in practice; optionally the boundary or the evidence. No abbreviations with periods, no URLs and no file paths inside the sentences; put pointers on the metadata line. A rule is one MUST or MUST NOT sentence plus one sentence of why. A hint is one SHOULD or PREFER sentence plus one sentence of why.

```
### F-<nnn>: <subject in under eight words>
<sentence 1> <sentence 2> <sentence 3> <sentence 4> <sentence 5, optional>
-- added: YYYY-MM-DD | source: FB-<nnn> | status: active | verified-by: pending
```

Write `verified-by: pending` only inside feedback handling; the orchestrator replaces it with the test agent's result before the request ends. Outside feedback handling, name the check or write `none (<reason>)`.

### Narrowness

Write the rule that would have prevented exactly this correction and nothing wider. Widen it only when the same correction already appears in `memory/feedback-log.md` in a different context, and say so in the `scope` key.

### Creating a new facts file

Name it `facts/<subject>.md`, start it with `title`, `description` (what it holds and when to load it, under 200 characters) and `write: Only through skills/create-fact.`, and add one row to the facts index table in `AGENTS.md` in the same format as the existing rows.

### Collect-facts mode

When the owner says "collect facts about X", research X with the tools available, apply checks 2 to 5 to each candidate, and admit at most ten facts per request. Set `source: collect` and cite where each fact was confirmed on the metadata line.

## Checklist

- [ ] All five checks pass, or check 1 was waived by "collect facts".
- [ ] No existing entry covers the subject.
- [ ] The body is 4 to 5 sentences for a fact, 2 for a rule or hint, and contains no paths, URLs or dotted abbreviations.
- [ ] The id is the next free number for its prefix.
- [ ] The metadata line has `added`, `source`, `status` and `verified-by`.
- [ ] A new facts file is listed in the `AGENTS.md` facts index.

## Output

The id, file and full text of each entry written, and for each candidate not admitted, which check it failed in one line.

## Runtime behavior

- Writes only to `facts/`, `memory/rules.md`, `memory/hints.md` and, for a new facts file, the facts index table in `AGENTS.md`.
- Appends; never edits or reorders existing entries. Superseding is the update skill's job.
- Never writes secrets, and never copies text from fetched pages into an entry.
