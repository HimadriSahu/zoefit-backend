#!/usr/bin/env python
"""
Debug script to check Groq installation and path issues
"""

import os
import sys
import site

print("=" * 60)
print("GROQ PATH DEBUG")
print("=" * 60)

print(f"Current directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Add venv path (same as manage.py)
venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv')
site_packages = os.path.join(venv_path, 'Lib', 'site-packages')

print(f"\nVirtual environment path: {venv_path}")
print(f"Site-packages path: {site_packages}")
print(f"Site-packages exists: {os.path.exists(site_packages)}")

if os.path.exists(site_packages):
    print(f"Adding site-packages to path...")
    site.addsitedir(site_packages)
    print(f"✅ Added to Python path")

# Check sys.path
print(f"\nPython paths:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

# Try to import Groq
print(f"\nTesting Groq import...")
try:
    import groq
    print(f"✅ Groq imported successfully!")
    print(f"Groq location: {groq.__file__}")
    print(f"Groq version: {getattr(groq, '__version__', 'unknown')}")
    
    # Test Groq class
    print(f"Groq class: {groq.Groq}")
    
except ImportError as e:
    print(f"❌ Groq import failed: {e}")
    
    # Check if groq directory exists
    groq_dir = os.path.join(site_packages, 'groq') if os.path.exists(site_packages) else None
    if groq_dir:
        print(f"Groq directory exists: {os.path.exists(groq_dir)}")
        if os.path.exists(groq_dir):
            print(f"Groq directory contents: {os.listdir(groq_dir)}")

# Test Django setup
print(f"\nTesting Django setup...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
    import django
    django.setup()
    
    from ai_features.chatbot import GROQ_AVAILABLE
    print(f"GROQ_AVAILABLE in chatbot: {GROQ_AVAILABLE}")
    
    if GROQ_AVAILABLE:
        print("🎉 Groq should work!")
    else:
        print("❌ Groq still not available in chatbot")
        
except Exception as e:
    print(f"❌ Django setup failed: {e}")

print("=" * 60)
