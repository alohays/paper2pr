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

    # Check staged content (not working directory) for Korean Hangul
    korean_lines=$(git diff --cached -p "$file" | grep "^+" | grep -cP '[\uAC00-\uD7AF]' 2>/dev/null || true)

    if [ "$korean_lines" -gt 0 ] 2>/dev/null; then
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
