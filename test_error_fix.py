#!/usr/bin/env python3
"""
Test script to check if the chatbot is working correctly and identify any issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import Chatbot
import uuid

def test_chatbot_functionality():
    """Test the chatbot functionality to identify any issues."""
    
    print("🔧 Testing Chatbot Functionality")
    print("=" * 50)
    
    try:
        # Initialize chatbot
        print("1. Initializing chatbot...")
        chatbot = Chatbot()
        print("✅ Chatbot initialized successfully!")
        
        # Test message processing
        print("\n2. Testing message processing...")
        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        
        test_messages = [
            "hello",
            "how are you",
            "what are your business hours",
            "I need help with my password"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   Testing message {i}: '{message}'")
            try:
                result = chatbot.process_message(user_id, message, session_id)
                
                print(f"   ✅ Success!")
                print(f"   Intent: {result['intent']}")
                print(f"   Confidence: {result['confidence']:.2f}")
                print(f"   Response: {result['response'][:100]}{'...' if len(result['response']) > 100 else ''}")
                
                # Check for errors in response
                if 'error' in result:
                    print(f"   ⚠️  Warning: Error field found: {result['error']}")
                
            except Exception as e:
                print(f"   ❌ Error processing message: {e}")
                return False
        
        # Test database operations
        print("\n3. Testing database operations...")
        try:
            history = chatbot.get_conversation_history(user_id, session_id, 10)
            print(f"   ✅ Retrieved {len(history)} messages from history")
        except Exception as e:
            print(f"   ❌ Error retrieving history: {e}")
        
        # Test health check
        print("\n4. Testing health check...")
        try:
            health = chatbot.health_check()
            print(f"   ✅ Health check passed: {health['status']}")
        except Exception as e:
            print(f"   ❌ Error in health check: {e}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        return False

if __name__ == "__main__":
    success = test_chatbot_functionality()
    if success:
        print("\n✅ Chatbot is working correctly!")
    else:
        print("\n❌ Chatbot has issues that need to be fixed!") 