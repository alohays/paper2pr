#!/usr/bin/env python3
"""
Quality Scoring System for Academic Course Materials

Calculates objective quality scores (0-100) based on defined rubrics.
Enforces quality gates: 80 (commit), 90 (PR), 95 (excellence).

Usage:
    python scripts/quality_score.py Quarto/papers/DreamZero.qmd
    python scripts/quality_score.py Quarto/papers/DreamZero.qmd --summary
    python scripts/quality_score.py Quarto/*/*.qmd
    python scripts/quality_score.py Slides/DreamZero.tex
    python scripts/quality_score.py scripts/R/analysis.R
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
        'tikz_label_overlap': {'points': 5},
        'bullet_density': {'points': 3},       # >5 bullets, or >3 with a figure (new decks)
        'box_density': {'points': 3},          # >1 colored box per slide (new decks)
        'notation_inconsistency': {'points': 3},
        'unexpanded_acronym': {'points': 2},        # lecture profile only
        'missing_prior_session_callback': {'points': 3},  # lecture profile only
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

R_SCRIPT_RUBRIC = {
    'critical': {
        'syntax_error': {'points': 100, 'auto_fail': True},
        'hardcoded_path': {'points': 20},
        'missing_library': {'points': 10},
    },
    'major': {
        'missing_set_seed': {'points': 10},
        'missing_figure': {'points': 5},
        'missing_rds': {'points': 5},
    },
    'minor': {
        'style_violation': {'points': 1},
        'missing_roxygen': {'points': 1},
    }
}

BEAMER_RUBRIC = {
    'critical': {
        'compilation_failure': {'points': 100, 'auto_fail': True},
        'undefined_citation': {'points': 15},
        'overfull_hbox': {'points': 10},
    },
    'major': {
        'text_overflow': {'points': 5},
        'notation_inconsistency': {'points': 3},
    },
    'minor': {
        'font_size_reduction': {'points': 1},
    }
}

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
        lines = content.split('\n')
        in_math = False
        math_start = 0
        math_delim = None  # Track which delimiter opened the block

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

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
    ACRONYM_RE = re.compile(r'\b([A-Z][A-Z0-9]{1,7})\b')

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

    @staticmethod
    def check_r_syntax(filepath: Path) -> Tuple[bool, str]:
        """Check R script for syntax errors."""
        try:
            result = subprocess.run(
                ['Rscript', '-e', f'parse("{filepath}")'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return False, result.stderr
            return True, ""
        except subprocess.TimeoutExpired:
            return False, "Syntax check timeout"
        except FileNotFoundError:
            return False, "Rscript not installed"

    @staticmethod
    def check_hardcoded_paths(content: str) -> List[int]:
        """Detect absolute paths in R scripts."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if re.search(r'["\'][/\\]|["\'][A-Za-z]:[/\\]', line):
                if not re.search(r'http:|https:|file://|/tmp/', line):
                    issues.append(i)

        return issues

    @staticmethod
    def check_latex_syntax(content: str) -> List[Dict]:
        """Check for common LaTeX syntax issues without compiling.

        Looks for:
        - Unmatched braces
        - Unclosed environments
        - Common typos in commands
        """
        issues = []
        lines = content.split('\n')

        # Track open environments
        env_stack = []
        for i, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.split('%')[0] if '%' in line else line

            # Check for \begin{env}
            for match in re.finditer(r'\\begin\{(\w+)\}', stripped):
                env_stack.append((match.group(1), i))

            # Check for \end{env}
            for match in re.finditer(r'\\end\{(\w+)\}', stripped):
                env_name = match.group(1)
                if env_stack and env_stack[-1][0] == env_name:
                    env_stack.pop()
                elif env_stack:
                    issues.append({
                        'line': i,
                        'description': f'Mismatched environment: \\end{{{env_name}}} '
                                       f'but expected \\end{{{env_stack[-1][0]}}} '
                                       f'(opened at line {env_stack[-1][1]})',
                    })
                else:
                    issues.append({
                        'line': i,
                        'description': f'\\end{{{env_name}}} without matching \\begin',
                    })

        # Report unclosed environments
        for env_name, line_num in env_stack:
            issues.append({
                'line': line_num,
                'description': f'Unclosed environment: \\begin{{{env_name}}} never closed',
            })

        return issues

    @staticmethod
    def check_overfull_hbox_risk(content: str) -> List[int]:
        """Detect lines in LaTeX source likely to cause overfull hbox.

        Checks for very long lines inside text and math environments
        that are likely to overflow the slide width.
        """
        issues = []
        lines = content.split('\n')
        in_frame = False

        for i, line in enumerate(lines, 1):
            stripped = line.split('%')[0] if '%' in line else line

            # Track frame environments for context
            if r'\begin{frame}' in stripped:
                in_frame = True
            elif r'\end{frame}' in stripped:
                in_frame = False

            # Flag very long content lines inside frames
            # Strip leading whitespace and LaTeX commands for length check
            if in_frame and len(stripped.strip()) > 120:
                # Skip lines that are just comments or common long commands
                if stripped.strip().startswith('%'):
                    continue
                # Skip includegraphics, input, and similar path-based commands
                if re.match(r'\s*\\(includegraphics|input|bibliography|usepackage)', stripped):
                    continue
                issues.append(i)

        return issues

    @staticmethod
    def check_quarto_citations(content: str, bib_file: Path) -> List[str]:
        """Check Quarto-style citation keys against bibliography.

        Supports patterns: @key, [@key], [@key1; @key2]
        """
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
        if (profile and profile.prior_session_callback
                and int(profile.raw.get('series_index', 0)) != 1):
            for v in IssueDetector.check_prior_session_callback(content):
                self.issues['major'].append({
                    'type': v['type'],
                    'description': f"No callback to the previous session (line {v['line']})",
                    'details': v['detail'],
                    'points': 3
                })
                self.score -= 3

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
        return self._generate_report()

    def score_r_script(self) -> Dict:
        """Score R script quality."""
        content = self.filepath.read_text(encoding='utf-8')

        # Check syntax
        is_valid, error = IssueDetector.check_r_syntax(self.filepath)
        if not is_valid:
            self.auto_fail = True
            self.issues['critical'].append({
                'type': 'syntax_error',
                'description': 'R syntax error',
                'details': error[:200],
                'points': 100
            })
            self.score = 0
            return self._generate_report()

        # Check hardcoded paths
        path_issues = IssueDetector.check_hardcoded_paths(content)
        for line in path_issues:
            self.issues['critical'].append({
                'type': 'hardcoded_path',
                'description': f'Hardcoded absolute path at line {line}',
                'details': 'Use relative paths or here::here()',
                'points': 20
            })
            self.score -= 20

        # Check for set.seed() if randomness detected
        has_random = any(fn in content for fn in ['rnorm', 'runif', 'sample', 'rbinom', 'rnbinom'])
        has_seed = 'set.seed' in content
        if has_random and not has_seed:
            self.issues['major'].append({
                'type': 'missing_set_seed',
                'description': 'Missing set.seed() for reproducibility',
                'details': 'Add set.seed(YYYYMMDD) after library() calls',
                'points': 10
            })
            self.score -= 10

        self.score = max(0, self.score)
        return self._generate_report()

    def score_beamer(self) -> Dict:
        """Score Beamer/LaTeX lecture slides."""
        content = self.filepath.read_text(encoding='utf-8')

        # Check for LaTeX syntax issues (without compiling)
        syntax_issues = IssueDetector.check_latex_syntax(content)
        if syntax_issues:
            # Mismatched environments are treated as compilation risk
            for issue in syntax_issues:
                self.issues['critical'].append({
                    'type': 'compilation_failure',
                    'description': f'LaTeX syntax issue at line {issue["line"]}',
                    'details': issue['description'],
                    'points': 100
                })
            self.auto_fail = True
            self.score = 0
            return self._generate_report()

        # Check for undefined/broken citations (\cite, \citep, \citet patterns)
        bib_file = BIB_FILE
        if not bib_file.exists():
            # Also check same directory
            bib_file = self.filepath.parent / 'Bibliography_base.bib'
        broken_citations = IssueDetector.check_broken_citations(content, bib_file)
        for key in broken_citations:
            self.issues['critical'].append({
                'type': 'undefined_citation',
                'description': f'Citation key not in bibliography: {key}',
                'details': 'Add to Bibliography_base.bib or fix key',
                'points': 15
            })
            self.score -= 15

        # Check for lines likely to cause overfull hbox
        overfull_lines = IssueDetector.check_overfull_hbox_risk(content)
        for line in overfull_lines:
            self.issues['critical'].append({
                'type': 'overfull_hbox',
                'description': f'Potential overfull hbox at line {line}',
                'details': 'Line >120 chars inside frame may overflow slide width',
                'points': 10
            })
            self.score -= 10

        # Check equation overflow (same heuristic as Quarto)
        equation_overflows = IssueDetector.check_equation_overflow(content)
        for line_num in equation_overflows:
            self.issues['critical'].append({
                'type': 'overfull_hbox',
                'description': f'Potential equation overflow at line {line_num}',
                'details': 'Single equation line >120 chars likely to overflow',
                'points': 10
            })
            self.score -= 10

        self.score = max(0, self.score)
        return self._generate_report()

    def _generate_report(self) -> Dict:
        """Generate quality score report."""
        if self.auto_fail:
            status = 'FAIL'
            threshold = 'None (auto-fail)'
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
            'issues': {
                'critical': self.issues['critical'],
                'major': self.issues['major'],
                'minor': self.issues['minor'],
                'counts': {
                    'critical': critical_count,
                    'major': major_count,
                    'minor': minor_count,
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

        if report['status'] == 'BLOCKED':
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
                  f"{report['issues']['counts']['minor']} minor)")
            return

        # Detailed issues
        print(f"\n## Critical Issues (MUST FIX): {report['issues']['counts']['critical']}")
        if report['issues']['counts']['critical'] == 0:
            print("No critical issues - safe to commit\n")
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
        if report['status'] == 'BLOCKED':
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

  # Score a Beamer/LaTeX file
  python scripts/quality_score.py Slides/DreamZero.tex

  # Score an R script
  python scripts/quality_score.py scripts/R/analysis.R

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
  1 = Score < 80 (commit blocked)
  2 = Auto-fail (compilation/syntax error)
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
            elif filepath.suffix == '.R':
                report = scorer.score_r_script()
            elif filepath.suffix == '.tex':
                report = scorer.score_beamer()
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
