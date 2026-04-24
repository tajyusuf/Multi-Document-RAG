from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from src.config import get_config
from src.services.rag_pipeline import RAGOrchestrator
from src.ui.styles import APP_CSS
from src.ui.view_helpers import confidence_label, highlight_text


load_dotenv()

st.set_page_config(
    page_title="AI Document Intelligence",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def build_orchestrator() -> RAGOrchestrator:
    config = get_config()
    return RAGOrchestrator(config)


def init_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("last_answer", None)
    st.session_state.setdefault("active_nav", "Chat")


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-kicker">AI SaaS | RAG-powered | Grounded with citations</div>
            <h1 class="hero-title">AI Document Intelligence System</h1>
            <p class="hero-copy">
                Upload PDFs, DOCX files, and text documents into a unified knowledge workspace.
                Ask nuanced cross-document questions, inspect the exact evidence used in each answer,
                and generate recruiter-ready insights with a premium, modern analyst experience.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(orchestrator: RAGOrchestrator) -> None:
    catalog = orchestrator.get_document_catalog()
    total_documents = len(catalog)
    total_chunks = sum(len(chunks) for chunks in catalog.values())
    total_pages = sum(
        1 for chunks in catalog.values() for chunk in chunks if chunk.metadata.get("page_number")
    )
    metrics_html = f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Indexed Documents</div>
            <div class="metric-value">{total_documents}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Semantic Chunks</div>
            <div class="metric-value">{total_chunks}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Page-aware Evidence</div>
            <div class="metric-value">{total_pages}</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)


def render_sidebar(orchestrator: RAGOrchestrator) -> None:
    with st.sidebar:
        st.markdown("## Control Center")
        nav = st.radio(
            "Workspace",
            options=["Upload", "Chat", "Summaries"],
            index=["Upload", "Chat", "Summaries"].index(st.session_state["active_nav"]),
        )
        st.session_state["active_nav"] = nav

        st.markdown("### Knowledge Base")
        if st.button("Reset Indexed Documents", use_container_width=True):
            orchestrator.reset_knowledge_base()
            st.session_state["messages"] = []
            st.session_state["last_answer"] = None
            st.success("Knowledge base cleared.")

        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">System Guardrails</div>
                <div class="small-muted">
                    Answers are forced to stay grounded in retrieved evidence. Missing evidence is reported instead of hallucinated.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def upload_view(orchestrator: RAGOrchestrator) -> None:
    st.markdown("### Upload & Index")
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Bring your document set together</div>
            <div class="small-muted">Drag files into the drop zone, then index them into a persistent semantic knowledge base.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Upload files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files:
        if st.button("Index Documents", use_container_width=True):
            with st.spinner("Extracting, chunking, embedding, and storing documents..."):
                counts = orchestrator.ingest_files(uploaded_files)
            st.success("Documents indexed successfully.")
            cols = st.columns(min(3, max(1, len(counts))))
            for idx, (file_name, chunk_count) in enumerate(counts.items()):
                with cols[idx % len(cols)]:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-label">{file_name}</div>
                            <div class="metric-value">{chunk_count}</div>
                            <div class="small-muted">indexed chunks</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    catalog = orchestrator.get_document_catalog()
    if catalog:
        st.markdown("### Indexed Library")
        for file_name, docs in catalog.items():
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="section-title">{file_name}</div>
                    <div class="small-muted">{len(docs)} indexed chunks | {len({doc.metadata.get('page_number') for doc in docs if doc.metadata.get('page_number')})} distinct pages detected</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def chat_view(orchestrator: RAGOrchestrator) -> None:
    st.markdown("### Analyst Chat")
    left_col, right_col = st.columns([1.5, 1], gap="large")

    with left_col:
        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Ask a cross-document question...")
        if prompt:
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Reasoning over your documents..."):
                    payload = orchestrator.ask(prompt, st.session_state["messages"][:-1])
                st.markdown(payload.answer)
                st.session_state["messages"].append({"role": "assistant", "content": payload.answer})
                st.session_state["last_answer"] = payload

    with right_col:
        payload = st.session_state.get("last_answer")
        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">Answer Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not payload:
            st.info("Ask a question to see sources, confidence, topics, and insights.")
            return

        st.markdown(
            f"""
            <div class="glass-card">
                <span class="confidence-pill">{confidence_label(payload.confidence)} | {int(payload.confidence * 100)}%</span>
                <div class="small-muted" style="margin-top:0.8rem;">Optimized query: {payload.rewritten_query}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if payload.topics:
            st.markdown("#### Topics")
            st.write(" | ".join(payload.topics))

        if payload.insights:
            st.markdown("#### Key Insights")
            for insight in payload.insights:
                st.markdown(f"<div class='summary-bullet'>{insight}</div>", unsafe_allow_html=True)

        st.markdown("#### Evidence Panel")
        for source in payload.sources:
            source_label = source.file_name
            if source.page_number:
                source_label += f" | Page {source.page_number}"
            if source.section_title:
                source_label += f" | {source.section_title}"
            highlighted = highlight_text(source.content[:900], payload.rewritten_query)
            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-meta">{source_label}</div>
                    <div class="small-muted">Relevance score: {int(source.relevance * 100)}%</div>
                    <div class="highlight-box">{highlighted}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def summaries_view(orchestrator: RAGOrchestrator) -> None:
    st.markdown("### Summaries & Themes")
    per_doc, combined = orchestrator.get_document_summaries()
    if not per_doc or not combined:
        st.info("Index documents first to generate summaries and thematic insights.")
        return

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-title">{combined.title}</div>
            <div class="small-muted">Built from {combined.source_count} indexed chunks across your knowledge base.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for bullet in combined.bullets:
        st.markdown(f"<div class='summary-bullet'>{bullet}</div>", unsafe_allow_html=True)

    st.markdown("### Per-document Executive Briefs")
    cols = st.columns(2, gap="large")
    for index, summary in enumerate(per_doc):
        with cols[index % 2]:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="section-title">{summary.title}</div>
                    <div class="small-muted">{summary.source_count} supporting chunks</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for bullet in summary.bullets:
                st.markdown(f"<div class='summary-bullet'>{bullet}</div>", unsafe_allow_html=True)


def main() -> None:
    init_state()
    st.markdown(APP_CSS, unsafe_allow_html=True)
    config = get_config()

    if not config.groq_api_key:
        st.error("GROQ_API_KEY is missing. Add it to your .env file before running the app.")
        st.stop()

    orchestrator = build_orchestrator()
    render_sidebar(orchestrator)
    render_hero()
    render_metrics(orchestrator)

    active_nav = st.session_state["active_nav"]
    if active_nav == "Upload":
        upload_view(orchestrator)
    elif active_nav == "Summaries":
        summaries_view(orchestrator)
    else:
        chat_view(orchestrator)


if __name__ == "__main__":
    main()
