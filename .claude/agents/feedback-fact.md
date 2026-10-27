---
name: feedback-fact
description: Feedback subagent 1. Decides whether one piece of human feedback becomes a long-lasting fact, rule or hint, and writes it in the exact format. Launch from skills/handle-feedback with the FB id, the verbatim feedback, the context, the artifact paths and the correction.
tools: Read, Grep, Glob, Edit, Write
---

Read `prompts/feedback-fact-agent.md` and follow it exactly. Your inputs are in the task message. Write only to `facts/`, `memory/rules.md`, `memory/hints.md`, and the facts index row in `AGENTS.md` when you create a new facts file. Append only; never commit. End with the output block the prompt specifies.
