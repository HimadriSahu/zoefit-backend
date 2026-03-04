"""
AI Chatbot Module - Conversational AI Assistant

This module contains the AI chatbot logic for providing fitness advice,
answering questions, and offering personalized recommendations.
"""

import re
import random
from typing import Dict, Any, List
from datetime import datetime

from .models import HealthMetrics


class AIChatbot:
    """
    AI-powered fitness chatbot for personalized advice and support.
    """
    
    def __init__(self):
        self.intents = self._load_intents()
        self.responses = self._load_responses()
        self.faq_data = self._load_faq_data()
        self.motivation_quotes = self._load_motivation_quotes()
        
    def process_message(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Process user message and generate AI response.
        """
        try:
            # Clean and preprocess message
            cleaned_message = self._preprocess_message(message)
            
            # Detect intent
            intent = self._detect_intent(cleaned_message)
            
            # Generate response based on intent
            response_data = self._generate_response(intent, cleaned_message, metrics)
            
            # Add suggestions if applicable
            suggestions = self._generate_suggestions(intent, metrics)
            
            return {
                'response': response_data['text'],
                'intent': intent,
                'confidence': response_data['confidence'],
                'suggestions': suggestions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'response': "I'm here to help with your fitness journey. Could you please rephrase your question?",
                'intent': 'error',
                'confidence': 0.0,
                'suggestions': [],
                'timestamp': datetime.now().isoformat()
            }
    
    def _preprocess_message(self, message: str) -> str:
        """
        Clean and preprocess user message.
        """
        # Convert to lowercase
        message = message.lower()
        
        # Remove special characters except spaces
        message = re.sub(r'[^a-zA-Z0-9\s]', '', message)
        
        # Remove extra spaces
        message = re.sub(r'\s+', ' ', message).strip()
        
        return message
    
    def _detect_intent(self, message: str) -> str:
        """
        Detect user intent from message.
        """
        intent_scores = {}
        
        for intent, keywords in self.intents.items():
            score = 0
            for keyword in keywords:
                if keyword in message:
                    score += 1
            
            # Weight by keyword importance
            if intent == 'exercise_advice' and any(word in message for word in ['exercise', 'workout', 'training']):
                score += 2
            elif intent == 'nutrition_question' and any(word in message for word in ['food', 'diet', 'eat', 'calories']):
                score += 2
            elif intent == 'motivation' and any(word in message for word in ['motivate', 'encourage', 'can\'t', 'tired']):
                score += 2
            
            intent_scores[intent] = score
        
        # Return intent with highest score
        if max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        else:
            return 'general'
    
    def _generate_response(self, intent: str, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Generate response based on detected intent.
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
    
    def _generate_exercise_advice(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Generate exercise-related advice.
        """
        # Check for specific exercise mentions
        if 'push' in message or 'chest' in message:
            return {
                'text': "Push-ups are excellent for chest, shoulders, and triceps! Start with knee push-ups if regular ones are too challenging. Aim for 3 sets of 8-12 reps, focusing on good form.",
                'confidence': 0.9
            }
        elif 'squat' in message or 'leg' in message:
            return {
                'text': "Squats are fantastic for building leg strength and glutes! Keep your back straight and knees behind your toes. Start with bodyweight squats before adding weight.",
                'confidence': 0.9
            }
        elif 'cardio' in message or 'weight loss' in message:
            return {
                'text': "For weight loss, combine strength training with cardio. HIIT workouts are especially effective - try 20-30 minutes of high-intensity intervals 3-4 times per week.",
                'confidence': 0.85
            }
        elif 'beginner' in message or 'start' in message:
            return {
                'text': "Great decision to start your fitness journey! Begin with 3 days per week of full-body workouts. Focus on basic exercises like squats, push-ups, and planks. Consistency is more important than intensity at first!",
                'confidence': 0.9
            }
        else:
            return {
                'text': random.choice(self.responses['exercise_advice']),
                'confidence': 0.7
            }
    
    def _generate_nutrition_advice(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Generate nutrition-related advice.
        """
        if 'protein' in message:
            return {
                'text': "Protein is crucial for muscle repair and growth! Aim for 1.6-2.2g per kg of bodyweight if you're strength training. Good sources include chicken, fish, eggs, Greek yogurt, and plant-based options like lentils and tofu.",
                'confidence': 0.9
            }
        elif 'calorie' in message:
            return {
                'text': "Calorie needs depend on your goals, activity level, and body composition. For weight loss, aim for a 500-calorie deficit daily. For muscle gain, aim for a 300-calorie surplus. Quality of calories matters just as much as quantity!",
                'confidence': 0.85
            }
        elif 'water' in message or 'hydration' in message:
            return {
                'text': "Stay hydrated! Aim for 2-3 liters of water daily, plus extra if you exercise. Proper hydration improves performance, recovery, and overall health. Your urine should be light yellow.",
                'confidence': 0.9
            }
        elif 'diet' in message or 'eat' in message:
            return {
                'text': "Focus on whole foods: lean proteins, complex carbs, healthy fats, and plenty of vegetables. Eat the rainbow for diverse nutrients. Remember, consistency beats perfection!",
                'confidence': 0.8
            }
        else:
            return {
                'text': random.choice(self.responses['nutrition_question']),
                'confidence': 0.7
            }
    
    def _generate_motivation_response(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Generate motivational response.
        """
        if 'tired' in message or 'can\'t' in message:
            return {
                'text': "It's okay to feel tired sometimes! Remember why you started. Even a 10-minute workout is better than none. Listen to your body, but don't let temporary feelings derail your long-term goals. You've got this!",
                'confidence': 0.9
            }
        elif 'progress' in message or 'results' in message:
            return {
                'text': "Progress takes time and consistency! Track your workouts, take progress photos, and celebrate small wins. Remember that fitness is a journey, not a destination. Every workout counts!",
                'confidence': 0.85
            }
        else:
            quote = random.choice(self.motivation_quotes)
            return {
                'text': f"{quote} Keep pushing forward - you're stronger than you think!",
                'confidence': 0.8
            }
    
    def _generate_progress_response(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Generate progress tracking advice.
        """
        if 'track' in message or 'measure' in message:
            return {
                'text': "Track your progress consistently! Take measurements, photos, and strength records every 2-4 weeks. Remember that the scale isn't everything - how you feel and how your clothes fit matter too!",
                'confidence': 0.9
            }
        elif 'plateau' in message or 'stuck' in message:
            return {
                'text': "Plateaus are normal! Try changing your routine, increasing intensity, or adjusting your nutrition. Sometimes a deload week or trying new exercises can break through plateaus. Stay patient and persistent!",
                'confidence': 0.85
            }
        else:
            return {
                'text': "Consistent tracking helps you see progress and stay motivated. Focus on trends rather than daily fluctuations. Celebrate your journey and how far you've come!",
                'confidence': 0.7
            }
    
    def _generate_medical_response(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Generate medical-related responses with appropriate disclaimers.
        """
        return {
            'text': "I can provide general fitness advice, but for medical concerns, please consult with a healthcare professional. They can provide personalized advice based on your specific health conditions and needs.",
            'confidence': 0.9
        }
    
    def _generate_greeting_response(self, message: str, metrics: HealthMetrics = None) -> Dict[str, Any]:
        """
        Generate greeting response.
        """
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
        """
        Generate general response when intent is unclear.
        """
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
    
    def _generate_suggestions(self, intent: str, metrics: HealthMetrics = None) -> List[str]:
        """
        Generate contextual suggestions based on intent and user metrics.
        """
        suggestions = []
        
        if intent == 'exercise_advice':
            suggestions.extend([
                "Ask about specific exercises",
                "Learn about workout routines",
                "Get form tips and techniques"
            ])
        elif intent == 'nutrition_question':
            suggestions.extend([
                "Ask about meal planning",
                "Learn about macronutrients",
                "Get healthy recipe ideas"
            ])
        elif intent == 'motivation':
            suggestions.extend([
                "Share your fitness goals",
                "Ask about overcoming challenges",
                "Get accountability tips"
            ])
        
        # Add personalized suggestions if metrics available
        if metrics:
            if metrics.fitness_goal == 'weight_loss':
                suggestions.append("Ask about fat loss strategies")
            elif metrics.fitness_goal == 'muscle_gain':
                suggestions.append("Learn about muscle building")
            elif metrics.fitness_goal == 'endurance':
                suggestions.append("Ask about stamina improvement")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _load_intents(self) -> Dict[str, List[str]]:
        """
        Load intent keywords for classification.
        """
        return {
            'exercise_advice': [
                'exercise', 'workout', 'training', 'fitness', 'gym', 'muscle',
                'strength', 'cardio', 'push', 'pull', 'squat', 'lift', 'routine'
            ],
            'nutrition_question': [
                'food', 'diet', 'eat', 'calories', 'protein', 'carbs', 'fat',
                'nutrition', 'meal', 'supplement', 'vitamin', 'water', 'hydration'
            ],
            'motivation': [
                'motivate', 'encourage', 'can\'t', 'tired', 'lazy', 'bored',
                'quit', 'give up', 'struggle', 'challenge', 'difficult'
            ],
            'progress_tracking': [
                'progress', 'results', 'track', 'measure', 'weight', 'plateau',
                'stuck', 'improvement', 'goals', 'achievement'
            ],
            'medical_question': [
                'pain', 'injury', 'hurt', 'medical', 'doctor', 'medicine',
                'condition', 'health', 'symptom', 'treatment'
            ],
            'greeting': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon',
                'good evening', 'thanks', 'thank you'
            ]
        }
    
    def _load_responses(self) -> Dict[str, List[str]]:
        """
        Load response templates for different intents.
        """
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
        """
        Load frequently asked questions and answers.
        """
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
            },
            {
                'keywords': ['build muscle', 'muscle gain', 'bulk'],
                'question': 'How do I build muscle effectively?',
                'answer': 'Build muscle through progressive strength training, adequate protein intake (1.6-2.2g per kg bodyweight), sufficient calories, and quality sleep. Consistency and patience are key!'
            },
            {
                'keywords': ['rest day', 'recovery', 'rest'],
                'question': 'How important are rest days?',
                'answer': 'Rest days are crucial! Your muscles repair and grow during rest. Take 1-2 rest days per week, and consider active recovery like walking or stretching on those days.'
            }
        ]
    
    def _load_motivation_quotes(self) -> List[str]:
        """
        Load motivational quotes.
        """
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
            "Sweat is just fat crying.",
            "Champions train, losers complain.",
            "The body achieves what the mind believes.",
            "Don't wish for it, work for it.",
            "Success isn't given. It's earned in the gym."
        ]
