#!/usr/bin/env python
"""
Simple API test to verify server connectivity
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Test if Django can start
    try:
        execute_from_command_line(['manage.py', 'check'])
        print("✅ Django setup successful")
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        sys.exit(1)
