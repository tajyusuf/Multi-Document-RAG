from __future__ import annotations

import hashlib

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.models import IngestedSection


class SemanticChunker:
    """Hybrid structural chunker that preserves section metadata and continuity."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
        )

    def chunk_sections(self, sections: list[IngestedSection]) -> list[Document]:
        documents: list[Document] = []
        for section in sections:
            parts = self.splitter.split_text(section.text)
            for idx, part in enumerate(parts, start=1):
                chunk_id = hashlib.sha1(
                    f"{section.file_name}:{section.order}:{idx}:{part[:120]}".encode("utf-8")
                ).hexdigest()
                documents.append(
                    Document(
                        page_content=part,
                        metadata={
                            "chunk_id": chunk_id,
                            "file_name": section.file_name,
                            "file_type": section.file_type,
                            "page_number": section.page_number,
                            "section_title": section.section_title,
                            "section_order": section.order,
                            "chunk_order": idx,
                        },
                    )
                )
        return documents
