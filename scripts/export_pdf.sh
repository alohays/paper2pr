#!/bin/bash
# Export a local handout. Paths and deck names work from any directory.
set -eu
exec python3 "$(dirname "$0")/export_pdf.py" "$@"
