#!/usr/bin/env python3
"""Trim and encode a deck's clips from its videos.yml, then write videos.json.

The manifest owns the clip's provenance, cut and redistribution decision.
An explicit redistribution: release permits the MP4 and poster to be uploaded.
An omitted policy or redistribution: classroom keeps both on the presenter’s
machine. The public slide links to the publisher for those entries. Use
quarto render -M delivery:classroom to play their local files; --local also
plays approved entries locally in that mode. Public rendering uses Release
URLs for approved entries regardless of the preview setting.

Run media_prep.py <deck> to encode stale clips and write the lock. --only SLUG
encodes one entry and carries the other cut records forward. --force recuts
all selected files. --dry-run describes the encoding without writing files.
Source paths are relative to the gitignored videos/ directory or absolute.
The lock fingerprints each source path so a change triggers a recut without
disclosing that path. Hand-edited external CDN URLs on approved clips survive
regeneration. The manifest fingerprint ties release and render to this input.

The input may also name a videos.yml or its directory. Encoding requires
ffmpeg and ffprobe. The public render and release checks only read metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deckpath  # noqa: E402
import minyaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

# The host every release_url / poster_url is built on. Derived from the
# repository's own remote rather than written down: a fork or a rename kept
# minting URLs for alohays/paper2pr, and because a URL that is not on this
# host counts as hand-edited, the wrong ones were then preserved forever.
DEFAULT_RELEASE_BASE = "https://github.com/alohays/paper2pr/releases/download"
GITHUB_REMOTE_RE = re.compile(r"github\.com[:/]+([^/]+?)/(.+?)(?:\.git)?/?$")


def _release_base() -> str:
    try:
        url = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return DEFAULT_RELEASE_BASE
    m = GITHUB_REMOTE_RE.search(url)
    if not m:
        return DEFAULT_RELEASE_BASE
    return f"https://github.com/{m.group(1)}/{m.group(2)}/releases/download"


RELEASE_BASE = _release_base()

# What counts as a URL this pipeline owns and may regenerate. Any GitHub
# Release download URL does, not only one on RELEASE_BASE: after a rename the
# old URLs are still ours, and treating them as someone else's would freeze
# them in the lock. A hand-edited URL is by definition somewhere else -- a
# publisher's CDN, a mirror -- which is what the rule is protecting.
RELEASE_URL_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/releases/download/")

SIZE_WARN_MB = 30.0

REQUIRED = ("slug", "title", "publisher", "source_url", "published", "autonomy")
OPTIONAL = ("speed", "segment", "source", "keep_audio", "caption", "licence_note", "redistribution")
REDISTRIBUTION = ("classroom", "release")
AUTONOMY = ("autonomous", "claimed", "teleop", "unknown")
CAPTION = ("visible", "fragment", "none")
SLUG_RE = re.compile(r"^[a-z0-9-]+$")
PUBLISHED_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
SEGMENT_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)?\s*$")

# What the caption strip prints for each autonomy value. Plain words, per the
# presenter (2026-08-19); the Lua shortcode carries the same table and
# test_media.py checks the two agree.
AUTONOMY_LABEL = {
    "autonomous": "autonomous",
    "claimed": "autonomy claimed",
    "teleop": "teleoperated",
    "unknown": "autonomy not stated",
}


class ManifestError(Exception):
    """videos.yml says something this pipeline will not guess at."""


# ----------------------------------------------------------------------------
# manifest


def parse_segment(value) -> tuple[float, float | None]:
    """"S-E" -> (S, E); "S-" -> (S, None); None -> (0.0, None).

    Seconds in the *source* clip. E may be omitted to run to the end.
    """
    if value is None:
        return 0.0, None
    m = SEGMENT_RE.match(str(value))
    if not m:
        raise ManifestError(
            f"segment {value!r} is not 'S-E' or 'S-' (seconds in the source)")
    start = float(m.group(1))
    end = float(m.group(2)) if m.group(2) is not None else None
    if end is not None and end <= start:
        raise ManifestError(f"segment {value!r}: end must be after start")
    return start, end


def validate_entry(raw, index: int, where: str) -> dict:
    """One mapping from the `videos:` list -> a normalised dict, or raise."""
    tag = f"{where}: videos[{index}]"
    if not isinstance(raw, dict):
        raise ManifestError(f"{tag}: expected a mapping, got {type(raw).__name__}")
    slug = raw.get("slug")
    if slug is not None and SLUG_RE.fullmatch(str(slug)):
        tag = f"{where}: videos[{index}] ({slug})"
    missing = [k for k in REQUIRED if raw.get(k) in (None, "")]
    if missing:
        raise ManifestError(f"{tag}: missing required key(s): {', '.join(missing)}")
    unknown = sorted(set(raw) - set(REQUIRED) - set(OPTIONAL))
    if unknown:
        raise ManifestError(
            f"{tag}: unknown key(s): {', '.join(unknown)} "
            f"(release_url and poster_url belong in videos.json, not here)")

    slug = str(slug)
    if not SLUG_RE.fullmatch(slug):
        raise ManifestError(f"{tag}: slug must match [a-z0-9-]+")
    published = str(raw["published"])
    if not PUBLISHED_RE.match(published):
        raise ManifestError(f"{tag}: published must be YYYY-MM, got {published!r}")
    autonomy = str(raw["autonomy"]).strip().lower()
    if autonomy not in AUTONOMY:
        raise ManifestError(
            f"{tag}: autonomy must be one of {', '.join(AUTONOMY)}, got {raw['autonomy']!r}")
    caption = str(raw.get("caption") or "visible").strip().lower()
    if caption not in CAPTION:
        raise ManifestError(
            f"{tag}: caption must be one of {', '.join(CAPTION)}, got {raw['caption']!r}")
    redistribution = raw.get("redistribution", "classroom")
    if redistribution not in REDISTRIBUTION:
        raise ManifestError(f"{tag}: redistribution must be classroom or release")
    keep_audio = raw.get("keep_audio", False)
    if not isinstance(keep_audio, bool):
        raise ManifestError(f"{tag}: keep_audio must be true or false, got {keep_audio!r}")
    speed = str(raw.get("speed") or "1x")
    start, end = parse_segment(raw.get("segment"))
    if raw.get("segment") is not None and raw.get("source") in (None, ""):
        raise ManifestError(
            f"{tag}: segment needs a source to cut from (without source, "
            f"videos/{slug}.mp4 is taken as final)")
    source_url = str(raw["source_url"])
    if not re.match(r"^https?://", source_url):
        raise ManifestError(f"{tag}: source_url must be an http(s) publisher URL")

    out = {
        "slug": slug,
        "title": str(raw["title"]),
        "publisher": str(raw["publisher"]),
        "source_url": source_url,
        "published": published,
        "autonomy": autonomy,
        "redistribution": redistribution,
        "speed": speed,
        "segment": None if raw.get("segment") is None else str(raw["segment"]),
        "source": None if raw.get("source") in (None, "") else str(raw["source"]),
        "keep_audio": keep_audio,
        "caption": caption,
        "licence_note": None if raw.get("licence_note") in (None, "") else str(raw["licence_note"]),
    }
    out["_start"], out["_end"] = start, end
    return out


def load_manifest(path: Path, content: bytes | None = None) -> list[dict]:
    if not path.exists():
        raise ManifestError(f"{path}: no such file (write the manifest first)")
    try:
        content = path.read_bytes() if content is None else content
        data = minyaml.loads(content.decode("utf-8"), name=path.name)
    except (UnicodeDecodeError, minyaml.MinYamlError):
        # YAML diagnostics can quote the offending line, including a source path.
        raise ManifestError("invalid YAML in videos.yml") from None
    where = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    if not isinstance(data, dict) or "videos" not in data:
        raise ManifestError(f"{where}: expected a top-level 'videos:' list")
    extra = sorted(set(data) - {"videos"})
    if extra:
        raise ManifestError(f"{where}: unknown top-level key(s): {', '.join(extra)}")
    videos = data["videos"]
    if not isinstance(videos, list) or not videos:
        raise ManifestError(f"{where}: 'videos:' must be a non-empty list")
    entries = [validate_entry(v, i, where) for i, v in enumerate(videos)]
    seen = set()
    for e in entries:
        if e["slug"] in seen:
            raise ManifestError(f"{where}: duplicate slug {e['slug']!r}")
        seen.add(e["slug"])
    return entries


# ----------------------------------------------------------------------------
# URLs and paths


def release_url(tag: str, filename: str, base: str = RELEASE_BASE) -> str:
    return f"{base}/{tag}/{filename}"


def local_rel_path(qmd_dir: Path, videos_dir: Path, filename: str) -> str:
    """The src a deck at qmd_dir uses for a local clip: relative, POSIX."""
    return Path(os.path.relpath(videos_dir / filename, qmd_dir)).as_posix()


def is_ours(url) -> bool:
    return isinstance(url, str) and bool(RELEASE_URL_RE.match(url))


# ----------------------------------------------------------------------------
# ffmpeg


def _tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    brew = Path("/opt/homebrew/bin") / name
    if brew.exists():
        return str(brew)
    raise ManifestError(f"{name} not found on PATH or in /opt/homebrew/bin")


def ffmpeg_cmd(src: Path, dst: Path, start: float, end: float | None,
               keep_audio: bool) -> list[str]:
    cmd = [_tool("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{start:g}"]
    if end is not None:
        cmd += ["-to", f"{end:g}"]
    cmd += ["-i", str(src),
            "-vf", "scale=1280:-2",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-maxrate", "8M", "-bufsize", "16M",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    cmd += ["-c:a", "aac", "-b:a", "128k"] if keep_audio else ["-an"]
    cmd += [str(dst)]
    return cmd


def poster_cmd(src: Path, dst: Path, start: float) -> list[str]:
    return [_tool("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:g}", "-i", str(src),
            "-frames:v", "1", "-vf", "scale=1280:-2", "-q:v", "3", str(dst)]


def probe(path: Path) -> tuple[float, float]:
    """-> (size_mb, duration_s); size to two decimals so a 15 KB fixture
    clip does not print as 0.0, duration to one."""
    out = subprocess.run(
        [_tool("ffprobe"), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    duration = float(out) if out else 0.0
    return round(path.stat().st_size / 1e6, 2), round(duration, 1)


def manifest_id(content: bytes) -> str:
    # Pandoc exposes SHA-1 in Lua. This is a freshness check on local inputs.
    return hashlib.sha1(content).hexdigest()


def cut_of(entry: dict) -> dict:
    """Parameters affecting the prepared file. The source name stays local."""
    source = entry.get("source")
    return {"segment": entry.get("segment"), "keep_audio": entry["keep_audio"],
            "source_id": hashlib.sha256(source.encode()).hexdigest() if source else None}


def _older(dst: Path, src: Path) -> bool:
    return not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime


def stale_reason(dst: Path, src: Path, want: dict, prev_cut: dict | None) -> str | None:
    """Why dst must be re-encoded from src, or None when it is fresh.

    `want` is cut_of(the manifest entry); `prev_cut` is the "cut" record of
    the same slug in the existing videos.json (None when there is none).
    """
    if not dst.exists():
        return "missing"
    if dst.stat().st_mtime < src.stat().st_mtime:
        return "source is newer"
    if prev_cut is None:
        return "no record of the cut in videos.json"
    changed = [f"{k} changed" for k in want if prev_cut.get(k) != want[k]]
    if changed:
        return ", ".join(changed)
    return None


def lock_mismatches(lock: dict, entries: list[dict]) -> list[str]:
    """Check that approved files still correspond to their declared cuts."""
    videos = {v["slug"]: v for v in lock["videos"]}
    if len(videos) != len(lock["videos"]) or videos.keys() != {e["slug"] for e in entries}:
        return ["clip list differs from the manifest"]
    errors = []
    for e in entries:
        slug = e["slug"]
        rec = videos[slug]
        if rec.get("redistribution", "classroom") != e["redistribution"]:
            errors.append(f"{slug}: redistribution differs from the manifest")
        if e["redistribution"] == "release" and e["source"]:
            recorded = rec.get("cut") or {}
            for key, value in cut_of(e).items():
                if recorded.get(key) != value:
                    errors.append(f"{slug}: {key} differs from the prepared cut")
    return errors


def release_assets(home: deckpath.MediaHome) -> list[tuple[str, str]]:
    """Build the upload list from current explicit approvals and verified lock records."""
    content = home.manifest.read_bytes()
    entries = load_manifest(home.manifest, content)
    lock = json.loads(home.lock.read_text(encoding="utf-8"))
    if lock.get("release_tag") != home.release_tag:
        raise ManifestError("release tag differs from videos.json; run media_prep.py")
    if lock.get("manifest_sha1") != manifest_id(content):
        raise ManifestError("videos.json is stale; run media_prep.py")
    bad = lock_mismatches(lock, entries)
    if bad:
        raise ManifestError("; ".join(bad) + "; run media_prep.py")
    videos = {v["slug"]: v for v in lock["videos"]}
    assets = []
    for entry in entries:
        if entry["redistribution"] != "release":
            continue
        slug = entry["slug"]
        rec = videos[slug]
        for name_key, url_key, filename in (("file", "release_url", f"{slug}.mp4"),
                                            ("poster_file", "poster_url", f"{slug}-poster.jpg")):
            url = rec.get(url_key)
            if not isinstance(url, str) or not re.fullmatch(r"https?://[^\s|]+", url):
                raise ManifestError(f"{slug}: invalid {url_key} in videos.json")
            # The approved slug determines the filename even if someone edits
            # the lock. Check its mapping before opening any files or calling gh.
            if rec.get(name_key) != filename:
                raise ManifestError(f"{slug}: invalid {name_key} in videos.json")
            assets.append((filename, url))
    return assets


def restricted_media_urls(home: deckpath.MediaHome) -> set[str]:
    """Release URLs a public deck must never embed, even with a stale lock."""
    entries = load_manifest(home.manifest)
    approved = {e["slug"] for e in entries if e["redistribution"] == "release"}
    restricted = {e["slug"] for e in entries} - approved
    locked = json.loads(home.lock.read_text(encoding="utf-8"))["videos"] if home.lock.exists() else []
    urls = set()
    for video in locked:
        if video["slug"] not in approved:
            restricted.add(video["slug"])
            urls.update(video[k] for k in ("release_url", "poster_url") if video.get(k))
    for slug in restricted:
        urls.update(release_url(home.release_tag, slug + suffix) for suffix in (".mp4", "-poster.jpg"))
    return urls


# ----------------------------------------------------------------------------
# main flow


def prepare(home: "deckpath.MediaHome", only: str | None = None, dry_run: bool = False,
            force: bool = False, local: bool = False, log=print) -> dict:
    """Encode what the manifest asks for and return the videos.json payload.

    Writes the lock file unless dry_run. `only` restricts encoding to one
    slug; the lock file still lists every entry (it is regenerated whole).
    """
    content = home.manifest.read_bytes()
    entries = load_manifest(home.manifest, content)
    if only and only not in {e["slug"] for e in entries}:
        raise ManifestError(f"--only {only}: no such slug in {home.manifest}")
    videos_dir = home.videos_dir
    if not dry_run:
        videos_dir.mkdir(parents=True, exist_ok=True)

    previous = {}
    if home.lock.exists():
        try:
            for v in json.loads(home.lock.read_text(encoding="utf-8")).get("videos", []):
                previous[v.get("slug")] = v
        except (OSError, ValueError):
            previous = {}

    out_videos = []
    for e in entries:
        slug = e["slug"]
        mp4 = videos_dir / f"{slug}.mp4"
        poster = videos_dir / f"{slug}-poster.jpg"
        do_work = only is None or only == slug

        if e["source"] is None:
            src = None
            if do_work and not mp4.exists() and not dry_run:
                raise ManifestError(
                    f"{slug}: place the prepared MP4 in the deck’s videos directory")
        else:
            src = Path(e["source"])
            # normpath, not resolve(): videos/ may not exist yet, and a
            # relative source that climbs out of it ("../../assets/x.mp4")
            # cannot be tested for existence through a missing directory.
            src = Path(os.path.normpath(src if src.is_absolute() else (videos_dir / src)))
            if do_work and not src.is_file():
                raise ManifestError(f"{slug}: source file is missing")

        prev = previous.get(slug, {})
        cut = None  # what <slug>.mp4 on disk was cut with, for the lock
        if do_work:
            if src is not None:
                want = cut_of(e)
                reason = "--force" if force else stale_reason(mp4, src, want, prev.get("cut"))
                if reason:
                    cmd = ffmpeg_cmd(src, mp4, e["_start"], e["_end"], e["keep_audio"])
                    log(f"  encode  {slug}.mp4 [{e['segment'] or 'whole'}]"
                        f"  ({reason})")
                    if not dry_run:
                        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
                else:
                    log(f"  fresh   {slug}.mp4")
                # The poster is the frame at the segment start: a changed cut
                # moves it, so it follows every re-encode.
                if reason or _older(poster, src):
                    cmd = poster_cmd(src, poster, e["_start"])
                    log(f"  poster  {slug}-poster.jpg @ {e['_start']:g}s")
                    if not dry_run:
                        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
                # After this run the file matches the manifest (encoded now,
                # or fresh and proven to match); a dry run changes nothing,
                # so it keeps the previous record.
                cut = prev.get("cut") if dry_run else want
            else:
                # slug.mp4 is final; only the poster may be missing.
                if force or _older(poster, mp4):
                    cmd = poster_cmd(mp4, poster, 0.0)
                    log(f"  poster  {slug}-poster.jpg  <- {mp4.name} @ 0s")
                    if not dry_run:
                        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        else:
            # --only skipped this slug: the file on disk is whatever the
            # previous run cut, so its record travels unchanged.
            cut = prev.get("cut")

        size_mb, duration_s = prev.get("size_mb", 0.0), prev.get("duration_s", 0.0)
        if mp4.exists():
            size_mb, duration_s = probe(mp4)
            if size_mb > SIZE_WARN_MB:
                log(f"  WARNING {slug}.mp4 is {size_mb} MB (> {SIZE_WARN_MB:g} MB): "
                    f"shorten the segment or raise the speed")

        rec = {k: v for k, v in e.items()
               if k not in ("source", "licence_note") and not k.startswith("_")}
        rec["file"] = mp4.name
        rec["poster_file"] = poster.name
        rec["size_mb"] = size_mb
        rec["duration_s"] = duration_s
        rec["autonomy_label"] = AUTONOMY_LABEL[e["autonomy"]]
        if cut is not None and "source_id" in cut:
            rec["cut"] = cut
        if src and cut != cut_of(e):
            rec["needs_prep"] = True
        if e["redistribution"] == "release":
            for key, filename in (("release_url", mp4.name), ("poster_url", poster.name)):
                old = prev.get(key)
                if old and not re.fullmatch(r"https?://[^\s|]+", str(old)):
                    raise ManifestError(f"{slug}: invalid {key} in videos.json")
                rec[key] = old if old and not is_ours(old) else release_url(home.release_tag, filename)
        if local:
            rec["local_only"] = True
        out_videos.append(rec)

    payload = {
        "deck": home.slug,
        "release_tag": home.release_tag,
        "generated_by": "scripts/media_prep.py",
        "manifest_sha1": manifest_id(content),
        "videos": out_videos,
    }
    if not dry_run:
        with tempfile.TemporaryDirectory(dir=home.lock.parent) as tmp:
            written = Path(tmp) / "videos.json"
            written.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            written.replace(home.lock)
        log(f"wrote {_rel(home.lock)} ({len(out_videos)} clip(s)"
            f"{', local_only' if local else ''})")
    return payload


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("deck", help="deck name, genre/name, a videos.yml path, or its directory")
    ap.add_argument("--only", metavar="SLUG", help="encode one clip only")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--force", action="store_true", help="re-encode even when outputs are fresh")
    ap.add_argument("--local", action="store_true",
                    help="prefer local files for approved videos in classroom delivery")
    args = ap.parse_args(argv)

    try:
        home = deckpath.find_media(args.deck)
        print(f"{home.slug}: manifest {_rel(home.manifest)}, release tag {home.release_tag}")
        prepare(home, only=args.only, dry_run=args.dry_run, force=args.force, local=args.local)
    except (deckpath.DeckNotFound, deckpath.AmbiguousDeck, ManifestError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"error: media file operation failed ({e.strerror})", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"error: {e.cmd[0]} failed with exit code {e.returncode}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
