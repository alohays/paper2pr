#!/usr/bin/env python3
"""Screenshot every slide of a deck at exactly 1280x720, one PNG per slide.

Usage:
    python3 scripts/shoot_slides.py <Deck|genre/name|path.qmd|path.html>
                                    [--out DIR] [--max N] [--prefix P]

The argument is resolved like everywhere else in this repo:
  - a bare deck name or genre/name goes through scripts/deckpath.py, and the
    rendered html is expected next to the qmd (Quarto/<genre>/<name>.html);
  - a .qmd path (a fixture, say) uses the sibling .html;
  - a .html path is used as-is, no render check.
For a qmd, the html is (re)rendered first -- by shelling to `quarto render` --
when it is missing or older than the qmd, so the shots never show a stale deck.

Output: <out_dir>/<prefix>-<NN>.png, NN = 0-based index in reading order,
vertical stacks included; the walk stops at the last slide or at --max.
Default out dir is a fresh temp dir, printed on the first line; default
prefix is the deck name.

Why this drives headless Chrome over the DevTools protocol instead of the
`--screenshot` one-liner: the one-shot flag lays the page out once at a
smaller viewport and then resizes, and Chrome can paint SVG <text> from that
stale layout. Here the viewport is pinned before navigation, fonts are
awaited, reveal is re-laid out, and slides are switched from inside the page.

The ?slide=N / URL-fragment trap, so nobody rediscovers it: reveal ignores
`?slide=N` entirely (its URL scheme is the `#/h` or `#/h/v` hash), and a flat
index does not survive vertical stacks -- a level-1 `#` heading folds every
following slide into one vertical stack, so `#/7` is not the eighth slide in
reading order. Mutating location.hash on a live page also races reveal's own
hash handling, and the capture can catch the previous slide still painted.
The deterministic walk is `Reveal.slide(0, 0)` once, then `Reveal.next()`,
which descends vertical stacks in reading order. Do not "optimise" this back
to hash navigation, and do not use `--virtual-time-budget` (it fast-forwards
timers, which breaks the settle delay background videos and transitions need).

Needs the `websocket-client` module (python3 -c "import websocket") and
Google Chrome (path below, override with the CHROME env var).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deckpath  # noqa: E402

import websocket  # websocket-client  # noqa: E402

CHROME = os.environ.get(
    "CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DEFAULT_MAX = 500  # the walk stops at Reveal.isLastSlide() anyway
SETTLE_S = 0.6     # let background video/poster and transitions settle


def resolve_html(ref: str) -> Path:
    """Turn the CLI argument into the html file to shoot, rendering first
    when the argument names a qmd (directly or via a deck name) whose html
    is missing or stale."""
    ref = ref.strip()
    p = Path(ref)
    p = p if p.is_absolute() else (Path.cwd() / p)
    if ref.endswith(".html"):
        if not p.is_file():
            sys.exit(f"error: {ref}: no such file")
        return p.resolve()
    if ref.endswith(".qmd"):
        if not p.is_file():
            sys.exit(f"error: {ref}: no such file")
        qmd = p.resolve()
    else:
        try:
            qmd = deckpath.find(ref).qmd
        except (deckpath.DeckNotFound, deckpath.AmbiguousDeck) as e:
            sys.exit(f"error: {e}")
    html = qmd.with_suffix(".html")
    if not html.exists() or html.stat().st_mtime < qmd.stat().st_mtime:
        why = "missing" if not html.exists() else "older than the qmd"
        print(f"render  {html.name} is {why}; quarto render {qmd}")
        r = subprocess.run(["quarto", "render", str(qmd)])
        if r.returncode != 0 or not html.exists():
            sys.exit(f"error: quarto render failed for {qmd}")
    return html


def shoot(html: Path, out_dir: Path, prefix: str,
          max_slides: int = DEFAULT_MAX) -> list[Path]:
    """Walk the rendered deck in reading order and save one PNG per slide.
    Returns the paths written, in order."""
    url = html.resolve().as_uri()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not Path(CHROME).exists():
        sys.exit(f"error: Chrome not found at {CHROME} (set CHROME to override)")
    profile_dir = Path(tempfile.mkdtemp(prefix="shoot-chrome-"))
    # --remote-debugging-port=0 lets the OS pick a free port (parallel runs
    # never collide); Chrome writes the real port to DevToolsActivePort in
    # the user-data dir.
    chrome = subprocess.Popen(
        [CHROME, "--headless=new", "--hide-scrollbars", "--disable-gpu",
         "--autoplay-policy=no-user-gesture-required",
         "--allow-file-access-from-files",
         f"--user-data-dir={profile_dir}",
         "--remote-debugging-port=0", "--window-size=1280,720", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shots: list[Path] = []
    try:
        port_file = profile_dir / "DevToolsActivePort"
        for _ in range(100):
            if port_file.exists() and port_file.read_text().strip():
                break
            time.sleep(0.2)
        else:
            sys.exit("error: chrome did not come up")
        port = int(port_file.read_text().splitlines()[0])
        for _ in range(50):
            try:
                targets = json.load(
                    urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                page = next(t for t in targets if t["type"] == "page")
                break
            except Exception:
                time.sleep(0.2)
        else:
            sys.exit("error: no debuggable page")
        ws = websocket.create_connection(page["webSocketDebuggerUrl"],
                                         suppress_origin=True)
        mid = [0]

        def send(method, **params):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": method, "params": params}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == mid[0]:
                    if "error" in msg:
                        raise RuntimeError(msg["error"])
                    return msg.get("result", {})

        def evaluate(expr):
            r = send("Runtime.evaluate", expression=expr,
                     awaitPromise=True, returnByValue=True)
            return r.get("result", {}).get("value")

        send("Page.enable")
        send("Runtime.enable")
        send("Emulation.setDeviceMetricsOverride", width=1280, height=720,
             deviceScaleFactor=1, mobile=False)
        send("Page.navigate", url=url + "#/0")
        for _ in range(100):
            if evaluate("typeof Reveal !== 'undefined' && Reveal.isReady()"):
                break
            time.sleep(0.1)
        else:
            sys.exit(f"error: Reveal never became ready on {html}")
        evaluate("document.fonts.ready.then(() => true)")
        # The deterministic walk (see the module docstring for why not
        # hash navigation): rewind, re-layout, then Reveal.next() through
        # the deck, which descends vertical stacks in reading order.
        evaluate("Reveal.slide(0, 0); Reveal.layout(); true")
        for i in range(max_slides):
            time.sleep(SETTLE_S)
            png = send("Page.captureScreenshot", format="png",
                       fromSurface=True)["data"]
            out = out_dir / f"{prefix}-{i:02d}.png"
            out.write_bytes(base64.b64decode(png))
            shots.append(out)
            print(f"ok  {out}  {evaluate('JSON.stringify(Reveal.getIndices())')}")
            if evaluate("Reveal.isLastSlide()"):
                break
            evaluate("Reveal.next(); true")
        ws.close()
    finally:
        chrome.terminate()
        chrome.wait(timeout=10)
        shutil.rmtree(profile_dir, ignore_errors=True)
    return shots


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("deck",
                    help="deck name, genre/name, a .qmd path, or a rendered "
                         ".html path")
    ap.add_argument("--out", help="output directory (default: a fresh temp "
                                  "dir, printed first)")
    ap.add_argument("--max", type=int, default=DEFAULT_MAX,
                    help="stop after N slides (default: the whole deck)")
    ap.add_argument("--prefix",
                    help="PNG name prefix (default: the deck name)")
    args = ap.parse_args(argv)

    html = resolve_html(args.deck)
    out_dir = Path(args.out) if args.out else Path(
        tempfile.mkdtemp(prefix="slide-shots-"))
    prefix = args.prefix or html.stem
    print(f"shots -> {out_dir}")
    shots = shoot(html, out_dir, prefix, args.max)
    print(f"{len(shots)} slides -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
