#!/bin/bash
# Assemble every publishable deck, or only the named publishable decks.
# bash scripts/assemble_site.sh [OUT [genre/name ...]]
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/assemble_site.py -- "$@"
