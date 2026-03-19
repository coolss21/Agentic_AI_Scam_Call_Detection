import re
from typing import Dict, List, Tuple
from loguru import logger

try:
    from sentence_transformers import SentenceTransformer, util
    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False


# High-risk semantic intents commonly found in scam calls
SCAM_INTENTS = {
    "otp_request": [
        "I need you to tell me the one time password",
        "Please read the six digit verification code sent to your phone",
        "Share the security code from the text message"
    ],
    "financial_transfer": [
        "You need to transfer the funds to this secure account",
        "Send the money using a wire transfer immediately",
        "Please complete the UPI payment to verify your identity"
    ],
    "gift_card_payment": [
        "Go to the store and buy Apple gift cards",
        "We need payment in the form of Google Play cards",
        "Purchase gift cards to pay the fine"
    ],
    "authority_threat": [
        "This is the police and an arrest warrant has been issued",
        "We are from the IRS and you will face legal action",
        "Your social security number is suspended due to illegal activity"
    ],
    "fake_investment": [
        "This is a risk free investment with guaranteed high returns",
        "Double your crypto investment in just a few days",
        "Exclusive opportunity to make daily profits"
    ],
    "remote_access": [
        "Download AnyDesk so I can help fix your computer",
        "Install TeamViewer to let me connect to your device",
        "I need remote access to your screen to process the refund"
    ],
    "say_yes_fishing": [
        "Can you hear me clearly?",
        "Are you the person who owns this house?",
        "Please answer yes to verify your identity."
    ],
    "isolation_demand": [
        "Do not tell your family members about this transfer.",
        "Keep this investigation a secret.",
        "If you tell anyone you will be arrested."
    ],
    "account_compromise_threat": [
        "Your account has been locked due to suspicious activity.",
        "Your subscription will be canceled today.",
        "Your IP address was flagged for illegal activity."
    ]
}

_GLOBAL_MODEL_CACHE = {}

class SemanticDetector:
    """Layer 3 - Detects semantic similarity between the transcript and known scam intents."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", threshold: float = 0.65):
        self.threshold = threshold
        self.is_available = _MODULE_AVAILABLE
        self.model = None
        self.intent_embeddings = {}
        
        if self.is_available:
            self._load_model_and_intents(model_name)
        else:
            logger.warning("sentence-transformers not installed. Semantic detection disabled.")

    def _load_model_and_intents(self, model_name: str):
        global _GLOBAL_MODEL_CACHE
        if model_name in _GLOBAL_MODEL_CACHE:
            self.model = _GLOBAL_MODEL_CACHE[model_name]["model"]
            self.intent_embeddings = _GLOBAL_MODEL_CACHE[model_name]["intent_embeddings"]
            return

        try:
            logger.info("Loading Semantic Detector model...")
            self.model = SentenceTransformer(model_name)
            
            # Precompute embeddings for all intent variations
            for intent_name, phrases in SCAM_INTENTS.items():
                self.intent_embeddings[intent_name] = self.model.encode(phrases, convert_to_tensor=True)
                
            _GLOBAL_MODEL_CACHE[model_name] = {
                "model": self.model,
                "intent_embeddings": self.intent_embeddings
            }
            logger.info("Semantic Detector ready.")
        except Exception as e:
            logger.error(f"Failed to load Semantic Detector: {e}")
            self.is_available = False

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split transcript into sentences for granular comparison."""
        # Simple regex splitting by punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]

    def analyze(self, transcript: str) -> Dict:
        """
        Analyze transcript for semantic similarity to scam intents.
        Returns a dictionary with score and detailed matches.
        """
        if not self.is_available or not transcript.strip() or not self.model:
            return {
                "semantic_risk_score": 0.0,
                "detected_intents": [],
                "highest_similarity": 0.0
            }

        sentences = self._split_into_sentences(transcript)
        if not sentences:
            # Fallback to whole transcript if no punctuation
            sentences = [transcript]

        transcript_embeddings = self.model.encode(sentences, convert_to_tensor=True)
        
        detected_intents = []
        max_similarity_overall = 0.0
        
        # Compare transcript sentences against all scam intents
        for intent_name, intent_embs in self.intent_embeddings.items():
            # Compute cosine similarity between all sentences and all phrases in this intent
            cosine_scores = util.cos_sim(transcript_embeddings, intent_embs)
            
            # Find the max similarity for this intent
            max_score = float(cosine_scores.max())
            max_similarity_overall = max(max_similarity_overall, max_score)
            
            if max_score >= self.threshold:
                # Find which sentence triggered this (optional detailed breakdown)
                sentence_idx = int(cosine_scores.argmax() // len(intent_embs))
                matched_sentence = sentences[sentence_idx]
                
                detected_intents.append({
                    "intent": intent_name,
                    "confidence": round(max_score * 100, 1),
                    "matched_sentence": matched_sentence
                })

        # Calculate a semantic score (out of 100) based on max similarity and number of distinct intents
        # Max out at 100.
        semantic_score = 0.0
        if detected_intents:
            base_score = max_similarity_overall * 100
            # Add a small bonus for multiple different fraud intents detected
            bonus = (len(detected_intents) - 1) * 10
            semantic_score = min(100.0, base_score + bonus)

        return {
            "semantic_risk_score": round(semantic_score, 1),
            "detected_intents": detected_intents,
            "highest_similarity": round(max_similarity_overall * 100, 1)
        }
