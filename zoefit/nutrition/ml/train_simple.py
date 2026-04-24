#!/usr/bin/env python
"""
Simple training script for enhanced ML models with proper model saving
"""

import os
import sys
import json
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.multioutput import MultiOutputRegressor
import pickle

# Add Django project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
import django
django.setup()

from nutrition.ml.training_data_handler import TrainingDataHandler
from django.conf import settings


class SimpleModelTrainer:
    """Simple trainer with enhanced features and proper model saving"""
    
    def __init__(self):
        self.data_handler = TrainingDataHandler()
    
    def train_and_save_models(self):
        """Train models with enhanced features and save properly"""
        print("=" * 50)
        print("SIMPLE ENHANCED MODEL TRAINING")
        print("=" * 50)
        
        try:
            # Create realistic dataset
            print("1. Creating realistic dataset...")
            df = self.data_handler._create_realistic_dataset(n_samples=2000)
            
            # Preprocess data
            print("2. Preprocessing data...")
            df_processed, preprocessing_info = self.data_handler.preprocess_data(df)
            
            # Prepare training data
            print("3. Preparing training data...")
            X, y_macros, y_meals = self.data_handler.prepare_training_data(df_processed)
            
            if X.shape[0] == 0:
                raise ValueError("No training data prepared")
            
            print(f"   Features shape: {X.shape}")
            print(f"   Macro targets shape: {y_macros.shape}")
            print(f"   Meal targets shape: {y_meals.shape}")
            
            # Split data
            X_train, X_test, y_macro_train, y_macro_test = train_test_split(
                X, y_macros, test_size=0.2, random_state=42
            )
            _, _, y_meal_train, y_meal_test = train_test_split(
                X, y_meals, test_size=0.2, random_state=42
            )
            
            # Train macro prediction model
            print("4. Training macro prediction model...")
            macro_model = self._train_macro_model(X_train, X_test, y_macro_train, y_macro_test)
            
            # Train meal recommendation model
            print("5. Training meal recommendation model...")
            meal_model = self._train_meal_model(X_train, X_test, y_meal_train, y_meal_test)
            
            # Save models properly
            print("6. Saving models...")
            self._save_models(macro_model, meal_model)
            
            # Save preprocessing info
            self._save_preprocessing_info(preprocessing_info)
            
            # Generate report
            report = self._generate_report(macro_model, meal_model, X_test, y_macro_test, y_meal_test)
            
            print("\n" + "=" * 50)
            print("TRAINING COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print(f"Macro R²: {macro_model['r2']:.4f}")
            print(f"Meal R²: {meal_model['r2']:.4f}")
            
            return report
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'status': 'failed'}
    
    def _train_macro_model(self, X_train, X_test, y_train, y_test):
        """Train macro prediction model"""
        # Use optimized parameters
        gb_params = {
            'n_estimators': 300,
            'learning_rate': 0.05,
            'max_depth': 6,
            'min_samples_split': 10,
            'subsample': 0.8,
            'random_state': 42
        }
        
        model = MultiOutputRegressor(GradientBoostingRegressor(**gb_params))
        model.fit(X_train, y_train)
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train,
            cv=KFold(n_splits=5, shuffle=True, random_state=42),
            scoring='r2',
            n_jobs=-1
        )
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'model': model,
            'mse': float(mse),
            'mae': float(mae),
            'r2': float(r2),
            'cv_score': float(cv_scores.mean())
        }
    
    def _train_meal_model(self, X_train, X_test, y_train, y_test):
        """Train meal recommendation model"""
        # Use optimized parameters
        rf_params = {
            'n_estimators': 300,
            'max_depth': 20,
            'min_samples_split': 2,
            'min_samples_leaf': 1,
            'max_features': 'sqrt',
            'random_state': 42
        }
        
        model = MultiOutputRegressor(RandomForestRegressor(**rf_params))
        model.fit(X_train, y_train)
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train,
            cv=KFold(n_splits=5, shuffle=True, random_state=42),
            scoring='r2',
            n_jobs=-1
        )
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'model': model,
            'mse': float(mse),
            'mae': float(mae),
            'r2': float(r2),
            'cv_score': float(cv_scores.mean())
        }
    
    def _save_models(self, macro_model, meal_model):
        """Save models to disk"""
        model_dir = os.path.join(settings.BASE_DIR, 'nutrition', 'ml', 'models')
        os.makedirs(model_dir, exist_ok=True)
        
        # Save macro model
        macro_path = os.path.join(model_dir, 'macro_prediction_model.pkl')
        with open(macro_path, 'wb') as f:
            pickle.dump(macro_model['model'], f)
        
        # Save meal model
        meal_path = os.path.join(model_dir, 'meal_recommendation_model.pkl')
        with open(meal_path, 'wb') as f:
            pickle.dump(meal_model['model'], f)
        
        # Save scaler
        scaler_path = os.path.join(model_dir, 'feature_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.data_handler.scaler, f)
        
        # Save encoders
        encoder_path = os.path.join(model_dir, 'label_encoders.pkl')
        with open(encoder_path, 'wb') as f:
            pickle.dump(self.data_handler.encoders, f)
        
        print(f"   Models saved to: {model_dir}")
    
    def _save_preprocessing_info(self, preprocessing_info):
        """Save preprocessing information"""
        model_dir = os.path.join(settings.BASE_DIR, 'nutrition', 'ml', 'models')
        info_path = os.path.join(model_dir, 'preprocessing_info.json')
        
        with open(info_path, 'w') as f:
            json.dump(preprocessing_info, f, indent=2)
        
        print(f"   Preprocessing info saved to: {info_path}")
    
    def _generate_report(self, macro_model, meal_model, X_test, y_macro_test, y_meal_test):
        """Generate training report"""
        report = {
            'training_date': datetime.now().isoformat(),
            'status': 'success',
            'model_version': 'enhanced_v2.0_simple',
            'data_quality': {
                'total_samples': 2000,
                'features_count': X_test.shape[1]
            },
            'model_performance': {
                'macro_prediction': {
                    'mse': macro_model['mse'],
                    'mae': macro_model['mae'],
                    'r2_score': macro_model['r2'],
                    'cv_score': macro_model['cv_score']
                },
                'meal_recommendation': {
                    'mse': meal_model['mse'],
                    'mae': meal_model['mae'],
                    'r2_score': meal_model['r2'],
                    'cv_score': meal_model['cv_score']
                }
            },
            'improvements': {
                'previous_r2_macro': 0.50,
                'previous_r2_meal': 0.51,
                'current_r2_macro': macro_model['r2'],
                'current_r2_meal': meal_model['r2'],
                'improvement_macro': macro_model['r2'] - 0.50,
                'improvement_meal': meal_model['r2'] - 0.51
            }
        }
        
        # Save report
        model_dir = os.path.join(settings.BASE_DIR, 'nutrition', 'ml', 'models')
        report_path = os.path.join(model_dir, 'training_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


if __name__ == "__main__":
    trainer = SimpleModelTrainer()
    results = trainer.train_and_save_models()
    
    if results.get('status') == 'success':
        print(f"\nFINAL RESULTS:")
        print(f"Status: {results['status']}")
        print(f"Macro R²: {results['model_performance']['macro_prediction']['r2_score']:.4f}")
        print(f"Meal R²: {results['model_performance']['meal_recommendation']['r2_score']:.4f}")
        print(f"Macro Improvement: {results['improvements']['improvement_macro']:+.4f}")
        print(f"Meal Improvement: {results['improvements']['improvement_meal']:+.4f}")
    else:
        print(f"Training failed: {results.get('error', 'Unknown error')}")
