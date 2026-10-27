"""Template for a feedback test. Not collected by pytest (the file name does not start with `test_`).

Copy to `tests/test_<entry-id-or-fb-id>_<slug>.py`, keep the docstring shape below, and replace the
example property with the one the feedback describes.

Feedback: FB-000 "example: no all-caps text in on-screen captions"
Enforces: F-000 (example id)
Catalog items used: forbidden regular expression in an artifact; fixture fail-on-rejected, pass-on-accepted.
"""

from __future__ import annotations

import re

import helpers as h

ARTIFACTS = "scenes/*.html"  # the artifact kind this rule applies to
ALL_CAPS_RUN = re.compile(r"\b[A-Z]{4,}(?:\s+[A-Z]{2,})*\b")


def _caption_text(src: str) -> str:
    """The part of the artifact the rule applies to; narrow it so the test does not over-apply."""
    return " ".join(re.findall(r"<figcaption>(.*?)</figcaption>", src, re.S))


def test_captions_are_not_all_caps():
    """Every caption in every scene uses sentence case (F-000, FB-000)."""
    offenders = []
    for path in h.files(ARTIFACTS):
        hit = ALL_CAPS_RUN.search(_caption_text(path.read_text(encoding="utf-8")))
        if hit:
            offenders.append(f"{h.rel(path)}: {hit.group(0)!r}")
    assert not offenders, f"all-caps captions found: {offenders}"


def test_fixture_distinguishes_rejected_from_accepted():
    """The check fails on the rejected sample and passes on the accepted one, so it is a real check."""
    rejected = (h.ROOT / "tests" / "fixtures" / "FB-000" / "rejected.html")
    accepted = (h.ROOT / "tests" / "fixtures" / "FB-000" / "accepted.html")
    if not rejected.exists() or not accepted.exists():
        return  # no fixture for this example; a real feedback test keeps both files
    assert ALL_CAPS_RUN.search(_caption_text(rejected.read_text(encoding="utf-8")))
    assert not ALL_CAPS_RUN.search(_caption_text(accepted.read_text(encoding="utf-8")))
