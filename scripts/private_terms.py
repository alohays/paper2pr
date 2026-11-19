"""Optional local vocabulary that must never appear in audience artifacts or diagnostics."""
import os
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_terms(path):
    return tuple(dict.fromkeys(
        term for line in path.read_text(encoding="utf-8").splitlines()
        if (term := line.strip()) and not term.startswith("#")
    ))


def private_terms():
    configured = os.environ.get("PAPER2PR_PRIVATE_DENYLIST")
    if configured is None:
        return ()
    try:
        path = Path(configured).expanduser().resolve(strict=True)
        if path.is_relative_to(ROOT):
            raise ValueError("PAPER2PR_PRIVATE_DENYLIST must be outside the checkout")
        return read_terms(path)
    except (OSError, UnicodeError, RuntimeError):
        raise ValueError("Cannot read PAPER2PR_PRIVATE_DENYLIST as UTF-8") from None


def contains_private(text, terms):
    if not terms:
        return False
    normalized = unescape(text).casefold()
    return any(term.casefold() in normalized for term in terms)
