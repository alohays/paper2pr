#!/usr/bin/env python3
"""Check the published DreamZero equations and HLS playback in Chrome."""
import argparse
import json
import re
import sys

from browser import browser_page
from deckpath import find


# Wait for two distinct, actually presented frames from each player on the
# visible slide. Calling play() here would hide a broken Reveal re-entry.
FRAMES = """
Promise.all(Array.from(Reveal.getCurrentSlide().querySelectorAll('video[data-hls]'), video =>
  new Promise((resolve, reject) => {
    let firstTime, callback;
    const timer = setTimeout(() => {
      video.cancelVideoFrameCallback(callback);
      reject(new Error('HLS playback stalled on ' + Reveal.getCurrentSlide().id));
    }, 30000);
    function frame(now, metadata) {
      if (firstTime !== undefined && metadata.mediaTime > firstTime && !video.paused) {
        clearTimeout(timer);
        resolve([video.videoWidth, video.videoHeight]);
        return;
      }
      firstTime = metadata.mediaTime;
      callback = video.requestVideoFrameCallback(frame);
    }
    callback = video.requestVideoFrameCallback(frame);
  })
))
"""


def select_slide(page, slide_id):
    page.evaluate(f"""(() => {{
      const target = document.getElementById({json.dumps(slide_id)});
      const {{h, v}} = Reveal.getIndices(target);
      Reveal.slide(h, v);
      if (Reveal.getCurrentSlide() !== target) throw new Error('Unexpected slide');
    }})()""")


def check(url):
    with browser_page(url) as page:
        versions = page.evaluate("""[ ['katex', window.katex?.version], ['hls.js', window.Hls?.version] ]
          .map(([name, version]) => ({name, version,
            pinned: !!version && [...document.scripts].some(s => s.src.includes('/' + name + '@' + version + '/'))}))""")
        if not all(lib["pinned"] for lib in versions):
            raise ValueError("The pinned KaTeX or hls.js library failed to load")

        math = page.evaluate("""(() => {
          const all = [...document.querySelectorAll('.slides .math')];
          return {total: all.length,
            errors: all.filter(el => !el.querySelector('.katex') || el.querySelector('.katex-error')).length};
        })()""")
        if not math["total"] or math["errors"]:
            raise ValueError(f"Rendered math check failed: {math}")

        displays = page.evaluate("""[...new Set([...document.querySelectorAll('.math.display')]
          .map(el => el.closest('section').id))]""")
        for slide_id in displays:
            select_slide(page, slide_id)
            page.evaluate("document.fonts.ready")
            inside = page.evaluate("""[...Reveal.getCurrentSlide().querySelectorAll('.katex-display .katex-html')]
              .every(el => {
                const r = document.createRange();
                r.selectNodeContents(el);
                const b = r.getBoundingClientRect();
                return b.width > 0 && b.left >= -1 && b.right <= innerWidth + 1
                   && b.top >= -1 && b.bottom <= innerHeight + 1;
              })""")
            if not inside:
                raise ValueError(f"Display equation extends beyond the frame on {slide_id}")

        slugs = page.evaluate("""[...new Set([...document.querySelectorAll('video[data-hls]')]
          .map(el => el.closest('section').id))]""")
        source = find("DreamZero").qmd.read_text(encoding="utf-8")
        expected = len(re.findall(r'<video\s+[^>]*\bdata-hls=', source))
        if not expected:
            raise ValueError("DreamZero has no HLS clips")
        for group in (slugs, reversed(slugs)):
            page.evaluate("Reveal.slide(0, 0)")
            count = 0
            for slide_id in group:
                select_slide(page, slide_id)
                sizes = page.evaluate(FRAMES)
                if not sizes or any(width <= 0 or height <= 0 for width, height in sizes):
                    raise ValueError(f"HLS frame missing on {slide_id}")
                count += len(sizes)
            if count != expected:
                raise ValueError(f"Decoded {count} of {expected} authored HLS clips")

        labels = ", ".join(f"{lib['name']} {lib['version']}" for lib in versions)
        print(f"{labels}: {math['total']} equations, {expected} HLS clips decoded on entry and return")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("url", help="HTTP URL of the rendered audience page")
    try:
        check(cli.parse_args().url)
    except (OSError, ValueError, RuntimeError) as error:
        sys.exit(str(error))
