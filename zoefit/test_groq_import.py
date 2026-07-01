#!/usr/bin/env python
"""
Test script to debug Groq import exactly as Django would do it
"""

import os
import sys
import site

print("=" * 60)
print("GROQ IMPORT TEST - Exact Django Simulation")
print("=" * 60)

print(f"Current directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")

# Add virtual environment site-packages to Python path (exact same as manage.py)
venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv')
site_packages = os.path.join(venv_path, 'Lib', 'site-packages')

print(f"\nVenv path: {venv_path}")
print(f"Site-packages path: {site_packages}")
print(f"Site-packages exists: {os.path.exists(site_packages)}")

if os.path.exists(site_packages):
    print("Adding site-packages to path...")
    site.addsitedir(site_packages)
    print("✅ Added to path")
    
    # Check if groq is in site-packages
    groq_path = os.path.join(site_packages, 'groq')
    print(f"Groq directory: {groq_path}")
    print(f"Groq directory exists: {os.path.exists(groq_path)}")
    
    if os.path.exists(groq_path):
        print(f"Groq directory contents: {os.listdir(groq_path)}")

print(f"\nPython path after adding site-packages:")
for i, path in enumerate(sys.path[:5]):  # Show first 5 paths
    print(f"  {i}: {path}")

# Now test the exact import that chatbot.py does
print(f"\n" + "=" * 40)
print("TESTING EXACT IMPORT FROM CHATBOT.PY")
print("=" * 40)

print("Trying: from groq import Groq")
try:
    from groq import Groq
    GROQ_AVAILABLE = True
    print("✅ SUCCESS: from groq import Groq")
    print(f"Groq class: {Groq}")
    print(f"Groq location: {Groq.__module__}")
except ImportError as e:
    GROQ_AVAILABLE = False
    Groq = None
    print(f"❌ FAILED: from groq import Groq")
    print(f"Error: {e}")

print(f"\nGROQ_AVAILABLE = {GROQ_AVAILABLE}")

# Test Django setup
print(f"\n" + "=" * 40)
print("TESTING DJANGO SETUP")
print("=" * 40)

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
    import django
    django.setup()
    print("✅ Django setup successful")
    
    # Now test the chatbot import
    print("\nTesting chatbot import...")
    from ai_features.chatbot import EnhancedAIChatbot, GROQ_AVAILABLE as chatbot_groq
    print(f"Chatbot GROQ_AVAILABLE: {chatbot_groq}")
    
    # Test initialization
    print("\nTesting chatbot initialization...")
    chatbot = EnhancedAIChatbot(ai_provider="groq")
    if chatbot.groq_client:
        print("✅ Chatbot Groq client initialized!")
    else:
        print("❌ Chatbot Groq client not initialized")
        
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
