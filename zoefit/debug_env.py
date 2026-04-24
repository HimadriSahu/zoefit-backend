#!/usr/bin/env python
"""
Debug script to check .env file loading
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths like in settings.py
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR.parent / '.env'

print("=== .ENV FILE DEBUG ===")
print(f"BASE_DIR: {BASE_DIR}")
print(f"env_path: {env_path}")
print(f"env_path.exists(): {env_path.exists()}")

if env_path.exists():
    print("✅ .env file found")
    
    # Load the .env file
    load_dotenv(env_path)
    
    # Check specific variables
    variables_to_check = [
        'SECRET_KEY',
        'OPENAI_API_KEY', 
        'GEMINI_API_KEY',
        'DEBUG',
        'DB_NAME'
    ]
    
    print("\nEnvironment Variables:")
    for var in variables_to_check:
        value = os.environ.get(var)
        if value:
            if var == 'SECRET_KEY':
                print(f"  {var}: ✅ Present (length: {len(value)})")
            elif 'API_KEY' in var:
                print(f"  {var}: ✅ Present (length: {len(value)}, format: {value[:10]}...{value[-10:] if len(value) > 20 else 'invalid'})")
            else:
                print(f"  {var}: ✅ Present ({value})")
        else:
            print(f"  {var}: ❌ Missing")
    
    # Show first few lines of .env file
    print(f"\nFirst 5 lines of .env file:")
    with open(env_path, 'r') as f:
        lines = f.readlines()[:5]
        for i, line in enumerate(lines, 1):
            print(f"  {i}: {line.strip()}")
else:
    print("❌ .env file not found")
    
    # Check if it exists in other locations
    possible_paths = [
        BASE_DIR / '.env',
        BASE_DIR.parent.parent / '.env',
        Path.cwd() / '.env'
    ]
    
    print("\nChecking other possible locations:")
    for path in possible_paths:
        print(f"  {path}: {'✅ Exists' if path.exists() else '❌ Not found'}")
