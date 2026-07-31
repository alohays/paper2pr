#!/bin/bash
# Pre-commit hook: block Korean (Hangul) text in staged files.
#
# Exceptions:
#   - .claude/skills/** (Korean examples for bilingual functionality)
#   - .claude/agents/** (Korean examples for bilingual functionality)
#   - .speaker-notes/**  (local-only, gitignored anyway)
#
# Install: cp scripts/check-korean-pre-commit.sh .git/hooks/pre-commit
# Or run: bash scripts/setup-git-filters.sh (installs everything)

EXEMPT_PATTERNS=(
    ".claude/skills/"
    ".claude/agents/"
    ".speaker-notes/"
)

found_korean=0

for file in $(git diff --cached --name-only --diff-filter=ACM); do
    # Skip exempt paths
    skip=false
    for pattern in "${EXEMPT_PATTERNS[@]}"; do
        if [[ "$file" == *"$pattern"* ]]; then
            skip=true
            break
        fi
    done
    if $skip; then
        continue
    fi

    # Skip binary files
    if git diff --cached --numstat "$file" | grep -q "^-"; then
        continue
    fi

    # Check staged content (not working directory) for Korean Hangul.
    #
    # This used `grep -cP '[\uAC00-\uD7AF]'`, which never matched anything:
    #   1. git runs hooks with a bare PATH, so `grep` is /usr/bin/grep (BSD),
    #      which has no -P at all -- and `2>/dev/null || true` swallowed the
    #      error, leaving korean_lines empty so the -gt test silently passed.
    #   2. `\uXXXX` is not PCRE escape syntax either (PCRE wants \x{AC00}),
    #      so even a GNU grep would have matched the literal characters
    #      u, A, C, 0, D, 7, F rather than any Hangul.
    # Verified before the fix: a staged file of Korean text exited 0.
    #
    # Python does the matching now -- it is already required by the clean
    # filter and by CI, its \uXXXX escapes mean this file stays pure ASCII
    # (a literal Hangul class here gets mangled back into escapes), and it
    # is locale-independent, unlike a BSD bracket expression.
    korean_lines=$(git diff --cached -p "$file" | grep "^+" | python3 -c '
import re, sys
hangul = re.compile("[\uAC00-\uD7A3\u1100-\u11FF\u3130-\u318F]")
print(sum(1 for line in sys.stdin if hangul.search(line)))
')

    if [ "${korean_lines:-0}" -gt 0 ]; then
        if [ "$found_korean" -eq 0 ]; then
            echo "ERROR: Korean text detected in staged files."
            echo "All GitHub content must be in English."
            echo ""
        fi
        echo "  $file ($korean_lines added lines with Korean)"
        found_korean=1
    fi
done

if [ "$found_korean" -eq 1 ]; then
    echo ""
    echo "Exempt paths: .claude/skills/, .claude/agents/"
    echo "Fix: translate Korean to English, or add path to exempt list."
    exit 1
fi
