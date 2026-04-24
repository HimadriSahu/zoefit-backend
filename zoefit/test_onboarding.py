#!/usr/bin/env python
"""
Test script to debug onboarding endpoint issues
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from users.views import onboarding_view
from users.models import UserProfile
import json

User = get_user_model()

def test_onboarding():
    print("Testing onboarding endpoint...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Create test profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'gender': 'male',
            'height': 175.0,
            'weight': 70.0,
            'fitness_goal': 'maintain',
            'activity_level': 'moderate',
        }
    )
    
    # Create mock request
    factory = RequestFactory()
    onboarding_data = {
        'gender': 'male',
        'height': 175.0,
        'weight': 70.0,
        'fitness_goal': 'maintain',
        'activity_level': 'moderate',
        'target_weight': 68.0,
        'dietary_preferences': {'diet_type': 'omnivore'},
        'allergies': [],
        'medical_conditions': [],
    }
    
    request = factory.post(
        '/api/users/onboarding/',
        data=json.dumps(onboarding_data),
        content_type='application/json'
    )
    request.user = user
    
    try:
        response = onboarding_view(request)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        print("Onboarding test successful!")
    except Exception as e:
        print(f"Error during onboarding test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_onboarding()
