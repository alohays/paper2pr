#!/bin/bash
# The pre-commit hook this repo installs (scripts/setup-git-filters.sh copies
# it to .git/hooks/pre-commit). It is a two-line wrapper on purpose: each gate
# stays a script you can run, read and test on its own.
#
#   check-notes-pre-commit.sh   no speaker notes in the staged blob, and the
#                               clean filter is actually configured
#   check-korean-pre-commit.sh  no Hangul beyond the deck's declared allowance
set -u

root="$(git rev-parse --show-toplevel)" || exit 1

bash "$root/scripts/check-notes-pre-commit.sh" || exit 1
bash "$root/scripts/check-korean-pre-commit.sh" || exit 1
