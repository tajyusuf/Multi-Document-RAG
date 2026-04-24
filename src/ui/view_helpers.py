from __future__ import annotations

import html
import re


def highlight_text(text: str, query: str) -> str:
    """Highlights query terms within a source snippet for quick inspection."""

    safe_text = html.escape(text)
    keywords = [term for term in re.findall(r"\w+", query) if len(term) > 3][:8]
    if not keywords:
        return safe_text

    pattern = re.compile(r"(" + "|".join(re.escape(term) for term in keywords) + r")", re.IGNORECASE)
    return pattern.sub(r"<mark style='background:#143a63;color:#f0f9ff;padding:0 2px;border-radius:4px;'>\1</mark>", safe_text)


def confidence_label(score: float) -> str:
    if score >= 0.8:
        return "High grounding confidence"
    if score >= 0.6:
        return "Moderate grounding confidence"
    if score >= 0.4:
        return "Partial evidence confidence"
    return "Low evidence confidence"
