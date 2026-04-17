# Frontend Module for ZoeFit

The frontend module provides comprehensive data visualization, tracking, and analytics features for the ZoeFit fitness application. This module bridges the gap between raw data storage and meaningful user experiences, powering both web and mobile applications.

## Overview

The frontend module handles all user-facing data features including:
- **Workout History**: Track actual workout sessions and exercise performance
- **Progress Tracking**: Monitor physical progress with measurements and photos
- **Streak System**: Motivational streak tracking for consistency
- **Meal Logging**: Comprehensive nutrition tracking and analysis
- **Dashboard**: Unified view of all fitness data and insights
- **Achievements**: Gamification system to motivate users

## Features

### 🏋️ Workout History Management
- **WorkoutSession**: Track actual workout completions with timing, calories, and user feedback
- **ExerciseLog**: Detailed exercise performance data including sets, reps, weight, and form ratings
- **Workout Analytics**: Comprehensive statistics on workout frequency, duration, and progress
- **Performance Tracking**: Monitor strength progression and cardio improvements

### 📊 Progress Tracking & Visualization
- **ProgressSnapshot**: Time-based measurements including weight, body fat, and muscle mass
- **Body Measurements**: Track chest, waist, arms, and other measurements
- **Progress Photos**: Store and compare progress photos over time
- **Chart Data**: Formatted data for various progress visualizations

### 🔥 Streak Tracking System
- **Multiple Streak Types**: Workout, calorie logging, water intake, and steps goals
- **Automatic Updates**: Streaks update based on user activity
- **Streak Analytics**: Historical data and patterns for motivation
- **Milestone Notifications**: Celebrate streak achievements

### 🍽️ Meal Logging & Nutrition
- **Comprehensive Logging**: Track meals with detailed nutritional information
- **Macronutrient Tracking**: Monitor protein, carbs, and fat intake
- **Nutrition Analytics**: Daily, weekly, and monthly nutrition summaries
- **Progress Photos**: Add photos to meal logs for visual tracking

### 📈 Dashboard & Analytics
- **Unified Dashboard**: Complete overview of fitness status and recent activity
- **Personalized Insights**: AI-powered recommendations based on user data
- **Achievement System**: Gamification with badges and points
- **Data Export**: Export workout, nutrition, and progress data

## API Endpoints

### Workout History
```
GET    /api/frontend/workout-sessions/          # List workout sessions
POST   /api/frontend/workout-sessions/          # Create workout session
GET    /api/frontend/workout-sessions/{id}/     # Get workout session
PUT    /api/frontend/workout-sessions/{id}/     # Update workout session
DELETE /api/frontend/workout-sessions/{id}/     # Delete workout session
GET    /api/frontend/workout-stats/              # Get workout statistics
```

### Progress Tracking
```
GET    /api/frontend/progress-snapshots/        # List progress snapshots
POST   /api/frontend/progress-snapshots/        # Create progress snapshot
GET    /api/frontend/progress-charts/           # Get chart data
```

### Streak Tracking
```
GET    /api/frontend/streaks/                   # Get current streaks
GET    /api/frontend/streak-history/            # Get streak history
```

### Meal Logging
```
GET    /api/frontend/meal-logs/                 # List meal logs
POST   /api/frontend/meal-logs/                 # Create meal log
GET    /api/frontend/nutrition-summary/         # Get nutrition summary
```

### Dashboard
```
GET    /api/frontend/dashboard/                 # Get dashboard summary
GET    /api/frontend/achievements/              # Get user achievements
```

## Data Models

### WorkoutSession
Tracks actual workout sessions completed by users.

**Key Fields:**
- `user`: Foreign key to User model
- `workout_plan`: Optional link to AI-generated plan
- `start_time`, `end_time`: Session timing
- `duration`: Auto-calculated duration
- `completed`: Whether workout was completed as planned
- `calories_burned`: Estimated calories burned
- `difficulty_rating`: User's 1-5 rating

### ExerciseLog
Detailed logging of individual exercises within workout sessions.

**Key Fields:**
- `workout_session`: Foreign key to WorkoutSession
- `exercise_name`: Name of exercise performed
- `sets_completed`: Number of sets completed
- `reps_per_set`: List of reps for each set
- `weight_used`: Weight used in kg
- `form_rating`: User's form rating (1-5)

### ProgressSnapshot
Time-based snapshots of user's physical progress.

**Key Fields:**
- `user`: Foreign key to User model
- `date`: Date of snapshot
- `weight`, `body_fat_percentage`, `muscle_mass`: Physical measurements
- `measurements`: JSON field for body measurements
- `progress_photos`: List of photo URLs

### Streak
Tracks various fitness streaks for motivation and consistency.

**Key Fields:**
- `user`: Foreign key to User model
- `streak_type`: Type of streak (workout, calorie, water, steps)
- `current_count`, `longest_count`: Streak counters
- `last_activity_date`: Date of last activity
- `is_active`: Whether streak is currently active

### MealLog
Tracks actual meals consumed by users.

**Key Fields:**
- `user`: Foreign key to User model
- `meal_type`: Type of meal (breakfast, lunch, dinner, snack)
- `food_items`: List of food items with nutritional info
- `total_calories`, `protein`, `carbs`, `fat`: Nutritional data
- `meal_time`: When meal was consumed

### Achievement
Tracks user achievements and milestones.

**Key Fields:**
- `user`: Foreign key to User model
- `achievement_type`: Type of achievement
- `title`, `description`: Achievement details
- `badge_icon`: Icon identifier
- `points_awarded`: Points awarded for achievement

## Integration with Other Modules

### Authentication Module
- All endpoints require JWT authentication
- Uses `IsAuthenticated` permission class
- Leverages current user context

### Profiles Module
- References user profile information
- Uses fitness goals for progress calculations
- Displays profile data in dashboard

### AI Features Module
- Connects with `WorkoutPlan` for planned vs actual workouts
- Uses `HealthMetrics` for progress calculations
- Integrates with `ProgressTracking` for AI insights
- Compares `MealPlan` with actual nutrition data

## Utility Functions

### DateRange
Helper class for working with date ranges and periods.

**Methods:**
- `get_period_dates(period)`: Get start/end dates for period
- `get_week_range(offset)`: Get week range with offset
- `get_month_range(offset)`: Get month range with offset

### ProgressCalculator
Helper class for progress calculations and analytics.

**Methods:**
- `calculate_weight_change(user, start, end)`: Calculate weight change
- `calculate_body_composition_change(user)`: Calculate composition changes
- `calculate_strength_progression(user, exercise)`: Calculate strength progression

### StreakManager
Helper class for managing and updating streaks.

**Methods:**
- `update_all_streaks(user)`: Update all user streaks
- `update_workout_streak(user)`: Update workout streak
- `update_calorie_streak(user)`: Update calorie logging streak

### AchievementManager
Helper class for managing achievements.

**Methods:**
- `check_workout_achievements(user)`: Check workout achievements
- `check_progress_achievements(user)`: Check progress achievements
- `award_achievement(user, ...)`: Award achievement to user

### DataExporter
Helper class for exporting user data.

**Methods:**
- `export_workout_data(user, format)`: Export workout data
- `export_nutrition_data(user, format)`: Export nutrition data
- `export_progress_data(user, format)`: Export progress data

### AnalyticsHelper
Helper class for analytics calculations.

**Methods:**
- `get_workout_frequency(user, weeks)`: Calculate workout frequency
- `get_nutrition_consistency(user, days)`: Calculate nutrition consistency
- `calculate_engagement_score(user)`: Calculate overall engagement

## Database Schema

The frontend module creates the following database tables:

- `frontend_workout_sessions`: Workout session data
- `frontend_exercise_logs`: Exercise performance data
- `frontend_progress_snapshots`: Progress measurement data
- `frontend_streaks`: Streak tracking data
- `frontend_meal_logs`: Meal logging data
- `frontend_achievements`: Achievement data

### Indexes
All tables include optimized indexes for common queries:
- User-based queries: `user_id`, `user_id + created_at`
- Date-based queries: `date`, `created_at`
- Type-based queries: `streak_type`, `meal_type`, `achievement_type`

## Testing

The frontend module includes comprehensive test coverage:

### Model Tests
- Model creation and validation
- Field constraints and relationships
- Model methods and properties
- Database constraints and edge cases

### Test Files
- `tests/test_models.py`: Model unit tests
- `tests/test_views.py`: API endpoint tests (to be added)
- `tests/test_utils.py`: Utility function tests (to be added)

### Running Tests
```bash
# Run all frontend tests
python manage.py test frontend

# Run specific test file
python manage.py test frontend.tests.test_models

# Run with coverage
python manage.py test frontend --coverage
```

## Performance Considerations

### Database Optimization
- Optimized indexes for frequent queries
- `select_related` and `prefetch_related` for query optimization
- Pagination for large datasets
- Database connection pooling

### Caching Strategy
- Cache frequently accessed data
- Cache dashboard summaries
- Cache streak calculations
- Cache chart data

### API Performance
- Pagination for all list endpoints
- Efficient query patterns
- Minimal data transfer
- Response compression

## Security Features

### Data Validation
- Comprehensive input validation with serializers
- Field-level validation for all models
- Sanitization of user-generated content
- Protection against injection attacks

### Authentication & Authorization
- JWT-based authentication
- User-scoped data access
- Permission checks on all endpoints
- Rate limiting for API calls

### Data Privacy
- User data isolation
- Secure file handling for photos
- Encrypted sensitive data storage
- GDPR compliance considerations

## Deployment Considerations

### Environment Variables
No additional environment variables required beyond the main ZoeFit configuration.

### Database Migration
Run migrations after deployment:
```bash
python manage.py migrate frontend
```

### Static Files
No additional static files required for this module.

### Monitoring
Monitor the following metrics:
- API response times
- Database query performance
- User engagement rates
- Streak calculation performance

## Future Enhancements

### Planned Features
- Real-time workout tracking
- Advanced analytics and insights
- Social features and competitions
- Integration with fitness devices
- Mobile app offline support

### Scalability Improvements
- Database sharding for large datasets
- Redis caching for performance
- Background job processing
- API rate limiting and throttling

## Support and Maintenance

### Common Issues
- Streak calculation errors
- Performance with large datasets
- Data validation failures
- Integration issues with AI module

### Troubleshooting
- Check database indexes
- Verify model relationships
- Review API response formats
- Monitor error logs

### Contributing
When contributing to the frontend module:
1. Follow Django and DRF best practices
2. Add comprehensive tests for new features
3. Update documentation
4. Consider performance implications
5. Ensure backward compatibility

## License

This module is part of the ZoeFit project and follows the same licensing terms.
