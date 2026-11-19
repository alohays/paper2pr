"""Verify one fresh audience build. Invoked by ./verify from any directory."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import deckpath
import deckprofile
from private_terms import contains_private, private_terms

ROOT = deckpath.REPO_ROOT
FIXTURES = [
    ROOT / "Quarto/_fixtures/design-test.qmd",
    ROOT / "Quarto/_fixtures/video/video.qmd",
    ROOT / "Quarto/_fixtures/series/series.qmd",
]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8")


def affected(paths, decks):
    """Only a change confined to a known deck source/config narrows the build.

    Loose assets can be shared even when named for a deck (W09 uses W06's
    font stylesheet). Removed decks change the landing page and redirects.
    """
    owners = {}
    for deck in decks:
        for path in (deck.qmd, deck.config, deck.forbidden):
            owners[path.relative_to(ROOT).as_posix()] = deck
    selected = set()
    for path in paths:
        if path in owners:
            selected.add(owners[path].slug)
        elif path.startswith(("quality_reports/", "assets/")) or path in {
            "README.md", "LICENSE", "MEMORY.md", "AGENTS.md", "CLAUDE.md"
        }:
            continue
        else:
            return list(decks), True
    return [deck for deck in decks if deck.slug in selected], False


def step(label, *cmd, quiet=False, private_output=False):
    """Keep authoring metadata out of CI logs, including Quarto's YAML dump."""
    print(label, flush=True)
    result = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, errors="replace")
    if result.returncode:
        diagnostic = result.stdout.strip().replace(str(ROOT) + os.sep, "")
        if private_output or contains_private(diagnostic, private_terms()):
            diagnostic = "Inspect this step in the local checkout for source details."
        raise RuntimeError(f"{label} failed ({result.returncode}).\n{diagnostic}")
    if not quiet and result.stdout.strip():
        summary = result.stdout.strip().splitlines()[-1].replace(str(ROOT) + os.sep, "")
        if not contains_private(summary, private_terms()):
            print(f"  {summary}", flush=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regressions(series_html=None):
    py = sys.executable
    step("Checking tracked QMD blobs for notes", "bash", "scripts/check-notes-pre-commit.sh", "--all")
    for cmd in (["bash", "scripts/test_note_filter.sh"],
                [py, "scripts/test_profiles.py"],
                [py, "scripts/test_minyaml.py"],
                ["bash", "scripts/test_korean_gate.sh"],
                [py, "scripts/test_media.py"],
                [py, "scripts/test_series.py"]):
        if series_html and cmd[-1] == "scripts/test_series.py":
            cmd.extend(["--rendered", str(series_html)])
        step(f"Running {cmd[1]}", *cmd)
    step("Checking per-deck runtime packaging", py, "scripts/test_site.py")
    step("Checking affected-deck selection", py, "scripts/test_verify.py")


def check_deck(qmd, site, build, slide, delivery):
    rel = qmd.relative_to(ROOT / "Quarto").with_suffix(".html")
    audience = site / "slides" / rel
    initial = digest(audience)
    output = build / "checks" / rel.with_suffix("")
    output.mkdir(parents=True)
    fixture = qmd in FIXTURES
    py = sys.executable
    if not fixture:
        step(f"Scoring {rel.stem}", py, "scripts/quality_score.py", str(qmd),
             "--rendered", str(audience), "--summary")
    config = deckprofile.load_for_path(qmd)
    dgist = (config and config.raw.get("series", "").startswith("dgist")) or fixture
    sizes = [1280, 896] if dgist else [1280]
    results = {"delivery": delivery, "audience_sha256": initial, "viewports": {}}
    from shoot_slides import local_url
    with local_url(audience) as url:
        for width in sizes:
            shots = output / f"{width}x720"
            cmd = [py, "scripts/shoot_slides.py", str(audience), "--url", url,
                   "--width", str(width), "--out", str(shots)]
            if slide:
                cmd.extend(["--slide", slide])
            step(f"Inspecting {rel.stem} at {width}x720", *cmd)
            stats = json.loads((shots / "browser.json").read_text())
            results["viewports"][str(width)] = {
                key: stats[key] for key in ("total_slides", "forward_steps", "reverse_steps")
            }
        if not slide:
            if rel.as_posix() == "papers/DreamZero.html":
                step("Checking DreamZero equations and HLS playback on entry and return",
                     py, "scripts/check_dreamzero.py", url)
            pdf = output / f"{qmd.stem}.pdf"
            pages = results["viewports"]["1280"]["total_slides"]
            step(f"Checking {rel.stem} handout against {pages} slides",
                 "bash", "scripts/export_pdf.sh", str(audience), "--url", url,
                 "--source", str(qmd), "--pages", str(pages), "--out", str(pdf))
            results["handout_sha256"] = digest(pdf)
    if digest(audience) != initial:
        raise RuntimeError(f"The {rel.stem} audience HTML changed during verification. Run again.")
    return results


def main():
    parser = argparse.ArgumentParser(prog="./verify", description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("deck", nargs="?", help="deck name, genre/name or fixture QMD")
    group.add_argument("--all", action="store_true", help="all publishable decks and three fixtures")
    group.add_argument("--changed-from", metavar="REF", help="verify decks affected by committed changes since REF")
    parser.add_argument("--delivery", choices=["public", "classroom"], default="public")
    parser.add_argument("--slide", metavar="ID", help="check one edited slide, skipping the full handout")
    parser.add_argument("--regressions", action="store_true", help="also run the repository regression suites")
    parser.add_argument("--site", type=Path, help="destination for the sanitized public Pages artifact")
    args = parser.parse_args()
    if (args.delivery == "classroom" or args.slide) and not args.deck:
        parser.error("--delivery classroom and --slide each require a single deck")
    if args.delivery == "classroom" and args.site:
        parser.error("--site only accepts public builds")
    private_terms()  # Invalid configuration stops the build before any diagnostic output.
    os.chdir(ROOT)
    revision = git("rev-parse", "HEAD").strip()
    fixtures = []
    if args.all:
        decks, fixtures = deckprofile.publishable_decks(), FIXTURES
    elif args.changed_from:
        base = git("merge-base", args.changed_from, "HEAD").strip()
        changes = git("diff", "--no-renames", "--name-only", "-z", base, "HEAD").split("\0")
        decks, shared = affected([p for p in changes if p], deckpath.all_decks())
        if shared:
            fixtures = FIXTURES
        step("Checking the language policy on the proposed changes",
             "bash", "scripts/check-korean-pre-commit.sh", base)
    elif (ROOT / args.deck).resolve() in FIXTURES:
        decks, fixtures = [], [(ROOT / args.deck).resolve()]
    else:
        decks = [deckpath.find(args.deck)]

    exports = ROOT / "exports/verify"
    exports.mkdir(parents=True, exist_ok=True)
    build = Path(tempfile.mkdtemp(prefix="run-", dir=exports))
    print(f"Checking {revision[:12]} in {build.relative_to(ROOT)}", flush=True)
    public = [d for d in decks if deckprofile.load(d).publish and args.delivery == "public"]
    checks = [d.qmd for d in decks] + fixtures
    rendered = {}
    for qmd in checks:
        step(f"Rendering {qmd.stem} once ({args.delivery})",
             "bash", "scripts/render_decks.sh", str(qmd), "--delivery", args.delivery,
             quiet=True, private_output=True)
        rendered[qmd] = digest(qmd.with_suffix(".html"))

    if args.regressions:
        series = FIXTURES[-1]
        regressions(series.with_suffix(".html") if series in fixtures else None)
    if not checks:
        print("No affected decks or fixtures.")
        return

    sites = {}
    if public:
        site = args.site.resolve() if args.site else build / "site"
        step("Assembling the public audience site", "bash", "scripts/assemble_site.sh",
             str(site), *(d.slug for d in public))
        sites.update((d.qmd, site) for d in public)
    elif args.site and not args.changed_from:
        parser.error("The selected deck has no public Pages artifact")

    for qmd in checks:
        if qmd not in sites:
            site = build / "previews" / qmd.parent.name / qmd.stem
            step(f"Packaging a local {args.delivery} preview of {qmd.stem}", sys.executable,
                 "scripts/assemble_site.py", "--preview", args.delivery, str(site), str(qmd))
            sites[qmd] = site
    for site in dict.fromkeys(sites.values()):
        options = ["--classroom"] if args.delivery == "classroom" else []
        step("Checking packaged assets", sys.executable, "scripts/check_site_assets.py", *options, str(site))
        if args.delivery == "public" and not args.slide:
            step("Checking referenced GitHub Release assets", sys.executable,
                 "scripts/check_release_media.py", str(site))

    def inspect(qmd):
        report = check_deck(qmd, sites[qmd], build, args.slide, args.delivery)
        report["rendered_sha256"] = rendered[qmd]
        if digest(qmd.with_suffix(".html")) != rendered[qmd]:
            raise RuntimeError(f"The {qmd.stem} presenter render changed during verification. Run again.")
        return qmd.relative_to(ROOT).as_posix(), report

    reports = {}
    failed = []
    with ThreadPoolExecutor(max_workers=2) as workers:
        futures = {workers.submit(inspect, qmd): qmd for qmd in checks}
        for task in as_completed(futures):
            try:
                name, report = task.result()
                reports[name] = report
            except (ValueError, OSError, RuntimeError) as error:
                failed.append(futures[task].stem)
                print(str(error), file=sys.stderr, flush=True)
    if failed:
        raise RuntimeError("Audience verification failed for " + ", ".join(sorted(failed)))
    receipt = build / "verification.json"
    receipt.write_text(json.dumps({"commit": revision, "quarto": (ROOT / ".quarto-version").read_text().strip(),
                                   "decks": dict(sorted(reports.items()))}, indent=2) + "\n")
    print(f"Verified {len(checks)} audience build(s). Receipt: {receipt.relative_to(ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError,
            deckpath.DeckNotFound, deckpath.AmbiguousDeck, deckprofile.ConfigError) as exc:
        sys.exit(str(exc))
