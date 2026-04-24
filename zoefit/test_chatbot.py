#!/usr/bin/env python
"""
Test script to verify AI chatbot functionality
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
django.setup()

from ai_features.chatbot import EnhancedAIChatbot
from django.conf import settings

def test_chatbot():
    """Test the AI chatbot functionality"""
    print("=== AI CHATBOT TEST ===")
    
    # Check environment variables
    print(f"OpenAI API Key: {'✅ Present' if getattr(settings, 'OPENAI_API_KEY', None) else '❌ Missing'}")
    print(f"Gemini API Key: {'✅ Present' if getattr(settings, 'GEMINI_API_KEY', None) else '❌ Missing'}")
    print(f"AI Provider Preference: {getattr(settings, 'AI_PROVIDER_PREFERENCE', 'auto')}")
    
    # Initialize chatbot
    try:
        chatbot = EnhancedAIChatbot(ai_provider='auto')
        print(f"\nChatbot initialized successfully")
        print(f"OpenAI client: {'✅ Available' if chatbot.openai_client else '❌ Not available'}")
        print(f"Gemini client: {'✅ Available' if chatbot.gemini_model else '❌ Not available'}")
        
        # Test a simple message
        test_message = "What are the best exercises for beginners?"
        print(f"\nTesting message: '{test_message}'")
        
        response = chatbot.process_message(test_message, None, [])
        
        print(f"\nResponse received:")
        print(f"Text: {response.get('text', 'No text')[:200]}...")
        print(f"Intent: {response.get('intent', 'No intent')}")
        print(f"Confidence: {response.get('confidence', 0)}")
        print(f"Provider: {response.get('ai_provider', 'unknown')}")
        
        # Check if AI was used
        if response.get('ai_provider') in ['openai', 'gemini']:
            print("✅ AI response generated successfully!")
        else:
            print("❌ Fell back to rule-based response")
            
    except Exception as e:
        print(f"❌ Error testing chatbot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chatbot()
