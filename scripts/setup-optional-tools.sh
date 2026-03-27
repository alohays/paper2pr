#!/bin/bash
# setup-optional-tools.sh — Install optional tools for paper2pr
#
# These tools enhance the workflow but are NOT required.
# The core project works with only XeLaTeX, Quarto, and Python 3.
#
# Usage: bash scripts/setup-optional-tools.sh [--all | tool-name ...]
# Examples:
#   bash scripts/setup-optional-tools.sh --all
#   bash scripts/setup-optional-tools.sh diff-pdf tex-fmt

set -e

TOOLS_AVAILABLE="diff-pdf tex-fmt"

print_help() {
    echo "paper2pr Optional Tools Installer"
    echo ""
    echo "Available tools:"
    echo "  diff-pdf    Visual PDF page-by-page comparison (regression testing)"
    echo "  tex-fmt     Fast LaTeX formatter written in Rust"
    echo ""
    echo "Already in TeX Live (no install needed):"
    echo "  chktex      LaTeX semantic linter"
    echo "  dvisvgm     DVI/PDF to SVG converter"
    echo ""
    echo "Usage:"
    echo "  $0 --all              Install all optional tools"
    echo "  $0 diff-pdf tex-fmt   Install specific tools"
    echo "  $0 --help             Show this message"
}

install_tool() {
    local tool=$1
    case $tool in
        diff-pdf)
            echo "Installing diff-pdf..."
            if command -v diff-pdf &>/dev/null; then
                echo "  diff-pdf already installed: $(diff-pdf --version 2>&1 | head -1)"
            else
                if command -v brew &>/dev/null; then
                    brew install diff-pdf
                elif command -v apt-get &>/dev/null; then
                    sudo apt-get install -y diff-pdf
                else
                    echo "  ERROR: No supported package manager found (brew or apt-get)"
                    return 1
                fi
            fi
            ;;
        tex-fmt)
            echo "Installing tex-fmt..."
            if command -v tex-fmt &>/dev/null; then
                echo "  tex-fmt already installed: $(tex-fmt --version 2>&1 | head -1)"
            else
                if command -v brew &>/dev/null; then
                    brew install tex-fmt
                elif command -v cargo &>/dev/null; then
                    cargo install tex-fmt
                else
                    echo "  ERROR: No supported package manager found (brew or cargo)"
                    return 1
                fi
            fi
            ;;
        *)
            echo "Unknown tool: $tool"
            echo "Available: $TOOLS_AVAILABLE"
            return 1
            ;;
    esac
}

if [ $# -eq 0 ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    print_help
    exit 0
fi

if [ "$1" = "--all" ]; then
    for tool in $TOOLS_AVAILABLE; do
        install_tool "$tool"
    done
else
    for tool in "$@"; do
        install_tool "$tool"
    done
fi

echo ""
echo "Done. Optional tools installed."
