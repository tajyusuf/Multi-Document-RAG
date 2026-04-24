# AI Document Intelligence System using RAG

A production-style, full-stack document intelligence app built with Python, Streamlit, LangChain, Groq, HuggingFace embeddings, and ChromaDB.

## Features

- Multi-document ingestion for `PDF`, `DOCX`, and `TXT`
- Page-aware extraction and metadata-rich chunking
- Semantic retrieval with HuggingFace embeddings + ChromaDB
- Query rewriting for stronger retrieval on vague questions
- Cross-document grounded Q&A with source citations
- Per-document summaries and portfolio-wide summaries
- Topic extraction, key insights, and confidence scoring
- Chat memory with a polished SaaS-style UI
- Evidence panel with highlighted retrieved passages

## Folder Structure

```text
.
├── app.py
├── requirements.txt
├── .env.example
├── README.md
└── src
    ├── __init__.py
    ├── config.py
    ├── models.py
    ├── prompts.py
    ├── services
    │   ├── __init__.py
    │   ├── chunking.py
    │   ├── document_processor.py
    │   ├── rag_pipeline.py
    │   ├── summarizer.py
    │   └── vector_store.py
    └── ui
        ├── __init__.py
        ├── styles.py
        └── view_helpers.py
```

## Quick Start

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set `GROQ_API_KEY`.
4. Start the app:

```bash
streamlit run app.py
```

## Notes

- The app uses Groq for fast grounded generation and query rewriting.
- Embeddings are generated locally with `sentence-transformers/all-mpnet-base-v2`, then stored in ChromaDB for retrieval.
- Chroma persists locally under `storage/chroma`, so uploaded knowledge survives restarts.
- The system is designed to refuse unsupported claims by constraining answers to retrieved evidence.
