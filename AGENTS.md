# Memory-backed task repo

Read this file first on every request. It is an index, not the memory: open the files it points to only when their "load when" matches the work.

## Task

(Replace this paragraph with the recurring task this repo serves: what is produced, for whom, from what inputs, and where it goes.)

## Goal

Fewer corrections from the owner over time, with every correction captured once and enforced from then on. The owner gives this repo the same kind of request again and again, and each correction they make should be the last time they make it. Memory holds the owner's corrections as slim facts and rules, loaded only when they apply, so the agent starts each request knowing what it got wrong before. Tests and verifier agents enforce those corrections on every generative step, so the agent cannot drift from them unnoticed. Every piece of feedback is handled the same way, through three subagents that decide what it becomes, so nothing the owner says is lost or half-applied. Every request ends with a commit that records how the memory footprint changed, so the owner can see the repo learning. The repo keeps score: the run log and the feedback log show whether corrections are going down.

## Objective

Produce the task's output while applying the facts, rules and guarantees in memory, citing their ids in the plan and the report. Verify each generative step with the full suite, tests and verifiers, in rounds, and stop only on a passing round within the bounds in the stopping condition below. Turn every piece of human feedback into memory and checks through the feedback skill, immediately when it arrives, before generating further on the same artifact. Keep progress current at every phase, so a reset context can resume without the owner repeating anything. Leave the repo with every test passing, no feedback pending, and every change committed and pushed with the footprint delta in the message. Report what was produced, how it was verified, what failed and how memory changed, so the owner can act on the report without opening the repo. Ask the owner only through the pausing procedure, so a question never leaves the repo in a half-finished state.

## Tasks

### Start of a request
1. Read `memory/progress.md`, `memory/guarantees.md` and `memory/rules.md`. Progress says whether a previous context left this request half done; guarantees and rules apply to every request.
2. From the memory index below, open only the files whose "load when" matches this request. Do not read the rest; an unneeded file costs context on every request and teaches nothing.
3. Grep `facts/` for the subjects this request touches and read the matching fact files in full. A fact that is not loaded is a correction about to be repeated.
4. Write the plan into `memory/progress.md`, citing the ids of the facts, rules and guarantees it applies, before producing anything. The plan names each generative step, so the rounds table has a row to fill per step. A plan with no ids means no memory was loaded, which is worth checking before generating.

### Generation
- Every generative step gets 3 to 5 verification rounds with the full suite: `tests/` plus every verifier in `verifiers/INDEX.md` whose trigger matches the artifact. Follow `skills/verify-generation/SKILL.md`; the stopping condition below says when a step is done. Findings are fixed in the artifact, never in a test, a verifier or a memory entry.

### Human feedback
- A correction, a rejection, a strong confirmation, "remember this", or "collect facts about X" triggers `skills/handle-feedback/SKILL.md`: log the feedback verbatim, launch the three feedback subagents, stitch their results, regenerate the artifact, run the tests. Feedback is handled before any further generation on the same artifact. The owner's words are logged exactly, never paraphrased.

### Pausing for the owner
- To ask the owner anything: write the question as a `Q` entry in `memory/open-questions.md`, give every pending feedback entry a disposition (`not kept (awaiting owner, Q-nnn)` is allowed), run `python scripts/footprint.py --commit --title "<request> (paused)"`, then stop. The owner's answer arrives as feedback and is handled through the feedback skill. Pausing this way keeps the guard satisfied and the repo consistent while the question waits.

### End of a request
1. Run `python scripts/footprint.py --write`, then `python -m pytest -q tests`. Every test must pass. A failing test is fixed or the request is reported as unfinished, never worked around and never deleted.
2. No entry in `memory/feedback-log.md` may be left with `disposition: pending`. A pending entry means a piece of feedback was logged and never became anything, which is the one outcome this repo cannot allow. Finish handling it, or pause for the owner with the disposition the pausing procedure allows.
3. Run `python scripts/footprint.py --commit --title "<request in a few words>"`. It regenerates `memory/footprint.md`, appends this request's line to `memory/run-log.md`, commits every change with the footprint delta in the message, and pushes.
4. Write the report described under Output. It cites ids, so the owner can open each entry it names. A step without evidence is reported as not done.

## Stopping condition

A generative step stops when a verification round passes, and never later than round 5. A round passes when `python -m pytest -q tests` is green and every verifier selected for the artifact, including `verifiers/memory-conformance.md`, returns PASS with no findings. The first passing round on or after round 3 ends the step; a clean round 1 or 2 is followed by another full round, because a single fresh-context read is weak evidence and the extra rounds are cheap. Round 5 is the last whatever it finds: the remaining findings go under open items in `memory/progress.md`, the step is reported as not done, and the owner decides. A finding is never cleared by editing a test, a verifier or a memory entry, and a round is never marked passing by overruling a verifier; the artifact is the only thing that changes between rounds.

The request stops when the end-of-request steps above have run: the suite is green after the footprint was regenerated, no feedback is pending, and the footprint commit is pushed. In Claude Code the Stop hook in `.claude/settings.json` enforces this by blocking the end of the turn while any of the three is unmet, at most 5 times in a row per session; after that it lets the turn end with a message that the request is not finished. The same cap applies by hand without the hook: five attempts at the end-of-request steps, then the report says what is unfinished and why.

## Instructions

- **Cite the id of every fact, rule or guarantee you apply**, for example `R-004`, in the plan in `memory/progress.md` and in the report. The citations are how the owner sees that memory is being used and which entries earn their place. A step that applied no id either needed no memory or missed some, and the report says which. An entry that is never cited over many requests is a candidate for retirement, which the owner can only see if citations are honest.
- **Never edit `facts/`, `memory/rules.md`, `memory/guarantees.md` or `tests/` as a side effect of generation.** Those change only through feedback handling, where the owner's words are the source and the change is logged with an FB id. An agent that edits a rule to make its output pass has removed a correction the owner paid for. The integrity test checks that every entry cites a source, and the guard blocks a request that leaves such an edit uncommitted.
- **Keep `memory/progress.md` current at each phase**, and assume the context may be reset at any moment. Write the plan before generating, each verification round before the next, and open items as they appear, so a fresh context can read the file and continue without the owner repeating anything. Progress is state, not memory: nothing in it becomes a fact or rule without going through feedback handling.
- **Nothing is marked done without evidence.** A step is done when the command and its output, or the verifier's verdict, that shows it is recorded in progress and named in the report. "Should work" and "I checked" are not evidence. A step whose evidence is missing is reported as not done, which the owner prefers to a false done.
- **Handle feedback before anything else.** When the owner corrects or confirms something, run the feedback skill before generating further on that artifact, so the next generation already uses the new memory and the owner is not corrected twice in one request. Feedback that arrives mid-step waits only for the current verification round to finish.

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
| `skills/create-fact/SKILL.md` | the feedback-fact subagent admits a fact or rule, or the owner says "collect facts" or "remember this" |
| `skills/create-test/SKILL.md` | turning feedback into a deterministic test |
| `skills/create-verifier/SKILL.md` | a check needs judgment a test cannot encode |
| `skills/update-memory/SKILL.md` | an existing entry must be superseded, retired, merged or confirmed |
| `skills/verify-generation/SKILL.md` | every generative step |
| `skills/install-memory/SKILL.md` | the owner asks to add this memory to another repo, or to repair an install |

## Subagents and verifiers

- Feedback subagents: `prompts/feedback-fact-agent.md`, `prompts/feedback-test-agent.md`, `prompts/feedback-update-agent.md`. Claude Code wrappers live in `.claude/agents/`.
- Verification agents: `verifiers/INDEX.md` lists each verifier and the artifacts it triggers on. `verifiers/memory-conformance.md` runs on everything.
- Deterministic checks: `tests/`. `tests/README.md` explains how feedback becomes a test.

## Checklist

- [ ] **Every generative step had at least 3 verification rounds and ended on a passing round, or the report says which did not and why.** The rounds table in `memory/progress.md` is the evidence, one row per round with findings and fixes. A step with findings after round 5 is listed under open items and reported as not done.
- [ ] **`python -m pytest -q tests` passes after `python scripts/footprint.py --write`.** No test was edited, skipped or deleted to get there; the order matters because the footprint test compares the file with a fresh scan. A test that cannot pass means the request is reported as unfinished.
- [ ] **Every feedback entry has a disposition other than `pending`.** Each disposition names the ids and paths that were created, or the reason nothing was kept. A request paused for the owner uses `not kept (awaiting owner, Q-nnn)`.
- [ ] **`memory/progress.md` reflects the true state, and nothing is marked done without evidence.** Open items list everything unresolved, including findings that survived round 5 and questions waiting on the owner. A fresh context could resume the request from this file alone.
- [ ] **`scripts/footprint.py --commit` ran and pushed, so `memory/run-log.md` has this request's line.** The commit message carries the footprint delta, and `git status` is clean afterwards. The guard blocks the end of the turn until this is true.

## Output

The request report: what was produced and where, what was verified and how (the rounds per step and their verdicts), what failed and what remains open, how memory changed (the footprint delta from the commit, with the ids added or superseded), each feedback entry's disposition, and any step with fewer than 3 rounds or without a passing round and why. The report cites ids, so the owner can open each entry it names.

## Runtime behavior

- Loaded on every request; `CLAUDE.md` imports it for Claude Code, and other harnesses read it as `AGENTS.md`. The indexed files are opened only when their "load when" matches, which keeps the context spent on memory proportional to the request.
- The entries in `memory/guarantees.md` are enforced by `scripts/guard.py`, a Claude Code Stop hook configured in `.claude/settings.json`, and by `tests/test_memory_integrity.py`. Memory is context; the guard and the tests are the enforcement, and a guarantee with no enforcement says so in its `verified-by`.
- Without the hook (another harness, or `.claude/settings.json` removed), the checklist above is the same contract, kept by hand, with the same five-attempt cap.
