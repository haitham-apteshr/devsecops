"""
Quick test to verify GROQ_API_KEY is set and Groq API is reachable.
Run: python test_groq.py
"""
import sys

from ai_utils import validate_api_key

print("=" * 50)
print("Groq API Connectivity Test")
print("=" * 50)

ok, message = validate_api_key()
if ok:
    print(f"[OK]   API responded: {message}")
    print("=" * 50)
    print("SUCCESS: Groq API is working correctly!")
    print("=" * 50)
else:
    print(f"[FAIL] {message}")
    print("       Set GROQ_API_KEY or add Jenkins credential: groq-api-key")
    print("       https://console.groq.com/keys")
    sys.exit(1)
