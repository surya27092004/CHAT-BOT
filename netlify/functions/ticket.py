import json
import uuid
from datetime import datetime

def handler(event, context):
    """
    Netlify Function handler for support ticket creation
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
        
        # Extract ticket data
        user_id = body.get('user_id')
        subject = body.get('subject', '').strip()
        description = body.get('description', '').strip()
        priority = body.get('priority', 'medium')
        
        if not user_id or not subject or not description:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'User ID, subject, and description are required'
                })
            }
        
        # Generate ticket ID
        ticket_id = f"TKT-{str(uuid.uuid4())[:8].upper()}"
        
        # Create ticket response
        ticket = {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'subject': subject,
            'description': description,
            'priority': priority,
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'ticket': ticket,
                'message': f'Support ticket {ticket_id} has been created successfully. Our team will respond within 24 hours.'
            })
        }
        
    except Exception as e:
        print(f"Error in ticket function: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Failed to create support ticket. Please try again.'
            })
        }
