import re
from typing import Dict, List

# Dictionary of manipulation tactics and regex patterns to match them
TACTIC_PATTERNS = {
    "urgency_pressure": [
        r"\b(act|do this)\s+(immediately|right now|quick)\b",
        r"\b(before|until)\s+(it's too late|the end of the day)\b",
        r"\b(time\s+is\s+running\s+out)\b",
        r"\b(you\s+only\s+have|limited\s+time)\b",
        r"\b(don't\s+hang\s+up)\b"
    ],
    "fear_tactics": [
        r"\b(arrest(ed)?|warrant|police|jail|prison)\b",
        r"\b(confiscate|suspend|freeze)\s+(your|the)\s+(account|assets|property)\b",
        r"\b(criminal|illegal)\s+(activity|charges)\b",
        r"\b(legal\s+action)\b",
        r"\b(lose\s+all\s+your\s+money)\b",
        r"\b(under\s+investigation)\b"
    ],
    "authority_exploitation": [
        r"\b(irs|fbi|cia|police\s+department|customs)\b",
        r"\b(officer|agent|inspector|detective)\s+[a-z]+\b",
        r"\b(federal\s+reserve|supreme\s+court)\b",
        r"\b(fraud\s+department|security\s+team)\b"
    ],
    "financial_temptation": [
        r"\b(guaranteed\s+returns|risk\s+free)\b",
        r"\b(double\s+your\s+money|make\s+thousands)\b",
        r"\b(won\s+the\s+(lottery|prize|sweepstakes))\b",
        r"\b(exclusive\s+opportunity)\b",
        r"\b(secret\s+investment)\b"
    ],
    "emotional_manipulation": [
        r"\b(trust\s+me|i'm\s+trying\s+to\s+help\s+you)\b",
        r"\b(you're\s+the\s+only\s+one)\b",
        r"\b(keep\s+this\s+secret)\b"
    ],
    "isolation_tactics": [
        r"\b(don't\s+tell|do\s+not\s+tell)\s+(anyone|your\s+family|the\s+bank|your\s+bank)\b",
        r"\b(keep\s+this\s+between\s+us)\b",
        r"\b(they\s+will\s+ask\s+questions)\b",
        r"\b(bank\s+employees\s+are\s+involved)\b"
    ],
    "tech_support_threats": [
        r"\b(hackers\s+have\s+access)\b",
        r"\b(your\s+ip\s+address\s+was\s+used)\b",
        r"\b(network\s+is\s+compromised)\b",
        r"\b(download\s+(anydesk|teamviewer|rustdesk|supremo))\b"
    ],
    "guilt_inducement": [
        r"\b(do\s+you\s+want\s+to\s+go\s+to\s+jail)\b",
        r"\b(you\s+are\s+wasting\s+my\s+time)\b",
        r"\b(if\s+you\s+don't\s+cooperate)\b",
        r"\b(we\s+are\s+trying\s+to\s+save\s+your\s+account)\b"
    ],
    "evasion_tactics": [
        r"\b(i\s+cannot\s+transfer\s+you\s+to\s+my\s+manager)\b",
        r"\b(this\s+is\s+a\s+secured\s+line)\b",
        r"\b(you\s+have\s+to\s+speak\s+with\s+me)\b"
    ]
}


class SocialEngineeringDetector:
    """Layer 4 - Detects psychological manipulation tactics in conversation."""
    
    def __init__(self):
        # Pre-compile the regex patterns for faster execution
        self.compiled_patterns = {}
        for tactic, patterns in TACTIC_PATTERNS.items():
            self.compiled_patterns[tactic] = [re.compile(p, re.IGNORECASE) for p in patterns]

    def analyze(self, transcript: str) -> Dict:
        """
        Analyze the transcript for social engineering patterns.
        """
        detected_tactics = []
        tactic_counts = {tactic: 0 for tactic in self.compiled_patterns}
        total_hits = 0

        for tactic, compiled_list in self.compiled_patterns.items():
            for pattern in compiled_list:
                matches = pattern.finditer(transcript)
                for match in matches:
                    total_hits += 1
                    tactic_counts[tactic] += 1
                    
                    # Store unique tactic findings
                    finding = {
                        "tactic": tactic,
                        "matched_text": match.group(0)
                    }
                    if finding not in detected_tactics:
                        detected_tactics.append(finding)

        # Calculate a normalized behavioral risk score (0-100)
        # 1 hit = 40, 2 hits = 65, 3 hits = 85, 4+ hits = 100
        score = 0.0
        if total_hits == 1:
            score = 40.0
        elif total_hits == 2:
            score = 65.0
        elif total_hits == 3:
            score = 85.0
        elif total_hits >= 4:
            score = 100.0

        return {
            "social_risk_score": score,
            "detected_tactics": detected_tactics,
            "tactic_summary": {k: v for k, v in tactic_counts.items() if v > 0}
        }
