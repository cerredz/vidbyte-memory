# Give OpenClaw memory that learns from your corrections

vidbyte-memory turns each correction you give OpenClaw into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

Copy the skills into the workspace `skills/` folder, or run the installer in the workspace.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** workspace `AGENTS.md`
- **Skills:** workspace `skills/`, `.agents/skills/`

## Enforcement: Advisory

Only a code plugin can request another pass (`before_agent_finalize`); planned.

Without a blocking hook, the checklist in `AGENTS.md` is the contract, kept by the agent.

## Notes

- Skills published on ClawHub are relicensed MIT-0.

## Status

Per the vendor's documentation (checked 2026-10-29); not yet tested end to end.

Vendor docs: https://github.com/openclaw/openclaw

[All agents](README.md)
