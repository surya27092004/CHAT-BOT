import json
from datetime import datetime

def handler(event, context):
    """
    Netlify Function handler for health check
    """
    try:
        # Handle CORS preflight
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS'
                },
                'body': ''
            }
        
        # Only allow GET requests
        if event['httpMethod'] != 'GET':
            return {
                'statusCode': 405,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'status': 'healthy',
                'service': 'Customer Support Chatbot',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'uptime': 'Running on Netlify Functions',
                'environment': 'production'
            })
        }
        
    except Exception as e:
        print(f"Error in health function: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }
