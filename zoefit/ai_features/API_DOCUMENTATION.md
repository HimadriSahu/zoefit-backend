# AI Features API Documentation

## Overview

The AI Features API provides endpoints for personalized meal planning, workout recommendations, and AI chatbot functionality. All endpoints require JWT authentication.

## Base URL
```
/api/ai/
```

## Authentication

All requests must include a valid JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### Health Metrics

#### Create/Update Health Metrics
```http
POST /api/ai/health-metrics/
```

**Request Body:**
```json
{
    "height": 175.0,
    "weight": 70.0,
    "fitness_goal": "weight_loss",
    "activity_level": "moderate",
    "dietary_preferences": {
        "diet_type": "omnivore",
        "preferences": ["low_carb"]
    },
    "medical_conditions": ["none"],
    "allergies": ["nuts"],
    "target_weight": 65.0
}
```

**Response:**
```json
{
    "message": "Health metrics updated successfully",
    "metrics": {
        "height": 175.0,
        "weight": 70.0,
        "bmi": 22.9,
        "bmi_category": "Normal",
        "fitness_goal": "weight_loss",
        "activity_level": "moderate",
        "daily_calories": 1800
    }
}
```

#### Get Health Metrics
```http
GET /api/ai/health-metrics/get/
```

**Response:**
```json
{
    "height": 175.0,
    "weight": 70.0,
    "bmi": 22.9,
    "bmi_category": "Normal",
    "fitness_goal": "weight_loss",
    "activity_level": "moderate",
    "dietary_preferences": {...},
    "medical_conditions": [...],
    "allergies": [...],
    "target_weight": 65.0,
    "daily_calories": 1800,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### Meal Plans

#### Generate Meal Plan
```http
POST /api/ai/meal-plan/generate/
```

**Request Body:**
```json
{
    "date": "2024-01-01"
}
```

**Response:**
```json
{
    "message": "Meal plan generated successfully",
    "meal_plan": {
        "id": 1,
        "date": "2024-01-01",
        "meals": {
            "breakfast": {
                "name": "Breakfast Meal",
                "foods": {
                    "main": [
                        {
                            "name": "Oatmeal with fruits",
                            "portion": 200,
                            "calories": 250,
                            "protein": 8,
                            "carbs": 45,
                            "fat": 6
                        }
                    ]
                }
            },
            "lunch": {...},
            "dinner": {...},
            "snacks": [...]
        },
        "total_calories": 1800,
        "protein": 90,
        "carbs": 180,
        "fat": 60,
        "confidence_score": 0.85
    }
}
```

#### Get Meal Plans
```http
GET /api/ai/meal-plans/?start_date=2024-01-01&end_date=2024-01-07
```

**Response:**
```json
{
    "meal_plans": [
        {
            "id": 1,
            "date": "2024-01-01",
            "meals": {...},
            "total_calories": 1800,
            "protein": 90,
            "carbs": 180,
            "fat": 60,
            "user_rating": null,
            "user_feedback": null
        }
    ]
}
```

### Workout Plans

#### Generate Workout Plan
```http
POST /api/ai/workout-plan/generate/
```

**Request Body:**
```json
{
    "day": 1
}
```

**Response:**
```json
{
    "message": "Workout plan generated successfully",
    "workout_plan": {
        "id": 1,
        "day": 1,
        "exercises": [
            {
                "name": "Push-ups",
                "type": "strength",
                "muscle_groups": ["chest", "shoulders", "triceps"],
                "sets": 3,
                "reps": 12,
                "rest_time": 60,
                "instructions": "Perform push-ups with proper form...",
                "difficulty": "beginner"
            }
        ],
        "workout_type": "strength",
        "estimated_duration": 30,
        "difficulty_level": "beginner",
        "intensity_score": 5.0,
        "equipment_needed": [],
        "adaptation_score": 0.8
    }
}
```

#### Get Workout Plans
```http
GET /api/ai/workout-plans/
```

**Response:**
```json
{
    "workout_plans": [
        {
            "id": 1,
            "day": 1,
            "exercises": [...],
            "workout_type": "strength",
            "estimated_duration": 30,
            "difficulty_level": "beginner",
            "intensity_score": 5.0,
            "equipment_needed": [],
            "completed": false,
            "completion_time": null,
            "user_rating": null
        }
    ]
}
```

#### Update Workout Completion
```http
POST /api/ai/workout-complete/
```

**Request Body:**
```json
{
    "workout_id": 1,
    "completed": true,
    "completion_time_minutes": 35,
    "rating": 4
}
```

**Response:**
```json
{
    "message": "Workout completion updated successfully"
}
```

### AI Chatbot

#### Chat with AI
```http
POST /api/ai/chat/
```

**Request Body:**
```json
{
    "message": "What exercises should I do for weight loss?"
}
```

**Response:**
```json
{
    "response": "For weight loss, I recommend combining strength training with cardio. Focus on compound exercises like squats, push-ups, and burpees, along with 20-30 minutes of cardio 3-4 times per week.",
    "intent": "exercise_advice",
    "confidence": 0.9,
    "suggestions": [
        "Ask about specific exercises",
        "Learn about workout routines",
        "Get form tips and techniques"
    ],
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Get Chat History
```http
GET /api/ai/chat/history/?limit=50
```

**Response:**
```json
{
    "chat_history": [
        {
            "id": 1,
            "user_message": "What exercises should I do for weight loss?",
            "ai_response": "For weight loss, I recommend...",
            "intent_detected": "exercise_advice",
            "confidence_score": 0.9,
            "helpful": null,
            "created_at": "2024-01-01T12:00:00Z"
        }
    ]
}
```

### Progress Tracking

#### Get Progress Data
```http
GET /api/ai/progress/
```

**Response:**
```json
{
    "progress_data": [
        {
            "id": 1,
            "weight": 70.0,
            "body_fat_percentage": 15.0,
            "muscle_mass": 35.0,
            "workout_streak": 5,
            "total_workouts": 20,
            "calories_burned": 5000,
            "progress_score": 75.0,
            "achievement_badges": ["first_workout", "week_streak"],
            "ai_insights": "Great progress! You've been consistent...",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

## Data Models

### HealthMetrics
- `height`: Height in cm (float)
- `weight`: Weight in kg (float)
- `bmi`: Body Mass Index (float, calculated)
- `fitness_goal`: One of 'weight_loss', 'muscle_gain', 'maintenance', 'endurance', 'strength'
- `activity_level`: One of 'sedentary', 'light', 'moderate', 'active', 'very_active'
- `dietary_preferences`: JSON object with dietary restrictions and preferences
- `medical_conditions`: Array of medical conditions
- `allergies`: Array of food allergies
- `target_weight`: Target weight in kg (float, optional)

### MealPlan
- `date`: Date of meal plan
- `meals`: JSON object with breakfast, lunch, dinner, snacks
- `total_calories`: Total calories for the day
- `protein`, `carbs`, `fat`: Macronutrient totals in grams
- `confidence_score`: AI confidence in meal plan quality (0-1)
- `user_rating`: User rating 1-5 (optional)
- `user_feedback`: User feedback text (optional)

### WorkoutPlan
- `day`: Day number in workout program
- `exercises`: Array of exercise objects
- `workout_type`: Type of workout (strength, cardio, hiit, flexibility, mixed)
- `estimated_duration`: Duration in minutes
- `difficulty_level`: beginner, intermediate, advanced
- `intensity_score`: Intensity rating (1-10)
- `equipment_needed`: Array of required equipment
- `completed`: Whether workout was completed
- `completion_time`: Actual time taken to complete
- `user_rating`: User rating 1-5 (optional)

### AIChatHistory
- `user_message`: User's message
- `ai_response`: AI's response
- `intent_detected`: Detected intent category
- `confidence_score`: AI confidence in response (0-1)
- `helpful`: Whether response was helpful (boolean, optional)

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Authentication required/failed
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
    "error": "Error message describing what went wrong"
}
```

## Rate Limiting

- Chat endpoint: Limited to 100 requests per hour per user
- Meal plan generation: Limited to 10 requests per day per user
- Workout plan generation: Limited to 10 requests per day per user

## Frontend Integration Examples

### React Native Example

```javascript
// Create health metrics
const createHealthMetrics = async (metricsData) => {
  try {
    const response = await fetch('/api/ai/health-metrics/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify(metricsData),
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error creating health metrics:', error);
  }
};

// Generate meal plan
const generateMealPlan = async (date) => {
  try {
    const response = await fetch('/api/ai/meal-plan/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ date }),
    });
    
    const data = await response.json();
    return data.meal_plan;
  } catch (error) {
    console.error('Error generating meal plan:', error);
  }
};

// Chat with AI
const chatWithAI = async (message) => {
  try {
    const response = await fetch('/api/ai/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ message }),
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error chatting with AI:', error);
  }
};
```

## Testing

Use the provided test suite to verify functionality:

```bash
python manage.py test ai_features
```

## Deployment Notes

- Ensure all environment variables are set
- Run migrations: `python manage.py migrate`
- Collect static files: `python manage.py collectstatic`
- Configure CORS for frontend domain
- Set up proper JWT token refresh mechanism
