#!/usr/bin/env python3
"""Capture the final fragment of each slide and check the clicker path in both directions.

A deck name or QMD always renders fresh. An HTML path uses those exact bytes. With
--url the checked site is already served on loopback. Images are numbered in
reading order; --slide ID checks a single slide and its neighboring transition.
"""
from __future__ import annotations

import argparse
import base64
import functools
import hashlib
import http.server
import json
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from contextlib import contextmanager
from pathlib import Path

import deckpath
from browser import browser_page


def resolve_html(ref: str) -> Path:
    path = Path(ref)
    if path.suffix.lower() == ".html":
        if not path.is_file():
            raise ValueError(f"no rendered HTML at {path}")
        return path.resolve()
    qmd = path.resolve() if path.suffix.lower() == ".qmd" else deckpath.find(ref).qmd
    renderer = Path(__file__).with_name("render_decks.sh")
    subprocess.run(["bash", renderer, qmd], check=True)
    return qmd.with_suffix(".html")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


@contextmanager
def local_url(html: Path, supplied: str | None = None):
    if supplied:
        yield supplied
        return
    # Match the deployment layout, including ../../Figures from a deck.
    root = next((parent.parent for parent in html.parents
                 if parent.name in {"slides", "Quarto"}), html.parent)
    handler = functools.partial(QuietHandler, directory=str(root))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            path = urllib.parse.quote(html.relative_to(root).as_posix())
            yield f"http://127.0.0.1:{server.server_port}/{path}"
        finally:
            server.shutdown()
            thread.join()


# Fragment indices are normalized by Reveal, including simultaneously revealed groups.
STATE = """(() => {
  const section = Reveal.getCurrentSlide();
  const index = Reveal.getSlides().indexOf(section);
  const fragment = Reveal.getIndices().f ?? -1;
  const remaining = !!Reveal.availableFragments().next;
  const widget = section.querySelector('.rttt-widget[data-beats]');
  const caption = widget && +widget.dataset.beats ?
    widget.querySelector('.rttt-caption')?.innerText.trim() : null;
  return {index, fragment, remaining, caption};
})()"""

# Check the real interactive state on both forward and backward key presses.
WIDGETS = """(() => {
  const slide = Reveal.getCurrentSlide();
  for (const diagram of slide.querySelectorAll('.mechanism:has(.build-step)')) {
    const step = diagram.querySelectorAll('.build-step.visible').length;
    if (diagram.dataset.step !== String(step)) return 'lecture diagram step';
  }
  return '';
})()"""

RESOURCES = """(() => {
  const slide = Reveal.getCurrentSlide();
  const visible = el => el.checkVisibility({checkOpacity: true, checkVisibilityCSS: true});
  const images = [...slide.querySelectorAll('img')].filter(visible);
  const missing = images.filter(img => !img.complete || !img.naturalWidth).length;
  if (missing) return missing + ' visible image(s)';
  if ([...document.querySelectorAll('link[rel=stylesheet]')].some(css => !css.disabled && !css.sheet))
    return 'missing stylesheet';
  const active = [...slide.querySelectorAll('video')].filter(visible);
  if (slide.dataset.backgroundVideo) {
    const bg = Reveal.getSlideBackground(Reveal.getIndices().h, Reveal.getIndices().v);
    if (bg?.querySelector('video')) active.push(bg.querySelector('video'));
    else if (!slide.dataset.backgroundPoster) return 'missing background video';
  }
  for (const v of active) {
    if (v.readyState >= 2 && v.videoWidth) continue;
    const poster = v.poster || slide.dataset.backgroundPoster;
    if (!poster) return 'video without a decoded frame';
    window.__paper2prPosters ??= new Map();
    if (!window.__paper2prPosters.has(poster)) {
      const img = new Image();
      img.src = poster;
      window.__paper2prPosters.set(poster, img);
    }
    if (!window.__paper2prPosters.get(poster).naturalWidth) return 'video without a decoded poster';
  }
  const math = [...slide.querySelectorAll('.math')].filter(visible);
  if (math.some(el => el.querySelector('.katex-error') ||
      !el.querySelector('.katex, mjx-container, .MathJax'))) return 'unrendered equation';
  if ([...document.fonts].some(face => face.status === 'error')) return 'failed web font';
  return '';
})()"""


# A caption's outer box is the title and source label the audience must see.
# Use the scaled Reveal canvas at caption-room size, including its letterbox.
CAPTIONS = """(() => {
  const slide = Reveal.getCurrentSlide();
  const canvas = Reveal.getSlidesElement().getBoundingClientRect();
  const bottom = Math.min(innerHeight, canvas.bottom);
  return [...slide.querySelectorAll('figure.video-card figcaption, .video-full > .video-caption')]
    .filter(el => el.checkVisibility({checkOpacity:true, checkVisibilityCSS:true}))
    .map(el => {
      const r = el.getBoundingClientRect();
      const outside = Math.max(0, r.bottom - bottom, Math.max(0, canvas.top) - r.top,
        Math.max(0, canvas.left) - r.left, r.right - Math.min(innerWidth, canvas.right));
      return {top:Math.round(r.top), bottom:Math.round(r.bottom),
              canvas_bottom:Math.round(bottom), outside:Math.round(outside)};
    });
})()"""


def ensure_state(state, slide, fragment):
    actual = (state["index"], state["fragment"])
    if actual != (slide, fragment):
        raise ValueError(f"navigation reached slide/fragment {actual}; expected {(slide, fragment)}")


def step(page, key):
    page.key(key)
    problem = page.evaluate(WIDGETS)
    if problem:
        raise ValueError(f"{problem} did not follow the clicker on {page.evaluate('Reveal.getCurrentSlide().id')}")
    return page.evaluate(STATE)


def capture(page, path):
    page.evaluate("document.fonts.ready.then(() => true)")
    # Reveal transitions run in wall-clock time. Wait for a settled audience frame,
    # including any animated diagram movement, before capturing it.
    time.sleep(0.65)
    if page.evaluate("!!Reveal.getCurrentSlide().querySelector('.rttt-widget[data-beats]')"):
        time.sleep(1.1)
    problem = page.evaluate(RESOURCES)
    if problem:
        page.wait_for(f"!({RESOURCES})", f"{path.stem}: {problem}", timeout=25)
    image = page.send("Page.captureScreenshot", format="png", fromSurface=True)["data"]
    path.write_bytes(base64.b64decode(image))


def shoot(html: Path, out_dir: Path, prefix: str, max_slides=None, *,
          width=1280, slide_id=None, url=None) -> list[Path]:
    html = html.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    shots = []
    captions = {}
    digest = hashlib.sha256(html.read_bytes()).hexdigest()
    with local_url(html, url) as address:
        with urllib.request.urlopen(address, timeout=12) as response:
            if hashlib.sha256(response.read()).hexdigest() != digest:
                raise ValueError("the served HTML differs from the input HTML")
        with browser_page(address, width) as page:
            slides = page.evaluate("Reveal.getSlides().map(s => ({id:s.id, pos:Reveal.getIndices(s)}))")
            ids = [slide["id"] for slide in slides]
            if not slides:
                raise ValueError("Reveal has no slides")
            if slide_id and ids.count(slide_id) != 1:
                raise ValueError(f"expected one slide with id {slide_id}")
            start = ids.index(slide_id) if slide_id else 0
            count = 1 if slide_id else min(max_slides or len(ids), len(ids))
            stop = start + count
            pos = slides[start]["pos"]
            page.evaluate(f"Reveal.slide({pos['h']},{pos.get('v', 0)},-1); Reveal.layout()")
            state = page.evaluate(STATE)
            ensure_state(state, start, -1)
            # Record the expected path from the forward walk. Reverse must retrace it,
            # including grouped fragments, vertical stacks and interactive builds.
            states = [state]
            for index in range(start, stop):
                ensure_state(state, index, -1)
                while state["remaining"]:
                    previous = state
                    state = step(page, "n")
                    ensure_state(state, index, previous["fragment"] + 1)
                    if state.get("caption") and state["caption"] == previous.get("caption"):
                        raise ValueError(f"widget caption did not advance on {ids[index]}")
                    states.append(state)
                path = out_dir / f"{prefix}-{index:02d}.png"
                capture(page, path)
                shots.append(path)
                boxes = page.evaluate(CAPTIONS)
                if boxes:
                    captions[ids[index]] = boxes
                if index + 1 < len(ids):
                    state = step(page, "n")
                    ensure_state(state, index + 1, -1)
                    states.append(state)
            for expected in reversed(states[:-1]):
                state = step(page, "p")
                ensure_state(state, expected["index"], expected["fragment"])
                if state.get("caption") != expected.get("caption"):
                    raise ValueError(f"widget caption did not rewind on {ids[state['index']]}")

    report = {"html_sha256": digest, "width": width, "height": 720,
              "total_slides": len(ids), "captured_ids": ids[start:stop],
              "forward_steps": len(states) - 1, "reverse_steps": len(states) - 1,
              "captions": captions}
    (out_dir / "browser.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"{len(shots)}/{len(ids)} final slide frames, {len(states)-1} steps each way "
          f"at {width}x720 -> {out_dir}")
    clipped = [name for name, boxes in captions.items() if any(b["outside"] > 1 for b in boxes)]
    if clipped:
        raise ValueError(f"caption clipped on {', '.join(clipped)} (see {out_dir / 'browser.json'})")
    return shots


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", help="deck name, QMD or rendered HTML")
    parser.add_argument("--out", type=Path, help="screenshot directory")
    parser.add_argument("--max", type=int, help="maximum slides to capture")
    parser.add_argument("--prefix", help="screenshot file prefix")
    parser.add_argument("--width", type=int, choices=[896, 1280], default=1280)
    parser.add_argument("--slide", help="capture one rendered slide ID")
    parser.add_argument("--url", help="URL serving the supplied HTML build")
    args = parser.parse_args(argv)
    if args.max is not None and args.max < 1:
        parser.error("--max must be positive")
    html = resolve_html(args.deck)
    out = args.out or Path(tempfile.mkdtemp(prefix="slide-shots-"))
    shoot(html, out, args.prefix or html.stem, args.max, width=args.width,
          slide_id=args.slide, url=args.url)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, deckpath.DeckNotFound, deckpath.AmbiguousDeck) as e:
        sys.exit(f"error: {e}")
