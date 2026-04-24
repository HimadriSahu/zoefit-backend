"""
ML Performance Monitoring Utilities

This module provides decorators and utilities for monitoring
ML model performance in real-time.
"""

import time
import functools
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from django.db import transaction, models
from django.contrib.auth import get_user_model

from .ml_performance import MLPerformanceLog, MLPredictionFeedback

User = get_user_model()


def monitor_ml_performance(model_type: str = 'nutrition'):
    """
    Decorator to monitor ML model performance.
    
    Args:
        model_type: Type of model being monitored ('nutrition' or 'workout')
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_message = None
            result = None
            confidence_score = None
            approach_used = 'unknown'
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Extract metadata from result if available
                if isinstance(result, dict):
                    approach_used = result.get('approach', 'unknown')
                    confidence_score = result.get('confidence_score') or result.get('model_confidence')
                
                return result
                
            except Exception as e:
                success = False
                error_message = str(e)
                raise
                
            finally:
                # Calculate processing time
                processing_time_ms = int((time.time() - start_time) * 1000)
                
                # Try to get user from args/kwargs
                user = None
                for arg in args:
                    if hasattr(arg, 'user'):
                        user = arg.user
                        break
                
                if not user:
                    # Check kwargs for user or user_metrics
                    user = kwargs.get('user')
                    if not user:
                        user_metrics = kwargs.get('metrics')
                        if user_metrics and hasattr(user_metrics, 'user'):
                            user = user_metrics.user
                
                # Log performance
                try:
                    with transaction.atomic():
                        MLPerformanceLog.objects.create(
                            model_type=model_type,
                            approach_used=approach_used,
                            confidence_score=confidence_score,
                            user=user,
                            processing_time_ms=processing_time_ms,
                            success=success,
                            error_message=error_message
                        )
                except Exception as log_error:
                    # Don't let logging errors break the main function
                    print(f"Failed to log ML performance: {log_error}")
        
        return wrapper
    return decorator


def log_user_feedback(
    performance_log_id: int,
    user_id: int,
    rating: int,
    helpful: bool = True,
    accurate: bool = True,
    comments: Optional[str] = None,
    suggestions: Optional[str] = None,
    accepted: bool = True,
    modified: bool = False
) -> bool:
    """
    Log user feedback for an ML prediction.
    
    Args:
        performance_log_id: ID of the performance log
        user_id: ID of the user providing feedback
        rating: Rating (1-5 stars)
        helpful: Whether the recommendation was helpful
        accurate: Whether the recommendation was accurate
        comments: Additional comments
        suggestions: User suggestions
        accepted: Whether user accepted the recommendation
        modified: Whether user modified the recommendation
        
    Returns:
        bool: True if feedback was logged successfully
    """
    try:
        with transaction.atomic():
            # Get the performance log
            perf_log = MLPerformanceLog.objects.get(id=performance_log_id)
            user = User.objects.get(id=user_id)
            
            # Update the performance log with rating
            perf_log.user_rating = rating
            perf_log.user_feedback = comments
            perf_log.save()
            
            # Create detailed feedback
            MLPredictionFeedback.objects.create(
                performance_log=perf_log,
                user=user,
                rating=rating,
                helpful=helpful,
                accurate=accurate,
                comments=comments,
                suggestions=suggestions,
                accepted=accepted,
                modified=modified
            )
            
        return True
        
    except Exception as e:
        print(f"Failed to log user feedback: {e}")
        return False


def get_ml_performance_metrics(
    model_type: str = 'nutrition',
    period_days: int = 7
) -> Dict[str, Any]:
    """
    Get performance metrics for ML models.
    
    Args:
        model_type: Type of model ('nutrition' or 'workout')
        period_days: Number of days to look back
        
    Returns:
        Dict containing performance metrics
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        logs = MLPerformanceLog.objects.filter(
            model_type=model_type,
            timestamp__gte=cutoff_date
        )
        
        total_predictions = logs.count()
        if total_predictions == 0:
            return {
                'period_days': period_days,
                'total_predictions': 0,
                'success_rate': 0,
                'avg_processing_time_ms': 0,
                'approach_distribution': {},
                'avg_confidence_score': 0,
                'avg_user_rating': 0,
                'user_satisfaction_rate': 0
            }
        
        # Basic metrics
        successful_predictions = logs.filter(success=True).count()
        success_rate = (successful_predictions / total_predictions) * 100
        
        avg_processing_time = logs.aggregate(
            avg_time=models.Avg('processing_time_ms')
        )['avg_time'] or 0
        
        # Approach distribution
        approach_dist = logs.values('approach_used').annotate(
            count=models.Count('id')
        ).order_by('approach_used')
        
        approach_distribution = {
            item['approach_used']: item['count'] 
            for item in approach_dist
        }
        
        # Confidence scores
        confidence_logs = logs.filter(
            confidence_score__isnull=False
        )
        avg_confidence = 0
        if confidence_logs.exists():
            avg_confidence = confidence_logs.aggregate(
                avg_conf=models.Avg('confidence_score')
            )['avg_conf'] or 0
        
        # User ratings
        rating_logs = logs.filter(
            user_rating__isnull=False
        )
        avg_rating = 0
        user_satisfaction_rate = 0
        if rating_logs.exists():
            avg_rating = rating_logs.aggregate(
                avg_rating=models.Avg('user_rating')
            )['avg_rating'] or 0
            
            # Satisfaction rate (ratings 4+)
            satisfied_count = rating_logs.filter(
                user_rating__gte=4
            ).count()
            user_satisfaction_rate = (satisfied_count / rating_logs.count()) * 100
        
        return {
            'period_days': period_days,
            'total_predictions': total_predictions,
            'success_rate': round(success_rate, 2),
            'avg_processing_time_ms': round(avg_processing_time, 2),
            'approach_distribution': approach_distribution,
            'avg_confidence_score': round(avg_confidence, 3),
            'avg_user_rating': round(avg_rating, 2),
            'user_satisfaction_rate': round(user_satisfaction_rate, 2)
        }
        
    except Exception as e:
        print(f"Failed to get ML performance metrics: {e}")
        return {
            'error': str(e),
            'period_days': period_days
        }


def get_ml_vs_rule_comparison(
    model_type: str = 'nutrition',
    period_days: int = 30
) -> Dict[str, Any]:
    """
    Compare ML vs rule-based approach performance.
    
    Args:
        model_type: Type of model to compare
        period_days: Number of days to look back
        
    Returns:
        Dict containing comparison metrics
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        logs = MLPerformanceLog.objects.filter(
            model_type=model_type,
            timestamp__gte=cutoff_date
        )
        
        # ML-based metrics
        ml_logs = logs.filter(approach_used='ml_based')
        ml_metrics = _calculate_approach_metrics(ml_logs)
        
        # Rule-based metrics
        rule_logs = logs.filter(approach_used='rule_based')
        rule_metrics = _calculate_approach_metrics(rule_logs)
        
        # Hybrid metrics
        hybrid_logs = logs.filter(approach_used='hybrid')
        hybrid_metrics = _calculate_approach_metrics(hybrid_logs)
        
        return {
            'period_days': period_days,
            'ml_based': ml_metrics,
            'rule_based': rule_metrics,
            'hybrid': hybrid_metrics,
            'recommendation': _get_recommendation(ml_metrics, rule_metrics, hybrid_metrics)
        }
        
    except Exception as e:
        print(f"Failed to get ML vs rule comparison: {e}")
        return {'error': str(e)}


def _calculate_approach_metrics(logs) -> Dict[str, Any]:
    """Calculate metrics for a specific approach."""
    if not logs.exists():
        return {
            'count': 0,
            'success_rate': 0,
            'avg_processing_time_ms': 0,
            'avg_confidence_score': 0,
            'avg_user_rating': 0,
            'user_satisfaction_rate': 0
        }
    
    count = logs.count()
    successful = logs.filter(success=True).count()
    success_rate = (successful / count) * 100
    
    avg_processing_time = logs.aggregate(
        avg_time=models.Avg('processing_time_ms')
    )['avg_time'] or 0
    
    confidence_logs = logs.filter(confidence_score__isnull=False)
    avg_confidence = 0
    if confidence_logs.exists():
        avg_confidence = confidence_logs.aggregate(
            avg_conf=models.Avg('confidence_score')
        )['avg_conf'] or 0
    
    rating_logs = logs.filter(user_rating__isnull=False)
    avg_rating = 0
    satisfaction_rate = 0
    if rating_logs.exists():
        avg_rating = rating_logs.aggregate(
            avg_rating=models.Avg('user_rating')
        )['avg_rating'] or 0
        
        satisfied = rating_logs.filter(user_rating__gte=4).count()
        satisfaction_rate = (satisfied / rating_logs.count()) * 100
    
    return {
        'count': count,
        'success_rate': round(success_rate, 2),
        'avg_processing_time_ms': round(avg_processing_time, 2),
        'avg_confidence_score': round(avg_confidence, 3),
        'avg_user_rating': round(avg_rating, 2),
        'user_satisfaction_rate': round(satisfaction_rate, 2)
    }


def _get_recommendation(ml_metrics, rule_metrics, hybrid_metrics) -> str:
    """Get recommendation based on performance comparison."""
    if ml_metrics['count'] < 10:  # Not enough data
        return "Collect more data to make recommendations"
    
    ml_score = ml_metrics['user_satisfaction_rate'] + ml_metrics['success_rate']
    rule_score = rule_metrics['user_satisfaction_rate'] + rule_metrics['success_rate']
    
    if ml_score > rule_score + 10:  # ML significantly better
        return "ML-based approach is performing better, consider increasing ML usage"
    elif rule_score > ml_score + 10:  # Rule-based significantly better
        return "Rule-based approach is performing better, review ML models"
    else:
        return "Both approaches are performing similarly, continue hybrid approach"
