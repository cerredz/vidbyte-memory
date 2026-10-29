# Privacy

vidbyte-memory collects nothing. It is files, tests and scripts that run on your machine, inside your repo.

- **No telemetry, no accounts, no API keys.** None of the scripts, skills, hooks or plugin manifests send data anywhere.
- **The only network call** is `scripts/install.py` downloading the template from GitHub (`codeload.github.com`) when it runs on its own rather than from a clone or plugin. It sends nothing about your repo.
- **Your memory stays in your repo.** Facts, feedback and run logs are markdown files committed to your own git remote; who can read them is decided by that repo's visibility.
- **The commit trailer.** Footprint commits end with `Memory-Template: vidbyte-memory`, which is visible to anyone who can read the repo. In public repos it lets the maintainers count adoption with GitHub commit search. Turn it off with `--no-marker` or `TEMPLATE_MARKER = ""` in `scripts/footprint.py`.
- **Agent harnesses** (Claude Code, Codex, Copilot and others) send your prompts and files to their own model providers under their own terms; vidbyte-memory does not change what they send.

Questions: open an issue at https://github.com/cerredz/vidbyte-memory/issues.
