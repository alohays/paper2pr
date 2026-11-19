"""Exercise Git's actual clean conversion, hook dispatch and public HTML output."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from strip_speaker_notes import count_notes, strip_notes

ROOT = Path(__file__).resolve().parents[1]
PROBE = Path("Quarto/lectures/note probe.qmd")
CANARY = "PRIVATE-SYNTHETIC-NOTE"
DECK = """---
title: Note filter fixture
format: revealjs
title-slide-attributes:
  "data-notes": |
    PRIVATE-SYNTHETIC-NOTE title.
---

## Audience {#audience}

Keep this audience sentence.

:::: {#script .notes .fragment} ::::
PRIVATE-SYNTHETIC-NOTE introduction.

::: {.group}
PRIVATE-SYNTHETIC-NOTE inside a nested group.
:::

PRIVATE-SYNTHETIC-NOTE conclusion.
::::
"""

# A gate under test may print diagnostics. Expose those only after ensuring
# the command didn't print private note values. Never inherit a caller's index
# or a user's Git hooks from outside this disposable repository.
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
           GIT_AUTHOR_NAME="Fixture", GIT_COMMITTER_NAME="Fixture",
           GIT_AUTHOR_EMAIL="fixture@example.org", GIT_COMMITTER_EMAIL="fixture@example.org")


def run(repo, *cmd, fails=False):
    result = subprocess.run(cmd, cwd=repo, env=ENV, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    if CANARY in result.stdout:
        raise AssertionError(f"{cmd[0]} printed private content")
    if (result.returncode != 0) != fails:
        raise AssertionError(f"{cmd[0]} exited {result.returncode}: {result.stdout}")
    return result.stdout.strip()


def stage(repo):
    path = repo / PROBE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DECK, encoding="utf-8")
    run(repo, "git", "add", "--", PROBE)
    staged = run(repo, "git", "show", f":{PROBE}")
    assert "Keep this audience sentence." in staged
    assert path.read_text(encoding="utf-8") == DECK
    run(repo, "bash", "scripts/check-notes-pre-commit.sh", "--all")
    oid = run(repo, "git", "rev-parse", f":{PROBE}")
    path.write_text(DECK + "\n::: notes\n" + CANARY, encoding="utf-8")
    run(repo, "git", "add", "--", PROBE, fails=True)
    assert run(repo, "git", "rev-parse", f":{PROBE}") == oid
    path.write_text(DECK, encoding="utf-8")


def test_delivery(tmp):
    seed = tmp / "seed"
    seed.mkdir()
    (seed / "scripts").mkdir()
    for name in ("setup-git-filters.sh", "check-notes-pre-commit.sh",
                 "pre-commit.sh", "check-korean-pre-commit.sh", "strip_qmd_notes.py"):
        shutil.copy2(ROOT / "scripts" / name, seed / "scripts" / name)
    shutil.copy2(ROOT / ".gitattributes", seed)
    run(seed, "git", "init", "-q")
    run(seed, "git", "add", ".")
    run(seed, "git", "commit", "-qm", "Fixture source")
    repo = tmp / "clone"
    run(tmp, "git", "clone", "-q", str(seed), str(repo))
    run(repo, "bash", "scripts/check-notes-pre-commit.sh", fails=True)
    run(repo, "bash", "scripts/setup-git-filters.sh")
    stage(repo)
    print("  ok    normal clone keeps local notes, stages clean text and rejects a broken add")

    linked = tmp / "linked"
    run(repo, "git", "worktree", "add", "-q", "--detach", str(linked), "HEAD")
    run(linked, "bash", "scripts/setup-git-filters.sh")
    run(repo, "git", "config", "core.hooksPath", ".custom hooks")
    run(linked, "bash", "scripts/setup-git-filters.sh")
    assert (linked / ".custom hooks" / "pre-commit").is_file()
    stage(linked)
    print("  ok    linked worktree uses Git's common hook or the configured relative hook path")

    run(linked, "quarto", "render", str(PROBE), "--quiet")
    presenter = (linked / PROBE).with_suffix(".html")
    local_html = presenter.read_bytes()
    assert CANARY.encode() in local_html and count_notes(presenter) >= 2
    public = tmp / "public.html"
    shutil.copyfile(presenter, public)
    assert strip_notes(public) >= 2 and count_notes(public) == 0
    public_html = public.read_bytes()
    assert CANARY.encode() not in public_html and b"Keep this audience sentence." in public_html
    assert presenter.read_bytes() == local_html
    print("  ok    Quarto presenter copy retains title and slide notes. Public copy has neither")

    # check-attr must inspect the attributes that Git will commit.
    attributes = linked / ".gitattributes"
    saved = attributes.read_bytes()
    attributes.write_bytes(b"")
    run(linked, "git", "add", "--", ".gitattributes")
    attributes.write_bytes(saved)
    run(linked, "bash", "scripts/check-notes-pre-commit.sh", "--all", fails=True)
    run(linked, "git", "add", "--", ".gitattributes")
    private = linked / ".speaker-notes" / "probe.txt"
    private.parent.mkdir()
    private.write_text(CANARY, encoding="utf-8")
    run(linked, "git", "add", "-f", "--", ".speaker-notes")
    run(linked, "bash", "scripts/check-notes-pre-commit.sh", fails=True)
    run(linked, "git", "reset", "-q", "HEAD", "--", ".speaker-notes")

    run(linked, "git", "-c", "filter.strip-speaker-notes.clean=cat",
        "add", "--renormalize", "--", PROBE)
    run(linked, "git", "commit", "-qm", "Unfiltered fixture", fails=True)
    run(linked, "git", "commit", "--no-verify", "-qm", "Bypassed local hooks in fixture")
    run(linked, "bash", "scripts/check-notes-pre-commit.sh", "--all", fails=True)
    print("  ok    installed hook rejects raw notes and the full-index CI check detects a bypass")


def test_html(tmp):
    unchanged = """<section title="example data-notes='literal'" id='kept'>"""
    public = tmp / "parser.html"
    noisy = ("<section title=\"example data-notes='literal'\" data-notes='private > value' id='kept'>"
             '<aside id="x" class="fragment notes">before<aside>nested</aside>after</aside>'
             '<div class="notes">extra</div>')
    tail = "<script>const x = '<aside class=\"notes\">';</script>visible</section>\r\n"
    public.write_bytes((noisy + tail).encode())
    assert strip_notes(public) == 3
    assert public.read_bytes() == (unchanged + tail).encode()
    assert strip_notes(public) == 0
    public.write_text('<aside class="notes">unclosed', encoding="utf-8")
    try:
        strip_notes(public)
    except ValueError:
        assert public.read_text(encoding="utf-8").endswith("unclosed")
    else:
        raise AssertionError("an unclosed HTML note passed")
    print("  ok    nested notes disappear while tags, script text and original line endings stay byte-exact")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temp:
        test_delivery(Path(temp))
        test_html(Path(temp))
