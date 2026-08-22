#!/usr/bin/env python3
"""Parse the small YAML subset this repo's config files actually use.

Why not PyYAML. The profile system decides how a deck is graded, and it sat
one missing `pip install` away from silently grading a lecture with
paper-review numbers: the loader caught ImportError, warned on stderr, and
returned an empty dict, so a deck kept scoring and kept passing the gate with
the wrong budget and both lecture checks switched off. An undeclared
dependency that fails soft is worse than a parser we own.

This handles exactly what <deck>.deck.yml, .claude/rules/slide-profiles/
*.yml and the per-deck asset manifests (figures.yml, videos.yml) contain:
nested mappings by indent, scalars, quoted strings, inline comments, flow
sequences, block sequences, block sequences of mappings (`- file: x` with
the item's remaining keys indented under it), and block scalars (| and >).

Everything else -- anchors, aliases, tags, multiple documents, flow mappings,
tab indentation -- raises MinYamlError naming the file and line. So does a
bare number whose value depends on the YAML version (`0123`, `1_000`):
quoting it is one character, guessing at it is a Wooclap code printed wrong
on a slide. Refusing to read a file is a fine outcome. Reading it wrong is
not, which is the whole reason this exists.

Verified against PyYAML on every config file in the repo by
scripts/test_minyaml.py, which is what keeps "small subset" honest.
"""
from __future__ import annotations

import re
from pathlib import Path

BLOCK_MARKERS = ("|", ">", "|-", ">-", "|+", ">+")
_BOOLS = {"true": True, "false": False, "yes": True, "no": False,
          "on": True, "off": False}

# A sequence item that is itself a mapping: `- key: value` or `- key:` (the
# value nested below). The key must look like a plain YAML key so that
# `- https://example.org` and `- 12:30` stay scalars.
_MAPPING_ITEM_RE = re.compile(r"^[A-Za-z0-9_][\w.-]*:(\s|$)")

# A bare scalar that Python's int()/float() would read one way and YAML
# another: a leading zero, or a digit separator. See _scalar().
_AMBIGUOUS_NUMBER_RE = re.compile(r"^[+-]?(?:0\d+|\d[\d_]*_[\d_]*)$")


class MinYamlError(ValueError):
    """The file used something this parser will not guess at."""


def _strip_comment(line: str) -> str:
    """Drop a trailing comment, honouring quotes.

    `assumes: practitioner   # none | practitioner | expert` loses the note;
    `title: "Rewards # and penalties"` keeps its hash.
    """
    out: list[str] = []
    quote = None
    i = 0
    while i < len(line):
        c = line[i]
        if quote:
            if quote == '"' and c == "\\" and i + 1 < len(line):
                out.append(c)
                out.append(line[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            out.append(c)
        elif c in "\"'":
            quote = c
            out.append(c)
        elif c == "#" and (not out or out[-1] in " \t"):
            break
        else:
            out.append(c)
        i += 1
    return "".join(out).rstrip()


def _split_flow(inner: str) -> list[str]:
    """Split `a, "b, c", d` on the commas that are not inside quotes."""
    parts: list[str] = []
    buf: list[str] = []
    quote = None
    for c in inner:
        if quote:
            buf.append(c)
            if c == quote:
                quote = None
        elif c in "\"'":
            quote = c
            buf.append(c)
        elif c == ",":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(c)
    if quote:
        raise MinYamlError("unterminated quote in flow sequence")
    tail = "".join(buf)
    if tail.strip() or parts:
        parts.append(tail)
    return parts


def _scalar(token: str, where: str):
    token = token.strip()
    if token in ("", "~") or token.lower() == "null":
        return None

    if token[0] in "\"'":
        if len(token) < 2 or token[-1] != token[0]:
            raise MinYamlError(f"{where}: unterminated quoted string")
        body = token[1:-1]
        if token[0] == '"':
            body = (body.replace("\\\\", "\x00").replace('\\"', '"')
                        .replace("\\n", "\n").replace("\\t", "\t")
                        .replace("\x00", "\\"))
        else:
            body = body.replace("''", "'")
        return body

    if token[0] == "[":
        if token[-1] != "]":
            raise MinYamlError(f"{where}: flow sequence is not closed")
        return [_scalar(p, where) for p in _split_flow(token[1:-1])]

    if token[0] == "{":
        raise MinYamlError(f"{where}: flow mappings are not supported")
    if token[0] in "&*!":
        raise MinYamlError(
            f"{where}: anchors, aliases and tags are not supported")

    low = token.lower()
    if low in _BOOLS:
        return _BOOLS[low]

    # Numbers whose meaning depends on which YAML version you ask. `0123` is
    # octal 83 in YAML 1.1 (PyYAML), an invalid int and therefore a string in
    # YAML 1.2, and an identifier to whoever typed it -- a Wooclap code, a
    # room number, a zero-padded index. Python's int() would silently return
    # 123, which is none of the three. Underscores are the same story
    # (`1_000` is 1000 in YAML 1.1, a string in 1.2). Refuse both and say so:
    # quoting is one character and removes the question.
    if _AMBIGUOUS_NUMBER_RE.match(token):
        raise MinYamlError(
            f"{where}: {token!r} reads as a different number in different YAML "
            f"versions (leading zero or underscore). Quote it to keep it a "
            f"string, or write it without the padding to mean the number")

    # `inf` / `nan` are plain words to YAML (it spells them `.inf` / `.nan`)
    # but floats to Python. Keep PyYAML's answer.
    if low.lstrip("+-") in ("inf", "infinity", "nan"):
        return token

    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token


class _Reader:
    def __init__(self, text: str, name: str):
        self.lines = text.splitlines()
        self.name = name
        self.i = 0

    # -- cursor helpers ---------------------------------------------------

    def where(self) -> str:
        return f"{self.name}:{self.i + 1}"

    def seek(self) -> bool:
        """Park the cursor on the next line that carries content."""
        while self.i < len(self.lines):
            stripped = self.lines[self.i].strip()
            if stripped == "" or stripped.startswith("#"):
                self.i += 1
                continue
            if stripped in ("---", "..."):
                raise MinYamlError(
                    f"{self.where()}: document markers are not supported")
            return True
        return False

    def indent_of(self, raw: str) -> int:
        lead = raw[:len(raw) - len(raw.lstrip())]
        if "\t" in lead:
            raise MinYamlError(f"{self.where()}: tab used for indentation")
        return len(lead)

    # -- grammar ----------------------------------------------------------

    def parse_node(self, indent: int):
        raw = self.lines[self.i]
        content = _strip_comment(raw.strip())
        if content == "-" or content.startswith("- "):
            return self.parse_sequence(indent)
        return self.parse_mapping(indent)

    def parse_mapping(self, indent: int) -> dict:
        result: dict = {}
        while self.seek():
            raw = self.lines[self.i]
            ind = self.indent_of(raw)
            if ind < indent:
                break
            if ind > indent:
                raise MinYamlError(
                    f"{self.where()}: unexpected indent (expected {indent})")

            content = _strip_comment(raw.strip())
            if content.startswith("- "):
                raise MinYamlError(
                    f"{self.where()}: list item where a key was expected")

            key, sep, rest = content.partition(":")
            if not sep:
                raise MinYamlError(f"{self.where()}: expected 'key: value'")
            key_token = key.strip()
            key = (_scalar(key_token, self.where())
                   if key_token[:1] in "\"'" else key_token)
            if key in result:
                raise MinYamlError(f"{self.where()}: duplicate key {key!r}")
            rest = rest.strip()
            self.i += 1

            if rest in BLOCK_MARKERS:
                result[key] = self.parse_block_scalar(rest, indent)
            elif rest == "":
                result[key] = self.parse_child(indent)
            else:
                result[key] = _scalar(rest, self.where())
        return result

    def parse_sequence(self, indent: int) -> list:
        items: list = []
        while self.seek():
            raw = self.lines[self.i]
            ind = self.indent_of(raw)
            if ind < indent:
                break
            if ind > indent:
                raise MinYamlError(
                    f"{self.where()}: unexpected indent in list")
            content = _strip_comment(raw.strip())
            if not (content == "-" or content.startswith("- ")):
                break
            rest = content[1:].strip()
            if _MAPPING_ITEM_RE.match(rest):
                # `- file: x` opens a mapping whose remaining keys sit at the
                # column of `file`. Re-point the line at that column and let
                # parse_mapping read it and everything indented to match;
                # it stops by itself at the next `- ` (a shallower indent).
                after_dash = raw[ind + 1:]
                key_col = ind + 1 + (len(after_dash) - len(after_dash.lstrip()))
                self.lines[self.i] = " " * key_col + raw[key_col:]
                items.append(self.parse_mapping(key_col))
                continue
            self.i += 1
            if rest == "":
                items.append(self.parse_child(indent))
            elif rest in BLOCK_MARKERS:
                items.append(self.parse_block_scalar(rest, indent))
            else:
                items.append(_scalar(rest, self.where()))
        return items

    def parse_child(self, parent_indent: int):
        """The value written under a `key:` line, or None if there is none."""
        if not self.seek():
            return None
        raw = self.lines[self.i]
        ind = self.indent_of(raw)
        content = _strip_comment(raw.strip())
        # A block sequence may sit at the parent's own indent -- that is
        # legal YAML and reads naturally, so accept it rather than demand
        # the deeper form.
        if ind == parent_indent and (content == "-" or content.startswith("- ")):
            return self.parse_sequence(ind)
        if ind <= parent_indent:
            return None
        return self.parse_node(ind)

    def parse_block_scalar(self, marker: str, parent_indent: int) -> str:
        style = marker[0]
        chomp = marker[1:]
        raw_lines: list[str] = []
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            if raw.strip() == "":
                raw_lines.append("")
                self.i += 1
                continue
            if self.indent_of(raw) <= parent_indent:
                break
            raw_lines.append(raw)
            self.i += 1

        while raw_lines and raw_lines[-1] == "":
            raw_lines.pop()
        if not raw_lines:
            return "" if chomp == "-" else "\n"

        base = min(len(l) - len(l.lstrip()) for l in raw_lines if l.strip())
        body = [l[base:] if l.strip() else "" for l in raw_lines]

        if style == "|":
            text = "\n".join(body)
        else:
            # Folded: a single newline between two non-empty lines becomes a
            # space; a blank line stays a paragraph break.
            chunks: list[str] = []
            run: list[str] = []
            for line in body:
                if line == "":
                    if run:
                        chunks.append(" ".join(run))
                        run = []
                    chunks.append("")
                else:
                    run.append(line)
            if run:
                chunks.append(" ".join(run))
            text = ""
            pending_breaks = 0
            for chunk in chunks:
                if chunk == "":
                    pending_breaks += 1
                    continue
                if text:
                    text += "\n" * max(pending_breaks, 1)
                pending_breaks = 0
                text += chunk

        if chomp == "-":
            return text
        return text + "\n"


def loads(text: str, name: str = "<string>") -> dict:
    reader = _Reader(text, name)
    if not reader.seek():
        return {}
    value = reader.parse_node(reader.indent_of(reader.lines[reader.i]))
    if reader.seek():
        raise MinYamlError(f"{reader.where()}: trailing content")
    return value if value is not None else {}


def load_path(path: Path) -> dict:
    return loads(Path(path).read_text(encoding="utf-8"), Path(path).name)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        sys.exit("usage: python3 scripts/minyaml.py <file.yml>")
    try:
        print(json.dumps(load_path(Path(sys.argv[1])), indent=2))
    except MinYamlError as e:
        sys.exit(f"error: {e}")
