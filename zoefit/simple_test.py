#!/usr/bin/env python
"""
Simple test to check API key availability
"""
import os
from dotenv import load_dotenv

# Load .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)

# Check if API keys are available in environment
openai_key = os.environ.get('OPENAI_API_KEY')
gemini_key = os.environ.get('GEMINI_API_KEY')

print("=== API KEY AVAILABILITY TEST ===")
print(f"OpenAI API Key: {'✅ Present' if openai_key else '❌ Missing'}")
if openai_key:
    print(f"  Length: {len(openai_key)}")
    print(f"  Format: {openai_key[:10]}...{openai_key[-10:] if len(openai_key) > 20 else 'invalid'}")
    print(f"  Starts with sk-: {openai_key.startswith('sk-')}")

print(f"Gemini API Key: {'✅ Present' if gemini_key else '❌ Missing'}")
if gemini_key:
    print(f"  Length: {len(gemini_key)}")
    print(f"  Format: {gemini_key[:10]}...{gemini_key[-10:] if len(gemini_key) > 20 else 'invalid'}")

# Check if .env file exists and load it
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
print(f"\n.env file path: {env_path}")
print(f".env file exists: {'✅ Yes' if os.path.exists(env_path) else '❌ No'}")

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        env_content = f.read()
        print(f".env file size: {len(env_content)} characters")
        if 'OPENAI_API_KEY=' in env_content:
            print("✅ OPENAI_API_KEY found in .env file")
        else:
            print("❌ OPENAI_API_KEY not found in .env file")
        if 'GEMINI_API_KEY=' in env_content:
            print("✅ GEMINI_API_KEY found in .env file")
        else:
            print("❌ GEMINI_API_KEY not found in .env file")
