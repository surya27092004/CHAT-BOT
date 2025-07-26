"""
Database Management Module

Handles all database operations including conversation storage,
user management, and support ticket tracking.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading


class DatabaseManager:
    """
    Database manager for chatbot data storage.
    Handles conversations, users, tickets, and analytics.
    """
    
    def __init__(self, db_path: str = "database/chatbot.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        print("💾 Database Manager initialized!")
    
    def initialize_database(self):
        """Initialize database tables if they don't exist."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    intent TEXT,
                    confidence REAL,
                    entities TEXT,
                    sentiment TEXT
                )
            ''')
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_messages INTEGER DEFAULT 0,
                    preferences TEXT,
                    language TEXT DEFAULT 'en',
                    timezone TEXT
                )
            ''')
            
            # Create support tickets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'open',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    assigned_to TEXT,
                    category TEXT
                )
            ''')
            
            # Create analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_conversations INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    avg_response_time REAL,
                    satisfaction_score REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)')
            
            conn.commit()
            conn.close()
            
            print("✅ Database tables initialized successfully!")
    
    def store_message(self, user_id: str, session_id: str, message: str, 
                     sender: str, intent: str = None, confidence: float = None,
                     entities: Dict = None, sentiment: Dict = None):
        """
        Store a message in the database.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            message: Message content
            sender: 'user' or 'bot'
            intent: Detected intent
            confidence: Confidence score
            entities: Extracted entities
            sentiment: Sentiment analysis results
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store the message
            cursor.execute('''
                INSERT INTO conversations (user_id, session_id, message, sender, intent, confidence, entities, sentiment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, session_id, message, sender, intent, confidence,
                json.dumps(entities) if entities else None,
                json.dumps(sentiment) if sentiment else None
            ))
            
            # Update user statistics
            self._update_user_stats(user_id, cursor)
            
            conn.commit()
            conn.close()
    
    def _update_user_stats(self, user_id: str, cursor):
        """Update user statistics."""
        # Check if user exists
        cursor.execute('SELECT total_messages FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            # Update existing user
            cursor.execute('''
                UPDATE users 
                SET total_messages = total_messages + 1, last_seen = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
        else:
            # Create new user
            cursor.execute('''
                INSERT INTO users (user_id, total_messages)
                VALUES (?, 1)
            ''', (user_id,))
    
    def get_conversation_history(self, user_id: str, session_id: str = None, 
                               limit: int = 50) -> List[Dict]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User identifier
            session_id: Optional session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation messages
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT message, sender, timestamp, intent, confidence, entities, sentiment
                    FROM conversations
                    WHERE user_id = ? AND session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, session_id, limit))
            else:
                cursor.execute('''
                    SELECT message, sender, timestamp, intent, confidence, entities, sentiment
                    FROM conversations
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            conversations = []
            for row in results:
                conversations.append({
                    'message': row[0],
                    'sender': row[1],
                    'timestamp': row[2],
                    'intent': row[3],
                    'confidence': row[4],
                    'entities': json.loads(row[5]) if row[5] else None,
                    'sentiment': json.loads(row[6]) if row[6] else None
                })
            
            return conversations[::-1]  # Reverse to get chronological order
    
    def create_ticket(self, user_id: str, subject: str, description: str, 
                     priority: str = "medium", category: str = None) -> int:
        """
        Create a support ticket.
        
        Args:
            user_id: User identifier
            subject: Ticket subject
            description: Ticket description
            priority: Ticket priority (low, medium, high, urgent)
            category: Ticket category
            
        Returns:
            Ticket ID
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tickets (user_id, subject, description, priority, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, subject, description, priority, category))
            
            ticket_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return ticket_id
    
    def get_tickets(self, user_id: str = None, status: str = None, 
                   limit: int = 50) -> List[Dict]:
        """
        Get support tickets.
        
        Args:
            user_id: Optional user filter
            status: Optional status filter
            limit: Maximum number of tickets to return
            
        Returns:
            List of tickets
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM tickets WHERE 1=1'
            params = []
            
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)
            
            if status:
                query += ' AND status = ?'
                params.append(status)
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            tickets = []
            for row in results:
                tickets.append({
                    'ticket_id': row[0],
                    'user_id': row[1],
                    'subject': row[2],
                    'description': row[3],
                    'priority': row[4],
                    'status': row[5],
                    'created_at': row[6],
                    'updated_at': row[7],
                    'assigned_to': row[8],
                    'category': row[9]
                })
            
            return tickets
    
    def update_ticket_status(self, ticket_id: int, status: str, 
                           assigned_to: str = None) -> bool:
        """
        Update ticket status.
        
        Args:
            ticket_id: Ticket identifier
            status: New status
            assigned_to: Assigned agent
            
        Returns:
            Success status
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if assigned_to:
                    cursor.execute('''
                        UPDATE tickets 
                        SET status = ?, assigned_to = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE ticket_id = ?
                    ''', (status, assigned_to, ticket_id))
                else:
                    cursor.execute('''
                        UPDATE tickets 
                        SET status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE ticket_id = ?
                    ''', (status, ticket_id))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error updating ticket: {e}")
                return False
    
    def get_user_profile(self, user_id: str) -> Dict:
        """
        Get user profile and statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile dictionary
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user info
            cursor.execute('''
                SELECT first_seen, last_seen, total_messages, preferences, language, timezone
                FROM users WHERE user_id = ?
            ''', (user_id,))
            
            user_result = cursor.fetchone()
            
            if not user_result:
                conn.close()
                return None
            
            # Get recent conversations
            cursor.execute('''
                SELECT COUNT(*) FROM conversations WHERE user_id = ?
            ''', (user_id,))
            total_conversations = cursor.fetchone()[0]
            
            # Get tickets
            cursor.execute('''
                SELECT COUNT(*) FROM tickets WHERE user_id = ?
            ''', (user_id,))
            total_tickets = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'user_id': user_id,
                'first_seen': user_result[0],
                'last_seen': user_result[1],
                'total_messages': user_result[2],
                'preferences': json.loads(user_result[3]) if user_result[3] else {},
                'language': user_result[4],
                'timezone': user_result[5],
                'total_conversations': total_conversations,
                'total_tickets': total_tickets
            }
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            preferences: User preferences dictionary
            
        Returns:
            Success status
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users 
                    SET preferences = ?
                    WHERE user_id = ?
                ''', (json.dumps(preferences), user_id))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error updating user preferences: {e}")
                return False
    
    def get_statistics(self, days: int = 30) -> Dict:
        """
        Get chatbot usage statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Statistics dictionary
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Total messages
            cursor.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE timestamp >= ? AND timestamp <= ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            total_messages = cursor.fetchone()[0]
            
            # Unique users
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM conversations 
                WHERE timestamp >= ? AND timestamp <= ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            unique_users = cursor.fetchone()[0]
            
            # Total conversations (sessions)
            cursor.execute('''
                SELECT COUNT(DISTINCT session_id) FROM conversations 
                WHERE timestamp >= ? AND timestamp <= ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            total_conversations = cursor.fetchone()[0]
            
            # Open tickets
            cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "open"')
            open_tickets = cursor.fetchone()[0]
            
            # Average response time (simplified)
            cursor.execute('''
                SELECT AVG(confidence) FROM conversations 
                WHERE sender = 'bot' AND timestamp >= ? AND timestamp <= ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            avg_confidence = cursor.fetchone()[0] or 0.0
            
            conn.close()
            
            return {
                'period_days': days,
                'total_messages': total_messages,
                'unique_users': unique_users,
                'total_conversations': total_conversations,
                'open_tickets': open_tickets,
                'avg_confidence': round(avg_confidence, 3),
                'messages_per_user': round(total_messages / max(unique_users, 1), 2),
                'conversations_per_user': round(total_conversations / max(unique_users, 1), 2)
            }
    
    def cleanup_old_data(self, days: int = 90):
        """
        Clean up old conversation data.
        
        Args:
            days: Keep data from last N days
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                cursor.execute('''
                    DELETE FROM conversations 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                print(f"🧹 Cleaned up {deleted_count} old conversation records")
                return deleted_count
            except Exception as e:
                print(f"Error cleaning up old data: {e}")
                return 0
    
    def health_check(self) -> Dict:
        """Perform health check on database."""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Check record counts
                stats = {}
                for table in ['conversations', 'users', 'tickets']:
                    if table in tables:
                        cursor.execute(f'SELECT COUNT(*) FROM {table}')
                        stats[f'{table}_count'] = cursor.fetchone()[0]
                    else:
                        stats[f'{table}_count'] = 0
                
                conn.close()
                
                return {
                    'status': 'healthy',
                    'database_path': self.db_path,
                    'tables': tables,
                    'statistics': stats
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'database_path': self.db_path
            } 