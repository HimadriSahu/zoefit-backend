# Database Analysis and Cleanup Plan

## Current Database Models Status

### ✅ Models Already Defined
1. **nutrition/models.py**:
   - MealPlan (nutrition_meal_plans)
   - DietaryPreferences (nutrition_dietary_preferences)
   - NutritionLog (nutrition_logs)
   - NutritionProgress (nutrition_progress)
   - FoodDatabase (nutrition_food_database)

2. **ai_features/ml_performance.py**:
   - MLPerformanceLog (ml_performance_logs)
   - MLModelMetrics (ml_model_metrics)
   - MLPredictionFeedback (ml_prediction_feedback)

3. **ai_features/models.py**:
   - HealthMetrics (ai_features_healthmetrics)

### ❌ Database Issues Found

1. **Field Name Mismatches**:
   - MLPerformanceLog uses `timestamp` but code references `created_at`
   - MLPredictionFeedback uses `timestamp` but code references `created_at`

2. **Missing Fields**:
   - MLPerformanceLog missing `prediction_data` field (JSONField)
   - MealPlan missing `approach` field (CharField)

3. **Unused Models**:
   - `FoodDatabase` table referenced but not properly populated
   - `NutritionLog` table referenced but may not be used

## Required Database Updates

### 1. Fix MLPerformanceLog Model
```python
class MLPerformanceLog(models.Model):
    # ... existing fields ...
    
    # Add missing field
    prediction_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Full prediction data for analysis"
    )
    
    # Fix field reference issue
    created_at = models.DateTimeField(auto_now_add=True)  # Add this
    timestamp = models.DateTimeField(auto_now_add=True)  # Keep for compatibility
```

### 2. Fix MLPredictionFeedback Model
```python
class MLPredictionFeedback(models.Model):
    # ... existing fields ...
    
    # Fix field reference issue
    created_at = models.DateTimeField(auto_now_add=True)  # Add this
    timestamp = models.DateTimeField(auto_now_add=True)  # Keep for compatibility
```

### 3. Fix MealPlan Model
```python
class MealPlan(models.Model):
    # ... existing fields ...
    
    # Add missing field
    approach = models.CharField(
        max_length=20,
        choices=[
            ('ml_based', 'ML Based'),
            ('rule_based', 'Rule Based'),
            ('hybrid', 'Hybrid'),
        ],
        default='ml_based',
        help_text="Approach used to generate meal plan"
    )
    
    # Add missing field
    adaptation_applied = models.BooleanField(
        default=False,
        help_text="Whether real-time adaptation was applied"
    )
```

## Files to Remove (Keep Only Essential)

### ❌ Remove These Files:
1. **quick_train.py** - Outdated training script
2. **train_models.py** - Superseded by train_simple.py
3. **quick_test.py** - Superseded by simple_final_test.py
4. **test_enhanced_ml.py** - Superseded by simple_final_test.py
5. **verify_features.py** - No longer needed
6. **final_test.py** - Superseded by simple_final_test.py
7. **test_phase3.py** - Development test file
8. **performance_optimizer.py** - Not integrated
9. **diet_model.pkl** - Old model file
10. **model_columns.pkl** - Old model file
11. **CLEANUP_SUMMARY.md** - Documentation file

### ✅ Keep These Files:
1. **train_simple.py** - Main training script
2. **ml_engine.py** - Core ML engine
3. **training_data_handler.py** - Data preparation
4. **real_time_adapter.py** - Real-time adaptation
5. **predictive_insights.py** - Predictive analytics
6. **simple_final_test.py** - Main test script
7. **models/** - Trained model files
8. **README.md** - Documentation
9. **ML_ENHANCEMENT_COMPLETE.md** - Final documentation

## Migration Plan

### Step 1: Database Model Updates
1. Add missing fields to existing models
2. Create migrations for new fields
3. Run migrations to update database schema

### Step 2: Code Cleanup
1. Remove unnecessary files
2. Update imports and references
3. Ensure field name consistency

### Step 3: Testing
1. Run tests to ensure database compatibility
2. Verify ML engine functionality
3. Test real-time adaptation system

## Priority Actions

### High Priority:
1. **Fix MLPerformanceLog.prediction_data field** - Critical for analytics
2. **Fix field name consistency** - Prevents runtime errors
3. **Remove unused files** - Reduce codebase complexity

### Medium Priority:
1. **Populate FoodDatabase** - Improve meal recommendations
2. **Optimize NutritionLog usage** - Better tracking
3. **Add database indexes** - Improve query performance

### Low Priority:
1. **Add model versioning** - Better deployment management
2. **Implement data archiving** - Manage database size
3. **Add backup strategies** - Data protection

## Production Readiness Checklist

- [ ] Database models updated with required fields
- [ ] Migrations created and run
- [ ] Unused files removed
- [ ] Field name consistency verified
- [ ] ML engine tested with updated models
- [ ] Real-time adaptation tested
- [ ] Predictive insights tested
- [ ] Performance monitoring verified
