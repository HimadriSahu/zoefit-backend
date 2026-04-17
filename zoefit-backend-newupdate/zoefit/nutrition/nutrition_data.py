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
        'snack_suitable': True
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
        'snack_suitable': True
    },
    {
        'name': 'Oats',
        'type': 'carb',
        'calories_per_100g': 389,
        'protein_per_100g': 16.9,
        'carbs_per_100g': 66,
        'fat_per_100g': 6.9,
        'allergens': ['gluten'],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Whole Wheat Pasta',
        'type': 'carb',
        'calories_per_100g': 131,
        'protein_per_100g': 5.5,
        'carbs_per_100g': 25,
        'fat_per_100g': 1.4,
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
        'snack_suitable': True
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
        'name': 'Carrots',
        'type': 'vegetable',
        'calories_per_100g': 41,
        'protein_per_100g': 0.9,
        'carbs_per_100g': 10,
        'fat_per_100g': 0.2,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    },
    {
        'name': 'Avocado',
        'type': 'vegetable',
        'calories_per_100g': 160,
        'protein_per_100g': 2,
        'carbs_per_100g': 9,
        'fat_per_100g': 15,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
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
        'calories_per_100g': 32,
        'protein_per_100g': 0.7,
        'carbs_per_100g': 7.6,
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
        'name': 'Almonds',
        'type': 'healthy_fat',
        'calories_per_100g': 579,
        'protein_per_100g': 21,
        'carbs_per_100g': 22,
        'fat_per_100g': 50,
        'allergens': ['tree_nuts'],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    },
    {
        'name': 'Olive Oil',
        'type': 'healthy_fat',
        'calories_per_100g': 884,
        'protein_per_100g': 0,
        'carbs_per_100g': 0,
        'fat_per_100g': 100,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': False
    },
    {
        'name': 'Chia Seeds',
        'type': 'healthy_fat',
        'calories_per_100g': 486,
        'protein_per_100g': 17,
        'carbs_per_100g': 42,
        'fat_per_100g': 31,
        'allergens': [],
        'vegetarian': True,
        'vegan': True,
        'snack_suitable': True
    }
]
 
# Meal Templates for different dietary preferences and goals
MEAL_TEMPLATES = {
    'weight_loss': {
        'breakfast': {
            'calories_target': 400,
            'protein_ratio': 0.3,
            'carbs_ratio': 0.4,
            'fat_ratio': 0.3,
            'meal_components': ['protein_source', 'complex_carb', 'vegetables', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Protein Oatmeal Bowl',
                    'ingredients': ['oats', 'protein_powder', 'berries', 'almonds'],
                    'prep_time': 10,
                    'difficulty': 'easy'
                },
                {
                    'name': 'Veggie Scramble with Toast',
                    'ingredients': ['eggs', 'spinach', 'bell_peppers', 'whole_grain_toast'],
                    'prep_time': 15,
                    'difficulty': 'easy'
                }
            ]
        },
        'lunch': {
            'calories_target': 500,
            'protein_ratio': 0.35,
            'carbs_ratio': 0.35,
            'fat_ratio': 0.3,
            'meal_components': ['lean_protein', 'complex_carb', 'vegetables', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Grilled Chicken Salad',
                    'ingredients': ['chicken_breast', 'mixed_greens', 'quinoa', 'olive_oil'],
                    'prep_time': 20,
                    'difficulty': 'easy'
                },
                {
                    'name': 'Tofu Stir-fry with Brown Rice',
                    'ingredients': ['tofu', 'mixed_vegetables', 'brown_rice', 'soy_sauce'],
                    'prep_time': 25,
                    'difficulty': 'medium'
                }
            ]
        },
        'dinner': {
            'calories_target': 600,
            'protein_ratio': 0.4,
            'carbs_ratio': 0.3,
            'fat_ratio': 0.3,
            'meal_components': ['lean_protein', 'vegetables', 'complex_carb', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Baked Salmon with Roasted Vegetables',
                    'ingredients': ['salmon', 'broccoli', 'sweet_potato', 'olive_oil'],
                    'prep_time': 35,
                    'difficulty': 'medium'
                },
                {
                    'name': 'Lentil Curry with Brown Rice',
                    'ingredients': ['lentils', 'spices', 'brown_rice', 'coconut_milk'],
                    'prep_time': 40,
                    'difficulty': 'medium'
                }
            ]
        },
        'snacks': {
            'calories_target': 200,
            'protein_ratio': 0.25,
            'carbs_ratio': 0.5,
            'fat_ratio': 0.25,
            'meal_components': ['protein_source', 'complex_carb', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Greek Yogurt with Berries',
                    'ingredients': ['greek_yogurt', 'mixed_berries', 'chia_seeds'],
                    'prep_time': 5,
                    'difficulty': 'easy'
                },
                {
                    'name': 'Apple with Almond Butter',
                    'ingredients': ['apple', 'almond_butter'],
                    'prep_time': 5,
                    'difficulty': 'easy'
                }
            ]
        }
    },
    'muscle_gain': {
        'breakfast': {
            'calories_target': 600,
            'protein_ratio': 0.35,
            'carbs_ratio': 0.4,
            'fat_ratio': 0.25,
            'meal_components': ['protein_source', 'complex_carb', 'vegetables', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Protein Pancakes with Eggs',
                    'ingredients': ['protein_powder', 'oats', 'eggs', 'banana'],
                    'prep_time': 20,
                    'difficulty': 'medium'
                },
                {
                    'name': 'Breakfast Burrito',
                    'ingredients': ['eggs', 'lean_meat', 'beans', 'tortilla', 'cheese'],
                    'prep_time': 25,
                    'difficulty': 'medium'
                }
            ]
        },
        'lunch': {
            'calories_target': 700,
            'protein_ratio': 0.4,
            'carbs_ratio': 0.35,
            'fat_ratio': 0.25,
            'meal_components': ['lean_protein', 'complex_carb', 'vegetables', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Chicken and Rice Bowl',
                    'ingredients': ['chicken_breast', 'brown_rice', 'vegetables', 'avocado'],
                    'prep_time': 30,
                    'difficulty': 'medium'
                },
                {
                    'name': 'Beef and Sweet Potato',
                    'ingredients': ['lean_beef', 'sweet_potato', 'green_beans', 'olive_oil'],
                    'prep_time': 35,
                    'difficulty': 'medium'
                }
            ]
        },
        'dinner': {
            'calories_target': 800,
            'protein_ratio': 0.4,
            'carbs_ratio': 0.35,
            'fat_ratio': 0.25,
            'meal_components': ['protein_source', 'complex_carb', 'vegetables', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Steak with Quinoa and Vegetables',
                    'ingredients': ['lean_steak', 'quinoa', 'roasted_vegetables', 'butter'],
                    'prep_time': 45,
                    'difficulty': 'medium'
                },
                {
                    'name': 'Salmon and Pasta',
                    'ingredients': ['salmon', 'whole_wheat_pasta', 'broccoli', 'cream_sauce'],
                    'prep_time': 40,
                    'difficulty': 'medium'
                }
            ]
        },
        'snacks': {
            'calories_target': 300,
            'protein_ratio': 0.3,
            'carbs_ratio': 0.4,
            'fat_ratio': 0.3,
            'meal_components': ['protein_source', 'complex_carb', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Protein Smoothie',
                    'ingredients': ['protein_powder', 'banana', 'oats', 'almond_butter'],
                    'prep_time': 10,
                    'difficulty': 'easy'
                },
                {
                    'name': 'Cottage Cheese with Fruit',
                    'ingredients': ['cottage_cheese', 'peaches', 'almonds'],
                    'prep_time': 5,
                    'difficulty': 'easy'
                }
            ]
        }
    },
    'maintenance': {
        'breakfast': {
            'calories_target': 500,
            'protein_ratio': 0.25,
            'carbs_ratio': 0.45,
            'fat_ratio': 0.3,
            'meal_components': ['protein_source', 'complex_carb', 'vegetables', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Overnight Oats with Fruits',
                    'ingredients': ['oats', 'greek_yogurt', 'berries', 'honey'],
                    'prep_time': 5,
                    'difficulty': 'easy'
                },
                {
                    'name': 'Avocado Toast with Egg',
                    'ingredients': ['whole_grain_bread', 'avocado', 'egg', 'spinach'],
                    'prep_time': 15,
                    'difficulty': 'easy'
                }
            ]
        },
        'lunch': {
            'calories_target': 600,
            'protein_ratio': 0.3,
            'carbs_ratio': 0.4,
            'fat_ratio': 0.3,
            'meal_components': ['lean_protein', 'complex_carb', 'vegetables', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Mediterranean Bowl',
                    'ingredients': ['chickpeas', 'quinoa', 'vegetables', 'feta', 'olive_oil'],
                    'prep_time': 25,
                    'difficulty': 'easy'
                },
                {
                    'name': 'Turkey Wrap',
                    'ingredients': ['turkey_breast', 'whole_grain_tortilla', 'vegetables', 'hummus'],
                    'prep_time': 20,
                    'difficulty': 'easy'
                }
            ]
        },
        'dinner': {
            'calories_target': 700,
            'protein_ratio': 0.3,
            'carbs_ratio': 0.4,
            'fat_ratio': 0.3,
            'meal_components': ['lean_protein', 'vegetables', 'complex_carb', 'healthy_fat'],
            'example_meals': [
                {
                    'name': 'Vegetable Stir-fry with Tofu',
                    'ingredients': ['tofu', 'mixed_vegetables', 'brown_rice', 'soy_sauce'],
                    'prep_time': 30,
                    'difficulty': 'medium'
                },
                {
                    'name': 'Chicken and Vegetable Pasta',
                    'ingredients': ['chicken_breast', 'whole_wheat_pasta', 'vegetables', 'olive_oil'],
                    'prep_time': 35,
                    'difficulty': 'medium'
                }
            ]
        },
        'snacks': {
            'calories_target': 250,
            'protein_ratio': 0.2,
            'carbs_ratio': 0.5,
            'fat_ratio': 0.3,
            'meal_components': ['complex_carb', 'healthy_fat', 'protein_source'],
            'example_meals': [
                {
                    'name': 'Trail Mix',
                    'ingredients': ['nuts', 'seeds', 'dried_fruits', 'dark_chocolate'],
                    'prep_time': 5,
                    'difficulty': 'easy'
                },
                {
                    'name': 'Rice Cakes with Nut Butter',
                    'ingredients': ['brown_rice_cakes', 'nut_butter', 'banana'],
                    'prep_time': 5,
                    'difficulty': 'easy'
                }
            ]
        }
    }
}
 
# Dietary restrictions and preferences
DIETARY_RESTRICTIONS = {
    'vegetarian': {
        'exclude_proteins': ['meat', 'poultry', 'fish', 'seafood'],
        'include_proteins': ['eggs', 'dairy', 'legumes', 'tofu', 'tempeh', 'seitan'],
        'notes': 'Include plant-based proteins and dairy/eggs if not vegan'
    },
    'vegan': {
        'exclude_proteins': ['meat', 'poultry', 'fish', 'seafood', 'dairy', 'eggs', 'honey'],
        'include_proteins': ['legumes', 'tofu', 'tempeh', 'seitan', 'nuts', 'seeds'],
        'notes': 'Only plant-based foods, no animal products'
    },
    'gluten_free': {
        'exclude_carbs': ['wheat', 'barley', 'rye', 'oats'],
        'include_carbs': ['rice', 'quinoa', 'potatoes', 'corn', 'buckwheat'],
        'notes': 'Avoid all gluten-containing grains and products'
    },
    'dairy_free': {
        'exclude_proteins': ['milk', 'cheese', 'yogurt', 'butter', 'cream'],
        'include_proteins': ['plant_based_milks', 'dairy_alternatives', 'fortified_foods'],
        'notes': 'Use dairy alternatives for calcium and protein'
    },
    'nut_free': {
        'exclude_allergens': ['peanuts', 'tree_nuts', 'shellfish', 'fish', 'eggs', 'milk', 'wheat', 'soy'],
        'safe_alternatives': {
            'peanuts': ['sunflower_seeds', 'pumpkin_seeds'],
            'tree_nuts': ['seeds', 'legumes'],
            'dairy': ['plant_milks', 'fortified_foods'],
            'wheat': ['gluten_free_grains', 'rice', 'corn']
        },
        'notes': 'Avoid all major food allergens'
    }
}
 
# Meal timing and frequency recommendations
MEAL_TIMING = {
    'early_bird': {
        'breakfast_time': '06:00-07:00',
        'lunch_time': '12:00-13:00',
        'dinner_time': '18:00-19:00',
        'snack_times': ['10:00', '15:00'],
        'notes': 'Earlier meal times for those who wake up early'
    },
    'standard': {
        'breakfast_time': '07:00-08:00',
        'lunch_time': '12:00-13:00',
        'dinner_time': '19:00-20:00',
        'snack_times': ['10:30', '15:30'],
        'notes': 'Standard meal timing for most people'
    },
    'night_owl': {
        'breakfast_time': '08:00-09:00',
        'lunch_time': '13:00-14:00',
        'dinner_time': '20:00-21:00',
        'snack_times': ['11:00', '16:00'],
        'notes': 'Later meal times for those who stay up late'
    }
}
 
# Cooking methods and their impact
COOKING_METHODS = {
    'grilling': {
        'health_impact': 'low',
        'fat_reduction': 'high',
        'flavor_enhancement': 'high',
        'cooking_time': 'medium',
        'suitable_for': ['meats', 'vegetables', 'fruits']
    },
    'steaming': {
        'health_impact': 'very_low',
        'fat_reduction': 'none',
        'flavor_enhancement': 'medium',
        'cooking_time': 'medium',
        'suitable_for': ['vegetables', 'fish', 'dumplings']
    },
    'baking': {
        'health_impact': 'medium',
        'fat_reduction': 'low',
        'flavor_enhancement': 'high',
        'cooking_time': 'high',
        'suitable_for': ['meats', 'vegetables', 'grains']
    },
    'stir_frying': {
        'health_impact': 'medium',
        'fat_reduction': 'low',
        'flavor_enhancement': 'high',
        'cooking_time': 'low',
        'suitable_for': ['vegetables', 'tofu', 'thin_meats']
    },
    'raw': {
        'health_impact': 'minimal',
        'fat_reduction': 'none',
        'flavor_enhancement': 'natural',
        'cooking_time': 'minimal',
        'suitable_for': ['vegetables', 'fruits', 'nuts', 'seeds']
    }
}
 