#!/usr/bin/env python
"""
Real-Time Adaptation System for ML Models
Implements continuous learning based on user feedback
"""

import os
import sys
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Add Django project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Django setup will be handled by the importing module

from ai_features.ml_performance import MLPredictionFeedback, MLPerformanceLog
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
import pickle

class RealTimeAdapter:
    """
    Real-time adaptation system for ML models
    Implements continuous learning based on user feedback
    """
    
    def __init__(self):
        self.adaptation_threshold = 10  # Minimum feedbacks for adaptation
        self.adaptation_window_days = 30  # Days to consider for adaptation
        self.feature_weights = defaultdict(float)
        self.adaptation_history = []
        
    def should_adapt(self, user_id: int) -> bool:
        """Check if user has enough feedback for adaptation"""
        feedback_count = MLPredictionFeedback.objects.filter(
            user_id=user_id,
            timestamp__gte=datetime.now() - timedelta(days=self.adaptation_window_days)
        ).count()
        
        return feedback_count >= self.adaptation_threshold
    
    def get_adaptation_data(self, user_id: int) -> Dict:
        """Get feedback data for adaptation"""
        feedbacks = MLPredictionFeedback.objects.filter(
            user_id=user_id,
            timestamp__gte=datetime.now() - timedelta(days=self.adaptation_window_days)
        ).order_by('-timestamp')
        
        if not feedbacks:
            return {}
        
        # Calculate adaptation factors
        adaptation_factors = self._calculate_adaptation_factors(feedbacks)
        
        # Get recent performance logs
        performance_logs = MLPerformanceLog.objects.filter(
            user_id=user_id,
            timestamp__gte=datetime.now() - timedelta(days=self.adaptation_window_days)
        ).order_by('-timestamp')[:50]  # Last 50 predictions
        
        return {
            'feedbacks': feedbacks,
            'adaptation_factors': adaptation_factors,
            'performance_logs': performance_logs,
            'feedback_count': len(feedbacks),
            'avg_rating': self._calculate_average_rating(feedbacks),
            'adaptation_strength': self._calculate_adaptation_strength(feedbacks)
        }
    
    def _calculate_adaptation_factors(self, feedbacks) -> Dict[str, float]:
        """Calculate adaptation factors based on feedback patterns"""
        factors = {
            'rating_adjustment': 0.0,
            'helpfulness_adjustment': 0.0,
            'accuracy_adjustment': 0.0,
            'goal_alignment_adjustment': 0.0
        }
        
        # Calculate rating-based adjustment
        ratings = [f.rating for f in feedbacks if f.rating is not None]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            # Lower ratings = more adjustment needed
            factors['rating_adjustment'] = (5.0 - avg_rating) / 5.0
        
        # Calculate helpfulness adjustment
        helpful_count = sum(1 for f in feedbacks if f.helpful)
        if feedbacks:
            helpful_ratio = helpful_count / len(feedbacks)
            factors['helpfulness_adjustment'] = 1.0 - helpful_ratio
        
        # Calculate accuracy adjustment
        accurate_count = sum(1 for f in feedbacks if f.accurate)
        if feedbacks:
            accurate_ratio = accurate_count / len(feedbacks)
            factors['accuracy_adjustment'] = 1.0 - accurate_ratio
        
        # Calculate goal alignment from suggestions
        goal_suggestions = defaultdict(int)
        for f in feedbacks:
            if f.suggestions:
                suggestions = f.suggestions.lower()
                if 'weight' in suggestions:
                    goal_suggestions['weight'] += 1
                if 'muscle' in suggestions:
                    goal_suggestions['muscle'] += 1
                if 'energy' in suggestions:
                    goal_suggestions['energy'] += 1
        
        if goal_suggestions:
            max_goal = max(goal_suggestions.values())
            factors['goal_alignment_adjustment'] = max_goal / len(feedbacks)
        
        return factors
    
    def _calculate_average_rating(self, feedbacks) -> float:
        """Calculate average rating from feedbacks"""
        ratings = [f.rating for f in feedbacks if f.rating is not None]
        return sum(ratings) / len(ratings) if ratings else 0.0
    
    def _calculate_adaptation_strength(self, feedbacks) -> float:
        """Calculate overall adaptation strength"""
        factors = self._calculate_adaptation_factors(feedbacks)
        
        # Weighted combination of factors
        strength = (
            factors['rating_adjustment'] * 0.4 +
            factors['helpfulness_adjustment'] * 0.3 +
            factors['accuracy_adjustment'] * 0.2 +
            factors['goal_alignment_adjustment'] * 0.1
        )
        
        return min(1.0, strength)  # Cap at 1.0
    
    def adapt_features(self, original_features: np.ndarray, adaptation_data: Dict) -> np.ndarray:
        """Adapt features based on user feedback patterns"""
        if not adaptation_data:
            return original_features
        
        factors = adaptation_data['adaptation_factors']
        strength = adaptation_data['adaptation_strength']
        
        # Create adapted features
        adapted_features = original_features.copy()
        
        # Apply feature-specific adaptations
        feature_count = adapted_features.shape[1]
        
        # Adjust BMI-related features based on goal alignment
        if 'goal_alignment_adjustment' in factors:
            bmi_adjustment = factors['goal_alignment_adjustment'] * strength * 0.1
            # BMI features (indices 3, 12, 21, 22, 23 in our feature set)
            bmi_indices = [3, 12, 21, 22, 23]
            for idx in bmi_indices:
                if idx < feature_count:
                    adapted_features[0, idx] *= (1.0 + bmi_adjustment)
        
        # Adjust activity features based on helpfulness
        if 'helpfulness_adjustment' in factors:
            activity_adjustment = factors['helpfulness_adjustment'] * strength * 0.05
            # Activity features (indices 9, 16)
            activity_indices = [9, 16]
            for idx in activity_indices:
                if idx < feature_count:
                    adapted_features[0, idx] *= (1.0 + activity_adjustment)
        
        # Adjust goal difficulty based on accuracy
        if 'accuracy_adjustment' in factors:
            goal_adjustment = factors['accuracy_adjustment'] * strength * 0.08
            # Goal features (indices 8, 17, 18, 19, 20)
            goal_indices = [8, 17, 18, 19, 20]
            for idx in goal_indices:
                if idx < feature_count:
                    adapted_features[0, idx] *= (1.0 + goal_adjustment)
        
        # Apply overall rating adjustment
        if 'rating_adjustment' in factors:
            overall_adjustment = factors['rating_adjustment'] * strength * 0.03
            adapted_features[0, :] *= (1.0 + overall_adjustment)
        
        return adapted_features
    
    def merge_adapted_features(self, original_features: np.ndarray, 
                              adapted_features: np.ndarray, 
                              adaptation_strength: float) -> np.ndarray:
        """Merge original and adapted features"""
        # Weighted merge: 70% original + 30% adapted (adjustable by strength)
        original_weight = 0.7
        adapted_weight = 0.3 * adaptation_strength
        
        merged_features = (
            original_features * original_weight + 
            adapted_features * adapted_weight
        )
        
        return merged_features
    
    def log_adaptation(self, user_id: int, adaptation_data: Dict, 
                      original_features: np.ndarray, 
                      adapted_features: np.ndarray):
        """Log adaptation for monitoring"""
        adaptation_record = {
            'user_id': user_id,
            'timestamp': datetime.now(),
            'feedback_count': adaptation_data.get('feedback_count', 0),
            'avg_rating': adaptation_data.get('avg_rating', 0),
            'adaptation_strength': adaptation_data.get('adaptation_strength', 0),
            'feature_changes': np.mean(np.abs(adapted_features - original_features)),
            'adaptation_factors': adaptation_data.get('adaptation_factors', {})
        }
        
        self.adaptation_history.append(adaptation_record)
        
        # Keep only last 1000 records
        if len(self.adaptation_history) > 1000:
            self.adaptation_history = self.adaptation_history[-1000:]
    
    def get_adaptation_stats(self, user_id: int) -> Dict:
        """Get adaptation statistics for a user"""
        user_adaptations = [
            record for record in self.adaptation_history 
            if record['user_id'] == user_id
        ]
        
        if not user_adaptations:
            return {
                'total_adaptations': 0,
                'avg_adaptation_strength': 0,
                'avg_rating_improvement': 0,
                'last_adaptation': None
            }
        
        total_adaptations = len(user_adaptations)
        avg_strength = sum(r['adaptation_strength'] for r in user_adaptations) / total_adaptations
        avg_rating = sum(r['avg_rating'] for r in user_adaptations) / total_adaptations
        last_adaptation = max(r['timestamp'] for r in user_adaptations)
        
        return {
            'total_adaptations': total_adaptations,
            'avg_adaptation_strength': avg_strength,
            'avg_rating_improvement': avg_rating,
            'last_adaptation': last_adaptation
        }


# Global adapter instance
real_time_adapter = RealTimeAdapter()
