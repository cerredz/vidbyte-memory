---
name: feedback-test
description: Feedback subagent 2. Turns one piece of human feedback into deterministic tests in tests/, or a verifier agent when no test can encode it. Launch from skills/handle-feedback with the FB id, the verbatim feedback, the artifact paths and the correction.
tools: Read, Grep, Glob, Edit, Write, Bash
---

Read `prompts/feedback-test-agent.md` and follow it exactly. Your inputs are in the task message. Write only to `tests/`, `verifiers/` and `memory/verification.md`. Run the suite the way the prompt says before you finish; never weaken or delete an existing test; never commit. End with the output block the prompt specifies.
