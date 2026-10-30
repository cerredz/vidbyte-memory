# Give Pi memory that learns from your corrections

vidbyte-memory turns each correction you give Pi into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Run the installer from the repo you want to give memory. When it finds Pi (a `.pi/` folder, `~/.pi` or `pi` on PATH) it writes the extension to `.pi/extensions/vidbyte-memory.js`. Add `--agents pi` to wire it explicitly.

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

Pi loads project extensions only in trusted projects: answer **Trust** the first time `pi` opens the repo (`pi --approve` trusts it for a single run). Start Pi from the repo root, where `.pi/` is. Commit the extension file with the rest of the memory.

## What it reads

- **Instructions:** `AGENTS.md` or `CLAUDE.md`
- **Skills:** `.agents/skills/`, `.pi/skills/`
- **Extension:** `.pi/extensions/vidbyte-memory.js` ([source](../../integrations/pi/vidbyte-memory.js))

## Enforcement: Enforced, through an extension

Pi has no Stop hook, but since 0.87.0 it fires `agent_before_settle` before a run settles. The extension runs `scripts/guard.py` there, and while the guard reports failing tests, pending feedback or uncommitted work, it hands the reason back to the model and asks Pi to continue. The guard stops after 5 rounds per session, and the extension adds its own cap per settle.

- Aborted and failed runs are not gated, and neither are JSON-mode child runs (subagents).
- It looks for Python 3 as `py -3`, `python`, then `python3` on Windows, and `python3`, then `python` elsewhere; set `VIDBYTE_MEMORY_PYTHON` to choose one.
- If you also run a bridge that executes `.claude/settings.json` Stop hooks inside Pi, the guard runs twice per settle; keep one of the two.

## Status

Tested with a fake Pi host against the real guard (2026-10-30), and loaded through jiti the way Pi loads extensions; not yet run in a live Pi session. Needs Pi 0.87.0 or later.

Vendor docs: https://github.com/earendil-works/pi

[All agents](README.md)
