#!/usr/bin/env python3
"""
Demo script for Customer Support Chatbot

This script provides a command-line interface to test the chatbot functionality.
"""

import sys
import time
from chatbot import Chatbot

def print_banner():
    """Print the demo banner."""
    print("=" * 60)
    print("🤖 Customer Support Chatbot Demo")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the demo")
    print("Type 'help' for available commands")
    print("=" * 60)
    print()

def print_help():
    """Print help information."""
    print("\nAvailable commands:")
    print("  help          - Show this help message")
    print("  quit/exit     - Exit the demo")
    print("  clear         - Clear conversation history")
    print("  stats         - Show chatbot statistics")
    print("  health        - Show system health")
    print("  ticket        - Create a support ticket")
    print("  history       - Show conversation history")
    print("\nOr just type your message to chat with the bot!")
    print()

def demo_chat():
    """Run the interactive chat demo."""
    print_banner()
    
    # Initialize chatbot
    try:
        bot = Chatbot()
        print("✅ Chatbot initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        return
    
    # Generate a demo user ID
    user_id = f"demo_user_{int(time.time())}"
    session_id = f"demo_session_{int(time.time())}"
    
    print(f"👤 Demo User ID: {user_id}")
    print(f"🆔 Session ID: {session_id}")
    print()
    
    # Start conversation
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye! Thanks for trying the chatbot demo!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'clear':
                bot.reset_conversation(user_id, session_id)
                print("🗑️  Conversation history cleared!")
                continue
            elif user_input.lower() == 'stats':
                stats = bot.get_statistics()
                print("\n📊 Chatbot Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()
                continue
            elif user_input.lower() == 'health':
                health = bot.health_check()
                print("\n🏥 System Health:")
                print(f"  Status: {health['status']}")
                for component, status in health['components'].items():
                    print(f"  {component}: {status}")
                print()
                continue
            elif user_input.lower() == 'ticket':
                print("\n🎫 Creating Support Ticket Demo:")
                subject = input("Subject: ").strip()
                description = input("Description: ").strip()
                priority = input("Priority (low/medium/high/urgent) [medium]: ").strip() or "medium"
                
                if subject and description:
                    result = bot.create_support_ticket(user_id, subject, description, priority)
                    print(f"✅ Ticket created: #{result['ticket_id']}")
                else:
                    print("❌ Subject and description are required")
                print()
                continue
            elif user_input.lower() == 'history':
                history = bot.get_conversation_history(user_id, session_id)
                print(f"\n📜 Conversation History ({len(history)} messages):")
                for i, msg in enumerate(history[-10:], 1):  # Show last 10 messages
                    sender = "Bot" if msg['sender'] == 'bot' else "You"
                    print(f"  {i}. {sender}: {msg['message'][:50]}{'...' if len(msg['message']) > 50 else ''}")
                print()
                continue
            elif not user_input:
                continue
            
            # Process message
            print("🤖 Bot is thinking...")
            start_time = time.time()
            
            result = bot.process_message(user_id, user_input, session_id)
            
            processing_time = time.time() - start_time
            
            # Display response
            print(f"\n🤖 Bot: {result['response']}")
            print(f"⏱️  Processing time: {result['processing_time']:.3f}s")
            print(f"🎯 Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
            
            if result.get('entities'):
                print(f"🏷️  Entities: {result['entities']}")
            
            if result.get('suggestions'):
                print(f"💡 Suggestions: {', '.join(result['suggestions'])}")
            
            if result.get('requires_human'):
                print("🚨 This conversation requires human intervention")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for assistance.\n")

def test_scenarios():
    """Run predefined test scenarios."""
    print("🧪 Running Test Scenarios...")
    print()
    
    bot = Chatbot()
    user_id = "test_user"
    session_id = "test_session"
    
    test_messages = [
        "Hello",
        "How do I reset my password?",
        "What are your business hours?",
        "I need help with billing",
        "Tell me about your products",
        "Create a support ticket",
        "What payment methods do you accept?",
        "Thank you for your help",
        "Goodbye"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: '{message}'")
        result = bot.process_message(user_id, message, session_id)
        print(f"Response: {result['response'][:100]}{'...' if len(result['response']) > 100 else ''}")
        print(f"Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        print("-" * 50)
        time.sleep(1)  # Small delay between tests
    
    print("✅ Test scenarios completed!")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            test_scenarios()
        else:
            print("Usage: python demo.py [test]")
            print("  test - Run predefined test scenarios")
    else:
        demo_chat()

if __name__ == "__main__":
    main() 