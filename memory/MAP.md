---
title: Memory map
description: Every memory type in this repo, what belongs in it, its entry format and its write rule. Load when writing to any memory file for the first time in a session, or when unsure where something belongs.
write: The owner, and the feedback subagents through their skills. A format changes only through an entry in decisions.md.
---

# Memory map

Memory is split into typed files so that a request loads only the kinds it needs. Each typed file starts with frontmatter (`title`, `description`, `write`) and holds entries in the shared format below. `AGENTS.md` is the index: it says what each file holds and when to load it, never the contents.

## Shared entry format

```
### <PREFIX>-<nnn>: <subject in under eight words>
<body in the type's format>
-- added: YYYY-MM-DD | source: <FB-nnn | owner | collect | run> | status: <active | superseded | retired> | verified-by: <tests/<file>.py::<test> | verifiers/<file>.md | scripts/<file>.py | none (<reason>)> | supersedes: <id> | superseded-by: <id> | confirmed: YYYY-MM-DD | reason: <text> | scope: <text>
```

- Ids are `<PREFIX>-` plus a three-digit number, allocated as the highest existing number plus one, never reused.
- The metadata line is the last line of the entry and starts with `-- `. `added`, `source` and `status` are required on every entry. `verified-by` is required on facts, rules and guarantees. Only the keys listed above are allowed.
- Supersede, never delete. The old entry gets `status: superseded` and `superseded-by: <new id>`; the new entry gets `supersedes: <old id>`. Retire with `status: retired` and a `reason`.
- Dates are ISO 8601 and absolute. Never write "yesterday", "last week" or "recently".
- Bodies hold no secrets, no credentials and no text copied from fetched pages or third-party files.
- Evidence pointers (paths, run ids, line numbers) go in the metadata line or at the end of the body, never inside the counted sentences of a fact.

## Types

| Prefix | File | Body format | Write rule |
|---|---|---|---|
| `F` | `facts/<subject>.md` | 4 to 5 full sentences: the subject and when it applies; the fact stated as the narrowest rule; why; how to apply it; optionally the boundary or evidence | only through `skills/create-fact` after the five admission checks |
| `R` | `memory/rules.md` | one MUST or MUST NOT sentence, then one sentence of why | only through `skills/create-fact`; every rule names its check |
| `H` | `memory/hints.md` | one SHOULD or PREFER sentence, then one sentence of why | feedback that is a preference, not a correction |
| `G` | `memory/guarantees.md` | "Before ending, the agent ..." plus how it is enforced | the owner, or a decision entry |
| `X` | `memory/failures.md` | `tried:` / `failed because:` / `do instead:` on three lines | any run where an approach failed; `do instead` is required |
| `V` | `memory/verification.md` | `claim type:` / `how to verify:` / `command or verifier:` on three lines | the feedback-test subagent and `skills/create-verifier` |
| `D` | `memory/decisions.md` | `context:` / `decision:` / `consequences:` on three lines; status `active` means accepted | the owner, or an agent with the owner's explicit decision in the feedback log |
| `Q` | `memory/open-questions.md` | the question, then one sentence on what would settle it | any run; closed by `superseded-by` pointing at the fact or decision that answered it |
| `W` | `memory/workflows.md` | `trigger:` then numbered steps with `{placeholders}`, at least two steps | only from a run the owner accepted |
| `S` | `memory/scope.md` | one line starting `in:`, `out:` or `never:` | the owner, or feedback that draws a boundary |
| `T` | `memory/glossary.md` | `<term>: <meaning in one or two sentences>` | feedback that defines a word, or a glossary request |
| `P` | `memory/pointers.md` | `<name>: <URL or path>` then one sentence on what it is for | any run that learns where something lives |
| none | `memory/owner-profile.md` | prose bullets | the owner, or feedback about how they work |
| none | `memory/examples/<slug>.md` | a three-line header (what, approved on, FB id) then the approved output | only an output the owner approved |
| `FB` | `memory/feedback-log.md` | `> verbatim:` quote; `context:` line; `disposition:` line | `skills/handle-feedback`, append only |
| none | `memory/run-log.md` | `- YYYY-MM-DD | <request> | <footprint delta>` | `scripts/footprint.py --commit` |
| none | `memory/progress.md` | the sections already in the file | the running agent, rewritten at each phase |
| none | `memory/footprint.md` | generated table | `scripts/footprint.py` only |

## Examples

A fact:

```
### F-012: on-screen text casing in films
On-screen text in films includes captions, titles and lower thirds. It is never rendered in all capitals; sentence case with weight is used for emphasis instead. The owner reads all-caps as shouting and rejected three films for it. When a scene file sets a text style, check the casing before the first render. This applies to every film, not only launch films.
-- added: 2026-10-27 | source: FB-003 | status: active | verified-by: tests/test_f012_no_all_caps.py::test_scene_text_is_not_all_caps
```

A rule:

```
### R-004: run the full test suite before ending
The agent MUST run `python -m pytest -q tests` before reporting a request as done. A passing suite is the only evidence that the owner's past corrections still hold.
-- added: 2026-10-27 | source: owner | status: active | verified-by: scripts/guard.py
```

A feedback entry:

```
### FB-003: no all caps text
> verbatim: "no all caps text"
context: run 2026-10-27 artek-launch-v2, artifact scenes/03.html, rejected on review
disposition: fact F-012 | tests tests/test_f012_no_all_caps.py | updates none
-- added: 2026-10-27 | source: owner | status: active
```
