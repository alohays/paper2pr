#!/usr/bin/env python3
"""Validate the assembled runtime files, presentation privacy and local references."""

from __future__ import annotations

import argparse
import html
import posixpath
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import deckpath
from private_terms import contains_private, private_terms
from strip_speaker_notes import count_notes

# RoboTTT supplies a local fallback after an external primary <source>.
ALLOW_MISSING = (re.compile(r"^(?:\.\./)*videos/[^/]+\.mp4$"),)
LOCAL_MEDIA = re.compile(r"(?:^|/)Figures/[^/]+/[^/]+/videos/")
REFERENCE_ATTRS = frozenset({
    "src", "href", "xlink:href", "data-src", "data-hls", "poster",
    "data-background-image", "data-background-video", "data-background-poster",
    "data-background-iframe",
})
RUNTIME_SUFFIXES = frozenset({
    ".html", ".css", ".js", ".mjs", ".json", ".svg", ".png", ".webp", ".jpg",
    ".jpeg", ".avif", ".gif", ".ico", ".woff", ".woff2", ".otf", ".ttf",
    ".eot", ".mp4", ".webm", ".mp3", ".ogg", ".wav", ".vtt", ".wasm",
})
FONT_SUFFIXES = {".eot", ".ttf", ".otf", ".woff", ".woff2"}
FONT_NOTICES = {"LICENSE", "LICENSE.txt", "OFL.txt"}
TEXT_SUFFIXES = {".html", ".css", ".js", ".mjs", ".json", ".svg", ".vtt"}
SCAN_REFS = {".html", ".css", ".svg"}
AUTHORING_NAMES = {"videos.json", "series.json", "figures.json", "package.json",
                   "package-lock.json"}
LOCAL_PATH = re.compile(
    r"""(?:file:///(?!/)|(?<![\w/])(?:/Users/|/home/|/private/var/|/var/folders/|/Volumes/|[A-Z]:[\\/]Users[\\/]))""",
    re.I,
)
CSS_URL = re.compile(
    r"""(?:\burl\(\s*(?:"([^"]*)"|'([^']*)'|([^)'"]+?))\s*\)|@import\s*["']([^"']+)["'])""",
    re.I,
)


def css_refs(value):
    for match in CSS_URL.finditer(re.sub(r"/\*.*?\*/", "", value, flags=re.S)):
        yield next((part.strip() for part in match.groups() if part is not None), "")


def srcset_refs(value):
    # A candidate URL extends to the next whitespace. An embedded data-URL
    # comma belongs to that URL. Trailing commas separate descriptorless URLs.
    while value.strip(" \t\r\n,"):
        value = value.lstrip(" \t\r\n,")
        words = value.split(None, 1)
        url = words[0]
        yield url.rstrip(",")
        value = words[1] if len(words) > 1 else ""
        if not url.endswith(","):
            value = value.partition(",")[2]


class RuntimeRefs(HTMLParser):
    """Read actual markup, including HTML-escaped attributes and inline styles."""

    def __init__(self):
        super().__init__()
        self.urls = []
        self.in_style = False
        self.video_primary = None
        self.sources = None
        self.videos = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "style":
            self.in_style = True
        if tag == "video":
            self.video_primary = False
            self.sources = []
            self.videos.append((attrs.get("data-redistribution"), self.sources))
        if attrs.get("data-background-video"):
            urls = [value.strip() for value in attrs["data-background-video"].split(",")]
            self.videos.append((attrs.get("data-redistribution"), urls))
        for key, value in attrs.items():
            if not value:
                continue
            if key in REFERENCE_ATTRS or (tag == "object" and key == "data"):
                if tag == "source" and key == "src" and self.video_primary is not None:
                    if self.video_primary and any(p.match(value) for p in ALLOW_MISSING):
                        continue
                    if value.startswith(("https://", "http://")):
                        self.video_primary = True
                if (self.sources is not None and tag in {"video", "source"}
                        and key in {"src", "data-src", "data-hls"}):
                    self.sources.append(value)
                self.urls.append(value)
            elif key in {"srcset", "data-srcset"}:
                self.urls.extend(srcset_refs(value))
            elif key in {"style", "fill", "stroke", "filter", "mask", "clip-path",
                         "marker", "marker-start", "marker-mid", "marker-end"}:
                self.urls.extend(css_refs(value))
            elif tag == "iframe" and key == "srcdoc":
                embedded = RuntimeRefs()
                embedded.feed(value)
                embedded.close()
                self.urls.extend(embedded.urls)
                self.videos.extend(embedded.videos)

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag == "video":
            self.video_primary = None
            self.sources = None

    def handle_data(self, data):
        if self.in_style:
            self.urls.extend(css_refs(data))


def is_external(url):
    return url.startswith(("#", "//")) or bool(urlsplit(url).scheme)


def refs_in(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".css":
        urls = css_refs(text)
    else:
        parser = RuntimeRefs()
        parser.feed(text)
        parser.close()
        urls = parser.urls
    refs = set()
    for raw in urls:
        raw = raw.strip()
        if raw.lower().startswith("file:") or "\\" in raw:
            raise ValueError("a runtime reference uses a local filesystem path")
        if raw and not is_external(raw):
            rel = unquote(urlsplit(raw).path)
            if rel:
                refs.add(rel)
    return sorted(refs)


def site_target(page, ref):
    """Return a site-relative path using browser URL resolution at the site root."""
    rel = posixpath.normpath(posixpath.join(posixpath.dirname(page), ref)
                             if not ref.startswith("/") else ref.lstrip("/"))
    if rel == ".." or rel.startswith("../") or "\\" in rel or "\0" in rel:
        raise ValueError("a reference escapes the site root")
    return Path(rel)


def runtime_path(path, classroom=False):
    path = Path(path)
    if any(part.startswith(".") for part in path.parts):
        return False
    if path.name in FONT_NOTICES:
        return True
    if path.suffix.lower() not in RUNTIME_SUFFIXES or path.name.lower() in AUTHORING_NAMES:
        return False
    local_clip = path.suffix.lower() in {".mp4", ".webm"}
    fixture_asset = path.parts[:3] == ("slides", "_fixtures", "assets")
    if not classroom and (LOCAL_MEDIA.search(path.as_posix()) or (local_clip and not fixture_asset)):
        return False
    return True


def check(site_root, classroom=False):
    """Check files as served. Never include the raw failing URL in diagnostics."""
    root = Path(site_root)
    checked = 0
    missing = []
    for file in sorted(root.rglob("*")):
        if file.suffix.lower() not in SCAN_REFS or not file.is_file():
            continue
        page = file.relative_to(root)
        for ref in refs_in(file):
            checked += 1
            target = site_target(page, ref)
            if LOCAL_MEDIA.search(target.as_posix()) and not classroom:
                missing.append((page.as_posix(), "local media in public output"))
            elif not runtime_path(target, classroom):
                missing.append((page.as_posix(), "reference to an authoring or private file"))
            elif not (root / target).is_file():
                missing.append((page.as_posix(), "missing local runtime asset"))
    return checked, missing


def validate_public_videos(page, text, home):
    """Authorize raw external playback and the approved URLs produced by shortcodes."""
    from media_prep import ManifestError, release_assets

    parser = RuntimeRefs()
    parser.feed(text)
    parser.close()
    approved = None
    for policy, sources in parser.videos:
        if policy == "embed-only":
            if sources and all(urlsplit(url).scheme in {"https", "http"} and urlsplit(url).netloc
                               for url in sources):
                continue
        elif policy == "release" and home is not None:
            if approved is None:
                try:
                    approved = {url for name, url in release_assets(home) if name.endswith(".mp4")}
                except (ManifestError, OSError, ValueError, KeyError, TypeError):
                    raise ValueError("could not validate approved video sources") from None
            if sources and all(url in approved for url in sources):
                continue
        elif (policy == "fixture" and page == Path("slides/_fixtures/design-test.html")
              and sources == ["assets/placeholder-video.mp4"]):
            continue
        raise ValueError("public video needs an approved manifest clip or external embed-only source")


def validate(site_root, classroom=False):
    """Verify contents as well as references; private values never enter diagnostics."""
    root = Path(site_root)
    terms = private_terms()
    count, missing = check(root, classroom)
    if missing:
        page, reason = missing[0]
        label = "a runtime file" if contains_private(page, terms) else page
        raise ValueError(f"{label}: {reason} ({len(missing)} failing references)")
    from media_prep import ManifestError, load_manifest, restricted_media_urls
    restricted = set()
    source_paths = set()
    homes = {}
    fixture = deckpath.QUARTO_DIR / "_fixtures/video/videos.yml"
    if fixture.is_file():
        homes[Path("slides/_fixtures/video/video.html")] = deckpath.find_media(str(fixture))
    for deck in deckpath.all_decks():
        if deck.videos_manifest.is_file():
            homes[Path("slides") / deck.genre / f"{deck.name}.html"] = deck.media
            try:
                restricted.update(restricted_media_urls(deck.media))
                for entry in load_manifest(deck.videos_manifest):
                    source = entry.get("source")
                    if source and ("/" in source or "\\" in source):
                        source_paths.add(source)
            except (ManifestError, OSError, ValueError, KeyError, TypeError):
                raise ValueError("could not validate media redistribution metadata") from None
    binary_private = re.compile(LOCAL_PATH.pattern.encode("ascii"), re.I)
    binary_terms = [term.encode("utf-8") for term in (*terms, *source_paths)]
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if path.is_symlink():
            raise ValueError("the audience artifact contains a symbolic link")
        if path.is_dir():
            continue
        if rel == Path(".nojekyll"):
            if path.read_text(encoding="utf-8").strip() not in {"", "Generated by Paper2PR."}:
                raise ValueError("unexpected content in the Pages marker")
            continue
        if not runtime_path(rel, classroom) or contains_private(rel.as_posix(), terms):
            raise ValueError("the audience artifact contains a private or authoring file")
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in FONT_NOTICES:
            # Raw strings can also reach image or font metadata. Classroom
            # videos live only in the ignored preview and can be much larger.
            if not classroom:
                payload = path.read_bytes()
                if binary_private.search(payload) or any(term in payload for term in binary_terms):
                    raise ValueError("private metadata in a packaged binary asset")
            continue
        text = path.read_text(encoding="utf-8")
        if contains_private(text, terms):
            raise ValueError("private denylist match in the audience artifact")
        decoded = unquote(html.unescape(text))
        if LOCAL_PATH.search(decoded) or any(source in decoded for source in source_paths):
            raise ValueError("a local filesystem path appears in the audience artifact")
        if any(url in decoded for url in restricted):
            raise ValueError("a classroom-only clip has a release reference in the audience artifact")
        if path.suffix.lower() == ".html" and not classroom:
            validate_public_videos(rel, text, homes.get(rel))
        if path.suffix.lower() == ".html" and count_notes(path):
            raise ValueError("presenter notes remain in the audience artifact")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path, nargs="?", default=Path("_site"))
    parser.add_argument("--classroom", action="store_true",
                        help="allow local playback assets in an ignored classroom preview")
    args = parser.parse_args()
    if not args.site.is_dir():
        parser.exit(2, "the audience output directory does not exist\n")
    if args.classroom and not args.site.resolve().is_relative_to(deckpath.REPO_ROOT / "exports"):
        parser.exit(2, "a classroom preview must reside in exports/\n")
    try:
        count = validate(args.site, args.classroom)
    except (ValueError, OSError) as exc:
        # OSError filenames and parser input can include private project paths.
        parser.exit(1, "asset check failed: " + safe_error(exc) + "\n")
    print(f"all {count} local references resolve; audience privacy checks passed")
    return 0


def safe_error(exc):
    try:
        terms = private_terms()
    except ValueError:
        return "cannot read a private denylist outside the checkout"
    if type(exc) is not ValueError or LOCAL_PATH.search(str(exc)) or contains_private(str(exc), terms):
        return "could not read a runtime asset or its metadata"
    return str(exc)


if __name__ == "__main__":
    sys.exit(main())
