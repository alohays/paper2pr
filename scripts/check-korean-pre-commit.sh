#!/bin/bash
# Check staged files (or the staged tree against a PR base) using the same
# deck and profile declarations Git will record.
set -e
cd "$(git rev-parse --show-toplevel)"
exec python3 scripts/check_korean_index.py "$@"
