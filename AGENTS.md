# Memory-backed task repo

This repo gives an agent task-specific memory that grows from human feedback. Facts stay slim and rare, every piece of feedback becomes a fact, a deterministic test, or a memory update, every generative step is verified in rounds, and every request ends with a commit that records how the memory footprint changed. Read this file first on every request. It is an index, not the memory: open the files it points to only when their "load when" matches the work.

## Task

<!-- Owner: replace this block with the recurring task this repo serves: what it produces, for whom, and what "done" means. Keep it under 15 lines. -->

## Goal

Fewer corrections from the owner over time, with every correction captured once and enforced from then on.

## Objective

Produce the task's output while applying the facts and rules in memory, verifying each generative step with the full suite, turning every piece of feedback into memory and checks, and leaving the repo committed with the footprint change recorded.

## Runtime behavior

### Start of a request
1. Read `memory/progress.md`, `memory/guarantees.md` and `memory/rules.md`.
2. From the memory index below, open only the files whose "load when" matches this request. Do not read the rest.
3. Grep `facts/` for the subjects this request touches and read the matching fact files.
4. Write the plan into `memory/progress.md`. Assume the context may be reset at any moment, so keep progress current.

### During generation
- Every generative step gets 3 to 5 verification rounds with the full suite: `tests/` plus every verifier in `verifiers/INDEX.md` whose trigger matches the artifact. Follow `skills/verify-generation/SKILL.md`.
- Cite the id of every fact, rule or guarantee you apply, for example `R-004`.
- Never edit `facts/`, `memory/rules.md`, `memory/guarantees.md` or `tests/` as a side effect of generation. Those change only through feedback handling.

### On human feedback
- A correction, a rejection, a strong confirmation, "remember this", or "collect facts about X" triggers `skills/handle-feedback/SKILL.md`: log the feedback verbatim, launch the three feedback subagents, stitch their results, run the tests.

### End of a request
1. Run `python -m pytest -q tests`. Every test must pass. A failing test is fixed or the request is reported as unfinished, never worked around and never deleted.
2. No entry in `memory/feedback-log.md` may be left with `disposition: pending`.
3. Append one line to `memory/run-log.md`, then run `python scripts/footprint.py --commit --title "<request in a few words>"`. It regenerates `memory/footprint.md`, commits every change with the footprint delta in the message, and pushes.
4. Report what was verified, what failed, and how memory changed.

## Memory index

| File | What it holds | Load when |
|---|---|---|
| `memory/MAP.md` | The memory map: every type, its entry format, its write rule | writing to any memory file for the first time in a session |
| `memory/progress.md` | Working memory for the current request | every request, at start and at each phase |
| `memory/guarantees.md` | What the agent guarantees before ending, and what enforces each | every request |
| `memory/rules.md` | MUST and MUST NOT rules in force, each tied to a check | every request |
| `memory/hints.md` | Soft preferences and heuristics | the output is something the owner will read or see |
| `memory/failures.md` | Pitfalls: tried, failed because, do instead | choosing an approach, and when something fails |
| `memory/verification.md` | Ways to verify each kind of claim or artifact | before each verification round |
| `memory/decisions.md` | Decisions with context, consequences and status | the request touches a decided area or proposes a change |
| `memory/open-questions.md` | Unresolved questions and what would settle them | planning, and before asking the owner anything |
| `memory/scope.md` | In scope, out of scope, never do | planning, and before adding anything not asked for |
| `memory/workflows.md` | Accepted step sequences with placeholders | the request matches a workflow's trigger |
| `memory/glossary.md` | Owner vocabulary with precise meanings | a term in the request is ambiguous |
| `memory/pointers.md` | Where things live outside the repo | the request needs an external system |
| `memory/owner-profile.md` | Who the owner is and how they work | the request involves communication or a judgment call |
| `memory/examples/` | Owner-approved outputs, one file each | producing the same kind of artifact |
| `memory/feedback-log.md` | Every piece of feedback, verbatim, with its disposition | handling feedback, and auditing why a memory exists |
| `memory/run-log.md` | One line per request with its footprint delta | reporting history |
| `memory/footprint.md` | Current counts per memory type, tests and verifiers (generated) | end of request |
| `facts/` | Slim facts by subject; see the facts index | the request touches a listed subject |

## Facts index

`skills/create-fact/SKILL.md` keeps this table current, and `tests/test_memory_integrity.py` fails when a fact file is missing from it.

| File | Title | Load when |
|---|---|---|
| `facts/project.md` | Project facts | the request touches what the project is, its users or its history |
| `facts/environment.md` | Environment facts | running, building or installing anything |
| `facts/conventions.md` | Convention facts | writing or formatting any artifact |
| `facts/domain.md` | Domain facts | the request needs subject-matter knowledge the model gets wrong |
| `facts/tooling.md` | Tooling facts | using a tool, library, CLI or service |

## Skills

| Skill | Use when |
|---|---|
| `skills/handle-feedback/SKILL.md` | any human feedback arrives |
| `skills/create-fact/SKILL.md` | the feedback-fact subagent admits a fact or rule, or the owner says "collect facts" |
| `skills/create-test/SKILL.md` | turning feedback into a deterministic test |
| `skills/create-verifier/SKILL.md` | a check needs judgment a test cannot encode |
| `skills/update-memory/SKILL.md` | an existing entry must be superseded, retired, merged or confirmed |
| `skills/verify-generation/SKILL.md` | every generative step |

## Subagents and verifiers

- Feedback subagents: `prompts/feedback-fact-agent.md`, `prompts/feedback-test-agent.md`, `prompts/feedback-update-agent.md`. Claude Code wrappers live in `.claude/agents/`.
- Verification agents: `verifiers/INDEX.md` lists each verifier and the artifacts it triggers on. `verifiers/memory-conformance.md` runs on everything.
- Deterministic checks: `tests/`. `tests/README.md` explains how feedback becomes a test.

## Checklist before ending

- [ ] Every generative step had at least 3 verification rounds, or the report says which did not and why.
- [ ] `python -m pytest -q tests` passes.
- [ ] Every feedback entry has a disposition other than `pending`.
- [ ] `memory/progress.md` reflects the true state, and nothing is marked done without evidence.
- [ ] `memory/run-log.md` has this request's line, and `scripts/footprint.py --commit` ran and pushed.
- [ ] The report names what was verified, what failed, and how memory changed.

## Guarantees

The entries in `memory/guarantees.md` are enforced by `scripts/guard.py`, a Claude Code Stop hook configured in `.claude/settings.json`, and by `tests/test_memory_integrity.py`. Memory is context. The guard and the tests are the enforcement.
