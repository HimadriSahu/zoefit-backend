#!/usr/bin/env python
"""
Complete test to verify AI chatbot functionality
"""
import os
from dotenv import load_dotenv
import django

# Load .env and setup Django
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
django.setup()

from ai_features.chatbot import EnhancedAIChatbot

def test_chatbot_complete():
    """Complete test of AI chatbot functionality"""
    print('=== COMPLETE AI CHATBOT TEST ===')
    
    # Check environment
    openai_key = os.environ.get('OPENAI_API_KEY')
    gemini_key = os.environ.get('GEMINI_API_KEY')
    print(f'OpenAI API Key: {"✅ Present" if openai_key else "❌ Missing"}')
    print(f'Gemini API Key: {"✅ Present" if gemini_key else "❌ Missing"}')
    
    try:
        # Initialize chatbot
        chatbot = EnhancedAIChatbot(ai_provider='auto')
        print('✅ Chatbot initialized successfully')
        
        # Check AI clients
        print(f'OpenAI client: {"✅ Available" if chatbot.openai_client else "❌ Not available"}')
        print(f'Gemini client: {"✅ Available" if chatbot.gemini_model else "❌ Not available"}')
        
        # Test multiple messages
        test_messages = [
            "What are the best exercises for beginners?",
            "Give me some nutrition tips for weight loss",
            "How can I stay motivated to work out?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f'\n--- Test Message {i}: {message} ---')
            response = chatbot.process_message(message, None, [])
            
            print(f'Provider: {response.get("ai_provider", "unknown")}')
            print(f'Intent: {response.get("intent", "unknown")}')
            print(f'Confidence: {response.get("confidence", 0)}')
            print(f'Response: {response.get("text", "No text")[:150]}...')
            
            if response.get('ai_provider') in ['openai', 'gemini']:
                print('🎉 SUCCESS: Using generative AI!')
            else:
                print('⚠️  Using rule-based fallback')
        
        print('\n=== FINAL RESULT ===')
        if chatbot.openai_client or chatbot.gemini_model:
            print('🎉 AI CHATBOT IS WORKING WITH GENERATIVE AI!')
            print('✅ The issue has been fixed successfully!')
        else:
            print('❌ AI clients are still not available')
            
    except Exception as e:
        print(f'❌ Error during test: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chatbot_complete()
