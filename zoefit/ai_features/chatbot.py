"""
Enhanced AI Chatbot with OpenAI GPT and Google Gemini Integration

This module provides an intelligent chatbot that uses advanced AI models
(GPT-4 or Gemini) for natural, contextual conversations while maintaining
fallback to rule-based responses for reliability.

The chatbot is designed specifically for fitness advice and can:
- Provide personalized workout recommendations
- Answer nutrition questions
- Offer motivation and support
- Track user progress
- Handle general fitness queries

Features:
- Integration with OpenAI GPT-4 or Google Gemini
- Context-aware responses using user health metrics
- Fallback to rule-based responses for reliability
- Rate limiting and cost optimization
- Safety filters for medical advice
"""

import os
import json
import re
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Suppress Google AI deprecation warnings
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=FutureWarning, module="google.genai")

# Try to import AI libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import google.genai as genai
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False
        genai = None

from django.conf import settings
from .models import HealthMetrics

# Fitness Knowledge Base - Integrated from fitness_knowledge_base.py
EXERCISE_DATABASE = {
    "push_up": {
        "name": "Push-up",
        "category": "upper_body",
        "muscle_groups": ["chest", "shoulders", "triceps"],
        "difficulty": "beginner",
        "equipment": "none",
        "instructions": [
            "Start in plank position with hands slightly wider than shoulders",
            "Lower body until chest nearly touches the floor",
            "Push back up to starting position",
            "Keep core engaged and back straight throughout"
        ],
        "variations": ["knee_push_up", "incline_push_up", "decline_push_up"],
        "common_mistakes": ["sagging hips", "flaring elbows", "incomplete range of motion"],
        "benefits": ["builds upper body strength", "improves core stability", "no equipment needed"]
    },
    "squat": {
        "name": "Squat",
        "category": "lower_body",
        "muscle_groups": ["quadriceps", "glutes", "hamstrings", "core"],
        "difficulty": "beginner",
        "equipment": "none",
        "instructions": [
            "Stand with feet shoulder-width apart",
            "Lower hips back and down as if sitting in a chair",
            "Keep chest up and knees behind toes",
            "Lower until thighs are parallel to ground or lower",
            "Push through heels to return to standing"
        ],
        "variations": ["bodyweight_squat", "goblet_squat", "jump_squat", "pistol_squat"],
        "common_mistakes": ["knees caving inward", "heels lifting off ground", "rounding back"],
        "benefits": ["builds leg strength", "improves functional movement", "increases flexibility"]
    },
    "plank": {
        "name": "Plank",
        "category": "core",
        "muscle_groups": ["core", "shoulders", "back"],
        "difficulty": "beginner",
        "equipment": "none",
        "instructions": [
            "Start in push-up position",
            "Hold body in straight line from head to heels",
            "Engage core and glutes",
            "Keep breathing steadily",
            "Hold for desired time"
        ],
        "variations": ["forearm_plank", "side_plank", "plank_with_leg_raise"],
        "common_mistakes": ["sagging hips", "arching back", "holding breath"],
        "benefits": ["strengthens core", "improves posture", "low impact"]
    },
    "lunge": {
        "name": "Lunge",
        "category": "lower_body",
        "muscle_groups": ["quadriceps", "glutes", "hamstrings", "calves"],
        "difficulty": "beginner",
        "equipment": "none",
        "instructions": [
            "Step forward with one leg",
            "Lower hips until both knees are bent at 90 degrees",
            "Front knee should be over ankle, back knee toward ground",
            "Push off front foot to return to starting position",
            "Alternate legs or complete all reps on one side"
        ],
        "variations": ["forward_lunge", "reverse_lunge", "lateral_lunge", "walking_lunge"],
        "common_mistakes": ["front knee extending past toes", "leaning forward", "upper body tension"],
        "benefits": ["improves balance", "builds leg strength", "functional movement pattern"]
    },
    "deadlift": {
        "name": "Deadlift",
        "category": "full_body",
        "muscle_groups": ["glutes", "hamstrings", "back", "core"],
        "difficulty": "intermediate",
        "equipment": "barbell",
        "instructions": [
            "Stand with feet hip-width apart, bar over mid-foot",
            "Hinge at hips, bend knees to grip bar",
            "Keep back straight, chest up, shoulders back",
            "Drive through heels to lift bar, extending hips and knees",
            "Lower bar with controlled movement"
        ],
        "variations": ["conventional_deadlift", "sumo_deadlift", "romanian_deadlift"],
        "common_mistakes": ["rounding back", "jerking the weight", "overextending at top"],
        "benefits": ["builds full body strength", "improves posture", "functional lifting pattern"]
    }
}

NUTRITION_GUIDELINES = {
    "protein": {
        "daily_requirements": {
            "sedentary": "0.8g per kg body weight",
            "active": "1.2-1.6g per kg body weight",
            "strength_training": "1.6-2.2g per kg body weight",
            "endurance_training": "1.2-1.4g per kg body weight"
        },
        "sources": {
            "animal": ["chicken breast", "fish", "eggs", "greek yogurt", "milk", "beef"],
            "plant": ["lentils", "beans", "tofu", "quinoa", "nuts", "seeds", "pea protein"]
        },
        "timing": "Distribute evenly throughout meals, 20-30g per meal optimal for muscle synthesis"
    },
    "carbohydrates": {
        "daily_requirements": {
            "general": "45-65% of total daily calories",
            "endurance_athletes": "6-10g per kg body weight",
            "strength_athletes": "3-5g per kg body weight"
        },
        "types": {
            "complex": ["oats", "brown rice", "quinoa", "sweet potatoes", "whole grains"],
            "simple": ["fruits", "honey", "maple syrup", "white bread"]
        },
        "timing": "Complex carbs for sustained energy, simple carbs around workouts"
    },
    "fats": {
        "daily_requirements": "20-35% of total daily calories",
        "types": {
            "unsaturated": ["avocado", "nuts", "seeds", "olive oil", "fatty fish"],
            "saturated": ["butter", "coconut oil", "red meat"],
            "trans": ["processed foods", "fried foods"]  # to be avoided
        },
        "benefits": ["hormone production", "vitamin absorption", "brain function"]
    },
    "hydration": {
        "daily_requirements": {
            "men": "3.7 liters (125 ounces)",
            "women": "2.7 liters (91 ounces)",
            "exercise": "+500-750ml per hour of exercise"
        },
        "signs_of_dehydration": ["dark urine", "fatigue", "headache", "dizziness", "dry mouth"],
        "tips": ["carry water bottle", "set reminders", "drink before/after workouts"]
    }
}

FITNESS_PRINCIPLES = {
    "progressive_overload": {
        "description": "Gradually increasing the stress placed on the body during training",
        "methods": [
            "Increase weight/resistance",
            "Increase repetitions",
            "Increase sets",
            "Decrease rest time",
            "Increase training frequency",
            "Improve exercise form"
        ],
        "importance": "Essential for continued muscle growth and strength gains"
    },
    "specificity": {
        "description": "Training should be relevant to the goals and activities you want to improve",
        "examples": [
            "Lift heavy for strength gains",
            "Do cardio for endurance",
            "Practice specific movements for sports performance"
        ]
    },
    "recovery": {
        "description": "Rest and recovery are essential for muscle growth and performance",
        "components": [
            "Sleep: 7-9 hours per night",
            "Rest days: 1-2 days per week from intense training",
            "Nutrition: Adequate protein and calories",
            "Stress management"
        ]
    },
    "consistency": {
        "description": "Regular training is more important than intensity",
        "recommendations": [
            "Minimum 3 training sessions per week",
            "Establish a routine",
            "Track progress",
            "Adjust training as needed"
        ]
    }
}

COMMON_QUESTIONS = {
    "how_often_workout": {
        "question": "How often should I work out?",
        "answer": "For most people, 3-5 days per week is ideal. Beginners should start with 3 days and gradually increase. Listen to your body and allow adequate recovery time.",
        "follow_up": ["What type of workouts?", "What are your goals?", "What's your current fitness level?"]
    },
    "best_time_workout": {
        "question": "What's the best time to work out?",
        "answer": "The best time to work out is when you can be consistent! Some people prefer morning workouts for energy, others prefer evening to de-stress. Find what works for your schedule.",
        "pros_cons": {
            "morning": ["more energy", "consistent", "crowded gyms"],
            "evening": ["less rushed", "better performance", "crowded gyms"]
        }
    },
    "weight_loss": {
        "question": "How can I lose weight effectively?",
        "answer": "Effective weight loss combines consistent exercise with a modest calorie deficit. Focus on strength training to preserve muscle, include cardio for heart health, and prioritize nutrition with whole foods.",
        "key_points": [
            "Create 300-500 calorie deficit",
            "Combine strength and cardio training",
            "Prioritize protein intake",
            "Get adequate sleep",
            "Be patient and consistent"
        ]
    },
    "muscle_gain": {
        "question": "How can I build muscle effectively?",
        "answer": "Muscle building requires progressive overload, adequate protein, and sufficient calories. Focus on compound exercises, eat in a slight calorie surplus, and prioritize recovery.",
        "requirements": [
            "Progressive strength training",
            "1.6-2.2g protein per kg body weight",
            "Slight calorie surplus (200-500 calories)",
            "7-9 hours of sleep",
            "Consistency"
        ]
    }
}

SAFETY_GUIDELINES = {
    "general_safety": [
        "Always warm up before exercise",
        "Use proper form over heavy weight",
        "Listen to your body and stop if you feel pain",
        "Stay hydrated during workouts",
        "Allow adequate recovery time"
    ],
    "beginner_tips": [
        "Start with bodyweight exercises",
        "Focus on learning proper form",
        "Gradually increase intensity",
        "Consider working with a trainer",
        "Don't compare yourself to others"
    ],
    "warning_signs": [
        "Sharp pain during exercise",
        "Dizziness or lightheadedness",
        "Shortness of breath",
        "Chest pain or pressure",
        "Excessive fatigue"
    ],
    "when_to_stop": [
        "Sharp or shooting pain",
        "Joint pain",
        "Feeling faint or dizzy",
        "Chest discomfort",
        "Unable to maintain proper form"
    ]
}

GOAL_SPECIFIC_ADVICE = {
    "weight_loss": {
        "exercise_focus": ["cardio", "full_body_strength", "hiit"],
        "nutrition_focus": ["calorie_deficit", "high_protein", "whole_foods"],
        "recommended_frequency": "4-5 days per week",
        "key_strategies": [
            "Create sustainable calorie deficit",
            "Prioritize protein for muscle preservation",
            "Include both cardio and strength training",
            "Focus on consistency over intensity"
        ]
    },
    "muscle_gain": {
        "exercise_focus": ["progressive_overload", "compound_lifts", "adequate_volume"],
        "nutrition_focus": ["calorie_surplus", "high_protein", "timed_nutrition"],
        "recommended_frequency": "3-4 days per week",
        "key_strategies": [
            "Progressive overload is essential",
            "Eat in slight calorie surplus",
            "Consume adequate protein (1.6-2.2g/kg)",
            "Prioritize compound exercises"
        ]
    },
    "maintenance": {
        "exercise_focus": ["balanced_program", "consistency", "enjoyment"],
        "nutrition_focus": ["balanced_diet", "moderation", "sustainability"],
        "recommended_frequency": "3-4 days per week",
        "key_strategies": [
            "Find enjoyable activities",
            "Maintain balanced approach",
            "Focus on long-term consistency",
            "Adjust as needed"
        ]
    },
    "endurance": {
        "exercise_focus": ["cardio", "progressive_training", "interval_training"],
        "nutrition_focus": ["carbohydrate_timing", "hydration", "electrolytes"],
        "recommended_frequency": "4-6 days per week",
        "key_strategies": [
            "Gradually increase training volume",
            "Include both steady-state and interval training",
            "Proper fueling before/after workouts",
            "Adequate hydration and electrolyte balance"
        ]
    }
}

# Knowledge base helper functions
def get_exercise_info(exercise_name):
    """Get exercise information by name."""
    exercise_key = exercise_name.lower().replace(" ", "_").replace("-", "_")
    return EXERCISE_DATABASE.get(exercise_key)

def get_nutrition_info(topic):
    """Get nutrition information by topic."""
    return NUTRITION_GUIDELINES.get(topic)

def get_goal_specific_advice(goal):
    """Get goal-specific advice."""
    return GOAL_SPECIFIC_ADVICE.get(goal)

def search_knowledge_base(query):
    """Search knowledge base for relevant information."""
    query = query.lower()
    results = []
    
    # Search exercises
    for exercise_key, exercise_data in EXERCISE_DATABASE.items():
        if query in exercise_data["name"].lower() or any(query in muscle.lower() for muscle in exercise_data["muscle_groups"]):
            results.append({
                "type": "exercise",
                "data": exercise_data
            })
    
    # Search nutrition
    for topic, nutrition_data in NUTRITION_GUIDELINES.items():
        if query in topic:
            results.append({
                "type": "nutrition",
                "data": nutrition_data
            })
    
    # Search common questions
    for question_key, question_data in COMMON_QUESTIONS.items():
        if query in question_data["question"].lower():
            results.append({
                "type": "faq",
                "data": question_data
            })
    
    return results

def get_contextual_knowledge(intent, user_profile=None):
    """Get relevant knowledge based on intent and user profile."""
    context = []
    
    if intent == "exercise_advice":
        context.append("Exercise Database: " + str(list(EXERCISE_DATABASE.keys())))
        context.append("Safety Guidelines: " + str(SAFETY_GUIDELINES["general_safety"]))
        
        if user_profile and user_profile.get("fitness_goal"):
            goal_advice = get_goal_specific_advice(user_profile["fitness_goal"])
            if goal_advice:
                context.append("Goal-specific exercise focus: " + ", ".join(goal_advice["exercise_focus"]))
    
    elif intent == "nutrition_question":
        context.append("Nutrition Guidelines: " + str(list(NUTRITION_GUIDELINES.keys())))
        
        if user_profile and user_profile.get("fitness_goal"):
            goal_advice = get_goal_specific_advice(user_profile["fitness_goal"])
            if goal_advice:
                context.append("Goal-specific nutrition focus: " + ", ".join(goal_advice["nutrition_focus"]))
    
    elif intent == "motivation":
        context.append("Fitness Principles: " + str(list(FITNESS_PRINCIPLES.keys())))
    
    return context

logger = logging.getLogger(__name__)


class EnhancedAIChatbot:
    """
    Advanced AI chatbot with GPT/Gemini integration for ZoeFit.
    
    This chatbot combines the power of large language models with
    specialized fitness knowledge to provide personalized, helpful
    responses to user queries.
    
    The system uses a hybrid approach:
    1. First tries to use GPT-4 or Gemini for complex queries
    2. Falls back to rule-based responses for common questions
    3. Always includes safety disclaimers for medical advice
    4. Personalizes responses based on user health metrics
    """
    
    def __init__(self, ai_provider: str = "auto"):
        """
        Initialize the enhanced chatbot.
        
        Args:
            ai_provider: "openai", "gemini", or "auto" (auto-selects best available)
        """
        self.ai_provider = ai_provider
        self.intents = self._load_intents()
        self.responses = self._load_responses()
        self.faq_data = self._load_faq_data()
        self.motivation_quotes = self._load_motivation_quotes()
        
        # Initialize AI clients
        self.openai_client = None
        self.gemini_model = None
        self._initialize_ai_clients()
        
        # System prompts for different contexts
        self.system_prompts = self._load_system_prompts()
        
    def _initialize_ai_clients(self):
        """Initialize AI clients based on availability and configuration."""
        # Initialize OpenAI
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        # Fallback: try to get from environment directly if settings doesn't have it
        if not openai_key:
            import os
            openai_key = os.environ.get('OPENAI_API_KEY')
        
        logger.info(f"OpenAI library available: {OPENAI_AVAILABLE}")
        logger.info(f"OpenAI key present: {bool(openai_key)}")
        if openai_key:
            logger.info(f"OpenAI key format: {openai_key[:10]}...{openai_key[-10:] if len(openai_key) > 20 else 'invalid'}")
            logger.info(f"OpenAI key starts with 'sk-': {openai_key.startswith('sk-')}")
        
        if OPENAI_AVAILABLE and openai_key and openai_key.strip() and (openai_key.startswith('sk-') or openai_key.startswith('sk-proj-')):
            try:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI not available: library not installed - will use enhanced rule-based responses")
            elif not openai_key:
                logger.warning("OpenAI not available: no API key configured - will use enhanced rule-based responses")
            elif not openai_key.strip():
                logger.warning("OpenAI not available: API key is empty - will use enhanced rule-based responses")
            elif not openai_key.startswith('sk-'):
                logger.warning(f"OpenAI not available: API key has invalid format (starts with: {openai_key[:5] if openai_key else 'none'}) - will use enhanced rule-based responses")
        
        # Initialize Gemini
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        # Fallback: try to get from environment directly if settings doesn't have it
        if not gemini_key:
            import os
            gemini_key = os.environ.get('GEMINI_API_KEY')
        
        logger.info(f"Gemini library available: {GEMINI_AVAILABLE}")
        logger.info(f"Gemini key present: {bool(gemini_key)}")
        if gemini_key:
            logger.info(f"Gemini key format: {gemini_key[:10]}...{gemini_key[-10:] if len(gemini_key) > 20 else 'invalid'}")
        
        if GEMINI_AVAILABLE and gemini_key and gemini_key.strip():
            try:
                genai.configure(api_key=gemini_key)
                model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-pro')
                self.gemini_model = genai.GenerativeModel(model_name)
                logger.info(f"✅ Gemini client initialized successfully with model: {model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini client: {e}")
                self.gemini_model = None
        else:
            if not GEMINI_AVAILABLE:
                logger.warning("Gemini not available: library not installed - will use enhanced rule-based responses")
            elif not gemini_key:
                logger.warning("Gemini not available: no API key configured - will use enhanced rule-based responses")
            elif not gemini_key.strip():
                logger.warning("Gemini not available: API key is empty - will use enhanced rule-based responses")
        
        # Log final status
        if not self.openai_client and not self.gemini_model:
            logger.warning("No AI clients available - chatbot will use enhanced rule-based responses with knowledge base")
        elif self.openai_client or self.gemini_model:
            logger.info("At least one AI client is available - chatbot will use AI responses")
    
    def process_message(self, message: str, metrics: HealthMetrics = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process user message and generate intelligent AI response.
        
        Args:
            message: User's message
            metrics: User's health metrics for personalization
            conversation_history: Recent conversation history for context
            
        Returns:
            Dictionary containing response, intent, confidence, and suggestions
        """
        try:
            # Clean and preprocess message
            cleaned_message = self._preprocess_message(message)
            
            # Detect intent
            intent = self._detect_intent(cleaned_message)
            
            # Try AI model first for complex queries with enhanced context
            response_data = self._generate_ai_response(intent, cleaned_message, metrics, conversation_history)
            
            # Enhanced fallback logic with multiple attempts
            if not response_data or response_data.get('confidence', 0) < 0.5:
                logger.warning(f"AI response confidence low ({response_data.get('confidence', 0) if response_data else 0}), trying rule-based fallback")
                response_data = self._generate_rule_based_response(intent, cleaned_message, metrics)
            
            # Final fallback if everything fails
            if not response_data or response_data.get('confidence', 0) < 0.3:
                logger.error("All response methods failed, using emergency fallback")
                response_data = {
                    'text': "I'm experiencing some technical difficulties, but I'm here to help! You can ask me about exercises, nutrition, or motivation. If you need immediate help, try rephrasing your question.",
                    'confidence': 0.5,
                    'provider': 'emergency_fallback'
                }
            
            # Add suggestions
            suggestions = self._generate_suggestions(intent, metrics)
            
            return {
                'response': response_data['text'],
                'intent': intent,
                'confidence': response_data['confidence'],
                'suggestions': suggestions,
                'timestamp': datetime.now().isoformat(),
                'ai_provider': response_data.get('provider', 'rule-based')
            }
            
        except Exception as e:
            logger.error(f"Critical error processing message: {e}")
            return {
                'response': "I'm here to help with your fitness journey! I'm currently experiencing some technical difficulties, but please try asking me about exercises, nutrition, or motivation tips.",
                'intent': 'error',
                'confidence': 0.0,
                'suggestions': [
                    "Ask about exercises",
                    "Learn about nutrition", 
                    "Get motivation tips",
                    "Try rephrasing your question"
                ],
                'timestamp': datetime.now().isoformat(),
                'ai_provider': 'error_fallback'
            }
    
    def _generate_ai_response(self, intent: str, message: str, metrics: HealthMetrics = None, conversation_history: List[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Generate response using AI model (GPT-4 or Gemini).
        
        Returns None if AI is unavailable or fails to generate response.
        """
        # Check if we have an AI client available
        if not self.openai_client and not self.gemini_model:
            logger.warning("No AI clients available - falling back to rule-based responses")
            return None
        
        # Build enhanced context-aware prompt
        context = self._build_context(intent, message, metrics, conversation_history)
        
        # Try OpenAI first if available
        if self.openai_client and (self.ai_provider in ['openai', 'auto']):
            try:
                return self._call_openai(context, intent)
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}")
        
        # Try Gemini if OpenAI failed or not preferred
        if self.gemini_model and (self.ai_provider in ['gemini', 'auto']):
            try:
                return self._call_gemini(context, intent)
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")
        
        logger.warning("All AI providers failed - falling back to rule-based responses")
        return None
    
    def _call_openai(self, context: str, intent: str) -> Dict[str, Any]:
        """Call OpenAI API for response generation."""
        try:
            model_name = getattr(settings, 'OPENAI_MODEL', 'gpt-4o')
            max_tokens = getattr(settings, 'AI_CHAT_MAX_TOKENS', 500)
            temperature = getattr(settings, 'AI_CHAT_TEMPERATURE', 0.8)
            
            logger.info(f"Calling OpenAI API with model: {model_name}")
            
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": self.system_prompts.get(intent, self.system_prompts['default'])},
                    {"role": "user", "content": context}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=1,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            logger.info(f"OpenAI response received successfully")
            
            # Add safety disclaimer for medical questions
            if intent == 'medical_question':
                response_text += "\n\n⚠️ Please consult with a healthcare professional for personalized medical advice."
            
            return {
                'text': response_text,
                'confidence': 0.9,
                'provider': 'openai'
            }
            
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise Exception("OpenAI API key is invalid or expired")
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {e}")
            raise Exception("OpenAI API rate limit exceeded")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {e}")
            raise
    
    def _call_gemini(self, context: str, intent: str) -> Dict[str, Any]:
        """Call Google Gemini API for response generation."""
        try:
            max_tokens = getattr(settings, 'AI_CHAT_MAX_TOKENS', 500)
            temperature = getattr(settings, 'AI_CHAT_TEMPERATURE', 0.8)
            
            full_prompt = f"{self.system_prompts.get(intent, self.system_prompts['default'])}\n\nUser: {context}"
            
            logger.info("Calling Gemini API")
            
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "top_p": 1,
                }
            )
            
            response_text = response.text.strip()
            logger.info("Gemini response received successfully")
            
            # Add safety disclaimer for medical questions
            if intent == 'medical_question':
                response_text += "\n\n⚠️ Please consult with a healthcare professional for personalized medical advice."
            
            return {
                'text': response_text,
                'confidence': 0.9,
                'provider': 'gemini'
            }
            
        except Exception as e:
            error_str = str(e).lower()
            if "permission" in error_str or "forbidden" in error_str or "api key" in error_str:
                logger.error(f"Gemini authentication error: {e}")
                raise Exception("Gemini API key is invalid or missing")
            elif "quota" in error_str or "rate" in error_str:
                logger.error(f"Gemini rate limit error: {e}")
                raise Exception("Gemini API quota exceeded")
            else:
                logger.error(f"Gemini API error: {e}")
                raise Exception(f"Gemini API error: {e}")
    
    def _build_context(self, intent: str, message: str, metrics: HealthMetrics = None, conversation_history: List[Dict] = None) -> str:
        """Build context-aware prompt with user information, conversation history, and fitness knowledge base."""
        context_parts = [f"User message: {message}"]
        
        # Add conversation history for context awareness with configurable window
        if conversation_history:
            context_window = getattr(settings, 'AI_CHAT_CONTEXT_WINDOW', 10)
            recent_history = conversation_history[-context_window:]  # Use configurable context window
            history_text = "\n".join([
                f"User: {chat['user_message']}\nAssistant: {chat['ai_response']}"
                for chat in recent_history
            ])
            context_parts.append(f"Recent conversation history:\n{history_text}")
        
        # Add fitness knowledge base context
        user_profile = {}
        if metrics:
            user_profile = {
                "fitness_goal": metrics.fitness_goal,
                "activity_level": metrics.activity_level,
                "bmi_category": metrics.get_bmi_category() if metrics.bmi else None
            }
        
        knowledge_context = get_contextual_knowledge(intent, user_profile)
        if knowledge_context:
            context_parts.append(f"Relevant fitness knowledge: {', '.join(knowledge_context)}")
        
        # Search knowledge base for specific information
        knowledge_results = search_knowledge_base(message)
        if knowledge_results:
            relevant_info = []
            for result in knowledge_results[:3]:  # Limit to top 3 results
                if result["type"] == "exercise":
                    relevant_info.append(f"Exercise: {result['data']['name']} - {', '.join(result['data']['muscle_groups'])}")
                elif result["type"] == "nutrition":
                    relevant_info.append(f"Nutrition topic: {result['type']}")
                elif result["type"] == "faq":
                    relevant_info.append(f"Related FAQ: {result['data']['question']}")
            
            if relevant_info:
                context_parts.append(f"Specific information: {', '.join(relevant_info)}")
        
        # Add enhanced user context if available
        if metrics:
            user_context = []
            
            if metrics.fitness_goal:
                goal_map = {
                    'weight_loss': 'weight loss',
                    'muscle_gain': 'muscle building',
                    'maintenance': 'maintenance',
                    'endurance': 'improving endurance'
                }
                user_context.append(f"Fitness goal: {goal_map.get(metrics.fitness_goal, metrics.fitness_goal)}")
            
            if metrics.height and metrics.weight:
                user_context.append(f"Height: {metrics.height}cm, Weight: {metrics.weight}kg")
                if metrics.bmi:
                    user_context.append(f"BMI: {metrics.bmi} ({metrics.get_bmi_category()})")
            
            if metrics.activity_level:
                activity_map = {
                    'sedentary': 'sedentary (little to no exercise)',
                    'light': 'light activity (1-3 days/week)',
                    'moderate': 'moderate activity (3-5 days/week)',
                    'active': 'active (6-7 days/week)',
                    'very_active': 'very active (twice per day or intense training)'
                }
                user_context.append(f"Activity level: {activity_map.get(metrics.activity_level, metrics.activity_level)}")
            
            if metrics.dietary_preferences:
                if isinstance(metrics.dietary_preferences, dict):
                    diet_types = metrics.dietary_preferences.get('diet_types', [])
                    if diet_types:
                        user_context.append(f"Diet types: {', '.join(diet_types)}")
                else:
                    user_context.append(f"Dietary preferences: {metrics.dietary_preferences}")
            
            if metrics.allergies:
                if isinstance(metrics.allergies, list):
                    user_context.append(f"Allergies: {', '.join(metrics.allergies)}")
                else:
                    user_context.append(f"Allergies: {metrics.allergies}")
            
            if metrics.target_weight:
                user_context.append(f"Target weight: {metrics.target_weight}kg")
            
            # Add calculated daily calories for nutrition advice
            if intent == 'nutrition_question':
                daily_calories = metrics.calculate_daily_calories()
                user_context.append(f"Daily calorie needs: {daily_calories} calories")
            
            # Add goal-specific advice context
            if metrics.fitness_goal:
                goal_advice = get_goal_specific_advice(metrics.fitness_goal)
                if goal_advice:
                    if intent == 'exercise_advice':
                        user_context.append(f"Recommended exercises: {', '.join(goal_advice['exercise_focus'])}")
                    elif intent == 'nutrition_question':
                        user_context.append(f"Nutrition focus: {', '.join(goal_advice['nutrition_focus'])}")
            
            # Add progress context if available
            if hasattr(metrics, 'get_progress_summary'):
                progress_summary = metrics.get_progress_summary()
                if progress_summary:
                    user_context.append(f"Recent progress: {progress_summary}")
            
            if user_context:
                context_parts.append(f"User profile context: {', '.join(user_context)}")
        
        return "\n".join(context_parts)
    
    def _generate_rule_based_response(self, intent: str, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Generate response using rule-based system (fallback).
        """
        if intent == 'exercise_advice':
            return self._generate_exercise_advice(message, metrics)
        elif intent == 'nutrition_question':
            return self._generate_nutrition_advice(message, metrics)
        elif intent == 'motivation':
            return self._generate_motivation_response(message, metrics)
        elif intent == 'progress_tracking':
            return self._generate_progress_response(message, metrics)
        elif intent == 'medical_question':
            return self._generate_medical_response(message, metrics)
        elif intent == 'greeting':
            return self._generate_greeting_response(message, metrics)
        else:
            return self._generate_general_response(message, metrics)
    
    def _preprocess_message(self, message: str) -> str:
        """Clean and preprocess user message."""
        message = message.lower()
        message = re.sub(r'[^a-zA-Z0-9\s]', '', message)
        message = re.sub(r'\s+', ' ', message).strip()
        return message
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message."""
        intent_scores = {}
        
        for intent, keywords in self.intents.items():
            score = sum(1 for keyword in keywords if keyword in message)
            
            # Weight important keywords
            if intent == 'exercise_advice' and any(word in message for word in ['exercise', 'workout', 'training']):
                score += 2
            elif intent == 'nutrition_question' and any(word in message for word in ['food', 'diet', 'eat', 'calories']):
                score += 2
            elif intent == 'motivation' and any(word in message for word in ['motivate', 'encourage', 'can\'t', 'tired']):
                score += 2
            
            intent_scores[intent] = score
        
        return max(intent_scores, key=intent_scores.get) if max(intent_scores.values()) > 0 else 'general'
    
    def _generate_suggestions(self, intent: str, metrics: HealthMetrics = None) -> List[str]:
        """Generate contextual suggestions based on intent and user metrics."""
        suggestions = []
        
        if intent == 'exercise_advice':
            suggestions.extend(["Ask about specific exercises", "Learn about workout routines", "Get form tips"])
        elif intent == 'nutrition_question':
            suggestions.extend(["Ask about meal planning", "Learn about macronutrients", "Get healthy recipes"])
        elif intent == 'motivation':
            suggestions.extend(["Share your fitness goals", "Ask about overcoming challenges", "Get accountability tips"])
        
        # Add personalized suggestions
        if metrics:
            if metrics.fitness_goal == 'weight_loss':
                suggestions.append("Ask about fat loss strategies")
            elif metrics.fitness_goal == 'muscle_gain':
                suggestions.append("Learn about muscle building")
            elif metrics.fitness_goal == 'endurance':
                suggestions.append("Ask about stamina improvement")
        
        return suggestions[:3]
    
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load enhanced system prompts for different intents with user personalization."""
        return {
            'default': """You are ZoeFit, an intelligent fitness assistant powered by advanced AI. You have access to the user's complete health profile, fitness goals, and conversation history. Provide highly personalized, evidence-based fitness advice.

Your capabilities:
- Access to user's health metrics (BMI, weight, height, activity level)
- Knowledge of user's fitness goals and dietary preferences
- Conversation history for context awareness
- Comprehensive fitness and nutrition knowledge base

Guidelines:
- Personalize every response using the user's profile data
- Reference their specific goals (weight loss, muscle gain, maintenance, endurance)
- Consider their activity level and fitness experience
- Provide actionable, specific recommendations
- Keep responses conversational but informative (under 200 words)
- Include safety disclaimers when appropriate
- Use conversation history to maintain context""",
            
            'exercise_advice': """You are a certified fitness trainer providing personalized exercise advice. You have detailed knowledge of the user's fitness profile.

User context available:
- Fitness goal and target weight
- Current activity level and BMI category
- Available equipment and preferences
- Exercise history and performance data

Guidelines:
- Recommend exercises specific to their fitness goal and experience level
- Adjust intensity based on their current activity level
- Consider any limitations or preferences from their profile
- Reference their progress and achievements when relevant
- Provide specific sets, reps, and progression advice
- Emphasize proper form and safety
- Keep responses under 200 words""",
            
            'nutrition_question': """You are a registered dietitian specializing in sports nutrition. You have access to the user's complete nutritional profile.

User context available:
- Daily calorie needs and macronutrient requirements
- Dietary preferences, restrictions, and allergies
- Fitness goals and target weight
- Current eating patterns and preferences

Guidelines:
- Provide meal plans and advice tailored to their calorie needs
- Respect dietary preferences and allergies
- Suggest practical, sustainable meal options
- Time nutrition advice around their workout schedule
- Reference their weight goals (loss/gain/maintenance)
- Include supplement advice when appropriate
- Keep responses under 200 words
- Always mention consulting professionals for specific medical conditions""",
            
            'motivation': """You are an empathetic fitness coach who understands the user's journey and challenges. You have access to their progress and consistency data.

User context available:
- Workout history and consistency patterns
- Progress towards goals
- Previous challenges and achievements
- Current fitness level and goals

Guidelines:
- Reference their actual progress and achievements
- Acknowledge their specific challenges and goals
- Provide personalized encouragement based on their journey
- Suggest practical strategies for maintaining consistency
- Celebrate their wins and milestones
- Be empathetic about their struggles
- Keep responses uplifting and under 150 words""",
            
            'progress_tracking': """You are a fitness analytics specialist helping users understand and optimize their progress. You have access to their complete progress data.

User context available:
- Historical weight and measurement data
- Workout completion rates and performance
- Progress towards specific goals
- Plateaus and breakthrough periods

Guidelines:
- Analyze their actual progress trends and patterns
- Provide realistic expectations based on their data
- Identify and address plateaus constructively
- Celebrate meaningful progress and consistency
- Suggest adjustments based on their results
- Reference their target weight and goals
- Keep responses under 200 words""",
            
            'medical_question': """You must provide general fitness safety information only. Always include strong disclaimers to consult healthcare professionals. Do not provide specific medical advice.

User context available:
- Basic health metrics and conditions
- Fitness level and limitations
- Goals and activity preferences

Guidelines:
- Focus on general fitness safety and best practices
- Explain warning signs that require medical attention
- Do not diagnose or provide treatment recommendations
- Consider their health profile only for general safety advice
- Always include strong disclaimer about consulting healthcare providers
- Keep responses under 150 words
- Err on the side of caution""",
            
            'greeting': """You are ZoeFit, the user's personal fitness assistant. You know their profile and goals.

User context available:
- Name and fitness goals
- Current progress and activity level
- Previous interactions and preferences

Guidelines:
- Welcome them back if they've used the app before
- Reference their current goals or recent progress
- Ask how you can help with their specific fitness journey
- Keep greeting warm, personal, and under 100 words
- Mention you can help with exercises, nutrition, and motivation"""
        }
    
    # Include all the original rule-based methods as fallbacks
    def _generate_exercise_advice(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """Generate exercise-related advice (enhanced rule-based fallback)."""
        # Search knowledge base first
        knowledge_results = search_knowledge_base(message)
        if knowledge_results:
            for result in knowledge_results:
                if result["type"] == "exercise":
                    exercise = result["data"]
                    return {
                        'text': f"{exercise['name']}: {exercise['instructions'][0]}. This exercise targets {', '.join(exercise['muscle_groups'])}. Benefits include {', '.join(exercise['benefits'][:2])}.",
                        'confidence': 0.9
                    }
        
        # Enhanced contextual responses
        if 'push' in message or 'chest' in message:
            return {
                'text': "Push-ups are excellent for building upper body strength! They work your chest, shoulders, and triceps. If regular push-ups are challenging, start with knee push-ups or incline push-ups against a wall. Aim for 3 sets of 8-12 reps with proper form.",
                'confidence': 0.8
            }
        elif 'squat' in message or 'leg' in message:
            return {
                'text': "Squats are fundamental for building leg strength and glutes! Keep your chest up, back straight, and knees behind your toes. Go down until your thighs are parallel to the floor. Start with bodyweight squats and gradually add weight as you get stronger.",
                'confidence': 0.8
            }
        elif 'beginner' in message or 'start' in message:
            return {
                'text': "Great question! As a beginner, start with 3 days per week focusing on basic exercises: push-ups, squats, planks, and lunges. Focus on proper form over intensity. Each workout should be 20-30 minutes. Consistency is more important than intensity when starting out!",
                'confidence': 0.85
            }
        elif 'weight' in message and 'loss' in message:
            return {
                'text': "For weight loss, combine strength training with cardio! Aim for 3-4 strength training sessions and 2-3 cardio sessions per week. Strength training builds muscle that boosts metabolism, while cardio burns calories. Don't forget nutrition - weight loss is 80% diet and 20% exercise!",
                'confidence': 0.8
            }
        else:
            # Enhanced varied responses
            responses = [
                "Based on your fitness goals, I recommend a balanced routine with both strength and cardio exercises. This approach ensures comprehensive fitness development.",
                "Consistency is the key to success! Aim for regular workouts rather than occasional intense sessions. Your body adapts best to consistent stimulus.",
                "Don't forget the importance of recovery! Your muscles grow and repair during rest days. Include 1-2 rest days per week in your routine.",
                "Progressive overload is essential - gradually increase weight, reps, or intensity to keep seeing results and avoid plateaus.",
                "Form over weight always! Proper exercise technique prevents injuries and ensures you're targeting the right muscles effectively."
            ]
            return {
                'text': random.choice(responses),
                'confidence': 0.75
            }
    
    def _generate_nutrition_advice(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """Generate nutrition-related advice (enhanced rule-based fallback)."""
        # Search knowledge base first
        knowledge_results = search_knowledge_base(message)
        if knowledge_results:
            for result in knowledge_results:
                if result["type"] == "nutrition":
                    nutrition_info = result["data"]
                    return {
                        'text': f"Here's what I found about {result['type']}: {str(nutrition_info)[:200]}...",
                        'confidence': 0.9
                    }
        
        # Enhanced contextual responses
        if 'protein' in message:
            return {
                'text': "Protein is crucial for muscle repair and growth! For strength training, aim for 1.6-2.2g per kg of bodyweight daily. Excellent sources include chicken breast, fish, eggs, Greek yogurt, and plant-based options like lentils, tofu, and quinoa. Spread your intake throughout the day for optimal absorption!",
                'confidence': 0.85
            }
        elif 'water' in message or 'hydration' in message:
            return {
                'text': "Hydration is essential for performance and recovery! Aim for 2.7-3.7 liters daily, plus an additional 500-750ml per hour of exercise. Monitor your urine color - pale yellow indicates good hydration. Don't wait until you're thirsty to drink!",
                'confidence': 0.85
            }
        elif 'pre' in message and 'workout' in message:
            return {
                'text': "Pre-workout nutrition is key! Eat a balanced meal 2-3 hours before exercise containing carbs for energy and some protein. Good options: oatmeal with banana, whole grain toast with peanut butter, or a smoothie with fruit and protein powder. Keep it light if eating closer to workout time.",
                'confidence': 0.8
            }
        elif 'calories' in message:
            return {
                'text': "Calorie needs vary based on goals! For weight loss, aim for a modest 300-500 calorie deficit. For muscle gain, a 200-500 calorie surplus works well. Use an online calculator to estimate your baseline needs, then adjust based on your progress. Focus on food quality over just calories!",
                'confidence': 0.8
            }
        else:
            # Enhanced varied responses
            responses = [
                "Nutrition is 80% of fitness success! Focus on whole foods, lean proteins, complex carbs, and healthy fats. Meal prep can help you stay consistent with your goals.",
                "Don't forget the power of timing! Eat protein within 30 minutes post-workout for optimal muscle recovery. Complex carbs before exercise provide sustained energy.",
                "Balance is key in nutrition! Include all macronutrients - proteins for muscle, carbs for energy, and fats for hormone function. The 80/20 rule works well for most people.",
                "Listen to your body's hunger and fullness cues. Eat when hungry, stop when satisfied. Mindful eating helps prevent overeating and improves digestion.",
                "Supplements can help but aren't magic! Focus on getting nutrients from whole foods first. Consider basic supplements like vitamin D, omega-3, or protein powder if needed."
            ]
            return {
                'text': random.choice(responses),
                'confidence': 0.75
            }
    
    def _generate_motivation_response(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """Generate motivational response (rule-based fallback)."""
        if 'tired' in message or 'can\'t' in message:
            return {
                'text': "It's okay to feel tired sometimes! Remember why you started. Even a 10-minute workout is better than none. You've got this!",
                'confidence': 0.8
            }
        else:
            quote = random.choice(self.motivation_quotes)
            return {
                'text': f"{quote} Keep pushing forward!",
                'confidence': 0.7
            }
    
    def _generate_progress_response(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """Generate progress tracking advice (rule-based fallback)."""
        return {
            'text': "Consistent tracking helps you see progress! Focus on trends rather than daily fluctuations. Every step forward counts!",
            'confidence': 0.7
        }
    
    def _generate_medical_response(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """Generate medical-related responses with disclaimers."""
        return {
            'text': "I can provide general fitness advice, but for medical concerns, please consult with a healthcare professional. They can provide personalized advice based on your specific health conditions.",
            'confidence': 0.9
        }
    
    def _generate_greeting_response(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """Generate greeting response."""
        greetings = [
            "Hello! I'm here to help with your fitness journey. What can I assist you with today?",
            "Hi there! Ready to crush your fitness goals? How can I help you today?",
            "Welcome! I'm your AI fitness assistant. Ask me anything about workouts, nutrition, or motivation!"
        ]
        
        return {
            'text': random.choice(greetings),
            'confidence': 0.9
        }
    
    def _generate_general_response(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """Generate general response when intent is unclear."""
        # Try to match with FAQ from knowledge base
        knowledge_results = search_knowledge_base(message)
        if knowledge_results:
            for result in knowledge_results:
                if result["type"] == "faq":
                    return {
                        'text': result["data"]["answer"],
                        'confidence': 0.8
                    }
        
        # Try to match with original FAQ
        for faq in self.faq_data:
            if any(keyword in message for keyword in faq['keywords']):
                return {
                    'text': faq['answer'],
                    'confidence': 0.7
                }
        
        # Default response
        default_responses = [
            "I'm here to help with your fitness journey! You can ask me about exercises, nutrition, motivation, or progress tracking.",
            "I can assist with workout advice, nutrition tips, and motivation. What specific aspect of fitness would you like to know about?",
            "Feel free to ask me about exercises, meal planning, or any fitness-related questions. I'm here to support your goals!"
        ]
        
        return {
            'text': random.choice(default_responses),
            'confidence': 0.5
        }
    
    # Load methods for intents, responses, FAQ, and quotes
    def _load_intents(self) -> Dict[str, List[str]]:
        """Load intent keywords for classification."""
        return {
            'exercise_advice': ['exercise', 'workout', 'training', 'fitness', 'gym', 'muscle', 'strength', 'cardio', 'push', 'pull', 'squat', 'lift', 'routine'],
            'nutrition_question': ['food', 'diet', 'eat', 'calories', 'protein', 'carbs', 'fat', 'nutrition', 'meal', 'supplement', 'vitamin', 'water', 'hydration'],
            'motivation': ['motivate', 'encourage', 'can\'t', 'tired', 'lazy', 'bored', 'quit', 'give up', 'struggle', 'challenge', 'difficult'],
            'progress_tracking': ['progress', 'results', 'track', 'measure', 'weight', 'plateau', 'stuck', 'improvement', 'goals', 'achievement'],
            'medical_question': ['pain', 'injury', 'hurt', 'medical', 'doctor', 'medicine', 'condition', 'health', 'symptom', 'treatment'],
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'thanks', 'thank you']
        }
    
    def _load_responses(self) -> Dict[str, List[str]]:
        """Load response templates for different intents."""
        return {
            'exercise_advice': [
                "Consistency is key to seeing results! Aim for at least 3 workouts per week.",
                "Listen to your body and progress gradually. Quality over quantity!",
                "Mix up your routine to prevent boredom and plateaus. Try new exercises regularly.",
                "Don't forget to warm up before workouts and cool down after. Your body will thank you!"
            ],
            'nutrition_question': [
                "Focus on whole foods and balanced meals. Remember, you can't out-train a bad diet!",
                "Preparation is key - meal prep can help you stay on track with your nutrition goals.",
                "Don't forget about hydration! Water is essential for performance and recovery.",
                "Allow for flexibility in your diet. The 80/20 rule works well for most people."
            ],
            'motivation': [
                "Every workout is progress, no matter how small. Keep showing up for yourself!",
                "Your future self will thank you for the work you're putting in today.",
                "Remember why you started on this journey. Your goals are worth the effort!",
                "Progress isn't always linear. Trust the process and stay consistent!"
            ]
        }
    
    def _load_faq_data(self) -> List[Dict[str, Any]]:
        """Load frequently asked questions and answers."""
        return [
            {
                'keywords': ['how often', 'frequency', 'days', 'week'],
                'question': 'How often should I work out?',
                'answer': 'For most people, 3-5 days per week is ideal. Beginners should start with 3 days and gradually increase. Listen to your body and allow adequate recovery time.'
            },
            {
                'keywords': ['best time', 'when', 'morning', 'evening'],
                'question': 'What\'s the best time to work out?',
                'answer': 'The best time to work out is when you can be consistent! Some people prefer morning workouts for energy, others prefer evening to de-stress. Find what works for your schedule.'
            },
            {
                'keywords': ['lose weight', 'weight loss', 'fat'],
                'question': 'How can I lose weight effectively?',
                'answer': 'Effective weight loss combines consistent exercise with a modest calorie deficit. Focus on strength training to preserve muscle, include cardio for heart health, and prioritize nutrition with whole foods.'
            }
        ]
    
    def _load_motivation_quotes(self) -> List[str]:
        """Load motivational quotes."""
        return [
            "The only bad workout is the one that didn't happen.",
            "Your body can stand almost anything. It's your mind you have to convince.",
            "Success starts with self-discipline.",
            "Don't stop when you're tired. Stop when you're done.",
            "The pain you feel today will be the strength you feel tomorrow.",
            "Fitness is not about being better than someone else. It's about being better than you used to be.",
            "A one hour workout is 4% of your day. No excuses.",
            "The hardest lift is lifting your butt off the couch.",
            "Your only limit is you.",
            "Sweat is just fat crying."
        ]
