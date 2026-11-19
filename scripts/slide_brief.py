"""Compare the presenter's optional deck.yml brief to actual Reveal slide sections."""
from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser


@dataclass
class Slide:
    id: str
    clips: set[str] = field(default_factory=set)
    text: list[str] = field(default_factory=list)
    seconds: str | None = None


class RenderedSlides(HTMLParser):
    """Read the reachable, leaf sections in Reveal order, including vertical stacks."""

    VOID = set("area base br col embed hr img input link meta param source track wbr".split())

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.slides = []
        self.stack = []
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        parent, slide = self.stack[-1][1:] if self.stack else ("", None)
        role = ""
        if parent == "hidden" or tag in ("style", "script", "template") or "notes" in classes:
            role, slide = "hidden", None
        elif tag == "div" and "reveal" in classes:
            role = "reveal"
        elif tag == "div" and "slides" in classes and parent == "reveal":
            role = "slides"
        elif tag == "section" and parent in ("slides", "slide"):
            if attrs.get("data-visibility") == "hidden" or "hidden" in attrs:
                role, slide = "hidden", None
            else:
                if parent == "slide" and self.slides and self.slides[-1] is slide:
                    self.slides.pop()  # the outer section is a stack
                role = "slide"
                slide = Slide(attrs.get("id", ""), seconds=attrs.get("data-seconds"))
                self.slides.append(slide)
        if slide and attrs.get("data-video-slug"):
            slide.clips.add(attrs["data-video-slug"])
        if tag not in self.VOID:
            self.stack.append((tag, role, slide))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1][2] and data.strip():
            self.stack[-1][2].text.append(data)


def required_items(brief, key, option):
    items = brief.get(key, [])
    if not isinstance(items, list):
        raise ValueError(f"brief.{key} must be a list")
    for item in items:
        if isinstance(item, str):
            item = {"slide": item}
        if (not isinstance(item, dict) or item.keys() - {"slide", option}
                or not isinstance(item.get("slide"), str) or not item["slide"].strip()):
            raise ValueError(f"brief.{key} entries need a slide ID and optional {option}")
        yield item


def check_brief(brief, slides, teaching_seconds):
    """Return actionable mismatches. Validate the schema even for an empty render."""
    if not isinstance(brief, dict) or brief.keys() - {"chapters", "demonstrations", "complete_clock"}:
        raise ValueError("brief accepts chapters, demonstrations and complete_clock")
    chapters = list(required_items(brief, "chapters", "seconds"))
    demos = list(required_items(brief, "demonstrations", "clip"))
    complete = brief.get("complete_clock", False)
    if type(complete) is not bool:
        raise ValueError("brief.complete_clock must be true or false")

    positions = {}
    for i, slide in enumerate(slides):
        positions.setdefault(slide.id, []).append(i)
    errors = []
    for item in chapters + demos:
        anchor = item["slide"]
        if len(positions.get(anchor, [])) != 1:
            errors.append(f"Required slide #{anchor} must occur exactly once in the audience deck")

    chapter_ids = [c["slide"] for c in chapters]
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("brief.chapters contains a duplicate slide ID")
    starts = [positions[c][0] for c in chapter_ids if len(positions.get(c, [])) == 1]
    if starts != sorted(starts):
        errors.append("Chapter order differs from brief.chapters")

    total = 0
    for i, chapter in enumerate(chapters):
        if "seconds" not in chapter:
            if complete:
                raise ValueError("brief.complete_clock requires seconds for every chapter")
            continue
        budget = chapter["seconds"]
        if type(budget) is not int or budget <= 0:
            raise ValueError("brief.chapters seconds must be a positive integer")
        total += budget
        if len(starts) == len(chapters) and starts == sorted(starts):
            end = starts[i + 1] if i + 1 < len(starts) else len(slides)
            times = [s.seconds for s in slides[starts[i]:end]]
            declared = [t for t in times if t is not None]
            if declared:
                if any(not t.isdecimal() for t in declared):
                    errors.append(f"Invalid data-seconds in chapter #{chapter['slide']}")
                else:
                    seconds = sum(map(int, declared))
                    if seconds > budget or (len(declared) == len(times) and seconds != budget):
                        errors.append(f"Slide timings disagree with the {budget}s budget for #{chapter['slide']}")
    if total > teaching_seconds or (complete and total != teaching_seconds):
        errors.append(f"Chapter budgets total {total}s for a {teaching_seconds}s teaching slot")

    for demo in demos:
        if "clip" in demo:
            clip = demo["clip"]
            if not isinstance(clip, str) or not clip:
                raise ValueError("brief.demonstrations clip must be a manifest slug")
            found = positions.get(demo["slide"], [])
            if len(found) == 1 and clip not in slides[found[0]].clips:
                errors.append(f"Required demonstration {clip} is missing on #{demo['slide']}")
    return errors
