# Changelog

All notable changes to the vidbyte-memory template. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/). Each entry says who asked for the change, because release notes credit requesters as well as authors.

Task repos made from the template do not update themselves. When a change matters for existing task repos, its entry says which files to copy.

## [Unreleased]

## [0.1.0] - 2026-10-28

First public release. Requested by @cerredz.

### Added

- The template: `AGENTS.md` as the runtime protocol and memory index, 17 typed memory files mapped in `memory/MAP.md`, slim facts in `facts/`, six skills, three feedback subagent prompts with Claude Code wrappers, the memory-conformance verifier, the memory integrity tests, `scripts/footprint.py` and the `scripts/guard.py` Stop hook.
- Footprint commits end with a `Memory-Template: vidbyte-memory` git trailer, so public task repos made from the template can be counted with GitHub commit search. `--no-marker` leaves it out of one commit; setting `TEMPLATE_MARKER = ""` in `scripts/footprint.py` removes it for good. Existing task repos: copy `scripts/footprint.py` and `tests/test_memory_integrity.py` to get it.
- A landing-page README with a quick start, a demo, a before-and-after comparison, known limits and an FAQ.
- `llms.txt`, `context7.json` and `.devin/wiki.json`, so coding agents and their documentation indexes can read the template.
- Community files: contributing guide, code of conduct, security policy, issue forms (including "A correction didn't stick"), a pull request template and release-note categories.
- `template-ci.yml`, which tests Python 3.9 and 3.13 on Ubuntu and 3.11 on Windows, only in this repo.
- A live example, [cerredz/vidbyte-memory-example](https://github.com/cerredz/vidbyte-memory-example), made from the template.

[Unreleased]: https://github.com/cerredz/vidbyte-memory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cerredz/vidbyte-memory/releases/tag/v0.1.0
