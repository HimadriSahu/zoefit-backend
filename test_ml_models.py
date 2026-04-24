#!/usr/bin/env python
"""
Simple test to verify ML models can be loaded
"""

import os
import sys
import pickle
import numpy as np

def test_model_loading():
    """Test if ML models can be loaded and used for predictions"""
    print("Testing ML Model Loading...")
    
    try:
        # Path to models
        model_dir = os.path.join(os.path.dirname(__file__), 'zoefit', 'nutrition', 'ml', 'models')
        
        # Load meal recommendation model
        meal_model_path = os.path.join(model_dir, 'meal_recommendation_model.pkl')
        print(f"Loading meal recommendation model from: {meal_model_path}")
        
        with open(meal_model_path, 'rb') as f:
            meal_model = pickle.load(f)
        print("✅ Meal recommendation model loaded successfully")
        
        # Load macro prediction model
        macro_model_path = os.path.join(model_dir, 'macro_prediction_model.pkl')
        print(f"Loading macro prediction model from: {macro_model_path}")
        
        with open(macro_model_path, 'rb') as f:
            macro_model = pickle.load(f)
        print("✅ Macro prediction model loaded successfully")
        
        # Load feature scaler
        scaler_path = os.path.join(model_dir, 'feature_scaler.pkl')
        print(f"Loading feature scaler from: {scaler_path}")
        
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        print("✅ Feature scaler loaded successfully")
        
        # Load training report
        import json
        report_path = os.path.join(model_dir, 'training_report.json')
        print(f"Loading training report from: {report_path}")
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        print("✅ Training report loaded successfully")
        
        # Test prediction with dummy data
        print("\nTesting model predictions...")
        
        # Create dummy features (26 features as expected by models)
        dummy_features = np.array([[
            30,      # age
            170,     # height
            70,      # weight
            24.2,    # bmi
            68,      # target_weight
            0,       # allergies_count
            0,       # medical_conditions_count
            1,       # gender_encoded (male)
            0.5,     # fitness_goal_encoded
            0.5,     # activity_level_encoded
            0,       # dietary_preferences_encoded
            1,       # bmi_category_encoded (normal)
            1,       # age_group_encoded (adult)
            -2,      # weight_difference
            -2.8,    # weight_change_percent
            0,       # weight_change_needed
            1.55,    # activity_multiplier
            3,       # goal_difficulty
            0.25,    # goal_activity_encoded
            0.5,     # age_goal_encoded
            0.5,     # bmi_goal_encoded
            0.5,     # gender_goal_encoded
            2,       # bmi_risk_score
            0,       # age_risk_factor
            2,       # total_health_risk
            0.55     # carb_calorie_ratio
        ]])
        
        print(f"Dummy features shape: {dummy_features.shape}")
        
        # Scale features
        scaled_features = scaler.transform(dummy_features)
        print(f"Scaled features shape: {scaled_features.shape}")
        
        # Make predictions
        macro_predictions = macro_model.predict(scaled_features)[0]
        print(f"Macro predictions: {macro_predictions}")
        
        meal_predictions = meal_model.predict(scaled_features)[0]
        print(f"Meal predictions: {meal_predictions}")
        
        print("\n✅ Model predictions successful!")
        print(f"Model version: {report.get('model_version', 'unknown')}")
        print(f"Training date: {report.get('training_date', 'unknown')}")
        print(f"Macro R² score: {report['model_performance']['macro_prediction']['r2_score']:.4f}")
        print(f"Meal R² score: {report['model_performance']['meal_recommendation']['r2_score']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing ML models: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_loading()
    sys.exit(0 if success else 1)
