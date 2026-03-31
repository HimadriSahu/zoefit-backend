"""
Nutrition module views for ZoeFit

This module handles all nutrition-related API endpoints:
- Meal plan generation and management
- Dietary preferences and restrictions
- Nutrition tracking and logging
- Nutrition progress and analytics

These views are specifically focused on nutrition functionality
and provide clean separation from workout features.
"""

import json
from datetime import date, timedelta, datetime
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import MealPlan, DietaryPreferences, NutritionLog, NutritionProgress, FoodDatabase
from ai_features.models import HealthMetrics
from ai_features.ai_engine import AIRecommendationEngine


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_meal_plan(request):
    """
    Generate AI-powered meal plan based on user's health metrics and preferences.
    """
    try:
        user = request.user
        target_date = request.data.get('date', date.today())
        
        # Get user's health metrics
        metrics = get_object_or_404(HealthMetrics, user=user)
        
        # Get user's dietary preferences
        try:
            dietary_prefs = DietaryPreferences.objects.get(user=user)
        except DietaryPreferences.DoesNotExist:
            dietary_prefs = DietaryPreferences.objects.create(user=user)
        
        # Check if meal plan already exists for this date
        existing_plan = MealPlan.objects.filter(user=user, date=target_date).first()
        if existing_plan:
            return Response({
                'message': 'Meal plan already exists for this date',
                'meal_plan': {
                    'id': existing_plan.id,
                    'date': existing_plan.date,
                    'meals': existing_plan.meals,
                    'total_calories': existing_plan.total_calories,
                    'protein': existing_plan.protein,
                    'carbs': existing_plan.carbs,
                    'fat': existing_plan.fat
                }
            }, status=status.HTTP_200_OK)
        
        # Generate meal plan using AI engine
        ai_engine = AIRecommendationEngine()
        meal_plan_data = ai_engine.generate_meal_plan(metrics, target_date, dietary_prefs)
        
        # Create meal plan record
        meal_plan = MealPlan.objects.create(
            user=user,
            date=target_date,
            meals=meal_plan_data['meals'],
            total_calories=meal_plan_data['total_calories'],
            protein=meal_plan_data['protein'],
            carbs=meal_plan_data['carbs'],
            fat=meal_plan_data['fat'],
            confidence_score=meal_plan_data['confidence_score']
        )
        
        return Response({
            'message': 'Meal plan generated successfully',
            'meal_plan': {
                'id': meal_plan.id,
                'date': meal_plan.date,
                'meals': meal_plan.meals,
                'total_calories': meal_plan.total_calories,
                'protein': meal_plan.protein,
                'carbs': meal_plan.carbs,
                'fat': meal_plan.fat,
                'confidence_score': meal_plan.confidence_score
            }
        }, status=status.HTTP_201_CREATED)
        
    except HealthMetrics.DoesNotExist:
        return Response({
            'error': 'Health metrics not found. Please create your health profile first.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Something went wrong while generating meal plan: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_meal_plans(request):
    """
    Get user's meal plans for a date range.
    """
    try:
        start_date = request.GET.get('start_date', date.today() - timedelta(days=7))
        end_date = request.GET.get('end_date', date.today() + timedelta(days=7))
        
        meal_plans = MealPlan.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        plans_data = []
        for plan in meal_plans:
            plans_data.append({
                'id': plan.id,
                'date': plan.date,
                'meals': plan.meals,
                'total_calories': plan.total_calories,
                'protein': plan.protein,
                'carbs': plan.carbs,
                'fat': plan.fat,
                'fiber': plan.fiber,
                'sugar': plan.sugar,
                'sodium': plan.sodium,
                'user_rating': plan.user_rating,
                'user_feedback': plan.user_feedback
            })
        
        return Response({
            'meal_plans': plans_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while fetching meal plans: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_dietary_preferences(request):
    """
    Save user's dietary preferences for AI personalization.
    """
    try:
        user = request.user
        
        preferences, created = DietaryPreferences.objects.get_or_create(
            user=user,
            defaults={
                'diet_type': request.data.get('diet_type', 'omnivore'),
                'restrictions': request.data.get('restrictions', []),
                'allergies': request.data.get('allergies', []),
                'disliked_foods': request.data.get('disliked_foods', []),
                'preferred_foods': request.data.get('preferred_foods', []),
                'meals_per_day': request.data.get('meals_per_day', 3),
                'snack_frequency': request.data.get('snack_frequency', 'sometimes'),
                'target_calories': request.data.get('target_calories'),
                'macro_split': request.data.get('macro_split', {'protein': 30, 'carbs': 40, 'fat': 30})
            }
        )
        
        if not created:
            preferences.diet_type = request.data.get('diet_type', preferences.diet_type)
            preferences.restrictions = request.data.get('restrictions', preferences.restrictions)
            preferences.allergies = request.data.get('allergies', preferences.allergies)
            preferences.disliked_foods = request.data.get('disliked_foods', preferences.disliked_foods)
            preferences.preferred_foods = request.data.get('preferred_foods', preferences.preferred_foods)
            preferences.meals_per_day = request.data.get('meals_per_day', preferences.meals_per_day)
            preferences.snack_frequency = request.data.get('snack_frequency', preferences.snack_frequency)
            preferences.target_calories = request.data.get('target_calories', preferences.target_calories)
            preferences.macro_split = request.data.get('macro_split', preferences.macro_split)
            preferences.save()
        
        return Response({
            'message': 'Dietary preferences saved successfully',
            'preferences': {
                'diet_type': preferences.diet_type,
                'restrictions': preferences.restrictions,
                'allergies': preferences.allergies,
                'disliked_foods': preferences.disliked_foods,
                'preferred_foods': preferences.preferred_foods,
                'meals_per_day': preferences.meals_per_day,
                'snack_frequency': preferences.snack_frequency,
                'target_calories': preferences.target_calories,
                'macro_split': preferences.macro_split
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while saving dietary preferences: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dietary_preferences(request):
    """
    Get user's dietary preferences.
    """
    try:
        preferences = get_object_or_404(DietaryPreferences, user=request.user)
        
        return Response({
            'diet_type': preferences.diet_type,
            'restrictions': preferences.restrictions,
            'allergies': preferences.allergies,
            'disliked_foods': preferences.disliked_foods,
            'preferred_foods': preferences.preferred_foods,
            'meals_per_day': preferences.meals_per_day,
            'snack_frequency': preferences.snack_frequency,
            'target_calories': preferences.target_calories,
            'macro_split': preferences.macro_split
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while fetching dietary preferences: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_nutrition(request):
    """
    Log user's daily nutrition intake.
    """
    try:
        user = request.user
        log_date = request.data.get('date', date.today())
        
        nutrition_log, created = NutritionLog.objects.get_or_create(
            user=user,
            date=log_date,
            defaults={
                'breakfast': request.data.get('breakfast', []),
                'lunch': request.data.get('lunch', []),
                'dinner': request.data.get('dinner', []),
                'snacks': request.data.get('snacks', []),
                'total_calories': request.data.get('total_calories', 0),
                'total_protein': request.data.get('total_protein', 0),
                'total_carbs': request.data.get('total_carbs', 0),
                'total_fat': request.data.get('total_fat', 0),
                'water_intake_ml': request.data.get('water_intake_ml', 0),
                'notes': request.data.get('notes', '')
            }
        )
        
        if not created:
            nutrition_log.breakfast = request.data.get('breakfast', nutrition_log.breakfast)
            nutrition_log.lunch = request.data.get('lunch', nutrition_log.lunch)
            nutrition_log.dinner = request.data.get('dinner', nutrition_log.dinner)
            nutrition_log.snacks = request.data.get('snacks', nutrition_log.snacks)
            nutrition_log.total_calories = request.data.get('total_calories', nutrition_log.total_calories)
            nutrition_log.total_protein = request.data.get('total_protein', nutrition_log.total_protein)
            nutrition_log.total_carbs = request.data.get('total_carbs', nutrition_log.total_carbs)
            nutrition_log.total_fat = request.data.get('total_fat', nutrition_log.total_fat)
            nutrition_log.water_intake_ml = request.data.get('water_intake_ml', nutrition_log.water_intake_ml)
            nutrition_log.notes = request.data.get('notes', nutrition_log.notes)
            nutrition_log.save()
        
        return Response({
            'message': 'Nutrition log saved successfully',
            'nutrition_log': {
                'date': nutrition_log.date,
                'breakfast': nutrition_log.breakfast,
                'lunch': nutrition_log.lunch,
                'dinner': nutrition_log.dinner,
                'snacks': nutrition_log.snacks,
                'total_calories': nutrition_log.total_calories,
                'total_protein': nutrition_log.total_protein,
                'total_carbs': nutrition_log.total_carbs,
                'total_fat': nutrition_log.total_fat,
                'water_intake_ml': nutrition_log.water_intake_ml,
                'notes': nutrition_log.notes
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while logging nutrition: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_nutrition_logs(request):
    """
    Get user's nutrition logs for a date range.
    """
    try:
        start_date = request.GET.get('start_date', date.today() - timedelta(days=7))
        end_date = request.GET.get('end_date', date.today())
        
        nutrition_logs = NutritionLog.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        logs_data = []
        for log in nutrition_logs:
            logs_data.append({
                'id': log.id,
                'date': log.date,
                'breakfast': log.breakfast,
                'lunch': log.lunch,
                'dinner': log.dinner,
                'snacks': log.snacks,
                'total_calories': log.total_calories,
                'total_protein': log.total_protein,
                'total_carbs': log.total_carbs,
                'total_fat': log.total_fat,
                'water_intake_ml': log.water_intake_ml,
                'notes': log.notes
            })
        
        return Response({
            'nutrition_logs': logs_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while fetching nutrition logs: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_nutrition_progress(request):
    """
    Get user's nutrition progress and health metrics.
    """
    try:
        progress_data = NutritionProgress.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]  # Last 10 entries
        
        progress_list = []
        for progress in progress_data:
            progress_list.append({
                'id': progress.id,
                'weight': progress.weight,
                'meal_plan_adherence': progress.meal_plan_adherence,
                'calorie_consistency': progress.calorie_consistency,
                'macro_balance_score': progress.macro_balance_score,
                'nutrition_score': progress.nutrition_score,
                'created_at': progress.created_at
            })
        
        return Response({
            'nutrition_progress': progress_list
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while fetching nutrition progress: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_nutrition_progress(request):
    """
    Update user's nutrition progress metrics.
    """
    try:
        user = request.user
        
        progress = NutritionProgress.objects.create(
            user=user,
            weight=request.data.get('weight'),
            meal_plan_adherence=request.data.get('meal_plan_adherence', 0),
            calorie_consistency=request.data.get('calorie_consistency', 0),
            macro_balance_score=request.data.get('macro_balance_score', 0),
            blood_pressure_systolic=request.data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=request.data.get('blood_pressure_diastolic'),
            resting_heart_rate=request.data.get('resting_heart_rate')
        )
        
        # Calculate nutrition score based on provided metrics
        score_components = []
        if progress.meal_plan_adherence:
            score_components.append(progress.meal_plan_adherence)
        if progress.calorie_consistency:
            score_components.append(progress.calorie_consistency)
        if progress.macro_balance_score:
            score_components.append(progress.macro_balance_score)
        
        if score_components:
            progress.nutrition_score = sum(score_components) / len(score_components)
        
        progress.save()
        
        return Response({
            'message': 'Nutrition progress updated successfully',
            'progress': {
                'id': progress.id,
                'weight': progress.weight,
                'nutrition_score': progress.nutrition_score,
                'created_at': progress.created_at
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating nutrition progress: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_foods(request):
    """
    Search foods in the database.
    """
    try:
        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        
        foods = FoodDatabase.objects.all()
        
        if query:
            foods = foods.filter(name__icontains=query)
        
        if category:
            foods = foods.filter(category__icontains=category)
        
        foods_data = []
        for food in foods[:50]:  # Limit to 50 results
            foods_data.append({
                'id': food.id,
                'name': food.name,
                'category': food.category,
                'calories_per_100g': food.calories_per_100g,
                'protein_per_100g': food.protein_per_100g,
                'carbs_per_100g': food.carbs_per_100g,
                'fat_per_100g': food.fat_per_100g,
                'fiber_per_100g': food.fiber_per_100g,
                'sugar_per_100g': food.sugar_per_100g,
                'sodium_per_100g': food.sodium_per_100g,
                'is_organic': food.is_organic,
                'is_processed': food.is_processed,
                'allergens': food.allergens,
                'suitable_for': food.suitable_for
            })
        
        return Response({
            'foods': foods_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while searching foods: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
