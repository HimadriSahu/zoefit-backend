#!/usr/bin/env python
"""
Test script to verify frontend module installation.

This script tests basic functionality of the frontend module
to ensure all models, views, and utilities are working correctly.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
django.setup()

def test_models_import():
    """Test that all models can be imported."""
    try:
        from frontend.models import (
            WorkoutSession, ExerciseLog, ProgressSnapshot,
            Streak, MealLog, Achievement
        )
        print("✅ Models imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_views_import():
    """Test that views can be imported."""
    try:
        from frontend.views import (
            workout_sessions_view, workout_stats_view,
            progress_snapshots_view, streaks_view,
            meal_logs_view, dashboard_summary_view
        )
        print("✅ Views imported successfully")
        return True
    except ImportError as e:
        print(f"❌ View import failed: {e}")
        return False

def test_serializers_import():
    """Test that serializers can be imported."""
    try:
        from frontend.serializers import (
            WorkoutSessionSerializer, ExerciseLogSerializer,
            ProgressSnapshotSerializer, StreakSerializer,
            MealLogSerializer, AchievementSerializer
        )
        print("✅ Serializers imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Serializer import failed: {e}")
        return False

def test_utils_import():
    """Test that utilities can be imported."""
    try:
        from frontend.utils import (
            DateRange, ProgressCalculator, StreakManager,
            AchievementManager, DataExporter, AnalyticsHelper
        )
        print("✅ Utilities imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Utils import failed: {e}")
        return False

def test_urls_import():
    """Test that URL configuration can be imported."""
    try:
        from frontend.urls import urlpatterns
        print("✅ URLs imported successfully")
        return True
    except ImportError as e:
        print(f"❌ URL import failed: {e}")
        return False

def test_admin_import():
    """Test that admin configuration can be imported."""
    try:
        from frontend.admin import (
            WorkoutSessionAdmin, ExerciseLogAdmin,
            ProgressSnapshotAdmin, StreakAdmin,
            MealLogAdmin, AchievementAdmin
        )
        print("✅ Admin configuration imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Admin import failed: {e}")
        return False

def test_app_config():
    """Test that app configuration is working."""
    try:
        from frontend.apps import FrontendConfig
        config = FrontendConfig('frontend', None)
        print(f"✅ App configuration: {config.verbose_name}")
        return True
    except Exception as e:
        print(f"❌ App config failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Frontend Module Installation")
    print("=" * 50)
    
    tests = [
        test_models_import,
        test_views_import,
        test_serializers_import,
        test_utils_import,
        test_urls_import,
        test_admin_import,
        test_app_config,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Frontend module is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
