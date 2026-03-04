"""
Nutrition Data Module - Food Database and Meal Templates

This module contains the food database and meal templates used by the AI
recommendation engine for generating personalized meal plans.
"""

# Food Database with nutritional information
FOOD_DATABASE = [
    # Proteins
    {
        'name': 'Chicken Breast',
        'type': 'protein',
        'calories_per_100g': 165,
        'protein_per_100g': 31,
        'carbs_per_100g': 0,
        'fat_per_100g': 3.6,
        'allergens': [],
        'vegetarian': False,
        'vegan': False,
        'snack_suitable': False
    },
    {
        'name': 'Salmon',
        'type': 'protein',
        'calories_per_100g': 208,
        'protein_per_100g': 20,
        'carbs_per_100g': 0,
        'fat_per_100g': 13,
        'allergens': ['fish'],
        'vegetarian': False,
        'vegan': False,
        'snack_suitable': False
    },
    {
        'name': 'Eggs',
        'type': 'protein',
        'calories_per_100g': 155,
        'protein_per_100g': 13,
        'carbs_per_100g': 1.1,
        'fat_per_100g': 11,
        'allergens': ['eggs'],
        'vegetarian': True,
        'vegan': False,
        'snack_suitable': True
    },
    {
        'name': 'Greek Yogurt',
        'type': 'protein',
        'calories_per_100g': 59,
        'protein_per_100g': 10,
        'carbs_per_100g': 3.6,
        'fat_per_100g': 0.4,
        'allergens': ['dairy'],
        'vegetarian': True,
        'vegan': False,
        'snack_suitable': True
    },
    {
        'name': 'Tofu',
        'type': 'protein',
        'calories_per_100g': 76,
        'protein_per_100g': 8,
        'carbs_per_100g': 1.9,
        'fat_per_100g': 4.8,
        'allergens': ['soy'],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Lentils',
        'type': 'protein',
        'calories_per_100g': 116,
        'protein_per_100g': 9,
        'carbs_per_100g': 20,
        'fat_per_100g': 0.4,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    
    # Carbohydrates
    {
        'name': 'Brown Rice',
        'type': 'carb',
        'calories_per_100g': 111,
        'protein_per_100g': 2.6,
        'carbs_per_100g': 23,
        'fat_per_100g': 0.9,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Quinoa',
        'type': 'carb',
        'calories_per_100g': 120,
        'protein_per_100g': 4.4,
        'carbs_per_100g': 21,
        'fat_per_100g': 1.9,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Sweet Potato',
        'type': 'carb',
        'calories_per_100g': 86,
        'protein_per_100g': 1.6,
        'carbs_per_100g': 20,
        'fat_per_100g': 0.1,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Oats',
        'type': 'carb',
        'calories_per_100g': 389,
        'protein_per_100g': 17,
        'carbs_per_100g': 66,
        'fat_per_100g': 7,
        'allergens': ['gluten'],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Whole Wheat Bread',
        'type': 'carb',
        'calories_per_100g': 247,
        'protein_per_100g': 13,
        'carbs_per_100g': 41,
        'fat_per_100g': 3.4,
        'allergens': ['gluten'],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    
    # Vegetables
    {
        'name': 'Broccoli',
        'type': 'vegetable',
        'calories_per_100g': 34,
        'protein_per_100g': 2.8,
        'carbs_per_100g': 7,
        'fat_per_100g': 0.4,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    },
    {
        'name': 'Spinach',
        'type': 'vegetable',
        'calories_per_100g': 23,
        'protein_per_100g': 2.9,
        'carbs_per_100g': 3.6,
        'fat_per_100g': 0.4,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Bell Peppers',
        'type': 'vegetable',
        'calories_per_100g': 31,
        'protein_per_100g': 1,
        'carbs_per_100g': 7,
        'fat_per_100g': 0.3,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    },
    {
        'name': 'Tomatoes',
        'type': 'vegetable',
        'calories_per_100g': 18,
        'protein_per_100g': 0.9,
        'carbs_per_100g': 3.9,
        'fat_per_100g': 0.2,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    
    # Fruits
    {
        'name': 'Apple',
        'type': 'fruit',
        'calories_per_100g': 52,
        'protein_per_100g': 0.3,
        'carbs_per_100g': 14,
        'fat_per_100g': 0.2,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    },
    {
        'name': 'Banana',
        'type': 'fruit',
        'calories_per_100g': 89,
        'protein_per_100g': 1.1,
        'carbs_per_100g': 23,
        'fat_per_100g': 0.3,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    },
    {
        'name': 'Berries',
        'type': 'fruit',
        'calories_per_100g': 57,
        'protein_per_100g': 0.7,
        'carbs_per_100g': 14,
        'fat_per_100g': 0.3,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    },
    {
        'name': 'Orange',
        'type': 'fruit',
        'calories_per_100g': 47,
        'protein_per_100g': 0.9,
        'carbs_per_100g': 12,
        'fat_per_100g': 0.1,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    },
    
    # Healthy Fats
    {
        'name': 'Avocado',
        'type': 'fat',
        'calories_per_100g': 160,
        'protein_per_100g': 2,
        'carbs_per_100g': 9,
        'fat_per_100g': 15,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Almonds',
        'type': 'fat',
        'calories_per_100g': 579,
        'protein_per_100g': 21,
        'carbs_per_100g': 22,
        'fat_per_100g': 50,
        'allergens': ['nuts'],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    },
    {
        'name': 'Olive Oil',
        'type': 'fat',
        'calories_per_100g': 884,
        'protein_per_100g': 0,
        'carbs_per_100g': 0,
        'fat_per_100g': 100,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    
    # Dairy Alternatives
    {
        'name': 'Almond Milk',
        'type': 'beverage',
        'calories_per_100g': 15,
        'protein_per_100g': 0.6,
        'carbs_per_100g': 0.3,
        'fat_per_100g': 1.2,
        'allergens': ['nuts'],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Soy Milk',
        'type': 'beverage',
        'calories_per_100g': 54,
        'protein_per_100g': 3.3,
        'carbs_per_100g': 3.4,
        'fat_per_100g': 1.8,
        'allergens': ['soy'],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    }
]

# Meal Templates for different dietary preferences and calorie ranges
MEAL_TEMPLATES = [
    # Low Calorie Templates (1200-1500 calories)
    {
        'name': 'Low Calorie Weight Loss',
        'dietary_type': 'omnivore',
        'calorie_range': 'low',
        'high_glycemic': False,
        'high_sodium': False,
        'high_saturated_fat': False,
        'meals': {
            'breakfast': {
                'main': ['protein', 'carb', 'fruit']
            },
            'lunch': {
                'main': ['protein', 'vegetable'],
                'side': ['vegetable']
            },
            'dinner': {
                'main': ['protein', 'vegetable'],
                'side': ['vegetable']
            }
        }
    },
    {
        'name': 'Low Calorie Vegetarian',
        'dietary_type': 'vegetarian',
        'calorie_range': 'low',
        'high_glycemic': False,
        'high_sodium': False,
        'high_saturated_fat': False,
        'meals': {
            'breakfast': {
                'main': ['protein', 'carb', 'fruit']
            },
            'lunch': {
                'main': ['protein', 'vegetable'],
                'side': ['carb']
            },
            'dinner': {
                'main': ['protein', 'vegetable'],
                'side': ['carb']
            }
        }
    },
    
    # Medium Calorie Templates (1500-2000 calories)
    {
        'name': 'Balanced Maintenance',
        'dietary_type': 'omnivore',
        'calorie_range': 'medium',
        'high_glycemic': False,
        'high_sodium': False,
        'high_saturated_fat': False,
        'meals': {
            'breakfast': {
                'main': ['protein', 'carb', 'fruit'],
                'side': ['fat']
            },
            'lunch': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['fat']
            },
            'dinner': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['fat']
            }
        }
    },
    {
        'name': 'Balanced Vegetarian',
        'dietary_type': 'vegetarian',
        'calorie_range': 'medium',
        'high_glycemic': False,
        'high_sodium': False,
        'high_saturated_fat': False,
        'meals': {
            'breakfast': {
                'main': ['protein', 'carb', 'fruit'],
                'side': ['fat']
            },
            'lunch': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['fat']
            },
            'dinner': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['fat']
            }
        }
    },
    
    # High Calorie Templates (2000-2500 calories)
    {
        'name': 'High Protein Muscle Gain',
        'dietary_type': 'omnivore',
        'calorie_range': 'high',
        'high_glycemic': False,
        'high_sodium': False,
        'high_saturated_fat': False,
        'meals': {
            'breakfast': {
                'main': ['protein', 'carb', 'fruit'],
                'side': ['protein', 'fat']
            },
            'lunch': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['protein', 'fat']
            },
            'dinner': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['protein', 'fat']
            }
        }
    },
    {
        'name': 'High Calorie Vegetarian',
        'dietary_type': 'vegetarian',
        'calorie_range': 'high',
        'high_glycemic': False,
        'high_sodium': False,
        'high_saturated_fat': False,
        'meals': {
            'breakfast': {
                'main': ['protein', 'carb', 'fruit'],
                'side': ['protein', 'fat']
            },
            'lunch': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['protein', 'fat']
            },
            'dinner': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['protein', 'fat']
            }
        }
    },
    
    # Very High Calorie Templates (2500+ calories)
    {
        'name': 'Bulking High Calorie',
        'dietary_type': 'omnivore',
        'calorie_range': 'very_high',
        'high_glycemic': False,
        'high_sodium': False,
        'high_saturated_fat': False,
        'meals': {
            'breakfast': {
                'main': ['protein', 'carb', 'fruit'],
                'side': ['protein', 'carb', 'fat']
            },
            'lunch': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['protein', 'carb', 'fat']
            },
            'dinner': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['protein', 'carb', 'fat']
            }
        }
    },
    {
        'name': 'Vegan High Calorie',
        'dietary_type': 'vegan',
        'calorie_range': 'very_high',
        'high_glycemic': False,
        'high_sodium': False,
        'high_saturated_fat': False,
        'meals': {
            'breakfast': {
                'main': ['protein', 'carb', 'fruit'],
                'side': ['protein', 'carb', 'fat']
            },
            'lunch': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['protein', 'carb', 'fat']
            },
            'dinner': {
                'main': ['protein', 'carb', 'vegetable'],
                'side': ['protein', 'carb', 'fat']
            }
        }
    }
]

# Nutritional guidelines for different goals
NUTRITIONAL_GUIDELINES = {
    'weight_loss': {
        'protein_percentage': 0.40,
        'carb_percentage': 0.30,
        'fat_percentage': 0.30,
        'calorie_adjustment': -500
    },
    'muscle_gain': {
        'protein_percentage': 0.35,
        'carb_percentage': 0.45,
        'fat_percentage': 0.20,
        'calorie_adjustment': 300
    },
    'maintenance': {
        'protein_percentage': 0.30,
        'carb_percentage': 0.40,
        'fat_percentage': 0.30,
        'calorie_adjustment': 0
    },
    'endurance': {
        'protein_percentage': 0.25,
        'carb_percentage': 0.55,
        'fat_percentage': 0.20,
        'calorie_adjustment': 0
    },
    'strength': {
        'protein_percentage': 0.35,
        'carb_percentage': 0.40,
        'fat_percentage': 0.25,
        'calorie_adjustment': 200
    }
}

# Meal timing recommendations
MEAL_TIMING = {
    'breakfast': {
        'time_range': '06:00-09:00',
        'importance': 'high',
        'recommended_calories': 0.25
    },
    'lunch': {
        'time_range': '11:30-14:00',
        'importance': 'high',
        'recommended_calories': 0.35
    },
    'dinner': {
        'time_range': '17:30-20:30',
        'importance': 'medium',
        'recommended_calories': 0.30
    },
    'snacks': {
        'time_range': '09:30-11:00, 14:30-17:00',
        'importance': 'low',
        'recommended_calories': 0.10
    }
}

# Hydration recommendations
HYDRATION_GUIDELINES = {
    'base_water_ml': 2000,  # Base 2 liters
    'per_kg_ml': 35,  # Additional 35ml per kg body weight
    'exercise_extra_ml': 500,  # Extra 500ml per hour of exercise
    'climate_factor': 1.2  # 20% more in hot climates
}

# Supplement recommendations
SUPPLEMENT_RECOMMENDATIONS = {
    'weight_loss': [
        {'name': 'Multivitamin', 'reason': 'Nutrient gap filling'},
        {'name': 'Omega-3', 'reason': 'Anti-inflammatory benefits'},
        {'name': 'Vitamin D', 'reason': 'Bone health support'}
    ],
    'muscle_gain': [
        {'name': 'Whey Protein', 'reason': 'Muscle recovery'},
        {'name': 'Creatine', 'reason': 'Performance enhancement'},
        {'name': 'Multivitamin', 'reason': 'Nutrient gap filling'}
    ],
    'maintenance': [
        {'name': 'Multivitamin', 'reason': 'General health'},
        {'name': 'Omega-3', 'reason': 'Heart health'},
        {'name': 'Vitamin D', 'reason': 'Immune support'}
    ],
    'endurance': [
        {'name': 'Electrolytes', 'reason': 'Hydration support'},
        {'name': 'B-Vitamins', 'reason': 'Energy metabolism'},
        {'name': 'Iron', 'reason': 'Oxygen transport'}
    ],
    'strength': [
        {'name': 'Whey Protein', 'reason': 'Muscle building'},
        {'name': 'Creatine', 'reason': 'Strength gains'},
        {'name': 'Zinc', 'reason': 'Testosterone support'}
    ]
}
