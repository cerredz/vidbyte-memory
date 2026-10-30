# Give Kilo Code memory that learns from your corrections

vidbyte-memory turns each correction you give Kilo Code into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer from the repo you want to give memory. When it finds Kilo (a `.kilo/` or `.kilocode/` folder, `kilo.json`, `~/.config/kilo` or `kilo` on PATH) it writes the plugin to `.kilo/plugins/vidbyte-memory.js`. Add `--agents kilo` to wire it explicitly.

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

Kilo is a fork of OpenCode but does not read `.opencode/`, so it gets its own copy of the same plugin. Commit the plugin file with the rest of the memory.

## What it reads

- **Instructions:** `AGENTS.md`
- **Skills:** `.agents/skills/`, `.kilo/skills/`
- **Plugin:** `.kilo/plugins/vidbyte-memory.js` ([source](../../integrations/opencode/index.js)), in both the Kilo CLI and the VS Code extension

## Enforcement: Enforced, through a plugin

When a session goes idle, the plugin runs `scripts/guard.py`. While the guard reports failing tests, pending feedback or uncommitted work, it sends the reason back into the same session as a new prompt. The guard stops after 5 rounds per session and the plugin after 6 continuations. Subagent sessions and interrupted turns are not gated.

## Status

Tested with a fake Kilo/OpenCode 1.x host against the real guard (2026-10-30); not yet run in a live Kilo session.

Vendor docs: https://kilo.ai/docs

[All agents](README.md)
