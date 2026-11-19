"""Apply the repository language policy to Git's index without logging content."""
import argparse
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import deckpath
import deckprofile
import minyaml

HANGUL = re.compile("[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]")
EXEMPT = (".claude/skills/", ".claude/agents/")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=deckprofile.REPO_ROOT)


def names(data):
    return {os.fsdecode(name) for name in data.split(b"\0") if name}


def check(base):
    diff = ["diff", "--cached", "--no-renames", "--no-ext-diff"]
    if base is not None:
        diff.append(git("rev-parse", "--verify", "--end-of-options", base + "^{commit}").decode().strip())
    changed = names(git(*diff, "--name-only", "-z", "--"))
    if not changed:
        return True

    qmds = names(git("ls-files", "-z", "--", ":(glob)Quarto/**/*.qmd"))
    profiles = deckprofile.PROFILE_DIR.relative_to(deckprofile.REPO_ROOT)
    metadata = names(git("ls-files", "-z", "--", f":(glob){profiles}/*.yml", ":(glob)Quarto/**/*.deck.yml"))
    profile_names = sorted(Path(p).stem for p in metadata if Path(p).parent == profiles)
    genres = {line.strip() for line in git("show", ":Quarto/_genres.txt").decode().splitlines()}
    # Removing a Korean exemption or lowering an allowance can change the
    # verdict even when nobody touched the QMD itself.
    check_qmd = qmds & (changed | {p[:-9] + ".qmd" for p in changed if p.endswith(".deck.yml")})
    if "Quarto/_genres.txt" in changed or any(p.startswith(f"{profiles}/") for p in changed):
        check_qmd = qmds

    @lru_cache(maxsize=None)
    def read_yaml(path):
        rel = path.relative_to(deckprofile.REPO_ROOT).as_posix()
        if rel not in metadata:
            return {}
        raw = minyaml.loads(git("show", f":{rel}").decode())
        if not isinstance(raw, dict):
            raise ValueError("a staged language configuration must contain a mapping")
        return raw

    passed = True
    for path in sorted(check_qmd):
        count = len(HANGUL.findall(git("show", f":{path}").decode()))
        if not count:
            continue
        rel = Path(path).relative_to("Quarto")
        deck = deckpath.Deck(name=rel.stem, genre=rel.parent.as_posix())
        allowance = 0
        if deck.genre in genres or str(Path(path).with_suffix(".deck.yml")) in metadata:
            cfg = deckprofile.load(deck, names=profile_names, read_yaml=read_yaml)
            language = cfg.raw.get("language") or {}
            if language.get("slides") == "ko":
                print(f"  {path}: Korean slides allowed by the staged deck config")
                continue
            allowance = cfg.korean_allowance
        if count > allowance:
            print(f"  {path}: {count} Hangul characters on the slides, allowance is {allowance}")
            passed = False
        else:
            print(f"  {path}: {count} Hangul characters within the allowance of {allowance}")

    # Outside decks the existing policy counts added lines. A deleted file
    # and a binary diff contribute none. Ignore Git's path headers.
    for path in sorted(changed - qmds):
        if path.startswith(EXEMPT):
            continue
        patch = git(*diff, "--unified=0", "--", f":(literal){path}").decode(errors="replace")
        in_hunk = False
        hits = 0
        for line in patch.splitlines():
            if line.startswith("@@"):
                in_hunk = True
            elif in_hunk and line.startswith("+") and HANGUL.search(line):
                hits += 1
        if hits:
            print(f"  {path}: {hits} added line(s) contain Hangul")
            passed = False
    return passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="?", help="compare the index to this commit (for a pull request)")
    args = parser.parse_args()
    try:
        if not check(args.base):
            sys.exit("Use English or declare the deck's slide language or allowance in its staged config.")
    except (OSError, ValueError, TypeError, AttributeError, deckprofile.ConfigError, subprocess.CalledProcessError):
        sys.exit("error: could not check the language policy against staged files and profiles")
