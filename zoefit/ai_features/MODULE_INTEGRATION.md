# Module Integration Guide

This document explains how the separated workout and nutrition modules integrate with the ai_features module to provide a cohesive system.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Workout Module│    │ Nutrition Module│    │  AI Features    │
│                 │    │                 │    │   Module        │
│ - WorkoutPlan   │◄──►│ - MealPlan      │◄──►│ - HealthMetrics │
│ - WorkoutSession│    │ - NutritionLog  │    │ - ProgressTrack │
│ - WorkoutProg   │    │ - NutritionProg│    │ - AIChatHistory │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Service Layer   │
                    │ - ProgressSync  │
                    │ - UserDataAgg   │
                    └─────────────────┘
```

## Key Integration Points

### 1. Data Synchronization
- **ProgressSyncService**: Automatically updates `ProgressTracking` when workout/nutrition data changes
- **Signals**: Real-time synchronization using Django signals
- **Service Methods**: Manual sync capabilities for batch operations

### 2. Aggregated Endpoints
- **Dashboard**: Single endpoint for complete user overview
- **Today Overview**: Daily workout and meal plan data
- **Weekly Report**: Comprehensive weekly progress analysis
- **Progress Insights**: AI-powered recommendations across all modules

### 3. Cross-Module Dependencies
- **HealthMetrics**: Foundation data used by both workout and nutrition modules
- **ProgressTracking**: Aggregates data from both modules for AI insights
- **AI Features**: Provides intelligent recommendations based on combined data

## API Endpoints

### Aggregated Endpoints (New)
```
GET /api/ai/dashboard/           - Complete dashboard data
GET /api/ai/summary/             - User summary statistics
POST /api/ai/sync-progress/      - Manual progress sync
GET /api/ai/today/               - Today's overview
GET /api/ai/weekly-report/       - Weekly progress report
GET /api/ai/progress-insights/   - AI-powered insights
```

### Module-Specific Endpoints
```
Workout Module:
  GET /api/workout/plans/        - User workout plans
  POST /api/workout/sessions/    - Log workout session

Nutrition Module:
  GET /api/nutrition/meals/      - User meal plans
  POST /api/nutrition/logs/      - Log nutrition intake

AI Features:
  GET /api/ai/health-metrics/   - User health profile
  POST /api/ai/chat/             - AI chatbot
```

## Data Flow

### 1. Workout Completion
```
WorkoutSession.completed = True
    ↓ (Signal)
ProgressSyncService.update_user_progress()
    ↓
ProgressTracking updated with:
    - workout_streak
    - total_workouts  
    - calories_burned
    - progress_score
    - ai_insights
```

### 2. Nutrition Logging
```
NutritionLog created/updated
    ↓ (Signal)
ProgressSyncService.update_user_progress()
    ↓
ProgressTracking updated with:
    - nutrition_adherence
    - progress_score
    - ai_insights
```

### 3. Dashboard Request
```
GET /api/ai/dashboard/
    ↓
UserDataAggregationService.get_user_dashboard_data()
    ↓
Aggregates data from:
    - HealthMetrics
    - ProgressTracking
    - WorkoutPlan (recent)
    - MealPlan (recent)
```

## Benefits of This Architecture

### 1. **Modularity**
- Clear separation of concerns
- Independent development and testing
- Easy to maintain and extend

### 2. **Data Consistency**
- Automatic synchronization via signals
- Single source of truth for progress tracking
- Real-time updates across modules

### 3. **Frontend Efficiency**
- Reduced API calls with aggregated endpoints
- Consistent data format
- Single point for cross-module operations

### 4. **Scalability**
- Easy to add new modules
- Service layer handles complex operations
- Clean interfaces between components

## Best Practices

### 1. **For Developers**
- Use service layer methods for cross-module operations
- Don't directly modify ProgressTracking from other modules
- Leverage aggregated endpoints for frontend data

### 2. **For Frontend**
- Use aggregated endpoints for dashboard/overview pages
- Call module-specific endpoints for detailed operations
- Implement manual sync after batch updates

### 3. **For Operations**
- Monitor signal performance in production
- Use manual sync for data migrations
- Regular cleanup of old progress records

## Troubleshooting

### Common Issues
1. **Progress not updating**: Check if signals are connected properly
2. **Inconsistent data**: Run manual sync via `/api/ai/sync-progress/`
3. **Slow dashboard**: Check database indexes on progress tables

### Debug Commands
```python
# Manual sync for specific user
from ai_features.services import ProgressSyncService
user = User.objects.get(username='testuser')
progress = ProgressSyncService.update_user_progress(user)

# Check signal connections
from ai_features.signals import *
# Signals should be automatically connected in apps.py
```

## Future Enhancements

1. **Caching Layer**: Add Redis caching for frequently accessed aggregated data
2. **Background Tasks**: Use Celery for heavy aggregation operations
3. **Real-time Updates**: WebSocket integration for live progress updates
4. **Advanced Analytics**: More sophisticated AI models for predictions
