"""
FraudSentinel – Agentic AI Module
Defines the agent interfaces and the multi-agent pipeline orchestration.

This module serves as the central registry for all agents and provides
a clean API for the Streamlit app to interact with the agent pipeline.
"""

from typing import Dict, Optional, Callable
from speech_to_text import SpeechAgent
from scam_detector import ScamDetectorOrchestrator
from risk_engine import KeywordRiskAgent, RiskScoringAgent
from semantic_detector import SemanticDetector
from social_engineering_detector import SocialEngineeringDetector
from llm_detector import LLMDetector


class AgentRegistry:
    """
    Central registry and factory for all FraudSentinel agents.
    Provides a unified interface to create and manage the 6-layer agent pipeline.
    """

    AGENT_INFO = {
        "speech_agent": {
            "name": "Speech-to-Text Agent",
            "role": "Converts uploaded audio into text using Faster-Whisper",
            "icon": "🎙️",
            "order": 1,
        },
        "keyword_risk_agent": {
            "name": "Rule-Based Detection Agent",
            "role": "Scans for risky keywords commonly used in scam calls",
            "icon": "🔍",
            "order": 2,
        },
        "semantic_agent": {
            "name": "Semantic Similarity Agent",
            "role": "Detects matching fraud intents using sentence-transformers",
            "icon": "🧠",
            "order": 3,
        },
        "social_agent": {
            "name": "Social Engineering Agent",
            "role": "Identifies psychological manipulation tactics",
            "icon": "🎭",
            "order": 4,
        },
        "llm_agent": {
            "name": "LLM Reasoning Agent",
            "role": "Deep analysis using OpenRouter to evaluate context",
            "icon": "🤖",
            "order": 5,
        },
        "risk_scoring_agent": {
            "name": "Risk Scoring Engine",
            "role": "Combines signals into a 30/30/40 weighted hybrid score",
            "icon": "📊",
            "order": 6,
        },
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openai/gpt-4o-mini",
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

        # Layer 1 acts outside the core pipeline (called directly)
        self.speech_agent = SpeechAgent()
        
        # Instantiate orchestrator (which spins up Layers 2-6)
        self.orchestrator = ScamDetectorOrchestrator(
            api_key=api_key, model=model, base_url=base_url
        )

    def get_agent_list(self):
        """Return ordered list of agent info dicts."""
        return sorted(self.AGENT_INFO.values(), key=lambda x: x["order"])

    def transcribe_audio(self, audio_bytes: bytes, file_ext: str = ".wav"):
        """Run Agent 1: Speech-to-text."""
        return self.speech_agent.transcribe(audio_bytes, file_ext)

    def analyze_transcript(
        self, transcript: str, progress_callback: Optional[Callable] = None
    ) -> Dict:
        """Run the full multi-agent analysis pipeline."""
        return self.orchestrator.analyze_transcript(transcript, progress_callback)

    @property
    def llm_available(self) -> bool:
        """Check if LLM-based analysis is available."""
        return self.orchestrator.llm_agent.is_available

    @property
    def speech_available(self) -> bool:
        """Check if speech-to-text is available."""
        return self.speech_agent.is_available
