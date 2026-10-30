# Install everywhere (v0.2.0)

## Problem

vidbyte-memory was a template you start a new repo from. Nothing installed it into an existing repo, and no coding agent could find it: the skills sat in a root `skills/` folder that no harness scans inside a project, two of them had frontmatter YAML rejects, and the repo had no plugin manifest for any marketplace. The 2026-10-29 research into where agents live found about 38 harnesses, 22 marketplaces and 15 registries, and that two manifest formats plus one folder reach most of them.

## Decisions

1. **The repo root is the plugin.** `.claude-plugin/marketplace.json` lists one plugin with `"source": "./"` (the layout of letta-ai/claude-subconscious), and a root `plugin.json` follows Agent Plugins 1.0, whose schema allows only `$schema`, `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords` and `extensions`. Components sit at the fixed `skills/` location both formats expect.
2. **Plugins install into a harness cache, but memory lives in the repo.** So every plugin route ends in the `install-memory` skill, which runs `scripts/install.py` to copy the protocol into the repo. The installer is the single source of install logic for the plugin, the one-line command and the skill.
3. **Never overwrite.** The installer keeps every existing file and reports the ones that differ; it edits only `AGENTS.md`, `CLAUDE.md`, JSON settings files and `.gitignore`, each after a backup. A conflict on a file the memory imports (`tests/helpers.py`, the integrity test, the guard, the footprint script) stops the install with exit code 1.
4. **The installer copies from a pristine template only.** A local source must carry `.claude-plugin/plugin.json` and have no feedback entries; otherwise it downloads the tarball from GitHub. This stops a task repo's own memory from being copied into another repo.
5. **The guard finds the project, not itself.** It searches upward for `memory/MAP.md` from `CLAUDE_PROJECT_DIR`, the hook's `cwd` or the current directory, and does nothing when there is none, so the plugin's hook is inert in other repos. A plugin copy defers when the repo's `.claude/settings.json` already runs `scripts/guard.py`.
6. **One guard, four hook protocols.** `--format claude` (`decision: block`; also Codex, Copilot, Cursor, Devin CLI, Grok Build, Factory), `gemini` (`decision: deny` on `AfterAgent`), `antigravity` (`decision: continue` in `.agents/hooks.json`), `exit2`. Each format comes from the vendor's hook reference.
7. **Existing repos keep their tests.** The feedback-test naming rule now applies only to `tests/test_fb*.py`, so a repo's own `tests/test_*.py` files no longer fail the integrity test.
8. **`AGENTS.md` stays under 200 lines.** A long existing `AGENTS.md` is kept as `AGENTS.previous.md` with a pointer in the Task section instead of being folded in.

## Verification

- `python -m pytest -q tests`: 37 pass, including an end-to-end install into a scratch repo with an existing `AGENTS.md`, `CLAUDE.md` and memory file, and a second run that writes nothing.
- `claude plugin validate .` passes (one warning: `CLAUDE.md` at the plugin root is not loaded as plugin context, which is expected for a template).
- The plugin installs and is enabled in scratch configs of Claude Code 2.1.312 and Codex 0.163; `gemini extensions validate .` (0.42) and `agy plugin validate .` (1.0.8, 7 skills) pass; `npx skills add <checkout> --list` finds 7 skills.

## Not in this change

- npm and PyPI packages (`npx vidbyte-memory init`, `uvx vidbyte-memory`): need the owner's registry accounts.
- Plugins for agents whose stop event can only re-prompt (OpenCode, Kilo, Pi, Cline, Amp, OpenClaw, Hermes `pre_verify` packaging).
- An `uninstall` command; the manifest and backups make it possible.
- End-to-end hook tests that run a model turn in each agent.
