from __future__ import annotations

import json
from collections import defaultdict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_core.documents import Document

from src.models import SummaryPayload
from src.prompts import SUMMARY_PROMPT, TOPIC_EXTRACTION_PROMPT


class DocumentSummarizer:
    def __init__(self, llm: ChatGroq) -> None:
        self.llm = llm

    def summarize_by_document(self, documents: list[Document]) -> list[SummaryPayload]:
        grouped: dict[str, list[Document]] = defaultdict(list)
        for doc in documents:
            grouped[doc.metadata.get("file_name", "Unknown")].append(doc)

        summaries: list[SummaryPayload] = []
        for file_name, docs in grouped.items():
            excerpt = self._build_excerpt(docs[:6])
            response = self.llm.invoke(
                [
                    SystemMessage(content=SUMMARY_PROMPT),
                    HumanMessage(
                        content=f"Create a concise executive summary for {file_name}.\n\n{excerpt}"
                    ),
                ]
            )
            bullets = [line.strip("- ").strip() for line in response.content.splitlines() if line.strip()]
            summaries.append(
                SummaryPayload(
                    title=file_name,
                    bullets=bullets[:6],
                    source_count=len(docs),
                )
            )
        return summaries

    def summarize_collection(self, documents: list[Document]) -> SummaryPayload:
        excerpt = self._build_excerpt(documents[:12])
        response = self.llm.invoke(
            [
                SystemMessage(content=SUMMARY_PROMPT),
                HumanMessage(content=f"Summarize the combined document set.\n\n{excerpt}"),
            ]
        )
        bullets = [line.strip("- ").strip() for line in response.content.splitlines() if line.strip()]
        return SummaryPayload(title="Portfolio Summary", bullets=bullets[:8], source_count=len(documents))

    def extract_topics_and_insights(self, documents: list[Document]) -> tuple[list[str], list[str]]:
        excerpt = self._build_excerpt(documents[:10])
        response = self.llm.invoke(
            [
                SystemMessage(content="Return valid JSON only."),
                HumanMessage(content=f"{TOPIC_EXTRACTION_PROMPT}\n\n{excerpt}"),
            ]
        )
        try:
            payload = json.loads(response.content)
        except json.JSONDecodeError:
            return [], []
        topics = payload.get("topics", [])[:8]
        insights = payload.get("insights", [])[:5]
        return topics, insights

    @staticmethod
    def _build_excerpt(documents: list[Document]) -> str:
        parts: list[str] = []
        for doc in documents:
            metadata = doc.metadata
            label = f"{metadata.get('file_name')} | {metadata.get('section_title') or 'Section'}"
            if metadata.get("page_number"):
                label += f" | Page {metadata['page_number']}"
            parts.append(f"[{label}]\n{doc.page_content[:1000]}")
        return "\n\n".join(parts)
