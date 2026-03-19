"""
FraudSentinel – Agent 3 & Agent 4: Keyword Risk Agent & Risk Scoring Agent
Analyzes transcripts for risky keywords and computes composite fraud risk scores.
"""

from typing import Dict, List, Tuple
from utils import (
    RISK_KEYWORDS,
    SCAM_TYPE_PATTERNS,
    SCAM_TYPES,
    preprocess_text,
)


class KeywordRiskAgent:
    """
    Agent 3 – Keyword Risk Agent
    Scans transcript text for risky keywords/phrases and returns
    per-category match counts and a keyword-based risk score.
    """

    def analyze(self, transcript: str) -> Dict:
        """
        Analyze transcript for risky keywords.

        Returns:
            Dict with keys:
                - category_scores: dict of category → score (0–100)
                - matched_keywords: dict of category → list of matched keyword strings
                - total_keyword_score: overall keyword risk score (0–100)
                - keyword_count: total number of keyword matches
        """
        cleaned = preprocess_text(transcript)
        category_scores: Dict[str, float] = {}
        matched_keywords: Dict[str, List[str]] = {}
        total_weight = 0
        total_matches = 0

        for category, keywords in RISK_KEYWORDS.items():
            cat_weight = 0
            cat_matches = []

            for keyword, weight in keywords.items():
                # Count occurrences of each keyword in the transcript
                count = cleaned.count(keyword.lower())
                if count > 0:
                    cat_weight += weight * min(count, 3)  # cap at 3 occurrences
                    cat_matches.append(keyword)
                    total_matches += count

            # Normalize category score to 0–100
            max_possible = sum(w * 3 for w in keywords.values())
            cat_score = min(100, (cat_weight / max(max_possible * 0.15, 1)) * 100)

            category_scores[category] = round(cat_score, 1)
            matched_keywords[category] = cat_matches
            total_weight += cat_weight

        # Compute overall keyword risk score
        all_max = sum(sum(w * 3 for w in kw.values()) for kw in RISK_KEYWORDS.values())
        total_score = min(100, (total_weight / max(all_max * 0.05, 1)) * 100)

        return {
            "category_scores": category_scores,
            "matched_keywords": matched_keywords,
            "total_keyword_score": round(total_score, 1),
            "keyword_count": total_matches,
        }

    def get_top_categories(self, analysis: Dict, top_n: int = 3) -> List[Tuple[str, float]]:
        """Return top N categories by score."""
        scores = analysis["category_scores"]
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_cats[:top_n]


class RiskScoringAgent:
    """
    Agent 6 – Risk Scoring Agent
    Combines Rule, Semantic, Social Engineering, and LLM analysis into a
    4-signal composite score for maximum detection accuracy.

    Weights (with LLM):
        25% Rule-Based  |  25% Semantic  |  15% Social Engineering  |  35% LLM

    Weights (without LLM):
        35% Rule-Based  |  35% Semantic  |  30% Social Engineering
    """

    def __init__(
        self,
        rule_weight: float = 0.25,
        semantic_weight: float = 0.25,
        social_weight: float = 0.15,
        llm_weight: float = 0.35,
    ):
        self.rule_weight = rule_weight
        self.semantic_weight = semantic_weight
        self.social_weight = social_weight
        self.llm_weight = llm_weight

    def compute_score(
        self,
        keyword_analysis: Dict,
        semantic_analysis: Dict,
        llm_analysis: Dict,
        social_analysis: Dict = None,
    ) -> Dict:
        """
        Compute composite fraud risk score based on multi-layer signals.

        Args:
            keyword_analysis: Output from KeywordRiskAgent.analyze()
            semantic_analysis: Output from SemanticDetector.analyze()
            llm_analysis: Output from LLMDetector.analyze()
            social_analysis: Output from SocialEngineeringDetector.analyze()

        Returns:
            Dict with final_score, scam_type, component_scores
        """
        rule_score = keyword_analysis.get("total_keyword_score", 0.0)
        semantic_score = semantic_analysis.get("semantic_risk_score", 0.0)
        social_score = (social_analysis or {}).get("social_risk_score", 0.0)
        
        llm_available = llm_analysis.get("llm_success", False)
        llm_score = llm_analysis.get("llm_risk_score", 0.0)

        if llm_available:
            final_score = (
                self.rule_weight * rule_score
                + self.semantic_weight * semantic_score
                + self.social_weight * social_score
                + self.llm_weight * llm_score
            )
        else:
            # Without LLM, redistribute weights across the 3 remaining signals
            final_score = (
                0.35 * rule_score
                + 0.35 * semantic_score
                + 0.30 * social_score
            )

        final_score = min(100, max(0, round(final_score, 1)))

        # Determine scam type - prefer LLM if available, fallback to keyword heuristic
        scam_type = llm_analysis.get("scam_type", "Unknown")
        if not llm_available or scam_type in ["Unknown", "Analysis Failed", "Not a Scam"]:
            fallback_type = self._classify_scam_type(keyword_analysis)
            if fallback_type != "unknown":
                scam_type = SCAM_TYPES.get(fallback_type, "Unknown Fraud Pattern")

        return {
            "final_score": final_score,
            "scam_type": scam_type,
            "component_scores": {
                "rule_score": round(rule_score, 1),
                "semantic_score": round(semantic_score, 1),
                "social_score": round(social_score, 1),
                "llm_score": round(llm_score, 1) if llm_available else None,
            },
            "llm_used": llm_available,
        }

    def _compute_pattern_score(self, keyword_analysis: Dict) -> float:
        """Score based on how many distinct risk categories are triggered."""
        category_scores = keyword_analysis["category_scores"]
        active_cats = sum(1 for s in category_scores.values() if s > 10)
        total_cats = len(category_scores)

        # More active categories = higher pattern score
        breadth_score = (active_cats / max(total_cats, 1)) * 100

        # High concentration in any single category also raises concern
        max_cat_score = max(category_scores.values()) if category_scores else 0
        concentration_score = max_cat_score

        return min(100, (breadth_score * 0.4 + concentration_score * 0.6))

    def _classify_scam_type(self, keyword_analysis: Dict) -> str:
        """Determine the most likely scam type based on keyword category scores."""
        category_scores = keyword_analysis["category_scores"]

        best_type = "unknown"
        best_score = 0

        for scam_type, primary_cats in SCAM_TYPE_PATTERNS.items():
            type_score = sum(category_scores.get(cat, 0) for cat in primary_cats)

            # Bonus for specific secondary indicators
            if scam_type == "bank_otp":
                type_score += category_scores.get("urgency_pressure", 0) * 0.3
            elif scam_type == "courier":
                type_score += category_scores.get("impersonation", 0) * 0.3
                type_score += category_scores.get("emotional_manipulation", 0) * 0.2
            elif scam_type == "investment":
                type_score += category_scores.get("urgency_pressure", 0) * 0.2
            elif scam_type == "government":
                type_score += category_scores.get("emotional_manipulation", 0) * 0.3
                type_score += category_scores.get("urgency_pressure", 0) * 0.2
            elif scam_type == "tech_support":
                type_score += category_scores.get("urgency_pressure", 0) * 0.2
            elif scam_type == "lottery":
                if category_scores.get("otp_banking", 0) < 20:
                    type_score += 10  # boost if not banking-related

            if type_score > best_score:
                best_score = type_score
                best_type = scam_type

        # Only classify if there's meaningful signal
        if best_score < 15:
            return "unknown"

        return best_type
