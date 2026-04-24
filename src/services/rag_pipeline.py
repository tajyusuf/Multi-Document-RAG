from __future__ import annotations

from pathlib import Path
from statistics import mean

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from src.config import AppConfig
from src.models import AnswerPayload, SourceSnippet
from src.prompts import QUERY_REWRITE_PROMPT, SYSTEM_GROUNDED_QA_PROMPT
from src.services.chunking import SemanticChunker
from src.services.document_processor import DocumentProcessor
from src.services.summarizer import DocumentSummarizer
from src.services.vector_store import VectorStoreManager


class RAGOrchestrator:
    """Coordinates ingestion, retrieval, rewriting, grounded answering, and summaries."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.processor = DocumentProcessor()
        self.chunker = SemanticChunker(
            chunk_size=config.max_chunk_size,
            chunk_overlap=config.chunk_overlap,
        )
        self.vector_store = VectorStoreManager(
            embedding_model=config.embedding_model,
            persist_directory=config.chroma_path,
        )
        self.llm = ChatGroq(
            model=config.groq_chat_model,
            api_key=config.groq_api_key,
            temperature=0.2,
        )
        self.summarizer = DocumentSummarizer(self.llm)

    def ingest_files(self, uploaded_files: list) -> dict[str, int]:
        self.config.uploads_path.mkdir(parents=True, exist_ok=True)
        ingested_counts: dict[str, int] = {}
        chunk_documents: list[Document] = []

        for uploaded_file in uploaded_files:
            file_path = self._save_upload(uploaded_file.name, uploaded_file.getbuffer())
            sections = self.processor.load(file_path)
            chunks = self.chunker.chunk_sections(sections)
            ingested_counts[uploaded_file.name] = len(chunks)
            chunk_documents.extend(chunks)

        self.vector_store.add_documents(chunk_documents)
        return ingested_counts

    def ask(self, query: str, chat_history: list[dict[str, str]]) -> AnswerPayload:
        if not self.vector_store.get_all_documents():
            return AnswerPayload(
                answer=(
                    "## Answer\n"
                    "No documents are indexed yet.\n\n"
                    "## Evidence\n"
                    "Upload and index one or more PDF, DOCX, or TXT files before asking a question.\n\n"
                    "## Caveats\n"
                    "The assistant cannot answer without retrieved source material."
                ),
                confidence=0.0,
                rewritten_query=query,
                insights=[],
                topics=[],
                sources=[],
                raw_metadata={"retrieved_chunks": 0},
            )
        rewritten_query = self._rewrite_query(query, chat_history)
        primary_hits = self.vector_store.similarity_search(rewritten_query, k=self.config.max_context_chunks)
        mmr_hits = self.vector_store.max_marginal_relevance_search(
            rewritten_query,
            k=self.config.max_context_chunks,
            fetch_k=max(20, self.config.max_context_chunks * 3),
        )
        merged_documents = self._merge_results(primary_hits, mmr_hits)
        context = self._build_context(merged_documents)
        answer = self.llm.invoke(
            [
                SystemMessage(content=SYSTEM_GROUNDED_QA_PROMPT),
                HumanMessage(
                    content=(
                        f"User query: {query}\n"
                        f"Optimized query: {rewritten_query}\n\n"
                        f"Context:\n{context}"
                    )
                ),
            ]
        )

        scored_sources = self._build_sources(primary_hits, merged_documents)
        confidence = self._estimate_confidence(primary_hits)
        topics, insights = self.summarizer.extract_topics_and_insights(merged_documents)
        return AnswerPayload(
            answer=answer.content,
            confidence=confidence,
            rewritten_query=rewritten_query,
            insights=insights,
            topics=topics,
            sources=scored_sources,
            raw_metadata={"retrieved_chunks": len(merged_documents)},
        )

    def get_document_summaries(self):
        documents = self.vector_store.get_all_documents()
        if not documents:
            return [], None
        per_doc = self.summarizer.summarize_by_document(documents)
        combined = self.summarizer.summarize_collection(documents)
        return per_doc, combined

    def get_document_catalog(self) -> dict[str, list[Document]]:
        grouped: dict[str, list[Document]] = {}
        for doc in self.vector_store.get_all_documents():
            grouped.setdefault(doc.metadata.get("file_name", "Unknown"), []).append(doc)
        return dict(sorted(grouped.items()))

    def reset_knowledge_base(self) -> None:
        self.vector_store.reset()

    def _rewrite_query(self, query: str, chat_history: list[dict[str, str]]) -> str:
        history_excerpt = "\n".join(
            f"{item['role'].upper()}: {item['content'][:300]}" for item in chat_history[-4:]
        )
        response = self.llm.invoke(
            [
                SystemMessage(content=QUERY_REWRITE_PROMPT),
                HumanMessage(
                    content=(
                        f"Conversation context:\n{history_excerpt or 'No previous history.'}\n\n"
                        f"Original query:\n{query}"
                    )
                ),
            ]
        )
        return response.content.strip()

    def _merge_results(
        self,
        primary_hits: list[tuple[Document, float]],
        mmr_hits: list[Document],
    ) -> list[Document]:
        seen: set[str] = set()
        merged: list[Document] = []
        for doc, _score in primary_hits:
            chunk_id = doc.metadata.get("chunk_id")
            if chunk_id not in seen:
                seen.add(chunk_id)
                merged.append(doc)
        for doc in mmr_hits:
            chunk_id = doc.metadata.get("chunk_id")
            if chunk_id not in seen:
                seen.add(chunk_id)
                merged.append(doc)
        return merged[: self.config.max_context_chunks]

    def _build_context(self, documents: list[Document]) -> str:
        parts: list[str] = []
        for doc in documents:
            metadata = doc.metadata
            source = metadata.get("file_name", "Unknown")
            if metadata.get("page_number"):
                source += f" | Page {metadata['page_number']}"
            if metadata.get("section_title"):
                source += f" | {metadata['section_title']}"
            parts.append(f"[{source}]\n{doc.page_content}")
        return "\n\n".join(parts)

    def _build_sources(
        self,
        primary_hits: list[tuple[Document, float]],
        merged_documents: list[Document],
    ) -> list[SourceSnippet]:
        relevance_map = {
            doc.metadata.get("chunk_id"): max(0.0, min(1.0, score))
            for doc, score in primary_hits
        }
        sources: list[SourceSnippet] = []
        for doc in merged_documents:
            metadata = doc.metadata
            chunk_id = metadata.get("chunk_id", "")
            sources.append(
                SourceSnippet(
                    file_name=metadata.get("file_name", "Unknown"),
                    page_number=metadata.get("page_number"),
                    section_title=metadata.get("section_title"),
                    content=doc.page_content,
                    relevance=relevance_map.get(chunk_id, 0.55),
                    chunk_id=chunk_id,
                )
            )
        return sources

    @staticmethod
    def _estimate_confidence(primary_hits: list[tuple[Document, float]]) -> float:
        if not primary_hits:
            return 0.0
        return round(mean(max(0.0, min(1.0, score)) for _doc, score in primary_hits), 2)

    def _save_upload(self, file_name: str, data: bytes) -> Path:
        file_path = self.config.uploads_path / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        return file_path
