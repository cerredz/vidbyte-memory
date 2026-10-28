## What and why

<!-- What changes, and the problem it solves. Link the issue: "Closes #12". -->

## Requested by

<!-- Who asked for this, for the changelog credit: "@someone in #12", or "nobody, found while ...". -->

## Checklist

- [ ] `python scripts/footprint.py --write` then `python -m pytest -q tests` passes.
- [ ] Standard library only in `scripts/` and `tests/`; no new runtime dependency.
- [ ] `AGENTS.md` is still under 200 lines, and every skill and prompt keeps its seven sections.
- [ ] A line under `## [Unreleased]` in `CHANGELOG.md` says what changed and who asked for it.
- [ ] No footprint commits from a task repo are included.
