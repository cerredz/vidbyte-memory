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
# "quote" is the owner's words, "pause" holds the frame for the given number of seconds, "clear" starts a new screen.
# CARD_COMMIT is a real footprint commit subject from the example repo.
CARD_COMMIT = "memory: +1 facts, +3 tests, +1 feedback"
DEMO: list[tuple[str, str]] = []


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
    label = "Claude Code  ·  Codex  ·  Cursor  ·  any AGENTS.md agent"
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
            color = {"out": TEXT, "say": MUTED, "quote": YELLOW, "ok": GREEN, "git": PURPLE, "file": BLUE}[kind]
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
