#!/usr/bin/env python3
"""Assert the genre profiles actually grade differently.

A profile system that resolves cleanly but applies the same numbers to every
genre is worse than no profile system: it looks like the lecture decks are
being held to lecture standards when they are not. So the test is not "does
it load" but "does the same slide pass as a paper review and fail as a
lecture".

Usage: python3 scripts/test_profiles.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import deckprofile  # noqa: E402
from quality_score import IssueDetector  # noqa: E402

fail = 0


def check(label, condition, detail=""):
    global fail
    if condition:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))
        fail = 1


class FakeProfile:
    """Stands in for a DeckConfig without needing a deck on disk."""

    def __init__(self, name):
        raw = deckprofile._load_yaml(
            deckprofile.PROFILE_DIR / f"{name}.yml")
        self._b = raw.get("bullets", {})
        self._c = raw.get("checks", {})
        self.raw = {}

    bullets_max = property(lambda s: s._b["max_per_slide"])
    bullets_max_with_figure = property(lambda s: s._b["max_with_figure"])
    bullets_max_two_line = property(lambda s: s._b["max_two_line"])
    box_density = property(lambda s: s._c["box_density"])
    expand_acronyms = property(lambda s: s._c["expand_acronyms"])
    prior_session_callback = property(lambda s: s._c["prior_session_callback"])


FIVE_BULLETS = """---
title: probe
format:
  revealjs:
    theme: [default, clean-academic.scss]
---

## A slide with five bullets

- one
- two
- three
- four
- five
"""

print("1. The same slide is judged differently by genre")
paper = FakeProfile("paper-review")
lecture = FakeProfile("lecture")
check("paper-review allows 5 bullets",
      not [v for v in IssueDetector.check_design_density(FIVE_BULLETS, paper)
           if v["type"] == "bullet_density"])
check("lecture rejects the same 5 bullets",
      [v for v in IssueDetector.check_design_density(FIVE_BULLETS, lecture)
       if v["type"] == "bullet_density"],
      "the lecture budget is 4; if this passes, the profile is not being read")

print("2. Acronym expansion is a lecture-only requirement")
check("lecture profile turns the check on", lecture.expand_acronyms)
check("paper-review profile leaves it off", not paper.expand_acronyms)

UNEXPANDED = """---
title: probe
---

## Robots that act

- A VLA maps pixels to motion
"""
EXPANDED = """---
title: probe
---

## Robots that act

- A Vision-Language-Action (VLA) model maps pixels to motion
"""
check("bare VLA is flagged",
      any(v["type"] == "unexpanded_acronym"
          for v in IssueDetector.check_acronym_expansion(UNEXPANDED)))
check("expanded VLA is not flagged",
      not any(v["type"] == "unexpanded_acronym"
              for v in IssueDetector.check_acronym_expansion(EXPANDED)))
check("common acronyms are left alone",
      not IssueDetector.check_acronym_expansion(
          "---\ntitle: p\n---\n\n## AI and 3D\n\n- AI on a GPU\n"))

print("3. Repeat use of an acronym is shorthand, not a new violation")
REPEATED = EXPANDED + "\n## Later slide\n\n- The VLA runs at 30Hz\n"
check("only the first appearance is checked",
      not any(v["type"] == "unexpanded_acronym"
              for v in IssueDetector.check_acronym_expansion(REPEATED)))

print("4. A lecture opens by reconnecting to the session before it")
NO_CALLBACK = """---
title: probe
---

## Today

- new material

## More

- more material
"""
WITH_CALLBACK = """---
title: probe
---

## Where we left off

- last session ended on data scaling

## Today

- new material
"""
check("a deck with no callback is flagged",
      IssueDetector.check_prior_session_callback(NO_CALLBACK))
check("a deck that calls back is not",
      not IssueDetector.check_prior_session_callback(WITH_CALLBACK))

print("5. Genre defaults resolve without a deck config")
check("papers -> paper-review",
      deckprofile.GENRE_DEFAULT_PROFILE["papers"] == "paper-review")
check("lectures -> lecture",
      deckprofile.GENRE_DEFAULT_PROFILE["lectures"] == "lecture")
check("talks -> invited-talk",
      deckprofile.GENRE_DEFAULT_PROFILE["talks"] == "invited-talk")
check("every genre in _genres.txt has a default profile",
      all(g in deckprofile.GENRE_DEFAULT_PROFILE
          for g in __import__("deckpath").genres()))
check("every default profile has a file on disk",
      all(p in deckprofile.profiles()
          for p in deckprofile.GENRE_DEFAULT_PROFILE.values()))

print()
print("PASS" if not fail else "FAIL")
sys.exit(fail)
