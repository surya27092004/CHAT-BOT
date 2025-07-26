#!/usr/bin/env python3
"""
Demo script for realistic human agent handoff and conversation flow.
This demonstrates how the chatbot transitions to human agents with natural conversation.
"""

import requests
import json
import time
import uuid

# Configuration
BASE_URL = "http://localhost:5000"
USER_ID = f"demo_user_{uuid.uuid4().hex[:8]}"
SESSION_ID = f"demo_session_{uuid.uuid4().hex[:8]}"

def send_message(message):
    """Send a message to the chatbot."""
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            'message': message,
            'user_id': USER_ID,
            'session_id': SESSION_ID
        })
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def connect_human_agent():
    """Connect to a human agent."""
    try:
        response = requests.post(f"{BASE_URL}/api/human-agent", json={
            'user_id': USER_ID,
            'session_id': SESSION_ID
        })
        return response.json()
    except Exception as e:
        print(f"Error connecting to human agent: {e}")
        return None

def demo_realistic_conversation():
    """Demonstrate realistic conversation flow with human agent handoff."""
    print("🤖 Customer Support Chatbot - Realistic Conversation Demo")
    print("=" * 60)
    print()
    
    # Start with a greeting
    print("👤 User: Hi, how are you?")
    response = send_message("Hi, how are you?")
    if response and response.get('success'):
        print(f"🤖 Bot: {response['response']}")
    print()
    
    # Ask about a complex issue
    print("👤 User: I'm having a really urgent problem with my account. It's completely broken and I need immediate help!")
    response = send_message("I'm having a really urgent problem with my account. It's completely broken and I need immediate help!")
    if response and response.get('success'):
        print(f"🤖 Bot: {response['response']}")
    print()
    
    # Simulate escalation to human agent
    print("🔄 Connecting to human agent...")
    time.sleep(2)
    
    human_response = connect_human_agent()
    if human_response and human_response.get('success'):
        print(f"👨‍💼 Human Agent: {human_response['response']}")
    print()
    
    # Continue conversation with human agent
    print("👤 User: Thank you! Yes, I've been trying to reset my password for hours and nothing is working.")
    print("👨‍💼 Human Agent: I can see from the conversation that you're dealing with a password reset issue. Let me help you get this resolved.")
    print()
    
    print("👤 User: That would be amazing! I'm so frustrated right now.")
    print("👨‍💼 Human Agent: I completely understand your frustration. Let's get this sorted out for you right away. Can you tell me what happens when you try to reset your password?")
    print()
    
    print("✅ Demo completed! This shows how the chatbot:")
    print("   • Provides realistic, varied responses")
    print("   • Escalates complex issues naturally")
    print("   • Handles human agent handoff smoothly")
    print("   • Continues conversation contextually")
    print("   • Uses natural, human-like language")

if __name__ == "__main__":
    print("Starting realistic conversation demo...")
    print("Make sure your Flask app is running on http://localhost:5000")
    print()
    
    try:
        demo_realistic_conversation()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Make sure the Flask app is running and accessible.") 