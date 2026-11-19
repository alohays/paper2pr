#!/usr/bin/env python3
"""Locate Chrome for the QA tools, or open a disposable CDP tab for a deck."""
from __future__ import annotations

import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path


def executable() -> str:
    override = os.environ.get("CHROME")
    names = [override] if override else [
        "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for name in names:
        path = shutil.which(os.path.expanduser(name))
        if path:
            return path
    raise RuntimeError("Chrome/Chromium executable missing. Set CHROME to its executable.")


class Page:
    def __init__(self, socket):
        self.socket = socket
        self.ids = itertools.count(1)

    def send(self, method, **params):
        serial = next(self.ids)
        self.socket.send(json.dumps({"id": serial, "method": method, "params": params}))
        while True:
            message = json.loads(self.socket.recv())
            if message.get("id") == serial:
                if "error" in message:
                    raise RuntimeError(f"{method} failed: {message['error']['message']}")
                return message.get("result", {})

    def evaluate(self, expression):
        result = self.send("Runtime.evaluate", expression=expression,
                           awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in result:
            exc = result["exceptionDetails"]
            detail = exc.get("exception", {}).get("description", exc["text"])
            raise RuntimeError(detail)
        return result["result"].get("value")

    def wait_for(self, condition, message, timeout=40):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if self.evaluate(condition):
                return
            time.sleep(0.1)
        raise RuntimeError(message)

    def key(self, key):
        code = ord(key.upper())
        params = dict(key=key, code="Key" + key.upper(), windowsVirtualKeyCode=code)
        self.send("Input.dispatchKeyEvent", type="rawKeyDown", **params)
        self.send("Input.dispatchKeyEvent", type="keyUp", **params)


@contextmanager
def browser_page(url, width=1280, height=720):
    """Pin the viewport before opening the URL; Reveal and its fonts are ready on entry."""
    import websocket  # websocket-client is only needed for CDP, not discovery.

    with tempfile.TemporaryDirectory(prefix="paper2pr-chrome-") as profile:
        command = [executable(), "--headless=new", "--hide-scrollbars",
                   "--autoplay-policy=no-user-gesture-required",
                   "--remote-debugging-port=0", f"--user-data-dir={profile}",
                   f"--window-size={width},{height}", "about:blank"]
        chrome = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            end = time.monotonic() + 15
            port_file = Path(profile, "DevToolsActivePort")
            while not port_file.is_file() or not port_file.read_text().strip():
                if chrome.poll() is not None or time.monotonic() > end:
                    raise RuntimeError("Chrome failed to start a debugging session")
                time.sleep(0.05)
            port = port_file.read_text().splitlines()[0]
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=15) as info:
                target = next(t for t in json.load(info) if t["type"] == "page")
            ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=65,
                                             suppress_origin=True)
            try:
                page = Page(ws)
                page.send("Page.enable")
                page.send("Emulation.setDeviceMetricsOverride", width=width, height=height,
                          deviceScaleFactor=1, mobile=False)
                page.send("Page.navigate", url=url)
                page.wait_for("window.Reveal && Reveal.isReady()", "Reveal did not start", timeout=90)
                # Reveal may be ready while a theme's @imports are still loading.
                # Taking font measurements then captures the browser's default serif face.
                page.wait_for("document.readyState === 'complete'", "audience page did not load", timeout=90)
                page.evaluate("document.fonts.ready.then(() => true)")
                yield page
            finally:
                ws.close()
        finally:
            chrome.terminate()
            try:
                chrome.wait(timeout=10)
            except subprocess.TimeoutExpired:
                chrome.kill()
                chrome.wait()


if __name__ == "__main__":
    try:
        print(executable())
    except RuntimeError as error:
        sys.exit(str(error))
