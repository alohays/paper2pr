#!/usr/bin/env python3
"""
Quality Scoring System for Academic Course Materials

Calculates objective quality scores (0-100) based on defined rubrics.
Enforces quality gates: 80 (commit), 90 (PR), 95 (excellence).

Usage:
    python scripts/quality_score.py Quarto/papers/DreamZero.qmd
    python scripts/quality_score.py Quarto/papers/DreamZero.qmd --summary
    python scripts/quality_score.py Quarto/*/*.qmd

Which checks run is decided by the deck's profile (scripts/deckprofile.py,
.claude/rules/slide-profiles/<profile>.yml, `checks:`). Two of them are
BLOCKERS rather than deductions: any hit forces the score to 0 and a
non-zero exit, because the deck is either leaking or mis-rendering.

  level1_heading   a line starting with "# " after the front matter (outside
                   fences and notes). Quarto turns a level-1 heading into a
                   vertical stack and every following slide nests under it;
                   section dividers are written as "## {.divider}".
  forbidden_terms  Quarto/<genre>/<deck>.forbidden.txt exists and a term in
                   it appears in the visible slide text. File format: one
                   term per line, "#" starts a comment, blank lines are
                   ignored, matching is a case-insensitive substring match
                   on visible text (never on speaker notes). Seed it with
                   internal project names, unpublished numbers, anything
                   that must not reach a public page.

Visible text, for every check below, means the slide body outside fenced
code blocks, outside ::: {.notes} divs, outside the YAML front matter and
outside HTML comments. A raw block (```{=html} ... ```) is NOT a code block:
its content goes straight to the screen, so the dash lint, the forbidden-term
scan and the attribution check read it as visible text (tags, <style> and
<script> bodies stripped). The level-1 check does not: a "# " inside raw
HTML is literal text, not a heading, and makes no stack. Deductions
(dash_lint, attribution) are listed in .claude/rules/quality-gates.md.
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import re
import json

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deckprofile  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
# Anchored to the repo, not counted back from the deck. This used to be
# `filepath.parent.parent`, which was right only while every deck sat at the
# Quarto root; once decks moved to Quarto/<genre>/ it resolved to
# Quarto/Bibliography_base.bib, the file was not there, and every citation in
# the deck was reported broken -- a 100/100 deck scored 0 without a single
# character of it having changed.
BIB_FILE = REPO_ROOT / 'Bibliography_base.bib'

# ==============================================================================
# SCORING RUBRIC (from .claude/rules/quality-gates.md)
# ==============================================================================

QUARTO_RUBRIC = {
    'critical': {
        'compilation_failure': {'points': 100, 'auto_fail': True},
        'equation_overflow': {'points': 20},
        'broken_citation': {'points': 15},
        'typo_in_equation': {'points': 10},
        'missing_plotly_chart': {'points': 10},
    },
    'major': {
        'text_overflow': {'points': 5},
        'font_shrink_to_fit': {'points': 5},   # .smaller/.smallest or font-size override (new decks)
        'bullet_density': {'points': 3},       # >5 bullets, or >3 with a figure (new decks)
        'box_density': {'points': 3},          # >1 colored box per slide (new decks)
        'notation_inconsistency': {'points': 3},
        'unexpanded_acronym': {'points': 2},        # profiles with expand_acronyms
        'missing_prior_session_callback': {'points': 3},  # lecture profile only
        'dash_expression': {'points': 2, 'cap': 10},      # profiles with dash_lint
        'missing_attribution': {'points': 5, 'cap': 20},  # profiles with attribution
        'missing_box_separation': {'points': 2},
        'color_contrast_low': {'points': 3},
    },
    'minor': {
        'deep_nesting': {'points': 1},         # list nesting >1 sub-level (new decks)
        'font_size_reduction': {'points': 1},  # legacy decks only
        'missing_forward_ref': {'points': 1},
        'missing_framing_sentence': {'points': 1},
    }
}

# Blockers: not deductions. Any hit forces the score to 0 (see the module
# docstring). Kept out of QUARTO_RUBRIC so nothing sums them as points.
BLOCKERS = ('level1_heading', 'forbidden_term')

THRESHOLDS = {
    'commit': 80,
    'pr': 90,
    'excellence': 95
}

# ==============================================================================
# ISSUE DETECTION (Lightweight checks - full agents run separately)
# ==============================================================================

class IssueDetector:
    """Detect common issues for quality scoring."""

    @staticmethod
    def check_quarto_compilation(filepath: Path) -> Tuple[bool, str]:
        """Check if Quarto file compiles successfully.

        `--to html` used to be passed here. It overrode the deck's declared
        `format: revealjs` and wrote the result to the same <Name>.html, so
        merely *scoring* a deck replaced the rendered presentation with a
        plain scrolling page -- and one that strip_speaker_notes.py cannot
        clean, because notes come out as <div class="notes"> instead of
        <aside class="notes">. sync_to_docs.sh then copied that into the
        local preview. Letting the deck's own format win keeps the render a
        refresh instead of a destruction.
        """
        try:
            result = subprocess.run(
                ['quarto', 'render', str(filepath.name)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=filepath.parent
            )
            if result.returncode != 0:
                return False, result.stderr
            return True, ""
        except subprocess.TimeoutExpired:
            return False, "Compilation timeout (>2min)"
        except FileNotFoundError:
            return False, "Quarto not installed"

    @staticmethod
    def blank_fences_and_notes(content: str) -> str:
        """`content` with fenced blocks and `::: {.notes}` divs blanked out,
        line for line, so a caller keeps its line numbers.

        The math scanner below toggles on any `$$` it sees. A single `$$` in
        a shell snippet (`echo "pid $$"`) therefore opened a math block that
        never closed, and every line over 120 characters after it -- speaker
        notes included -- was billed -20 as an equation overflow (measured
        2026-08-22). Neither a fence nor a note holds a display equation the
        audience can see, so neither is read.
        """
        out = []
        in_yaml = False
        in_fence = False
        notes_depth = 0
        div_stack = []
        for i, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            blank = ''
            if i == 1 and stripped == '---':
                in_yaml = True
                out.append(blank)
                continue
            if in_yaml:
                if stripped == '---':
                    in_yaml = False
                out.append(blank)
                continue
            if stripped.startswith('```'):
                in_fence = not in_fence
                out.append(blank)
                continue
            if in_fence:
                out.append(blank)
                continue
            if stripped.startswith(':::'):
                bare = stripped.lstrip(':').strip()
                if bare:
                    is_notes = '.notes' in bare or bare == 'notes'
                    div_stack.append(is_notes)
                    if is_notes:
                        notes_depth += 1
                elif div_stack and div_stack.pop():
                    notes_depth -= 1
                out.append(blank)
                continue
            out.append(blank if notes_depth > 0 else line)
        return '\n'.join(out)

    @staticmethod
    def check_equation_overflow(content: str) -> List[int]:
        """Detect displayed equations with single lines likely to overflow.

        Flags equations only when a SINGLE LINE within a math block exceeds
        120 characters. Multi-line equations properly broken across lines
        are not flagged even if the total block is long.

        Checks:
        - $$ ... $$ blocks (Quarto/LaTeX)
        - \\begin{equation} ... \\end{equation} blocks
        - \\begin{align} ... \\end{align} blocks
        - \\begin{gather} ... \\end{gather} blocks
        """
        overflows = []
        lines = IssueDetector.blank_fences_and_notes(content).split('\n')
        in_math = False
        math_start = 0
        math_delim = None  # Track which delimiter opened the block

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # A `$$` that is never closed used to run to the end of the file.
            # A slide boundary ends any block that is still open: no display
            # equation spans two slides.
            if stripped.startswith('##'):
                in_math = False
                math_delim = None
                continue

            # Check for $$ delimiter (toggle)
            if '$$' in stripped and math_delim != 'env':
                if not in_math:
                    in_math = True
                    math_start = i
                    math_delim = '$$'
                    # Handle single-line $$ ... $$ (both delimiters on same line)
                    if stripped.count('$$') >= 2:
                        inner = stripped.split('$$')[1]
                        if len(inner.strip()) > 120:
                            overflows.append(i)
                        in_math = False
                        math_delim = None
                    continue
                else:
                    in_math = False
                    math_delim = None
                    continue

            # Check for \begin{equation/align/gather/...}
            env_begin = re.match(
                r'\\begin\{(equation|align|gather|multline|eqnarray)\*?\}', stripped
            )
            if env_begin and not in_math:
                in_math = True
                math_start = i
                math_delim = 'env'
                continue

            # Check for \end{equation/align/gather/...}
            if re.match(r'\\end\{(equation|align|gather|multline|eqnarray)\*?\}', stripped):
                in_math = False
                math_delim = None
                continue

            # Inside a math block: check individual line length
            if in_math:
                # Strip LaTeX comments before measuring
                code_part = line.split('%')[0] if '%' in line else line
                if len(code_part.strip()) > 120:
                    overflows.append(i)

        return overflows

    @staticmethod
    def check_broken_citations(content: str, bib_file: Path) -> List[str]:
        """Check for LaTeX citation keys not in bibliography.

        Matches \\cite{}, \\citep{}, \\citet{}, \\citeauthor{}, \\citeyear{}, etc.
        """
        cite_pattern = r'\\cite[a-z]*\{([^}]+)\}'
        content = IssueDetector.citation_source(content, drop_attrs=False)
        cited_keys = set()
        for match in re.finditer(cite_pattern, content):
            keys = match.group(1).split(',')
            cited_keys.update(k.strip() for k in keys)

        if not bib_file.exists():
            return list(cited_keys)

        bib_content = bib_file.read_text(encoding='utf-8')
        bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_content))

        broken = cited_keys - bib_keys
        return list(broken)

    # Acronyms a first-year undergraduate meets outside this course anyway.
    # Everything else has to be spelled out once. Keep this list short -- the
    # whole point of the check is that "obvious to me" is not the standard.
    COMMON_ACRONYMS = {
        'AI', 'PC', 'USB', 'GPS', 'CPU', 'GPU', 'PDF', 'URL', 'HTML', 'API',
        '2D', '3D', 'ID', 'TV', 'OK', 'CEO', 'IT', 'DNA', 'LED', 'US', 'UK',
        'KAIST', 'DGIST', 'MIT', 'Q', 'A', 'QA',
        # Editorial placeholders. All-caps and the right length, so the
        # acronym matcher happily flagged the TODO in its own scaffold.
        'TODO', 'FIXME', 'XXX', 'NOTE', 'WIP', 'TBD', 'TBA',
    }
    # A candidate is an all-caps token of 2-8 characters that stands on its
    # own: not glued to a hyphen or another word character on either side.
    # That is what keeps "RT-2", "QT-Opt", "DALL-E" and "LAION-5B" whole --
    # the old \b...\b version split them at the hyphen and flagged "RT",
    # "QT", "DALL" and "LAION" as acronyms nobody had expanded. Tokens with
    # fewer than two letters ("A100", "3D") are not acronyms either; that
    # filter is applied in check_acronym_expansion.
    ACRONYM_RE = re.compile(r'(?<![\w-])([A-Z][A-Z0-9]{1,7})(?![\w-])')

    @staticmethod
    def check_acronym_expansion(content: str) -> List[Dict]:
        """Every acronym expanded the first time it appears on a slide.

        Lecture profile only. An audience with no background cannot recover
        from a term it never saw defined, and the author is the last person
        able to notice which ones those are -- by the time you write the deck
        every acronym in it feels obvious.

        An acronym counts as expanded if the words appear next to it in
        either order: "Vision-Language-Action (VLA)" or "VLA (Vision-Language
        -Action)". Only the FIRST appearance is checked; after that it is
        shorthand, which is the point.
        """
        violations = []
        seen = set()
        for title, start, vis in IssueDetector.iter_slides(content):
            for line_no, text in vis:
                stripped = IssueDetector.strip_inline(text)
                for acr in IssueDetector.ACRONYM_RE.findall(stripped):
                    if acr in IssueDetector.COMMON_ACRONYMS or acr in seen:
                        continue
                    if sum(c.isalpha() for c in acr) < 2:
                        continue
                    seen.add(acr)
                    expanded = (
                        re.search(r'[A-Za-z][\w-]*[\s-][^()]*\(\s*%s\s*\)' % acr,
                                  stripped)
                        or re.search(r'\b%s\s*\([^)]*[A-Za-z]{3}[^)]*\)' % acr,
                                     stripped)
                    )
                    if not expanded:
                        violations.append({
                            'type': 'unexpanded_acronym', 'slide': title,
                            'line': line_no,
                            'detail': f'"{acr}" appears first here without an '
                                      f'expansion - write it out once, e.g. '
                                      f'"... ({acr})"',
                        })
        return violations

    RECALL_RE = re.compile(
        r'\.recap\b'
        r'|last (session|week|time|lecture)'
        r'|previous(ly| session| week| lecture)'
        r'|where we (left off|stopped|ended)'
        r'|recap|so far',
        re.I)

    @staticmethod
    def check_prior_session_callback(content: str) -> List[Dict]:
        """A lecture opens by reconnecting to the session before it.

        Lecture profile only, and only from the second session onward -- a
        deck that declares itself first in the series is exempt via
        `series_index: 1` in its config.

        Students who missed a week need a way back in and the ones who did
        not need the thread picked up. One slide near the top is enough; this
        looks at the first three.
        """
        slides = list(IssueDetector.iter_slides(content))
        if not slides:
            return []
        head = slides[:3]
        for title, start, vis in head:
            blob = title + ' ' + ' '.join(t for _, t in vis)
            if IssueDetector.RECALL_RE.search(blob):
                return []
        return [{
            'type': 'missing_prior_session_callback',
            'slide': head[0][0], 'line': head[0][1],
            'detail': 'no callback to the previous session in the first three '
                      'slides - name where the last one ended, or set '
                      'series_index: 1 in the deck config if this is the first',
        }]

    @staticmethod
    def get_deck_theme(content: str) -> str:
        """Classify a QMD deck by its theme setting.

        Returns 'main' for decks on clean-academic.scss (the minimalist
        design principles apply) and 'legacy' for decks pinned to
        clean-academic-legacy.scss or a deck-specific theme (SUNY).

        This has to be exactly right or the gate fails *open* and every design
        check is skipped in silence. YAML spells the same value at least four
        legal ways, and Quarto's own render log round-trips the inline form
        into the block form, so hand-matching spellings kept missing one:

            theme: [default, clean-academic.scss]
            theme: clean-academic.scss
            theme:
              - default
              - clean-academic.scss
            theme:
            - default                 # sequence at the key's own indent
            - clean-academic.scss

        So parse the frontmatter as YAML when PyYAML is importable, and keep
        the hand scanner only as a fallback for environments without it.
        """
        m = re.match(r'^---\s*\n(.*?)\n---\s*(?:\n|$)', content, re.DOTALL)
        front = m.group(1) if m else ''

        try:
            import yaml
            data = yaml.safe_load(front) if front.strip() else None
        except Exception:
            data = None

        themes = ''
        if isinstance(data, dict):
            def find_theme(node):
                """Deepest-last search, but never mistake a nested `theme:`
                belonging to another key (mermaid, revealjs-plugins, ...) for
                the deck's own -- that misdirection reads as 'legacy' and
                silently disables every design check."""
                if isinstance(node, dict):
                    if 'theme' in node:
                        return node['theme']
                    for k, v in node.items():
                        if k == 'mermaid':      # has its own unrelated theme
                            continue
                        hit = find_theme(v)
                        if hit is not None:
                            return hit
                elif isinstance(node, list):
                    for item in node:
                        hit = find_theme(item)
                        if hit is not None:
                            return hit
                return None

            # The deck's theme lives at format.revealjs.theme; look there first
            # and only fall back to a search if the file is shaped differently.
            found = None
            fmt = data.get('format')
            if isinstance(fmt, dict):
                rj = fmt.get('revealjs')
                if isinstance(rj, dict) and 'theme' in rj:
                    found = rj['theme']
            if found is None:
                found = find_theme(data)
            if isinstance(found, str):
                themes = found
            elif isinstance(found, (list, tuple)):
                themes = ' '.join(str(x) for x in found)
            elif found is not None:
                themes = str(found)
        else:
            # Fallback: no PyYAML, or frontmatter that will not parse.
            m2 = re.search(r'^([ \t]*)theme:[ \t]*(.*)$', front or content,
                           re.MULTILINE)
            if m2:
                indent, inline = m2.group(1), m2.group(2).strip()
                themes = inline
                if not inline or inline.startswith('#'):
                    rest = (front or content)[m2.end():].split('\n')[1:]
                    block = []
                    for line in rest:
                        if not line.strip():
                            continue
                        lead = len(line) - len(line.lstrip())
                        # A sequence item may sit at the key's own indent.
                        if lead < len(indent) or (
                                lead == len(indent)
                                and not line.strip().startswith('-')):
                            break
                        block.append(line.strip().lstrip('-').strip())
                    themes = ' '.join(block)

        if 'clean-academic-legacy' in themes:
            return 'legacy'
        if 'clean-academic.scss' in themes:
            return 'main'
        return 'legacy'  # custom per-deck themes are graded without design checks

    @staticmethod
    def iter_slides(content: str):
        """Yield (title, start_line, visible_lines) per level-2 slide.

        visible_lines excludes YAML frontmatter, fenced code blocks, and
        speaker-notes divs (they are not on-screen content). Each element
        is (line_number, text).
        """
        lines = content.split('\n')
        slides = []
        title, start, buf = None, None, []
        in_yaml = False
        in_fence = False
        notes_depth = 0   # >0 while inside a ::: {.notes} div
        div_stack = []    # True for each open div that is a notes div

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if i == 1 and stripped == '---':
                in_yaml = True
                continue
            if in_yaml:
                if stripped == '---':
                    in_yaml = False
                continue
            if stripped.startswith('```'):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if stripped.startswith(':::'):
                bare = stripped.rstrip(':').strip()
                if bare:  # opener like ::: {.notes} or :::: {.columns}
                    is_notes = '.notes' in stripped
                    div_stack.append(is_notes)
                    if is_notes:
                        notes_depth += 1
                elif div_stack:  # bare ::: closer
                    if div_stack.pop():
                        notes_depth -= 1
                # keep non-notes openers visible so box classes are counted
                if notes_depth == 0 and start is not None and bare:
                    buf.append((i, line))
                continue
            if notes_depth > 0:
                continue
            m = re.match(r'^##\s+(.*)$|^##\s*$', line)
            if m is not None and not line.startswith('###'):
                if start is not None:
                    slides.append((title, start, buf))
                title = (m.group(1) or '(untitled)').strip() or '(untitled)'
                # include the heading line itself: slide-level classes like
                # {.smaller} live on it
                start, buf = i, [(i, line)]
                continue
            if start is not None:
                buf.append((i, line))

        if start is not None:
            slides.append((title, start, buf))
        return slides

    # Colored boxes the density rule counts (≤1 per slide)
    BOX_CLASSES = ('keybox', 'methodbox', 'highlightbox', 'resultbox',
                   'assumptionbox', 'quotebox')

    # Where a bullet wraps on the main theme. Measured in-browser at 1280x720
    # with the 40px root font, lengthening one bullet a character at a time:
    #   <=70 chars -> 1 line | 71-137 -> 2 lines | >=138 -> 3 lines
    # Source length is not rendered length, so strip_inline() below removes the
    # markup that costs characters but no pixels before comparing.
    ONE_LINE_CHARS = 70
    TWO_LINE_CHARS = 137

    @staticmethod
    def strip_inline(text: str) -> str:
        """Approximate what a bullet actually renders to, for width estimates."""
        t = text
        t = re.sub(r'^\s*(?:[-*+]|\d+[.)])\s+', '', t)     # list marker
        t = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', t)   # links / images
        t = re.sub(r'\[([^\]]*)\]\{[^}]*\}', r'\1', t)     # [text]{.class}
        t = re.sub(r'<[^>]+>', '', t)                      # inline html
        t = re.sub(r'\[-?@[\w:.#$%&\-+?<>~/]+\]', '', t)   # [@citekey]
        t = re.sub(r'[*_`]', '', t)                        # bold/italic/code
        return t.strip()

    @staticmethod
    def bullet_texts(vis) -> List[str]:
        """Top-level bullets, with lazy continuation lines folded in."""
        bullets, cur = [], None
        for _, t in vis:
            if re.match(r'^[-*+] |^\d+[.)] ', t):
                if cur is not None:
                    bullets.append(cur)
                cur = t
            elif cur is not None:
                # a blank line, a new block, or a nested item ends the bullet
                if not t.strip() or re.match(r'^\s*(?:[-*+]|\d+[.)])\s|^[#:<|]', t):
                    bullets.append(cur)
                    cur = None
                else:
                    cur += ' ' + t.strip()
        if cur is not None:
            bullets.append(cur)
        return bullets

    @staticmethod
    def check_design_density(content: str, profile=None) -> List[Dict]:
        """Density-budget violations per slide (main-theme decks only).

        Enforces .claude/rules/slide-design-principles.md:
          - bullets ≤5, or ≤3 when a figure shares the slide
          - a two-line bullet costs one slot (cap drops by 1) and only one
            such bullet is allowed per slide
          - no bullet may run to three lines
          - colored boxes ≤1, list nesting ≤1 sub-level

        The two-line rules exist because the written budget did not fit the
        frame: five bullets of two lines each overflow the 720px canvas by
        38px and get clipped, while the gate happily scored them 100/100.

        Slides containing a panel-tabset are skipped for bullet counts —
        tabs display one panel at a time.
        """
        violations = []
        for title, start, vis in IssueDetector.iter_slides(content):
            text = '\n'.join(t for _, t in vis)
            bullets = IssueDetector.bullet_texts(vis)
            top_bullets = len(bullets)
            deep_nested = sum(
                1 for _, t in vis if re.match(r'^\s{4,}[-*+] |^\s{4,}\d+[.)] ', t)
            )
            has_figure = bool(
                re.search(r'!\[|<img|<video|\{\{<\s*video', text))
            has_tabset = '.panel-tabset' in text
            boxes = sum(
                len(re.findall(r'\{[^}]*\.%s\b' % cls, text))
                for cls in IssueDetector.BOX_CLASSES
            )

            lengths = [len(IssueDetector.strip_inline(b)) for b in bullets]
            two_line = [n for n in lengths
                        if IssueDetector.ONE_LINE_CHARS < n <= IssueDetector.TWO_LINE_CHARS]
            over_two = [n for n in lengths if n > IssueDetector.TWO_LINE_CHARS]

            base = (profile.bullets_max_with_figure if has_figure
                    else profile.bullets_max) if profile else (3 if has_figure else 5)
            limit = base - 1 if two_line else base

            if not has_tabset and top_bullets > limit:
                why = (f'limit {limit} = {base} - 1 because a two-line bullet is present'
                       if two_line else
                       f'limit {base}{" with figure" if has_figure else ""}')
                violations.append({
                    'type': 'bullet_density', 'slide': title, 'line': start,
                    'detail': f'{top_bullets} bullets ({why}) — split the slide',
                })
            two_line_limit = profile.bullets_max_two_line if profile else 1
            if not has_tabset and len(two_line) > two_line_limit:
                violations.append({
                    'type': 'bullet_density', 'slide': title, 'line': start,
                    'detail': f'{len(two_line)} bullets wrap to two lines (limit {two_line_limit}) '
                              f'— tighten them to one line or split the slide',
                })
            if not has_tabset and over_two:
                violations.append({
                    'type': 'bullet_density', 'slide': title, 'line': start,
                    'detail': f'{len(over_two)} bullet(s) run past two lines '
                              f'({max(over_two)} chars; two lines end at '
                              f'{IssueDetector.TWO_LINE_CHARS}) — split the slide',
                })
            box_limit = profile.box_density if profile else 1
            if boxes > box_limit:
                violations.append({
                    'type': 'box_density', 'slide': title, 'line': start,
                    'detail': f'{boxes} colored boxes (limit {box_limit})',
                })
            if deep_nested:
                violations.append({
                    'type': 'deep_nesting', 'slide': title, 'line': start,
                    'detail': f'{deep_nested} bullets nested deeper than 1 sub-level',
                })
        return violations

    @staticmethod
    def check_font_shrink(content: str) -> List[Dict]:
        """Slides using .smaller/.smallest or sub-1em font-size overrides.

        Forbidden in main-theme decks: if content does not fit at full
        size, the slide must be split.
        """
        hits = []
        for title, start, vis in IssueDetector.iter_slides(content):
            text = '\n'.join(t for _, t in vis)
            count = len(re.findall(r'\.small(?:er|est)\b', text))
            count += len(re.findall(
                r'font-size:\s*0?\.\d+em|font-size:\s*[0-6]\d?%', text))
            if count:
                hits.append({
                    'type': 'font_shrink_to_fit', 'slide': title, 'line': start,
                    'detail': f'{count} font-shrink usage(s) — split the slide instead',
                })
        return hits

    # ------------------------------------------------------------------
    # WP2 gates: visible-text helpers, dash lint, attribution, forbidden
    # terms, level-1 heading. All of them read "visible text" the same way
    # (see the module docstring) and none of them touch iter_slides, so the
    # checks that predate them keep scoring exactly what they scored.
    # ------------------------------------------------------------------

    @staticmethod
    def _blank(m) -> str:
        return re.sub(r'[^\n]', ' ', m.group(0))

    @staticmethod
    def blank_html_comments(content: str) -> str:
        """Replace every <!-- ... --> with spaces, newlines kept, so line
        numbers survive and nothing inside a comment is visible text."""
        return re.sub(r'<!--.*?-->', IssueDetector._blank, content,
                      flags=re.DOTALL)

    @staticmethod
    def blank_invisible_html(content: str) -> str:
        """HTML comments plus <style>...</style> and <script>...</script>
        bodies, blanked the same way. Raw blocks carry CSS with custom
        properties (`var(--accent)`) and scripts with `--` operators, none
        of which a viewer reads; without this the dash lint would bill a
        chart for its stylesheet."""
        out = IssueDetector.blank_html_comments(content)
        out = re.sub(r'<style\b[^>]*>.*?</style\s*>', IssueDetector._blank,
                     out, flags=re.DOTALL | re.I)
        out = re.sub(r'<script\b[^>]*>.*?</script\s*>', IssueDetector._blank,
                     out, flags=re.DOTALL | re.I)
        return out

    RAW_FENCE_RE = re.compile(r'^`{3,}\s*\{=')   # ```{=html}, ```{=latex}

    @staticmethod
    def iter_visible_lines(content: str):
        """Yield (line_no, line, slide_title, raw) for every on-screen
        source line.

        Same state machine as iter_slides (front matter, fences, notes)
        plus HTML comments, <style> and <script> bodies blanked, and three
        differences that the new checks need: lines before the first `##`
        are yielded too (slide_title is None there), `:::` closers are
        yielded so a caller can find the extent of a div, and the body of a
        raw block (```{=html}) is yielded with raw=True -- it is on screen,
        unlike a code block, so the text checks must read it. Headings and
        divs are not parsed inside a raw block; `##` there is literal text.
        """
        lines = IssueDetector.blank_invisible_html(content).split('\n')
        in_yaml = False
        in_fence = False
        in_raw = False
        notes_depth = 0
        div_stack = []
        title = None
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if i == 1 and stripped == '---':
                in_yaml = True
                continue
            if in_yaml:
                if stripped == '---':
                    in_yaml = False
                continue
            if stripped.startswith('```'):
                if in_fence:
                    in_fence = False
                    in_raw = False
                else:
                    in_fence = True
                    in_raw = bool(IssueDetector.RAW_FENCE_RE.match(stripped))
                continue
            if in_fence:
                if in_raw and notes_depth == 0:
                    yield i, line, title, True
                continue
            if stripped.startswith(':::'):
                bare = stripped.rstrip(':').strip()
                if bare:
                    is_notes = '.notes' in stripped or bare == 'notes'
                    div_stack.append(is_notes)
                    if is_notes:
                        notes_depth += 1
                        continue
                elif div_stack:
                    if div_stack.pop():
                        notes_depth -= 1
                        continue
                if notes_depth == 0:
                    yield i, line, title, False
                continue
            if notes_depth > 0:
                continue
            m = re.match(r'^##\s+(.*)$|^##\s*$', line)
            if m is not None and not line.startswith('###'):
                title = (m.group(1) or '(untitled)').strip() or '(untitled)'
            yield i, line, title, False

    @staticmethod
    def visible_slides(content: str):
        """[(title, start_line, [(line_no, line), ...])] from
        iter_visible_lines, one entry per `##` slide (lines before the first
        slide are dropped, as iter_slides drops them). Raw-block lines are
        included in the slide they sit in."""
        out = []
        cur = None
        for ln, line, title, raw in IssueDetector.iter_visible_lines(content):
            if not raw and re.match(r'^##(?!#)', line):
                cur = (title, ln, [])
                out.append(cur)
            if cur is not None:
                cur[2].append((ln, line))
        return out

    @staticmethod
    def rendered_text(text: str) -> str:
        """What a source line contributes to the screen: drop inline code,
        inline math, link and image targets, HTML tags and attribute blocks
        (none of which Quarto's smart punctuation touches, and none of which
        a viewer reads), keep the words."""
        t = re.sub(r'`[^`]*`', ' ', text)
        t = re.sub(r'\$\$.*?\$\$', ' ', t)
        t = re.sub(r'(?<!\\)\$[^$\n]+?\$', ' ', t)
        t = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', t)
        t = re.sub(r'<[^>]+>', ' ', t)
        t = re.sub(r'\{[^}]*\}', ' ', t)
        return t

    TABLE_RULE_RE = re.compile(r'^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$')
    # `--`/`---`, the literal characters, and the HTML entities a raw block
    # would use to write the same thing (they render identically).
    DASH_RE = re.compile('-{2,}|[\u2014\u2013]|&(?:mdash|ndash|#8212|#8211|#x2014|#x2013);',
                         re.I)

    @staticmethod
    def check_dash_expressions(content: str) -> List[Dict]:
        """`---`, `--`, and literal em/en dashes in visible text.

        Quarto's smart punctuation renders `---` as an em dash and `--` as an
        en dash. The presenter writes a plain hyphen instead, everywhere.
        Lines that are only a rule (`---` slide break, `-----`, a table
        delimiter row) are syntax, not text, and are skipped; so is math,
        where `--` is two minus signs. Raw ```{=html} blocks are read too
        (tags stripped, <style>/<script> bodies blanked): the characters in
        them reach the screen exactly as written, entities included.

        One entry per slide (title, count, first snippet); the caller
        deducts 2 per hit with a cap of 10.
        """
        hits = []
        for title, start, vis in IssueDetector.visible_slides(content):
            count = 0
            snippet = None
            first_line = None
            in_math = False
            for ln, line in vis:
                stripped = line.strip()
                if stripped.startswith('$$') and stripped.count('$$') == 1:
                    in_math = not in_math
                    continue
                if in_math:
                    continue
                if re.match(r'^\s*-{3,}\s*$', line):
                    continue
                if IssueDetector.TABLE_RULE_RE.match(line):
                    continue
                text = IssueDetector.rendered_text(line)
                for m in IssueDetector.DASH_RE.finditer(text):
                    count += 1
                    if snippet is None:
                        lo = max(0, m.start() - 25)
                        hi = min(len(text), m.end() + 25)
                        snippet = text[lo:hi].strip()
                        first_line = ln
            if count:
                hits.append({
                    'type': 'dash_expression', 'slide': title,
                    'line': first_line or start, 'count': count,
                    'detail': f'{count} dash expression(s) (---, -- or a '
                              f'literal em/en dash) - write a plain hyphen; '
                              f'first at line {first_line}: "{snippet}"',
                })
        return hits

    @staticmethod
    def load_figures_manifest(path: Path) -> List[Dict]:
        """figures.yml -> the entries under `figures:`. Each is a mapping
        with file, source, licence, third_party; anything else is an error
        (a manifest that cannot be read must not pass as 'no manifest')."""
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import minyaml  # noqa: E402
        data = minyaml.load_path(path)
        figures = data.get('figures') if isinstance(data, dict) else None
        if figures is None:
            return []
        if not isinstance(figures, list):
            raise ValueError(f'{path}: `figures:` must be a list')
        out = []
        for entry in figures:
            if not isinstance(entry, dict) or not entry.get('file'):
                raise ValueError(
                    f'{path}: each figures entry needs at least `file:`')
            out.append(entry)
        return out

    # Every way a slide can put a file on screen: markdown image, HTML
    # src/poster, the slide-types `video=`/`poster=` header attributes, a
    # reveal background (Quarto source writes `background-image=` on the
    # header; the renderer adds the `data-` prefix, so both spellings are
    # accepted), and the `{{< video path >}}` shortcode.
    ASSET_REF_RE = re.compile(
        r'!\[[^\]]*\]\(\s*<?([^)\s>]+)'                      # ![alt](path)
        r'|(?:src|poster|video|(?:data-)?background-image'
        r'|(?:data-)?background-video)'
        r'\s*=\s*["\']?([^"\'\s>}]+)'                         # attr="path"
        r'|\{\{<\s*video\s+["\']?([^"\'\s>]+)',              # {{< video path >}}
        re.I)

    @staticmethod
    def slide_asset_basenames(vis) -> List[str]:
        names = []
        for _, line in vis:
            for m in IssueDetector.ASSET_REF_RE.finditer(line):
                ref = m.group(1) or m.group(2) or m.group(3)
                if ref:
                    names.append(Path(ref.split('?')[0].split('#')[0]).name)
        return names

    @staticmethod
    def slide_caption_text(vis) -> str:
        """Text of every .footnote / .video-caption div, figure caption
        (image alt text, <figcaption>) and [..]{.footnote} span on the
        slide. This is where a source has to be named."""
        parts = []
        depth = 0          # >0 while inside a caption div
        stack = []         # True for each open div that is a caption div
        for _, line in vis:
            stripped = line.strip()
            if stripped.startswith(':::'):
                bare = stripped.rstrip(':').strip()
                if bare:
                    is_cap = bool(re.search(
                        r'\.(footnote|video-caption|caption)\b'
                        r'|^(footnote|video-caption|caption)$', bare))
                    stack.append(is_cap)
                    if is_cap:
                        depth += 1
                elif stack:
                    if stack.pop():
                        depth -= 1
                continue
            if depth > 0:
                parts.append(line)
            parts += re.findall(r'!\[([^\]]+)\]\(', line)
            parts += re.findall(r'<figcaption[^>]*>(.*?)</figcaption>', line, re.I)
            parts += re.findall(r'\[([^\]]*)\]\{[^}]*\.(?:footnote|caption)\b', line)
        return ' '.join(parts)

    @staticmethod
    def check_attribution(content: str, manifest: Path) -> List[Dict]:
        """Every slide that shows a third-party figure names its source.

        `manifest` is the deck's figures.yml. For each entry with
        third_party: true, any slide referencing that file (by basename, via
        ![](..), <img src> -- inside a raw block too --, a video poster, a
        `background-image=` header attribute, a `{{< video >}}` shortcode or
        a data-background) must carry
        the entry's `source` string, case-insensitively, inside a .footnote
        div, a .video-caption div or a figure caption. 5 per missing, cap
        20 (applied by the caller).
        """
        entries = IssueDetector.load_figures_manifest(manifest)
        third = {}
        for e in entries:
            if e.get('third_party'):
                third[Path(str(e['file'])).name] = e
        if not third:
            return []
        hits = []
        for title, start, vis in IssueDetector.visible_slides(content):
            names = IssueDetector.slide_asset_basenames(vis)
            caption = IssueDetector.slide_caption_text(vis).lower()
            seen = set()
            for name in names:
                if name not in third or name in seen:
                    continue
                seen.add(name)
                source = str(third[name].get('source') or '').strip()
                licence = str(third[name].get('licence') or '').strip()
                if source and source.lower() in caption:
                    continue
                want = source or '<source missing in figures.yml>'
                hits.append({
                    'type': 'missing_attribution', 'slide': title,
                    'line': start, 'file': name,
                    'detail': f'{name} is third-party (source: {want}'
                              f'{", licence: " + licence if licence else ""}) '
                              f'but this slide has no .footnote or caption '
                              f'naming "{want}"',
                })
        return hits

    @staticmethod
    def load_forbidden_terms(path: Path) -> List[str]:
        """<deck>.forbidden.txt: one term per line, # comments, blanks
        ignored. Returned in file order, duplicates dropped."""
        terms = []
        for raw in path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if line not in terms:
                terms.append(line)
        return terms

    @staticmethod
    def front_matter_titles(content: str) -> List[Tuple[int, str]]:
        """(line_no, value) of title: and subtitle: in the front matter.
        They are rendered on the title slide, so a forbidden term there is
        as public as one on a body slide."""
        m = re.match(r'^---\s*\n(.*?)\n---\s*(?:\n|$)', content, re.DOTALL)
        if not m:
            return []
        out = []
        for i, line in enumerate(m.group(1).split('\n'), 2):
            mm = re.match(r'^(title|subtitle):\s*(.+)$', line)
            if mm:
                out.append((i, mm.group(2).strip().strip('"\'')))
        return out

    @staticmethod
    def check_forbidden_terms(content: str, forbidden: Path) -> List[Dict]:
        """Any forbidden term in visible text is a BLOCKER.

        Case-insensitive substring match, on visible text only -- never on
        speaker notes, which is where the internal context is supposed to
        live. Raw ```{=html} blocks count as visible (this is a leak gate;
        a term inside hand-written HTML is on the public page all the same).
        Reports every line:term pair.
        """
        terms = IssueDetector.load_forbidden_terms(forbidden)
        if not terms:
            return []
        hits = []
        candidates = [(ln, IssueDetector.rendered_text(line), title)
                      for ln, line, title, _raw
                      in IssueDetector.iter_visible_lines(content)]
        candidates += [(ln, text, '(title slide)')
                       for ln, text in IssueDetector.front_matter_titles(content)]
        for ln, text, title in candidates:
            low = text.lower()
            for term in terms:
                if term.lower() in low:
                    hits.append({
                        'type': 'forbidden_term', 'slide': title,
                        'line': ln, 'term': term,
                        'detail': f'forbidden term "{term}" (from '
                                  f'{forbidden.name}) in visible text: '
                                  f'"{text.strip()[:80]}"',
                    })
        return hits

    @staticmethod
    def check_level1_headings(content: str) -> List[Dict]:
        """A `# ` line after the front matter (outside fences, notes and
        comments) is a BLOCKER: Quarto renders it as a vertical stack and
        every slide that follows nests under it, so the deck's navigation
        and slide count silently change. Section dividers are written as
        `## {.divider}`. Raw ```{=html} lines are skipped: a "# " there is
        literal text and builds no stack."""
        hits = []
        for ln, line, title, raw in IssueDetector.iter_visible_lines(content):
            if raw:
                continue
            if re.match(r'^#(?!#)(\s|$)', line):
                hits.append({
                    'type': 'level1_heading', 'slide': title, 'line': ln,
                    'heading': line.strip(),
                    'detail': f'level-1 heading "{line.strip()}" at line {ln}: '
                              f'Quarto turns it into a vertical stack and every '
                              f'following slide nests under it. Write section '
                              f'dividers as "## {{.divider}}" (see '
                              f'Quarto/_fixtures/design-test.qmd)',
                })
        return hits

    @staticmethod
    def check_plotly_widgets(html_file: Path, expected: int = None) -> Tuple[int, bool]:
        """Check if plotly charts rendered in HTML."""
        if not html_file.exists():
            return 0, False

        html_content = html_file.read_text(encoding='utf-8')
        actual_count = html_content.count('htmlwidget')

        if expected is None:
            return actual_count, True

        return actual_count, (actual_count >= expected)

    # Contexts an `@` sits in that are never a citation, blanked before the
    # citation scan (line count irrelevant here, only the keys are returned):
    # a shortcode call, an attribute block, and a code fence.
    #
    # `## {.video-full video="@hook"}` was read as a citation to `hook` and
    # billed -15 as a broken one, on every deck that used the WP4 media
    # pipeline as documented (measured 2026-08-22 on a scaffolded lecture
    # deck: 85/100, one phantom critical). Pandoc resolves no citation inside
    # a header attribute block, a `{{< >}}` call or a fence, so neither does
    # this. Speaker notes stay in: pandoc does resolve citations there, so a
    # broken key in a note is a real one.
    FENCE_BLOCK_RE = re.compile(r'^`{3,}.*?^`{3,}[^\n]*$',
                                re.DOTALL | re.MULTILINE)
    SHORTCODE_RE = re.compile(r'\{\{<.*?>\}\}', re.DOTALL)
    ATTR_BLOCK_RE = re.compile(r'(?<!\$)\{[^{}\n]*\}')

    @staticmethod
    def citation_source(content: str, drop_attrs: bool = True) -> str:
        """`content` with every context that cannot hold a citation removed.

        `drop_attrs` is off for the LaTeX scan, whose own `\cite{key}` is a
        brace block: blanking those would drop every key it looks for.
        """
        out = IssueDetector.blank_html_comments(content)
        out = IssueDetector.FENCE_BLOCK_RE.sub(' ', out)
        out = IssueDetector.SHORTCODE_RE.sub(' ', out)
        if drop_attrs:
            out = IssueDetector.ATTR_BLOCK_RE.sub(' ', out)
        return out

    @staticmethod
    def check_quarto_citations(content: str, bib_file: Path) -> List[str]:
        """Check Quarto-style citation keys against bibliography.

        Supports patterns: @key, [@key], [@key1; @key2]
        """
        content = IssueDetector.citation_source(content)
        cited_keys = set()

        # Pattern 1: [@key] or [@key1; @key2; ...]
        bracket_pattern = r'\[([^\]]*@[^\]]+)\]'
        for match in re.finditer(bracket_pattern, content):
            inner = match.group(1)
            # Extract individual @key references from within brackets
            for key_match in re.finditer(r'@([\w:.#$%&\-+?<>~/]+)', inner):
                cited_keys.add(key_match.group(1))

        # Pattern 2: standalone @key (not inside brackets, not email addresses)
        # Match @key that is preceded by start-of-line or whitespace or punctuation
        # but NOT preceded by characters that indicate an email address
        standalone_pattern = r'(?<![.\w])@([\w:.#$%&\-+?<>~/]+)'
        for match in re.finditer(standalone_pattern, content):
            key = match.group(1)
            # Skip if it looks like a Quarto directive or special syntax
            if key.startswith('{') or key in ('fig', 'tbl', 'sec', 'eq', 'lst'):
                continue
            cited_keys.add(key)

        if not cited_keys:
            return []

        if not bib_file.exists():
            return list(cited_keys)

        bib_content = bib_file.read_text(encoding='utf-8')
        bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_content))

        broken = cited_keys - bib_keys
        return list(broken)

# ==============================================================================
# QUALITY SCORER
# ==============================================================================

class QualityScorer:
    """Calculate quality scores for course materials."""

    def __init__(self, filepath: Path, verbose: bool = False):
        self.filepath = filepath
        self.verbose = verbose
        self.score = 100
        self.issues = {
            'critical': [],
            'major': [],
            'minor': []
        }
        self.blockers = []      # forced-0 findings; see BLOCKERS
        self.auto_fail = False

    def score_quarto(self) -> Dict:
        """Score Quarto lecture slides."""
        content = self.filepath.read_text(encoding='utf-8')

        # The deck's profile decides the density budget and which extra
        # checks apply. A deck with no config resolves to its genre's
        # default profile, and a file outside Quarto/<genre>/ gets None --
        # in which case every limit falls back to what it was before
        # profiles existed.
        profile = deckprofile.load_for_path(self.filepath)

        # Check compilation
        compiles, error = IssueDetector.check_quarto_compilation(self.filepath)
        if not compiles:
            self.auto_fail = True
            self.issues['critical'].append({
                'type': 'compilation_failure',
                'description': 'Quarto compilation failed',
                'details': error[:200],
                'points': 100
            })
            self.score = 0
            return self._generate_report()

        # Check equation overflow (heuristic)
        equation_overflows = IssueDetector.check_equation_overflow(content)
        for line in equation_overflows:
            self.issues['critical'].append({
                'type': 'equation_overflow',
                'description': f'Potential equation overflow at line {line}',
                'details': 'Single equation line >120 chars may overflow slide',
                'points': 20
            })
            self.score -= 20

        # Check broken citations (LaTeX-style \cite patterns)
        bib_file = BIB_FILE
        broken_citations = IssueDetector.check_broken_citations(content, bib_file)

        # Also check Quarto-style @key citations
        quarto_broken = IssueDetector.check_quarto_citations(content, bib_file)
        # Merge both sets, avoiding duplicates
        all_broken = set(broken_citations) | set(quarto_broken)
        for key in all_broken:
            self.issues['critical'].append({
                'type': 'broken_citation',
                'description': f'Citation key not in bibliography: {key}',
                'details': 'Add to Bibliography_base.bib or fix key',
                'points': 15
            })
            self.score -= 15

        # Design-principle checks — main-theme decks only. Legacy decks
        # (clean-academic-legacy.scss, per-deck themes) predate the
        # minimalist principles and are graded without them.
        if IssueDetector.get_deck_theme(content) == 'main':
            for v in IssueDetector.check_font_shrink(content):
                self.issues['major'].append({
                    'type': v['type'],
                    'description': f"Font shrink on slide \"{v['slide']}\" (line {v['line']})",
                    'details': v['detail'],
                    'points': 5
                })
                self.score -= 5
            for v in IssueDetector.check_design_density(content, profile):
                severity = 'minor' if v['type'] == 'deep_nesting' else 'major'
                points = 1 if v['type'] == 'deep_nesting' else 3
                self.issues[severity].append({
                    'type': v['type'],
                    'description': f"{v['type'].replace('_', ' ')} on slide \"{v['slide']}\" (line {v['line']})",
                    'details': v['detail'],
                    'points': points
                })
                self.score -= points

        # Profile-gated checks. These are off for a paper review by
        # design: an audience that already knows the notation does not need
        # every acronym spelled out, and a one-off talk has no previous
        # session to call back to.
        if profile and profile.expand_acronyms:
            for v in IssueDetector.check_acronym_expansion(content):
                self.issues['major'].append({
                    'type': v['type'],
                    'description': f"Unexpanded acronym on slide \"{v['slide']}\" (line {v['line']})",
                    'details': v['detail'],
                    'points': 2
                })
                self.score -= 2
        # A deck that does not say where it sits in the series is checked.
        # Guessing "first" would switch the check off for every lecture that
        # forgot to declare one, which is the population most likely to need it.
        if (profile and profile.prior_session_callback
                and profile.series_index != 1):
            # When the deck sits in a series, the series file knows which
            # session came before (a guest or DGIST slot counts; holiday and
            # exam weeks are skipped), so the message can name it. The check
            # itself is unchanged: the resolution only sharpens the wording.
            expected = ''
            prior = getattr(profile, 'prior_session', None)
            if prior:
                who = f" by {prior['presenter']}" if prior.get('presenter') else ''
                expected = (f"; the series says the previous session was "
                            f"{prior['week']} ({prior['short_date']}): "
                            f"\"{prior['title']}\"{who}")
            for v in IssueDetector.check_prior_session_callback(content):
                self.issues['major'].append({
                    'type': v['type'],
                    'description': f"No callback to the previous session (line {v['line']})",
                    'details': v['detail'] + expected,
                    'points': 3
                })
                self.score -= 3

        # WP2 gates. Each is switched by the profile (see the profile yml,
        # checks:), so a deck whose profile leaves one off is not touched by
        # it. The two blockers force the score to 0 below.
        if profile and profile.dash_lint:
            hits = IssueDetector.check_dash_expressions(content)
            cap = QUARTO_RUBRIC['major']['dash_expression']['cap']
            per = QUARTO_RUBRIC['major']['dash_expression']['points']
            spent = 0
            for v in hits:
                points = min(per * v['count'], max(cap - spent, 0))
                spent += points
                self.issues['major'].append({
                    'type': v['type'],
                    'description': f"Dash expression(s) on slide \"{v['slide']}\" (line {v['line']})",
                    'details': v['detail'] + ('' if points else ' (cap reached, no further deduction)'),
                    'points': points
                })
                self.score -= points
        if profile and profile.attribution and profile.figures_manifest:
            try:
                hits = IssueDetector.check_attribution(content, profile.figures_manifest)
            except Exception as e:   # unreadable manifest: say so, loudly
                hits = [{'type': 'missing_attribution', 'slide': '(manifest)',
                         'line': 0, 'detail': f'figures.yml could not be read: {e}'}]
            cap = QUARTO_RUBRIC['major']['missing_attribution']['cap']
            per = QUARTO_RUBRIC['major']['missing_attribution']['points']
            spent = 0
            for v in hits:
                points = min(per, max(cap - spent, 0))
                spent += points
                self.issues['major'].append({
                    'type': v['type'],
                    'description': f"Missing attribution on slide \"{v['slide']}\" (line {v['line']})",
                    'details': v['detail'] + ('' if points else ' (cap reached, no further deduction)'),
                    'points': points
                })
                self.score -= points
        if profile and profile.forbidden_terms and profile.forbidden_file:
            for v in IssueDetector.check_forbidden_terms(content, profile.forbidden_file):
                self.blockers.append({
                    'type': v['type'],
                    'description': f"{self.filepath}:{v['line']}: forbidden term \"{v['term']}\"",
                    'details': v['detail'],
                })
        if profile and profile.level1_heading != 'off':
            for v in IssueDetector.check_level1_headings(content):
                self.blockers.append({
                    'type': v['type'],
                    'description': f"{self.filepath}:{v['line']}: level-1 heading \"{v['heading']}\"",
                    'details': v['detail'],
                })

        # Check plotly widgets (if HTML exists)
        html_file = self.filepath.parent.parent / 'docs' / 'slides' / self.filepath.with_suffix('.html').name
        if html_file.exists():
            widget_count, _ = IssueDetector.check_plotly_widgets(html_file)
            expected_plotly = content.count('plotly::plot_ly')
            if expected_plotly > 0 and widget_count < expected_plotly:
                missing = expected_plotly - widget_count
                self.issues['critical'].append({
                    'type': 'missing_plotly_chart',
                    'description': f'{missing} plotly chart(s) failed to render',
                    'details': f'Expected {expected_plotly}, found {widget_count}',
                    'points': 10 * missing
                })
                self.score -= 10 * missing

        self.score = max(0, self.score)
        if self.blockers:
            self.score = 0
        return self._generate_report()

    def _generate_report(self) -> Dict:
        """Generate quality score report."""
        if self.auto_fail:
            status = 'FAIL'
            threshold = 'None (auto-fail)'
        elif self.blockers:
            status = 'BLOCKED'
            threshold = 'None (blocker: score forced to 0)'
        elif self.score >= THRESHOLDS['excellence']:
            status = 'EXCELLENCE'
            threshold = 'excellence'
        elif self.score >= THRESHOLDS['pr']:
            status = 'PR_READY'
            threshold = 'pr'
        elif self.score >= THRESHOLDS['commit']:
            status = 'COMMIT_READY'
            threshold = 'commit'
        else:
            status = 'BLOCKED'
            threshold = 'None (below commit)'

        critical_count = len(self.issues['critical'])
        major_count = len(self.issues['major'])
        minor_count = len(self.issues['minor'])
        total_count = critical_count + major_count + minor_count

        return {
            'filepath': str(self.filepath),
            'score': self.score,
            'status': status,
            'threshold': threshold,
            'auto_fail': self.auto_fail,
            'blocked': bool(self.blockers),
            'blockers': self.blockers,
            'issues': {
                'critical': self.issues['critical'],
                'major': self.issues['major'],
                'minor': self.issues['minor'],
                'counts': {
                    'critical': critical_count,
                    'major': major_count,
                    'minor': minor_count,
                    'blocker': len(self.blockers),
                    'total': total_count
                }
            },
            'thresholds': THRESHOLDS
        }

    def print_report(self, summary_only: bool = False) -> None:
        """Print formatted quality report."""
        report = self._generate_report()

        print(f"\n# Quality Score: {self.filepath.name}\n")

        status_emoji = {
            'EXCELLENCE': '[EXCELLENCE]',
            'PR_READY': '[PASS]',
            'COMMIT_READY': '[PASS]',
            'BLOCKED': '[BLOCKED]',
            'FAIL': '[FAIL]'
        }

        print(f"## Overall Score: {report['score']}/100 {status_emoji.get(report['status'], '')}")

        if report['blockers']:
            # Shown in every mode, summary included: a blocker is the one
            # finding a reader must not have to scroll for.
            print(f"\n## BLOCKERS (score forced to 0): {len(report['blockers'])}")
            for b in report['blockers']:
                print(f"BLOCKER [{b['type']}] {b['description']}")
                print(f"    {b['details']}")

        if report['status'] == 'BLOCKED' and report['blockers']:
            print(f"\n**Status:** BLOCKED - {len(report['blockers'])} blocker(s); "
                  f"fix them, the rest of the score is moot until then")
        elif report['status'] == 'BLOCKED':
            print(f"\n**Status:** BLOCKED - Cannot commit (score < {THRESHOLDS['commit']})")
        elif report['status'] == 'COMMIT_READY':
            print(f"\n**Status:** Ready for commit (score >= {THRESHOLDS['commit']})")
            gap_to_pr = THRESHOLDS['pr'] - report['score']
            print(f"**Next milestone:** PR threshold ({THRESHOLDS['pr']}+)")
            print(f"**Gap analysis:** Need +{gap_to_pr} points to reach PR quality")
        elif report['status'] == 'PR_READY':
            print(f"\n**Status:** Ready for PR (score >= {THRESHOLDS['pr']})")
            gap_to_excellence = THRESHOLDS['excellence'] - report['score']
            if gap_to_excellence > 0:
                print(f"**Next milestone:** Excellence ({THRESHOLDS['excellence']})")
                print(f"**Gap analysis:** +{gap_to_excellence} points to excellence")
        elif report['status'] == 'EXCELLENCE':
            print(f"\n**Status:** Excellence achieved! (score >= {THRESHOLDS['excellence']})")
        elif report['status'] == 'FAIL':
            print(f"\n**Status:** Auto-fail (compilation/syntax error)")

        if summary_only:
            print(f"\n**Total issues:** {report['issues']['counts']['total']} "
                  f"({report['issues']['counts']['critical']} critical, "
                  f"{report['issues']['counts']['major']} major, "
                  f"{report['issues']['counts']['minor']} minor"
                  + (f", {report['issues']['counts']['blocker']} BLOCKER"
                     if report['blockers'] else '') + ")")
            return

        # Detailed issues
        print(f"\n## Critical Issues (MUST FIX): {report['issues']['counts']['critical']}")
        if report['issues']['counts']['critical'] == 0:
            print("No critical issues" + ("\n" if report['blockers']
                                          else " - safe to commit\n"))
        else:
            for i, issue in enumerate(report['issues']['critical'], 1):
                print(f"{i}. **{issue['description']}** (-{issue['points']} points)")
                print(f"   - {issue['details']}\n")

        if report['issues']['counts']['major'] > 0:
            print(f"## Major Issues (SHOULD FIX): {report['issues']['counts']['major']}")
            for i, issue in enumerate(report['issues']['major'], 1):
                print(f"{i}. **{issue['description']}** (-{issue['points']} points)")
                print(f"   - {issue['details']}\n")

        if report['issues']['counts']['minor'] > 0 and self.verbose:
            print(f"## Minor Issues (NICE-TO-HAVE): {report['issues']['counts']['minor']}")
            for i, issue in enumerate(report['issues']['minor'], 1):
                print(f"{i}. {issue['description']} (-{issue['points']} points)\n")

        # Recommendations
        if report['blockers']:
            print("## Recommended Actions")
            print("1. Fix every BLOCKER above (the score stays 0 until they are gone)")
            print(f"2. Re-run quality score (target: >={THRESHOLDS['commit']})\n")
        elif report['status'] == 'BLOCKED':
            print("## Recommended Actions")
            print("1. Fix all critical issues above")
            print(f"2. Re-run quality score (target: >={THRESHOLDS['commit']})")
            print("3. Commit after reaching threshold\n")
        elif report['status'] == 'COMMIT_READY' and report['score'] < THRESHOLDS['pr']:
            print("## Recommended Actions to Reach PR Threshold")
            points_needed = THRESHOLDS['pr'] - report['score']
            print(f"Need +{points_needed} points to reach {THRESHOLDS['pr']}/100")
            if report['issues']['counts']['major'] > 0:
                print("Fix major issues listed above to improve score")
            print(f"\n**Estimated time:** 10-20 minutes\n")

# ==============================================================================
# CLI INTERFACE
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Calculate quality scores for course materials',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Score a single Quarto file
  python scripts/quality_score.py Quarto/papers/DreamZero.qmd

  # Score multiple files
  python scripts/quality_score.py Quarto/*/*.qmd

  # Summary only (no detailed issues)
  python scripts/quality_score.py Quarto/papers/DreamZero.qmd --summary

  # Verbose output (include minor issues)
  python scripts/quality_score.py Quarto/papers/DreamZero.qmd --verbose

Quality Thresholds:
  80/100 = Commit threshold (blocks if below)
  90/100 = PR threshold (warning if below)
  95/100 = Excellence (aspirational)

Exit Codes:
  0 = Score >= 80 (commit allowed)
  1 = Score < 80 (commit blocked), including any BLOCKER (forced 0)
  2 = Auto-fail (compilation error)
        """
    )

    parser.add_argument('filepaths', type=Path, nargs='+', help='Path(s) to file(s) to score')
    parser.add_argument('--summary', action='store_true', help='Show summary only')
    parser.add_argument('--verbose', action='store_true', help='Show all issues including minor')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    results = []
    exit_code = 0

    for filepath in args.filepaths:
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            exit_code = 1
            continue

        try:
            scorer = QualityScorer(filepath, verbose=args.verbose)

            if filepath.suffix == '.qmd':
                report = scorer.score_quarto()
            else:
                print(f"Error: Unsupported file type: {filepath.suffix}")
                continue

            results.append(report)

            if not args.json:
                scorer.print_report(summary_only=args.summary)

            if report['auto_fail']:
                exit_code = max(exit_code, 2)
            elif report['score'] < THRESHOLDS['commit']:
                exit_code = max(exit_code, 1)

        except Exception as e:
            print(f"Error scoring {filepath}: {e}")
            import traceback
            traceback.print_exc()
            exit_code = 1

    if args.json:
        print(json.dumps(results, indent=2))

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
