#!/usr/bin/env python3
"""Screenshot every slide of a rendered fixture deck at exactly 1280x720.

Usage: python3 shoot.py <deck.html> <max_slides> <out_dir> <prefix>
Output: <out_dir>/<prefix>-<NN>.png  (NN = 0-based index in reading order,
vertical stacks included; stops at the last slide)

Drives headless Chrome over the DevTools protocol instead of `--screenshot`:
the one-shot flag lays the page out once at a smaller viewport and then
resizes, and Chrome can paint SVG <text> from the stale layout in that frame.
Here the viewport is pinned before navigation, fonts are awaited, reveal is
re-laid out, and the slide is switched with Reveal.slide() so the capture is
deterministic. Needs the `websocket-client` module (python3 -c "import websocket").
"""
import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket  # websocket-client

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9333


def main():
    html, n, out_dir, prefix = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
    url = Path(html).resolve().as_uri()
    out_dir.mkdir(parents=True, exist_ok=True)
    chrome = subprocess.Popen(
        [CHROME, "--headless=new", "--hide-scrollbars", "--disable-gpu",
         "--autoplay-policy=no-user-gesture-required", "--allow-file-access-from-files",
         f"--remote-debugging-port={PORT}", "--window-size=1280,720", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                page = next(t for t in targets if t["type"] == "page")
                break
            except Exception:
                time.sleep(0.2)
        else:
            sys.exit("chrome did not come up")
        ws = websocket.create_connection(page["webSocketDebuggerUrl"], suppress_origin=True)
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
            r = send("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
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
        evaluate("document.fonts.ready.then(() => true)")
        # Walk the deck in reading order (Reveal.next() also descends vertical
        # stacks, which `# Part` headings create), numbering shots linearly.
        evaluate("Reveal.slide(0, 0); Reveal.layout(); true")
        for i in range(n):
            time.sleep(0.6)  # let background video/poster and transitions settle
            png = send("Page.captureScreenshot", format="png", fromSurface=True)["data"]
            out = out_dir / f"{prefix}-{i:02d}.png"
            out.write_bytes(base64.b64decode(png))
            print(f"ok  {out}  {evaluate('JSON.stringify(Reveal.getIndices())')}")
            if evaluate("Reveal.isLastSlide()"):
                break
            evaluate("Reveal.next(); true")
        ws.close()
    finally:
        chrome.terminate()


if __name__ == "__main__":
    main()
