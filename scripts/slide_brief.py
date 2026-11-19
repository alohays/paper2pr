"""Compare the presenter's optional deck.yml brief to actual Reveal slide sections."""
from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
import re


@dataclass
class Slide:
    id: str
    clips: set[str] = field(default_factory=set)
    text: list[str] = field(default_factory=list)
    seconds: str | None = None


@dataclass
class Element:
    tag: str
    role: str = ""
    slide: Slide | None = None
    clip: str | None = None
    in_video: bool = False


class RenderedSlides(HTMLParser):
    """Read the reachable, leaf sections in Reveal order, including vertical stacks."""

    VOID = set("area base br col embed hr img input link meta param source track wbr".split())
    HIDDEN_STYLE = re.compile(r"(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\b", re.I)

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.slides = []
        self.stack = [Element("")]
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        parent = self.stack[-1]
        elem = Element(tag)
        if (parent.role == "hidden" or tag in ("style", "script", "template")
                or "notes" in classes or "hidden" in attrs or attrs.get("data-visibility") == "hidden"
                or self.HIDDEN_STYLE.search(attrs.get("style") or "")):
            elem.role = "hidden"
        elif tag == "div" and "reveal" in classes:
            elem.role = "reveal"
        elif tag == "div" and "slides" in classes and parent.role == "reveal":
            elem.role = "slides"
        elif tag == "section" and parent.role in ("slides", "slide"):
            if parent.role == "slide" and self.slides and self.slides[-1] is parent.slide:
                self.slides.pop()  # the outer section is a stack
            elem.role = "slide"
            elem.slide = Slide(attrs.get("id", ""), seconds=attrs.get("data-seconds"))
            self.slides.append(elem.slide)
        else:
            elem.slide = parent.slide

        if elem.slide:
            elem.clip = attrs.get("data-video-slug") or parent.clip
            elem.in_video = tag == "video" or parent.in_video
            source = attrs.get("src") or attrs.get("data-src")
            # A stray marker, caption or poster cannot stand in for a demo.
            if elem.clip and (
                (tag in ("video", "source") and elem.in_video and source)
                or (tag == "a" and (attrs.get("href") or "").startswith(("https://", "http://")))
                or (elem.role == "slide" and attrs.get("data-background-video"))
            ):
                elem.slide.clips.add(elem.clip)
        if tag not in self.VOID:
            self.stack.append(elem)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        slide = self.stack[-1].slide
        if slide and data.strip():
            slide.text.append(data)


def required_items(brief, key, *options):
    items = brief.get(key, [])
    if not isinstance(items, list):
        raise ValueError(f"brief.{key} must be a list")
    for item in items:
        if isinstance(item, str):
            item = {"slide": item}
        if (not isinstance(item, dict) or item.keys() - {"slide", "title", *options}
                or not isinstance(item.get("slide"), str) or not item["slide"].strip()):
            raise ValueError(f"Invalid brief.{key} entry. Use slide, title or {', '.join(options)}")
        if "title" in item and (not isinstance(item["title"], str) or not item["title"].strip()):
            raise ValueError(f"brief.{key} title must be non-empty text")
        yield item


def check_brief(brief, slides, teaching_seconds):
    """Return actionable mismatches. Validate the schema even for an empty render."""
    if not isinstance(brief, dict) or brief.keys() - {"chapters", "demonstrations", "complete_clock"}:
        raise ValueError("brief accepts chapters, demonstrations and complete_clock")
    chapters = list(required_items(brief, "chapters", "seconds"))
    demos = list(required_items(brief, "demonstrations", "clip", "chapter"))
    complete = brief.get("complete_clock", False)
    if type(complete) is not bool:
        raise ValueError("brief.complete_clock must be true or false")

    positions = {}
    for i, slide in enumerate(slides):
        positions.setdefault(slide.id, []).append(i)
    errors = []
    for anchor in dict.fromkeys(item["slide"] for item in chapters + demos):
        if len(positions.get(anchor, [])) != 1:
            errors.append(f"Required slide #{anchor} must occur exactly once in the audience deck")

    chapter_ids = [c["slide"] for c in chapters]
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("brief.chapters contains a duplicate slide ID")
    starts = [positions[c][0] for c in chapter_ids if len(positions.get(c, [])) == 1]
    if starts != sorted(starts):
        errors.append("Chapter order differs from brief.chapters")

    bounds = {}
    if len(starts) == len(chapters) and starts == sorted(starts):
        bounds = dict(zip(chapter_ids, zip(starts, starts[1:] + [len(slides)])))

    total = 0
    for chapter in chapters:
        if "seconds" not in chapter:
            if complete:
                raise ValueError("brief.complete_clock requires seconds for every chapter")
            continue
        budget = chapter["seconds"]
        if type(budget) is not int or budget <= 0:
            raise ValueError("brief.chapters seconds must be a positive integer")
        total += budget
        if chapter["slide"] in bounds:
            start, end = bounds[chapter["slide"]]
            times = [s.seconds for s in slides[start:end]]
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
        found = positions.get(demo["slide"], [])
        if "chapter" in demo:
            chapter = demo["chapter"]
            if not isinstance(chapter, str) or chapter not in chapter_ids:
                raise ValueError("brief.demonstrations chapter must name a declared chapter slide")
            if len(found) == 1 and chapter in bounds:
                start, end = bounds[chapter]
                if not start <= found[0] < end:
                    errors.append(f"Required demonstration #{demo['slide']} belongs in chapter #{chapter}")
        if "clip" in demo:
            clip = demo["clip"]
            if not isinstance(clip, str) or not clip:
                raise ValueError("brief.demonstrations clip must be a manifest slug")
            if len(found) == 1 and clip not in slides[found[0]].clips:
                errors.append(f"Required demonstration {clip} is missing on #{demo['slide']}")
    return errors
