"""
AI Analytics Module - Performance Tracking and Insights

This module provides analytics capabilities for tracking AI performance,
user behavior, and generating insights for continuous improvement.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import (
    HealthMetrics, MealPlan, WorkoutPlan, 
    AIChatHistory, ProgressTracking
)


class AIAnalytics:
    """
    Analytics engine for AI features performance and user insights.
    """
    
    def __init__(self):
        self.insight_cache = {}
    
    def get_user_engagement_metrics(self, user, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive user engagement metrics.
        """
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Meal plan engagement
            meal_plans = MealPlan.objects.filter(
                user=user,
                created_at__range=[start_date, end_date]
            )
            
            meal_engagement = {
                'total_plans_generated': meal_plans.count(),
                'average_rating': meal_plans.aggregate(
                    avg_rating=Avg('user_rating')
                )['avg_rating'] or 0,
                'rated_plans': meal_plans.filter(
                    user_rating__isnull=False
                ).count(),
                'feedback_provided': meal_plans.filter(
                    user_feedback__isnull=False
                ).count()
            }
            
            # Workout plan engagement
            workout_plans = WorkoutPlan.objects.filter(
                user=user,
                created_at__range=[start_date, end_date]
            )
            
            workout_engagement = {
                'total_plans_generated': workout_plans.count(),
                'completion_rate': (
                    workout_plans.filter(completed=True).count() / 
                    max(workout_plans.count(), 1) * 100
                ),
                'average_rating': workout_plans.aggregate(
                    avg_rating=Avg('user_rating')
                )['avg_rating'] or 0,
                'rated_workouts': workout_plans.filter(
                    user_rating__isnull=False
                ).count()
            }
            
            # Chatbot engagement
            chats = AIChatHistory.objects.filter(
                user=user,
                created_at__range=[start_date, end_date]
            )
            
            chat_engagement = {
                'total_conversations': chats.count(),
                'average_confidence': chats.aggregate(
                    avg_confidence=Avg('confidence_score')
                )['avg_confidence'] or 0,
                'helpful_responses': chats.filter(
                    helpful=True
                ).count(),
                'intents_detected': chats.values('intent_detected').annotate(
                    count=Count('id')
                ).order_by('-count')
            }
            
            # Progress tracking engagement
            progress_entries = ProgressTracking.objects.filter(
                user=user,
                created_at__range=[start_date, end_date]
            )
            
            progress_engagement = {
                'total_entries': progress_entries.count(),
                'average_progress_score': progress_entries.aggregate(
                    avg_score=Avg('progress_score')
                )['avg_score'] or 0,
                'workout_streak_peak': progress_entries.aggregate(
                    max_streak=Avg('workout_streak')
                )['max_streak'] or 0
            }
            
            return {
                'period_days': days,
                'meal_engagement': meal_engagement,
                'workout_engagement': workout_engagement,
                'chat_engagement': chat_engagement,
                'progress_engagement': progress_engagement,
                'overall_engagement_score': self._calculate_engagement_score(
                    meal_engagement, workout_engagement, chat_engagement, progress_engagement
                )
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_ai_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get AI system performance metrics across all users.
        """
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Meal plan performance
            meal_plans = MealPlan.objects.filter(
                created_at__range=[start_date, end_date]
            )
            
            meal_performance = {
                'total_plans': meal_plans.count(),
                'average_confidence': meal_plans.aggregate(
                    avg_confidence=Avg('confidence_score')
                )['avg_confidence'] or 0,
                'user_satisfaction': meal_plans.aggregate(
                    avg_rating=Avg('user_rating')
                )['avg_rating'] or 0,
                'high_confidence_plans': meal_plans.filter(
                    confidence_score__gte=0.8
                ).count(),
                'low_confidence_plans': meal_plans.filter(
                    confidence_score__lt=0.5
                ).count()
            }
            
            # Workout plan performance
            workout_plans = WorkoutPlan.objects.filter(
                created_at__range=[start_date, end_date]
            )
            
            workout_performance = {
                'total_plans': workout_plans.count(),
                'average_adaptation_score': workout_plans.aggregate(
                    avg_adaptation=Avg('adaptation_score')
                )['avg_adaptation'] or 0,
                'completion_rate': (
                    workout_plans.filter(completed=True).count() / 
                    max(workout_plans.count(), 1) * 100
                ),
                'user_satisfaction': workout_plans.aggregate(
                    avg_rating=Avg('user_rating')
                )['avg_rating'] or 0
            }
            
            # Chatbot performance
            chats = AIChatHistory.objects.filter(
                created_at__range=[start_date, end_date]
            )
            
            chat_performance = {
                'total_interactions': chats.count(),
                'average_confidence': chats.aggregate(
                    avg_confidence=Avg('confidence_score')
                )['avg_confidence'] or 0,
                'helpfulness_rate': (
                    chats.filter(helpful=True).count() / 
                    max(chats.filter(helpful__isnull=False).count(), 1) * 100
                ),
                'intent_distribution': chats.values('intent_detected').annotate(
                    count=Count('id')
                ).order_by('-count')
            }
            
            return {
                'period_days': days,
                'meal_performance': meal_performance,
                'workout_performance': workout_performance,
                'chat_performance': chat_performance,
                'overall_ai_score': self._calculate_ai_performance_score(
                    meal_performance, workout_performance, chat_performance
                )
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_user_behavior_insights(self, user) -> Dict[str, Any]:
        """
        Generate behavioral insights for a specific user.
        """
        try:
            # Get user's health metrics
            metrics = HealthMetrics.objects.get(user=user)
            
            # Analyze patterns
            insights = {
                'goal_alignment': self._analyze_goal_alignment(user, metrics),
                'consistency_patterns': self._analyze_consistency(user),
                'preference_analysis': self._analyze_preferences(user),
                'engagement_trends': self._analyze_engagement_trends(user),
                'recommendation_accuracy': self._analyze_recommendation_accuracy(user)
            }
            
            # Generate actionable insights
            actionable_insights = self._generate_actionable_insights(insights, metrics)
            
            return {
                'behavioral_insights': insights,
                'actionable_recommendations': actionable_insights,
                'generated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_health_metrics(self) -> Dict[str, Any]:
        """
        Get overall system health and performance metrics.
        """
        try:
            # User metrics
            total_users = HealthMetrics.objects.count()
            active_users = HealthMetrics.objects.filter(
                updated_at__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            # Content generation metrics
            recent_meal_plans = MealPlan.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=1)
            ).count()
            
            recent_workout_plans = WorkoutPlan.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=1)
            ).count()
            
            recent_chats = AIChatHistory.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=1)
            ).count()
            
            # Error rates
            meal_error_rate = self._calculate_error_rate(MealPlan)
            workout_error_rate = self._calculate_error_rate(WorkoutPlan)
            chat_error_rate = self._calculate_error_rate(AIChatHistory)
            
            return {
                'user_metrics': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'user_retention_rate': (active_users / max(total_users, 1)) * 100
                },
                'content_generation': {
                    'daily_meal_plans': recent_meal_plans,
                    'daily_workout_plans': recent_workout_plans,
                    'daily_chat_interactions': recent_chats
                },
                'system_performance': {
                    'meal_plan_error_rate': meal_error_rate,
                    'workout_plan_error_rate': workout_error_rate,
                    'chat_error_rate': chat_error_rate
                },
                'system_health_score': self._calculate_system_health_score(
                    total_users, active_users, recent_meal_plans, 
                    recent_workout_plans, recent_chats
                )
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_engagement_score(self, meal_eng: Dict, workout_eng: Dict, 
                                  chat_eng: Dict, progress_eng: Dict) -> float:
        """Calculate overall engagement score."""
        scores = []
        
        # Meal engagement score
        if meal_eng['total_plans_generated'] > 0:
            meal_score = (meal_eng['rated_plans'] / meal_eng['total_plans_generated']) * 50
            meal_score += (meal_eng['average_rating'] / 5) * 50
            scores.append(min(100, meal_score))
        
        # Workout engagement score
        if workout_eng['total_plans_generated'] > 0:
            workout_score = workout_eng['completion_rate'] * 0.6
            workout_score += (workout_eng['average_rating'] / 5) * 40
            scores.append(min(100, workout_score))
        
        # Chat engagement score
        if chat_eng['total_conversations'] > 0:
            chat_score = (chat_eng['helpful_responses'] / max(chat_eng['total_conversations'], 1)) * 50
            chat_score += chat_eng['average_confidence'] * 50
            scores.append(min(100, chat_score))
        
        # Progress engagement score
        if progress_eng['total_entries'] > 0:
            progress_score = progress_eng['average_progress_score']
            scores.append(progress_score)
        
        return sum(scores) / len(scores) if scores else 0
    
    def _calculate_ai_performance_score(self, meal_perf: Dict, workout_perf: Dict, 
                                       chat_perf: Dict) -> float:
        """Calculate overall AI performance score."""
        scores = []
        
        # Meal plan performance
        meal_score = meal_perf['average_confidence'] * 40
        meal_score += (meal_perf['user_satisfaction'] / 5) * 60
        scores.append(min(100, meal_score))
        
        # Workout plan performance
        workout_score = workout_perf['average_adaptation_score'] * 40
        workout_score += (workout_perf['user_satisfaction'] / 5) * 60
        scores.append(min(100, workout_score))
        
        # Chat performance
        chat_score = chat_perf['average_confidence'] * 40
        chat_score += chat_perf['helpfulness_rate'] * 0.6
        scores.append(min(100, chat_score))
        
        return sum(scores) / len(scores) if scores else 0
    
    def _analyze_goal_alignment(self, user, metrics) -> Dict[str, Any]:
        """Analyze how well user actions align with their goals."""
        # This would analyze if user's meal plans and workouts align with their stated goals
        return {
            'alignment_score': 0.8,  # Placeholder
            'goal_consistency': 0.9,
            'recommendation_relevance': 0.85
        }
    
    def _analyze_consistency(self, user) -> Dict[str, Any]:
        """Analyze user's consistency patterns."""
        progress_data = ProgressTracking.objects.filter(user=user).order_by('created_at')
        
        if not progress_data:
            return {'consistency_score': 0, 'patterns': []}
        
        # Calculate consistency metrics
        workout_gaps = []
        for i in range(1, len(progress_data)):
            gap = (progress_data[i].created_at - progress_data[i-1].created_at).days
            workout_gaps.append(gap)
        
        avg_gap = sum(workout_gaps) / len(workout_gaps) if workout_gaps else 0
        
        return {
            'consistency_score': max(0, 1 - (avg_gap / 7)),  # Normalize to 0-1
            'average_workout_gap': avg_gap,
            'longest_gap': max(workout_gaps) if workout_gaps else 0
        }
    
    def _analyze_preferences(self, user) -> Dict[str, Any]:
        """Analyze user's preferences from feedback."""
        meal_plans = MealPlan.objects.filter(user=user, user_feedback__isnull=False)
        
        preferences = {
            'preferred_meal_types': [],
            'avoided_foods': [],
            'preferred_workout_intensity': 'moderate',
            'workout_type_preferences': []
        }
        
        # Analyze meal feedback for preferences
        for plan in meal_plans:
            feedback = plan.user_feedback.lower()
            if 'too intense' in feedback:
                preferences['preferred_workout_intensity'] = 'light'
            elif 'too easy' in feedback:
                preferences['preferred_workout_intensity'] = 'hard'
        
        return preferences
    
    def _analyze_engagement_trends(self, user) -> Dict[str, Any]:
        """Analyze user's engagement trends over time."""
        # Get last 4 weeks of data
        engagement_data = []
        for week in range(4):
            start_date = timezone.now() - timedelta(weeks=week+1)
            end_date = timezone.now() - timedelta(weeks=week)
            
            week_engagement = self.get_user_engagement_metrics(user, 7)
            engagement_data.append({
                'week': week + 1,
                'score': week_engagement.get('overall_engagement_score', 0)
            })
        
        return {
            'weekly_engagement': engagement_data,
            'trend': 'improving' if engagement_data and engagement_data[-1]['score'] > engagement_data[0]['score'] else 'declining'
        }
    
    def _analyze_recommendation_accuracy(self, user) -> Dict[str, Any]:
        """Analyze how accurate AI recommendations are for this user."""
        meal_plans = MealPlan.objects.filter(user=user, user_rating__isnull=False)
        workout_plans = WorkoutPlan.objects.filter(user=user, user_rating__isnull=False)
        
        meal_accuracy = sum(plan.user_rating for plan in meal_plans) / max(len(meal_plans), 1)
        workout_accuracy = sum(plan.user_rating for plan in workout_plans) / max(len(workout_plans), 1)
        
        return {
            'meal_recommendation_accuracy': meal_accuracy / 5,  # Normalize to 0-1
            'workout_recommendation_accuracy': workout_accuracy / 5,
            'overall_accuracy': ((meal_accuracy + workout_accuracy) / 2) / 5
        }
    
    def _generate_actionable_insights(self, insights: Dict, metrics) -> List[str]:
        """Generate actionable recommendations based on insights."""
        recommendations = []
        
        # Goal alignment recommendations
        if insights['goal_alignment']['alignment_score'] < 0.7:
            recommendations.append("Consider adjusting your meal plans to better align with your fitness goals.")
        
        # Consistency recommendations
        if insights['consistency_patterns']['consistency_score'] < 0.6:
            recommendations.append("Try to establish a more consistent workout schedule for better results.")
        
        # Engagement recommendations
        if insights['engagement_trends']['trend'] == 'declining':
            recommendations.append("Your engagement has been declining. Try varying your workouts to stay motivated.")
        
        # Accuracy recommendations
        if insights['recommendation_accuracy']['overall_accuracy'] < 0.7:
            recommendations.append("Provide more feedback on meal plans and workouts to improve AI recommendations.")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _calculate_error_rate(self, model_class) -> float:
        """Calculate error rate for a given model."""
        # This would track actual errors, for now return placeholder
        return 0.05  # 5% error rate
    
    def _calculate_system_health_score(self, total_users: int, active_users: int, 
                                     meal_plans: int, workout_plans: int, chats: int) -> float:
        """Calculate overall system health score."""
        scores = []
        
        # User engagement score
        if total_users > 0:
            user_score = (active_users / total_users) * 100
            scores.append(min(100, user_score))
        
        # Content generation score
        content_score = min(100, (meal_plans + workout_plans + chats) / 10)
        scores.append(content_score)
        
        return sum(scores) / len(scores) if scores else 0
