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

1. Append the feedback to `memory/feedback-log.md` as `FB-<next>` with `> verbatim:`, a `context:` line naming the run and the artifact, and `disposition: pending`.
2. Launch the three subagents, in parallel where the harness allows, each with the FB id, the verbatim text, the artifact paths, and the correction or the accepted version:
   - feedback-fact: `prompts/feedback-fact-agent.md` (writes only `facts/`, `memory/rules.md`, `memory/hints.md`)
   - feedback-test: `prompts/feedback-test-agent.md` (writes only `tests/`, `verifiers/`, `memory/verification.md`)
   - feedback-update: `prompts/feedback-update-agent.md` (edits only existing entries' status and metadata, plus `memory/failures.md`, `memory/decisions.md`, `memory/open-questions.md`, `memory/scope.md`, `memory/glossary.md`, `memory/pointers.md`, `memory/workflows.md`)
3. Read the three reports. Attach `verified-by` from the test report to the new fact or rule's metadata line, and `supersedes` links where the update report superseded an entry the fact agent replaced.
4. Replace `disposition: pending` with `disposition: fact <ids or none> | tests <paths or none> | updates <ids or none>`. When nothing was kept, write `disposition: not kept (<reason from the fact report>)`.
5. Run `python -m pytest -q tests`. Fix integrity failures in the entries just written. A new feedback test may legitimately fail against the rejected artifact; regenerate the artifact until it passes.

## Instructions

- Log before launching. The FB id is the thread that ties the three results together.
- Pass each subagent only its inputs, never this conversation. The prompts say what each may write; do not widen it.
- The fact agent decides whether anything durable exists; the test agent decides how to check it; the update agent decides what old memory the feedback changes. They do not depend on each other's output, which is why they can run at once.
- If the harness has no subagents, run the three prompts one after another in fresh context in the order fact, test, update.
- If two reports conflict (for example the fact agent writes a rule the update agent superseded), keep the owner's latest words and resolve by superseding the older entry.
- "Collect facts about X" skips the first admission check in the fact agent and may admit several facts; the other two agents still run, since collected facts need checks and may contradict old entries.

## Checklist

- [ ] FB entry exists with verbatim text and context before any subagent ran.
- [ ] Each subagent wrote only inside its scope.
- [ ] New fact or rule has `verified-by` pointing at a test, a verifier, a script, or `none (<reason>)`.
- [ ] Disposition line is filled and names every id and path created.
- [ ] `python -m pytest -q tests` passes.

## Output

One paragraph in the request report: the FB id, what was kept and where, which tests or verifiers now check it, which entries changed status, and what was dropped and why.

## Runtime behavior

- Runs inside the main request, immediately when feedback arrives, before further generation on the same artifact.
- Does not commit; the end-of-request footprint commit records the change.
- Never rewrites a memory file whole. Append entries and edit metadata lines in place.
