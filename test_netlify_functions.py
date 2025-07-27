#!/usr/bin/env python3
"""
Test script to verify Netlify Functions are working correctly
"""

import json
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(__file__))

def test_chat_function():
    """Test the chat function"""
    try:
        # Import the chat function
        from netlify.functions.chat import handler
        
        # Create a test event
        test_event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'message': 'Hello, how are you?',
                'user_id': 'test_user_123'
            })
        }
        
        # Call the function
        result = handler(test_event, {})
        
        print("✅ Chat Function Test:")
        print(f"Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"Response: {body.get('response', 'No response')}")
            print(f"Intent: {body.get('intent', 'No intent')}")
            return True
        else:
            print(f"Error: {result['body']}")
            return False
            
    except Exception as e:
        print(f"❌ Chat Function Test Failed: {e}")
        return False

def test_ticket_function():
    """Test the ticket function"""
    try:
        from netlify.functions.ticket import handler
        
        test_event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'user_id': 'test_user_123',
                'subject': 'Test Ticket',
                'description': 'This is a test ticket',
                'priority': 'medium'
            })
        }
        
        result = handler(test_event, {})
        
        print("\n✅ Ticket Function Test:")
        print(f"Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"Ticket ID: {body.get('ticket', {}).get('ticket_id', 'No ticket ID')}")
            return True
        else:
            print(f"Error: {result['body']}")
            return False
            
    except Exception as e:
        print(f"❌ Ticket Function Test Failed: {e}")
        return False

def test_health_function():
    """Test the health function"""
    try:
        from netlify.functions.health import handler
        
        test_event = {
            'httpMethod': 'GET'
        }
        
        result = handler(test_event, {})
        
        print("\n✅ Health Function Test:")
        print(f"Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"Status: {body.get('status', 'No status')}")
            return True
        else:
            print(f"Error: {result['body']}")
            return False
            
    except Exception as e:
        print(f"❌ Health Function Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Netlify Functions...")
    print("=" * 50)
    
    tests = [
        test_health_function,
        test_chat_function,
        test_ticket_function
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Netlify Functions are ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
