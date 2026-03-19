"""
FraudSentinel – Master Orchestrator
Coordinates the 6-layer AI fraud detection pipeline.
"""

from typing import Dict, Optional

from risk_engine import KeywordRiskAgent, RiskScoringAgent
from semantic_detector import SemanticDetector
from social_engineering_detector import SocialEngineeringDetector
from llm_detector import LLMDetector
from utils import get_risk_level


class ScamDetectorOrchestrator:
    """
    Master Orchestrator – Coordinates the 6-layer agentic pipeline.
    Layer 1: Preprocessing (handled internally before scoring)
    Layer 2: Rule-Based Detection
    Layer 3: Semantic Similarity Detection
    Layer 4: Social Engineering Detection
    Layer 5: LLM Reasoning Analysis
    Layer 6: Risk Scoring Engine
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openai/gpt-4o-mini",
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        # Layer 2 & 6: Rules and Scoring
        self.keyword_agent = KeywordRiskAgent()
        self.risk_agent = RiskScoringAgent()
        
        # Layer 3: Semantic Similarity
        self.semantic_agent = SemanticDetector()
        
        # Layer 4: Social Engineering
        self.social_agent = SocialEngineeringDetector()
        
        # Layer 5: LLM Analysis
        self.llm_agent = LLMDetector(api_key=api_key, model=model, base_url=base_url)

    def analyze_transcript(self, transcript: str, progress_callback=None) -> Dict:
        """
        Run the full 6-layer analysis pipeline on a transcript.
        """

        def update_progress(step, total, message):
            if progress_callback:
                progress_callback(step, total, message)

        # Ensure transcript is valid
        if not transcript or not transcript.strip():
            return {"error": "Empty transcript provided"}

        # Layer 2: Rule-based Detection
        update_progress(2, 6, "🔍 Layer 2: Rule-based keyword analysis...")
        keyword_analysis = self.keyword_agent.analyze(transcript)

        # Layer 3: Semantic Detection
        update_progress(3, 6, "🧠 Layer 3: Semantic intent similarity detection...")
        semantic_analysis = self.semantic_agent.analyze(transcript)

        # Layer 4: Social Engineering Detection
        update_progress(4, 6, "🎭 Layer 4: Analyzing social engineering tactics...")
        social_analysis = self.social_agent.analyze(transcript)

        # Layer 5: LLM Reasoning
        update_progress(5, 6, "🤖 Layer 5: Deep LLM reasoning via OpenRouter...")
        llm_analysis = self.llm_agent.analyze(transcript)

        # Layer 6: Risk Scoring
        update_progress(6, 6, "📊 Layer 6: Computing hybrid composite risk score...")
        risk_result = self.risk_agent.compute_score(
            keyword_analysis=keyword_analysis,
            semantic_analysis=semantic_analysis,
            llm_analysis=llm_analysis,
            social_analysis=social_analysis,
        )

        update_progress(6, 6, "✅ Analysis complete!")

        # Compile final unified results
        
        # Combine indicators from LLM and rules
        all_indicators = list(set(
            llm_analysis.get("indicators_detected", []) +
            [kw for cat_list in keyword_analysis.get("matched_keywords", {}).values() for kw in cat_list]
        ))
        
        # Combine tactics from LLM and Social Engineering modules
        all_tactics = list(set(
            llm_analysis.get("manipulation_tactics", []) +
            [t["tactic"] for t in social_analysis.get("detected_tactics", [])]
        ))

        score = risk_result["final_score"]
        risk_level = get_risk_level(score)
        
        severity = risk_level.lower()
        if severity == "low":
            recommendation = "This call appears safe, but always remain cautious about sharing personal information over the phone."
        elif severity == "medium":
            recommendation = "Be cautious with this caller. Do not share any personal, financial, or identity information until you can independently verify their identity."
        elif severity == "high":
            recommendation = "Do NOT share any sensitive information. Hang up immediately and report this number. If you've already shared information, contact your bank immediately."
        else:
            recommendation = "IMMEDIATELY hang up! Do NOT share any OTP, PIN, bank details, or personal information. Contact your bank's official helpline to secure your accounts. Report this to cyber crime authorities."
        
        return {
            "transcript": transcript,
            "risk_score": score,
            "risk_level": risk_level,
            "scam_type": risk_result["scam_type"],
            "scam_type_display": risk_result["scam_type"],
            "indicators": all_indicators,
            "tactics_used": all_tactics,
            "explanation": llm_analysis.get("explanation", ""),
            "recommendation": recommendation,
            "severity": severity,
            "component_scores": risk_result["component_scores"],
            "semantic_details": semantic_analysis,
            "social_details": social_analysis,
            "keyword_details": {
                "category_scores": keyword_analysis["category_scores"],
                "keyword_count": keyword_analysis["keyword_count"],
            },
            "llm_used": llm_analysis.get("llm_success", False),
        }
