---
name: handle-feedback
description: Use when any human feedback arrives: a correction, a rejection, a strong confirmation, "remember this", or "collect facts about X". Logs the feedback verbatim, runs the three feedback subagents, stitches their results, and runs the tests.
---

# Handle feedback

## Goal

Every piece of human feedback is captured once, verbatim, and becomes exactly what it should: a fact or rule, deterministic tests or a verifier, and updates to existing memory, with nothing left pending.

## Objective

Run the three feedback subagents with disjoint write scopes, stitch their outputs into consistent memory, and leave the suite green.

## Tasks

1. Append the feedback to `memory/feedback-log.md` in this shape, with the number being the highest existing one plus one:
   ```
   ### FB-<nnn>: <subject in under eight words>
   > verbatim: "<the owner's words>"
   context: <run, artifact path, and where it was rejected or confirmed>
   disposition: pending
   -- added: YYYY-MM-DD | source: owner | status: active
   ```
2. Launch the three subagents, in parallel where the harness allows, each with the FB id, the verbatim text, the context line, the artifact paths, and the correction or the accepted version:
   - feedback-fact (Claude Code agent `feedback-fact`; elsewhere `prompts/feedback-fact-agent.md`): writes only `facts/`, `memory/rules.md`, `memory/hints.md`, and a new row in the `AGENTS.md` facts index.
   - feedback-test (agent `feedback-test`; `prompts/feedback-test-agent.md`): writes only `tests/`, `verifiers/`, `memory/verification.md`.
   - feedback-update (agent `feedback-update`; `prompts/feedback-update-agent.md`): writes only `memory/failures.md`, `memory/decisions.md`, `memory/open-questions.md`, `memory/scope.md`, `memory/glossary.md`, `memory/pointers.md`, `memory/workflows.md`; for entries in the other two agents' files it reports the operation instead of applying it.
3. Stitch the three reports. On each new fact or rule, replace `verified-by: pending` with `tests/<file>.py::<function>` for the first test whose docstring names this FB id (the other tests are found by the FB id), or the verifier path when one was registered, or `none (<reason from the test report>)` when neither exists. Apply every operation under `for-orchestrator` in the update report by editing that entry's metadata line; for a `narrow` with no replacement from the fact agent, write the narrower entry through `skills/create-fact/SKILL.md`. Where the fact agent wrote `supersedes: <old id>`, set `status: superseded | superseded-by: <new id>` on the old entry.
4. If the update report lists `not-taking-effect` ids, or the fact report names an `existing` entry for a correction, that entry's check is missing or not catching the mistake: run `skills/create-test/SKILL.md` for it now and set its `verified-by`; if it is a hint, supersede it with a fact through `skills/create-fact/SKILL.md`.
5. Replace `disposition: pending` with `disposition: fact <ids or none> | tests <paths or none> | updates <ids or none>`, naming everything the three reports kept. Write `disposition: not kept (<reason>)` only when all three kept nothing.
6. Regenerate the rejected artifact with the new entries applied, run `python scripts/footprint.py --write`, then `python -m pytest -q tests`. Fix integrity failures in the entries just written; a new feedback test that still fails means the artifact is still wrong, so regenerate again rather than touching the test.

## Instructions

- Log before launching. The FB id is the thread that ties the three results together.
- Pass each subagent only its inputs, never this conversation. The prompts say what each may write; do not widen it.
- The fact agent decides whether anything durable exists; the test agent decides how to check it; the update agent decides what old memory the feedback changes. They do not depend on each other's output and no file is written by two of them, which is why they can run at once.
- If the harness has no subagents, run the three prompts one after another yourself, in the order fact, test, update, reading only each prompt and its inputs.
- If two reports conflict (for example the update report says to retire an entry the fact agent superseded with a new one), keep the owner's latest words: the newest entry stays active and the older one is superseded, never retired and superseded at once.
- "Collect facts about X" skips the first admission check in the fact agent and may admit several facts; the other two agents still run, since collected facts need checks and may contradict old entries.

## Checklist

- [ ] FB entry exists with verbatim text and context before any subagent ran.
- [ ] Each subagent wrote only inside its scope.
- [ ] New fact or rule has `verified-by` pointing at a test, a verifier, a script, or `none (<reason>)`.
- [ ] Every operation under `for-orchestrator` in the update report was applied.
- [ ] Disposition line is filled and names every id and path created.
- [ ] `python -m pytest -q tests` passes after `python scripts/footprint.py --write`.

## Output

One paragraph in the request report: the FB id, what was kept and where, which tests or verifiers now check it, which entries changed status, and what was dropped and why.

## Runtime behavior

- Runs inside the main request, immediately when feedback arrives, before further generation on the same artifact.
- Does not commit; the end-of-request footprint commit records the change.
- Never rewrites a memory file whole. Append entries, edit metadata lines, and replace the FB entry's `disposition:` line in place.
