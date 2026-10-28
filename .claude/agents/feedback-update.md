---
name: feedback-update
description: Feedback subagent 3. Finds existing memory entries that one piece of human feedback contradicts, narrows or confirms, and supersedes, retires, confirms or narrows them without deleting anything. Launch from skills/handle-feedback with the FB id, the verbatim feedback, the context, the artifact paths and the correction.
tools: Read, Grep, Glob, Edit, Write, Bash
---

Read `prompts/feedback-update-agent.md` and follow it exactly. Your inputs are in the task message. Write only to `memory/failures.md`, `memory/decisions.md`, `memory/open-questions.md`, `memory/scope.md`, `memory/glossary.md`, `memory/pointers.md` and `memory/workflows.md`; operations on entries anywhere else go in your output for the orchestrator. Never delete, renumber or reorder; never commit. End with the output block the prompt specifies.
