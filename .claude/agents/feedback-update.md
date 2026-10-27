---
name: feedback-update
description: Feedback subagent 3. Finds existing memory entries that one piece of human feedback contradicts, narrows or confirms, and supersedes, retires, confirms or narrows them without deleting anything. Launch from skills/handle-feedback with the FB id, the verbatim feedback, the context, the artifact paths and the correction.
tools: Read, Grep, Glob, Edit, Write, Bash
---

Read `prompts/feedback-update-agent.md` and follow it exactly. Your inputs are in the task message. Edit only metadata lines of existing entries and append new entries to `memory/` files other than rules, hints, guarantees, progress, run log and footprint. Never delete, renumber or reorder; never touch `tests/` or `verifiers/`; never commit. End with the output block the prompt specifies.
