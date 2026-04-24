#!/usr/bin/env python
"""
Predictive Insights System for ML Nutrition
Implements trend analysis and forward-looking analytics
"""

import os
import sys
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import calendar

# Add Django project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Django setup will be handled by the importing module

from ai_features.ml_performance import MLPerformanceLog, MLPredictionFeedback
from ai_features.models import HealthMetrics
from django.contrib.auth import get_user_model

User = get_user_model()

class PredictiveInsights:
    """
    Predictive insights system for nutrition recommendations
    Implements trend analysis and forward-looking analytics
    """
    
    def __init__(self):
        self.prediction_window_days = 30
        self.trend_analysis_window = 90
        self.goal_projection_days = 180
        
    def generate_nutrition_trends(self, user_id: int) -> Dict:
        """Generate nutrition trend analysis"""
        # Get nutrition data from performance logs
        nutrition_logs = MLPerformanceLog.objects.filter(
            user_id=user_id,
            timestamp__gte=datetime.now() - timedelta(days=self.trend_analysis_window)
        ).order_by('timestamp')
        
        if not nutrition_logs:
            return self._empty_trend_analysis()
        
        # Extract nutrition data
        nutrition_data = []
        for log in nutrition_logs:
            if log.prediction_data:
                try:
                    prediction = log.prediction_data
                    nutrition_data.append({
                        'date': log.timestamp.date(),
                        'calories': prediction.get('total_calories', 0),
                        'protein': prediction.get('protein', 0),
                        'carbs': prediction.get('carbs', 0),
                        'fat': prediction.get('fat', 0),
                        'confidence': prediction.get('confidence_score', 0),
                        'approach': prediction.get('approach', 'unknown')
                    })
                except:
                    continue
        
        if not nutrition_data:
            return self._empty_trend_analysis()
        
        # Calculate trends
        trends = self._calculate_nutrition_trends(nutrition_data)
        
        # Generate insights
        insights = self._generate_nutrition_insights(trends, nutrition_data)
        
        return {
            'trends': trends,
            'insights': insights,
            'data_points': len(nutrition_data),
            'analysis_period': self.trend_analysis_window,
            'last_updated': datetime.now()
        }
    
    def _empty_trend_analysis(self) -> Dict:
        """Return empty trend analysis"""
        return {
            'trends': {
                'calories': {'direction': 'stable', 'change_percent': 0, 'avg': 0},
                'protein': {'direction': 'stable', 'change_percent': 0, 'avg': 0},
                'carbs': {'direction': 'stable', 'change_percent': 0, 'avg': 0},
                'fat': {'direction': 'stable', 'change_percent': 0, 'avg': 0},
                'confidence': {'direction': 'stable', 'change_percent': 0, 'avg': 0}
            },
            'insights': [],
            'data_points': 0,
            'analysis_period': self.trend_analysis_window,
            'last_updated': datetime.now()
        }
    
    def _calculate_nutrition_trends(self, nutrition_data: List[Dict]) -> Dict:
        """Calculate nutrition trends"""
        trends = {}
        
        # Calculate trends for each metric
        metrics = ['calories', 'protein', 'carbs', 'fat', 'confidence']
        
        for metric in metrics:
            values = [entry[metric] for entry in nutrition_data if entry[metric] > 0]
            
            if len(values) < 2:
                trends[metric] = {
                    'direction': 'stable',
                    'change_percent': 0,
                    'avg': np.mean(values) if values else 0
                }
                continue
            
            # Calculate trend
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = np.mean(first_half)
            second_avg = np.mean(second_half)
            
            change_percent = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
            
            # Determine direction
            if abs(change_percent) < 2:
                direction = 'stable'
            elif change_percent > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'
            
            trends[metric] = {
                'direction': direction,
                'change_percent': round(change_percent, 1),
                'avg': round(np.mean(values), 1)
            }
        
        return trends
    
    def _generate_nutrition_insights(self, trends: Dict, nutrition_data: List[Dict]) -> List[Dict]:
        """Generate insights from nutrition trends"""
        insights = []
        
        # Calorie trend insights
        calorie_trend = trends.get('calories', {})
        if calorie_trend.get('direction') == 'decreasing' and calorie_trend.get('change_percent', 0) < -5:
            insights.append({
                'type': 'calorie_trend',
                'severity': 'info',
                'title': 'Calorie Intake Decreasing',
                'message': f'Your calorie intake has decreased by {abs(calorie_trend.get("change_percent", 0))}% over the past 3 months.',
                'recommendation': 'Ensure you\'re meeting your minimum calorie requirements for optimal performance.'
            })
        elif calorie_trend.get('direction') == 'increasing' and calorie_trend.get('change_percent', 0) > 5:
            insights.append({
                'type': 'calorie_trend',
                'severity': 'warning',
                'title': 'Calorie Intake Increasing',
                'message': f'Your calorie intake has increased by {calorie_trend.get("change_percent", 0)}% over the past 3 months.',
                'recommendation': 'Monitor your calorie intake to ensure it aligns with your fitness goals.'
            })
        
        # Protein trend insights
        protein_trend = trends.get('protein', {})
        if protein_trend.get('direction') == 'decreasing' and protein_trend.get('change_percent', 0) < -5:
            insights.append({
                'type': 'protein_trend',
                'severity': 'warning',
                'title': 'Protein Intake Decreasing',
                'message': f'Your protein intake has decreased by {abs(protein_trend.get("change_percent", 0))}% over the past 3 months.',
                'recommendation': 'Consider increasing protein intake to support muscle maintenance and growth.'
            })
        
        # Confidence trend insights
        confidence_trend = trends.get('confidence', {})
        if confidence_trend.get('direction') == 'increasing' and confidence_trend.get('change_percent', 0) > 3:
            insights.append({
                'type': 'confidence_trend',
                'severity': 'success',
                'title': 'ML Confidence Improving',
                'message': f'ML model confidence has increased by {confidence_trend.get("change_percent", 0)}% over the past 3 months.',
                'recommendation': 'The system is becoming more accurate with your preferences. Keep providing feedback!'
            })
        elif confidence_trend.get('direction') == 'decreasing' and confidence_trend.get('change_percent', 0) < -3:
            insights.append({
                'type': 'confidence_trend',
                'severity': 'warning',
                'title': 'ML Confidence Decreasing',
                'message': f'ML model confidence has decreased by {abs(confidence_trend.get("change_percent", 0))}% over the past 3 months.',
                'recommendation': 'Your preferences may be changing. Consider updating your goals or activity level.'
            })
        
        return insights
    
    def project_goal_progress(self, user_id: int) -> Dict:
        """Project goal achievement timeline"""
        try:
            # Get user's health metrics
            health_metrics = HealthMetrics.objects.filter(user_id=user_id).first()
            if not health_metrics:
                return self._empty_goal_projection()
            
            current_weight = health_metrics.weight
            target_weight = health_metrics.target_weight or current_weight
            fitness_goal = health_metrics.fitness_goal
            
            # Get recent nutrition data
            nutrition_logs = MLPerformanceLog.objects.filter(
                user_id=user_id,
                timestamp__gte=datetime.now() - timedelta(days=30)
            ).order_by('timestamp')
            
            if not nutrition_logs:
                return self._empty_goal_projection()
            
            # Calculate average daily calories
            daily_calories = []
            for log in nutrition_logs:
                if log.prediction_data and log.prediction_data.get('total_calories'):
                    daily_calories.append(log.prediction_data['total_calories'])
            
            if not daily_calories:
                return self._empty_goal_projection()
            
            avg_daily_calories = np.mean(daily_calories)
            
            # Calculate BMR and TDEE
            bmr = self._calculate_bmr(health_metrics)
            tdee = self._calculate_tdee(bmr, health_metrics.activity_level)
            
            # Calculate weight change rate
            calorie_deficit = tdee - avg_daily_calories
            weight_change_rate = calorie_deficit / 7700  # 7700 calories per kg
            
            # Project timeline
            weight_difference = target_weight - current_weight
            if weight_change_rate == 0:
                days_to_goal = float('inf')
            else:
                days_to_goal = abs(weight_difference / weight_change_rate)
            
            # Generate projection
            projection = self._generate_goal_projection(
                current_weight, target_weight, weight_change_rate, 
                days_to_goal, fitness_goal, avg_daily_calories
            )
            
            return projection
            
        except Exception as e:
            print(f"Error in goal projection: {e}")
            return self._empty_goal_projection()
    
    def _empty_goal_projection(self) -> Dict:
        """Return empty goal projection"""
        return {
            'current_weight': 0,
            'target_weight': 0,
            'weight_difference': 0,
            'days_to_goal': None,
            'projected_date': None,
            'weight_change_rate': 0,
            'calorie_deficit': 0,
            'projection_confidence': 0,
            'recommendations': []
        }
    
    def _calculate_bmr(self, health_metrics: HealthMetrics) -> float:
        """Calculate Basal Metabolic Rate using Harris-Benedict equation"""
        # Get user profile for gender and age
        try:
            user_profile = health_metrics.user.user_profile
            gender = user_profile.gender
            age = None
            if user_profile.date_of_birth:
                today = datetime.now().date()
                age = today.year - user_profile.date_of_birth.year - (
                    (today.month, today.day) < (user_profile.date_of_birth.month, user_profile.date_of_birth.day)
                )
        except:
            gender = 'male'
            age = 30
        
        age = age or 30
        weight = health_metrics.weight or 70
        height = health_metrics.height or 170
        
        if gender == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        return bmr
    
    def _calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        return bmr * multiplier
    
    def _generate_goal_projection(self, current_weight: float, target_weight: float,
                                 weight_change_rate: float, days_to_goal: float,
                                 fitness_goal: str, avg_calories: float) -> Dict:
        """Generate comprehensive goal projection"""
        recommendations = []
        
        # Generate recommendations based on projection
        if days_to_goal == float('inf'):
            recommendations.append({
                'type': 'maintenance',
                'message': 'You\'re maintaining your current weight.',
                'action': 'Adjust calorie intake to reach your goal.'
            })
        elif days_to_goal > 365:
            recommendations.append({
                'type': 'slow_progress',
                'message': f'Goal projected to take {int(days_to_goal/30)} months.',
                'action': 'Consider adjusting calorie intake for faster progress.'
            })
        elif days_to_goal < 30:
            recommendations.append({
                'type': 'rapid_progress',
                'message': f'Goal projected to be reached in {int(days_to_goal)} days.',
                'action': 'Ensure sustainable approach to weight change.'
            })
        
        # Calculate confidence
        if abs(weight_change_rate) < 0.1:
            confidence = 0.3  # Low confidence for very slow changes
        elif abs(weight_change_rate) > 0.5:
            confidence = 0.7  # Moderate confidence for moderate changes
        else:
            confidence = 0.9  # High confidence for reasonable changes
        
        # Projected date
        projected_date = None
        if days_to_goal != float('inf') and days_to_goal < 365 * 2:  # Within 2 years
            projected_date = datetime.now() + timedelta(days=days_to_goal)
        
        return {
            'current_weight': round(current_weight, 1),
            'target_weight': round(target_weight, 1),
            'weight_difference': round(target_weight - current_weight, 1),
            'days_to_goal': int(days_to_goal) if days_to_goal != float('inf') else None,
            'projected_date': projected_date.isoformat() if projected_date else None,
            'weight_change_rate': round(weight_change_rate, 3),
            'calorie_deficit': round(-weight_change_rate * 7700, 0),
            'projection_confidence': confidence,
            'recommendations': recommendations
        }
    
    def analyze_recommendation_patterns(self, user_id: int) -> Dict:
        """Analyze user's preference patterns for recommendations"""
        # Get performance logs with approach information
        logs = MLPerformanceLog.objects.filter(
            user_id=user_id,
            timestamp__gte=datetime.now() - timedelta(days=90)
        ).order_by('timestamp')
        
        if not logs:
            return self._empty_pattern_analysis()
        
        # Analyze approach preferences
        approach_counts = defaultdict(int)
        approach_ratings = defaultdict(list)
        
        for log in logs:
            if log.prediction_data:
                approach = log.prediction_data.get('approach', 'unknown')
                approach_counts[approach] += 1
                
                # Get feedback for this prediction
                feedback = MLPredictionFeedback.objects.filter(
                    performance_log=log
                ).first()
                
                if feedback and feedback.rating:
                    approach_ratings[approach].append(feedback.rating)
        
        # Calculate approach preferences
        total_predictions = sum(approach_counts.values())
        approach_preferences = {}
        
        for approach, count in approach_counts.items():
            percentage = (count / total_predictions) * 100
            avg_rating = np.mean(approach_ratings[approach]) if approach_ratings[approach] else 0
            
            approach_preferences[approach] = {
                'usage_percentage': round(percentage, 1),
                'average_rating': round(avg_rating, 1),
                'prediction_count': count
            }
        
        # Generate insights
        insights = self._generate_pattern_insights(approach_preferences)
        
        return {
            'approach_preferences': approach_preferences,
            'insights': insights,
            'total_predictions': total_predictions,
            'analysis_period': 90
        }
    
    def _empty_pattern_analysis(self) -> Dict:
        """Return empty pattern analysis"""
        return {
            'approach_preferences': {},
            'insights': [],
            'total_predictions': 0,
            'analysis_period': 90
        }
    
    def _generate_pattern_insights(self, approach_preferences: Dict) -> List[Dict]:
        """Generate insights from approach preferences"""
        insights = []
        
        # Find most used approach
        most_used = max(approach_preferences.items(), key=lambda x: x[1]['usage_percentage'])
        
        # Find highest rated approach
        highest_rated = max(approach_preferences.items(), key=lambda x: x[1]['average_rating'])
        
        # Generate insights
        if most_used[0] == 'ml_based' and most_used[1]['usage_percentage'] > 70:
            insights.append({
                'type': 'approach_preference',
                'severity': 'info',
                'title': 'ML-Based Approach Preferred',
                'message': f'You prefer ML-based recommendations {most_used[1]["usage_percentage"]}% of the time.',
                'recommendation': 'Continue providing feedback to improve ML accuracy.'
            })
        
        if highest_rated[0] != most_used[0] and highest_rated[1]['average_rating'] > 4.0:
            insights.append({
                'type': 'approach_rating',
                'severity': 'info',
                'title': 'Rating vs Usage Mismatch',
                'message': f'You rate {highest_rated[0]} highest but use {most_used[0]} most often.',
                'recommendation': 'Consider trying more recommendations from your highest-rated approach.'
            })
        
        return insights


# Global insights instance
predictive_insights = PredictiveInsights()
