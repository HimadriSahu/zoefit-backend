#!/usr/bin/env python
"""
Simple test to verify onboarding endpoint works
"""

import requests
import json

# Test data
test_data = {
    "gender": "male",
    "height": 175.0,
    "weight": 70.0,
    "fitness_goal": "maintain",
    "activity_level": "moderate",
    "target_weight": 68.0,
    "dietary_preferences": {"diet_type": "omnivore"},
    "allergies": [],
    "medical_conditions": [],
}

# Test the endpoint
url = "http://127.0.0.1:8000/api/users/onboarding/"
headers = {
    "Content-Type": "application/json",
    # Note: This will fail without proper auth, but we can see the error
}

try:
    response = requests.post(url, json=test_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        print("✅ Endpoint exists but requires authentication (expected)")
    elif response.status_code == 200:
        print("✅ Onboarding endpoint working!")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
