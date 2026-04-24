APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Manrope:wght@400;500;600;700&display=swap');

:root {
    --bg: #08111f;
    --bg-soft: #0f1b31;
    --panel: rgba(12, 23, 43, 0.72);
    --panel-strong: rgba(15, 28, 52, 0.9);
    --stroke: rgba(255, 255, 255, 0.1);
    --text: #ecf4ff;
    --muted: #97adc9;
    --accent: #60a5fa;
    --accent-2: #22d3ee;
    --good: #34d399;
    --warning: #fbbf24;
    --shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(34, 211, 238, 0.22), transparent 28%),
        radial-gradient(circle at top right, rgba(96, 165, 250, 0.18), transparent 30%),
        linear-gradient(180deg, #07101d 0%, #091427 50%, #08111f 100%);
    color: var(--text);
    font-family: 'Manrope', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(8, 17, 31, 0.96), rgba(12, 24, 46, 0.9));
    border-right: 1px solid var(--stroke);
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: -0.03em;
    color: var(--text);
}

.hero-shell {
    position: relative;
    overflow: hidden;
    padding: 2rem;
    border-radius: 28px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: linear-gradient(135deg, rgba(15, 27, 48, 0.88), rgba(11, 31, 58, 0.62));
    box-shadow: var(--shadow);
    backdrop-filter: blur(22px);
    margin-bottom: 1.5rem;
}

.hero-shell::after {
    content: "";
    position: absolute;
    inset: auto -20% -45% auto;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(34, 211, 238, 0.25), transparent 62%);
    pointer-events: none;
}

.hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 0.85rem;
    border-radius: 999px;
    background: rgba(96, 165, 250, 0.14);
    border: 1px solid rgba(96, 165, 250, 0.25);
    color: #d7ebff;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

.hero-title {
    font-size: clamp(2.1rem, 4vw, 4rem);
    line-height: 1;
    margin: 0 0 0.8rem 0;
}

.hero-copy {
    max-width: 760px;
    color: var(--muted);
    font-size: 1rem;
    line-height: 1.7;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin: 1.4rem 0 0.2rem;
}

.metric-card, .glass-card, .source-card {
    background: var(--panel);
    border: 1px solid var(--stroke);
    border-radius: 22px;
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow);
    backdrop-filter: blur(18px);
}

.metric-label {
    color: var(--muted);
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    margin-top: 0.2rem;
}

.section-title {
    margin: 0.2rem 0 0.8rem;
    font-size: 1.1rem;
}

.source-card {
    margin-bottom: 0.85rem;
}

.source-meta {
    color: #c4d8f2;
    font-size: 0.88rem;
    margin-bottom: 0.5rem;
}

.confidence-pill {
    display: inline-flex;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: rgba(52, 211, 153, 0.12);
    color: #b8ffe4;
    border: 1px solid rgba(52, 211, 153, 0.25);
    font-size: 0.8rem;
}

.highlight-box {
    background: rgba(96, 165, 250, 0.08);
    border-left: 3px solid var(--accent-2);
    padding: 0.9rem 1rem;
    border-radius: 14px;
    color: #dcecff;
    font-size: 0.95rem;
    line-height: 1.6;
}

.summary-bullet {
    padding: 0.5rem 0 0.5rem 1.1rem;
    position: relative;
    color: #dbeafe;
}

.summary-bullet::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0.95rem;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
}

.small-muted {
    color: var(--muted);
    font-size: 0.9rem;
}

.stButton > button, .stDownloadButton > button {
    border-radius: 14px;
    border: 1px solid rgba(96, 165, 250, 0.35);
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.92), rgba(34, 211, 238, 0.82));
    color: white;
    font-weight: 700;
    padding: 0.7rem 1rem;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 32px rgba(59, 130, 246, 0.28);
}

.stTextInput > div > div > input, .stTextArea textarea {
    background: rgba(12, 23, 43, 0.7);
    color: var(--text);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

[data-testid="stFileUploader"] {
    background: rgba(12, 23, 43, 0.58);
    border: 1px dashed rgba(96, 165, 250, 0.35);
    border-radius: 20px;
    padding: 0.5rem;
}

[data-testid="stChatMessage"] {
    background: rgba(12, 23, 43, 0.48);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
}

@media (max-width: 768px) {
    .hero-shell {
        padding: 1.35rem;
        border-radius: 22px;
    }
}
</style>
"""
