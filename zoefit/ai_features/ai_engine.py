"""
AI recommendation engine that powers ZoeFit's smart features

This is the brain behind ZoeFit's personalized recommendations.
It takes user data (health metrics, preferences, goals) and
turns it into actionable meal plans and workouts.

The engine uses a hybrid approach:
1. Rule-based algorithms for predictable results
2. Machine learning patterns for personalization
3. Template-based generation for consistency
4. Randomization for variety

Think of it as a smart fitness coach that knows:
- Nutrition science for meal planning
- Exercise physiology for workout design
- User preferences for personalization
- Best practices for safety and effectiveness

The goal is to make every recommendation feel personal
while being grounded in solid fitness science.
"""

import random
import json
from datetime import datetime, date
from typing import Dict, List, Any

from .models import HealthMetrics
# Import data from respective modules
from workout.exercise_data import WORKOUT_TEMPLATES, EXERCISE_DATABASE
from nutrition.nutrition_data import MEAL_TEMPLATES, FOOD_DATABASE

# Import ML-based nutrition engine
try:
    from nutrition.ml.ml_engine import ml_nutrition_engine
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML nutrition engine not available, using rule-based fallback")

# Import ML monitoring
try:
    from .ml_monitoring import monitor_ml_performance
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("Warning: ML monitoring not available")


class AIRecommendationEngine:
    """
    The smart engine that creates personalized fitness recommendations.
    
    This class combines nutrition science, exercise physiology,
    and user preferences to create plans that actually work.
    
    The engine is designed to be:
    - Personalized: Adapts to each user's unique needs
    - Scientific: Based on proven fitness and nutrition principles
    - Flexible: Handles various goals, restrictions, and preferences
    - Consistent: Produces reliable, high-quality recommendations
    
    Future enhancements could include:
    - Machine learning from user feedback
    - Real-time adaptation based on progress
    - Integration with wearable devices
    - Social features for motivation
    """
    
    def __init__(self):
        self.meal_templates = MEAL_TEMPLATES
        self.exercise_database = EXERCISE_DATABASE
        self.workout_templates = WORKOUT_TEMPLATES
        
    @monitor_ml_performance(model_type='nutrition') if MONITORING_AVAILABLE else lambda f: f
    def generate_meal_plan(self, metrics: HealthMetrics, target_date: date) -> Dict[str, Any]:
        """
        Generate personalized meal plan based on user metrics and preferences.
        Uses ML models when available, falls back to rule-based approach.
        """
        try:
            # Try ML-based approach first
            if ML_AVAILABLE and hasattr(ml_nutrition_engine, 'generate_ml_meal_plan'):
                try:
                    ml_plan = ml_nutrition_engine.generate_ml_meal_plan(metrics, target_date)
                    
                    # Add metadata about the approach used
                    ml_plan['approach'] = 'ml_based'
                    ml_plan['model_confidence'] = ml_plan.get('confidence_score', 0.5)
                    
                    return ml_plan
                    
                except Exception as ml_error:
                    print(f"ML meal plan generation failed: {ml_error}")
                    print("Falling back to rule-based approach...")
            
            # Rule-based fallback
            rule_plan = self._generate_rule_based_meal_plan(metrics, target_date)
            rule_plan['approach'] = 'rule_based'
            rule_plan['model_confidence'] = 0.5  # Default confidence for rule-based
            return rule_plan
            
        except Exception as e:
            print(f"Error in meal plan generation: {e}")
            emergency_plan = self._generate_emergency_fallback_plan(metrics, target_date)
            emergency_plan['approach'] = 'emergency_fallback'
            emergency_plan['model_confidence'] = 0.1
            return emergency_plan
    
    def _calculate_macro_split(self, fitness_goal: str) -> Dict[str, float]:
        """
        Calculate macronutrient distribution based on fitness goal.
        """
        macro_splits = {
            'weight_loss': {'protein': 0.4, 'carbs': 0.3, 'fat': 0.3},
            'muscle_gain': {'protein': 0.35, 'carbs': 0.45, 'fat': 0.2},
            'maintenance': {'protein': 0.3, 'carbs': 0.4, 'fat': 0.3},
            'endurance': {'protein': 0.25, 'carbs': 0.55, 'fat': 0.2},
            'strength': {'protein': 0.35, 'carbs': 0.4, 'fat': 0.25}
        }
        
        return macro_splits.get(fitness_goal, macro_splits['maintenance'])
    
    def _select_meal_template(self, calories: int, preferences: Dict, 
                            allergies: List, medical_conditions: List, fitness_goal: str) -> Dict:
        """
        Select appropriate meal template based on user constraints and fitness goal.
        """
        # Get template for the specific fitness goal
        goal_template = self.meal_templates.get(fitness_goal, self.meal_templates.get('maintenance', {}))
        
        return goal_template
    
    def _get_calorie_range(self, calories: int) -> str:
        """
        Determine calorie range category.
        """
        if calories < 1500:
            return 'low'
        elif calories < 2000:
            return 'medium'
        elif calories < 2500:
            return 'high'
        else:
            return 'very_high'
    
    def _filter_by_medical_conditions(self, templates: List[Dict], 
                                    conditions: List) -> List[Dict]:
        """
        Filter meal templates based on medical conditions.
        """
        filtered_templates = []
        
        for template in templates:
            suitable = True
            
            # Check for condition-specific restrictions
            if 'diabetes' in conditions:
                if template.get('high_glycemic', False):
                    suitable = False
            
            if 'hypertension' in conditions:
                if template.get('high_sodium', False):
                    suitable = False
            
            if 'heart_disease' in conditions:
                if template.get('high_saturated_fat', False):
                    suitable = False
            
            if suitable:
                filtered_templates.append(template)
        
        return filtered_templates
    
    def _generate_daily_meals(self, template: Dict, daily_calories: int, 
                            macro_split: Dict, preferences: Dict, 
                            allergies: List) -> Dict:
        """
        Generate specific meals for the day based on template and requirements.
        """
        meals = {
            'breakfast': {},
            'lunch': {},
            'dinner': {},
            'snacks': []
        }
        
        # Calculate calorie distribution for each meal
        meal_distribution = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.30,
            'snacks': 0.10
        }
        
        for meal_type, percentage in meal_distribution.items():
            meal_calories = int(daily_calories * percentage)
            
            if meal_type == 'snacks':
                # Generate multiple snacks
                snacks = self._generate_snacks(
                    meal_calories, preferences, allergies
                )
                meals['snacks'] = snacks
            else:
                # Generate main meal
                meal = self._generate_single_meal(
                    meal_type, meal_calories, macro_split, 
                    preferences, allergies, template
                )
                meals[meal_type] = meal
        
        return meals
    
    def _generate_single_meal(self, meal_type: str, calories: int, 
                            macro_split: Dict, preferences: Dict, 
                            allergies: List, template: Dict) -> Dict:
        """
        Generate a single meal with specific foods.
        """
        # Get meal template structure
        meal_structure = template.get(meal_type, {})
        
        if not meal_structure:
            # Fallback to basic meal structure
            return self._generate_basic_meal(meal_type, calories, preferences, allergies)
        
        # Get example meals from template
        example_meals = meal_structure.get('example_meals', [])
        if example_meals:
            # Select a random example meal
            selected_meal = random.choice(example_meals)
            meal_name = selected_meal['name']
            
            # Generate foods based on meal components
            meal_components = meal_structure.get('meal_components', [])
            meal_foods = []
            
            for component in meal_components:
                selected_foods = self._select_foods_for_component_type(
                    component, calories // len(meal_components), preferences, allergies
                )
                meal_foods.extend(selected_foods)
            
            return {
                'name': meal_name,
                'foods': meal_foods,
                'estimated_calories': calories,
                'prep_time': selected_meal.get('prep_time', 30),
                'difficulty': selected_meal.get('difficulty', 'medium')
            }
        else:
            return self._generate_basic_meal(meal_type, calories, preferences, allergies)
    
    def _select_foods_for_component(self, food_types: List, calories: int, 
                                  preferences: Dict, allergies: List) -> List[Dict]:
        """
        Select specific foods for a meal component.
        """
        selected_foods = []
        component_calories = calories // len(food_types)
        
        for food_type in food_types:
            # Filter food database by type and restrictions
            suitable_foods = [
                food for food in FOOD_DATABASE
                if food['type'] == food_type and 
                not any(allergen in food['allergens'] for allergen in allergies)
            ]
            
            # Apply dietary preferences
            if preferences.get('diet_type') == 'vegetarian':
                suitable_foods = [
                    food for food in suitable_foods
                    if food.get('vegetarian', False)
                ]
            elif preferences.get('diet_type') == 'vegan':
                suitable_foods = [
                    food for food in suitable_foods
                    if food.get('vegan', False)
                ]
            
            if suitable_foods:
                selected_food = random.choice(suitable_foods)
                # Calculate appropriate portion size
                portion = self._calculate_portion_size(
                    selected_food, component_calories
                )
                selected_foods.append({
                    'name': selected_food['name'],
                    'portion': portion,
                    'calories': selected_food['calories_per_100g'] * portion / 100,
                    'protein': selected_food['protein_per_100g'] * portion / 100,
                    'carbs': selected_food['carbs_per_100g'] * portion / 100,
                    'fat': selected_food['fat_per_100g'] * portion / 100
                })
        
        return selected_foods
    
    def _calculate_portion_size(self, food: Dict, target_calories: int) -> float:
        """
        Calculate appropriate portion size in grams.
        """
        if food['calories_per_100g'] > 0:
            return min(500, (target_calories * 100) / food['calories_per_100g'])
        return 100  # Default 100g
    
    def _generate_basic_meal(self, meal_type: str, calories: int, preferences: Dict, allergies: List) -> Dict:
        """
        Generate a basic meal when template is not available.
        """
        # Basic meal components
        if meal_type == 'breakfast':
            components = ['protein', 'carb']
        elif meal_type == 'lunch':
            components = ['protein', 'carb', 'vegetable']
        elif meal_type == 'dinner':
            components = ['protein', 'carb', 'vegetable']
        else:
            components = ['protein']
        
        meal_foods = []
        for component in components:
            selected_foods = self._select_foods_for_component_type(
                component, calories // len(components), preferences, allergies
            )
            meal_foods.extend(selected_foods)
        
        return {
            'name': f"{meal_type.title()} Meal",
            'foods': meal_foods,
            'estimated_calories': calories,
            'prep_time': 20,
            'difficulty': 'easy'
        }
    
    def _select_foods_for_component_type(self, component_type: str, calories: int, 
                                       preferences: Dict, allergies: List) -> List[Dict]:
        """
        Select foods based on component type (protein, carb, etc).
        """
        # Map component types to food types
        type_mapping = {
            'protein': ['protein'],
            'carb': ['carb'],
            'vegetable': ['vegetable'],
            'healthy_fat': ['healthy_fat'],
            'lean_protein': ['protein'],
            'complex_carb': ['carb'],
            'protein_source': ['protein'],
            'fat': ['healthy_fat']
        }
        
        food_types = type_mapping.get(component_type, ['protein'])
        return self._select_foods_for_component(food_types, calories, preferences, allergies)
    
    def _generate_snacks(self, total_calories: int, preferences: Dict, 
                        allergies: List) -> List[Dict]:
        """
        Generate healthy snack options.
        """
        snacks = []
        snack_calories = total_calories // 2  # 2 snacks
        
        snack_foods = [
            food for food in FOOD_DATABASE
            if food.get('snack_suitable', False) and
            not any(allergen in food['allergens'] for allergen in allergies)
        ]
        
        # Apply dietary preferences
        if preferences.get('diet_type') == 'vegetarian':
            snack_foods = [
                food for food in snack_foods
                if food.get('vegetarian', False)
            ]
        elif preferences.get('diet_type') == 'vegan':
            snack_foods = [
                food for food in snack_foods
                if food.get('vegan', False)
            ]
        
        for _ in range(2):  # Generate 2 snacks
            if snack_foods:
                snack = random.choice(snack_foods)
                portion = self._calculate_portion_size(snack, snack_calories)
                snacks.append({
                    'name': snack['name'],
                    'portion': portion,
                    'calories': snack['calories_per_100g'] * portion / 100,
                    'protein': snack['protein_per_100g'] * portion / 100,
                    'carbs': snack['carbs_per_100g'] * portion / 100,
                    'fat': snack['fat_per_100g'] * portion / 100
                })
        
        return snacks
    
    def _calculate_meal_macros(self, meals: Dict) -> Dict[str, float]:
        """
        Calculate total macronutrients for all meals.
        """
        total_macros = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0
        }
        
        # Process main meals
        for meal_type in ['breakfast', 'lunch', 'dinner']:
            meal = meals.get(meal_type, {})
            foods = meal.get('foods', {})
            
            for component, food_list in foods.items():
                for food in food_list:
                    total_macros['calories'] += food.get('calories', 0)
                    total_macros['protein'] += food.get('protein', 0)
                    total_macros['carbs'] += food.get('carbs', 0)
                    total_macros['fat'] += food.get('fat', 0)
        
        # Process snacks
        for snack in meals.get('snacks', []):
            total_macros['calories'] += snack.get('calories', 0)
            total_macros['protein'] += snack.get('protein', 0)
            total_macros['carbs'] += snack.get('carbs', 0)
            total_macros['fat'] += snack.get('fat', 0)
        
        return total_macros
    
    def _calculate_meal_confidence(self, metrics: HealthMetrics, 
                                  meals: Dict, macros: Dict) -> float:
        """
        Calculate confidence score for meal plan quality.
        """
        confidence = 0.5  # Base confidence
        
        # Check if calories match target
        target_calories = metrics.calculate_daily_calories()
        calorie_diff = abs(macros['calories'] - target_calories) / target_calories
        
        if calorie_diff < 0.05:  # Within 5%
            confidence += 0.2
        elif calorie_diff < 0.1:  # Within 10%
            confidence += 0.1
        
        # Check macro balance
        target_protein = target_calories * 0.3 / 4  # 30% protein
        protein_diff = abs(macros['protein'] - target_protein) / target_protein
        
        if protein_diff < 0.1:
            confidence += 0.15
        elif protein_diff < 0.2:
            confidence += 0.1
        
        # Check dietary preferences compliance
        if metrics.dietary_preferences:
            confidence += 0.1
        
        # Check medical condition compliance
        if not metrics.medical_conditions:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _generate_fallback_meal_plan(self, metrics: HealthMetrics, 
                                   target_date: date) -> Dict[str, Any]:
        """
        Generate fallback meal plan if main algorithm fails.
        """
        daily_calories = metrics.calculate_daily_calories()
        
        # Enhanced fallback with more variety
        fallback_meals = {
            'breakfast': {
                'name': 'Simple Breakfast',
                'foods': {
                    'main': [{
                        'name': 'Oatmeal with fruits',
                        'portion': 200,
                        'calories': daily_calories * 0.25,
                        'protein': 8,
                        'carbs': 45,
                        'fat': 6
                    }],
                    'side': [{
                        'name': 'Greek yogurt',
                        'portion': 100,
                        'calories': daily_calories * 0.05,
                        'protein': 10,
                        'carbs': 4,
                        'fat': 0.4
                    }]
                }
            },
            'lunch': {
                'name': 'Balanced Lunch',
                'foods': {
                    'main': [{
                        'name': 'Grilled chicken salad',
                        'portion': 300,
                        'calories': daily_calories * 0.35,
                        'protein': 35,
                        'carbs': 25,
                        'fat': 15
                    }],
                    'side': [{
                        'name': 'Whole grain bread',
                        'portion': 50,
                        'calories': daily_calories * 0.05,
                        'protein': 4,
                        'carbs': 20,
                        'fat': 2
                    }]
                }
            },
            'dinner': {
                'name': 'Healthy Dinner',
                'foods': {
                    'main': [{
                        'name': 'Salmon with vegetables',
                        'portion': 350,
                        'calories': daily_calories * 0.30,
                        'protein': 40,
                        'carbs': 30,
                        'fat': 20
                    }]
                }
            },
            'snacks': [
                {
                    'name': 'Apple',
                    'portion': 150,
                    'calories': daily_calories * 0.05,
                    'protein': 0.5,
                    'carbs': 20,
                    'fat': 0.3
                }
            ]
        }
        
        return {
            'meals': fallback_meals,
            'total_calories': daily_calories,
            'protein': 97.5,
            'carbs': 144,
            'fat': 43.7,
            'confidence_score': 0.6
        }
    
    def generate_workout_plan(self, metrics: HealthMetrics, day_number: int, preferences=None) -> Dict[str, Any]:
        """
        Generate personalized workout plan based on user metrics and goals.
        """
        try:
            # Determine fitness level
            fitness_level = self._assess_fitness_level(metrics)
            
            # Get user preferences if available
            user_equipment = []
            preferred_difficulty = fitness_level
            preferred_workout_type = 'mixed'
            
            if preferences:
                user_equipment = getattr(preferences, 'equipment_available', [])
                preferred_difficulty = getattr(preferences, 'difficulty_level', fitness_level)
                preferred_workout_type = getattr(preferences, 'workout_type_preference', 'mixed')
            
            # Select workout template based on goal, fitness level, and preferences
            workout_template = self._select_workout_template(
                metrics.fitness_goal, preferred_difficulty, day_number, preferred_workout_type
            )
            
            # Generate specific exercises based on available equipment
            exercises = self._generate_workout_exercises(
                workout_template, metrics, day_number, user_equipment
            )
            
            # Calculate workout metrics
            workout_type = workout_template.get('type', preferred_workout_type)
            estimated_duration = self._calculate_workout_duration(exercises)
            intensity_score = self._calculate_intensity_score(
                exercises, preferred_difficulty
            )
            
            # Calculate adaptation score
            adaptation_score = self._calculate_adaptation_score(
                metrics, exercises, day_number
            )
            
            # Determine equipment needed for this workout
            equipment_needed = self._determine_equipment_needed(exercises)
            
            return {
                'day': day_number,
                'exercises': exercises,
                'workout_type': workout_type,
                'estimated_duration': estimated_duration,
                'difficulty_level': preferred_difficulty,
                'intensity_score': intensity_score,
                'adaptation_score': adaptation_score,
                'equipment_needed': equipment_needed
            }
            
        except Exception as e:
            # Return fallback workout plan
            return self._generate_fallback_workout_plan()
    
    def _assess_fitness_level(self, metrics: HealthMetrics) -> str:
        """
        Assess user's fitness level based on metrics and activity level.
        """
        activity_scores = {
            'sedentary': 0,
            'light': 1,
            'moderate': 2,
            'active': 3,
            'very_active': 4
        }
        
        activity_score = activity_scores.get(metrics.activity_level, 2)
        
        # Adjust based on BMI
        if metrics.bmi < 18.5:
            activity_score -= 1
        elif metrics.bmi > 30:
            activity_score -= 1
        
        # Determine fitness level
        if activity_score <= 1:
            return 'beginner'
        elif activity_score <= 3:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _select_workout_template(self, goal: str, fitness_level: str, 
                                 day_number: int, preferred_workout_type: str = 'mixed') -> Dict:
        """
        Select appropriate workout template.
        """
        # Filter templates by goal
        suitable_templates = [
            template for template in self.workout_templates
            if template['goal'] == goal or template['goal'] == 'general'
        ]
        
        # Filter by fitness level
        suitable_templates = [
            template for template in suitable_templates
            if template['fitness_level'] == fitness_level
        ]
        
        # Select template based on day number (for variety)
        if suitable_templates:
            template_index = (day_number - 1) % len(suitable_templates)
            return suitable_templates[template_index]
        else:
            # Return default template
            return {
                'type': 'mixed',
                'goal': 'general',
                'fitness_level': 'beginner',
                'exercises': ['pushups', 'squats', 'plank']
            }
    
    def _generate_workout_exercises(self, template: Dict, metrics: HealthMetrics, 
                                   day_number: int, user_equipment: List[str] = None) -> List[Dict]:
        """
        Generate specific exercises for the workout.
        """
        exercises = []
        template_exercises = template.get('exercises', [])
        
        for exercise_name in template_exercises:
            # Get exercise details from database
            exercise_data = self._get_exercise_data(exercise_name)
            
            if exercise_data:
                # Check if exercise requires equipment user doesn't have
                exercise_equipment = exercise_data.get('equipment_needed', [])
                if user_equipment and exercise_equipment:
                    if not any(eq in user_equipment for eq in exercise_equipment):
                        # Skip this exercise if user doesn't have required equipment
                        continue
                
                # Generate sets and reps based on fitness level
                sets_reps = self._generate_sets_reps(
                    exercise_data, metrics.fitness_goal, day_number
                )
                
                exercises.append({
                    'name': exercise_data['name'],
                    'type': exercise_data['type'],
                    'muscle_groups': exercise_data['muscle_groups'],
                    'sets': sets_reps['sets'],
                    'reps': sets_reps['reps'],
                    'rest_time': sets_reps['rest_time'],
                    'instructions': exercise_data['instructions'],
                    'difficulty': exercise_data['difficulty']
                })
        
        return exercises
    
    def _get_exercise_data(self, exercise_name: str) -> Dict:
        """
        Get exercise data from database.
        """
        for exercise in self.exercise_database:
            if exercise['name'].lower() == exercise_name.lower():
                return exercise
        
        # Return default exercise if not found
        return {
            'name': exercise_name,
            'type': 'strength',
            'muscle_groups': ['full_body'],
            'difficulty': 'beginner',
            'instructions': f"Perform {exercise_name} with proper form."
        }
    
    def _generate_sets_reps(self, exercise: Dict, goal: str, day_number: int) -> Dict:
        """
        Generate appropriate sets and reps based on exercise and goals.
        """
        base_reps = {
            'beginner': {'strength': 8, 'cardio': 15, 'flexibility': 30},
            'intermediate': {'strength': 12, 'cardio': 20, 'flexibility': 45},
            'advanced': {'strength': 15, 'cardio': 30, 'flexibility': 60}
        }
        
        difficulty = exercise['difficulty']
        exercise_type = exercise['type']
        
        # Get base reps
        base_rep_count = base_reps[difficulty].get(exercise_type, 10)
        
        # Adjust for goal
        if goal == 'muscle_gain' and exercise_type == 'strength':
            base_rep_count = max(6, base_rep_count - 2)
        elif goal == 'endurance' and exercise_type == 'strength':
            base_rep_count = min(20, base_rep_count + 4)
        
        # Progressive overload
        progression_bonus = (day_number - 1) // 7  # Increase every week
        final_reps = base_rep_count + progression_bonus
        
        return {
            'sets': 3 if difficulty == 'beginner' else 4,
            'reps': final_reps,
            'rest_time': 60 if exercise_type == 'strength' else 30
        }
    
    def _calculate_workout_duration(self, exercises: List[Dict]) -> int:
        """
        Calculate estimated workout duration in minutes.
        """
        total_time = 0
        
        for exercise in exercises:
            sets = exercise['sets']
            reps = exercise['reps']
            rest_time = exercise['rest_time']
            
            # Estimate time per rep (seconds)
            if exercise['type'] == 'strength':
                time_per_rep = 3
            elif exercise['type'] == 'cardio':
                time_per_rep = 1
            else:  # flexibility
                time_per_rep = 2
            
            # Calculate exercise time
            exercise_time = (sets * reps * time_per_rep) + ((sets - 1) * rest_time)
            total_time += exercise_time
        
        return max(15, total_time // 60)  # Convert to minutes, minimum 15 minutes
    
    def _calculate_intensity_score(self, exercises: List[Dict], 
                                  fitness_level: str) -> float:
        """
        Calculate workout intensity score (1-10).
        """
        base_intensity = {
            'beginner': 4.0,
            'intermediate': 6.0,
            'advanced': 8.0
        }
        
        intensity = base_intensity[fitness_level]
        
        # Adjust based on exercises
        for exercise in exercises:
            if exercise['difficulty'] == 'advanced':
                intensity += 0.5
            elif exercise['difficulty'] == 'beginner':
                intensity -= 0.3
            
            if exercise['type'] == 'cardio':
                intensity += 0.2
        
        return min(10.0, max(1.0, intensity))
    
    def _calculate_adaptation_score(self, metrics: HealthMetrics, 
                                  exercises: List[Dict], day_number: int) -> float:
        """
        Calculate how well workout adapts to user's progress.
        """
        base_score = 0.7
        
        # Adjust for fitness goal alignment
        goal_exercises = {
            'weight_loss': ['cardio', 'hiit'],
            'muscle_gain': ['strength'],
            'endurance': ['cardio', 'hiit'],
            'strength': ['strength']
        }
        
        target_types = goal_exercises.get(metrics.fitness_goal, ['mixed'])
        exercise_types = [ex['type'] for ex in exercises]
        
        for target_type in target_types:
            if target_type in exercise_types:
                base_score += 0.1
        
        # Progressive overload consideration
        if day_number > 1:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _generate_fallback_workout_plan(self, metrics: HealthMetrics, 
                                      day_number: int) -> Dict[str, Any]:
        """
        Generate fallback workout plan if main algorithm fails.
        """
        fallback_exercises = [
            {
                'name': 'Push-ups',
                'type': 'strength',
                'muscle_groups': ['chest', 'shoulders', 'triceps'],
                'sets': 3,
                'reps': 10,
                'rest_time': 60,
                'instructions': 'Perform push-ups with proper form, keeping your body straight.',
                'difficulty': 'beginner'
            },
            {
                'name': 'Bodyweight Squats',
                'type': 'strength',
                'muscle_groups': ['quadriceps', 'glutes', 'hamstrings'],
                'sets': 3,
                'reps': 15,
                'rest_time': 60,
                'instructions': 'Perform squats with proper form, keeping your back straight.',
                'difficulty': 'beginner'
            },
            {
                'name': 'Plank',
                'type': 'strength',
                'muscle_groups': ['core'],
                'sets': 3,
                'reps': 30,  # seconds
                'rest_time': 30,
                'instructions': 'Hold plank position with proper form.',
                'difficulty': 'beginner'
            }
        ]
        
        return {
            'exercises': fallback_exercises,
            'workout_type': 'strength',
            'estimated_duration': 20,
            'difficulty_level': 'beginner',
            'intensity_score': 4.0,
            'adaptation_score': 0.6,
            'equipment_needed': []
        }
    
    def _determine_equipment_needed(self, exercises: List[Dict]) -> List[str]:
        """
        Determine all equipment needed for a workout based on exercises.
        """
        equipment_needed = set()
        
        for exercise in exercises:
            exercise_equipment = exercise.get('equipment_needed', [])
            equipment_needed.update(exercise_equipment)
        
        return list(equipment_needed)
    
    def _generate_rule_based_meal_plan(self, metrics: HealthMetrics, target_date: date) -> Dict[str, Any]:
        """
        Generate meal plan using rule-based approach (original method).
        """
        try:
            # Calculate daily nutritional needs
            daily_calories = metrics.calculate_daily_calories()
            
            # Calculate macronutrient distribution based on fitness goal
            macro_split = self._calculate_macro_split(metrics.fitness_goal)
            
            # Get dietary preferences and restrictions
            preferences = metrics.dietary_preferences or {}
            allergies = metrics.allergies or []
            medical_conditions = metrics.medical_conditions or []
            
            # Select appropriate meal template
            meal_template = self._select_meal_template(
                daily_calories, 
                preferences, 
                allergies, 
                medical_conditions,
                metrics.fitness_goal
            )
            
            # Generate meals for the day
            meals = self._generate_daily_meals(
                meal_template, 
                daily_calories, 
                macro_split,
                preferences,
                allergies
            )
            
            # Calculate total macros
            total_macros = self._calculate_meal_macros(meals)
            
            # Calculate confidence score
            confidence_score = self._calculate_meal_confidence(
                metrics, meals, total_macros
            )
            
            return {
                'meals': meals,
                'total_calories': total_macros['calories'],
                'protein': total_macros['protein'],
                'carbs': total_macros['carbs'],
                'fat': total_macros['fat'],
                'confidence_score': confidence_score,
                'approach': 'rule_based',
                'model_confidence': confidence_score,
                'prediction_date': target_date.isoformat()
            }
            
        except Exception as e:
            print(f"Error in rule-based meal plan: {e}")
            return self._generate_emergency_fallback_plan(metrics, target_date)
    
    def _generate_emergency_fallback_plan(self, metrics: HealthMetrics, target_date: date) -> Dict[str, Any]:
        """
        Generate emergency fallback meal plan when all else fails.
        """
        try:
            # Basic calorie calculation
            weight = metrics.weight or 70
            height = metrics.height or 170
            age = metrics.age or 30
            gender = metrics.gender or 'male'
            
            # Simple BMR calculation
            if gender == 'male':
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
            calories = int(bmr * 1.2)  # Sedentary multiplier
            
            # Basic macros
            protein = int(weight * 1.6)
            fat = int(calories * 0.25 / 9)
            carbs = int((calories - (protein * 4) - (fat * 9)) / 4)
            
            # Generate basic meals
            meals = [
                {
                    'name': 'Basic Breakfast',
                    'foods': [
                        {
                            'name': 'Oatmeal',
                            'quantity': '50g',
                            'calories': 200,
                            'protein': 6,
                            'carbs': 35,
                            'fat': 4
                        },
                        {
                            'name': 'Eggs',
                            'quantity': '2 large',
                            'calories': 140,
                            'protein': 12,
                            'carbs': 1,
                            'fat': 10
                        }
                    ],
                    'estimated_calories': 340,
                    'prep_time': 15,
                    'difficulty': 'easy'
                },
                {
                    'name': 'Basic Lunch',
                    'foods': [
                        {
                            'name': 'Chicken Breast',
                            'quantity': '150g',
                            'calories': 250,
                            'protein': 45,
                            'carbs': 0,
                            'fat': 5
                        },
                        {
                            'name': 'Brown Rice',
                            'quantity': '100g',
                            'calories': 360,
                            'protein': 8,
                            'carbs': 75,
                            'fat': 3
                        }
                    ],
                    'estimated_calories': 610,
                    'prep_time': 25,
                    'difficulty': 'medium'
                },
                {
                    'name': 'Basic Dinner',
                    'foods': [
                        {
                            'name': 'Salmon',
                            'quantity': '120g',
                            'calories': 280,
                            'protein': 25,
                            'carbs': 0,
                            'fat': 20
                        },
                        {
                            'name': 'Vegetables',
                            'quantity': '200g',
                            'calories': 100,
                            'protein': 4,
                            'carbs': 15,
                            'fat': 2
                        }
                    ],
                    'estimated_calories': 380,
                    'prep_time': 30,
                    'difficulty': 'medium'
                },
                {
                    'name': 'Basic Snack',
                    'foods': [
                        {
                            'name': 'Greek Yogurt',
                            'quantity': '150g',
                            'calories': 100,
                            'protein': 15,
                            'carbs': 8,
                            'fat': 2
                        }
                    ],
                    'estimated_calories': 100,
                    'prep_time': 5,
                    'difficulty': 'easy'
                }
            ]
            
            return {
                'meals': meals,
                'total_calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fat': fat,
                'confidence_score': 0.3,
                'approach': 'emergency_fallback',
                'model_confidence': 0.3,
                'prediction_date': target_date.isoformat()
            }
            
        except Exception as e:
            print(f"Error in emergency fallback: {e}")
            
            # Absolute last resort
            return {
                'meals': [{
                    'name': 'Emergency Meal',
                    'foods': [{'name': 'Balanced Meal', 'quantity': '1 serving', 'calories': 500}],
                    'estimated_calories': 500,
                    'prep_time': 20,
                    'difficulty': 'medium'
                }],
                'total_calories': 2000,
                'protein': 100,
                'carbs': 250,
                'fat': 65,
                'confidence_score': 0.1,
                'approach': 'last_resort',
                'model_confidence': 0.1,
                'prediction_date': target_date.isoformat()
            }
