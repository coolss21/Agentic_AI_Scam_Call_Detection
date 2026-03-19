import os
import json
from typing import Dict, Optional, Tuple
from loguru import logger

class LLMDetector:
    """Layer 5 - Uses OpenRouter LLM to analyze the transcript and return structured structured logic."""
    
    def __init__(self, model: str = "openai/gpt-4o-mini", api_key: Optional[str] = None, base_url: str = "https://openrouter.ai/api/v1"):
        # Try both variants for OpenRouter API Key
        raw_keys = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPEN_ROUTER_API_KEY") or ""
        self.api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        self.current_key_idx = 0
        self.model = model
        self.base_url = base_url
        self.is_available = len(self.api_keys) > 0
        self.client = None
        
        if self.is_available:
            self._init_client()
        else:
            logger.warning("No OpenRouter API key found. LLM reasoning disabled.")

    def _init_client(self):
        try:
            from openai import OpenAI
            current_key = self.api_keys[self.current_key_idx]
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=current_key,
            )
            logger.info(f"LLM Detector initialized with model: {self.model} using key index: {self.current_key_idx}")
        except ImportError:
            logger.error("openai package is not installed. LLM reasoning disabled.")
            self.is_available = False
        except Exception as e:
            logger.error(f"Failed to intialize LLM client: {e}")
            self.is_available = False

    def analyze(self, transcript: str) -> Dict:
        """
        Analyze the transcript using LLM and return structured JSON output.
        """
        if not self.is_available or not self.client:
            return {
                "llm_risk_score": 0.0,
                "scam_type": "Unknown",
                "indicators_detected": [],
                "manipulation_tactics": [],
                "explanation": "LLM Analysis unavailable. Relying on Rule-based and Semantic scoring.",
                "llm_success": False
            }

        prompt = f"""
        Analyze this phone call transcript and determine whether it represents a scam attempt.
        Look for:
        1. financial fraud indicators
        2. requests for sensitive information (e.g., OTP, SSN)
        3. authority impersonation
        4. social engineering tactics (urgency, fear)
        5. payment demands
        
        Transcript:
        \"\"\"{transcript}\"\"\"
        
        Return your analysis strict JSON format matching exactly this structure:
        {{
            "scam_probability": <integer 0 to 100>,
            "scam_type": "<string classifying the scam, e.g., 'Bank OTP Scam', 'Tech Support Scam', or 'Not a Scam'>",
            "indicators_detected": ["<list of specific strings/phrases identified as malicious>"],
            "manipulation_tactics": ["<list of strings describing tactics used, e.g., 'Urgency', 'Authority exploitation'>"],
            "explanation": "<2-3 clear sentences explaining the reasoning behind this assessment>"
        }}
        """

        max_retries = min(3, len(self.api_keys))  # Don't retry more times than we have keys (optimistically) or 3 times max
        attempts = 0
        
        while attempts <= max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert fraud detection AI. Output strictly valid JSON without markdown wrapping."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Low temp for more deterministic, JSON-compliant output
                    max_tokens=800,   # Added to prevent 402 Insufficient Credit errors caused by massive default max_tokens
                )

                raw_content = response.choices[0].message.content.strip()
                # Clean up potential markdown formatting from the response
                if raw_content.startswith("```json"):
                    raw_content = raw_content[7:]
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3]
                
                result = json.loads(raw_content)

                return {
                    "llm_risk_score": float(result.get("scam_probability", 0.0)),
                    "scam_type": result.get("scam_type", "Unknown"),
                    "indicators_detected": result.get("indicators_detected", []),
                    "manipulation_tactics": result.get("manipulation_tactics", []),
                    "explanation": result.get("explanation", "No explanation provided."),
                    "llm_success": True
                }

            except Exception as e:
                logger.error(f"[LLMDetector] Attempt {attempts + 1} failed with key index {self.current_key_idx}: {e}")
                attempts += 1
                
                if attempts <= max_retries:
                    # Rotate the key and try again
                    self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
                    logger.info(f"[LLMDetector] Rotating to key index {self.current_key_idx}")
                    self._init_client()
                    
                    import time
                    time.sleep(1) # Small delay before retry
                else:
                    logger.error(f"[LLMDetector] All {attempts} retries exhausted.")
                    return {
                        "llm_risk_score": 0.0,
                        "scam_type": "Analysis Failed",
                        "indicators_detected": [],
                        "manipulation_tactics": [],
                        "explanation": f"LLM failed to process after {attempts} attempts. Last error: {str(e)}",
                        "llm_success": False
                    }
