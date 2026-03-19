"""
FraudSentinel – Pattern Library
Contains categorized scam phrases and variations for rule-based detection.
"""

SCAM_PATTERNS = {
    "otp_requests": [
        "share your otp",
        "tell me the otp",
        "give the verification code",
        "read the code you received",
        "six digit code",
        "four digit pin",
        "one time password",
        "verification number sent to your phone",
        "confirm the code",
        "do not share this code but tell me"
    ],
    
    "financial_requests": [
        "transfer money",
        "send payment",
        "upi payment required",
        "pay verification fee",
        "processing fee",
        "customs duty charge",
        "refundable deposit",
        "link your bank account",
        "credit card details",
        "cvv number",
        "wire the funds",
        "send via western union",
        "buy gift cards",
        "apple gift card",
        "google play cards"
    ],
    
    "authority_impersonation": [
        "this is the police",
        "calling from the irs",
        "fbi investigation",
        "customs officer",
        "federal reserve investigator",
        "from your bank's fraud department",
        "social security administration",
        "supreme court warrant",
        "tax enforcement agent",
        "calling from microsoft support",
        "amazon fraud team"
    ],
    
    "legal_threats": [
        "arrest warrant issued",
        "will be arrested",
        "legal action will be taken",
        "suspect in a money laundering case",
        "your ssn has been suspended",
        "bank account will be frozen",
        "police will arrive at your address",
        "face criminal charges",
        "property will be confiscated"
    ],
    
    "urgency_pressure": [
        "act immediately",
        "within a few minutes",
        "do it right now",
        "urgent verification required",
        "before it's too late",
        "time sensitive matter",
        "we need this done today",
        "don't hang up the phone",
        "stay on the line"
    ],
    
    "identity_verification": [
        "verify your identity",
        "confirm your full social security number",
        "need your date of birth for security",
        "confirm your mother's maiden name",
        "what is your zip code and account number",
        "to prove you are the account holder"
    ],
    
    "investment_promises": [
        "guaranteed returns",
        "double your money",
        "risk free investment",
        "exclusive crypto opportunity",
        "once in a lifetime deal",
        "high yield daily profits",
        "insider trading tip"
    ],

    "say_yes_scams": [
        "can you hear me",
        "are you the homeowner",
        "is this the head of the household",
        "just say yes to confirm",
        "answer yes if you can hear me"
    ],
    
    "account_threats": [
        "subscription will be canceled",
        "account locked for security reasons",
        "suspicious activity from your ip address",
        "update your card details",
        "your coverage will stop",
        "medicare will drop you"
    ],
    
    "isolation_tactics": [
        "don't tell anyone about this call",
        "do not tell your family",
        "keep this investigation a secret",
        "do not consult anyone",
        "move your money to protect it"
    ]
}
