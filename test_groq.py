"""
Quick test to verify GROQ_API_KEY is set and Groq API is reachable.
Run: python test_groq.py
"""
import os
import sys

api_key = os.environ.get("GROQ_API_KEY", "")

print("=" * 50)
print("Groq API Connectivity Test")
print("=" * 50)

if not api_key:
    print("[FAIL] GROQ_API_KEY environment variable is NOT set or is empty.")
    print("       Set it with:  set GROQ_API_KEY=gsk_xxxxxxxxxxxx")
    sys.exit(1)

print(f"[OK]   GROQ_API_KEY found (starts with: {api_key[:8]}...)")

try:
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Say: API connection successful"}],
        model="llama-3.3-70b-versatile",
        max_tokens=20
    )
    reply = response.choices[0].message.content.strip()
    print(f"[OK]   API responded: {reply}")
    print("=" * 50)
    print("SUCCESS: Groq API is working correctly!")
    print("=" * 50)
except Exception as e:
    print(f"[FAIL] API call failed: {e}")
    print("       Check your API key at: https://console.groq.com/keys")
    sys.exit(1)
