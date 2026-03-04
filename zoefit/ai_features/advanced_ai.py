"""
Advanced AI Features - Progress Prediction and Adaptation

This module contains advanced AI algorithms for progress prediction,
workout adaptation, and enhanced personalization.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from .models import HealthMetrics, ProgressTracking, WorkoutPlan, MealPlan


class AdvancedAIEngine:
    """
    Advanced AI engine with machine learning capabilities.
    """
    
    def __init__(self):
        self.progress_models = {}
        self.adaptation_factors = {
            'weight_loss': 0.8,
            'muscle_gain': 1.2,
            'maintenance': 1.0,
            'endurance': 1.1,
            'strength': 1.15
        }
    
    def predict_progress(self, user, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Predict user's progress over the next N days.
        """
        try:
            # Get historical data
            progress_data = ProgressTracking.objects.filter(
                user=user
            ).order_by('created_at')[:10]  # Last 10 entries
            
            if len(progress_data) < 3:
                return self._basic_prediction(user, days_ahead)
            
            # Calculate trends
            weight_trend = self._calculate_trend([p.weight for p in progress_data if p.weight])
            workout_trend = self._calculate_workout_trend(progress_data)
            
            # Predict future values
            predictions = {
                'weight_prediction': self._predict_weight(user, weight_trend, days_ahead),
                'workout_completion': self._predict_workout_completion(workout_trend, days_ahead),
                'goal_achievement_probability': self._calculate_goal_probability(user, progress_data),
                'recommendations': self._generate_progress_recommendations(user, progress_data)
            }
            
            return predictions
            
        except Exception:
            return self._basic_prediction(user, days_ahead)
    
    def adapt_workout_plan(self, user, current_plan: WorkoutPlan, performance_data: Dict) -> WorkoutPlan:
        """
        Adapt workout plan based on user performance.
        """
        try:
            # Analyze performance
            difficulty_adjustment = self._analyze_performance_difficulty(performance_data)
            
            # Get user metrics
            metrics = HealthMetrics.objects.get(user=user)
            
            # Adapt exercises
            adapted_exercises = []
            for exercise in current_plan.exercises:
                adapted_exercise = self._adapt_exercise(
                    exercise, 
                    difficulty_adjustment, 
                    metrics.fitness_goal
                )
                adapted_exercises.append(adapted_exercise)
            
            # Update plan
            current_plan.exercises = adapted_exercises
            current_plan.intensity_score *= difficulty_adjustment
            current_plan.save()
            
            return current_plan
            
        except Exception:
            return current_plan
    
    def optimize_meal_plan(self, user, current_plan: MealPlan, feedback_data: Dict) -> MealPlan:
        """
        Optimize meal plan based on user feedback and progress.
        """
        try:
            # Analyze feedback
            preferences = self._analyze_meal_feedback(feedback_data)
            
            # Get user metrics
            metrics = HealthMetrics.objects.get(user=user)
            
            # Optimize meals
            optimized_meals = self._optimize_meals(current_plan.meals, preferences, metrics)
            
            # Update plan
            current_plan.meals = optimized_meals
            current_plan.confidence_score = min(1.0, current_plan.confidence_score + 0.1)
            current_plan.save()
            
            return current_plan
            
        except Exception:
            return current_plan
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate linear trend from values."""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Simple linear regression
        slope = np.polyfit(x, y, 1)[0]
        return slope
    
    def _calculate_workout_trend(self, progress_data: List) -> float:
        """Calculate workout completion trend."""
        completion_rates = []
        for p in progress_data:
            if p.total_workouts > 0:
                rate = p.workout_streak / p.total_workouts
                completion_rates.append(rate)
        
        if not completion_rates:
            return 0.0
        
        return self._calculate_trend(completion_rates)
    
    def _predict_weight(self, user, trend: float, days: int) -> List[float]:
        """Predict weight changes over time."""
        try:
            current_weight = user.healthmetrics.weight
            predictions = []
            
            for day in range(1, days + 1):
                predicted_weight = current_weight + (trend * day)
                predictions.append(max(0, predicted_weight))  # Ensure non-negative
            
            return predictions
        except:
            return [user.healthmetrics.weight] * days
    
    def _predict_workout_completion(self, trend: float, days: int) -> List[float]:
        """Predict workout completion rates."""
        base_rate = 0.8  # Base 80% completion rate
        predictions = []
        
        for day in range(1, days + 1):
            predicted_rate = base_rate + (trend * day * 0.1)
            predictions.append(max(0.0, min(1.0, predicted_rate)))  # Clamp between 0-1
        
        return predictions
    
    def _calculate_goal_probability(self, user, progress_data: List) -> float:
        """Calculate probability of achieving fitness goal."""
        try:
            metrics = user.healthmetrics
            target_weight = metrics.target_weight or metrics.weight
            
            if len(progress_data) < 2:
                return 0.5  # Default 50% probability
            
            # Calculate progress rate
            current_weight = progress_data[-1].weight or metrics.weight
            initial_weight = progress_data[0].weight or metrics.weight
            
            if initial_weight == 0:
                return 0.5
            
            progress_rate = (current_weight - initial_weight) / abs(target_weight - initial_weight)
            
            # Adjust based on goal
            if metrics.fitness_goal == 'weight_loss':
                return max(0.0, min(1.0, 1.0 - progress_rate))
            elif metrics.fitness_goal == 'muscle_gain':
                return max(0.0, min(1.0, progress_rate))
            else:
                return 0.7  # Maintenance goals have higher base probability
                
        except:
            return 0.5
    
    def _generate_progress_recommendations(self, user, progress_data: List) -> List[str]:
        """Generate personalized recommendations based on progress."""
        recommendations = []
        
        try:
            metrics = user.healthmetrics
            
            # Workout consistency
            if len(progress_data) >= 2:
                recent_streak = progress_data[-1].workout_streak
                if recent_streak < 3:
                    recommendations.append("Try to maintain at least 3 workouts per week for better results.")
                elif recent_streak >= 7:
                    recommendations.append("Great consistency! Consider increasing workout intensity.")
            
            # Weight progress
            if metrics.fitness_goal == 'weight_loss':
                recommendations.append("Focus on creating a sustainable calorie deficit through diet and exercise.")
            elif metrics.fitness_goal == 'muscle_gain':
                recommendations.append("Ensure adequate protein intake and progressive overload in your workouts.")
            
            # General advice
            recommendations.append("Stay hydrated and prioritize sleep for optimal recovery.")
            
        except:
            recommendations.append("Keep tracking your progress for more personalized recommendations.")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _basic_prediction(self, user, days: int) -> Dict[str, Any]:
        """Basic prediction when insufficient data is available."""
        metrics = user.healthmetrics
        
        return {
            'weight_prediction': [metrics.weight] * days,
            'workout_completion': [0.8] * days,
            'goal_achievement_probability': 0.6,
            'recommendations': [
                "Continue tracking your progress for better predictions.",
                "Maintain consistency in your workouts and nutrition.",
                "Listen to your body and adjust intensity as needed."
            ]
        }
    
    def _analyze_performance_difficulty(self, performance_data: Dict) -> float:
        """Analyze performance to determine difficulty adjustment."""
        try:
            completion_rate = performance_data.get('completion_rate', 0.8)
            user_rating = performance_data.get('user_rating', 3)
            
            # Calculate adjustment factor
            if completion_rate > 0.9 and user_rating >= 4:
                return 1.1  # Increase difficulty
            elif completion_rate < 0.7 or user_rating <= 2:
                return 0.9  # Decrease difficulty
            else:
                return 1.0  # Maintain current difficulty
                
        except:
            return 1.0
    
    def _adapt_exercise(self, exercise: Dict, adjustment: float, goal: str) -> Dict:
        """Adapt individual exercise based on performance."""
        adapted = exercise.copy()
        
        # Adjust reps
        if adjustment > 1.0:  # Increase difficulty
            adapted['reps'] = min(adapted['reps'] + 2, 20)
            adapted['rest_time'] = max(adapted['rest_time'] - 10, 30)
        elif adjustment < 1.0:  # Decrease difficulty
            adapted['reps'] = max(adapted['reps'] - 2, 5)
            adapted['rest_time'] = min(adapted['rest_time'] + 10, 120)
        
        return adapted
    
    def _analyze_meal_feedback(self, feedback_data: Dict) -> Dict:
        """Analyze meal feedback to extract preferences."""
        preferences = {
            'avoid_foods': [],
            'prefer_foods': [],
            'portion_adjustment': 1.0
        }
        
        try:
            rating = feedback_data.get('rating', 3)
            feedback_text = feedback_data.get('feedback', '').lower()
            
            if rating <= 2:
                # Low rating - identify issues
                if 'bland' in feedback_text or 'tasteless' in feedback_text:
                    preferences['avoid_foods'].extend(['oatmeal', 'chicken breast'])
                if 'too much' in feedback_text or 'full' in feedback_text:
                    preferences['portion_adjustment'] = 0.8
            elif rating >= 4:
                # High rating - identify preferences
                if 'delicious' in feedback_text or 'great' in feedback_text:
                    preferences['prefer_foods'].extend(['salmon', 'vegetables'])
                if 'perfect' in feedback_text or 'just right' in feedback_text:
                    preferences['portion_adjustment'] = 1.0
        
        except:
            pass
        
        return preferences
    
    def _optimize_meals(self, meals: Dict, preferences: Dict, metrics: HealthMetrics) -> Dict:
        """Optimize meals based on preferences and user metrics."""
        optimized = meals.copy()
        
        try:
            # Apply portion adjustments
            if preferences['portion_adjustment'] != 1.0:
                for meal_type in optimized:
                    if isinstance(optimized[meal_type], dict):
                        foods = optimized[meal_type].get('foods', {})
                        for component in foods:
                            for food in foods[component]:
                                food['portion'] *= preferences['portion_adjustment']
                                food['calories'] *= preferences['portion_adjustment']
                                food['protein'] *= preferences['portion_adjustment']
                                food['carbs'] *= preferences['portion_adjustment']
                                food['fat'] *= preferences['portion_adjustment']
        
        except:
            pass
        
        return optimized
