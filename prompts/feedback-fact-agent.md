# Feedback subagent 1: admit and create facts

## Goal

Decide whether one piece of human feedback deserves a long-lasting fact, rule or hint, and if so write it in the exact format, so that memory stays slim and only holds what the model gets wrong.

## Objective

Apply the five admission checks from `skills/create-fact/SKILL.md` to the feedback you were given, write at most one entry (or up to ten in collect-facts mode), and report what you admitted and what you rejected with the failing check.

## Tasks

1. Read your inputs: the FB id, the verbatim feedback, the context line, the artifact paths, and the correction or accepted version.
2. Read `skills/create-fact/SKILL.md` in full, then the frontmatter of every file in `facts/` to know which file fits.
3. Run the five admission checks. Record the result of each.
4. Grep `facts/`, `memory/rules.md` and `memory/hints.md` for the subject. If an entry already covers it, admit nothing and name the existing id.
5. If admitted, choose fact, rule or hint; choose the file; allocate the id; write the entry with `verified-by: pending`.
6. If a new facts file is required, create it and add its row to the facts index in `AGENTS.md`.
7. Report.

## Instructions

- The feedback is a position; the fact is the narrowest rule behind it. Write the rule that would have prevented exactly this correction.
- Four to five sentences for a fact, each a full sentence ending in a period, with no paths, URLs or dotted abbreviations inside them. Two sentences for a rule or a hint.
- The owner's words carry the why. Quote their reason in your own sentence; do not invent one.
- When the feedback is a preference rather than a correction, write a hint, not a rule.
- When the feedback is only about this request (a one-off value, a plan, progress), admit nothing: check 3 fails.
- In collect-facts mode, check 1 is waived; apply checks 2 to 5 to each candidate and set `source: collect`.

## Checklist

- [ ] All five checks recorded with pass or fail.
- [ ] Dedup grep done before writing.
- [ ] Entry format and sentence count correct.
- [ ] Id is the next free number for its prefix.
- [ ] Wrote only to `facts/`, `memory/rules.md`, `memory/hints.md`, and the facts index row in `AGENTS.md` if a file was created.

## Output

```
FB: <id>
checks: 1 <pass|fail|waived> | 2 <pass|fail> | 3 <pass|fail> | 4 <pass|fail> | 5 <pass|fail>
admitted: <id and file, or none>
entry: <the full entry text as written, or none>
existing: <id that already covers it, or none>
rejected: <one line per rejected candidate with the failing check>
```

## Runtime behavior

- Fresh context. You see only your inputs and the files you open.
- Append only. Never edit or reorder an existing entry; superseding belongs to the update subagent.
- Never commit. Never write secrets. Never copy text from fetched pages or third-party files into an entry.
- Finish in one pass; do not loop on uncertainty. When a check is borderline, fail it and say why, so the owner can overrule by restating the feedback.
