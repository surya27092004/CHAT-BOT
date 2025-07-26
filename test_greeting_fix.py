#!/usr/bin/env python3
"""
Test script to verify greeting recognition and response generation fixes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import Chatbot
import uuid

def test_greeting_responses():
    """Test various greeting messages to ensure they get proper responses."""
    
    print("🧪 Testing Greeting Recognition and Responses")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = Chatbot()
    
    # Test cases
    test_cases = [
        "how are you",
        "hi",
        "hello",
        "hey",
        "how r u",
        "whats up",
        "good morning",
        "good afternoon",
        "how's it going",
        "random unrelated message",
        "I need help with my password",
        "what are your business hours"
    ]
    
    user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{message}'")
        print("-" * 30)
        
        try:
            result = chatbot.process_message(user_id, message, session_id)
            
            print(f"Intent: {result['intent']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Response: {result['response']}")
            
            # Check if greeting got proper response
            if 'how are you' in message.lower() or message.lower() in ['hi', 'hello', 'hey']:
                if result['intent'] != 'greeting':
                    print("❌ ERROR: Greeting not recognized!")
                elif 'password' in result['response'].lower():
                    print("❌ ERROR: Greeting got password reset response!")
                else:
                    print("✅ SUCCESS: Greeting recognized and responded correctly!")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_greeting_responses() 