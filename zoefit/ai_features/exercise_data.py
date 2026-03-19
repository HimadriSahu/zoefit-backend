"""
Exercise Data Module - Exercise Database and Workout Templates

This module contains the exercise database and workout templates used by the AI
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
        'tips': ['Keep front knee behind toes', 'Keep torso upright', 'Control the movement'],
        'variations': ['Reverse lunges', 'Walking lunges', 'Jump lunges'],
        'calories_per_minute': 7
    },
    {
        'name': 'Burpees',
        'type': 'hiit',
        'muscle_groups': ['full_body', 'chest', 'legs', 'core'],
        'difficulty': 'intermediate',
        'equipment': [],
        'instructions': 'Start standing, drop to squat position, kick feet back to push-up position, perform a push-up, jump feet back to squat, then jump up with arms overhead.',
        'tips': ['Maintain good form', 'Land softly', 'Breathe consistently'],
        'variations': ['No-push-up burpees', 'Burpee with tuck jump', 'One-legged burpees'],
        'calories_per_minute': 12
    },
    {
        'name': 'Mountain Climbers',
        'type': 'hiit',
        'muscle_groups': ['core', 'shoulders', 'legs'],
        'difficulty': 'intermediate',
        'equipment': [],
        'instructions': 'Start in push-up position. Alternately bring knees toward chest as if running in place. Keep your core engaged and hips level.',
        'tips': ['Keep hips down', 'Drive knees forward', 'Maintain steady pace'],
        'variations': ['Cross-body mountain climbers', 'Slow mountain climbers', 'Mountain climber holds'],
        'calories_per_minute': 10
    },
    {
        'name': 'Jumping Jacks',
        'type': 'cardio',
        'muscle_groups': ['legs', 'full_body'],
        'difficulty': 'beginner',
        'equipment': [],
        'instructions': 'Jump while spreading legs shoulder-width apart and raising arms overhead. Return to starting position and repeat.',
        'tips': ['Land softly on balls of feet', 'Keep rhythm steady', 'Engage core'],
        'variations': ['Plyo jacks', 'Squat jacks', 'Half jacks'],
        'calories_per_minute': 8
    },
    {
        'name': 'High Knees',
        'type': 'cardio',
        'muscle_groups': ['legs', 'core', 'cardio'],
        'difficulty': 'beginner',
        'equipment': [],
        'instructions': 'Run in place, bringing knees up toward chest as high as possible. Pump arms to maintain rhythm and intensity.',
        'tips': ['Drive knees high', 'Land softly', 'Maintain quick pace'],
        'variations': ['High knee sprints', 'Backward high knees', 'High knee with arm circles'],
        'calories_per_minute': 10
    },
    
    # Intermediate Exercises
    {
        'name': 'Pull-ups',
        'type': 'strength',
        'muscle_groups': ['back', 'biceps', 'shoulders', 'core'],
        'difficulty': 'intermediate',
        'instructions': 'Hang from a pull-up bar with palms facing away. Pull your body up until chin is above the bar, then lower back to starting position.',
        'tips': ['Use full range of motion', 'Engage your back', 'Control the descent'],
        'variations': ['Chin-ups', 'Wide grip pull-ups', 'Neutral grip pull-ups'],
        'calories_per_minute': 9
    },
    {
        'name': 'Dips',
        'type': 'strength',
        'muscle_groups': ['triceps', 'chest', 'shoulders'],
        'difficulty': 'intermediate',
        'equipment': ['dip_bars', 'chair'],
        'instructions': 'Support your body on parallel bars or a chair edge. Lower your body by bending elbows, then push back up to starting position.',
        'tips': ['Keep chest up', 'Go to 90-degree angle', 'Control movement'],
        'variations': ['Bench dips', 'Ring dips', 'Weighted dips'],
        'calories_per_minute': 7
    },
    {
        'name': 'Pike Push-ups',
        'type': 'strength',
        'muscle_groups': ['shoulders', 'triceps', 'upper_chest'],
        'difficulty': 'intermediate',
        'equipment': [],
        'instructions': 'Start in push-up position but lift hips up to form an inverted V shape. Lower head toward floor, then push back up.',
        'tips': ['Keep elbows close to body', 'Focus on shoulder movement', 'Control pace'],
        'variations': ['Handstand push-ups', 'Decline push-ups', 'Pike push-up holds'],
        'calories_per_minute': 6
    },
    {
        'name': 'Bulgarian Split Squats',
        'type': 'strength',
        'muscle_groups': ['quadriceps', 'glutes', 'hamstrings'],
        'difficulty': 'intermediate',
        'equipment': ['bench', 'chair'],
        'instructions': 'Place one foot on a bench behind you. Lower into a lunge with front leg, then push back up. Complete all reps before switching legs.',
        'tips': ['Keep front knee behind toes', 'Go deep into the lunge', 'Maintain balance'],
        'variations': ['Bulgarian split squat jumps', 'Weighted Bulgarian squats', 'Pause Bulgarian squats'],
        'calories_per_minute': 8
    },
    
    # Advanced Exercises
    {
        'name': 'Handstand Push-ups',
        'type': 'strength',
        'muscle_groups': ['shoulders', 'triceps', 'upper_chest', 'core'],
        'difficulty': 'advanced',
        'equipment': ['wall'],
        'instructions': 'Perform a handstand against a wall. Lower your body by bending elbows, then push back up to starting position.',
        'tips': ['Control the movement', 'Keep core tight', 'Use wall for balance'],
        'variations': ['Free handstand push-ups', 'Partial handstand push-ups', 'Handstand push-up holds'],
        'calories_per_minute': 10
    },
    {
        'name': 'Muscle-ups',
        'type': 'strength',
        'muscle_groups': ['back', 'chest', 'shoulders', 'arms', 'core'],
        'difficulty': 'advanced',
        'equipment': ['pull_up_bar', 'rings'],
        'instructions': 'Hang from a bar or rings. Pull up, then transition to dip position and push up. Reverse the movement to return to start.',
        'tips': ['Practice transition separately', 'Build strength gradually', 'Maintain control'],
        'variations': ['Ring muscle-ups', 'Bar muscle-ups', 'Weighted muscle-ups'],
        'calories_per_minute': 12
    },
    {
        'name': 'Pistol Squats',
        'type': 'strength',
        'muscle_groups': ['quadriceps', 'glutes', 'hamstrings', 'core', 'balance'],
        'difficulty': 'advanced',
        'equipment': [],
        'instructions': 'Stand on one leg with other leg extended forward. Lower into a deep squat on standing leg, then return to starting position.',
        'tips': ['Keep non-working leg straight', 'Maintain balance', 'Go as low as possible'],
        'variations': ['Pistol squat holds', 'Weighted pistol squats', 'Pistol squat jumps'],
        'calories_per_minute': 9
    },
    
    # Cardio Exercises
    {
        'name': 'Jump Rope',
        'type': 'cardio',
        'muscle_groups': ['legs', 'calves', 'cardio', 'coordination'],
        'difficulty': 'beginner',
        'equipment': ['jump_rope'],
        'instructions': 'Jump over a rope while swinging it under your feet. Maintain rhythm and good posture throughout.',
        'tips': ['Stay on balls of feet', 'Keep elbows close to body', 'Start slow'],
        'variations': ['Double unders', 'Cross overs', 'High knees jump rope'],
        'calories_per_minute': 12
    },
    {
        'name': 'Box Jumps',
        'type': 'plyometric',
        'muscle_groups': ['legs', 'glutes', 'calves', 'explosive_power'],
        'difficulty': 'intermediate',
        'equipment': ['box', 'step'],
        'instructions': 'Stand in front of a box. Jump onto the box, landing softly with knees bent. Step back down and repeat.',
        'tips': ['Land softly', 'Use arms for momentum', 'Start with lower height'],
        'variations': ['Box jump burpees', 'Lateral box jumps', 'Depth jumps'],
        'calories_per_minute': 11
    },
    
    # Flexibility and Mobility
    {
        'name': 'Yoga Flow',
        'type': 'flexibility',
        'muscle_groups': ['full_body', 'flexibility', 'balance'],
        'difficulty': 'beginner',
        'equipment': ['yoga_mat'],
        'instructions': 'Perform a sequence of yoga poses flowing from one to the next with coordinated breathing.',
        'tips': ['Focus on breathing', 'Move mindfully', 'Listen to your body'],
        'variations': ['Sun salutation', 'Vinyasa flow', 'Restorative yoga'],
        'calories_per_minute': 3
    },
    {
        'name': 'Dynamic Stretching',
        'type': 'flexibility',
        'muscle_groups': ['full_body', 'mobility', 'injury_prevention'],
        'difficulty': 'beginner',
        'equipment': [],
        'instructions': 'Perform controlled movements that take your muscles through their full range of motion.',
        'tips': ['Don\'t bounce', 'Move smoothly', 'Focus on problem areas'],
        'variations': ['Leg swings', 'Arm circles', 'Torso twists'],
        'calories_per_minute': 2
    }
]

# Workout Templates for different goals and fitness levels
WORKOUT_TEMPLATES = [
    # Beginner Templates
    {
        'name': 'Beginner Full Body',
        'goal': 'general',
        'fitness_level': 'beginner',
        'type': 'strength',
        'exercises': ['push-ups', 'bodyweight squats', 'plank', 'jumping jacks'],
        'duration_minutes': 20,
        'frequency_per_week': 3
    },
    {
        'name': 'Beginner Cardio',
        'goal': 'weight_loss',
        'fitness_level': 'beginner',
        'type': 'cardio',
        'exercises': ['jumping jacks', 'high knees', 'mountain climbers', 'jump rope'],
        'duration_minutes': 15,
        'frequency_per_week': 4
    },
    {
        'name': 'Beginner Flexibility',
        'goal': 'maintenance',
        'fitness_level': 'beginner',
        'type': 'flexibility',
        'exercises': ['yoga flow', 'dynamic stretching', 'plank'],
        'duration_minutes': 15,
        'frequency_per_week': 3
    },
    
    # Intermediate Templates
    {
        'name': 'Intermediate Strength',
        'goal': 'muscle_gain',
        'fitness_level': 'intermediate',
        'type': 'strength',
        'exercises': ['push-ups', 'pull-ups', 'bodyweight squats', 'lunges', 'dips', 'plank'],
        'duration_minutes': 35,
        'frequency_per_week': 4
    },
    {
        'name': 'Intermediate HIIT',
        'goal': 'weight_loss',
        'fitness_level': 'intermediate',
        'type': 'hiit',
        'exercises': ['burpees', 'mountain climbers', 'high knees', 'box jumps', 'jumping jacks'],
        'duration_minutes': 25,
        'frequency_per_week': 3
    },
    {
        'name': 'Intermediate Mixed',
        'goal': 'endurance',
        'fitness_level': 'intermediate',
        'type': 'mixed',
        'exercises': ['push-ups', 'burpees', 'lunges', 'jump rope', 'plank', 'mountain climbers'],
        'duration_minutes': 30,
        'frequency_per_week': 4
    },
    
    # Advanced Templates
    {
        'name': 'Advanced Strength',
        'goal': 'strength',
        'fitness_level': 'advanced',
        'type': 'strength',
        'exercises': ['pull-ups', 'muscle-ups', 'pistol squats', 'handstand push-ups', 'dips', 'plank'],
        'duration_minutes': 45,
        'frequency_per_week': 5
    },
    {
        'name': 'Advanced HIIT',
        'goal': 'weight_loss',
        'fitness_level': 'advanced',
        'type': 'hiit',
        'exercises': ['burpees', 'muscle-ups', 'box jumps', 'mountain climbers', 'pistol squats'],
        'duration_minutes': 30,
        'frequency_per_week': 4
    },
    {
        'name': 'Advanced Athletic',
        'goal': 'endurance',
        'fitness_level': 'advanced',
        'type': 'mixed',
        'exercises': ['burpees', 'pull-ups', 'box jumps', 'handstand push-ups', 'jump rope', 'plank'],
        'duration_minutes': 40,
        'frequency_per_week': 5
    }
]

# Workout progression schemes
PROGRESSION_SCHEMES = {
    'beginner': {
        'volume_increase': 'add_reps',
        'intensity_increase': 'reduce_rest',
        'frequency': '3x_per_week',
        'deload_frequency': 'every_4th_week'
    },
    'intermediate': {
        'volume_increase': 'add_sets',
        'intensity_increase': 'add_difficulty',
        'frequency': '4x_per_week',
        'deload_frequency': 'every_6th_week'
    },
    'advanced': {
        'volume_increase': 'add_exercises',
        'intensity_increase': 'advanced_variations',
        'frequency': '5x_per_week',
        'deload_frequency': 'every_8th_week'
    }
}

# Rest period recommendations
REST_PERIODS = {
    'strength': {
        'beginner': 90,
        'intermediate': 75,
        'advanced': 60
    },
    'cardio': {
        'beginner': 45,
        'intermediate': 30,
        'advanced': 20
    },
    'hiit': {
        'beginner': 60,
        'intermediate': 45,
        'advanced': 30
    },
    'flexibility': {
        'beginner': 30,
        'intermediate': 20,
        'advanced': 15
    }
}

# Warm-up and cool-down routines
WARMUP_ROUTINES = {
    'strength': [
        {'exercise': 'Jumping jacks', 'duration': 60},
        {'exercise': 'High knees', 'duration': 45},
        {'exercise': 'Arm circles', 'duration': 30},
        {'exercise': 'Leg swings', 'duration': 30},
        {'exercise': 'Dynamic stretching', 'duration': 60}
    ],
    'cardio': [
        {'exercise': 'Light jogging', 'duration': 180},
        {'exercise': 'Dynamic stretching', 'duration': 120},
        {'exercise': 'Movement preparation', 'duration': 60}
    ],
    'flexibility': [
        {'exercise': 'Gentle movement', 'duration': 120},
        {'exercise': 'Joint rotations', 'duration': 60},
        {'exercise': 'Light stretching', 'duration': 180}
    ]
}

COOLDOWN_ROUTINES = {
    'strength': [
        {'exercise': 'Light walking', 'duration': 120},
        {'exercise': 'Static stretching', 'duration': 300},
        {'exercise': 'Foam rolling', 'duration': 180}
    ],
    'cardio': [
        {'exercise': 'Slow walking', 'duration': 300},
        {'exercise': 'Static stretching', 'duration': 240},
        {'exercise': 'Deep breathing', 'duration': 60}
    ],
    'flexibility': [
        {'exercise': 'Meditation', 'duration': 300},
        {'exercise': 'Gentle stretching', 'duration': 240},
        {'exercise': 'Relaxation breathing', 'duration': 120}
    ]
}

# Exercise modifications for injuries or limitations
EXERCISE_MODIFICATIONS = {
    'knee_pain': {
        'avoid': ['jumping jacks', 'burpees', 'box jumps', 'high knees'],
        'substitute': {
            'jumping jacks': 'arm circles',
            'burpees': 'modified burpees (no jump)',
            'box jumps': 'step-ups',
            'high knees': 'marching in place'
        }
    },
    'shoulder_pain': {
        'avoid': ['push-ups', 'pull-ups', 'handstand push-ups', 'dips'],
        'substitute': {
            'push-ups': 'chest presses with bands',
            'pull-ups': 'lat pulldowns with bands',
            'handstand push-ups': 'pike push-ups',
            'dips': 'bench dips'
        }
    },
    'back_pain': {
        'avoid': ['burpees', 'mountain climbers', 'jumping jacks'],
        'substitute': {
            'burpees': 'squat to overhead reach',
            'mountain climbers': 'standing knee raises',
            'jumping jacks': 'step jacks'
        }
    },
    'wrist_pain': {
        'avoid': ['push-ups', 'plank', 'handstand push-ups'],
        'substitute': {
            'push-ups': 'knuckle push-ups or push-up bars',
            'plank': 'forearm plank',
            'handstand push-ups': 'pike push-ups on forearms'
        }
    }
}

# Calorie burn estimates per exercise
CALORIE_BURN_ESTIMATES = {
    'beginner': {
        'per_minute': 5,
        'adjustment_factor': 1.0
    },
    'intermediate': {
        'per_minute': 8,
        'adjustment_factor': 1.2
    },
    'advanced': {
        'per_minute': 12,
        'adjustment_factor': 1.5
    }
}

# Muscle group focus distribution
MUSCLE_GROUP_DISTRIBUTION = {
    'weight_loss': {
        'legs': 0.4,
        'upper_body': 0.3,
        'core': 0.2,
        'cardio': 0.1
    },
    'muscle_gain': {
        'legs': 0.3,
        'upper_body': 0.4,
        'core': 0.2,
        'cardio': 0.1
    },
    'endurance': {
        'legs': 0.3,
        'upper_body': 0.2,
        'core': 0.2,
        'cardio': 0.3
    },
    'strength': {
        'legs': 0.3,
        'upper_body': 0.4,
        'core': 0.3,
        'cardio': 0.0
    }
}
