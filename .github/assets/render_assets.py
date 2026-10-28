"""Render the README demo GIF and the GitHub social preview image.

Maintainer-only: needs Pillow (`pip install pillow`); the template itself never imports this file.
Usage: python .github/assets/render_assets.py      writes demo.gif and social-preview.png next to this file

The demo replays real commands and outputs from cerredz/vidbyte-memory-example (see DEMO below); edit DEMO
when that history changes, never to show something that did not happen.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = Path("C:/Windows/Fonts")


def font(names: list[str], size: int) -> ImageFont.FreeTypeFont:
    """The first font that loads, from Windows fonts or the Linux DejaVu fallback."""
    for name in names:
        for candidate in (FONTS / name, Path("/usr/share/fonts/truetype/dejavu") / name):
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size)
    raise SystemExit(f"none of these fonts found: {names}")


SANS = ["segoeui.ttf", "DejaVuSans.ttf"]
SANS_BOLD = ["segoeuib.ttf", "DejaVuSans-Bold.ttf"]
MONO = ["CascadiaMono.ttf", "consola.ttf", "DejaVuSansMono.ttf"]

BG = (13, 17, 23)
PANEL = (22, 27, 34)
BORDER = (48, 54, 61)
TEXT = (230, 237, 243)
MUTED = (139, 148, 158)
GREEN = (63, 185, 80)
BLUE = (88, 166, 255)
YELLOW = (210, 153, 34)
PURPLE = (188, 140, 255)
RED = (248, 81, 73)

# Each step: (kind, text). kinds: "cmd" is typed after a prompt, "out" prints, "say" is a dim narration line,
# "quote" is the owner's words, "ok" / "fail" are passing and failing results, "git" is a commit line, "file" is a
# changed path, "pause" holds the frame for the given number of seconds, "clear" starts a new screen.
# CARD_COMMIT is the start of a real footprint commit subject from the example repo (2026-10-28, cut at a comma).
CARD_COMMIT = "memory: +1 facts, 1 facts superseded, +1 failures, …"
DEMO: list[tuple[str, str]] = [
    ("say", "# the owner corrected the agent once (memory/feedback-log.md, FB-002):"),
    ("quote", '"for each price though can you just intregrate it with its regular price?"'),
    ("say", "# three subagents turned it into memory and checks:"),
    ("file", "facts/domain.md                     F-002 regular rate only (supersedes F-001)"),
    ("file", "tests/test_fb002_regular_prices.py  8 tests, fixtures from real promo prices"),
    ("file", "verifiers/price-source-match.md     fetches each source_url, ties out prices"),
    ("file", "memory/open-questions.md            Q-001..Q-003 left for the owner to decide"),
    ("git", "memory: +1 facts, 1 facts superseded, ... +16 tests, +1 verifiers, +2 feedback"),
    ("pause", "2.2"),
    ("clear", ""),
    ("say", "# demo: slip the corrected mistake back into prices.csv"),
    ("cmd", "tail -1 prices.csv"),
    ("out", "openai,gpt-5.6-sol,standard,4,20,...,promo 4/20 through 2026-11-21; regular 5/30"),
    ("cmd", "python -m pytest -q tests"),
    ("fail", "FAILED tests/test_fb002_regular_prices.py::"),
    ("fail", "       test_no_row_is_priced_at_a_promotion_its_note_names"),
    ("out", "  prices.csv:8 (openai / gpt-5.6-sol / standard): the prices equal '4/20', which"),
    ("out", "  the note calls a promotion or sale; price the row at the regular rate"),
    ("fail", "2 failed, 53 passed in 0.28s"),
    ("say", "# the agent fixes the row before the owner ever sees it"),
    ("pause", "2.2"),
    ("clear", ""),
    ("say", "# the next real request: price the current Claude models"),
    ("cmd", "python -m pytest -q tests"),
    ("ok", "55 passed in 0.19s"),
    ("say", "# round 2: a fresh-context verifier finds what no test encodes"),
    ("fail", "memory-conformance FAIL  prices.csv:3  no row for claude-opus-5-5 fast mode"),
    ("out", "  its own source page prices fast mode as a premium tier: $8 / $40 per MTok"),
    ("say", "# the agent adds the row; round 3 reruns everything"),
    ("ok", "55 passed  |  memory-conformance PASS  |  price-source-match PASS (6 rows)"),
    ("cmd", 'python scripts/footprint.py --commit --title "price the current Claude models"'),
    ("git", "committed: memory: no change"),
    ("say", "# no new correction from the owner, so memory did not have to grow"),
    ("pause", "2.5"),
]


def social_preview(path: Path) -> None:
    width, height = 1280, 640
    img = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, width, 8], fill=GREEN)
    d.text((80, 70), "vidbyte-memory", font=font(SANS_BOLD, 88), fill=TEXT)
    d.text((84, 182), "Correction-driven memory for coding agents", font=font(SANS, 40), fill=BLUE)
    d.text((84, 246), "No API key, no database, no service: agent memory as files, tests", font=font(SANS, 28), fill=MUTED)
    d.text((84, 284), "and git in a repo you own.", font=font(SANS, 28), fill=MUTED)

    box = [80, 350, width - 80, 540]
    d.rounded_rectangle(box, radius=14, fill=PANEL, outline=BORDER, width=2)
    mono = font(MONO, 26)
    y = 374
    rows = [
        [("owner  ", MUTED), ("corrects the agent once", YELLOW)],
        [("agent  ", MUTED), ("fact ", TEXT), ("+ ", MUTED), ("pytest test ", GREEN), ("+ ", MUTED), ("memory update ", TEXT), ("+ ", MUTED), ("commit", BLUE)],
        [("git    ", MUTED), (CARD_COMMIT, PURPLE)],
        [("next   ", MUTED), ("the same mistake fails a test instead of reaching the owner", TEXT)],
    ]
    for row in rows:
        x = 108
        for text, color in row:
            d.text((x, y), text, font=mono, fill=color)
            x += d.textlength(text, font=mono)
        y += 40
    d.text((84, 572), "github.com/cerredz/vidbyte-memory", font=font(SANS_BOLD, 28), fill=TEXT)
    label = "For Claude Code and any AGENTS.md agent"
    small = font(SANS, 22)
    d.text((width - 80 - d.textlength(label, font=small), 578), label, font=small, fill=MUTED)
    img.save(path, optimize=True)


def demo_gif(path: Path, steps: list[tuple[str, str]]) -> None:
    width, height = 1000, 560
    mono = font(MONO, 19)
    line_h = 27
    top, left = 58, 26
    max_lines = (height - top - 18) // line_h
    fps = 10
    frames: list[Image.Image] = []
    durations: list[int] = []
    screen: list[list[tuple[str, tuple[int, int, int]]]] = []

    def render(cursor: bool = False) -> Image.Image:
        img = Image.new("RGB", (width, height), BG)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, width - 1, height - 1], radius=10, fill=BG, outline=BORDER, width=2)
        d.rectangle([2, 2, width - 3, 38], fill=PANEL)
        for i, color in enumerate((RED, YELLOW, GREEN)):
            d.ellipse([18 + i * 22, 13, 30 + i * 22, 25], fill=color)
        title = "vidbyte-memory-example  —  a correction becomes a test"
        d.text(((width - d.textlength(title, font=mono)) / 2, 9), title, font=mono, fill=MUTED)
        y = top
        for segments in screen[-max_lines:]:
            x = left
            for text, color in segments:
                d.text((x, y), text, font=mono, fill=color)
                x += d.textlength(text, font=mono)
            y += line_h
        if cursor:
            last = screen[-max_lines:][-1] if screen else []
            x = left + sum(d.textlength(t, font=mono) for t, _ in last)
            yy = top + (min(len(screen), max_lines) - 1) * line_h
            d.rectangle([x + 2, yy + 3, x + 12, yy + line_h - 5], fill=TEXT)
        return img

    def emit(ms: int, cursor: bool = False) -> None:
        frames.append(render(cursor))
        durations.append(ms)

    for kind, text in steps:
        if kind == "clear":
            screen.clear()
        elif kind == "pause":
            emit(int(float(text) * 1000))
        elif kind == "cmd":
            screen.append([("$ ", GREEN)])
            for i in range(0, len(text), 3):
                screen[-1] = [("$ ", GREEN), (text[: i + 3], TEXT)]
                emit(1000 // fps // 2, cursor=True)
            emit(350)
        else:
            color = {"out": TEXT, "say": MUTED, "quote": YELLOW, "ok": GREEN, "fail": RED, "git": PURPLE, "file": BLUE}[kind]
            screen.append([(text, color)])
            emit(220)
    emit(2500)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True, disposal=1)


def main() -> int:
    social_preview(HERE / "social-preview.png")
    print("wrote social-preview.png")
    if DEMO:
        demo_gif(HERE / "demo.gif", DEMO)
        print("wrote demo.gif")
    else:
        print("DEMO is empty; skipped demo.gif")
    return 0


if __name__ == "__main__":
    sys.exit(main())
