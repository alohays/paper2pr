#!/usr/bin/env python3
"""Assemble self-contained RevealJS widget fragments for the RoboTTT deck.

Reads the animation sources in
  target-papers/2607-robottt/anim/
and writes one Quarto include fragment per widget to
  Quarto/_widgets/<name>.qmd

Each fragment is raw HTML: markup + scoped CSS + the widget's own JS, so a
slide only has to say {{< include _widgets/rttt-dit.qmd >}}.

Five of the widgets are lifted verbatim from the official project page
(research.nvidia.com/labs/gear/robottt); those get a visible credit line.
Two (nv-update, nv-spectrum) were built for this talk.

Usage:  python3 scripts/build_widgets.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "target-papers", "2607-robottt", "anim")
DST = os.path.join(HERE, "Quarto", "_widgets")

PAGE = "https://research.nvidia.com/labs/gear/robottt/"
CREDIT = ('<p class="widget-credit">Animation reproduced verbatim from the '
          f'official RoboTTT project page (NVIDIA GEAR), '
          f'<a href="{PAGE}">{PAGE}</a></p>')
OWN = ('<p class="widget-credit own">Built for this talk; the paper states '
       'this in prose only.</p>')

# name -> (kind, credit)
#   "pair"  : <name>.html + <name>.js, the JS is a self-running IIFE
#   "init"  : <name>.anim.js exposing window.initRttt_<slug>(container)
#   "static": <name>.html only
WIDGETS = [
    ("rttt-dit",     "pair",   CREDIT),
    ("rttt-tanh",    "pair",   CREDIT),
    ("rttt-forcing", "init",   CREDIT),
    ("rttt-tbptt",   "init",   CREDIT),
    ("rttt-context", "init",   CREDIT),
    ("nv-update",    "pair",   OWN),
    ("nv-spectrum",  "static", OWN),
]

WRAP_OPEN = '<div class="rttt-widget" data-widget="{name}" data-beats="{beats}">\n'
WRAP_CLOSE = "</div>\n"

# beats per widget, used by the RevealJS fragment bridge
BEATS = {"rttt-dit": 6, "rttt-tanh": 6, "rttt-forcing": 6,
         "rttt-tbptt": 7, "rttt-context": 7, "nv-update": 6,
         "nv-spectrum": 0}

FENCE = "``````"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def desection(html):
    """Turn the widget's own outer <section> into a <div>.

    RevealJS reads any <section> nested inside a slide as a vertical sub-slide.
    A widget that ships its own <section> silently turns its slide into a
    one-element stack, and Reveal.slide() can no longer land on it. The widget
    CSS is all id-scoped, so the tag name itself carries no styling.
    """
    out = re.sub(r'<section(\s+id="[^"]*")', r'<div role="region"\1', html,
                 count=1)
    if out == html:
        return html                      # widget has no wrapper section
    return out[::-1].replace("</section>"[::-1], "</div>"[::-1], 1)[::-1]


def build(name, kind, credit):
    if kind == "static":
        body = desection(read(os.path.join(SRC, name + ".html")))
    elif kind == "pair":
        body = (desection(read(os.path.join(SRC, name + ".html")))
                + "\n<script>\n" + read(os.path.join(SRC, name + ".js"))
                + "\n</script>\n")
    elif kind == "init":
        slug = name.split("-", 1)[1]
        host = f"host-{slug}"
        body = (f'<div id="{host}"></div>\n<script>\n'
                + read(os.path.join(SRC, name + ".anim.js"))
                + f'\nwindow.initRttt_{slug}(document.getElementById('
                  f'"{host}"));\n</script>\n')
    else:
        raise ValueError(kind)
    html = (WRAP_OPEN.format(name=name, beats=BEATS[name])
            + body + credit + "\n" + WRAP_CLOSE)
    # Emit as an explicit pandoc raw-HTML block. A bare HTML block would end at
    # the first blank line, and these widgets have plenty (plus JS template
    # literals that must survive untouched).
    for line in html.splitlines():
        if line.strip().startswith(FENCE):
            raise SystemExit(f"{name}: content collides with the raw-block fence")
    return f"{FENCE}{{=html}}\n{html}{FENCE}\n"


def main():
    os.makedirs(DST, exist_ok=True)
    missing = []
    for name, kind, credit in WIDGETS:
        need = {"static": [name + ".html"],
                "pair": [name + ".html", name + ".js"],
                "init": [name + ".anim.js"]}[kind]
        gone = [f for f in need if not os.path.exists(os.path.join(SRC, f))]
        if gone:
            missing.append((name, gone))
            continue
        out = os.path.join(DST, name + ".qmd")
        with open(out, "w", encoding="utf-8") as f:
            f.write(build(name, kind, credit))
        print(f"  {name+'.qmd':<24} {os.path.getsize(out):>7,} B")
    if missing:
        for name, gone in missing:
            print(f"  MISSING {name}: {', '.join(gone)}", file=sys.stderr)
        return 1
    print(f"\n{len(WIDGETS)} fragments -> {os.path.relpath(DST, HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
