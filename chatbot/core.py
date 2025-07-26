"""
Core Chatbot Engine

Main chatbot class that orchestrates NLP processing, response generation,
and database operations.
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .nlp import NLPProcessor
from .database import DatabaseManager
from .responses import ResponseManager


class Chatbot:
    """
    Main chatbot class that handles user interactions and coordinates
    all chatbot components.
    """
    
    def __init__(self, config_path: str = "data/config.json"):
        """
        Initialize the chatbot with all necessary components.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.nlp = NLPProcessor()
        self.db = DatabaseManager()
        self.response_manager = ResponseManager()
        
        # Conversation state
        self.conversations = {}
        self.lock = threading.Lock()
        
        # Initialize database
        self.db.initialize_database()
        
        print("🤖 Chatbot initialized successfully!")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                "name": "Customer Support Bot",
                "version": "1.0.0",
                "language": "en",
                "max_context_length": 10,
                "response_timeout": 5.0,
                "enable_sentiment": True,
                "enable_learning": True
            }
    
    def process_message(self, user_id: str, message: str, session_id: str = None) -> Dict:
        """
        Process a user message and generate a response.
        
        Args:
            user_id: Unique identifier for the user
            message: User's input message
            session_id: Session identifier for conversation tracking
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = f"{user_id}_{int(time.time())}"
            
            # Store user message
            self.db.store_message(user_id, session_id, message, "user")
            
            # Process message with NLP
            nlp_result = self.nlp.process_message(message)
            
            # Get conversation context
            context = self._get_conversation_context(user_id, session_id)
            
            # Generate response
            response_data = self.response_manager.generate_response(
                message, nlp_result, context, user_id
            )
            
            # Store bot response
            self.db.store_message(user_id, session_id, response_data['response'], "bot")
            
            # Update conversation state
            self._update_conversation_state(user_id, session_id, message, response_data)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return {
                'response': response_data['response'],
                'confidence': response_data.get('confidence', 0.8),
                'intent': nlp_result.get('intent', 'general'),
                'entities': nlp_result.get('entities', []),
                'session_id': session_id,
                'processing_time': round(processing_time, 3),
                'timestamp': datetime.now().isoformat(),
                'suggestions': response_data.get('suggestions', []),
                'requires_human': response_data.get('requires_human', False)
            }
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                'response': "I apologize, but I'm experiencing some technical difficulties. Please try again or contact our support team.",
                'confidence': 0.0,
                'intent': 'error',
                'session_id': session_id,
                'processing_time': round(time.time() - start_time, 3),
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_conversation_context(self, user_id: str, session_id: str) -> List[Dict]:
        """Get recent conversation context for the user."""
        with self.lock:
            if user_id not in self.conversations:
                self.conversations[user_id] = {}
            
            if session_id not in self.conversations[user_id]:
                self.conversations[user_id][session_id] = []
            
            return self.conversations[user_id][session_id][-self.config.get('max_context_length', 10):]
    
    def _update_conversation_state(self, user_id: str, session_id: str, 
                                 message: str, response_data: Dict):
        """Update conversation state with new message and response."""
        with self.lock:
            if user_id not in self.conversations:
                self.conversations[user_id] = {}
            
            if session_id not in self.conversations[user_id]:
                self.conversations[user_id][session_id] = []
            
            # Add message and response to context
            self.conversations[user_id][session_id].append({
                'message': message,
                'response': response_data['response'],
                'timestamp': datetime.now().isoformat(),
                'intent': response_data.get('intent', 'general')
            })
            
            # Keep only recent context
            max_length = self.config.get('max_context_length', 10)
            if len(self.conversations[user_id][session_id]) > max_length:
                self.conversations[user_id][session_id] = self.conversations[user_id][session_id][-max_length:]
    
    def get_conversation_history(self, user_id: str, session_id: str = None, limit: int = 50) -> List[Dict]:
        """Get conversation history for a user."""
        return self.db.get_conversation_history(user_id, session_id, limit)
    
    def create_support_ticket(self, user_id: str, subject: str, description: str, priority: str = "medium") -> Dict:
        """Create a support ticket for the user."""
        ticket_id = self.db.create_ticket(user_id, subject, description, priority)
        return {
            'ticket_id': ticket_id,
            'status': 'created',
            'message': f'Support ticket #{ticket_id} has been created successfully.'
        }
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile and preferences."""
        return self.db.get_user_profile(user_id)
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update user preferences."""
        return self.db.update_user_preferences(user_id, preferences)
    
    def get_statistics(self) -> Dict:
        """Get chatbot usage statistics."""
        return self.db.get_statistics()
    
    def reset_conversation(self, user_id: str, session_id: str):
        """Reset conversation context for a user session."""
        with self.lock:
            if user_id in self.conversations and session_id in self.conversations[user_id]:
                self.conversations[user_id][session_id] = []
    
    def health_check(self) -> Dict:
        """Perform health check on all components."""
        return {
            'status': 'healthy',
            'components': {
                'nlp': self.nlp.health_check(),
                'database': self.db.health_check(),
                'response_manager': self.response_manager.health_check()
            },
            'timestamp': datetime.now().isoformat()
        } 