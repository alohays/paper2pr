#!/usr/bin/env python3
"""Convert vault HTML slides to QMD-ready content for Quarto RevealJS.

Usage:
    python3 scripts/prefix_slide_css.py <html_file> --slide-num <N>

Each vault slide is a standalone HTML file. This script:
1. Extracts title, CSS, body classes, and body content via regex.
2. Extracts the first <h1> text for the slide heading and removes it from body.
3. Processes CSS with tinycss2: skips universal reset, rewrites body -> #sNN,
   prefixes all other selectors with #sNN.
4. Fixes asset paths for Quarto figure directory.
5. Adds video poster attributes where missing.
6. Handles Korean text replacement (slide-14).
7. Outputs QMD-ready markdown to stdout.
"""

from __future__ import annotations

import argparse
import re
import sys

import tinycss2


def extract_body_content_raw(html: str) -> str:
    """Extract raw inner HTML of <body> preserving original formatting."""
    m = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    if not m:
        return ""
    return m.group(1)


def extract_body_attrs(html: str) -> tuple[list[str], str]:
    """Extract body class list and inline style."""
    m = re.search(r'<body([^>]*)>', html)
    if not m:
        return [], ""
    attr_str = m.group(1)
    cls_m = re.search(r'class="([^"]*)"', attr_str)
    classes = cls_m.group(1).split() if cls_m else []
    style_m = re.search(r'style="([^"]*)"', attr_str)
    style = style_m.group(1) if style_m else ""
    return classes, style


def extract_style_content(html: str) -> str:
    """Extract content of all <style> blocks in <head>."""
    head_m = re.search(r'<head[^>]*>(.*?)</head>', html, re.DOTALL)
    if not head_m:
        return ""
    head_content = head_m.group(1)
    parts = []
    for m in re.finditer(r'<style[^>]*>(.*?)</style>', head_content, re.DOTALL):
        parts.append(m.group(1))
    return "\n".join(parts)


def extract_title(html: str) -> str:
    """Extract <title> text."""
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_h1_text(body_html: str) -> tuple[str, str]:
    """Find the first <h1> in body, extract its text, return (text, body_without_h1).

    The h1 may contain inline HTML like <br> tags.
    """
    m = re.search(r'<h1[^>]*>(.*?)</h1>', body_html, re.DOTALL)
    if not m:
        return "", body_html
    h1_inner = m.group(1)
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h1_inner).strip())
    body_without_h1 = body_html[:m.start()] + body_html[m.end():]
    return text, body_without_h1


def is_universal_reset(rule) -> bool:
    """Check if a rule is `* { margin: 0; padding: 0; ... }`."""
    if not isinstance(rule, tinycss2.ast.QualifiedRule):
        return False
    selector = tinycss2.serialize(rule.prelude).strip()
    if selector != "*":
        return False
    decl_text = tinycss2.serialize(rule.content).lower()
    return "margin" in decl_text and "padding" in decl_text


def is_body_rule(rule) -> bool:
    """Check if a rule targets `body`."""
    if not isinstance(rule, tinycss2.ast.QualifiedRule):
        return False
    selector = tinycss2.serialize(rule.prelude).strip()
    return selector == "body"


BODY_REMOVE_PROPS = {"width", "height", "overflow", "position"}
BODY_BG_PROPS = {"background", "background-color"}


def process_body_rule(rule, slide_id: str) -> tuple[str, str | None]:
    """Process a body rule: extract bg, remove width/height/overflow, rewrite selector.

    Returns (css_text_for_slide_id_rule, background_value_or_None).
    """
    declarations = tinycss2.parse_declaration_list(rule.content)
    keep_decls = []
    bg_value = None

    for decl in declarations:
        if isinstance(decl, tinycss2.ast.Declaration):
            prop = decl.name.strip().lower()
            if prop in BODY_REMOVE_PROPS:
                continue
            if prop in BODY_BG_PROPS:
                bg_value = tinycss2.serialize(decl.value).strip()
            keep_decls.append(decl)

    decl_parts = []
    for decl in keep_decls:
        important = " !important" if decl.important else ""
        decl_parts.append(f"  {decl.name}: {tinycss2.serialize(decl.value).strip()}{important};")

    decl_text = "\n".join(decl_parts)
    css_text = f"{slide_id} {{\n  position: relative; width: 100%; height: 100%;\n{decl_text}\n}}"
    return css_text, bg_value


def prefix_selector(selector_str: str, slide_id: str) -> str:
    """Prefix each comma-separated selector with the slide ID.

    Examples:
        .headline -> #s05 .headline
        .grid .cell -> #s05 .grid .cell
        .tide-line::before, .tide-line::after -> #s05 .tide-line::before, #s05 .tide-line::after
        h1 -> #s05 h1
    """
    parts = [s.strip() for s in selector_str.split(",")]
    prefixed = [f"{slide_id} {p}" for p in parts if p]
    return ", ".join(prefixed)


def process_css(style_content: str, slide_id: str) -> tuple[str, str | None]:
    """Process the full CSS content, returning (prefixed_css, bg_color_or_None)."""
    rules = tinycss2.parse_stylesheet(style_content, skip_whitespace=True, skip_comments=True)
    output_parts = []
    bg_value = None

    for rule in rules:
        if isinstance(rule, tinycss2.ast.QualifiedRule):
            if is_universal_reset(rule):
                continue

            if is_body_rule(rule):
                css_text, bg = process_body_rule(rule, slide_id)
                if bg:
                    bg_value = bg
                output_parts.append(css_text)
                continue

            selector = tinycss2.serialize(rule.prelude).strip()
            prefixed_sel = prefix_selector(selector, slide_id)
            body_text = tinycss2.serialize(rule.content).strip()
            output_parts.append(f"{prefixed_sel} {{ {body_text} }}")

        elif isinstance(rule, tinycss2.ast.AtRule):
            if rule.lower_at_keyword == "media" and rule.content:
                inner_rules = tinycss2.parse_stylesheet(
                    tinycss2.serialize(rule.content),
                    skip_whitespace=True,
                    skip_comments=True,
                )
                inner_parts = []
                for inner in inner_rules:
                    if isinstance(inner, tinycss2.ast.QualifiedRule):
                        sel = tinycss2.serialize(inner.prelude).strip()
                        prefixed = prefix_selector(sel, slide_id)
                        body = tinycss2.serialize(inner.content).strip()
                        inner_parts.append(f"  {prefixed} {{ {body} }}")
                prelude = tinycss2.serialize(rule.prelude).strip()
                inner_text = "\n".join(inner_parts)
                output_parts.append(f"@media {prelude} {{\n{inner_text}\n}}")
            else:
                output_parts.append(tinycss2.serialize([rule]).strip())

    return "\n".join(output_parts), bg_value


ASSET_PATH_REPLACEMENTS = [
    ("./assets/wrtn/", "../Figures/SUNY/wrtn/"),
    ("./assets/worv/", "../Figures/SUNY/worv/"),
    ("./assets/d2e/", "../Figures/SUNY/d2e/"),
    ("./assets/videos/", "../Figures/SUNY/videos/"),
    ("./assets/vendor/", "../Figures/SUNY/vendor/"),
    ("./assets/surfer-wave-silhouette.svg", "../Figures/SUNY/surfer-wave-silhouette.svg"),
]


def fix_asset_paths(text: str) -> str:
    """Replace vault asset paths with Quarto figure directory paths."""
    for old, new in ASSET_PATH_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def add_video_posters(html: str) -> str:
    """For <video src="..."> tags without a poster attribute, add poster with -poster.jpg."""
    def _add_poster(m: re.Match) -> str:
        tag = m.group(0)
        if 'poster=' in tag:
            return tag
        src_m = re.search(r'src="([^"]*)"', tag)
        if not src_m:
            return tag
        src = src_m.group(1)
        base = re.sub(r'\.[^.]+$', '', src)
        poster = f'{base}-poster.jpg'
        tag = tag.replace(src_m.group(0), f'{src_m.group(0)} poster="{poster}"')
        return tag

    return re.sub(r'<video\b[^>]*>', _add_poster, html)


def handle_korean_text(text: str, slide_num: int) -> str:
    """Replace Korean text for specific slides."""
    if slide_num == 14:
        text = text.replace("\ub098\ub9cc\uc758 AI", "Your Own AI")
    return text


def strip_link_tags(html: str) -> str:
    """Remove all <link ...> tags from HTML content."""
    return re.sub(r'<link\b[^>]*/?>', '', html)


def extract_bg_color(bg_value: str | None, body_classes: list[str]) -> str:
    """Determine the background color for the slide heading attribute.

    For gradients, extracts the first hex color.
    Falls back to class-based detection or default navy.
    """
    if bg_value:
        hex_m = re.search(r'#[0-9A-Fa-f]{3,8}', bg_value)
        if hex_m:
            return hex_m.group(0)
        rgb_m = re.search(r'rgba?\([^)]+\)', bg_value)
        if rgb_m:
            return rgb_m.group(0)

    if "deck-light" in body_classes:
        return "#F8F7F4"

    return "#0B1D3A"


def clean_slide_title(title_text: str) -> str:
    """Strip 'Slide NN — ' prefix from title text."""
    m = re.match(r'Slide\s+\d+\s*[\u2014\u2013\-]+\s*', title_text)
    if m:
        return title_text[m.end():]
    return title_text


KEEP_BODY_CLASSES = {"deck-dark", "deck-light", "deck-poster", "deck-manifesto", "deck-cover"}


def filter_body_classes(classes: list[str]) -> list[str]:
    """Keep only the classes that should transfer to the wrapper div."""
    return [c for c in classes if c in KEEP_BODY_CLASSES]


def process_slide(html_path: str, slide_num: int) -> str:
    """Process a single HTML slide file and return QMD-ready markdown."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    slide_id = f"#s{slide_num:02d}"
    nn = f"{slide_num:02d}"

    title_raw = extract_title(html)
    style_content = extract_style_content(html)
    body_classes, _ = extract_body_attrs(html)
    body_html = extract_body_content_raw(html)
    body_html = strip_link_tags(body_html)

    prefixed_css, bg_value = process_css(style_content, slide_id)
    bg_color = extract_bg_color(bg_value, body_classes)

    prefixed_css = fix_asset_paths(prefixed_css)
    body_html = fix_asset_paths(body_html)
    body_html = add_video_posters(body_html)
    body_html = handle_korean_text(body_html, slide_num)
    prefixed_css = handle_korean_text(prefixed_css, slide_num)

    wrapper_classes = filter_body_classes(body_classes)
    class_str = " ".join(["suny-slide"] + wrapper_classes)

    lines = [
        f'## {{background-color="{bg_color}"}}',
        "",
        "```{=html}",
        "<style>",
        prefixed_css,
        "</style>",
        "",
        f'<div id="s{nn}" class="{class_str}">',
        body_html,
        "</div>",
        "```",
        "",
        "",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Convert vault HTML slides to QMD-ready content for Quarto RevealJS."
    )
    parser.add_argument("html_file", help="Path to the HTML slide file")
    parser.add_argument(
        "--slide-num", type=int, required=True, help="Slide number (e.g., 5 for slide-05)"
    )
    args = parser.parse_args()

    output = process_slide(args.html_file, args.slide_num)
    sys.stdout.write(output)


if __name__ == "__main__":
    main()
