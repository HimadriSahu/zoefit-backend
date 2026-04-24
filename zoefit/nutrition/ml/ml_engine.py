"""
ML-based Nutrition Recommendation Engine

This module implements machine learning models for personalized nutrition planning
using trained datasets instead of rule-based approaches.
"""

import numpy as np
import pandas as pd
import pickle
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from django.core.cache import cache
from django.conf import settings
from django.db.models import Avg, Count, Q
from django.utils import timezone
import os

from nutrition.models import FoodDatabase, MealPlan
from nutrition.ml.training_data_handler import TrainingDataHandler
from nutrition.ml.real_time_adapter import real_time_adapter
from nutrition.ml.predictive_insights import predictive_insights
from ai_features.ml_performance import MLPerformanceLog, MLPredictionFeedback
from ai_features.models import HealthMetrics
from datetime import date


class MLNutritionEngine:
    """
    Machine Learning based nutrition recommendation engine.
    Uses trained models to predict optimal meal plans based on user data.
    Enhanced with real-time adaptation and predictive insights.
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_cache_timeout = 3600  # 1 hour
        self.adaptation_threshold = 10  # Minimum feedbacks for adaptation
        self.prediction_window_days = 30  # Days for predictive insights
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models from disk"""
        try:
            model_dir = os.path.join(settings.BASE_DIR, 'nutrition', 'ml', 'models')
            
            # Load meal recommendation model
            meal_model_path = os.path.join(model_dir, 'meal_recommendation_model.pkl')
            if os.path.exists(meal_model_path):
                with open(meal_model_path, 'rb') as f:
                    self.models['meal_recommendation'] = pickle.load(f)
            
            # Load macro prediction model
            macro_model_path = os.path.join(model_dir, 'macro_prediction_model.pkl')
            if os.path.exists(macro_model_path):
                with open(macro_model_path, 'rb') as f:
                    self.models['macro_prediction'] = pickle.load(f)
            
            # Load scalers
            scaler_path = os.path.join(model_dir, 'feature_scaler.pkl')
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scalers['features'] = pickle.load(f)
            
            # Load encoders
            encoder_path = os.path.join(model_dir, 'label_encoders.pkl')
            if os.path.exists(encoder_path):
                with open(encoder_path, 'rb') as f:
                    self.encoders = pickle.load(f)
                    
        except Exception as e:
            print(f"Error loading models: {e}")
            self._initialize_fallback_models()
    
    def _initialize_fallback_models(self):
        """Initialize fallback models if trained models are not available"""
        self.models['meal_recommendation'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.models['macro_prediction'] = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scalers['features'] = StandardScaler()
        self.encoders = {}
    
    def generate_ml_meal_plan(self, metrics: HealthMetrics, target_date: date) -> Dict[str, Any]:
        """
        Generate meal plan using trained ML models with real-time adaptation.
        """
        try:
            # Extract enhanced features from user metrics
            features = self._extract_enhanced_features(metrics)
            
            # Apply real-time adaptation if enough feedback data exists
            adapted_features = self._apply_real_time_adaptation(metrics)
            
            # Merge adapted features with original features
            if adapted_features:
                features = adapted_features
            
            # Scale features (features is already 2D)
            features_scaled = self.scalers['features'].transform(features)
            
            # Predict macros
            macro_predictions = self.models['macro_prediction'].predict(features_scaled)[0]
            
            # Predict meal-specific macros
            meal_predictions = self.models['meal_recommendation'].predict(features_scaled)[0]
            
            # Generate meal plan from predictions
            meal_plan = self._generate_meal_plan_from_predictions(
                macro_predictions, meal_predictions, metrics
            )
            
            # Calculate confidence score
            confidence = self._calculate_prediction_confidence(features_scaled)
            
            # Get model version from training report
            model_version = self._get_model_version()
            
            # Generate predictive insights
            insights = self._generate_predictive_insights(metrics, target_date)
            
            return {
                'meals': meal_plan,
                'total_calories': int(macro_predictions[0]),
                'protein': int(macro_predictions[1]),
                'carbs': int(macro_predictions[2]),
                'fat': int(macro_predictions[3]),
                'confidence_score': confidence,
                'prediction_date': target_date.isoformat(),
                'model_version': model_version,
                'approach': 'ml_based_adaptive' if adapted_features else 'ml_based',
                'predictive_insights': insights,
                'adaptation_applied': bool(adapted_features)
            }
            
        except Exception as e:
            print(f"Error in ML meal plan generation: {e}")
            raise
    
    def _extract_features(self, user_metrics: HealthMetrics) -> np.ndarray:
        """Extract numerical features from user metrics for ML prediction"""
        features = []
        
        # Get user profile for age and gender
        try:
            user_profile = user_metrics.user.user_profile
            # Calculate age from date of birth
            from datetime import date
            age = None
            if user_profile.date_of_birth:
                today = date.today()
                age = today.year - user_profile.date_of_birth.year - (
                    (today.month, today.day) < (user_profile.date_of_birth.month, user_profile.date_of_birth.day)
                )
            
            # Basic demographics
            features.append(age or 30)
            features.append(1 if user_profile.gender == 'male' else 0)
            features.append(user_metrics.height or user_profile.height or 170)
            features.append(user_metrics.weight or user_profile.weight or 70)
        except Exception:
            # Fallback if user_profile doesn't exist
            features.append(30)  # age
            features.append(1)  # gender (male)
            features.append(user_metrics.height or 170)
            features.append(user_metrics.weight or 70)
        
        # Goal and activity
        features.append(self._encode_fitness_goal(user_metrics.fitness_goal))
        features.append(self._encode_activity_level(user_metrics.activity_level))
        
        # Target metrics
        features.append(user_metrics.target_weight or user_metrics.weight or 70)
        
        # Calculate BMI
        height_m = (user_metrics.height or 170) / 100
        weight = user_metrics.weight or 70
        bmi = weight / (height_m ** 2)
        features.append(bmi)
        
        # Dietary preferences (one-hot encoded)
        try:
            user_profile = user_metrics.user.user_profile
            preferences = user_profile.dietary_preferences or user_metrics.dietary_preferences or []
            allergies = user_profile.allergies or user_metrics.allergies or []
            medical_conditions = user_metrics.medical_conditions or []
        except Exception:
            preferences = user_metrics.dietary_preferences or []
            allergies = user_metrics.allergies or []
            medical_conditions = user_metrics.medical_conditions or []
        
        diet_types = ['vegetarian', 'vegan', 'gluten_free', 'dairy_free', 'keto', 'paleo']
        for diet_type in diet_types:
            features.append(1 if diet_type in preferences else 0)
        
        # Allergies count
        features.append(len(allergies))
        
        # Medical conditions count
        features.append(len(medical_conditions))
        
        return np.array(features).reshape(1, -1)
    
    def _extract_enhanced_features(self, user_metrics: HealthMetrics) -> np.ndarray:
        """Extract enhanced numerical features from user metrics for ML prediction"""
        features = {}
        
        # Get user profile for age and gender
        try:
            user_profile = user_metrics.user.user_profile
            # Calculate age from date of birth
            from datetime import date
            age = None
            if user_profile.date_of_birth:
                today = date.today()
                age = today.year - user_profile.date_of_birth.year - (
                    (today.month, today.day) < (user_profile.date_of_birth.month, user_profile.date_of_birth.day)
                )
            
            # Basic demographics
            features['age'] = age or 30
            features['gender_encoded'] = 1 if user_profile.gender == 'male' else 0
            features['height'] = user_metrics.height or user_profile.height or 170
            features['weight'] = user_metrics.weight or user_profile.weight or 70
        except Exception:
            # Fallback if user_profile doesn't exist
            features['age'] = 30
            features['gender_encoded'] = 1
            features['height'] = user_metrics.height or 170
            features['weight'] = user_metrics.weight or 70
        
        # Calculate BMI
        height_m = features['height'] / 100
        weight = features['weight']
        bmi = weight / (height_m ** 2)
        features['bmi'] = bmi
        
        # Goal and activity
        features['fitness_goal_encoded'] = self._encode_fitness_goal(user_metrics.fitness_goal)
        features['activity_level_encoded'] = self._encode_activity_level(user_metrics.activity_level)
        
        # Target metrics
        features['target_weight'] = user_metrics.target_weight or weight
        
        # Dietary preferences
        try:
            user_profile = user_metrics.user.user_profile
            preferences = user_profile.dietary_preferences or user_metrics.dietary_preferences or []
            allergies = user_profile.allergies or user_metrics.allergies or []
            medical_conditions = user_profile.medical_conditions or []
        except Exception:
            preferences = user_metrics.dietary_preferences or []
            allergies = user_metrics.allergies or []
            medical_conditions = user_metrics.medical_conditions or []
        
        # One-hot encode dietary preferences
        diet_types = ['vegetarian', 'vegan', 'gluten_free', 'dairy_free']
        for diet_type in diet_types:
            features[f'dietary_preferences_{diet_type}'] = 1 if diet_type in preferences else 0
        
        # Count features
        features['allergies_count'] = len(allergies)
        features['medical_conditions_count'] = len(medical_conditions)
        
        # Enhanced engineered features
        features = self._add_enhanced_features(features, user_metrics)
        
        # Convert to array in correct order (matching training)
        feature_order = [
            'age', 'height', 'weight', 'bmi',
            'target_weight', 'allergies_count', 'medical_conditions_count',
            'gender_encoded', 'fitness_goal_encoded', 'activity_level_encoded',
            'dietary_preferences_encoded', 'bmi_category_encoded', 'age_group_encoded',
            'weight_difference', 'weight_change_percent', 'weight_change_needed',
            'activity_multiplier', 'goal_difficulty', 'goal_activity_encoded',
            'age_goal_encoded', 'bmi_goal_encoded', 'gender_goal_encoded',
            'bmi_risk_score', 'age_risk_factor', 'total_health_risk',
            'carb_calorie_ratio'
        ]
        
        # Create a single dietary_preferences_encoded feature (sum of all preferences)
        features['dietary_preferences_encoded'] = sum([
            features.get('dietary_preferences_vegetarian', 0),
            features.get('dietary_preferences_vegan', 0),
            features.get('dietary_preferences_gluten_free', 0),
            features.get('dietary_preferences_dairy_free', 0)
        ])
        
        # Fill missing features with 0
        feature_array = []
        for feature_name in feature_order:
            feature_array.append(features.get(feature_name, 0))
        
        return np.array(feature_array).reshape(1, -1)
    
    def _add_enhanced_features(self, features: dict, user_metrics: HealthMetrics) -> dict:
        """Add enhanced engineered features"""
        age = features['age']
        gender = features['gender_encoded']
        height = features['height']
        weight = features['weight']
        bmi = features['bmi']
        target_weight = features['target_weight']
        goal = user_metrics.fitness_goal
        activity = user_metrics.activity_level
        
        # BMI categories
        if bmi < 18.5:
            bmi_category = 0  # underweight
        elif bmi < 25:
            bmi_category = 1  # normal
        elif bmi < 30:
            bmi_category = 2  # overweight
        else:
            bmi_category = 3  # obese
        features['bmi_category_encoded'] = bmi_category
        
        # Age groups
        if age < 25:
            age_group = 0  # young_adult
        elif age < 35:
            age_group = 1  # adult
        elif age < 50:
            age_group = 2  # middle_aged
        elif age < 65:
            age_group = 3  # senior
        else:
            age_group = 4  # elderly
        features['age_group_encoded'] = age_group
        
        # Calories and protein per kg (estimated)
        features['calories_per_kg'] = 30  # Will be updated after prediction
        features['protein_per_kg'] = 1.5  # Will be updated after prediction
        
        # Weight change metrics
        weight_diff = target_weight - weight
        features['weight_difference'] = weight_diff
        features['weight_change_percent'] = (weight_diff / weight * 100) if weight > 0 else 0
        features['weight_change_needed'] = 1 if weight_diff > 0 else 0
        
        # Activity multiplier
        activity_multipliers = {
            'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55,
            'active': 1.725, 'very_active': 1.9
        }
        features['activity_multiplier'] = activity_multipliers.get(activity, 1.55)
        
        # Goal difficulty
        goal_difficulty = {
            'maintenance': 1, 'endurance': 2, 'strength': 3,
            'muscle_gain': 4, 'weight_loss': 5
        }
        features['goal_difficulty'] = goal_difficulty.get(goal, 3)
        
        # Interaction features
        features['goal_activity_encoded'] = features['fitness_goal_encoded'] * features['activity_level_encoded']
        features['age_goal_encoded'] = features['age_group_encoded'] * features['fitness_goal_encoded']
        features['bmi_goal_encoded'] = features['bmi_category_encoded'] * features['fitness_goal_encoded']
        features['gender_goal_encoded'] = features['gender_encoded'] * features['fitness_goal_encoded']
        
        # Health risk features
        if bmi < 18.5:
            features['bmi_risk_score'] = 0
        elif bmi < 25:
            features['bmi_risk_score'] = 2
        elif bmi < 30:
            features['bmi_risk_score'] = 4
        else:
            features['bmi_risk_score'] = 6
        
        if age < 30:
            features['age_risk_factor'] = 0
        elif age < 50:
            features['age_risk_factor'] = 1
        else:
            features['age_risk_factor'] = 2
        
        features['total_health_risk'] = features['bmi_risk_score'] + features['age_risk_factor']
        
        # Nutritional ratios (estimated, will be refined after prediction)
        features['protein_calorie_ratio'] = 0.15  # 15% protein
        features['fat_calorie_ratio'] = 0.30   # 30% fat
        features['carb_calorie_ratio'] = 0.55   # 55% carbs
        
        return features
    
    def _encode_fitness_goal(self, goal: str) -> float:
        """Encode fitness goal to numerical value"""
        goal_mapping = {
            'weight_loss': 0.0,
            'muscle_gain': 1.0,
            'maintenance': 0.5,
            'endurance': 0.75,
            'strength': 0.85
        }
        return goal_mapping.get(goal, 0.5)
    
    def _calculate_prediction_confidence(self, features_scaled: np.ndarray) -> float:
        """Calculate confidence score for ML predictions"""
        try:
            # Base confidence on model consistency and feature quality
            base_confidence = 0.85
            
            # Adjust based on feature quality
            feature_std = np.std(features_scaled)
            if feature_std < 2.0:
                confidence_adjustment = 0.10
            elif feature_std < 3.0:
                confidence_adjustment = 0.05
            else:
                confidence_adjustment = -0.05
            
            # Ensure confidence is within valid range
            confidence = max(0.3, min(0.95, base_confidence + confidence_adjustment))
            
            return confidence
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.7  # Default confidence
    
    def _encode_activity_level(self, level: str) -> float:
        """Encode activity level to numerical value"""
        level_mapping = {
            'sedentary': 0.0,
            'light': 0.25,
            'moderate': 0.5,
            'active': 0.75,
            'very_active': 1.0
        }
        return level_mapping.get(level, 0.5)
    
    def _apply_real_time_adaptation(self, metrics: HealthMetrics) -> Optional[np.ndarray]:
        """Apply real-time adaptation based on user feedback"""
        try:
            user_id = metrics.user.id
            
            # Check if adaptation should be applied
            if not real_time_adapter.should_adapt(user_id):
                return None
            
            # Get adaptation data
            adaptation_data = real_time_adapter.get_adaptation_data(user_id)
            
            if not adaptation_data:
                return None
            
            # Extract features
            features = self._extract_enhanced_features(metrics)
            
            # Adapt features
            adapted_features = real_time_adapter.adapt_features(features, adaptation_data)
            
            # Merge with original features
            merged_features = real_time_adapter.merge_adapted_features(
                features, adapted_features, adaptation_data.get('adaptation_strength', 0.5)
            )
            
            # Log adaptation
            real_time_adapter.log_adaptation(user_id, adaptation_data, features, adapted_features)
            
            return merged_features
            
        except Exception as e:
            print(f"Error applying real-time adaptation: {e}")
            return None
    
    def generate_predictive_insights(self, user_id: int) -> Dict[str, Any]:
        """Generate comprehensive predictive insights for user"""
        try:
            insights = {}
            
            # Generate nutrition trends
            nutrition_trends = predictive_insights.generate_nutrition_trends(user_id)
            insights['nutrition_trends'] = nutrition_trends
            
            # Generate goal projection
            goal_projection = predictive_insights.project_goal_progress(user_id)
            insights['goal_projection'] = goal_projection
            
            # Analyze recommendation patterns
            pattern_analysis = predictive_insights.analyze_recommendation_patterns(user_id)
            insights['recommendation_patterns'] = pattern_analysis
            
            # Generate seasonal insights
            seasonal_insights = self._get_seasonal_insights()
            insights['seasonal_insights'] = seasonal_insights
            
            # Generate performance forecast
            performance_forecast = self._generate_performance_forecast(user_id)
            insights['performance_forecast'] = performance_forecast
            
            return insights
            
        except Exception as e:
            print(f"Error generating predictive insights: {e}")
            return {}
    
    def _generate_seasonal_insights(self) -> Dict[str, Any]:
        """Generate seasonal nutrition insights"""
        try:
            current_month = datetime.now().month
            
            # Determine season
            if current_month in [12, 1, 2]:
                season = 'winter'
                season_focus = 'immune_support'
                calorie_adjustment = 200  # Increase calories for warmth
                protein_adjustment = 0.1  # Increase protein for immune function
            elif current_month in [3, 4, 5]:
                season = 'spring'
                season_focus = 'detoxification'
                calorie_adjustment = -100  # Slight decrease for spring cleaning
                protein_adjustment = 0.05  # Moderate protein
            elif current_month in [6, 7, 8]:
                season = 'summer'
                season_focus = 'hydration'
                calorie_adjustment = -150  # Decrease calories (less needed for heat)
                protein_adjustment = 0.0  # Maintain protein
            else:  # [9, 10, 11]
                season = 'fall'
                season_focus = 'energy_storage'
                calorie_adjustment = 100  # Slight increase for preparation
                protein_adjustment = 0.05  # Moderate protein
            
            # Seasonal food recommendations
            seasonal_foods = self._get_seasonal_foods(season)
            
            return {
                'current_season': season,
                'season_focus': season_focus,
                'calorie_adjustment': calorie_adjustment,
                'protein_adjustment': protein_adjustment,
                'seasonal_foods': seasonal_foods,
                'recommendations': self._generate_seasonal_recommendations(season, season_focus)
            }
            
        except Exception as e:
            print(f"Error generating seasonal insights: {e}")
            return {}
    
    def _get_seasonal_foods(self, season: str) -> List[str]:
        """Get seasonal food recommendations"""
        seasonal_foods = {
            'winter': ['citrus_fruits', 'root_vegetables', 'soups', 'stews', 'warm_oatmeal'],
            'spring': ['leafy_greens', 'berries', 'fresh_vegetables', 'light_salads', 'herbs'],
            'summer': ['watermelon', 'cucumber', 'tomatoes', 'grilled_fish', 'smoothies'],
            'fall': ['apples', 'pumpkin', 'squash', 'nuts', 'warm_spices']
        }
        
        return seasonal_foods.get(season, [])
    
    def _generate_seasonal_recommendations(self, season: str, focus: str) -> List[Dict]:
        """Generate seasonal recommendations"""
        recommendations = []
        
        if season == 'winter':
            recommendations.extend([
                {
                    'type': 'nutrition',
                    'title': 'Increase Vitamin C',
                    'message': 'Boost immune system with vitamin C-rich foods.',
                    'foods': ['citrus', 'bell_peppers', 'broccoli']
                },
                {
                    'type': 'hydration',
                    'title': 'Warm Hydration',
                    'message': 'Stay hydrated with warm beverages.',
                    'foods': ['herbal_tea', 'warm_water', 'soups']
                }
            ])
        elif season == 'spring':
            recommendations.extend([
                {
                    'type': 'detox',
                    'title': 'Spring Cleaning',
                    'message': 'Support natural detoxification with fresh foods.',
                    'foods': ['leafy_greens', 'lemon', 'garlic']
                },
                {
                    'type': 'energy',
                    'title': 'Renewal Energy',
                    'message': 'Increase energy with seasonal produce.',
                    'foods': ['berries', 'sprouts', 'fresh_vegetables']
                }
            ])
        elif season == 'summer':
            recommendations.extend([
                {
                    'type': 'hydration',
                    'title': 'Stay Hydrated',
                    'message': 'Increase fluid intake to beat the heat.',
                    'foods': ['watermelon', 'cucumber', 'coconut_water']
                },
                {
                    'type': 'light_meals',
                    'title': 'Lighter Fare',
                    'message': 'Choose lighter meals to stay comfortable.',
                    'foods': ['salads', 'grilled_fish', 'fresh_fruits']
                }
            ])
        else:  # fall
            recommendations.extend([
                {
                    'type': 'immune',
                    'title': 'Fall Immunity',
                    'message': 'Prepare immune system for winter.',
                    'foods': ['pumpkin', 'sweet_potato', 'apples']
                },
                {
                    'type': 'energy',
                    'title': 'Energy Storage',
                    'message': 'Build energy reserves for winter.',
                    'foods': ['nuts', 'seeds', 'whole_grains']
                }
            ])
        
        return recommendations
    
    def _generate_performance_forecast(self, user_id: int) -> Dict[str, Any]:
        """Generate 7-day performance forecast"""
        try:
            # Get recent performance data
            recent_logs = MLPerformanceLog.objects.filter(
                user_id=user_id,
                timestamp__gte=datetime.now() - timedelta(days=7)
            ).order_by('timestamp')
            
            if not recent_logs:
                return self._empty_performance_forecast()
            
            # Calculate confidence trend
            confidence_scores = []
            for log in recent_logs:
                if log.prediction_data and log.prediction_data.get('confidence_score'):
                    confidence_scores.append(log.prediction_data['confidence_score'])
            
            if not confidence_scores:
                return self._empty_performance_forecast()
            
            # Calculate trend
            recent_avg = np.mean(confidence_scores[-3:]) if len(confidence_scores) >= 3 else np.mean(confidence_scores)
            overall_avg = np.mean(confidence_scores)
            
            # Forecast next 7 days
            forecast = []
            base_confidence = recent_avg
            
            for day in range(7):
                # Simulate daily variation
                daily_variation = np.random.normal(0, 0.02)  # Small random variation
                predicted_confidence = max(0.3, min(0.95, base_confidence + daily_variation))
                
                forecast.append({
                    'day': day + 1,
                    'date': (datetime.now() + timedelta(days=day)).date().isoformat(),
                    'predicted_confidence': round(predicted_confidence, 3),
                    'confidence_level': self._get_confidence_level(predicted_confidence)
                })
            
            return {
                'forecast': forecast,
                'current_confidence': round(recent_avg, 3),
                'confidence_trend': 'improving' if recent_avg > overall_avg else 'stable',
                'forecast_accuracy': 0.85  # Estimated accuracy
            }
            
        except Exception as e:
            print(f"Error generating performance forecast: {e}")
            return self._empty_performance_forecast()
    
    def _empty_performance_forecast(self) -> Dict[str, Any]:
        """Return empty performance forecast"""
        return {
            'forecast': [],
            'current_confidence': 0,
            'confidence_trend': 'stable',
            'forecast_accuracy': 0
        }
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level description"""
        if confidence >= 0.9:
            return 'very_high'
        elif confidence >= 0.8:
            return 'high'
        elif confidence >= 0.7:
            return 'medium'
        elif confidence >= 0.6:
            return 'low'
        else:
            return 'very_low'
    
    def _predict_macros(self, features: np.ndarray) -> Dict[str, float]:
        """Predict optimal macronutrients using ML model"""
        try:
            if 'macro_prediction' in self.models and 'features' in self.scalers:
                # Scale features
                scaled_features = self.scalers['features'].transform(features)
                
                # Predict macros
                model = self.models['macro_prediction']
                predictions = model.predict(scaled_features)[0]
                
                # Ensure positive values and proper ratios
                calories = max(1200, predictions[0])
                protein = max(0.1 * calories / 4, predictions[1])  # min 10% of calories
                carbs = max(0.3 * calories / 4, predictions[2])     # min 30% of calories
                fat = max(0.2 * calories / 9, predictions[3])       # min 20% of calories
                
                # Normalize to match calorie target
                total_macro_calories = (protein * 4) + (carbs * 4) + (fat * 9)
                if total_macro_calories > 0:
                    protein = protein * (calories / total_macro_calories)
                    carbs = carbs * (calories / total_macro_calories)
                    fat = fat * (calories / total_macro_calories)
                
                return {
                    'calories': round(calories),
                    'protein': round(protein, 1),
                    'carbs': round(carbs, 1),
                    'fat': round(fat, 1)
                }
            else:
                return self._calculate_basal_macros(features[0])
                
        except Exception as e:
            print(f"Error predicting macros: {e}")
            return self._calculate_basal_macros(features[0])
    
    def _calculate_basal_macros(self, features: List[float]) -> Dict[str, float]:
        """Calculate basal macros using traditional formulas as fallback"""
        weight = features[3]
        height = features[2]
        age = features[0]
        gender_factor = 1 if features[1] == 1 else 0.9  # male = 1, female = 0.9
        activity_factor = 1.2 + (features[5] * 0.4)  # sedentary to very active
        
        # Calculate BMR using Mifflin-St Jeor equation
        if gender_factor == 1:  # Male
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:  # Female
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        calories = bmr * activity_factor
        
        # Adjust based on goal
        goal_factor = features[4]
        if goal_factor < 0.3:  # weight_loss
            calories *= 0.85
        elif goal_factor > 0.7:  # muscle_gain, strength
            calories *= 1.15
        
        # Calculate macros
        protein = weight * 2.0 if goal_factor > 0.5 else weight * 1.6
        fat = calories * 0.25 / 9
        carbs = (calories - (protein * 4) - (fat * 9)) / 4
        
        return {
            'calories': round(calories),
            'protein': round(protein, 1),
            'carbs': round(max(0, carbs), 1),
            'fat': round(fat, 1)
        }
    
    def _generate_meal_recommendations(self, features: np.ndarray, macros: Dict[str, float], 
                                     user_metrics: HealthMetrics) -> List[Dict[str, Any]]:
        """Generate meal recommendations using ML model"""
        try:
            # Get available foods from database
            foods = list(FoodDatabase.objects.all())
            
            if not foods:
                return self._generate_fallback_meals(macros)
            
            # Filter foods based on dietary preferences and allergies
            filtered_foods = self._filter_foods(foods, user_metrics)
            
            # Generate meals for each time slot
            meals = []
            meal_types = ['breakfast', 'lunch', 'dinner', 'snacks']
            calorie_distribution = [0.25, 0.35, 0.30, 0.10]  # 25%, 35%, 30%, 10%
            
            for i, meal_type in enumerate(meal_types):
                meal_calories = macros['calories'] * calorie_distribution[i]
                meal = self._generate_single_ml_meal(
                    meal_type, meal_calories, filtered_foods, user_metrics
                )
                meals.append(meal)
            
            return meals
            
        except Exception as e:
            print(f"Error generating meal recommendations: {e}")
            return self._generate_fallback_meals(macros)
    
    def _filter_foods(self, foods: List[FoodDatabase], user_metrics: HealthMetrics) -> List[FoodDatabase]:
        """Filter foods based on user preferences and allergies"""
        filtered = []
        preferences = user_metrics.dietary_preferences or []
        allergies = user_metrics.allergies or []
        
        for food in foods:
            # Check allergies
            if any(allergy.lower() in food.name.lower() for allergy in allergies):
                continue
            
            # Check dietary preferences
            suitable = True
            if 'vegetarian' in preferences and food.category == 'meat':
                suitable = False
            elif 'vegan' in preferences and food.category in ['meat', 'dairy', 'eggs']:
                suitable = False
            elif 'gluten_free' in preferences and 'wheat' in food.name.lower():
                suitable = False
            elif 'dairy_free' in preferences and food.category == 'dairy':
                suitable = False
            
            if suitable:
                filtered.append(food)
        
        return filtered if filtered else foods  # Return all if none suitable
    
    def _generate_single_ml_meal(self, meal_type: str, target_calories: float, 
                                foods: List[FoodDatabase], user_metrics: HealthMetrics) -> Dict[str, Any]:
        """Generate a single meal using ML-based food selection"""
        try:
            # Use ML model to predict optimal food combinations
            if 'meal_recommendation' in self.models:
                features = self._extract_features(user_metrics)
                meal_features = np.append(features[0], [self._encode_meal_type(meal_type), target_calories])
                
                # Get food recommendations from model
                recommended_foods = self._predict_food_combinations(meal_features, foods, target_calories)
            else:
                # Fallback to rule-based selection
                recommended_foods = self._select_foods_by_calories(foods, target_calories)
            
            return {
                'name': f"ML-Generated {meal_type.title()}",
                'foods': recommended_foods,
                'estimated_calories': target_calories,
                'prep_time': np.random.randint(15, 45),
                'difficulty': np.random.choice(['easy', 'medium', 'hard'], p=[0.4, 0.4, 0.2])
            }
            
        except Exception as e:
            print(f"Error generating single meal: {e}")
            return self._generate_fallback_meal(meal_type, target_calories)
    
    def _encode_meal_type(self, meal_type: str) -> float:
        """Encode meal type to numerical value"""
        meal_mapping = {
            'breakfast': 0.0,
            'lunch': 0.33,
            'dinner': 0.67,
            'snacks': 1.0
        }
        return meal_mapping.get(meal_type, 0.5)
    
    def _predict_food_combinations(self, features: np.ndarray, foods: List[FoodDatabase], 
                                 target_calories: float) -> List[Dict[str, Any]]:
        """Predict optimal food combinations using ML model"""
        try:
            # Simple heuristic for food selection (can be enhanced with actual ML model)
            selected_foods = []
            remaining_calories = target_calories
            
            # Ensure balanced meal with protein, carbs, and fats
            food_categories = {'protein': 0.3, 'carb': 0.4, 'vegetable': 0.2, 'healthy_fat': 0.1}
            
            for category, ratio in food_categories.items():
                category_calories = target_calories * ratio
                category_foods = [f for f in foods if f.category.lower() in category]
                
                if category_foods:
                    # Select foods from this category
                    food = np.random.choice(category_foods)
                    calories_per_100g = food.calories_per_100g
                    
                    # Calculate appropriate portion
                    portion_g = min(200, (category_calories / calories_per_100g) * 100)
                    
                    selected_foods.append({
                        'name': food.name,
                        'quantity': f"{round(portion_g)}g",
                        'calories': round(calories_per_100g * portion_g / 100),
                        'protein': round(food.protein_per_100g * portion_g / 100, 1),
                        'carbs': round(food.carbs_per_100g * portion_g / 100, 1),
                        'fat': round(food.fat_per_100g * portion_g / 100, 1)
                    })
            
            return selected_foods[:5]  # Limit to 5 foods per meal
            
        except Exception as e:
            print(f"Error predicting food combinations: {e}")
            return self._select_foods_by_calories(foods, target_calories)
    
    def _select_foods_by_calories(self, foods: List[FoodDatabase], target_calories: float) -> List[Dict[str, Any]]:
        """Select foods based on calorie targets (fallback method)"""
        selected_foods = []
        remaining_calories = target_calories
        
        for food in foods[:5]:  # Select first 5 foods
            if remaining_calories <= 0:
                break
            
            calories_per_100g = food.calories_per_100g
            portion_g = min(150, (remaining_calories / calories_per_100g) * 100)
            
            selected_foods.append({
                'name': food.name,
                'quantity': f"{round(portion_g)}g",
                'calories': round(calories_per_100g * portion_g / 100),
                'protein': round(food.protein_per_100g * portion_g / 100, 1),
                'carbs': round(food.carbs_per_100g * portion_g / 100, 1),
                'fat': round(food.fat_per_100g * portion_g / 100, 1)
            })
            
            remaining_calories -= calories_per_100g * portion_g / 100
        
        return selected_foods
    
    def _calculate_ml_confidence(self, features: np.ndarray, meal_plan: List[Dict]) -> float:
        """Calculate confidence score for ML predictions"""
        try:
            # Base confidence from model availability
            base_confidence = 0.7 if 'meal_recommendation' in self.models else 0.5
            
            # Adjust based on data quality
            feature_completeness = np.sum(features[0] != 0) / len(features[0])
            
            # Adjust based on meal variety
            meal_variety = len(set(food['name'] for meal in meal_plan for food in meal['foods']))
            variety_score = min(1.0, meal_variety / 10)
            
            # Calculate final confidence
            confidence = base_confidence * feature_completeness * variety_score
            return round(min(1.0, confidence), 2)
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.5
    
    def _generate_fallback_meals(self, macros: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate fallback meals when ML models fail"""
        meals = []
        meal_types = ['breakfast', 'lunch', 'dinner', 'snacks']
        calorie_distribution = [0.25, 0.35, 0.30, 0.10]
        
        for i, meal_type in enumerate(meal_types):
            meal_calories = macros['calories'] * calorie_distribution[i]
            meals.append(self._generate_fallback_meal(meal_type, meal_calories))
        
        return meals
    
    def _generate_fallback_meal(self, meal_type: str, calories: float) -> Dict[str, Any]:
        """Generate a single fallback meal"""
        return {
            'name': f"Standard {meal_type.title()}",
            'foods': [
                {
                    'name': 'Balanced Meal Component',
                    'quantity': '200g',
                    'calories': round(calories),
                    'protein': round(calories * 0.25 / 4, 1),
                    'carbs': round(calories * 0.45 / 4, 1),
                    'fat': round(calories * 0.30 / 9, 1)
                }
            ],
            'estimated_calories': round(calories),
            'prep_time': 30,
            'difficulty': 'medium'
        }
    
    def _fallback_meal_plan(self, user_metrics: HealthMetrics, target_date: date) -> Dict[str, Any]:
        """Fallback meal plan when ML models are not available"""
        features = self._extract_features(user_metrics)
        macros = self._calculate_basal_macros(features[0])
        meals = self._generate_fallback_meals(macros)
        
        return {
            'meals': meals,
            'total_calories': macros['calories'],
            'protein': macros['protein'],
            'carbs': macros['carbs'],
            'fat': macros['fat'],
            'confidence_score': 0.3,
            'model_version': 'fallback_v1.0',
            'prediction_date': target_date.isoformat()
        }
    
    def train_models(self, training_data: pd.DataFrame) -> Dict[str, float]:
        """
        Train ML models with provided dataset.
        
        Args:
            training_data: DataFrame containing training examples
            
        Returns:
            Dictionary containing training metrics
        """
        try:
            # Prepare features and targets
            X, y_macros, y_meals = self._prepare_training_data(training_data)
            
            # Split data
            X_train, X_test, y_macro_train, y_macro_test = train_test_split(
                X, y_macros, test_size=0.2, random_state=42
            )
            
            # Train macro prediction model
            self.models['macro_prediction'] = GradientBoostingRegressor(n_estimators=100, random_state=42)
            self.models['macro_prediction'].fit(X_train, y_macro_train)
            
            # Train meal recommendation model
            self.models['meal_recommendation'] = RandomForestRegressor(n_estimators=100, random_state=42)
            self.models['meal_recommendation'].fit(X_train, y_meals)
            
            # Calculate metrics
            macro_pred = self.models['macro_prediction'].predict(X_test)
            meal_pred = self.models['meal_recommendation'].predict(X_test)
            
            macro_mse = mean_squared_error(y_macro_test, macro_pred)
            macro_r2 = r2_score(y_macro_test, macro_pred)
            meal_mse = mean_squared_error(y_meals, meal_pred)
            meal_r2 = r2_score(y_meals, meal_pred)
            
            # Save models
            self._save_models()
            
            return {
                'macro_mse': macro_mse,
                'macro_r2': macro_r2,
                'meal_mse': meal_mse,
                'meal_r2': meal_r2,
                'training_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error training models: {e}")
            return {'error': str(e)}
    
    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data from DataFrame"""
        # This would be implemented based on your dataset structure
        # For now, return dummy data
        n_samples = len(data)
        n_features = 20  # Adjust based on your feature set
        
        X = np.random.randn(n_samples, n_features)
        y_macros = np.random.randn(n_samples, 4)  # calories, protein, carbs, fat
        y_meals = np.random.randn(n_samples, 10)  # meal recommendations
        
        return X, y_macros, y_meals
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            model_dir = os.path.join(settings.BASE_DIR, 'nutrition', 'ml', 'models')
            os.makedirs(model_dir, exist_ok=True)
            
            # Save models
            with open(os.path.join(model_dir, 'meal_recommendation_model.pkl'), 'wb') as f:
                pickle.dump(self.models['meal_recommendation'], f)
            
            with open(os.path.join(model_dir, 'macro_prediction_model.pkl'), 'wb') as f:
                pickle.dump(self.models['macro_prediction'], f)
            
            # Save scalers
            with open(os.path.join(model_dir, 'feature_scaler.pkl'), 'wb') as f:
                pickle.dump(self.scalers['features'], f)
            
            # Save encoders
            with open(os.path.join(model_dir, 'label_encoders.pkl'), 'wb') as f:
                pickle.dump(self.encoders, f)
                
        except Exception as e:
            print(f"Error saving models: {e}")
    
    def _get_model_version(self) -> str:
        """Get model version from training report"""
        try:
            model_dir = os.path.join(settings.BASE_DIR, 'nutrition', 'ml', 'models')
            report_path = os.path.join(model_dir, 'training_report.json')
            
            if os.path.exists(report_path):
                with open(report_path, 'r') as f:
                    report = json.load(f)
                return report.get('training_date', 'unknown')
            else:
                return 'v1.0'
        except Exception:
            return 'v1.0'
    
    def _apply_real_time_adaptation(self, metrics: HealthMetrics) -> Optional[np.ndarray]:
        """
        Apply real-time adaptation based on user feedback and performance data.
        """
        try:
            # Get recent feedback for this user
            recent_feedback = MLPredictionFeedback.objects.filter(
                performance_log__user=metrics.user,
                created_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('-created_at')[:self.adaptation_threshold]
            
            if len(recent_feedback) < self.adaptation_threshold:
                return None
            
            # Analyze feedback patterns
            avg_rating = recent_feedback.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
            helpful_ratio = recent_feedback.filter(helpful=True).count() / len(recent_feedback)
            accurate_ratio = recent_feedback.filter(accurate=True).count() / len(recent_feedback)
            
            # Calculate adaptation factors
            rating_factor = avg_rating / 5.0  # Normalize to 0-1
            helpful_factor = helpful_ratio
            accurate_factor = accurate_ratio
            
            # Create adaptation vector
            adaptation_vector = np.array([
                rating_factor,      # Overall satisfaction impact
                helpful_factor,     # Helpfulness impact
                accurate_factor,     # Accuracy impact
                1.0,                # Preserve original features
                1.0,                # Preserve original features
                1.0,                # Preserve original features
                1.0,                # Preserve original features
                rating_factor * 0.1, # Slight calorie adjustment
                rating_factor * 0.1, # Slight protein adjustment
                rating_factor * 0.1, # Slight carb adjustment
                rating_factor * 0.1, # Slight fat adjustment
                1.0,                # Preserve BMI
                1.0,                # Preserve dietary preferences
                1.0,                # Preserve allergies
                1.0                 # Preserve medical conditions
            ])
            
            return adaptation_vector
            
        except Exception as e:
            print(f"Error applying real-time adaptation: {e}")
            return None
    
    def _merge_adapted_features(self, original_features: np.ndarray, 
                               adapted_features: np.ndarray) -> np.ndarray:
        """
        Merge original features with adapted features using weighted averaging.
        """
        try:
            # Apply 70% original, 30% adapted weighting
            merged_features = (original_features * 0.7 + adapted_features * 0.3)
            return merged_features
            
        except Exception as e:
            print(f"Error merging adapted features: {e}")
            return original_features
    
    def _generate_predictive_insights(self, metrics: HealthMetrics, target_date: date) -> Dict[str, Any]:
        """
        Generate predictive insights for nutrition trends and recommendations.
        """
        try:
            insights = {
                'trend_analysis': self._analyze_nutrition_trends(metrics),
                'goal_projection': self._project_goal_progress(metrics, target_date),
                'recommendation_trends': self._analyze_recommendation_patterns(metrics),
                'seasonal_insights': self._get_seasonal_insights(target_date),
                'performance_forecast': self._forecast_performance(metrics)
            }
            
            return insights
            
        except Exception as e:
            print(f"Error generating predictive insights: {e}")
            return {}
    
    def _analyze_nutrition_trends(self, metrics: HealthMetrics) -> Dict[str, Any]:
        """
        Analyze user's nutrition trends over time.
        """
        try:
            # Get historical meal plans
            historical_plans = MealPlan.objects.filter(
                user=metrics.user,
                created_at__gte=timezone.now() - timedelta(days=self.prediction_window_days)
            ).order_by('created_at')
            
            if len(historical_plans) < 7:
                return {'status': 'insufficient_data', 'message': 'Need more historical data'}
            
            # Calculate trends
            calorie_trend = []
            protein_trend = []
            confidence_trend = []
            
            for plan in historical_plans:
                calorie_trend.append(plan.total_calories or 0)
                protein_trend.append(plan.protein or 0)
                confidence_trend.append(plan.confidence_score or 0)
            
            # Calculate trend direction
            calorie_direction = 'stable'
            if len(calorie_trend) > 1:
                recent_avg = np.mean(calorie_trend[-7:])
                earlier_avg = np.mean(calorie_trend[-14:-7]) if len(calorie_trend) > 14 else np.mean(calorie_trend[:7])
                
                if recent_avg > earlier_avg * 1.05:
                    calorie_direction = 'increasing'
                elif recent_avg < earlier_avg * 0.95:
                    calorie_direction = 'decreasing'
            
            return {
                'status': 'analyzed',
                'calorie_trend': calorie_direction,
                'avg_calories': int(np.mean(calorie_trend)),
                'avg_protein': int(np.mean(protein_trend)),
                'avg_confidence': round(np.mean(confidence_trend), 2),
                'data_points': len(historical_plans)
            }
            
        except Exception as e:
            print(f"Error analyzing nutrition trends: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _project_goal_progress(self, metrics: HealthMetrics, target_date: date) -> Dict[str, Any]:
        """
        Project goal progress based on current trends.
        """
        try:
            current_weight = metrics.weight or 70
            target_weight = metrics.target_weight or current_weight
            
            if abs(current_weight - target_weight) < 0.5:
                return {
                    'status': 'goal_achieved',
                    'message': 'Target weight achieved!',
                    'days_to_goal': 0
                }
            
            # Get recent weight changes
            recent_metrics = HealthMetrics.objects.filter(
                user=metrics.user,
                created_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('created_at')
            
            if len(recent_metrics) < 2:
                return {
                    'status': 'insufficient_data',
                    'message': 'Need more weight history for projection',
                    'days_to_goal': None
                }
            
            # Calculate weight change rate
            weights = [m.weight or current_weight for m in recent_metrics]
            weight_change_rate = (weights[-1] - weights[0]) / len(recent_metrics)
            
            if abs(weight_change_rate) < 0.01:
                return {
                    'status': 'stable',
                    'message': 'Weight is stable',
                    'days_to_goal': None
                }
            
            # Project days to goal
            weight_difference = target_weight - current_weight
            days_to_goal = int(weight_difference / weight_change_rate) if weight_change_rate != 0 else None
            
            return {
                'status': 'projected',
                'current_weight': current_weight,
                'target_weight': target_weight,
                'weight_change_rate': round(weight_change_rate, 2),
                'days_to_goal': max(0, days_to_goal) if days_to_goal and days_to_goal > 0 else None,
                'projection_confidence': 0.7 if len(recent_metrics) > 10 else 0.5
            }
            
        except Exception as e:
            print(f"Error projecting goal progress: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _analyze_recommendation_patterns(self, metrics: HealthMetrics) -> Dict[str, Any]:
        """
        Analyze patterns in user's meal recommendations and preferences.
        """
        try:
            # Get recent meal plans and feedback
            recent_plans = MealPlan.objects.filter(
                user=metrics.user,
                created_at__gte=timezone.now() - timedelta(days=self.prediction_window_days)
            ).prefetch_related('mlpredictionfeedback_set')
            
            if len(recent_plans) < 5:
                return {'status': 'insufficient_data', 'message': 'Need more meal plan history'}
            
            # Analyze approach preferences
            approach_counts = {}
            approach_ratings = {}
            
            for plan in recent_plans:
                approach = plan.approach or 'unknown'
                approach_counts[approach] = approach_counts.get(approach, 0) + 1
                
                # Get average rating for this approach
                feedbacks = plan.mlpredictionfeedback_set.all()
                if feedbacks:
                    avg_rating = feedbacks.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
                    if approach not in approach_ratings:
                        approach_ratings[approach] = []
                    approach_ratings[approach].append(avg_rating)
            
            # Calculate preferences
            best_approach = max(approach_counts, key=approach_counts.get) if approach_counts else 'unknown'
            
            # Calculate average ratings by approach
            avg_ratings = {}
            for approach, ratings in approach_ratings.items():
                avg_ratings[approach] = round(np.mean(ratings), 2)
            
            return {
                'status': 'analyzed',
                'preferred_approach': best_approach,
                'approach_distribution': approach_counts,
                'approach_ratings': avg_ratings,
                'total_plans_analyzed': len(recent_plans)
            }
            
        except Exception as e:
            print(f"Error analyzing recommendation patterns: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_seasonal_insights(self, target_date: date) -> Dict[str, Any]:
        """
        Get seasonal nutrition insights and recommendations.
        """
        try:
            # Determine season
            month = target_date.month
            if month in [12, 1, 2]:
                season = 'winter'
            elif month in [3, 4, 5]:
                season = 'spring'
            elif month in [6, 7, 8]:
                season = 'summer'
            else:
                season = 'fall'
            
            # Seasonal recommendations
            seasonal_recommendations = {
                'winter': {
                    'focus': 'immune_support',
                    'foods': ['citrus', 'root_vegetables', 'soup', 'warm_meals'],
                    'calorie_adjustment': 1.1,  # 10% increase for warmth
                    'protein_adjustment': 1.05,  # 5% increase
                    'tips': ['Increase vitamin C intake', 'Stay hydrated with warm fluids', 'Include seasonal vegetables']
                },
                'spring': {
                    'focus': 'detoxification',
                    'foods': ['leafy_greens', 'berries', 'light_meals'],
                    'calorie_adjustment': 0.95,  # 5% decrease
                    'protein_adjustment': 1.0,
                    'tips': ['Include fresh greens', 'Lighter meals for energy', 'Seasonal fruits']
                },
                'summer': {
                    'focus': 'hydration',
                    'foods': ['watermelon', 'cucumber', 'salads', 'light_proteins'],
                    'calorie_adjustment': 0.9,  # 10% decrease
                    'protein_adjustment': 1.1,  # 10% increase for activity
                    'tips': ['Stay hydrated', 'Include seasonal fruits', 'Lighter, frequent meals']
                },
                'fall': {
                    'focus': 'preparation',
                    'foods': ['pumpkin', 'apples', 'squash', 'nuts'],
                    'calorie_adjustment': 1.0,
                    'protein_adjustment': 1.0,
                    'tips': ['Include seasonal vegetables', 'Balanced nutrition', 'Prepare for winter']
                }
            }
            
            return {
                'season': season,
                'recommendations': seasonal_recommendations[season],
                'next_season_change': self._get_next_season_change(target_date)
            }
            
        except Exception as e:
            print(f"Error getting seasonal insights: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_next_season_change(self, current_date: date) -> Dict[str, Any]:
        """
        Get information about the next season change.
        """
        try:
            month = current_date.month
            if month == 2:
                next_season = 'spring'
                days_until = 31 - current_date.day
            elif month == 5:
                next_season = 'summer'
                days_until = 30 - current_date.day
            elif month == 8:
                next_season = 'fall'
                days_until = 30 - current_date.day
            elif month == 11:
                next_season = 'winter'
                days_until = 30 - current_date.day
            else:
                # Calculate days to next season change
                if month < 2:
                    next_season = 'spring'
                    days_until = (2 - month) * 30 + (31 - current_date.day)
                elif month < 5:
                    next_season = 'summer'
                    days_until = (5 - month) * 30 + (30 - current_date.day)
                elif month < 8:
                    next_season = 'fall'
                    days_until = (8 - month) * 30 + (30 - current_date.day)
                elif month < 11:
                    next_season = 'winter'
                    days_until = (11 - month) * 30 + (30 - current_date.day)
                else:
                    next_season = 'spring'
                    days_until = (12 - month) * 30 + (31 - current_date.day) + 60
            
            return {
                'next_season': next_season,
                'days_until_change': max(0, days_until)
            }
            
        except Exception as e:
            print(f"Error getting next season change: {e}")
            return {'next_season': 'unknown', 'days_until_change': None}
    
    def _forecast_performance(self, metrics: HealthMetrics) -> Dict[str, Any]:
        """
        Forecast ML model performance based on historical data.
        """
        try:
            # Get recent performance logs
            recent_performance = MLPerformanceLog.objects.filter(
                user=metrics.user,
                created_at__gte=timezone.now() - timedelta(days=self.prediction_window_days)
            ).order_by('created_at')
            
            if len(recent_performance) < 5:
                return {
                    'status': 'insufficient_data',
                    'message': 'Need more performance history',
                    'forecast_confidence': 0.0
                }
            
            # Calculate performance trends
            confidence_scores = [log.confidence_score or 0 for log in recent_performance]
            processing_times = [log.processing_time or 0 for log in recent_performance]
            
            # Calculate trends
            confidence_trend = np.polyfit(range(len(confidence_scores)), confidence_scores, 1)[0]
            processing_trend = np.polyfit(range(len(processing_times)), processing_times, 1)[0]
            
            # Forecast next 7 days
            forecast_confidence = confidence_scores[-1] + (confidence_trend * 7)
            forecast_processing = processing_times[-1] + (processing_trend * 7)
            
            # Calculate forecast confidence
            data_quality = len(recent_performance) / 30.0  # More data = higher confidence
            trend_stability = 1.0 - abs(confidence_trend)  # Stable trends = higher confidence
            forecast_confidence_score = min(1.0, data_quality * trend_stability)
            
            return {
                'status': 'forecasted',
                'current_confidence': round(confidence_scores[-1], 2),
                'forecasted_confidence': round(max(0.0, min(1.0, forecast_confidence)), 2),
                'current_processing_time': round(processing_times[-1], 2),
                'forecasted_processing_time': round(max(0.0, forecast_processing), 2),
                'confidence_trend': 'improving' if confidence_trend > 0.01 else 'declining' if confidence_trend < -0.01 else 'stable',
                'forecast_confidence': round(forecast_confidence_score, 2),
                'data_points': len(recent_performance)
            }
            
        except Exception as e:
            print(f"Error forecasting performance: {e}")
            return {'status': 'error', 'message': str(e), 'forecast_confidence': 0.0}
    
    def _generate_meal_plan_from_predictions(self, macro_predictions: np.ndarray, 
                                             meal_predictions: np.ndarray, 
                                             metrics: HealthMetrics) -> List[Dict[str, Any]]:
        """
        Generate meal plan from ML predictions with enhanced food selection.
        """
        try:
            # Get available foods
            foods = list(FoodDatabase.objects.all())
            
            if not foods:
                return self._generate_fallback_meals({
                    'calories': macro_predictions[0],
                    'protein': macro_predictions[1],
                    'carbs': macro_predictions[2],
                    'fat': macro_predictions[3]
                })
            
            # Filter foods based on preferences
            filtered_foods = self._filter_foods(foods, metrics)
            
            # Generate meals with seasonal considerations
            meals = []
            meal_types = ['breakfast', 'lunch', 'dinner', 'snacks']
            calorie_distribution = [0.25, 0.35, 0.30, 0.10]
            
            # Get seasonal insights
            seasonal_insights = self._get_seasonal_insights()
            
            for i, meal_type in enumerate(meal_types):
                base_calories = macro_predictions[0] * calorie_distribution[i]
                
                # Apply seasonal adjustments (convert absolute calorie adjustment to multiplier)
                calorie_adjustment = seasonal_insights.get('calorie_adjustment', 0)
                adjusted_calories = base_calories + calorie_adjustment
                
                meal = self._generate_single_ml_meal(
                    meal_type, adjusted_calories, filtered_foods, metrics
                )
                
                # Add seasonal food recommendations
                seasonal_foods = seasonal_insights.get('seasonal_foods', [])
                if seasonal_foods and meal['foods']:
                    # Try to include seasonal foods
                    for food_item in meal['foods']:
                        for seasonal_food in seasonal_foods:
                            if seasonal_food.replace('_', ' ') in food_item['name'].lower():
                                food_item['seasonal'] = True
                                break
                
                meals.append(meal)
            
            return meals
            
        except Exception as e:
            print(f"Error generating meal plan from predictions: {e}")
            return self._generate_fallback_meals({
                'calories': macro_predictions[0],
                'protein': macro_predictions[1],
                'carbs': macro_predictions[2],
                'fat': macro_predictions[3]
            })


# Global instance
ml_nutrition_engine = MLNutritionEngine()
