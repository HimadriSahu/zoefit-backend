#!/usr/bin/env python
"""
Simple test to verify ML engine core functionality without Django
"""

import os
import sys
import pickle
import json
import numpy as np
from datetime import date

# Add the zoefit directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'zoefit'))

def test_ml_core():
    """Test ML engine core functionality"""
    print("Testing ML Engine Core Functionality...")
    
    try:
        # Path to models
        model_dir = os.path.join('zoefit', 'nutrition', 'ml', 'models')
        
        # Check if model files exist
        meal_model_path = os.path.join(model_dir, 'meal_recommendation_model.pkl')
        macro_model_path = os.path.join(model_dir, 'macro_prediction_model.pkl')
        scaler_path = os.path.join(model_dir, 'feature_scaler.pkl')
        
        print(f"Checking model files:")
        print(f"  Meal model: {os.path.exists(meal_model_path)}")
        print(f"  Macro model: {os.path.exists(macro_model_path)}")
        print(f"  Scaler: {os.path.exists(scaler_path)}")
        
        if not all([os.path.exists(meal_model_path), os.path.exists(macro_model_path), os.path.exists(scaler_path)]):
            print("❌ Missing model files")
            return False
        
        # Load models
        print("\nLoading models...")
        with open(meal_model_path, 'rb') as f:
            meal_model = pickle.load(f)
        with open(macro_model_path, 'rb') as f:
            macro_model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        # Load training report
        with open(os.path.join(model_dir, 'training_report.json'), 'r') as f:
            report = json.load(f)
        
        print("✅ Models loaded successfully")
        
        # Test feature extraction (simulate user data)
        print("\nTesting feature extraction...")
        
        # Simulate enhanced features extraction
        features = {}
        
        # Basic demographics
        features['age'] = 30
        features['gender_encoded'] = 1  # male
        features['height'] = 175
        features['weight'] = 70
        
        # Calculate BMI
        height_m = features['height'] / 100
        weight = features['weight']
        bmi = weight / (height_m ** 2)
        features['bmi'] = bmi
        
        # Goal and activity
        features['fitness_goal_encoded'] = 0.0  # weight_loss
        features['activity_level_encoded'] = 0.5  # moderate
        
        # Target metrics
        features['target_weight'] = 68
        
        # Dietary preferences
        preferences = ['vegetarian']
        diet_types = ['vegetarian', 'vegan', 'gluten_free', 'dairy_free']
        for diet_type in diet_types:
            features[f'dietary_preferences_{diet_type}'] = 1 if diet_type in preferences else 0
        
        # Create a single dietary_preferences_encoded feature
        features['dietary_preferences_encoded'] = sum([
            features.get('dietary_preferences_vegetarian', 0),
            features.get('dietary_preferences_vegan', 0),
            features.get('dietary_preferences_gluten_free', 0),
            features.get('dietary_preferences_dairy_free', 0)
        ])
        
        # Count features
        features['allergies_count'] = 1  # nuts allergy
        features['medical_conditions_count'] = 0
        
        # Enhanced engineered features
        # BMI categories
        if bmi < 18.5:
            bmi_category = 0
        elif bmi < 25:
            bmi_category = 1
        elif bmi < 30:
            bmi_category = 2
        else:
            bmi_category = 3
        features['bmi_category_encoded'] = bmi_category
        
        # Age groups
        age = features['age']
        if age < 25:
            age_group = 0
        elif age < 35:
            age_group = 1
        elif age < 50:
            age_group = 2
        elif age < 65:
            age_group = 3
        else:
            age_group = 4
        features['age_group_encoded'] = age_group
        
        # Weight change metrics
        target_weight = features['target_weight']
        weight_diff = target_weight - weight
        features['weight_difference'] = weight_diff
        features['weight_change_percent'] = (weight_diff / weight * 100) if weight > 0 else 0
        features['weight_change_needed'] = 1 if weight_diff > 0 else 0
        
        # Activity multiplier
        activity_multipliers = {
            'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55,
            'active': 1.725, 'very_active': 1.9
        }
        features['activity_multiplier'] = activity_multipliers.get('moderate', 1.55)
        
        # Goal difficulty
        goal_difficulty = {
            'maintenance': 1, 'endurance': 2, 'strength': 3,
            'muscle_gain': 4, 'weight_loss': 5
        }
        features['goal_difficulty'] = goal_difficulty.get('weight_loss', 3)
        
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
        
        # Nutritional ratios
        features['carb_calorie_ratio'] = 0.55
        
        # Convert to array in correct order
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
        
        # Fill missing features with 0
        feature_array = []
        for feature_name in feature_order:
            feature_array.append(features.get(feature_name, 0))
        
        features_array = np.array(feature_array).reshape(1, -1)
        print(f"✅ Feature extraction successful - Shape: {features_array.shape}")
        
        # Test scaling
        scaled_features = scaler.transform(features_array)
        print(f"✅ Feature scaling successful - Shape: {scaled_features.shape}")
        
        # Test predictions
        macro_predictions = macro_model.predict(scaled_features)[0]
        meal_predictions = meal_model.predict(scaled_features)[0]
        
        print(f"✅ Predictions successful:")
        print(f"  Macros: Calories={macro_predictions[0]:.0f}, Protein={macro_predictions[1]:.1f}g, Carbs={macro_predictions[2]:.1f}g, Fat={macro_predictions[3]:.1f}g")
        print(f"  Meal predictions shape: {meal_predictions.shape}")
        
        # Test confidence calculation
        feature_std = np.std(scaled_features)
        base_confidence = 0.85
        if feature_std < 2.0:
            confidence_adjustment = 0.10
        elif feature_std < 3.0:
            confidence_adjustment = 0.05
        else:
            confidence_adjustment = -0.05
        
        confidence = max(0.3, min(0.95, base_confidence + confidence_adjustment))
        print(f"✅ Confidence calculation: {confidence:.3f}")
        
        print(f"\n✅ All tests passed!")
        print(f"Model version: {report.get('model_version', 'unknown')}")
        print(f"Macro R²: {report['model_performance']['macro_prediction']['r2_score']:.4f}")
        print(f"Meal R²: {report['model_performance']['meal_recommendation']['r2_score']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_core()
    sys.exit(0 if success else 1)
