"""
Natural Language Processing Module

Handles text preprocessing, intent recognition, entity extraction,
and sentiment analysis for the chatbot.
"""

import re
import json
import nltk
from typing import Dict, List, Tuple, Optional
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data (uncomment if needed)
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

try:
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.sentiment import SentimentIntensityAnalyzer
except ImportError:
    print("Warning: NLTK components not available. Using fallback methods.")
    # Fallback tokenization
    def word_tokenize(text):
        return text.lower().split()
    
    def sent_tokenize(text):
        return text.split('.')
    
    stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
    
    class WordNetLemmatizer:
        def lemmatize(self, word):
            return word
    
    class SentimentIntensityAnalyzer:
        def polarity_scores(self, text):
            return {'neg': 0.0, 'neu': 0.5, 'pos': 0.0, 'compound': 0.0}


class NLPProcessor:
    """
    Natural Language Processing processor for chatbot.
    Handles text preprocessing, intent recognition, and entity extraction.
    """
    
    def __init__(self, intents_file: str = "data/intents.json"):
        """
        Initialize the NLP processor.
        
        Args:
            intents_file: Path to intents configuration file
        """
        self.intents = self._load_intents(intents_file)
        # Ensure greeting patterns are comprehensive
        if 'greeting' in self.intents:
            self.intents['greeting']['patterns'] = [
                "hello", "hi", "hey", "good morning", "good afternoon",
                "good evening", "how are you", "how are u", "how r u", "how's it going", "whats up", "what's up", "how do you do", "greetings", "sup", "yo"
            ]
        self.lemmatizer = WordNetLemmatizer()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Train the vectorizer with intent examples
        self._train_vectorizer()
        
        # Common entities and patterns
        self.entity_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'url': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'time': r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b',
            'number': r'\b\d+\b',
            'currency': r'\$\d+(?:\.\d{2})?',
            'percentage': r'\d+(?:\.\d+)?%'
        }
        
        print("🧠 NLP Processor initialized successfully!")
    
    def _load_intents(self, intents_file: str) -> Dict:
        """Load intents from JSON file."""
        try:
            with open(intents_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default intents
            return {
                "greeting": {
                    "patterns": [
                        "hello", "hi", "hey", "good morning", "good afternoon",
                        "good evening", "how are you", "what's up"
                    ],
                    "responses": ["Hello! How can I help you today?"]
                },
                "goodbye": {
                    "patterns": [
                        "bye", "goodbye", "see you", "see you later", "take care",
                        "have a good day", "farewell"
                    ],
                    "responses": ["Goodbye! Have a great day!"]
                },
                "help": {
                    "patterns": [
                        "help", "support", "assistance", "what can you do",
                        "how does this work", "i need help"
                    ],
                    "responses": ["I'm here to help! I can answer questions, create support tickets, and assist with various tasks."]
                },
                "thanks": {
                    "patterns": [
                        "thank you", "thanks", "appreciate it", "grateful",
                        "thank you so much"
                    ],
                    "responses": ["You're welcome! Is there anything else I can help you with?"]
                },
                "support_ticket": {
                    "patterns": [
                        "create ticket", "support ticket", "issue", "problem",
                        "bug report", "complaint", "technical issue"
                    ],
                    "responses": ["I can help you create a support ticket. What's the issue you're experiencing?"]
                },
                "product_info": {
                    "patterns": [
                        "product", "feature", "specification", "details",
                        "what is", "tell me about", "information"
                    ],
                    "responses": ["I'd be happy to provide product information. What specific details are you looking for?"]
                },
                "pricing": {
                    "patterns": [
                        "price", "cost", "pricing", "how much", "fee",
                        "subscription", "payment"
                    ],
                    "responses": ["I can help you with pricing information. What product or service are you interested in?"]
                }
            }
    
    def _train_vectorizer(self):
        """Train the TF-IDF vectorizer with intent patterns."""
        all_patterns = []
        for intent, data in self.intents.items():
            all_patterns.extend(data.get('patterns', []))
        
        if all_patterns:
            self.vectorizer.fit(all_patterns)
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text by cleaning and normalizing.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize_and_lemmatize(self, text: str) -> List[str]:
        """
        Tokenize text and lemmatize tokens.
        
        Args:
            text: Input text
            
        Returns:
            List of lemmatized tokens
        """
        try:
            tokens = word_tokenize(text)
            lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
            return [token for token in lemmatized if token not in stopwords.words('english')]
        except:
            # Fallback tokenization
            tokens = text.lower().split()
            return [token for token in tokens if token not in stopwords]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text using regex patterns.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entity types and their values
        """
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of the text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment scores
        """
        try:
            return self.sentiment_analyzer.polarity_scores(text)
        except:
            # Fallback sentiment analysis
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'satisfied']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'unhappy', 'angry', 'frustrated']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return {'compound': 0.5, 'pos': 0.5, 'neu': 0.3, 'neg': 0.2}
            elif negative_count > positive_count:
                return {'compound': -0.5, 'pos': 0.2, 'neu': 0.3, 'neg': 0.5}
            else:
                return {'compound': 0.0, 'pos': 0.3, 'neu': 0.4, 'neg': 0.3}
    
    def recognize_intent(self, text: str) -> Tuple[str, float]:
        """
        Recognize the intent of the user message.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        preprocessed_text = self.preprocess_text(text)
        text_lower = text.lower().strip()
        
        # First, check for exact matches with high confidence
        exact_greetings = [
            'hello', 'hi', 'hey', 'how are you', 'how are u', 'how r u', 
            "how's it going", 'whats up', "what's up", 'how do you do', 
            'greetings', 'sup', 'yo', 'good morning', 'good afternoon', 'good evening'
        ]
        
        if text_lower in exact_greetings:
            return 'greeting', 0.95
        
        # Check for greetings that start with these words
        greeting_starts = ['hello', 'hi', 'hey', 'how', 'whats', "what's", 'sup', 'yo']
        if any(text_lower.startswith(start) for start in greeting_starts):
            return 'greeting', 0.9
        
        # Check for exact goodbyes
        exact_goodbyes = ['bye', 'goodbye', 'see you', 'take care', 'farewell']
        if text_lower in exact_goodbyes:
            return 'goodbye', 0.95
        
        # Check for exact thanks
        exact_thanks = ['thank you', 'thanks', 'thank', 'appreciate it', 'grateful']
        if text_lower in exact_thanks:
            return 'thanks', 0.95
        
        # Check for business hours questions
        business_hours_words = ['business hours', 'hours', 'when are you open', 'what time', 'operating hours']
        if any(phrase in text_lower for phrase in business_hours_words):
            return 'business_hours', 0.9
        
        # Check for password reset questions
        password_words = ['password reset', 'forgot password', 'reset password', 'change password']
        if any(phrase in text_lower for phrase in password_words):
            return 'password_reset', 0.9
        
        # Check for contact/support questions
        contact_words = ['contact support', 'how to contact', 'support phone', 'support email']
        if any(phrase in text_lower for phrase in contact_words):
            return 'contact_support', 0.9
        
        # Vectorize the input text
        try:
            text_vector = self.vectorizer.transform([preprocessed_text])
        except:
            # Fallback: simple keyword matching
            return self._fallback_intent_recognition(text)
        
        best_intent = "general"
        best_score = 0.0
        
        # Compare with each intent's patterns
        for intent, data in self.intents.items():
            patterns = data.get('patterns', [])
            if patterns:
                try:
                    pattern_vectors = self.vectorizer.transform(patterns)
                    similarities = cosine_similarity(text_vector, pattern_vectors)
                    max_similarity = np.max(similarities)
                    
                    if max_similarity > best_score:
                        best_score = max_similarity
                        best_intent = intent
                except:
                    continue
        
        # Boost confidence for certain intents if we have a reasonable match
        if best_intent in ['greeting', 'goodbye', 'thanks'] and best_score > 0.3:
            best_score = min(0.9, best_score + 0.3)
        
        return best_intent, best_score
    
    def _fallback_intent_recognition(self, text: str) -> Tuple[str, float]:
        """Fallback intent recognition using keyword matching."""
        text_lower = text.lower()
        
        intent_keywords = {
            'greeting': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
                'how are you', 'how are u', 'how r u', "how's it going", 'whats up', "what's up",
                'how do you do', 'greetings', 'sup', 'yo'
            ],
            'goodbye': ['bye', 'goodbye', 'see you', 'take care'],
            'help': ['help', 'support', 'assistance'],
            'thanks': ['thank', 'thanks', 'appreciate'],
            'support_ticket': ['ticket', 'issue', 'problem', 'bug', 'complaint'],
            'product_info': ['product', 'feature', 'specification'],
            'pricing': ['price', 'cost', 'how much', 'pricing']
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent, 0.8
        
        return "general", 0.5
    
    def process_message(self, message: str) -> Dict:
        """
        Process a complete message and return comprehensive analysis.
        
        Args:
            message: User's input message
            
        Returns:
            Dictionary containing intent, entities, sentiment, and other analysis
        """
        # Preprocess text
        preprocessed = self.preprocess_text(message)
        
        # Tokenize and lemmatize
        tokens = self.tokenize_and_lemmatize(preprocessed)
        
        # Recognize intent
        intent, confidence = self.recognize_intent(message)
        
        # Extract entities
        entities = self.extract_entities(message)
        
        # Analyze sentiment
        sentiment = self.analyze_sentiment(message)
        
        return {
            'original_text': message,
            'preprocessed_text': preprocessed,
            'tokens': tokens,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'sentiment': sentiment,
            'word_count': len(tokens),
            'has_question': '?' in message,
            'is_urgent': self._detect_urgency(message)
        }
    
    def _detect_urgency(self, text: str) -> bool:
        """Detect if the message indicates urgency."""
        urgent_keywords = ['urgent', 'emergency', 'asap', 'immediately', 'critical', 'broken', 'down']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in urgent_keywords)
    
    def get_suggestions(self, intent: str) -> List[str]:
        """Get suggested follow-up questions based on intent."""
        suggestions = {
            'greeting': [
                "How can I help you today?",
                "What would you like to know about our services?",
                "Do you need help with something specific?"
            ],
            'help': [
                "I can help you with product information, pricing, or creating support tickets.",
                "What specific area do you need assistance with?",
                "Would you like me to create a support ticket for you?"
            ],
            'support_ticket': [
                "What type of issue are you experiencing?",
                "Can you provide more details about the problem?",
                "What is the priority level of this issue?"
            ],
            'product_info': [
                "Which product are you interested in?",
                "What specific features would you like to know about?",
                "Would you like pricing information as well?"
            ],
            'pricing': [
                "Which product or service are you interested in?",
                "Are you looking for individual or enterprise pricing?",
                "Would you like to see our current promotions?"
            ]
        }
        
        return suggestions.get(intent, ["Is there anything else I can help you with?"])
    
    def health_check(self) -> Dict:
        """Perform health check on NLP components."""
        return {
            'status': 'healthy',
            'components': {
                'vectorizer': 'initialized',
                'lemmatizer': 'initialized',
                'sentiment_analyzer': 'initialized',
                'intents_loaded': len(self.intents)
            },
            'intents_available': list(self.intents.keys())
        } 