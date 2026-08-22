#!/bin/bash
# Pre-commit hook: block Korean (Hangul) text in staged files.
#
# Exceptions:
#   - .claude/skills/** (Korean examples for bilingual functionality)
#   - .claude/agents/** (Korean examples for bilingual functionality)
#   - .speaker-notes/**  (local-only, gitignored anyway)
#   - a deck that declares `language.slides: ko` in its own <deck>.deck.yml
#   - a deck qmd may carry up to `language.korean_allowance` Hangul
#     characters (deck config, else its profile, else 0) -- term glosses,
#     Wooclap instructions -- without being declared Korean (plan D18)
#
# The `slides: ko` one is the reason the deck config exists. A course taught
# in Korean will eventually want Korean on the slides, and the alternative was
# exempting Quarto/lectures/ wholesale -- a directory exemption never gets
# narrowed again, and it would cover every future lecture including the ones
# that should stay English. Declaring it per deck keeps the gate strict by
# default and makes each exception a line someone wrote on purpose.
#
# The allowance is counted on the STAGED blob of the deck qmd, i.e. after the
# clean filter has stripped the speaker notes, as whole characters (not
# lines): `python3 scripts/deckprofile.py <qmd> --field korean_allowance`
# says how many are allowed. The lecture profile says 300; paper-review and
# invited-talk say 0; a deck that does not resolve (no config, broken config,
# not under Quarto/) gets 0, which is the same as the strict rule. Files that
# are not deck qmds stay strict: any added line with Hangul blocks.
#
# Speaker notes are Korean by default and never reach this hook: the clean
# filter strips them out of the staged content before the diff is read.
#
# Install: bash scripts/setup-git-filters.sh, which puts scripts/pre-commit.sh
# in .git/hooks/ to run this gate after the speaker-note one
# (scripts/check-notes-pre-commit.sh). Runnable on its own at any time.

EXEMPT_PATTERNS=(
    ".claude/skills/"
    ".claude/agents/"
    ".speaker-notes/"
)

# A deck qmd: Quarto/<genre>/<deck>.qmd (a fixture with a config beside it
# resolves the same way; see deckprofile.resolve). Everything else is held
# to zero Hangul on every added line.
is_deck_qmd() {
    case "$1" in
        Quarto/*/*.qmd) return 0 ;;
        *) return 1 ;;
    esac
}

# Ask the deck's own config whether it may carry non-English slides.
# Anything that is not a deck, and any deck whose config will not resolve,
# stays strict: this fails closed on purpose.
slides_may_be_korean() {
    is_deck_qmd "$1" || return 1
    lang=$(python3 scripts/deckprofile.py "$1" --field slide_language 2>/dev/null)
    [ "$lang" = "ko" ]
}

# How many Hangul characters this deck may carry. Prints 0 when the deck does
# not resolve or the field is not a number, so a broken config is strict.
korean_allowance() {
    n=$(python3 scripts/deckprofile.py "$1" --field korean_allowance 2>/dev/null)
    case "$n" in
        ''|*[!0-9]*) echo 0 ;;
        *) echo "$n" ;;
    esac
}

# Hangul characters in the staged blob of a path (after the clean filter).
# Python for the same reasons as below: BSD grep has no -P, and the \uXXXX
# escapes keep this file ASCII.
staged_hangul_count() {
    git show ":$1" 2>/dev/null | python3 -c '
import re, sys
hangul = re.compile("[\uAC00-\uD7A3\u1100-\u11FF\u3130-\u318F]")
print(len(hangul.findall(sys.stdin.read())))
'
}

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

    if slides_may_be_korean "$file"; then
        echo "  $file: Korean slides allowed (language.slides: ko in its deck config)"
        continue
    fi

    # Skip binary files
    if git diff --cached --numstat "$file" | grep -q "^-"; then
        continue
    fi

    # A deck qmd is measured against its allowance: total Hangul characters
    # in the staged blob (notes already stripped), not added lines.
    if is_deck_qmd "$file"; then
        allowance=$(korean_allowance "$file")
        count=$(staged_hangul_count "$file")
        count=${count:-0}
        if [ "$count" -gt "$allowance" ]; then
            if [ "$found_korean" -eq 0 ]; then
                echo "ERROR: Korean text detected in staged files."
                echo "All GitHub content must be in English."
                echo ""
            fi
            echo "  $file: $count Hangul characters on the slides, allowance is $allowance"
            echo "         (language.korean_allowance in its deck config, else the profile's)"
            found_korean=1
        elif [ "$count" -gt 0 ]; then
            echo "  $file: $count Hangul characters within the allowance of $allowance"
        fi
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
    echo "For a deck that is genuinely delivered in Korean, set"
    echo "  language:"
    echo "    slides: ko"
    echo "in its <deck>.deck.yml rather than exempting a path here."
    echo "For a few glossed terms on English slides, raise"
    echo "  language:"
    echo "    korean_allowance: <characters>"
    echo "in the deck config (the lecture profile already allows 300)."
    echo "Otherwise: translate the slide text to English."
    exit 1
fi
