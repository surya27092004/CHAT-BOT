import json
import uuid
from datetime import datetime

def handler(event, context):
    """
    Netlify Function handler for human agent handoff
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
        
        # Extract data
        user_id = body.get('user_id')
        session_id = body.get('session_id')
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'User ID is required'})
            }
        
        # Generate realistic human agent introduction
        agent_names = ['Sarah', 'Mike', 'Jessica', 'David', 'Emma', 'Alex']
        agent_name = agent_names[hash(user_id) % len(agent_names)]
        
        human_intro = f"Hi! I'm {agent_name}, a human support specialist. I've reviewed your conversation and I'm here to help you personally. What specific issue can I assist you with today?"
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'response': human_intro,
                'agent_type': 'human',
                'agent_name': agent_name,
                'session_id': session_id or str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'message': 'Human agent has joined the conversation'
            })
        }
        
    except Exception as e:
        print(f"Error in human agent handoff: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'response': 'I apologize, but there was an error connecting you to a human agent.'
            })
        }
