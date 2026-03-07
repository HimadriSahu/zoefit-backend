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
    import google.genai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False
        genai = None

from django.conf import settings
from .models import HealthMetrics

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
        if OPENAI_AVAILABLE and hasattr(settings, 'OPENAI_API_KEY'):
            try:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        
        # Initialize Gemini
        if GEMINI_AVAILABLE and hasattr(settings, 'GEMINI_API_KEY'):
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-pro')
                self.gemini_model = genai.GenerativeModel(model_name)
                logger.info(f"Gemini client initialized successfully with model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.gemini_model = None
    
    def process_message(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Process user message and generate intelligent AI response.
        
        Args:
            message: User's message
            metrics: User's health metrics for personalization
            
        Returns:
            Dictionary containing response, intent, confidence, and suggestions
        """
        try:
            # Clean and preprocess message
            cleaned_message = self._preprocess_message(message)
            
            # Detect intent
            intent = self._detect_intent(cleaned_message)
            
            # Try AI model first for complex queries
            response_data = self._generate_ai_response(intent, cleaned_message, metrics)
            
            # Fallback to rule-based if AI fails
            if not response_data or response_data.get('confidence', 0) < 0.5:
                response_data = self._generate_rule_based_response(intent, cleaned_message, metrics)
            
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
            logger.error(f"Error processing message: {e}")
            return {
                'response': "I'm here to help with your fitness journey! Could you please rephrase your question?",
                'intent': 'error',
                'confidence': 0.0,
                'suggestions': [
                    "Ask about exercises",
                    "Learn about nutrition",
                    "Get motivation tips"
                ],
                'timestamp': datetime.now().isoformat(),
                'ai_provider': 'error'
            }
    
    def _generate_ai_response(self, intent: str, message: str, metrics: HealthMetrics = None) -> Optional[Dict[str, Any]]:
        """
        Generate response using AI model (GPT-4 or Gemini).
        
        Returns None if AI is unavailable or fails to generate response.
        """
        # Check if we have an AI client available
        if not self.openai_client and not self.gemini_model:
            return None
        
        # Build context-aware prompt
        context = self._build_context(intent, message, metrics)
        
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
        
        return None
    
    def _call_openai(self, context: str, intent: str) -> Dict[str, Any]:
        """Call OpenAI API for response generation."""
        try:
            model_name = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": self.system_prompts.get(intent, self.system_prompts['default'])},
                    {"role": "user", "content": context}
                ],
                max_tokens=300,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Add safety disclaimer for medical questions
            if intent == 'medical_question':
                response_text += "\n\n⚠️ Please consult with a healthcare professional for personalized medical advice."
            
            return {
                'text': response_text,
                'confidence': 0.9,
                'provider': 'openai'
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _call_gemini(self, context: str, intent: str) -> Dict[str, Any]:
        """Call Google Gemini API for response generation."""
        try:
            full_prompt = f"{self.system_prompts.get(intent, self.system_prompts['default'])}\n\nUser: {context}"
            
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 300,
                    "top_p": 1,
                }
            )
            
            response_text = response.text.strip()
            
            # Add safety disclaimer for medical questions
            if intent == 'medical_question':
                response_text += "\n\n⚠️ Please consult with a healthcare professional for personalized medical advice."
            
            return {
                'text': response_text,
                'confidence': 0.9,
                'provider': 'gemini'
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def _build_context(self, intent: str, message: str, metrics: HealthMetrics = None) -> str:
        """Build context-aware prompt with user information."""
        context_parts = [f"User message: {message}"]
        
        # Add user context if available
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
                    user_context.append(f"BMI: {metrics.bmi}")
            
            if metrics.activity_level:
                user_context.append(f"Activity level: {metrics.activity_level}")
            
            if metrics.dietary_preferences:
                user_context.append(f"Dietary preferences: {metrics.dietary_preferences}")
            
            if metrics.allergies:
                user_context.append(f"Allergies: {metrics.allergies}")
            
            if user_context:
                context_parts.append(f"User context: {', '.join(user_context)}")
        
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
        """Load system prompts for different intents."""
        return {
            'default': """You are a friendly, knowledgeable fitness assistant for ZoeFit. Provide helpful, accurate fitness advice in a conversational tone. Keep responses concise but informative. Always prioritize safety and encourage users to consult professionals for medical concerns.""",
            
            'exercise_advice': """You are a fitness expert providing exercise advice. Consider the user's fitness level and goals. Provide specific, actionable advice. Emphasize proper form and safety. Keep responses under 200 words.""",
            
            'nutrition_question': """You are a nutrition specialist for fitness enthusiasts. Provide evidence-based nutrition advice. Consider dietary preferences and restrictions mentioned. Keep responses practical and actionable. Always mention consulting professionals for specific medical conditions.""",
            
            'motivation': """You are an encouraging fitness coach. Provide motivational support that is genuine and uplifting. Share practical tips for staying consistent. Be empathetic but firm about the importance of consistency.""",
            
            'progress_tracking': """You are a fitness progress specialist. Provide advice on tracking fitness progress effectively. Suggest realistic expectations and celebrate small wins. Address plateaus constructively.""",
            
            'medical_question': """You must provide general information only and always include a disclaimer to consult healthcare professionals. Do not provide specific medical advice. Focus on general fitness safety and when to seek professional help.""",
            
            'greeting': """You are a welcoming fitness assistant. Greet users warmly and briefly introduce yourself as their fitness helper. Ask how you can assist with their fitness journey today."""
        }
    
    # Include all the original rule-based methods as fallbacks
    def _generate_exercise_advice(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """Generate exercise-related advice (rule-based fallback)."""
        if 'push' in message or 'chest' in message:
            return {
                'text': "Push-ups are excellent for chest, shoulders, and triceps! Start with knee push-ups if regular ones are too challenging. Aim for 3 sets of 8-12 reps, focusing on good form.",
                'confidence': 0.8
            }
        elif 'squat' in message or 'leg' in message:
            return {
                'text': "Squats are fantastic for building leg strength and glutes! Keep your back straight and knees behind your toes. Start with bodyweight squats before adding weight.",
                'confidence': 0.8
            }
        else:
            return {
                'text': random.choice(self.responses['exercise_advice']),
                'confidence': 0.7
            }
    
    def _generate_nutrition_advice(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """Generate nutrition-related advice (rule-based fallback)."""
        if 'protein' in message:
            return {
                'text': "Protein is crucial for muscle repair and growth! Aim for 1.6-2.2g per kg of bodyweight if you're strength training. Good sources include chicken, fish, eggs, Greek yogurt, and plant-based options like lentils and tofu.",
                'confidence': 0.8
            }
        else:
            return {
                'text': random.choice(self.responses['nutrition_question']),
                'confidence': 0.7
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
        # Try to match with FAQ
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
