"""
Training Data Handler for Nutrition ML Models

This module handles loading, preprocessing, and preparing training data
for the nutrition recommendation system.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, date
from typing import Dict, List, Any, Tuple, Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from django.conf import settings

from nutrition.models import FoodDatabase, MealPlan
from ai_features.models import HealthMetrics


class TrainingDataHandler:
    """
    Handles training data for nutrition ML models.
    Loads data from various sources and prepares it for training.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoders = {}
        self.feature_columns = []
        self.target_columns = ['calories', 'protein', 'carbs', 'fat']
    
    def load_training_dataset(self, dataset_path: str) -> pd.DataFrame:
        """
        Load training dataset from file.
        
        Args:
            dataset_path: Path to the training dataset file
            
        Returns:
            DataFrame containing training data
        """
        try:
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
            elif dataset_path.endswith('.json'):
                df = pd.read_json(dataset_path)
            elif dataset_path.endswith('.xlsx'):
                df = pd.read_excel(dataset_path)
            else:
                raise ValueError("Unsupported file format. Use CSV, JSON, or Excel.")
            
            print(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return self._create_realistic_dataset()
    
    def _create_realistic_dataset(self, n_samples=2000) -> pd.DataFrame:
        """Create realistic synthetic training data with correlations"""
        np.random.seed(42)
        
        # Generate correlated demographics
        age = np.random.randint(18, 65, n_samples)
        gender = np.random.choice(['male', 'female'], n_samples, p=[0.5, 0.5])
        
        # Height correlated with gender
        height = np.where(gender == 'male', 
                         np.random.normal(178, 8, n_samples),
                         np.random.normal(165, 7, n_samples))
        
        # Weight correlated with height and age
        base_weight = (height - 100) * 0.9
        weight = base_weight + np.random.normal(0, 10, n_samples)
        weight = np.maximum(weight, 40)  # Minimum weight
        
        # Realistic BMI calculation
        bmi = weight / ((height / 100) ** 2)
        
        # Fitness goals correlated with BMI
        goals = []
        for b in bmi:
            if b < 18.5:
                goals.append(np.random.choice(['muscle_gain', 'maintenance'], p=[0.7, 0.3]))
            elif b < 25:
                goals.append(np.random.choice(['maintenance', 'strength', 'endurance'], p=[0.4, 0.3, 0.3]))
            elif b < 30:
                goals.append(np.random.choice(['weight_loss', 'maintenance'], p=[0.8, 0.2]))
            else:
                goals.append(np.random.choice(['weight_loss', 'endurance'], p=[0.9, 0.1]))
        
        # Activity levels correlated with age
        activity_levels = []
        for a in age:
            if a < 30:
                activity_levels.append(np.random.choice(['moderate', 'active', 'very_active'], p=[0.3, 0.4, 0.3]))
            elif a < 50:
                activity_levels.append(np.random.choice(['light', 'moderate', 'active'], p=[0.3, 0.4, 0.3]))
            else:
                activity_levels.append(np.random.choice(['sedentary', 'light', 'moderate'], p=[0.3, 0.4, 0.3]))
        
        # Calculate realistic calorie targets using Harris-Benedict equation
        base_bmr = 10 * weight + 6.25 * height - 5 * age
        base_bmr = np.where(gender == 'male', base_bmr + 5, base_bmr - 161)
        
        activity_mult = {
            'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55,
            'active': 1.725, 'very_active': 1.9
        }
        
        tdee = base_bmr * np.array([activity_mult[act] for act in activity_levels])
        
        # Adjust calories based on goals
        goal_adjustments = {
            'weight_loss': -500, 'muscle_gain': 300, 'maintenance': 0,
            'endurance': 200, 'strength': 400
        }
        
        target_calories = tdee + np.array([goal_adjustments[goal] for goal in goals])
        target_calories = np.maximum(target_calories, 1200)  # Minimum calories
        
        # Calculate macro distributions based on goals
        macro_ratios = {
            'weight_loss': {'protein': 0.3, 'carbs': 0.4, 'fat': 0.3},
            'muscle_gain': {'protein': 0.35, 'carbs': 0.4, 'fat': 0.25},
            'maintenance': {'protein': 0.25, 'carbs': 0.45, 'fat': 0.3},
            'endurance': {'protein': 0.2, 'carbs': 0.6, 'fat': 0.2},
            'strength': {'protein': 0.35, 'carbs': 0.4, 'fat': 0.25}
        }
        
        target_protein = []
        target_carbs = []
        target_fat = []
        
        for i, goal in enumerate(goals):
            ratios = macro_ratios[goal]
            calories = target_calories[i]
            
            target_protein.append((calories * ratios['protein']) / 4)  # 4 cal/g protein
            target_carbs.append((calories * ratios['carbs']) / 4)     # 4 cal/g carbs
            target_fat.append((calories * ratios['fat']) / 9)        # 9 cal/g fat
        
        # Create realistic meal distributions
        data = {
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'bmi': bmi,
            'fitness_goal': goals,
            'activity_level': activity_levels,
            'target_weight': weight + np.random.normal(-5, 10, n_samples),
            'dietary_preferences': np.random.choice(['none', 'vegetarian', 'vegan', 'gluten_free', 'dairy_free'], 
                                               n_samples, p=[0.6, 0.15, 0.1, 0.1, 0.05]),
            'allergies_count': np.random.poisson(1, n_samples),
            'medical_conditions_count': np.random.poisson(0.5, n_samples),
            'target_calories': target_calories,
            'target_protein': target_protein,
            'target_carbs': target_carbs,
            'target_fat': target_fat,
            # Realistic meal distributions with some variance
            'breakfast_calories': target_calories * np.random.normal(0.25, 0.05, n_samples),
            'breakfast_protein': np.array(target_protein) * np.random.normal(0.25, 0.05, n_samples),
            'breakfast_carbs': np.array(target_carbs) * np.random.normal(0.25, 0.05, n_samples),
            'breakfast_fat': np.array(target_fat) * np.random.normal(0.25, 0.05, n_samples),
            'lunch_calories': target_calories * np.random.normal(0.35, 0.05, n_samples),
            'lunch_protein': np.array(target_protein) * np.random.normal(0.35, 0.05, n_samples),
            'lunch_carbs': np.array(target_carbs) * np.random.normal(0.35, 0.05, n_samples),
            'lunch_fat': np.array(target_fat) * np.random.normal(0.35, 0.05, n_samples),
            'dinner_calories': target_calories * np.random.normal(0.30, 0.05, n_samples),
            'dinner_protein': np.array(target_protein) * np.random.normal(0.30, 0.05, n_samples),
            'dinner_carbs': np.array(target_carbs) * np.random.normal(0.30, 0.05, n_samples),
            'dinner_fat': np.array(target_fat) * np.random.normal(0.30, 0.05, n_samples),
            'snacks_calories': target_calories * np.random.normal(0.10, 0.03, n_samples),
            'snacks_protein': np.array(target_protein) * np.random.normal(0.10, 0.03, n_samples),
            'snacks_carbs': np.array(target_carbs) * np.random.normal(0.10, 0.03, n_samples),
            'snacks_fat': np.array(target_fat) * np.random.normal(0.10, 0.03, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Ensure meal totals roughly match target totals
        for macro in ['calories', 'protein', 'carbs', 'fat']:
            meal_cols = [f'{meal}_{macro}' for meal in ['breakfast', 'lunch', 'dinner', 'snacks']]
            meal_totals = df[meal_cols].sum(axis=1)
            target_col = f'target_{macro}'
            
            # Adjust to match targets within 5% tolerance
            adjustment_factor = df[target_col] / meal_totals
            adjustment_factor = adjustment_factor.clip(0.95, 1.05)  # Limit adjustment
            
            for col in meal_cols:
                df[col] = df[col] * adjustment_factor
        
        print(f"Created realistic dataset with {len(df)} rows")
        print(f"  BMI range: {df['bmi'].min():.1f} - {df['bmi'].max():.1f}")
        print(f"  Calorie range: {df['target_calories'].min():.0f} - {df['target_calories'].max():.0f}")
        
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Preprocess the training data.
        
        Args:
            df: Raw training data
            
        Returns:
            Tuple of (preprocessed DataFrame, preprocessing info)
        """
        try:
            # Make a copy to avoid modifying original
            df_processed = df.copy()
            
            # Handle missing values
            df_processed = self._handle_missing_values(df_processed)
            
            # Encode categorical variables
            df_processed, encoding_info = self._encode_categorical_variables(df_processed)
            
            # Enhanced feature engineering
            df_processed = self._enhanced_feature_engineering(df_processed)
            
            # Normalize numerical features
            df_processed, scaling_info = self._normalize_features(df_processed)
            
            # Store preprocessing info
            preprocessing_info = {
                'encoding_info': encoding_info,
                'scaling_info': scaling_info,
                'feature_columns': df_processed.columns.tolist(),
                'target_columns': self.target_columns
            }
            
            return df_processed, preprocessing_info
            
        except Exception as e:
            print(f"Error preprocessing data: {e}")
            return df, {}
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        # Fill numerical missing values with median
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        for col in numerical_columns:
            df[col] = df[col].fillna(df[col].median())
        
        # Fill categorical missing values with mode
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown')
        
        return df
    
    def _encode_categorical_variables(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Encode categorical variables"""
        encoding_info = {}
        
        # Encode gender
        if 'gender' in df.columns:
            le_gender = LabelEncoder()
            df['gender_encoded'] = le_gender.fit_transform(df['gender'])
            encoding_info['gender'] = le_gender.classes_.tolist()
        
        # Encode fitness goal
        if 'fitness_goal' in df.columns:
            le_goal = LabelEncoder()
            df['fitness_goal_encoded'] = le_goal.fit_transform(df['fitness_goal'])
            encoding_info['fitness_goal'] = le_goal.classes_.tolist()
        
        # Encode activity level
        if 'activity_level' in df.columns:
            le_activity = LabelEncoder()
            df['activity_level_encoded'] = le_activity.fit_transform(df['activity_level'])
            encoding_info['activity_level'] = le_activity.classes_.tolist()
        
        # Encode dietary preferences
        if 'dietary_preferences' in df.columns:
            le_diet = LabelEncoder()
            df['dietary_preferences_encoded'] = le_diet.fit_transform(df['dietary_preferences'])
            encoding_info['dietary_preferences'] = le_diet.classes_.tolist()
        
        # Store encoders for later use
        self.encoders = encoding_info
        
        return df, encoding_info
    
    def _enhanced_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create enhanced features for better ML performance"""
        # BMI categories with medical standards
        if 'bmi' in df.columns:
            df['bmi_category'] = pd.cut(df['bmi'], 
                                       bins=[0, 18.5, 25, 30, float('inf')],
                                       labels=['underweight', 'normal', 'overweight', 'obese'])
            df['bmi_category_encoded'] = LabelEncoder().fit_transform(df['bmi_category'].astype(str))
        
        # Age groups with life stages
        if 'age' in df.columns:
            df['age_group'] = pd.cut(df['age'],
                                     bins=[0, 25, 35, 50, 65, float('inf')],
                                     labels=['young_adult', 'adult', 'middle_aged', 'senior', 'elderly'])
            df['age_group_encoded'] = LabelEncoder().fit_transform(df['age_group'].astype(str))
        
        # Calorie and protein needs per kg body weight
        if 'weight' in df.columns:
            if 'target_calories' in df.columns:
                df['calories_per_kg'] = df['target_calories'] / df['weight']
            if 'target_protein' in df.columns:
                df['protein_per_kg'] = df['target_protein'] / df['weight']
        
        # Weight change metrics
        if 'weight' in df.columns and 'target_weight' in df.columns:
            df['weight_difference'] = df['target_weight'] - df['weight']
            df['weight_change_percent'] = df['weight_difference'] / df['weight'] * 100
            df['weight_change_needed'] = (df['weight_difference'] > 0).astype(int)
        
        # Activity multiplier mapping
        if 'activity_level' in df.columns:
            activity_multipliers = {
                'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55,
                'active': 1.725, 'very_active': 1.9
            }
            df['activity_multiplier'] = df['activity_level'].map(activity_multipliers)
        
        # Goal-specific features
        if 'fitness_goal' in df.columns:
            # Goal difficulty score (1-5 scale)
            goal_difficulty = {
                'maintenance': 1, 'endurance': 2, 'strength': 3,
                'muscle_gain': 4, 'weight_loss': 5
            }
            df['goal_difficulty'] = df['fitness_goal'].map(goal_difficulty)
        
        # Interaction features
        df = self._add_interaction_features(df)
        
        # Health risk indicators
        df = self._add_health_risk_features(df)
        
        # Nutritional ratios
        df = self._add_nutritional_ratios(df)
        
        return df
    
    def _add_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add interaction features between variables"""
        # Goal x Activity interactions
        if 'fitness_goal' in df.columns and 'activity_level' in df.columns:
            df['goal_activity_interaction'] = df['fitness_goal'] + '_' + df['activity_level']
            df['goal_activity_encoded'] = LabelEncoder().fit_transform(df['goal_activity_interaction'])
        
        # Age x Goal interactions
        if 'age_group' in df.columns and 'fitness_goal' in df.columns:
            df['age_goal_interaction'] = df['age_group'].astype(str) + '_' + df['fitness_goal']
            df['age_goal_encoded'] = LabelEncoder().fit_transform(df['age_goal_interaction'])
        
        # BMI x Goal interactions
        if 'bmi_category' in df.columns and 'fitness_goal' in df.columns:
            df['bmi_goal_interaction'] = df['bmi_category'].astype(str) + '_' + df['fitness_goal']
            df['bmi_goal_encoded'] = LabelEncoder().fit_transform(df['bmi_goal_interaction'])
        
        # Gender x Goal interactions
        if 'gender' in df.columns and 'fitness_goal' in df.columns:
            df['gender_goal_interaction'] = df['gender'] + '_' + df['fitness_goal']
            df['gender_goal_encoded'] = LabelEncoder().fit_transform(df['gender_goal_interaction'])
        
        return df
    
    def _add_health_risk_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add health risk assessment features"""
        # BMI risk score
        if 'bmi' in df.columns:
            df['bmi_risk_score'] = np.where(df['bmi'] < 18.5, 3,  # Underweight risk
                                          np.where(df['bmi'] < 25, 0,  # Normal
                                                 np.where(df['bmi'] < 30, 2,  # Overweight
                                                        4)))  # Obese
        
        # Age-related factors
        if 'age' in df.columns:
            df['age_risk_factor'] = np.where(df['age'] < 30, 0,
                                           np.where(df['age'] < 50, 1, 2))
        
        # Combined health risk score
        if 'bmi_risk_score' in df.columns and 'age_risk_factor' in df.columns:
            df['total_health_risk'] = df['bmi_risk_score'] + df['age_risk_factor']
        
        return df
    
    def _add_nutritional_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add nutritional ratio features"""
        # Protein to calorie ratio
        if 'target_protein' in df.columns and 'target_calories' in df.columns:
            df['protein_calorie_ratio'] = (df['target_protein'] * 4) / df['target_calories']
        
        # Fat to calorie ratio
        if 'target_fat' in df.columns and 'target_calories' in df.columns:
            df['fat_calorie_ratio'] = (df['target_fat'] * 9) / df['target_calories']
        
        # Carb to calorie ratio
        if 'target_carbs' in df.columns and 'target_calories' in df.columns:
            df['carb_calorie_ratio'] = (df['target_carbs'] * 4) / df['target_calories']
        
        return df
    
    def _normalize_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Normalize numerical features"""
        # Select numerical columns for scaling
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        
        # Exclude target variables from scaling
        feature_columns = [col for col in numerical_columns if not any(target in col for target in self.target_columns)]
        
        if feature_columns:
            df[feature_columns] = self.scaler.fit_transform(df[feature_columns])
        
        scaling_info = {
            'feature_columns': feature_columns,
            'scaler_mean': self.scaler.mean_.tolist(),
            'scaler_scale': self.scaler.scale_.tolist()
        }
        
        return df, scaling_info
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for ML training.
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            Tuple of (features, macro_targets, meal_targets)
        """
        try:
            # Select feature columns (only numerical columns, exclude target variables)
            exclude_columns = ['target_calories', 'target_protein', 'target_carbs', 'target_fat',
                           'breakfast_calories', 'breakfast_protein', 'breakfast_carbs', 'breakfast_fat',
                           'lunch_calories', 'lunch_protein', 'lunch_carbs', 'lunch_fat',
                           'dinner_calories', 'dinner_protein', 'dinner_carbs', 'dinner_fat',
                           'snacks_calories', 'snacks_protein', 'snacks_carbs', 'snacks_fat']
            
            # Use exact feature order from preprocessing info to ensure consistency
            feature_columns = [
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
            
            # Select target columns
            macro_target_columns = ['target_calories', 'target_protein', 'target_carbs', 'target_fat']
            meal_target_columns = ['breakfast_calories', 'breakfast_protein', 'breakfast_carbs', 'breakfast_fat',
                                 'lunch_calories', 'lunch_protein', 'lunch_carbs', 'lunch_fat',
                                 'dinner_calories', 'dinner_protein', 'dinner_carbs', 'dinner_fat']
            
            # Extract features and targets
            X = df[feature_columns].values
            y_macros = df[macro_target_columns].values
            y_meals = df[meal_target_columns].values
            
            # Store feature columns for later use
            self.feature_columns = feature_columns
            
            print(f"Prepared training data:")
            print(f"Features shape: {X.shape}")
            print(f"Macro targets shape: {y_macros.shape}")
            print(f"Meal targets shape: {y_meals.shape}")
            
            return X, y_macros, y_meals
            
        except Exception as e:
            print(f"Error preparing training data: {e}")
            return np.array([]), np.array([]), np.array([])
    
    def load_user_feedback_data(self) -> pd.DataFrame:
        """Load user feedback data for continuous learning"""
        try:
            # Get meal feedback from database
            feedback_data = []
            
            # This would be implemented based on your actual feedback model
            # For now, return empty DataFrame
            df = pd.DataFrame(feedback_data)
            
            print(f"Loaded {len(df)} feedback records")
            return df
            
        except Exception as e:
            print(f"Error loading feedback data: {e}")
            return pd.DataFrame()
    
    def augment_training_data(self, df: pd.DataFrame, augment_factor: int = 2) -> pd.DataFrame:
        """
        Augment training data to improve model performance.
        
        Args:
            df: Original training data
            augment_factor: How many times to augment the data
            
        Returns:
            Augmented DataFrame
        """
        try:
            augmented_data = [df]
            
            for i in range(augment_factor):
                # Create variations of the data
                df_augmented = df.copy()
                
                # Add noise to numerical features
                numerical_columns = df.select_dtypes(include=[np.number]).columns
                for col in numerical_columns:
                    noise = np.random.normal(0, 0.05, len(df))
                    df_augmented[col] = df[col] * (1 + noise)
                
                # Ensure realistic bounds
                if 'target_calories' in df_augmented.columns:
                    df_augmented['target_calories'] = df_augmented['target_calories'].clip(1200, 4000)
                
                augmented_data.append(df_augmented)
            
            df_final = pd.concat(augmented_data, ignore_index=True)
            print(f"Augmented data from {len(df)} to {len(df_final)} samples")
            
            return df_final
            
        except Exception as e:
            print(f"Error augmenting data: {e}")
            return df
    
    def save_preprocessing_info(self, info: Dict[str, Any], filepath: str):
        """Save preprocessing information for later use"""
        try:
            with open(filepath, 'w') as f:
                json.dump(info, f, indent=2)
            print(f"Saved preprocessing info to {filepath}")
        except Exception as e:
            print(f"Error saving preprocessing info: {e}")
    
    def load_preprocessing_info(self, filepath: str) -> Dict[str, Any]:
        """Load preprocessing information"""
        try:
            with open(filepath, 'r') as f:
                info = json.load(f)
            print(f"Loaded preprocessing info from {filepath}")
            return info
        except Exception as e:
            print(f"Error loading preprocessing info: {e}")
            return {}
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the quality of training data.
        
        Args:
            df: Training data
            
        Returns:
            Dictionary containing quality metrics
        """
        quality_report = {
            'total_samples': len(df),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict(),
            'numerical_summary': df.describe().to_dict(),
            'categorical_summary': {}
        }
        
        # Add categorical summaries
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            quality_report['categorical_summary'][col] = df[col].value_counts().to_dict()
        
        return quality_report
