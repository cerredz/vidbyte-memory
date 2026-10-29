# Give Codex memory that learns from your corrections

vidbyte-memory turns each correction you give Codex into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

`codex plugin marketplace add cerredz/vidbyte-memory`, then `codex plugin add vidbyte-memory@vidbyte`. Or run the installer.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md` (32 KiB combined limit)
- **Skills:** `.agents/skills/`

## Enforcement: Enforced

The installer writes `.codex/hooks.json` with a Stop hook in the Claude Code format. Codex skips project hooks until you trust them: open `/hooks` once and approve it.

## Notes

- Custom agents live in `.codex/agents/*.toml`; without them the agent runs the three feedback prompts itself.

## Status

Tested on 2026-10-29: the plugin installs and is enabled in Codex 0.163.

Vendor docs: https://learn.chatgpt.com/docs/hooks

[All agents](README.md)
