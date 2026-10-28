---
name: verify-generation
description: Use on every generative step. Runs 3 to 5 verification rounds with the full suite (tests plus the matching verifier agents), fixes every finding between rounds, records the rounds in progress, and refuses to call a step done while findings remain.
---

# Verify a generation

## Goal

No generative output reaches the owner without having survived the full verification suite, so the owner's past corrections are enforced before they can be repeated.

## Objective

Run the suite against the current output in rounds, fix findings between rounds, and stop only on a clean round after the minimum, or report the unresolved findings after the maximum.

## Tasks

1. Identify the artifacts the step produced or changed.
2. Load `memory/verification.md` and `verifiers/INDEX.md`; select every verifier whose trigger matches an artifact, plus `verifiers/memory-conformance.md`.
3. Round: run `python -m pytest -q tests`; then run each selected verifier in fresh context with the artifact paths, the rule texts it names, and the examples it names; collect every `FAIL` with its location.
4. Fix every finding in the artifact. Do not touch tests, verifiers or memory to make a finding go away.
5. Record the round in the table in `memory/progress.md`: step, round number, tests result, verifiers run, findings, fixed.
6. Repeat from step 3. Stop after a round with zero findings once at least 3 rounds have run, or after round 5.
7. If findings remain after round 5, list them under open items in `memory/progress.md` and report the step as not done.

## Instructions

- The full suite is both parts: the tests and the verifiers. Skipping either is not a round.
- A verifier runs as a separate agent that sees only what its file lists. In Claude Code, launch the `verifier` agent from `.claude/agents/` with the verifier path and the artifact paths. Elsewhere, start a fresh context with the verifier file as the system prompt.
- A `FAIL` the agent believes is wrong is still a finding: fix the artifact, or record the disagreement as a `Q` entry in `memory/open-questions.md` for the owner to settle; every other unresolved finding goes under open items in `memory/progress.md`. Never mark a round clean by overruling a verifier.
- Each round is a full run against the current output, not a re-check of only the last findings.
- Cite the rule or fact ids that each fix applied.

## Checklist

- [ ] Verifiers selected by trigger, plus memory-conformance.
- [ ] At least 3 rounds, at most 5.
- [ ] Every round recorded in `memory/progress.md` with its evidence.
- [ ] No test, verifier or memory file changed during the rounds.
- [ ] Unresolved findings reported, never hidden.

## Output

The progress table rows for the step, and a one-line verdict: clean after round N, or unresolved findings listed.

## Runtime behavior

- Runs inside the main request after every generative step, before the output is shown or used downstream.
- Reads memory and runs tests; fixes go to the artifact, and the only repo file it writes is `memory/progress.md`.
