"""
FraudSentinel AI – Scam Call Detection System
Main Streamlit Application
"""

import sys
import os
import time
import streamlit as st

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scam_detector import ScamDetectorOrchestrator
from demo_transcripts import DEMO_TRANSCRIPTS
from utils import get_risk_color, get_risk_emoji, get_risk_level, SCAM_TYPES

# ── Page Config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="FraudSentinel AI – Scam Call Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

/* Global */
* { font-family: 'Outfit', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #050505 0%, #0a0a0a 40%, #0f172a 100%);
    color: #e2e8f0;
}

/* Hide default streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Hero header */
.hero-container {
    text-align: center;
    padding: 3.5rem 2rem 2.5rem;
    margin-bottom: 2rem;
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 30px;
    border: 1px solid rgba(14, 165, 233, 0.15);
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(14, 165, 233, 0.05), inset 0 0 20px rgba(139, 92, 246, 0.05);
}
.hero-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, #0ea5e9, #8b5cf6, #ec4899, transparent);
    animation: neon-sweep 4s linear infinite;
}
@keyframes neon-sweep {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    text-transform: uppercase;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 30%, #c084fc 70%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    letter-spacing: -0.04em;
    filter: drop-shadow(0px 0px 8px rgba(129, 140, 248, 0.4));
}
.hero-subtitle {
    font-size: 1.15rem;
    color: #94a3b8;
    font-weight: 500;
    letter-spacing: 0.05em;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.4rem 1.4rem;
    background: rgba(14, 165, 233, 0.08);
    border: 1px solid rgba(14, 165, 233, 0.3);
    border-radius: 30px;
    color: #38bdf8;
    font-size: 0.8rem;
    font-weight: 700;
    margin-top: 1rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    box-shadow: 0 0 15px rgba(14, 165, 233, 0.15);
}

/* Glass card */
.glass-card {
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    transition: all 0.4s cubic-bezier(.17,.67,.26,1.02);
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
.glass-card:hover {
    border-color: rgba(139, 92, 246, 0.3);
    box-shadow: 0 15px 50px rgba(139, 92, 246, 0.1), inset 0 0 10px rgba(255, 255, 255, 0.02);
    transform: translateY(-2px);
}
.card-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 1.2rem;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    text-shadow: 0 2px 5px rgba(0,0,0,0.5);
    letter-spacing: 0.02em;
}

/* ── Risk Score Circular Gauge ── */
.risk-gauge-wrap {
    position: relative;
    width: 200px;
    height: 200px;
    margin: 1rem auto 1.5rem;
}
.risk-gauge-ring {
    width: 100%; height: 100%;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    position: relative;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.6);
}
.risk-gauge-ring::before {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 50%;
    padding: 8px;
    background: conic-gradient(var(--gauge-color) calc(var(--gauge-pct) * 1%), rgba(30,30,40,0.4) 0);
    -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 8px), #000 calc(100% - 7px));
    mask: radial-gradient(farthest-side, transparent calc(100% - 8px), #000 calc(100% - 7px));
    filter: drop-shadow(0 0 10px var(--gauge-color));
}
.risk-gauge-inner {
    width: 164px; height: 164px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(15,23,42,0.95) 0%, rgba(5,5,10,0.98) 100%);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    box-shadow: inset 0 0 25px rgba(0,0,0,0.8), 0 0 15px rgba(0,0,0,0.5);
    border: 1px solid rgba(255,255,255,0.02);
}
.risk-gauge-number {
    font-size: 3.8rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.05em;
    text-shadow: 0 0 20px var(--gauge-color);
}
.risk-gauge-label {
    font-size: 0.8rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-top: 0.4rem;
    text-shadow: 0 0 10px var(--gauge-color);
}
.risk-gauge-sublabel {
    font-size: 0.7rem;
    color: #64748b;
    margin-top: 0.2rem;
    font-weight: 500;
}

/* Scam type badge */
.scam-type-badge {
    display: inline-block;
    padding: 0.5rem 1.5rem;
    border-radius: 40px;
    font-weight: 800;
    font-size: 0.95rem;
    letter-spacing: 0.05em;
    margin: 0.5rem 0;
    text-transform: uppercase;
    box-shadow: 0 0 20px rgba(0,0,0,0.2);
    backdrop-filter: blur(10px);
}

/* Indicator pills */
.indicator-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.4rem 1rem;
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 24px;
    color: #fca5a5;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 0.25rem 0.4rem 0.25rem 0;
    transition: all 0.3s;
    box-shadow: 0 0 8px rgba(239, 68, 68, 0.05);
}
.indicator-pill:hover {
    background: rgba(239, 68, 68, 0.15);
    box-shadow: 0 0 12px rgba(239, 68, 68, 0.2);
    transform: translateY(-1px);
}

/* Agent pipeline steps */
.agent-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.4rem;
    color: #64748b;
    font-size: 0.92rem;
    font-weight: 500;
    border-radius: 12px;
    background: rgba(15, 23, 42, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.02);
    transition: all 0.4s ease;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.01);
}
.agent-active {
    color: #38bdf8;
    font-weight: 700;
    background: rgba(14, 165, 233, 0.08);
    border: 1px solid rgba(14, 165, 233, 0.4);
    box-shadow: 0 0 20px rgba(14, 165, 233, 0.15), inset 0 0 10px rgba(14, 165, 233, 0.05);
    transform: scale(1.01);
}
.agent-done {
    color: #4ade80;
    background: rgba(34, 197, 94, 0.06);
    border: 1px solid rgba(34, 197, 94, 0.15);
}

/* Recommendation / Warning boxes */
.recommendation-box {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.05), rgba(139, 92, 246, 0.05));
    border-left: 4px solid #8b5cf6;
    border-radius: 0 16px 16px 0;
    padding: 1.25rem 1.5rem;
    margin-top: 1.25rem;
    color: #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.8;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.recommendation-title {
    font-weight: 800;
    color: #c4b5fd;
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    display: flex;
    align-items: center;
    gap: 8px;
}
.warning-box {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(220, 38, 38, 0.05));
    border-left: 4px solid #ef4444;
    border-radius: 0 16px 16px 0;
    padding: 1.25rem 1.5rem;
    margin-top: 1.25rem;
    color: #fca5a5;
    font-size: 0.95rem;
    line-height: 1.8;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1);
}

/* Score detail rows */
.score-detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    color: #94a3b8;
    font-size: 0.92rem;
    transition: background 0.2s;
    border-radius: 6px;
}
.score-detail-row:hover { background: rgba(255,255,255,0.02); }
.score-detail-row:last-child { border-bottom: none; }
.score-detail-label { font-weight: 600; }
.score-detail-value { font-weight: 800; color: #f8fafc; font-variant-numeric: tabular-nums; }

/* Demo buttons */
.stButton > button {
    border-radius: 14px;
    font-weight: 700;
    padding: 0.6rem 1.2rem;
    transition: all 0.3s cubic-bezier(.17,.67,.26,1.02);
    border: 1px solid rgba(139, 92, 246, 0.2);
    background: rgba(139, 92, 246, 0.08);
    color: #e2e8f0;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}
.stButton > button:hover {
    border-color: rgba(139, 92, 246, 0.6);
    background: rgba(139, 92, 246, 0.15);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.2), inset 0 0 10px rgba(139, 92, 246, 0.1);
    color: white;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);
    border: none;
    color: white;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 8px 30px rgba(139, 92, 246, 0.5), inset 0 0 15px rgba(255,255,255,0.2);
    border: none;
    background: linear-gradient(135deg, #38bdf8 0%, #a78bfa 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(10, 15, 30, 0.8) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #f8fafc;
    font-weight: 800;
    letter-spacing: -0.02em;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(15, 23, 42, 0.3);
    padding: 8px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.03);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 16px;
    color: #94a3b8;
    font-weight: 600;
    transition: all 0.3s;
    background-color: transparent;
}
.stTabs [aria-selected="true"] {
    background-color: rgba(139, 92, 246, 0.15) !important;
    color: #c4b5fd !important;
    box-shadow: 0 0 10px rgba(139, 92, 246, 0.1);
}

/* Category bars */
.cat-bar-container { margin-bottom: 0.85rem; }
.cat-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 0.4rem;
}
.cat-bar-track {
    height: 8px;
    background: rgba(15, 23, 42, 0.8);
    border-radius: 4px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.02);
}
.cat-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 1s cubic-bezier(.17,.67,.26,1.02);
    box-shadow: 0 0 10px currentcolor;
}

/* Transcript box */
.transcript-box {
    background: rgba(5, 5, 10, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 16px;
    padding: 1.5rem;
    color: #cbd5e1;
    font-size: 0.9rem;
    line-height: 1.8;
    max-height: 450px;
    overflow-y: auto;
    white-space: pre-wrap;
    box-shadow: inset 0 5px 20px rgba(0,0,0,0.3);
}

/* Mode indicator */
.mode-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0.35rem 0.8rem;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    backdrop-filter: blur(5px);
}
.mode-llm {
    background: rgba(34, 197, 94, 0.08);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: #4ade80;
    box-shadow: 0 0 15px rgba(34, 197, 94, 0.1);
}
.mode-rule {
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.3);
    color: #fbbf24;
    box-shadow: 0 0 15px rgba(245, 158, 11, 0.1);
}

/* Pipeline icon card (landing) */
.pipeline-icon-card {
    background: rgba(15,23,42,0.4);
    border: 1px solid rgba(139, 92, 246, 0.1);
    border-radius: 16px;
    padding: 1.5rem 0.5rem;
    transition: all 0.4s cubic-bezier(.17,.67,.26,1.02);
    backdrop-filter: blur(10px);
}
.pipeline-icon-card:hover {
    border-color: rgba(139, 92, 246, 0.4);
    background: rgba(139, 92, 246, 0.08);
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(139, 92, 246, 0.15);
}

/* Stats row on landing */
.stat-number {
    font-size: 1.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #38bdf8, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 2px 4px rgba(56, 189, 248, 0.2));
}

/* Neon glow animations for progress */
.progress-glow {
    filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.6));
}

/* Animations */
@keyframes pulse-glow {
    0%, 100% { opacity: 0.7; filter: drop-shadow(0 0 5px rgba(56, 189, 248, 0.3)); }
    50% { opacity: 1; filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.8)); text-shadow: 0 0 8px rgba(56, 189, 248, 0.8); }
}
@keyframes slide-up {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}
.animate-in {
    animation: slide-up 0.6s cubic-bezier(.17,.67,.26,1.02) forwards;
}
.delay-1 { animation-delay: 0.1s; opacity: 0; animation-fill-mode: forwards; }
.delay-2 { animation-delay: 0.2s; opacity: 0; animation-fill-mode: forwards; }
.delay-3 { animation-delay: 0.3s; opacity: 0; animation-fill-mode: forwards; }
</style>
""", unsafe_allow_html=True)

# ── Hero Header ────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-container">
    <div class="hero-title">🛡️ FraudSentinel AI</div>
    <div class="hero-subtitle">Multi-Layer Agentic Intelligence for Scam Call Detection</div>
    <div class="hero-badge">🤖 6-Layer Detection Pipeline &nbsp;•&nbsp; 4-Signal Risk Scoring</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Configuration ─────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Dashboard")

    st.markdown("---")
    with st.expander("🛠️ Advanced Configuration", expanded=False):
        st.markdown("### 🔑 API Settings")

        # Auto-detect OpenRouter API Key from environment (check both common variants)
        env_api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPEN_ROUTER_API_KEY") or ""

        if env_api_key:
            st.markdown(
                "<span style='font-size:0.82rem; color:#4ade80;'>"
                "✅ OPENROUTER_API_KEY detected from environment"
                "</span>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<span style='font-size:0.82rem; color:#64748b;'>"
                "Enter your OpenRouter API key for LLM-enhanced analysis. "
                "Without a key, rule-based analysis is used."
                "</span>",
                unsafe_allow_html=True,
            )

        api_provider = st.selectbox(
            "API Provider",
            ["OpenRouter", "OpenAI"],
            help="Select your LLM provider (OpenRouter recommended)",
        )

        api_key_input = st.text_input(
            "API Key",
            type="password",
            value=env_api_key if env_api_key else "",
            placeholder="sk-or-... (your OpenRouter key)",
        )

        # Use input key, fallback to env key
        api_key = api_key_input if api_key_input else env_api_key

        if api_provider == "OpenRouter":
            model = st.text_input(
                "Model",
                value="openai/gpt-4o-mini",
                placeholder="e.g. openai/gpt-4o-mini",
            )
            base_url = "https://openrouter.ai/api/v1"
        else:
            model = st.selectbox(
                "Model",
                ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4", "gpt-4o"],
            )
            base_url = None

    st.markdown("### 🤖 Agent Pipeline")
    st.markdown("""
    <div style="font-size: 0.85rem; color: #94a3b8; line-height: 2; border-left: 2px solid rgba(139,92,246,0.3); padding-left: 10px;">
        <div style="color:#e2e8f0; font-weight:600;">1. Speech Agent</div>
        <div style="color:#e2e8f0; font-weight:600;">2. Rule-based Agent</div>
        <div style="color:#e2e8f0; font-weight:600;">3. Semantic Agent</div>
        <div style="color:#e2e8f0; font-weight:600;">4. Social Agent</div>
        <div style="color:#e2e8f0; font-weight:600;">5. LLM Agent</div>
        <div style="color:#e2e8f0; font-weight:600;">6. Scoring Agent</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; font-size:0.75rem; color:#475569; letter-spacing:0.05em;'>"
        "FraudSentinel AI v1.0<br>Multi-Agent Security Layer"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Initialize Orchestrator ───────────────────────────────────────────────────

@st.cache_resource
def get_speech_agent():
    """Load the speech agent (cached)."""
    from speech_to_text import SpeechAgent
    return SpeechAgent()


def get_orchestrator(api_key_val, model_val, base_url_val):
    """Create a fresh orchestrator with current settings."""
    return ScamDetectorOrchestrator(
        api_key=api_key_val if api_key_val else None,
        model=model_val,
        base_url=base_url_val,
    )


# ── Main Content Area ─────────────────────────────────────────────────────────

# Input section
col_input, col_spacer, col_demo = st.columns([3, 0.2, 1.5])

with col_input:
    st.markdown(
        '<div class="card-title">📥 Input Source</div>',
        unsafe_allow_html=True,
    )

    input_tab1, input_tab2 = st.tabs(["🎙️ Upload Audio", "📝 Paste Transcript"])

    with input_tab1:
        uploaded_file = st.file_uploader(
            "Upload a phone call recording (Audio or Video)",
            type=["wav", "mp3", "ogg", "m4a", "flac", "wma", "mp4", "avi", "mov", "mkv", "webm"],
            help="Supported formats: WAV, MP3, OGG, M4A, FLAC, WMA, MP4, AVI, MOV, MKV, WEBM",
        )
        if uploaded_file:
            # Check if it's a video or audio file by extension
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            is_video = file_ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]
            
            if is_video:
                st.video(uploaded_file)
            else:
                st.audio(uploaded_file)

    with input_tab2:
        pasted_transcript = st.text_area(
            "Paste phone call transcript",
            height=200,
            placeholder="Paste the conversation transcript here...",
        )

with col_demo:
    st.markdown(
        '<div class="card-title">🧪 Quick Demo</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<span style='font-size:0.8rem; color:#64748b;'>Test with sample scam transcripts:</span>",
        unsafe_allow_html=True,
    )

    demo_bank = st.button("🏦 Bank OTP Scam", use_container_width=True)
    demo_courier = st.button("📦 Courier Scam", use_container_width=True)
    demo_investment = st.button("💰 Investment Scam", use_container_width=True)
    demo_safe = st.button("✅ Safe Call", use_container_width=True)

# ── Determine transcript to analyze ───────────────────────────────────────────

transcript_to_analyze = None
analysis_source = None

# Demo button handling
if demo_bank:
    transcript_to_analyze = DEMO_TRANSCRIPTS["bank_scam"]["transcript"]
    analysis_source = "Demo: Bank OTP Scam"
elif demo_courier:
    transcript_to_analyze = DEMO_TRANSCRIPTS["courier_scam"]["transcript"]
    analysis_source = "Demo: Courier Delivery Scam"
elif demo_investment:
    transcript_to_analyze = DEMO_TRANSCRIPTS["investment_scam"]["transcript"]
    analysis_source = "Demo: Investment Scam"
elif demo_safe:
    transcript_to_analyze = DEMO_TRANSCRIPTS["safe_call"]["transcript"]
    analysis_source = "Demo: Safe Call"

# Audio/Video upload handling
if uploaded_file is not None and transcript_to_analyze is None:
    # Use session state to store processed audio so we don't re-extract on every rerun
    if "processed_audio" not in st.session_state or st.session_state.get("last_uploaded") != uploaded_file.name:
        file_bytes = uploaded_file.read()
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        is_video = file_ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]
        
        st.session_state.processed_audio = file_bytes
        st.session_state.processed_ext = file_ext
        st.session_state.is_video = is_video
        st.session_state.last_uploaded = uploaded_file.name
        
        # If it's a video, extract audio immediately so we can show the player and download button
        if is_video:
            with st.spinner("🎬 Extracting audio from video file..."):
                try:
                    import tempfile
                    from pydub import AudioSegment
                    
                    with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_vid:
                        tmp_vid.write(file_bytes)
                        tmp_vid_path = tmp_vid.name
                    
                    video = AudioSegment.from_file(tmp_vid_path)
                    
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_aud:
                        tmp_aud_path = tmp_aud.name
                        
                    video.export(tmp_aud_path, format="mp3")
                    
                    with open(tmp_aud_path, "rb") as f:
                        audio_bytes = f.read()
                    
                    st.session_state.processed_audio = audio_bytes
                    st.session_state.processed_ext = ".mp3"
                    
                    os.unlink(tmp_vid_path)
                    os.unlink(tmp_aud_path)
                    st.success("✅ Audio extracted successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to extract audio: {str(e)}")
                    st.session_state.processed_audio = None

    # Show download button if audio was processed/extracted
    if st.session_state.get("processed_audio"):
        st.download_button(
            label="⬇️ Download Audio (MP3)",
            data=st.session_state.processed_audio,
            file_name=f"extracted_{os.path.splitext(uploaded_file.name)[0]}.mp3",
            mime="audio/mp3",
            key="download_btn"
        )
        
        # Analyze Button
        if st.button("🔍 Analyze Conversation", type="primary", use_container_width=True):
            with st.spinner("🎙️ Agent 1: Transcribing audio with Faster-Whisper..."):
                speech_agent = get_speech_agent()
                if speech_agent.is_available:
                    transcript, error = speech_agent.transcribe(
                        st.session_state.processed_audio, 
                        st.session_state.processed_ext
                    )
                    if error:
                        st.error(f"❌ Transcription error: {error}")
                    else:
                        transcript_to_analyze = transcript
                        analysis_source = f"File: {uploaded_file.name}"
                else:
                    st.warning("⚠️ Faster-Whisper is not available.")

# Pasted transcript handling
if pasted_transcript and pasted_transcript.strip() and transcript_to_analyze is None:
    if st.button("🔍 Analyze Pasted Transcript", type="primary", use_container_width=True):
        transcript_to_analyze = pasted_transcript.strip()
        analysis_source = "Pasted Transcript"

# ── Run Analysis ──────────────────────────────────────────────────────────────

if transcript_to_analyze:
    st.markdown("---")

    # Analysis mode indicator
    mode_class = "mode-llm" if api_key else "mode-rule"
    mode_text = "LLM-Enhanced Analysis" if api_key else "Rule-Based Analysis"
    mode_icon = "🧠" if api_key else "⚡"
    st.markdown(
        f'<div style="margin-bottom:1rem;">'
        f'<span class="mode-indicator {mode_class}">{mode_icon} {mode_text}</span>'
        f'<span style="font-size:0.82rem; color:#64748b; margin-left:0.5rem;">Source: {analysis_source}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Progress bar and Agent Pipeline Visualization
    st.markdown('<div class="card-title">🤖 Agentic Analysis Pipeline</div>', unsafe_allow_html=True)
    pipeline_container = st.container()
    
    with pipeline_container:
        agent_steps = [
            ("🎙️ Agent 1: Speech-to-Text", "Transcribing and extracting features..."),
            ("🔍 Agent 2: Rule-Based Detection", "Analyzing text for risky keywords..."),
            ("🧠 Agent 3: Semantic Similarity", "Detecting matching fraud intents..."),
            ("🎭 Agent 4: Social Engineering", "Identifying psychological manipulation tactics..."),
            ("🤖 Agent 5: LLM Reasoning", "Deep analysis using reasoning models..."),
            ("📊 Agent 6: Risk Scoring Engine", "Computing hybrid risk index...")
        ]
        
        step_placeholders = [st.empty() for _ in range(6)]
        
        # Initial state (all pending)
        for i, (title, _) in enumerate(agent_steps):
            step_placeholders[i].markdown(
                f'<div class="agent-step" style="opacity: 0.6;">⏳ <span>{title} <span style="font-size:0.8rem; color:#475569;">(Waiting)</span></span></div>', 
                unsafe_allow_html=True
            )
            
    st.markdown("<br>", unsafe_allow_html=True)
    progress_bar = st.progress(0)

    def progress_callback(step, total, message):
        progress_bar.progress(step / total)
        current_idx = step - 1
        
        # Update preceding steps to done
        for i in range(current_idx):
            title = agent_steps[i][0]
            step_placeholders[i].markdown(
                f'<div class="agent-step agent-done">✅ <span>{title} <span style="font-size:0.8rem; color:#22c55e;">(Complete)</span></span></div>', 
                unsafe_allow_html=True
            )
            
        # Update current step to active
        if current_idx < 6:
            title, desc = agent_steps[current_idx]
            step_placeholders[current_idx].markdown(
                f'<div class="agent-step agent-active">🔄 <span style="animation: pulse-glow 1.5s infinite;">{title} - <span style="color:#e0f2fe;">{desc}</span></span></div>', 
                unsafe_allow_html=True
            )
            
        time.sleep(0.4)  # Brief pause for visual effect

    # Run the orchestrator
    orchestrator = get_orchestrator(api_key, model, base_url)
    results = orchestrator.analyze_transcript(transcript_to_analyze, progress_callback)

    # Mark all done and clean up progress bar
    for i, (title, _) in enumerate(agent_steps):
        step_placeholders[i].markdown(
            f'<div class="agent-step agent-done">✅ {title} (Complete)</div>', 
            unsafe_allow_html=True
        )
    time.sleep(0.5)
    progress_bar.empty()

    # ── Display Results ───────────────────────────────────────────────────

    score = results["risk_score"]
    risk_color = get_risk_color(score)
    risk_emoji = get_risk_emoji(score)
    risk_level = results["risk_level"].upper()

    # Results layout
    r_col1, r_col2 = st.columns([1.2, 2])

    with r_col1:
        # Risk Score Gauge Card
        st.markdown(f"""
        <div class="glass-card animate-in" style="text-align:center;">
            <div class="risk-gauge-wrap" style="--gauge-color:{risk_color}; --gauge-pct:{score};">
                <div class="risk-gauge-ring">
                    <div class="risk-gauge-inner">
                        <div class="risk-gauge-number" style="color:{risk_color};">{score:.0f}</div>
                        <div class="risk-gauge-label" style="color:{risk_color};">{risk_emoji} {risk_level}</div>
                        <div class="risk-gauge-sublabel">Risk Score</div>
                    </div>
                </div>
            </div>
            <div class="scam-type-badge" style="
                background: {risk_color}15;
                border: 1px solid {risk_color}35;
                color: {risk_color};
            ">
                {results['scam_type_display']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Component Scores
        comp_scores = results["component_scores"]
        scores_html = '<div class="glass-card"><div class="card-title">📊 Score Breakdown</div>'
        for label, val in [
            ("Rule-Based Analysis", comp_scores.get("rule_score", 0)),
            ("Semantic Similarity", comp_scores.get("semantic_score", 0)),
            ("Social Engineering", comp_scores.get("social_score", 0)),
            ("LLM Reasoning", comp_scores.get("llm_score")),
        ]:
            if val is not None:
                bar_color = get_risk_color(val)
                scores_html += f"""
                <div class="score-detail-row">
                    <span class="score-detail-label">{label}</span>
                    <span class="score-detail-value" style="color:{bar_color};">{val:.0f}/100</span>
                </div>"""
            else:
                scores_html += f"""
                <div class="score-detail-row">
                    <span class="score-detail-label">{label}</span>
                    <span style="color:#475569; font-size:0.82rem;">N/A (no API key)</span>
                </div>"""
        scores_html += "</div>"
        st.markdown(scores_html, unsafe_allow_html=True)

    with r_col2:
        # Explanation card
        severity_class = "warning-box" if results["severity"] in ("high", "critical") else "recommendation-box"

        indicators_html = "".join(
            f'<span class="indicator-pill">⚠ {ind}</span>' for ind in results["indicators"][:8]
        )

        tactics_html = ""
        if results.get("tactics_used"):
            tactics_html = "<div style='margin-top:0.8rem;'><strong style='color:#94a3b8; font-size:0.82rem;'>Tactics Used:</strong><br>"
            tactics_html += "".join(
                f'<span class="indicator-pill" style="background:rgba(168,85,247,0.12);border-color:rgba(168,85,247,0.25);color:#c4b5fd;">🎭 {t}</span>'
                for t in results["tactics_used"][:6]
            )
            tactics_html += "</div>"

        st.markdown(f"""
        <div class="glass-card animate-in">
            <div class="card-title">🔍 Analysis Report</div>
            <p style="color:#cbd5e1; font-size:0.92rem; line-height:1.7; margin-bottom:1rem;">
                {results['explanation']}
            </p>
            <div style="margin-bottom:0.8rem;">
                <strong style="color:#94a3b8; font-size:0.82rem;">Indicators Detected:</strong><br>
                {indicators_html if indicators_html else '<span style="color:#4ade80; font-size:0.85rem;">✅ No significant fraud indicators detected</span>'}
            </div>
            {tactics_html}
            <div class="{severity_class}">
                <div class="recommendation-title">💡 Recommendation</div>
                {results['recommendation']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tabs for detailed breakdowns
        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["🏷️ Keyword Analysis", "🧠 Semantic Matches", "🎭 Social Tactics"])

        # Keyword category breakdown
        with tab1:
            kw_details = results.get("keyword_details", {})
            cat_scores = kw_details.get("category_scores", {})
            matched = kw_details.get("matched_keywords", {})

            cat_html = ""
            if any(s > 0 for s in cat_scores.values()):
                cat_html = '<div class="glass-card animate-in delay-1" style="padding: 1.2rem;">'
                sorted_cats = sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)
                for cat, cat_score in sorted_cats:
                    if cat_score > 0:
                        bar_color = get_risk_color(cat_score)
                        cat_label = cat.replace("_", " ").title()
                        keywords_list = matched.get(cat, [])
                        kw_preview = ", ".join(keywords_list[:5])
                        cat_html += f"""
                        <div class="cat-bar-container">
                            <div class="cat-bar-label">
                                <span>{cat_label}</span>
                                <span style="color:{bar_color};">{cat_score:.0f}%</span>
                            </div>
                            <div class="cat-bar-track">
                                <div class="cat-bar-fill" style="width:{min(100,cat_score)}%; background:{bar_color}; box-shadow: 0 0 10px {bar_color};"></div>
                            </div>
                            <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">{kw_preview}</div>
                        </div>"""
                cat_html += "</div>"
                st.markdown(cat_html, unsafe_allow_html=True)
            else:
                st.info("No significant keywords matched.")

        # Semantic Analysis Breakdown
        with tab2:
            sem_details = results.get("semantic_details", {})
            intents = sem_details.get("detected_intents", [])
            sem_html = ""
            if intents:
                sem_html = '<div class="glass-card animate-in delay-2" style="padding: 1.2rem;">'
                for intent in intents:
                    conf = intent.get("confidence", 0)
                    bar_color = get_risk_color(conf)
                    intent_label = intent.get("intent", "").replace("_", " ").title()
                    match_text = intent.get("matched_sentence", "")
                    sem_html += f"""
                    <div class="cat-bar-container">
                        <div class="cat-bar-label">
                            <span style="font-weight:700;">{intent_label}</span>
                            <span style="color:{bar_color};">{conf:.1f}%</span>
                        </div>
                        <div class="cat-bar-track">
                            <div class="cat-bar-fill" style="width:{min(100, conf)}%; background:{bar_color}; box-shadow: 0 0 10px {bar_color};"></div>
                        </div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:6px; font-style:italic; padding-left:10px; border-left:2px solid {bar_color}40;">"{match_text}"</div>
                    </div>"""
                sem_html += "</div>"
                st.markdown(sem_html, unsafe_allow_html=True)
            else:
                st.info("No semantic intents detected.")

        # Social Engineering Breakdown
        with tab3:
            soc_details = results.get("social_details", {})
            tactics = soc_details.get("tactic_summary", {})
            soc_html = ""
            if any(v > 0 for v in tactics.values()):
                soc_html = '<div class="glass-card animate-in delay-3" style="padding: 1.2rem;"><div style="display:flex; flex-wrap:wrap; gap:10px;">'
                for tactic, count in tactics.items():
                    if count > 0:
                        tactic_label = tactic.replace("_", " ").title()
                        soc_html += f'<span class="indicator-pill" style="background:rgba(217,119,6,0.15); border-color:rgba(217,119,6,0.3); color:#fcd34d; margin:0; box-shadow:0 0 10px rgba(217,119,6,0.1);"><span style="font-size:1.1rem; vertical-align:middle; margin-right:4px;">🎭</span> {tactic_label} <span style="background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:10px; font-size:0.75rem; margin-left:4px;">x{count}</span></span>'
                soc_html += '</div></div>'
                st.markdown(soc_html, unsafe_allow_html=True)
            else:
                st.info("No social engineering tactics identified.")

    # Transcript display
    with st.expander("📄 View Full Transcript", expanded=False):
        st.markdown(
            f'<div class="transcript-box">{transcript_to_analyze}</div>',
            unsafe_allow_html=True,
        )

    # LLM summary if available
    if results.get("llm_analysis_summary"):
        with st.expander("🧠 LLM Analysis Details", expanded=False):
            st.markdown(results["llm_analysis_summary"])

else:
    # No input yet – show instructions
    st.markdown("---")
    st.markdown("""
    <div class="glass-card" style="text-align:center; padding:3rem 2rem;">
        <div style="font-size:3rem; margin-bottom:1rem;">🎙️</div>
        <div style="font-size:1.2rem; font-weight:600; color:#e2e8f0; margin-bottom:0.5rem;">
            Upload Audio or Paste a Transcript
        </div>
        <div style="font-size:0.9rem; color:#64748b; max-width:500px; margin:0 auto; line-height:1.6;">
            Upload a phone call recording for automatic transcription and scam analysis,
            or paste a conversation transcript directly. You can also try the quick demo buttons
            on the right to see the system in action.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # How it works section
    st.markdown("""
    <div class="glass-card">
        <div class="card-title">🤖 How It Works – 6-Layer AI Pipeline</div>
        <div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:0.8rem; text-align:center;">
            <div class="pipeline-icon-card">
                <div style="font-size:1.6rem; margin-bottom:0.4rem;">🎙️</div>
                <div style="font-size:0.75rem; font-weight:700; color:#e2e8f0;">Speech</div>
                <div style="font-size:0.65rem; color:#64748b;">Audio → Text</div>
            </div>
            <div class="pipeline-icon-card">
                <div style="font-size:1.6rem; margin-bottom:0.4rem;">🔍</div>
                <div style="font-size:0.75rem; font-weight:700; color:#e2e8f0;">Rules</div>
                <div style="font-size:0.65rem; color:#64748b;">Keyword Scan</div>
            </div>
            <div class="pipeline-icon-card">
                <div style="font-size:1.6rem; margin-bottom:0.4rem;">🧠</div>
                <div style="font-size:0.75rem; font-weight:700; color:#e2e8f0;">Semantic</div>
                <div style="font-size:0.65rem; color:#64748b;">Intent Match</div>
            </div>
            <div class="pipeline-icon-card">
                <div style="font-size:1.6rem; margin-bottom:0.4rem;">🎭</div>
                <div style="font-size:0.75rem; font-weight:700; color:#e2e8f0;">Social</div>
                <div style="font-size:0.65rem; color:#64748b;">Psych. Tactics</div>
            </div>
            <div class="pipeline-icon-card">
                <div style="font-size:1.6rem; margin-bottom:0.4rem;">🤖</div>
                <div style="font-size:0.75rem; font-weight:700; color:#e2e8f0;">LLM</div>
                <div style="font-size:0.65rem; color:#64748b;">Deep Reasoning</div>
            </div>
            <div class="pipeline-icon-card">
                <div style="font-size:1.6rem; margin-bottom:0.4rem;">📊</div>
                <div style="font-size:0.75rem; font-weight:700; color:#e2e8f0;">Scoring</div>
                <div style="font-size:0.65rem; color:#64748b;">Hybrid Index</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    st.markdown("""
    <div class="glass-card" style="padding:1.2rem 1.5rem;">
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:1rem; text-align:center;">
            <div>
                <div class="stat-number">150+</div>
                <div style="font-size:0.7rem; color:#64748b; margin-top:0.2rem;">Risk Keywords</div>
            </div>
            <div>
                <div class="stat-number">9</div>
                <div style="font-size:0.7rem; color:#64748b; margin-top:0.2rem;">Semantic Intents</div>
            </div>
            <div>
                <div class="stat-number">9</div>
                <div style="font-size:0.7rem; color:#64748b; margin-top:0.2rem;">Tactic Detectors</div>
            </div>
            <div>
                <div class="stat-number">4</div>
                <div style="font-size:0.7rem; color:#64748b; margin-top:0.2rem;">Risk Signals</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
