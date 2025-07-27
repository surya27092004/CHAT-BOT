"""
Main Flask Application for Customer Support Chatbot

Provides web interface and API endpoints for the chatbot system.
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import uuid
import json
import os
from datetime import datetime
import threading

from chatbot import Chatbot

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SESSION_TYPE'] = 'filesystem'

# Enable CORS
CORS(app)

# Initialize chatbot
chatbot = None
chatbot_lock = threading.Lock()

def get_chatbot():
    """Get or create chatbot instance."""
    global chatbot
    if chatbot is None:
        with chatbot_lock:
            if chatbot is None:
                chatbot = Chatbot()
    return chatbot

@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')

@app.route('/test')
def test():
    """Serve the test page for debugging."""
    return render_template('test_web_interface.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return responses."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = data.get('user_id', str(uuid.uuid4()))
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({
                'error': 'Message is required',
                'response': 'Please provide a message.'
            }), 400
        
        # Get chatbot instance
        bot = get_chatbot()
        
        # Process message
        result = bot.process_message(user_id, message, session_id)
        
        return jsonify({
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
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'response': 'I apologize, but I encountered an error. Please try again.'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history for a user."""
    try:
        user_id = request.args.get('user_id')
        session_id = request.args.get('session_id')
        limit = int(request.args.get('limit', 50))
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        bot = get_chatbot()
        history = bot.get_conversation_history(user_id, session_id, limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
        
    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500

@app.route('/api/ticket', methods=['POST'])
def create_ticket():
    """Create a support ticket."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        subject = data.get('subject', '').strip()
        description = data.get('description', '').strip()
        priority = data.get('priority', 'medium')
        
        if not user_id or not subject or not description:
            return jsonify({
                'error': 'User ID, subject, and description are required'
            }), 400
        
        bot = get_chatbot()
        result = bot.create_support_ticket(user_id, subject, description, priority)
        
        return jsonify({
            'success': True,
            'ticket_id': result['ticket_id'],
            'message': result['message']
        })
        
    except Exception as e:
        print(f"Error creating ticket: {e}")
        return jsonify({'error': 'Failed to create ticket'}), 500

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Get support tickets for a user."""
    try:
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        bot = get_chatbot()
        tickets = bot.db.get_tickets(user_id, status, limit)
        
        return jsonify({
            'success': True,
            'tickets': tickets,
            'count': len(tickets)
        })
        
    except Exception as e:
        print(f"Error getting tickets: {e}")
        return jsonify({'error': 'Failed to retrieve tickets'}), 500

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get user profile and statistics."""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        bot = get_chatbot()
        profile = bot.get_user_profile(user_id)
        
        if not profile:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return jsonify({'error': 'Failed to retrieve user profile'}), 500

@app.route('/api/user/preferences', methods=['PUT'])
def update_user_preferences():
    """Update user preferences."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        preferences = data.get('preferences', {})
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        bot = get_chatbot()
        success = bot.update_user_preferences(user_id, preferences)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Preferences updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to update preferences'}), 500
        
    except Exception as e:
        print(f"Error updating preferences: {e}")
        return jsonify({'error': 'Failed to update preferences'}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get chatbot usage statistics."""
    try:
        days = int(request.args.get('days', 30))
        
        bot = get_chatbot()
        stats = bot.get_statistics(days)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        bot = get_chatbot()
        health = bot.health_check()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': health
        })
        
    except Exception as e:
        print(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation for a user."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        bot = get_chatbot()
        success = bot.reset_conversation(user_id, session_id)
        
        return jsonify({
            'success': success,
            'message': 'Conversation reset successfully' if success else 'Failed to reset conversation'
        })
        
    except Exception as e:
        print(f"Error in reset endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to reset conversation'
        }), 500

@app.route('/api/human-agent', methods=['POST'])
def human_agent_handoff():
    """Simulate human agent handoff with realistic conversation flow."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        bot = get_chatbot()
        
        # Get conversation context
        context = bot.get_conversation_history(user_id, session_id, 10)
        
        # Generate realistic human agent introduction
        human_intro = bot.response_manager.generate_human_agent_intro(context)
        
        # Store the human agent message in conversation history
        bot.database_manager.store_message(
            user_id=user_id,
            session_id=session_id,
            message=human_intro,
            sender='human_agent',
            intent='human_handoff',
            confidence=1.0,
            timestamp=datetime.now()
        )
        
        return jsonify({
            'success': True,
            'response': human_intro,
            'agent_type': 'human',
            'agent_name': 'Support Specialist',
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'message': 'Human agent has joined the conversation'
        })
        
    except Exception as e:
        print(f"Error in human agent handoff: {e}")
        return jsonify({
            'error': 'Internal server error',
            'response': 'I apologize, but there was an error connecting you to a human agent.'
        }), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_old_data():
    """Clean up old conversation data."""
    try:
        data = request.get_json()
        days = int(data.get('days', 90))
        
        bot = get_chatbot()
        deleted_count = bot.db.cleanup_old_data(days)
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} old records',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"Error cleaning up data: {e}")
        return jsonify({'error': 'Failed to cleanup data'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('database', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting Customer Support Chatbot...")
    
    # Get port from environment variable (for Render deployment)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )