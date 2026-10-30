# Give Hermes Agent memory that learns from your corrections

vidbyte-memory turns each correction you give Hermes Agent into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Install the gate plugin once for your user, then run the installer in each repo you want to give memory:

```bash
hermes plugins install cerredz/vidbyte-memory/integrations/hermes --enable
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
hermes skills trust
```

`hermes skills trust` lets Hermes load the memory skills from `.agents/skills/` in that repo. The plugin does nothing in folders without `memory/MAP.md`.

## What it reads

- **Instructions:** `.hermes.md`, then `AGENTS.md`, then `CLAUDE.md`
- **Skills:** `.agents/skills/` after `hermes skills trust`
- **Plugin:** `vidbyte-memory` ([source](../../integrations/hermes/))

## Enforcement: Enforced on turns that edit files

The plugin registers a `pre_verify` hook. Before Hermes finishes a turn, it runs the project's `scripts/guard.py`, and while the guard reports failing tests, pending feedback or uncommitted work, it returns the reason and Hermes keeps working.

- Hermes fires `pre_verify` only on turns where `write_file` or `patch` changed a file. A turn that edits nothing, or edits only through the terminal, is not gated.
- Hermes allows 3 continues per turn (`agent.max_verify_nudges`); the guard allows 5 blocking rounds per session.
- Hermes gives a hook 30 seconds by default, and the plugin stops the guard just before that. For a slower test suite: `hermes config set plugins.hook_callback_timeout 200`.
- The guard runs with the project's Python: its `.venv` when there is one, otherwise `python` on PATH.

## Status

Tested with a fake Hermes context against the real guard (2026-10-30); not yet run in a live Hermes session. Needs Hermes 0.21.6 or later.

Vendor docs: https://github.com/NousResearch/hermes-agent

[All agents](README.md)
