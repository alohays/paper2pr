#!/usr/bin/env python3
"""Check that the speaker notes mark every press of the right arrow.

A rendered deck advances on the right arrow: once per fragment on a slide
(fragments inside an inlined SVG figure count too, and the qmd does not show
them), then once more to leave the slide. A presenter reading the notes has
to know where each press goes, so the notes carry one cue per press:

    [→ k/n · what appears]   fragment k of the slide's n, on its own line,
                             before the sentence that goes with it
    [→ next slide]           last line of the note; a Korean script writes
                             the Korean for "next slide" (see NEXT below)

This script reads the rendered HTML, counts the fragments of every slide and
compares them with the cues in that slide's notes.

Usage:
    python3 scripts/check_advance_cues.py Quarto/lectures/<deck>.html
    python3 scripts/check_advance_cues.py <deck>.html --list   # every step

Exit status 1 when a slide's cues do not match its fragments.
"""
import re
import sys
from html.parser import HTMLParser

VOID = {
    "br", "img", "source", "path", "rect", "circle", "line", "polygon",
    "polyline", "ellipse", "use", "input", "meta", "link", "hr", "track",
    "stop", "wbr", "col", "embed", "area", "base", "param",
}
CUE = re.compile(r"\[→ (\d+)/(\d+)\b[^\]]*\]")
# "\ub2e4\uc74c \uc7a5" is the Korean for "next slide"; escaped because this repo keeps
# Hangul out of committed files.
NEXT = re.compile("\\[→ (\\ub2e4\\uc74c \\uc7a5|next slide)\\]")


class Deck(HTMLParser):
    """Top-level slides with their fragments (document order) and notes."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides = []
        self.in_slides = False
        self.depth = 0
        self.cur = None
        self.stack = []
        self.notes_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag == "div" and "slides" in cls:
            self.in_slides = True
        if not self.in_slides:
            return
        if tag == "section":
            self.depth += 1
            if self.depth == 1:
                # Quarto renders a title slide's data-notes to HTML paragraphs.
                raw = (a.get("data-notes") or "").replace("</p>", "\n")
                self.cur = {
                    "id": a.get("id", ""),
                    "frags": [],
                    "notes": re.sub(r"<[^>]+>", "", raw),
                }
                self.slides.append(self.cur)
                self.stack = []
            return
        if self.cur is None:
            return
        if tag in VOID:
            if "fragment" in cls and not self.notes_depth:
                self.cur["frags"].append(a.get("alt") or f"<{tag}>")
            return
        is_notes = tag == "aside" and "notes" in cls
        if is_notes:
            self.notes_depth += 1
        self.stack.append({
            "tag": tag,
            "frag": "fragment" in cls and not self.notes_depth,
            "notes": is_notes,
            "buf": [],
        })

    def handle_startendtag(self, tag, attrs):
        if tag in VOID:
            self.handle_starttag(tag, attrs)
        else:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.in_slides:
            return
        if tag == "section":
            self.depth -= 1
            if self.depth == 0:
                self.cur = None
            return
        if self.cur is None or tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] != tag:
                continue
            e = self.stack[i]
            inner = "".join(e["buf"])
            del self.stack[i:]
            if e["notes"]:
                self.notes_depth -= 1
                self.cur["notes"] += "\n" + inner
            elif e["frag"]:
                self.cur["frags"].append(re.sub(r"\s+", " ", inner).strip())
            if self.stack and not e["notes"]:
                self.stack[-1]["buf"].append(" " + inner + " ")
            break

    def handle_data(self, data):
        # Quarto puts a <style> block inside every notes aside; it is not text.
        if self.cur is not None and self.stack and self.stack[-1]["tag"] not in ("style", "script"):
            self.stack[-1]["buf"].append(data)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    show = "--list" in argv
    deck = Deck()
    with open(argv[1], encoding="utf-8") as fh:
        deck.feed(fh.read())

    problems, clicks = [], 0
    last = len(deck.slides)
    for i, s in enumerate(deck.slides, 1):
        n = len(s["frags"])
        clicks += n
        cues = [(int(k), int(t)) for k, t in CUE.findall(s["notes"])]
        want = [(k, n) for k in range(1, n + 1)]
        tail = s["notes"].strip().splitlines()[-1].strip() if s["notes"].strip() else ""
        if cues != want:
            got = ", ".join(f"{k}/{t}" for k, t in cues) or "none"
            problems.append(f"slide {i} #{s['id']}: {n} fragment(s), cues in notes: {got}")
        if i < last and not NEXT.search(tail):
            problems.append(f"slide {i} #{s['id']}: note does not end with a next-slide cue")
        if i == last and NEXT.search(s["notes"]):
            problems.append(f"slide {i} #{s['id']}: last slide carries a next-slide cue")
        if show:
            print(f"{i:3d} #{s['id']}: {n} fragment(s)")
            for k, text in enumerate(s["frags"], 1):
                print(f"      {k}/{n} {text[:80]}")

    presses = clicks + last - 1
    print(f"{last} slides, {clicks} fragments, {presses} presses of the right arrow")
    for p in problems:
        print("MISMATCH " + p)
    if not problems:
        print("OK: every press is marked in the notes")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
