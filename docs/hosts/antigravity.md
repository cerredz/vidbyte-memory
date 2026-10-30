# Give Antigravity (app, `agy` CLI, IDE) memory that learns from your corrections

vidbyte-memory turns each correction you give Antigravity (app, `agy` CLI, IDE) into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

`agy plugin install https://github.com/cerredz/vidbyte-memory`, then run the installer in the repo.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `AGENTS.md` or `GEMINI.md` in any folder
- **Skills:** `.agents/skills/`

## Enforcement: Enforced

The installer writes `.agents/hooks.json` with a Stop hook that runs `scripts/guard.py --format antigravity`, which answers `continue` with the reason.

## Status

Tested on 2026-10-29: `agy plugin validate` processes all 7 skills on agy 1.0.8.

Vendor docs: https://antigravity.google/docs/hooks

[All agents](README.md)
