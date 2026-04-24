from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


class VectorStoreManager:
    def __init__(self, embedding_model: str, persist_directory: Path) -> None:
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.persist_directory = persist_directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.vector_store = Chroma(
            collection_name="document_intelligence",
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory),
        )

    def add_documents(self, documents: list[Document]) -> None:
        if documents:
            self.vector_store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 8) -> list[tuple[Document, float]]:
        return self.vector_store.similarity_search_with_relevance_scores(query, k=k)

    def max_marginal_relevance_search(self, query: str, k: int = 8, fetch_k: int = 20) -> list[Document]:
        return self.vector_store.max_marginal_relevance_search(query, k=k, fetch_k=fetch_k)

    def get_all_documents(self) -> list[Document]:
        payload = self.vector_store.get(include=["documents", "metadatas"])
        documents: list[Document] = []
        for text, metadata in zip(payload["documents"], payload["metadatas"], strict=False):
            documents.append(Document(page_content=text, metadata=metadata))
        return documents

    def reset(self) -> None:
        self.vector_store.reset_collection()
