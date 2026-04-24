# ML-Based Nutrition Recommendation System

This directory contains the machine learning implementation for personalized nutrition recommendations in ZoeFit.

## Overview

The ML-based nutrition system replaces the rule-based approach with trained machine learning models that learn from user data to provide more accurate and personalized meal plans.

## Architecture

```
nutrition/ml/
|-- ml_engine.py              # Main ML recommendation engine
|-- training_data_handler.py  # Data preprocessing and preparation
|-- train_models.py          # Training script and pipeline
|-- models/                  # Trained model storage
|   |-- meal_recommendation_model.pkl
|   |-- macro_prediction_model.pkl
|   |-- feature_scaler.pkl
|   |-- label_encoders.pkl
|   |-- preprocessing_info.json
|   |-- training_report.json
|-- data/                    # Training datasets
|   |-- nutrition_dataset.csv
|   |-- test_dataset.csv
|-- README.md               # This file
```

## Step-by-Step Implementation Guide

### Step 1: Prepare Your Dataset

Create a training dataset with the following columns:

**Required User Features:**
- `age`: User age (18-80)
- `gender`: 'male' or 'female'
- `height`: Height in cm
- `weight`: Weight in kg
- `fitness_goal`: 'weight_loss', 'muscle_gain', 'maintenance', 'endurance', 'strength'
- `activity_level`: 'sedentary', 'light', 'moderate', 'active', 'very_active'
- `target_weight`: Target weight in kg
- `dietary_preferences`: 'none', 'vegetarian', 'vegan', 'gluten_free', 'dairy_free'
- `allergies_count`: Number of allergies
- `medical_conditions_count`: Number of medical conditions

**Target Variables:**
- `target_calories`: Daily calorie target
- `target_protein`: Daily protein target (grams)
- `target_carbs`: Daily carbohydrate target (grams)
- `target_fat`: Daily fat target (grams)

**Meal-Specific Targets:**
- `breakfast_calories`, `breakfast_protein`, `breakfast_carbs`, `breakfast_fat`
- `lunch_calories`, `lunch_protein`, `lunch_carbs`, `lunch_fat`
- `dinner_calories`, `dinner_protein`, `dinner_carbs`, `dinner_fat`
- `snacks_calories`, `snacks_protein`, `snacks_carbs`, `snacks_fat`

### Step 2: Train the Models

#### Option A: Train from Dataset File

```bash
# Navigate to project directory
cd backend/back/zoefit

# Train models using your dataset
python manage.py train_nutrition_ml --dataset path/to/your/dataset.csv

# Train with evaluation
python manage.py train_nutrition_ml --dataset path/to/dataset.csv --test-data path/to/test.csv

# Train without data augmentation
python manage.py train_nutrition_ml --dataset path/to/dataset.csv --no-augment
```

#### Option B: Train from Database Data

```bash
# Train using data from your database
python manage.py train_nutrition_ml --from-db

# Train with evaluation
python manage.py train_nutrition_ml --from-db --test-data path/to/test.csv
```

#### Option C: Evaluate Existing Models

```bash
# Only evaluate existing models
python manage.py train_nutrition_ml --evaluate-only --test-data path/to/test.csv
```

### Step 3: Model Files Generated

After training, the following files will be created in `nutrition/ml/models/`:

- `meal_recommendation_model.pkl`: Random Forest model for meal recommendations
- `macro_prediction_model.pkl`: Gradient Boosting model for macro predictions
- `feature_scaler.pkl`: StandardScaler for feature normalization
- `label_encoders.pkl`: Label encoders for categorical variables
- `preprocessing_info.json`: Preprocessing configuration
- `training_report.json`: Training metrics and results

### Step 4: Integration with Nutrition System

The ML models are automatically integrated with the nutrition system:

1. **AI Engine Update**: The `AIRecommendationEngine` now prioritizes ML predictions
2. **Fallback System**: If ML models fail, it falls back to rule-based approach
3. **Confidence Scoring**: Each prediction includes a confidence score
4. **Approach Tracking**: System tracks whether ML or rule-based approach was used

### Step 5: Using the System

Once trained, the system will automatically use ML models for meal plan generation:

```python
from ai_features.ai_engine import AIRecommendationEngine
from ai_features.models import HealthMetrics
from datetime import date

# Initialize engine
engine = AIRecommendationEngine()

# Generate meal plan (automatically uses ML if available)
user_metrics = HealthMetrics.objects.get(user=request.user)
meal_plan = engine.generate_meal_plan(user_metrics, date.today())

# Check which approach was used
print(f"Approach: {meal_plan['approach']}")
print(f"Confidence: {meal_plan['confidence_score']}")
```

## Model Performance Metrics

The training system tracks the following metrics:

### Macro Prediction Model
- **MSE (Mean Squared Error)**: Average squared difference between predicted and actual values
- **R² Score**: Proportion of variance explained by the model (0-1, higher is better)

### Meal Recommendation Model
- **MSE**: Average squared difference for meal-specific predictions
- **R² Score**: Model fit for meal recommendations

### Good Performance Benchmarks
- **Macro R²**: > 0.85 (excellent), 0.70-0.85 (good), < 0.70 (needs improvement)
- **Meal R²**: > 0.80 (excellent), 0.65-0.80 (good), < 0.65 (needs improvement)

## Data Quality Requirements

For optimal model performance:

1. **Minimum Samples**: 500+ training examples
2. **Feature Completeness**: < 5% missing values
3. **Target Distribution**: Balanced across different goals and demographics
4. **Data Validation**: Remove outliers and impossible values

## Continuous Learning

The system supports continuous learning:

1. **User Feedback**: Collect meal ratings and preferences
2. **Model Retraining**: Periodically retrain with new data
3. **Performance Monitoring**: Track model accuracy over time
4. **A/B Testing**: Compare ML vs rule-based performance

## Troubleshooting

### Common Issues

1. **Import Error**: ML engine not available
   - **Solution**: Install ML dependencies: `pip install scikit-learn pandas numpy`
   - **Fallback**: System automatically uses rule-based approach

2. **Model Loading Error**: Trained models not found
   - **Solution**: Train models first using the training command
   - **Fallback**: System uses rule-based approach until models are trained

3. **Poor Performance**: Low R² scores
   - **Solution**: Increase training data size, improve data quality
   - **Check**: Feature engineering and preprocessing steps

4. **Memory Error**: Large dataset
   - **Solution**: Use data sampling, reduce feature dimensions
   - **Alternative**: Train with smaller batch sizes

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Features

### Custom Model Training

Create custom training scripts:

```python
from nutrition.ml.train_models import NutritionModelTrainer

trainer = NutritionModelTrainer()
results = trainer.train_from_dataset('my_dataset.csv')
```

### Model Evaluation

Detailed evaluation:

```python
results = trainer.evaluate_models('test_dataset.csv')
print(f"Macro R²: {results['macro_prediction']['r2_score']}")
```

### Feature Engineering

Add custom features in `training_data_handler.py`:

```python
def _feature_engineering(self, df):
    # Add custom features
    df['custom_feature'] = df['weight'] / df['height']
    return df
```

## Production Deployment

### Environment Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Train models: `python manage.py train_nutrition_ml --dataset production_data.csv`
3. Verify models: Check `nutrition/ml/models/` directory
4. Test system: Generate sample meal plans

### Monitoring

Monitor model performance in production:

1. Track confidence scores
2. Log approach usage (ML vs rule-based)
3. Collect user feedback
4. Schedule periodic retraining

### Scaling

For large-scale deployments:

1. Use model caching
2. Implement batch predictions
3. Consider model quantization
4. Set up monitoring alerts

## API Integration

The ML system integrates seamlessly with existing APIs:

- `/api/nutrition/meal-plans/`: Uses ML for meal plan generation
- `/api/nutrition/meal-plan/<date>/`: Returns ML-generated plans with confidence scores
- `/api/ai/insights/`: Includes ML approach information

## Future Enhancements

Planned improvements:

1. **Deep Learning**: Neural networks for complex patterns
2. **Real-time Adaptation**: Online learning from user feedback
3. **Multi-objective Optimization**: Balance taste, nutrition, and cost
4. **Integration with Wearables**: Real-time health data integration
5. **Personalized Learning**: User-specific model fine-tuning

## Support

For issues or questions:

1. Check troubleshooting section
2. Review training logs
3. Validate dataset format
4. Test with sample data first

## License

This ML implementation is part of the ZoeFit project and follows the same licensing terms.
