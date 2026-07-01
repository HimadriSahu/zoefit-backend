#!/usr/bin/env python
"""
Test script to verify Groq chat functionality is working
"""

import os
import sys
import site

# Add venv site-packages like manage.py
venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv')
site_packages = os.path.join(venv_path, 'Lib', 'site-packages')
if os.path.exists(site_packages):
    site.addsitedir(site_packages)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
import django
django.setup()

# Test the AI chat functionality
try:
    from ai_features.chatbot import EnhancedAIChatbot
    print("Testing AI chat with Groq...")
    
    # Initialize chatbot
    chatbot = EnhancedAIChatbot()
    
    # Test a simple message
    response = chatbot.process_message('Hello, this is a test message')
    
    print(f"✅ AI Response received")
    print(f"Provider: {response.get('ai_provider', 'unknown')}")
    print(f"Confidence: {response.get('confidence', 'unknown')}")
    print(f"Intent: {response.get('intent', 'unknown')}")
    print(f"Response: {response.get('response', 'No response')[:100]}...")
    
    if response.get('ai_provider') == 'groq':
        print("🎉 GROQ IS WORKING!")
    else:
        print(f"⚠️  Using fallback: {response.get('ai_provider')}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
