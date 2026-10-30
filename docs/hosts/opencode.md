# Give OpenCode memory that learns from your corrections

vidbyte-memory turns each correction you give OpenCode into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md` (falls back to `CLAUDE.md`)
- **Skills:** `.agents/skills/`, `.claude/skills/`, `.opencode/skills/`

## Enforcement: Advisory

OpenCode's `session.idle` event cannot block; a plugin that re-prompts until the guard passes is planned.

Without a blocking hook, the checklist in `AGENTS.md` is the contract, kept by the agent.

## Notes

- Subagents live in `.opencode/agents/`.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://opencode.ai/docs/skills

[All agents](README.md)
