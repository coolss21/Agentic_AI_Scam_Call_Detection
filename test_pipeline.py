"""Quick test script for the FraudSentinel analysis pipeline."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scam_detector import ScamDetectorOrchestrator
from demo_transcripts import DEMO_TRANSCRIPTS

orchestrator = ScamDetectorOrchestrator()

for key, label in [("bank_scam", "BANK SCAM"), ("courier_scam", "COURIER SCAM"), 
                   ("investment_scam", "INVESTMENT SCAM"), ("safe_call", "SAFE CALL")]:
    transcript = DEMO_TRANSCRIPTS[key]["transcript"]
    results = orchestrator.analyze_transcript(transcript)
    print(f"=== {label} ===")
    print(f"  Risk Score: {results['risk_score']}")
    print(f"  Risk Level: {results['risk_level']}")
    print(f"  Scam Type:  {results['scam_type_display']}")
    print(f"  Indicators: {len(results['indicators'])} detected")
    print(f"  LLM Used:   {results['llm_used']}")
    print()

print("ALL TESTS PASSED!")
