# Give OpenCode memory that learns from your corrections

vidbyte-memory turns each correction you give OpenCode into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer from the repo you want to give memory. When it finds OpenCode (an `.opencode/` folder, `opencode.json`, `~/.config/opencode` or `opencode` on PATH) it writes the plugin to `.opencode/plugins/vidbyte-memory.js`, which OpenCode loads on its own; no npm step. Add `--agents opencode` to wire it explicitly.

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

Commit the plugin file with the rest of the memory, so the guard does not count it as uncommitted work.

## What it reads

- **Instructions:** `AGENTS.md` (falls back to `CLAUDE.md`)
- **Skills:** `.agents/skills/`, `.claude/skills/`, `.opencode/skills/`
- **Plugin:** `.opencode/plugins/vidbyte-memory.js` ([source](../../integrations/opencode/index.js))

## Enforcement: Enforced, through a plugin

OpenCode has no blocking Stop hook, so the plugin does the same job another way. When a session goes idle it runs `scripts/guard.py`, and while the guard reports failing tests, pending feedback or uncommitted work, it sends the reason back into the same session as a new prompt, with the agent the session was using. The guard stops after 5 rounds per session and the plugin after 6 continuations, so a check that cannot pass never holds the session forever.

- Subagent (child) sessions and turns you interrupt are not gated.
- One file serves OpenCode 1.x (the `event` hook on `session.idle`) and OpenCode 2.x (the `experimental.idle` session hook, which continues the same run).
- It looks for Python 3 as `py -3`, `python`, then `python3` on Windows, and `python3`, then `python` elsewhere; set `VIDBYTE_MEMORY_PYTHON` to choose one.

## Notes

- Subagents live in `.opencode/agents/`.
- The plugin also ships as `opencode-vidbyte-memory` for `"plugin": ["opencode-vidbyte-memory"]` in `opencode.json`; use one or the other, not both.

## Status

Tested with fake OpenCode 1.x and 2.x hosts against the real guard (2026-10-30); not yet run in a live OpenCode session.

Vendor docs: https://opencode.ai/docs/plugins

[All agents](README.md)
