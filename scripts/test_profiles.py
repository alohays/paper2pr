#!/usr/bin/env python3
"""Assert the genre profiles actually grade differently, and that the WP2
gates do what their profile switches say.

A profile system that resolves cleanly but applies the same numbers to every
genre is worse than no profile system: it looks like the lecture decks are
being held to lecture standards when they are not. So the test is not "does
it load" but "does the same slide pass as a paper review and fail as a
lecture".

Sections 6-12 cover the WP2 additions: korean_allowance resolution,
speaking_min arithmetic, the acronym matcher's hyphen cases, the dash lint,
the forbidden-term file, the level-1 heading blocker and the attribution
check, run on Quarto/_fixtures/gates/{pass,trip}.qmd (no rendering) and on
inline documents.

Usage: python3 scripts/test_profiles.py
"""
import argparse
import re
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import deckpath  # noqa: E402
import deckprofile  # noqa: E402
from quality_score import IssueDetector  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
GATES = REPO_ROOT / "Quarto" / "_fixtures" / "gates"

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

print("2. Acronym expansion is off for every shipped profile (D17), but the "
      "check still works for a profile that opts in")
# The presenter switched it off for lectures on 2026-08-19: the matcher
# cannot tell a model name from a term that needs spelling out, and the
# glosses live in the notes. The check stays available; the assertions
# below exercise it directly so a profile that turns it on gets a working
# gate.
check("lecture profile leaves the check off", not lecture.expand_acronyms)
check("paper-review profile leaves it off", not paper.expand_acronyms)
check("invited-talk profile leaves it off",
      not FakeProfile("invited-talk").expand_acronyms)

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
_defaults = deckprofile.genre_defaults()
check("papers -> paper-review", _defaults["papers"] == "paper-review")
check("lectures -> lecture", _defaults["lectures"] == "lecture")
check("talks -> invited-talk", _defaults["talks"] == "invited-talk")
# The mapping is read from the profiles' own `genre_default:`, so a genre
# added to _genres.txt without a profile claiming it shows up here rather
# than as a deck silently graded on built-in defaults.
check("every genre in _genres.txt has a default profile",
      all(g in _defaults for g in __import__("deckpath").genres()),
      f"unclaimed: {[g for g in __import__('deckpath').genres() if g not in _defaults]}")
check("every default profile has a file on disk",
      all(p in deckprofile.profiles() for p in _defaults.values()))


# ---------------------------------------------------------------------------
# WP2
# ---------------------------------------------------------------------------

def fixture(name):
    """DeckConfig for a gates fixture, resolved by path (bare names never
    find a fixture: that is deliberate, see deckprofile._fixture_deck)."""
    return deckprofile.resolve(str(GATES / f"{name}.qmd"))


print("6. korean_allowance resolves deck -> profile -> 0")
pass_cfg = fixture("pass")
trip_cfg = fixture("trip")
check("pass fixture resolves to the lecture profile by path",
      pass_cfg.profile == "lecture")
check("a lecture deck that omits the key takes the profile's 300",
      pass_cfg.korean_allowance == 300, f"got {pass_cfg.korean_allowance}")
check("a deck-level value overrides the profile (trip says 12)",
      trip_cfg.korean_allowance == 12, f"got {trip_cfg.korean_allowance}")
for name in ("DreamZero", "SUNY"):
    cfg = deckprofile.load(deckpath.find(name))
    check(f"{name} ({cfg.profile}) resolves to 0",
          cfg.korean_allowance == 0, f"got {cfg.korean_allowance}")
check("the built-in default is 0 when neither deck nor profile says",
      deckprofile.DEFAULTS["language"]["korean_allowance"] == 0)
check("bare-name lookup does not find a fixture",
      not any(d.name == "pass" for d in deckpath.all_decks()))
as_dict = pass_cfg.as_dict()
for key in ("publish", "korean_allowance", "video_min", "qa_min", "speaking_min",
            "sources", "forbidden_file", "figures_manifest"):
    check(f"as_dict exposes {key}", key in as_dict)

print("7. speaking_min = max(duration_min - video_min - qa_min, 0)")
check("pass fixture: 60 - 10 - 5 = 45",
      pass_cfg.speaking_min == 45, f"got {pass_cfg.speaking_min}")
check("trip fixture declares neither, so speaking_min == duration_min",
      trip_cfg.speaking_min == trip_cfg.duration_min == 60)


def TopOnly(raw):
    """A DeckConfig over an in-memory deck config, no files needed."""
    return deckprofile.DeckConfig(
        deck=deckpath.Deck(name="inline", genre="papers"),
        profile="paper-review", raw=raw, profile_raw={})


check("video + qa larger than the slot clamps to 0, not negative",
      TopOnly({"duration_min": 20, "video_min": 15, "qa_min": 10}).speaking_min == 0)
check("a deck that declares only video_min",
      TopOnly({"duration_min": 30, "video_min": 8}).speaking_min == 22)

print("7a. publish is a strict, deck-only public-site switch")
check("publish defaults to true", TopOnly({}).publish is True)
check("a deck may opt out explicitly",
      TopOnly({"publish": False}).publish is False)
_profile_publish = deckprofile.DeckConfig(
    deck=deckpath.Deck(name="inline", genre="papers"),
    profile="paper-review", raw={}, profile_raw={"publish": False})
check("profiles cannot opt every deck out",
      _profile_publish.publish is True)
try:
    TopOnly({"publish": "false"}).publish
    check("a non-boolean publish value is rejected", False, "no error")
except deckprofile.ConfigError as e:
    check("a non-boolean publish value is rejected",
          "publish must be true or false" in str(e), str(e))

_pub_decks = [deckpath.Deck("shown", "talks"),
              deckpath.Deck("hidden", "talks")]
_saved_all_decks = deckpath.all_decks
_saved_load = deckprofile.load
deckpath.all_decks = lambda: _pub_decks
deckprofile.load = lambda deck: TopOnly({"publish": deck.name == "shown"})
try:
    check("publishable_decks returns only opted-in decks",
          deckprofile.publishable_decks() == [_pub_decks[0]])
    check("unpublishable_decks returns only opted-out decks",
          deckprofile.unpublishable_decks() == [_pub_decks[1]])
finally:
    deckpath.all_decks = _saved_all_decks
    deckprofile.load = _saved_load

print("8. The acronym matcher keeps hyphenated and digit-suffixed names whole")
NAMES = """---
title: probe
---

## Models

- RT-2, QT-Opt, DALL-E, LAION-5B, pi0.5 and OpenVLA are names, not acronyms
- A VLA and an LLM are acronyms that need spelling out
"""
hits = [v["detail"].split('"')[1]
        for v in IssueDetector.check_acronym_expansion(NAMES)]
check("RT-2 / QT-Opt / DALL-E / LAION-5B / pi0.5 are not split and flagged",
      not any(h in ("RT", "QT", "DALL", "LAION", "E", "5B") for h in hits),
      f"flagged: {hits}")
check("VLA and LLM are still flagged, in that order",
      hits == ["VLA", "LLM"], f"flagged: {hits}")
check("an expansion still clears the flag",
      not IssueDetector.check_acronym_expansion(
          "---\ntitle: p\n---\n\n## S\n\n- A Large Language Model (LLM) and RT-2\n"))

print("9. Dash lint counts ---, --, literal em/en dashes and entities in "
      "visible text only")
pass_src = (GATES / "pass.qmd").read_text(encoding="utf-8")
trip_src = (GATES / "trip.qmd").read_text(encoding="utf-8")
check("pass.qmd has no dash expression",
      not IssueDetector.check_dash_expressions(pass_src))
dash_hits = IssueDetector.check_dash_expressions(trip_src)
by_slide = {h["slide"]: h["count"] for h in dash_hits}
check("trip.qmd: the Dash expressions slide counts --- and -- as 2",
      by_slide.get("Dash expressions") == 2, f"got {by_slide}")
check("trip.qmd: an &mdash; entity inside a raw {=html} block counts",
      by_slide.get("Raw HTML is on screen too") == 1, f"got {by_slide}")
check("trip.qmd: the HTML comment with --- on the dash slide is not counted",
      sum(by_slide.values()) == 3, f"got {by_slide}")
DASHES = """---
title: p
subtitle: has --- in the front matter, which is not a slide
---

## Rules and tables are syntax

---

| a | b |
|---|---|
| x | y |

```python
x = a -- b  # code is not visible text
```

## Notes and math are not visible

$$
a -- b
$$

::: {.notes}
--- in the notes is fine
:::

## Raw HTML

```{=html}
<style>.x{fill:var(--y)}</style>
<p style="--z: 1">one \u2014 em dash, one \u2013 en dash</p>
```
"""
hits = IssueDetector.check_dash_expressions(DASHES)
check("rules, table delimiters, code, notes, math and front matter: 0 hits "
      "on the first two slides",
      not [h for h in hits if h["slide"] != "Raw HTML"], f"got {hits}")
raw = [h for h in hits if h["slide"] == "Raw HTML"]
check("raw html: the two literal dashes count, the CSS custom properties do not",
      raw and raw[0]["count"] == 2, f"got {raw}")

print("10. The forbidden-term file: format, matching, and where it applies")
with tempfile.TemporaryDirectory() as td:
    fb = Path(td) / "x.forbidden.txt"
    fb.write_text("# a comment\n\nProject Nightjar\n  internal-only number  \n"
                  "Project Nightjar\n", encoding="utf-8")
    terms = IssueDetector.load_forbidden_terms(fb)
    check("comments and blank lines are ignored, whitespace trimmed, "
          "duplicates dropped",
          terms == ["Project Nightjar", "internal-only number"], f"got {terms}")
    trip_fb = IssueDetector.check_forbidden_terms(trip_src, GATES / "trip.forbidden.txt")
    check("trip.qmd trips both terms, case-insensitively, raw html included",
          sorted({h["term"] for h in trip_fb}) == ["Project Nightjar", "internal-only number"]
          and len(trip_fb) == 3, f"got {trip_fb}")
    check("trip.qmd: the term in the notes and in the HTML comment is not reported",
          all("notes" not in h["detail"] and "comment" not in h["detail"].lower()
              for h in trip_fb))
    check("pass.qmd (term only in its notes) is clean",
          not IssueDetector.check_forbidden_terms(pass_src, fb))
    check("a term in the front-matter title is reported (it is on the title slide)",
          IssueDetector.check_forbidden_terms(
              "---\ntitle: Project Nightjar\n---\n\n## S\n\n- x\n", fb))
check("trip's forbidden_file resolves next to the qmd; pass has none",
      trip_cfg.forbidden_file is not None and pass_cfg.forbidden_file is None)

print("11. A level-1 heading is a blocker; dividers and raw html are not")
check("trip.qmd reports the actual source line of its single level-1 heading",
      [h["line"] for h in IssueDetector.check_level1_headings(trip_src)]
      == [trip_src.splitlines().index("# A level-1 heading") + 1],
      f"got {IssueDetector.check_level1_headings(trip_src)}")
check("pass.qmd: the ## {.divider} slide is not a level-1 heading",
      not IssueDetector.check_level1_headings(pass_src))
L1 = """---
title: p
---

## Fine

```python
# a comment in code
```

```{=html}
# literal text in raw html, not a heading
```

::: {.notes}
# a heading in the notes never renders
:::

<!-- # commented out -->

#hashtag is not a heading
"""
check("code, raw html, notes, comments and #hashtag are not headings",
      not IssueDetector.check_level1_headings(L1),
      f"got {IssueDetector.check_level1_headings(L1)}")
check("profile switch: level1_heading is 'fail' on every shipped profile",
      all(deckprofile._load_yaml(deckprofile.PROFILE_DIR / f"{n}.yml")
          ["checks"]["level1_heading"] == "fail"
          for n in ("lecture", "paper-review", "invited-talk")))
check("a deck may switch it off with level1_heading: off",
      TopOnly({"checks": {"level1_heading": "off"}}).level1_heading == "off"
      and TopOnly({}).level1_heading == "fail")

print("12. Attribution: third-party figures need their source on the slide")
manifest = pass_cfg.figures_manifest
check("the fixtures' figures.yml next to the qmd is found as a fallback",
      manifest is not None and manifest.parent == GATES)
check("pass.qmd: footnoted markdown image and raw-html <img> are attributed",
      not IssueDetector.check_attribution(pass_src, manifest),
      f"got {IssueDetector.check_attribution(pass_src, manifest)}")
attr = IssueDetector.check_attribution(trip_src, manifest)
attr_slides = sorted(h["slide"].split(" {")[0] for h in attr)
check("trip.qmd: the markdown image, the background-image header and the "
      "{{< video >}} shortcode are each reported once",
      attr_slides == ["A third-party background, not attributed",
                      "A third-party clip through the shortcode, not attributed",
                      "A third-party figure, not attributed"],
      f"got {attr_slides}")
refs = IssueDetector.slide_asset_basenames([
    (1, '## T {background-image="figs/third.png"}'),
    (2, '## T2 {data-background-image="figs/x.png"}'),
    (3, '<img src="a/b.png?x=1">'),
    (4, '{{< video ../vid/c.mp4 >}}'),
    (5, '<video src=d.mp4>'),
    (6, '![](e.svg)'),
])
check("every asset reference form is recognised",
      refs == ["third.png", "x.png", "b.png", "c.mp4", "d.mp4", "e.svg"],
      f"got {refs}")
check("the source string is matched case-insensitively in a caption",
      not IssueDetector.check_attribution(
          "---\ntitle: p\n---\n\n## S\n\n![FIXTURE STUDIO still](x/placeholder-poster.jpg)\n",
          manifest))
check("paper-review leaves attribution off; lecture and invited-talk turn it on",
      not deckprofile._load_yaml(deckprofile.PROFILE_DIR / "paper-review.yml")["checks"]["attribution"]
      and all(deckprofile._load_yaml(deckprofile.PROFILE_DIR / f"{n}.yml")["checks"]["attribution"]
              for n in ("lecture", "invited-talk")))

print("13. A render that times out takes every process it spawned with it")
# `quarto` is a shell wrapper that execs deno. subprocess.run(timeout=) kills
# only the wrapper, so the renderer outlived the gate and was still free to
# write into the deck's directory after the gate had declined to judge it
# (measured 2026-08-24 on a real render: gate returned "not scored", a deno
# process was still alive). The probe below has the same shape: a wrapper
# whose grandchild would touch a file well after the timeout.
import subprocess as _sp  # noqa: E402
import tempfile as _tf  # noqa: E402

with _tf.TemporaryDirectory() as _td:
    _wrote = Path(_td) / "grandchild-wrote"
    _probe = ["/bin/sh", "-c",
              f"sh -c 'sleep 20; touch {_wrote}' & sleep 20"]
    _timed_out = False
    try:
        IssueDetector.run_with_group_timeout(_probe, cwd=_td, timeout=1.0)
    except _sp.TimeoutExpired:
        _timed_out = True
    check("the timeout still raises TimeoutExpired for the caller", _timed_out)
    _alive = _sp.run(["pgrep", "-f", str(_wrote)],
                     capture_output=True, text=True).stdout.split()
    check("no descendant of the render survives it", not _alive,
          f"still running: {_alive}")
    check("and nothing it would have written appears", not _wrote.exists())

print("14. The brief follows reachable slide IDs, demonstration clips and the teaching clock")
from slide_brief import RenderedSlides, check_brief

brief = {
    "complete_clock": True,
    "chapters": [{"slide": "open", "seconds": 40}, {"slide": "close", "seconds": 20}],
    "demonstrations": [{"slide": "open", "clip": "turn"}],
}
sample = (
    '<div class="reveal"><div class="slides"><section id="stack">'
    '<section id="open" data-seconds="40"><a data-video-slug="turn" href="https://example.org">'
    'Watch the turn</a><aside class="notes"><span data-video-slug="private"></span></aside>'
    '</section><section id="close"></section></section></div></div>'
    '<section id="backstage"></section>'
)
def matches(html, constraints=brief):
    return check_brief(constraints, RenderedSlides(html).slides, 60)

check("public links count as the named demonstration on that slide", not matches(sample))
check("chapter order and slide timing must match the brief",
      matches(sample.replace('id="open"', 'id="close"', 1).replace(
          'id="close"></section>', 'id="open"></section>'))
      and matches(sample.replace('data-seconds="40"', 'data-seconds="45"')))
check("the full teaching clock must match, including quiet video time",
      check_brief(brief, RenderedSlides(sample).slides, 61))
check("a partial allocation can leave the author time for other material",
      not matches(sample, {"chapters": [{"slide": "close", "seconds": 10}]}))
check("substituting a different clip on a required slide is detected",
      matches(sample.replace('data-video-slug="turn"', 'data-video-slug="other"')))
check("a demo assigned to a chapter cannot move outside its boundaries",
      matches(sample, {"chapters": ["open", "close"],
                       "demonstrations": [{"slide": "open", "chapter": "close"}]}))
check("an empty clip marker, poster or hidden alternative cannot satisfy a demonstration",
      all(matches(sample.replace('<a data-video-slug="turn" href="https://example.org">'
                                 'Watch the turn</a>', element)) for element in (
          '<figure data-video-slug="turn"></figure>',
          '<figure data-video-slug="turn"><img src="poster.jpg"></figure>',
          '<div hidden><video data-video-slug="turn" src="turn.mp4"></video></div>',
          '<figure data-video-slug="turn"><source src="not-a-video.mp4"></figure>',
          '<style></style><figure style="display: none" data-video-slug="turn"><video src="v"></video></figure>',
      )))
check("an actual video source or a Reveal video background counts",
      not matches(sample.replace('<a data-video-slug="turn" href="https://example.org">Watch the turn</a>',
                                 '<figure data-video-slug="turn"><video><source data-src="turn.mp4"></video></figure>'))
      and not matches(sample.replace('data-seconds="40"', 'data-seconds="40" data-video-slug="turn" data-background-video="turn.mp4"')
                      .replace('<a data-video-slug="turn"', '<a')))
check("stack containers, speaker notes and elements outside the slides cannot satisfy the brief",
      matches(sample, {"chapters": ["stack"]}) and matches(sample, {"chapters": ["backstage"]})
      and matches(sample, {"demonstrations": [{"slide": "open", "clip": "private"}]}))
check("the author can add slides and choose different examples and layouts",
      not matches(sample.replace('<section id="close">', '<section id="extra">A different example</section><section id="close">')))
check("missing and duplicate required slide IDs stop verification",
      matches(sample.replace('id="open"', 'id="missing"'))
      and matches(sample.replace('id="close"', 'id="open"')))

print("15. The source grade resolves includes and keeps measurements distinct from estimates")
from unittest.mock import patch
from quality_score import QualityScorer

with tempfile.TemporaryDirectory() as td:
    directory = Path(td)
    deck = directory / "sample.qmd"
    child = directory / "shared"
    child.mkdir()
    (child / "outer.qmd").write_text("{{< include inner.qmd >}}")
    included = directory / "inner.qmd"
    included.write_text("## A sentence -- edited\n\n- " + "words " * 30 + "\n")
    deck.write_text("---\nformat:\n  revealjs:\n    theme: clean-academic.scss\n---\n\n"
                    "{{< include shared/outer.qmd >}}")
    # The HTML argument is intentionally elsewhere. No secondary render can
    # substitute a stale sibling HTML for the actual audience copy.
    html = directory / "audience.html"
    html.write_text(sample)
    with patch.object(deckprofile, "load_for_path", return_value=pass_cfg):
        report = QualityScorer(deck, rendered=html).score_quarto()
        check("punctuation, wrapped text estimates and a callback hint leave the grade unchanged",
              report["score"] == 100 and len(report["editorial_feedback"]) >= 2)
        included.write_text("# Unintended stack\n## A slide")
        report = QualityScorer(deck, rendered=html).score_quarto()
        check("a heading in a nested include blocks with its own file and line",
              report["blocked"] and "inner.qmd:1" in report["blockers"][0]["description"])
    sentinel = "synthetic-audience-probe"
    deny = directory / "private-list"
    deny.write_text(sentinel)
    included.write_text("## A slide")
    html.write_text(sample.replace("Watch the turn", sentinel.upper()))
    for mode in ("--summary", "--json"):
        result = subprocess.run([sys.executable, str(REPO_ROOT / "scripts/quality_score.py"),
                                 str(deck), "--rendered", str(html), mode],
                                env={**os.environ, "PAPER2PR_PRIVATE_DENYLIST": str(deny)},
                                capture_output=True, text=True)
        check(f"a private match fails {mode} without quoting its value or the denylist path",
              result.returncode == 1 and sentinel not in (result.stdout + result.stderr).lower()
              and str(deny) not in result.stdout + result.stderr)

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--w13-html", type=Path, help="also replay the archived classroom render")
parser.add_argument("--w13-config", type=Path, help="compare the archived audience and slot to the brief")
parser.add_argument("--w13-before", type=Path, help="also test the superseded W13 render against the original brief")
args = parser.parse_args()
if (args.w13_before or args.w13_config) and not args.w13_html:
    parser.error("a W13 replay requires --w13-html")
if args.w13_html:
    print("16. Archived W13 survey for second-semester first-years")
    historical = deckprofile._load_yaml(GATES / "w13-brief.yml")
    plan = historical["brief"]
    clock = 60 * (historical["duration_min"] - historical["qa_min"])
    if args.w13_config:
        config = deckprofile._load_yaml(args.w13_config)
        audience = config["audience"]["description"].lower()
        check("the restored metadata preserves the introductory audience and booked slot",
              config["audience"]["assumes"] == historical["audience"]["assumes"]
              and all(term in audience for term in ("first-year", "second semester"))
              and re.search(r"no (?:prior )?mechanics or control", audience)
              and all(config[key] == historical[key] for key in ("duration_min", "qa_min", "video_min")))
    archived_html = args.w13_html.read_text()
    actual = RenderedSlides(archived_html).slides
    errors = check_brief(plan, actual, clock)
    check("10 chapters, 3,000 teaching seconds and eight demonstration requirements",
          not errors and len(plan["chapters"]) == 10 and clock == 3000
          and len(plan["demonstrations"]) == 8, "; ".join(errors))
    check("removing the history chapter fails the original brief",
          check_brief(plan, [s for s in actual if s.id != "history-asimo"], clock))
    half_demo = re.sub(r'<figure[^>]*data-video-slug="box-raise-ctrl-f"[^>]*>.*?</figure>',
                       '<figure data-video-slug="box-raise-ctrl-f"></figure>', archived_html, flags=re.S)
    check("leaving an empty second card in the Berkeley comparison fails its demonstration",
          any("box-raise-ctrl-f" in m for m in check_brief(plan, RenderedSlides(half_demo).slides, clock)))
    opening = re.search(r'<section id="atlas-opening".*?</section>', archived_html, re.S)
    moved = archived_html.replace(opening[0], "").replace('<section id="atlas-return"',
                                                          opening[0] + '<section id="atlas-return"', 1)
    check("moving the opening Atlas question beside the closing reprise fails the brief",
          any("belongs in chapter #survey-route" in m for m in
              check_brief(plan, RenderedSlides(moved).slides, clock)))
    if args.w13_before:
        earlier = RenderedSlides(args.w13_before.read_text()).slides
        missing = check_brief(plan, earlier, clock)
        check("the superseded course sequence loses required chapter and demonstration coverage",
              any("#joint-inside" in m for m in missing)
              and any("#body-quadruped" in m for m in missing))
        print(f"  Compared {len(earlier)} superseded sections to {len(actual)} restored sections")

print()
print("PASS" if not fail else "FAIL")
sys.exit(fail)
