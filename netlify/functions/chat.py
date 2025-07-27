import json
import sys
import os
import uuid
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from chatbot import Chatbot
except ImportError:
    # Fallback chatbot implementation
    class Chatbot:
        def __init__(self):
            self.responses = {
                "greeting": [
                    "Hello! How can I help you today?",
                    "Hi there! What can I assist you with?",
                    "Welcome! How may I help you?"
                ],
                "products": [
                    "We offer a wide range of products including software solutions, consulting services, and technical support. What specific product are you interested in?"
                ],
                "account": [
                    "I can help you with account-related issues. Please describe what specific problem you're experiencing with your account."
                ],
                "hours": [
                    "Our business hours are Monday to Friday, 9 AM to 6 PM EST. For urgent issues, you can create a support ticket anytime."
                ],
                "ticket": [
                    "I can help you create a support ticket. Please provide details about your issue and I'll escalate it to our support team."
                ],
                "default": [
                    "I understand you need help. Could you please provide more details about your question?",
                    "I'm here to assist you. Can you tell me more about what you need help with?",
                    "Thank you for your message. Could you please elaborate on your request?"
                ]
            }
        
        def process_message(self, user_id, message, session_id=None):
            message_lower = message.lower()
            
            # Simple intent detection
            if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
                intent = 'greeting'
            elif any(word in message_lower for word in ['product', 'service', 'offer']):
                intent = 'products'
            elif any(word in message_lower for word in ['account', 'login', 'password']):
                intent = 'account'
            elif any(word in message_lower for word in ['hours', 'time', 'open']):
                intent = 'hours'
            elif any(word in message_lower for word in ['ticket', 'support', 'help']):
                intent = 'ticket'
            else:
                intent = 'default'
            
            response = self.responses[intent][0]  # Use first response for simplicity
            
            return {
                'response': response,
                'confidence': 0.8,
                'intent': intent,
                'session_id': session_id or str(uuid.uuid4()),
                'processing_time': 0.1,
                'timestamp': datetime.now().isoformat(),
                'suggestions': self._get_suggestions(intent),
                'requires_human': False,
                'entities': {}
            }
        
        def _get_suggestions(self, intent):
            suggestions = {
                'greeting': ['Tell me about your products', 'I need help with my account', 'What are your business hours?'],
                'products': ['Show me pricing', 'Technical specifications', 'Contact sales'],
                'account': ['Reset password', 'Update profile', 'Billing questions'],
                'default': ['Create support ticket', 'Talk to human agent', 'FAQ']
            }
            return suggestions.get(intent, [])

def handler(event, context):
    """
    Netlify Function handler for chat endpoint
    """
    try:
        # Handle CORS preflight
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': ''
            }
        
        # Only allow POST requests
        if event['httpMethod'] != 'POST':
            return {
                'statusCode': 405,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        # Parse request body
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Invalid JSON'})
            }
        
        # Extract message data
        message = body.get('message', '').strip()
        user_id = body.get('user_id', str(uuid.uuid4()))
        session_id = body.get('session_id')
        
        if not message:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Message is required',
                    'response': 'Please provide a message.'
                })
            }
        
        # Initialize chatbot
        chatbot = Chatbot()
        
        # Process message
        result = chatbot.process_message(user_id, message, session_id)
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'response': result['response'],
                'confidence': result['confidence'],
                'intent': result['intent'],
                'session_id': result['session_id'],
                'processing_time': result['processing_time'],
                'timestamp': result['timestamp'],
                'suggestions': result.get('suggestions', []),
                'requires_human': result.get('requires_human', False),
                'entities': result.get('entities', {}),
                'user_id': user_id
            })
        }
        
    except Exception as e:
        print(f"Error in chat function: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'response': 'I apologize, but I encountered an error. Please try again.'
            })
        }
