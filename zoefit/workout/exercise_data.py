"""
Exercise Data Module - Exercise Database and Workout Templates

This module contains exercise database and workout templates used by the AI
recommendation engine for generating personalized workout plans.
"""

# Exercise Database with detailed information
EXERCISE_DATABASE = [
    # Bodyweight Exercises
    {
        'name': 'Push-ups',
        'type': 'strength',
        'muscle_groups': ['chest', 'shoulders', 'triceps', 'core'],
        'difficulty': 'beginner',
        'instructions': 'Start in plank position with hands slightly wider than shoulders. Lower your body until chest nearly touches the floor, then push back up to starting position.',
        'tips': ['Keep your body straight', 'Engage your core', 'Lower slowly for better muscle activation'],
        'variations': ['Knee push-ups', 'Wide push-ups', 'Diamond push-ups'],
        'calories_per_minute': 8
    },
    {
        'name': 'Bodyweight Squats',
        'type': 'strength',
        'muscle_groups': ['quadriceps', 'glutes', 'hamstrings', 'calves'],
        'difficulty': 'beginner',
        'equipment': [],
        'instructions': 'Stand with feet shoulder-width apart. Lower your body as if sitting in a chair, keeping your back straight and chest up. Return to starting position.',
        'tips': ['Keep knees behind toes', 'Go as low as comfortable', 'Push through heels'],
        'variations': ['Jump squats', 'Sumo squats', 'Pistol squats'],
        'calories_per_minute': 6
    },
    {
        'name': 'Plank',
        'type': 'strength',
        'muscle_groups': ['core', 'shoulders', 'back'],
        'difficulty': 'beginner',
        'equipment': [],
        'instructions': 'Hold a push-up position with your body in a straight line from head to heels. Engage your core and hold the position.',
        'tips': ['Keep hips level', 'Don\'t let your back sag', 'Breathe normally'],
        'variations': ['Side plank', 'Plank with leg lifts', 'Plank with arm raises'],
        'calories_per_minute': 4
    },
    {
        'name': 'Lunges',
        'type': 'strength',
        'muscle_groups': ['quadriceps', 'glutes', 'hamstrings', 'calves'],
        'difficulty': 'beginner',
        'equipment': [],
        'instructions': 'Step forward with one leg and lower your hips until both knees are bent at 90-degree angles. Push back to starting position and repeat with other leg.',
        'tips': ['Keep front knee behind toes', 'Keep torso upright', 'Control of movement'],
        'variations': ['Reverse lunges', 'Side lunges', 'Walking lunges'],
        'calories_per_minute': 7
    },
    {
        'name': 'Jumping Jacks',
        'type': 'cardio',
        'muscle_groups': ['full_body', 'legs', 'core'],
        'difficulty': 'beginner',
        'equipment': [],
        'instructions': 'Jump while spreading legs shoulder-width apart and raising arms overhead. Return to starting position by jumping back.',
        'tips': ['Land softly', 'Keep rhythm steady', 'Engage core throughout'],
        'variations': ['Cross jacks', 'Plyometric jacks', 'Squat jacks'],
        'calories_per_minute': 10
    },
    {
        'name': 'Mountain Climbers',
        'type': 'cardio',
        'muscle_groups': ['core', 'shoulders', 'legs'],
        'difficulty': 'intermediate',
        'equipment': [],
        'instructions': 'Start in plank position. Bring one knee toward chest, then return to plank. Alternate knees rapidly.',
        'tips': ['Keep hips down', 'Maintain plank form', 'Breathe steadily'],
        'variations': ['Cross-body mountain climbers', 'Spider mountain climbers', 'Slow mountain climbers'],
        'calories_per_minute': 12
    },
    {
        'name': 'Burpees',
        'type': 'cardio',
        'muscle_groups': ['full_body', 'chest', 'legs', 'core'],
        'difficulty': 'intermediate',
        'equipment': [],
        'instructions': 'Start standing, drop to plank, do a push-up, jump feet to hands, then jump up with arms overhead.',
        'tips': ['Land softly', 'Keep core tight', 'Pace yourself'],
        'variations': ['Half burpees', 'Burpee with push-up', 'Burpee with jump'],
        'calories_per_minute': 14
    },
    {
        'name': 'Dumbbell Bench Press',
        'type': 'strength',
        'muscle_groups': ['chest', 'shoulders', 'triceps'],
        'difficulty': 'intermediate',
        'equipment': ['dumbbells', 'bench'],
        'instructions': 'Lie on bench with dumbbells at chest level. Press weights upward until arms are extended, then lower slowly.',
        'tips': ['Control the movement', 'Don\'t bounce weights', 'Keep proper form'],
        'variations': ['Incline press', 'Decline press', 'Close grip press'],
        'calories_per_minute': 8
    },
    {
        'name': 'Dumbbell Rows',
        'type': 'strength',
        'muscle_groups': ['back', 'biceps', 'core'],
        'difficulty': 'intermediate',
        'equipment': ['dumbbells', 'bench'],
        'instructions': 'Bend at waist with dumbbells in hands. Pull weights up toward chest, squeezing back muscles. Lower slowly.',
        'tips': ['Keep back straight', 'Squeeze shoulder blades', 'Control the weight'],
        'variations': ['Bent over rows', 'Single arm rows', 'Inverted rows'],
        'calories_per_minute': 7
    },
    {
        'name': 'Dumbbell Squats',
        'type': 'strength',
        'muscle_groups': ['quadriceps', 'glutes', 'hamstrings', 'calves'],
        'difficulty': 'intermediate',
        'equipment': ['dumbbells'],
        'instructions': 'Hold dumbbells at shoulders. Squat down keeping back straight, then return to standing.',
        'tips': ['Keep chest up', 'Go deep', 'Control movement'],
        'variations': ['Goblet squats', 'Front squats', 'Overhead squats'],
        'calories_per_minute': 8
    },
    {
        'name': 'Shoulder Press',
        'type': 'strength',
        'muscle_groups': ['shoulders', 'triceps', 'core'],
        'difficulty': 'intermediate',
        'equipment': ['dumbbells', 'barbell'],
        'instructions': 'Press weights overhead from shoulder height until arms are fully extended. Lower slowly to starting position.',
        'tips': ['Keep core tight', 'Don\'t arch back', 'Control the movement'],
        'variations': ['Seated press', 'Arnold press', 'Push press'],
        'calories_per_minute': 6
    },
    {
        'name': 'Bicep Curls',
        'type': 'strength',
        'muscle_groups': ['biceps', 'forearms'],
        'difficulty': 'beginner',
        'equipment': ['dumbbells', 'barbell', 'resistance bands'],
        'instructions': 'Hold weights with palms facing forward. Curl weights up toward shoulders, then lower slowly.',
        'tips': ['Keep elbows stationary', 'Squeeze at top', 'Control negative'],
        'variations': ['Hammer curls', 'Preacher curls', 'Concentration curls'],
        'calories_per_minute': 4
    },
    {
        'name': 'Tricep Dips',
        'type': 'strength',
        'muscle_groups': ['triceps', 'shoulders', 'chest'],
        'difficulty': 'intermediate',
        'equipment': ['dip bars', 'bench', 'parallel bars'],
        'instructions': 'Lower body between bars or bench, then push up until arms are straight. Control movement throughout.',
        'tips': ['Keep elbows close', 'Go full range', 'Don\'t swing'],
        'variations': ['Bench dips', 'Parallel bar dips', 'Assisted dips'],
        'calories_per_minute': 8
    },
    {
        'name': 'Pull-ups',
        'type': 'strength',
        'muscle_groups': ['back', 'biceps', 'shoulders'],
        'difficulty': 'advanced',
        'equipment': ['pull-up bar'],
        'instructions': 'Hang from bar with overhand grip. Pull body up until chin is over bar, then lower slowly.',
        'tips': ['Keep core tight', 'Full range of motion', 'Control negative'],
        'variations': ['Chin-ups', 'Wide grip', 'Close grip', 'Assisted pull-ups'],
        'calories_per_minute': 10
    },
    {
        'name': 'Deadlifts',
        'type': 'strength',
        'muscle_groups': ['back', 'legs', 'glutes', 'core'],
        'difficulty': 'advanced',
        'equipment': ['barbell', 'deadlift bar', 'weights'],
        'instructions': 'Stand with bar over mid-foot. Bend knees and hips to grasp bar. Lift by extending hips and knees, keeping back straight.',
        'tips': ['Keep back straight', 'Drive through heels', 'Control the weight'],
        'variations': ['Romanian deadlifts', 'Sumo deadlifts', 'Trap bar deadlifts'],
        'calories_per_minute': 10
    },
    {
        'name': 'Running',
        'type': 'cardio',
        'muscle_groups': ['legs', 'core', 'cardiovascular'],
        'difficulty': 'beginner',
        'equipment': ['treadmill', 'outdoor'],
        'instructions': 'Run at steady pace, maintaining proper form and breathing.',
        'tips': ['Land midfoot', 'Keep arms relaxed', 'Maintain steady breathing'],
        'variations': ['Sprinting', 'Jogging', 'Trail running', 'Treadmill running'],
        'calories_per_minute': 12
    },
    {
        'name': 'Cycling',
        'type': 'cardio',
        'muscle_groups': ['legs', 'core', 'cardiovascular'],
        'difficulty': 'beginner',
        'equipment': ['stationary bike', 'outdoor bike'],
        'instructions': 'Pedal at steady pace, maintaining proper form and resistance.',
        'tips': ['Adjust seat height', 'Maintain cadence', 'Stay hydrated'],
        'variations': ['Indoor cycling', 'Outdoor cycling', 'Spin classes', 'Hill cycling'],
        'calories_per_minute': 8
    },
    {
        'name': 'Jump Rope',
        'type': 'cardio',
        'muscle_groups': ['legs', 'core', 'cardiovascular'],
        'difficulty': 'intermediate',
        'equipment': ['jump rope'],
        'instructions': 'Swing rope over head and jump as it passes under feet. Maintain rhythm and proper form.',
        'tips': ['Stay on balls of feet', 'Keep elbows close', 'Maintain rhythm'],
        'variations': ['Double unders', 'Cross overs', 'High knees', 'Boxer skip'],
        'calories_per_minute': 15
    }
]

# Workout Templates for different goals and fitness levels
WORKOUT_TEMPLATES = {
    'beginner': {
        'weight_loss': {
            'name': 'Beginner Weight Loss Workout',
            'duration': 30,
            'exercises_per_session': 6,
            'rest_periods': 60,
            'intensity': 'low_to_moderate',
            'focus': 'cardio_and_full_body',
            'exercise_types': ['cardio', 'strength'],
            'equipment_needed': ['minimal', 'bodyweight'],
            'progression': 'gradual'
        },
        'muscle_gain': {
            'name': 'Beginner Muscle Building',
            'duration': 45,
            'exercises_per_session': 5,
            'rest_periods': 90,
            'intensity': 'moderate',
            'focus': 'strength_training',
            'exercise_types': ['strength'],
            'equipment_needed': ['basic_weights'],
            'progression': 'linear'
        },
        'endurance': {
            'name': 'Beginner Endurance Builder',
            'duration': 40,
            'exercises_per_session': 4,
            'rest_periods': 45,
            'intensity': 'low',
            'focus': 'cardio',
            'exercise_types': ['cardio'],
            'equipment_needed': ['minimal'],
            'progression': 'time_based'
        }
    },
    'intermediate': {
        'weight_loss': {
            'name': 'Intermediate Fat Burner',
            'duration': 45,
            'exercises_per_session': 8,
            'rest_periods': 45,
            'intensity': 'moderate_to_high',
            'focus': 'hiit_and_strength',
            'exercise_types': ['cardio', 'strength', 'hiit'],
            'equipment_needed': ['weights', 'cardio_equipment'],
            'progression': 'progressive'
        },
        'muscle_gain': {
            'name': 'Intermediate Hypertrophy',
            'duration': 60,
            'exercises_per_session': 6,
            'rest_periods': 120,
            'intensity': 'high',
            'focus': 'strength_training',
            'exercise_types': ['strength'],
            'equipment_needed': ['full_gym'],
            'progression': 'periodized'
        },
        'endurance': {
            'name': 'Intermediate Stamina Builder',
            'duration': 60,
            'exercises_per_session': 5,
            'rest_periods': 60,
            'intensity': 'moderate',
            'focus': 'cardio_and_circuit',
            'exercise_types': ['cardio', 'circuit'],
            'equipment_needed': ['cardio_equipment'],
            'progression': 'interval_based'
        }
    },
    'advanced': {
        'weight_loss': {
            'name': 'Advanced Metabolic Conditioning',
            'duration': 60,
            'exercises_per_session': 10,
            'rest_periods': 30,
            'intensity': 'very_high',
            'focus': 'hiit_and_complex',
            'exercise_types': ['hiit', 'strength', 'plyometric'],
            'equipment_needed': ['full_gym', 'advanced_equipment'],
            'progression': 'advanced_periodization'
        },
        'muscle_gain': {
            'name': 'Advanced Strength & Power',
            'duration': 75,
            'exercises_per_session': 7,
            'rest_periods': 180,
            'intensity': 'very_high',
            'focus': 'strength_and_power',
            'exercise_types': ['strength', 'power'],
            'equipment_needed': ['full_gym', 'advanced_weights'],
            'progression': 'advanced_periodization'
        },
        'endurance': {
            'name': 'Advanced Performance Training',
            'duration': 90,
            'exercises_per_session': 6,
            'rest_periods': 90,
            'intensity': 'high',
            'focus': 'performance_and_conditioning',
            'exercise_types': ['cardio', 'sport_specific'],
            'equipment_needed': ['sport_specific', 'advanced_cardio'],
            'progression': 'performance_based'
        }
    }
}

# Equipment categories
EQUIPMENT_CATEGORIES = {
    'minimal': ['bodyweight', 'mat'],
    'basic_weights': ['dumbbells', 'resistance_bands', 'kettlebells'],
    'full_gym': ['barbells', 'dumbbells', 'cable_machines', 'benches', 'racks'],
    'cardio_equipment': ['treadmill', 'bike', 'elliptical', 'rower'],
    'advanced_equipment': ['plyometric_boxes', 'battle_ropes', 'sleds'],
    'sport_specific': ['agility_ladders', 'cones', 'medicine_balls']
}

# Muscle group focus areas
MUSCLE_GROUPS = {
    'upper_body': ['chest', 'back', 'shoulders', 'arms'],
    'lower_body': ['quadriceps', 'hamstrings', 'glutes', 'calves'],
    'core': ['abs', 'obliques', 'lower_back'],
    'full_body': ['all_muscle_groups']
}

# Intensity levels
INTENSITY_LEVELS = {
    'low': {'heart_rate': '50-60%', 'rpe': '3-4', 'description': 'Easy conversation pace'},
    'moderate': {'heart_rate': '60-70%', 'rpe': '5-6', 'description': 'Can talk but not sing'},
    'high': {'heart_rate': '70-85%', 'rpe': '7-8', 'description': 'Can only speak a few words'},
    'very_high': {'heart_rate': '85-95%', 'rpe': '9-10', 'description': 'Maximum effort'}
}
