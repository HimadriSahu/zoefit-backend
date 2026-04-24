"""
ML Performance Tracking Models

This module tracks the performance of ML models over time,
including accuracy, confidence scores, and user feedback.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MLPerformanceLog(models.Model):
    """
    Logs ML model performance for each prediction.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    model_type = models.CharField(
        max_length=50,
        choices=[
            ('nutrition', 'Nutrition Recommendation'),
            ('workout', 'Workout Recommendation'),
        ]
    )
    approach_used = models.CharField(
        max_length=20,
        choices=[
            ('ml_based', 'ML Based'),
            ('rule_based', 'Rule Based'),
            ('hybrid', 'Hybrid'),
        ]
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        help_text="ML model confidence score (0-1)"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_performance_logs'
    )
    
    # Performance metrics
    processing_time_ms = models.IntegerField(
        help_text="Processing time in milliseconds"
    )
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    # User feedback
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="User rating (1-5 stars)"
    )
    user_feedback = models.TextField(blank=True, null=True)
    
    # Full prediction data for analysis
    prediction_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Full prediction data for analysis"
    )
    
    class Meta:
        db_table = 'ml_performance_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['model_type']),
            models.Index(fields=['approach_used']),
        ]
    
    def __str__(self):
        return f"{self.model_type} - {self.approach_used} - {self.timestamp}"


class MLModelMetrics(models.Model):
    """
    Aggregated metrics for ML models over time periods.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    model_type = models.CharField(
        max_length=50,
        choices=[
            ('nutrition', 'Nutrition Recommendation'),
            ('workout', 'Workout Recommendation'),
        ]
    )
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ]
    )
    
    # Performance metrics
    total_predictions = models.IntegerField(default=0)
    ml_based_predictions = models.IntegerField(default=0)
    rule_based_predictions = models.IntegerField(default=0)
    hybrid_predictions = models.IntegerField(default=0)
    
    # Success rates
    success_rate = models.FloatField(default=0.0)
    ml_success_rate = models.FloatField(default=0.0)
    rule_based_success_rate = models.FloatField(default=0.0)
    
    # Average confidence scores
    avg_confidence_score = models.FloatField(null=True, blank=True)
    avg_ml_confidence = models.FloatField(null=True, blank=True)
    
    # User satisfaction
    avg_user_rating = models.FloatField(null=True, blank=True)
    total_user_ratings = models.IntegerField(default=0)
    
    # Performance
    avg_processing_time_ms = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'ml_model_metrics'
        ordering = ['-timestamp']
        unique_together = ['model_type', 'period_type', 'timestamp']
        indexes = [
            models.Index(fields=['model_type', 'period_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.model_type} - {self.period_type} - {self.timestamp}"


class MLPredictionFeedback(models.Model):
    """
    User feedback on specific ML predictions.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    performance_log = models.ForeignKey(
        MLPerformanceLog,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ml_feedback'
    )
    
    # Feedback types
    rating = models.IntegerField(
        help_text="Rating (1-5 stars)"
    )
    helpful = models.BooleanField(
        default=True,
        help_text="Was the recommendation helpful?"
    )
    accurate = models.BooleanField(
        default=True,
        help_text="Was the recommendation accurate?"
    )
    
    # Detailed feedback
    comments = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    
    # What user did with the recommendation
    accepted = models.BooleanField(
        default=True,
        help_text="Did user accept the recommendation?"
    )
    modified = models.BooleanField(
        default=False,
        help_text="Did user modify the recommendation?"
    )
    
    class Meta:
        db_table = 'ml_prediction_feedback'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['performance_log']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Feedback by {self.user.username} - {self.rating} stars"
