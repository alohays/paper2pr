#!/bin/bash
# Screenshot every slide of a rendered fixture deck at 1280x720.
# Usage: bash shoot.sh w02-sample [n_slides]       (run after quarto render)
# Output: shots/<deck>-<NN>.png  (NN is the 0-based slide index in reading order)
#
# Thin wrapper over ../shoot.py, which drives headless Chrome through the
# DevTools protocol. The older `chrome --screenshot` one-liner laid the page
# out at a smaller viewport first and could paint SVG <text> from that stale
# layout (the chart labels drifted off their bars), so it is gone.
set -u
V="${1:?deck name, e.g. w02-sample}"; N="${2:-6}"
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/../shoot.py" "$HERE/$V.html" "$N" "$HERE/shots" "$V"
