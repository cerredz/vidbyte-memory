# Give Claude Code memory that learns from your corrections

vidbyte-memory turns each correction you give Claude Code into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

`/plugin install vidbyte-memory --marketplace cerredz/vidbyte-memory`, then ask Claude to install vidbyte-memory in the repo. Or run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `CLAUDE.md`, which imports `AGENTS.md`
- **Skills:** `.claude/skills/` (template) or the plugin's `skills/`

## Enforcement: Enforced

Stop hook in `.claude/settings.json`, or the plugin's `hooks/hooks.json`. Subagents in `.claude/agents/`.

## Notes

- The plugin's guard does nothing in a repo without `memory/MAP.md`, and defers to the repo's own hook when it has one.

## Status

Tested on 2026-10-29: the plugin installs and is enabled in Claude Code 2.1.312; `claude plugin validate` passes.

Vendor docs: https://code.claude.com/docs/en/plugins

[All agents](README.md)
