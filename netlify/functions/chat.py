import json
import uuid
from datetime import datetime

def handler(event, context):
    # Handle CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '').lower()
        
        # Simple responses
        if 'hello' in message or 'hi' in message:
            response = "Hello! How can I help you today?"
        elif 'product' in message:
            response = "We offer great products and services. What would you like to know?"
        elif 'account' in message:
            response = "I can help with account issues. What do you need?"
        elif 'ticket' in message:
            response = "I can help create a support ticket. Please describe your issue."
        else:
            response = "I'm here to help! Can you tell me more about what you need?"
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'response': response,
                'user_id': body.get('user_id', 'user_123'),
                'session_id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'response': 'Sorry, I encountered an error. Please try again.'
            })
        }
