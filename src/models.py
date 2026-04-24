from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class IngestedSection:
    text: str
    file_name: str
    file_type: str
    page_number: int | None = None
    section_title: str | None = None
    order: int = 0


@dataclass(slots=True)
class SourceSnippet:
    file_name: str
    page_number: int | None
    section_title: str | None
    content: str
    relevance: float
    chunk_id: str


@dataclass(slots=True)
class AnswerPayload:
    answer: str
    confidence: float
    rewritten_query: str
    insights: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    sources: list[SourceSnippet] = field(default_factory=list)
    raw_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SummaryPayload:
    title: str
    bullets: list[str]
    source_count: int
