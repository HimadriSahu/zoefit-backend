#!/usr/bin/env python
"""
Test script to verify Groq works from the zoefit directory with the updated manage.py
"""

import os
import sys
import site

# Same logic as updated manage.py
venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv')
site_packages = os.path.join(venv_path, 'Lib', 'site-packages')
if os.path.exists(site_packages):
    site.addsitedir(site_packages)
    print(f"✅ Added venv site-packages: {site_packages}")
else:
    print(f"❌ Venv site-packages not found: {site_packages}")

print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")

# Test Groq import
try:
    import groq
    print("✅ Groq import: SUCCESS")
    print(f"Groq version: {getattr(groq, '__version__', 'unknown')}")
    print(f"Groq location: {groq.__file__}")
except ImportError as e:
    print(f"❌ Groq import: FAILED - {e}")

# Test Django setup
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
    import django
    django.setup()
    
    from ai_features.chatbot import GROQ_AVAILABLE
    print(f"✅ GROQ_AVAILABLE in chatbot: {GROQ_AVAILABLE}")
    
    if GROQ_AVAILABLE:
        print("🎉 Groq should now work from back\\zoefit directory!")
    else:
        print("❌ Still not working - need to check further")
        
except Exception as e:
    print(f"❌ Django test failed: {e}")
