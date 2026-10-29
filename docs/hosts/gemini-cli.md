# Give Gemini CLI memory that learns from your corrections

vidbyte-memory turns each correction you give Gemini CLI into a slim fact, a test and a footprint commit in your repo. No API key, no database, no service.

## Install

`gemini extensions install https://github.com/cerredz/vidbyte-memory`, then run the installer in the repo.

The installer, from the repo you want to give memory:

```bash
curl -fsSL https://raw.githubusercontent.com/cerredz/vidbyte-memory/main/scripts/install.py | python3 -
```

## What it reads

- **Instructions:** `GEMINI.md`; the installer adds `@AGENTS.md` to it
- **Skills:** `.agents/skills/` (wins over `.gemini/skills/`)

## Enforcement: Enforced

The installer adds an `AfterAgent` hook to `.gemini/settings.json` that runs `scripts/guard.py --format gemini`, which answers `deny` with the reason so Gemini retries.

## Notes

- Google moved consumer plans from Gemini CLI to Antigravity CLI on 2026-06-18; Gemini CLI still serves paid API keys and Code Assist Standard and Enterprise.

## Status

Tested on 2026-10-29: `gemini extensions validate` passes on Gemini CLI 0.42.

Vendor docs: https://geminicli.com/docs/hooks/reference/

[All agents](README.md)
