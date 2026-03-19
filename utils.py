"""
FraudSentinel – Utility Module
Contains keyword dictionaries, scam type definitions, risk thresholds, and helpers.
"""

import re
from typing import Dict, List, Tuple

# ── Scam Type Definitions ──────────────────────────────────────────────────────

SCAM_TYPES = {
    "bank_otp": "Bank OTP Scam",
    "courier": "Courier Delivery Scam",
    "investment": "Investment Scam",
    "government": "Government Impersonation",
    "tech_support": "Tech Support Scam",
    "lottery": "Lottery Scam",
    "unknown": "Unknown Fraud Pattern",
}

# ── Risk Keyword Dictionaries (weighted) ───────────────────────────────────────
# Each category maps keyword/phrase → weight (1–5)

RISK_KEYWORDS: Dict[str, Dict[str, int]] = {
    "otp_banking": {
        "otp": 5,
        "one time password": 5,
        "one-time password": 5,
        "verification code": 4,
        "bank account": 4,
        "account number": 4,
        "credit card": 4,
        "debit card": 4,
        "cvv": 5,
        "pin number": 5,
        "pin code": 4,
        "atm pin": 5,
        "net banking": 4,
        "internet banking": 4,
        "mobile banking": 3,
        "upi": 4,
        "upi pin": 5,
        "transfer money": 4,
        "fund transfer": 4,
        "bank details": 4,
        "account details": 4,
        "ifsc": 3,
        "swift code": 3,
        "aadhaar": 4,
        "aadhar": 4,
        "pan card": 3,
        "pan number": 3,
        "kyc": 4,
        "kyc verification": 4,
        "update kyc": 5,
    },
    "urgency_pressure": {
        "urgent": 4,
        "immediately": 4,
        "right now": 4,
        "right away": 4,
        "hurry": 3,
        "quickly": 3,
        "as soon as possible": 3,
        "asap": 3,
        "time is running out": 5,
        "last chance": 5,
        "expires today": 5,
        "limited time": 4,
        "act now": 5,
        "don't delay": 4,
        "within 24 hours": 4,
        "within one hour": 5,
        "deadline": 3,
        "before it's too late": 5,
        "suspend": 4,
        "suspended": 4,
        "blocked": 4,
        "deactivate": 4,
        "deactivated": 4,
        "freeze": 4,
        "frozen": 4,
        "close your account": 5,
    },
    "impersonation": {
        "reserve bank": 5,
        "rbi": 5,
        "state bank": 4,
        "sbi": 4,
        "income tax": 4,
        "income tax department": 5,
        "police": 4,
        "cyber cell": 5,
        "cyber crime": 5,
        "customs": 4,
        "customs department": 5,
        "narcotics": 5,
        "enforcement directorate": 5,
        "cbi": 5,
        "government": 3,
        "government official": 5,
        "senior officer": 4,
        "bank manager": 4,
        "bank officer": 4,
        "calling from": 3,
        "this is from": 3,
        "department": 2,
        "authority": 3,
        "federal": 4,
        "irs": 5,
        "social security": 5,
        "microsoft support": 5,
        "apple support": 5,
        "tech support": 5,
        "customer care": 3,
        "helpdesk": 3,
    },
    "financial_manipulation": {
        "payment": 3,
        "pay now": 4,
        "send money": 4,
        "wire transfer": 5,
        "gift card": 5,
        "buy gift card": 5,
        "bitcoin": 4,
        "cryptocurrency": 4,
        "crypto wallet": 5,
        "investment opportunity": 5,
        "guaranteed returns": 5,
        "high returns": 5,
        "double your money": 5,
        "risk free": 5,
        "risk-free": 5,
        "no risk": 4,
        "profit": 3,
        "bonus": 3,
        "refund": 3,
        "cashback": 3,
        "compensation": 3,
        "claim your prize": 5,
        "won a prize": 5,
        "lottery": 5,
        "lucky winner": 5,
        "jackpot": 5,
        "inheritance": 5,
        "fee": 3,
        "processing fee": 4,
        "registration fee": 4,
        "tax amount": 3,
        "fine": 3,
        "penalty": 4,
    },
    "emotional_manipulation": {
        "arrest": 5,
        "arrested": 5,
        "warrant": 5,
        "arrest warrant": 5,
        "jail": 5,
        "prison": 5,
        "legal action": 5,
        "court case": 5,
        "lawsuit": 4,
        "criminal case": 5,
        "fir": 4,
        "complaint filed": 4,
        "illegal activity": 5,
        "money laundering": 5,
        "drug trafficking": 5,
        "don't tell anyone": 5,
        "keep this confidential": 5,
        "do not share": 4,
        "secret": 3,
        "between us": 4,
        "trust me": 4,
        "help me": 3,
        "emergency": 4,
        "accident": 3,
        "hospital": 3,
        "family member": 3,
        "your son": 4,
        "your daughter": 4,
    },
    "courier_delivery": {
        "parcel": 4,
        "package": 3,
        "courier": 4,
        "delivery": 3,
        "shipment": 4,
        "customs clearance": 5,
        "held at customs": 5,
        "seized": 5,
        "contraband": 5,
        "illegal substance": 5,
        "drugs found": 5,
        "passport found": 4,
        "fake documents": 5,
        "tracking number": 3,
        "delivery failed": 4,
        "undelivered": 3,
    },
    "tech_support": {
        "virus": 4,
        "malware": 4,
        "hacked": 5,
        "compromised": 4,
        "security breach": 5,
        "remote access": 5,
        "teamviewer": 5,
        "anydesk": 5,
        "download this app": 5,
        "install this software": 5,
        "screen share": 4,
        "computer problem": 3,
        "system error": 3,
        "license expired": 4,
        "subscription expired": 4,
    },
}

# ── Risk Thresholds ────────────────────────────────────────────────────────────

RISK_THRESHOLDS = {
    "low": (0, 30),
    "medium": (31, 60),
    "high": (61, 85),
    "critical": (86, 100),
}

# ── Scam Type Detection Patterns ──────────────────────────────────────────────

SCAM_TYPE_PATTERNS: Dict[str, List[str]] = {
    "bank_otp": ["otp_banking"],
    "courier": ["courier_delivery"],
    "investment": ["financial_manipulation"],
    "government": ["impersonation"],
    "tech_support": ["tech_support"],
    "lottery": ["financial_manipulation"],
}


# ── Helper Functions ───────────────────────────────────────────────────────────

def preprocess_text(text: str) -> str:
    """Lowercase and clean transcript text for analysis."""
    text = text.lower()
    text = re.sub(r"[^\w\s'-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_risk_level(score: float) -> str:
    """Return risk level label based on score."""
    for level, (low, high) in RISK_THRESHOLDS.items():
        if low <= score <= high:
            return level
    return "critical" if score > 100 else "low"


def get_risk_color(score: float) -> str:
    """Return a hex color for the risk score."""
    if score <= 30:
        return "#22C55E"  # green
    elif score <= 60:
        return "#F59E0B"  # amber
    elif score <= 85:
        return "#F97316"  # orange
    else:
        return "#EF4444"  # red


def get_risk_emoji(score: float) -> str:
    """Return an emoji for the risk level."""
    if score <= 30:
        return "✅"
    elif score <= 60:
        return "⚠️"
    elif score <= 85:
        return "🔶"
    else:
        return "🚨"


def format_scam_type(scam_type_key: str) -> str:
    """Convert scam type key to display name."""
    return SCAM_TYPES.get(scam_type_key, SCAM_TYPES["unknown"])
