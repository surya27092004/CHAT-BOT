"""
Response Management Module

Handles response generation based on user intent, context, and
knowledge base. Manages conversation flow and provides intelligent responses.
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ResponseManager:
    """
    Manages response generation for the chatbot.
    Handles different intents, context awareness, and dynamic responses.
    """
    
    def __init__(self, knowledge_base_path: str = "data/knowledge_base.json",
                 responses_path: str = "data/responses.json"):
        """
        Initialize the response manager.
        
        Args:
            knowledge_base_path: Path to knowledge base file
            responses_path: Path to response templates file
        """
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.response_templates = self._load_response_templates(responses_path)
        
        # Conversation state tracking
        self.conversation_states = {}
        
        print("💬 Response Manager initialized successfully!")
    
    def _load_knowledge_base(self, path: str) -> Dict:
        """Load knowledge base from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default knowledge base
            return {
                "faqs": [
                    {
                        "question": "How do I reset my password?",
                        "answer": "To reset your password, go to the login page and click 'Forgot Password'. Enter your email address and follow the instructions sent to your email.",
                        "keywords": ["password", "reset", "forgot", "login"],
                        "category": "account"
                    },
                    {
                        "question": "What are your business hours?",
                        "answer": "Our customer support is available Monday through Friday, 9 AM to 6 PM EST. For urgent issues, you can create a support ticket anytime.",
                        "keywords": ["hours", "business", "support", "time", "available"],
                        "category": "support"
                    },
                    {
                        "question": "How do I contact customer support?",
                        "answer": "You can contact our customer support team by creating a support ticket through this chat, calling us at 1-800-SUPPORT, or emailing support@company.com.",
                        "keywords": ["contact", "support", "help", "phone", "email"],
                        "category": "support"
                    },
                    {
                        "question": "What payment methods do you accept?",
                        "answer": "We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers for enterprise customers.",
                        "keywords": ["payment", "credit card", "paypal", "money", "billing"],
                        "category": "billing"
                    },
                    {
                        "question": "How do I cancel my subscription?",
                        "answer": "To cancel your subscription, go to your account settings and click on 'Subscription Management'. You can cancel anytime, and you'll have access until the end of your current billing period.",
                        "keywords": ["cancel", "subscription", "billing", "account"],
                        "category": "billing"
                    }
                ],
                "products": [
                    {
                        "name": "Basic Plan",
                        "description": "Perfect for individuals and small teams",
                        "price": "$9.99/month",
                        "features": ["Basic features", "Email support", "5GB storage"],
                        "category": "subscription"
                    },
                    {
                        "name": "Pro Plan",
                        "description": "Advanced features for growing businesses",
                        "price": "$29.99/month",
                        "features": ["All Basic features", "Priority support", "50GB storage", "Advanced analytics"],
                        "category": "subscription"
                    },
                    {
                        "name": "Enterprise Plan",
                        "description": "Custom solutions for large organizations",
                        "price": "Contact sales",
                        "features": ["All Pro features", "Dedicated support", "Unlimited storage", "Custom integrations"],
                        "category": "subscription"
                    }
                ],
                "categories": {
                    "account": "Account management and settings",
                    "support": "Technical support and troubleshooting",
                    "billing": "Payment, pricing, and subscription questions",
                    "product": "Product features and capabilities",
                    "general": "General inquiries and information"
                }
            }
    
    def _load_response_templates(self, path: str) -> Dict:
        """Load response templates from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default response templates
            return {
                "greeting": [
                    "Hello! 👋 How can I help you today?",
                    "Hi there! Welcome to our customer support. What can I assist you with?",
                    "Greetings! I'm here to help. What would you like to know?",
                    "Welcome! How may I be of service to you today?"
                ],
                "goodbye": [
                    "Goodbye! Have a wonderful day! 👋",
                    "Thank you for chatting with us. Take care!",
                    "See you later! Feel free to return if you need more help.",
                    "Have a great day! Don't hesitate to reach out if you need assistance."
                ],
                "thanks": [
                    "You're welcome! 😊 Is there anything else I can help you with?",
                    "My pleasure! Let me know if you need any further assistance.",
                    "Happy to help! What else can I do for you?",
                    "You're very welcome! Feel free to ask if you have more questions."
                ],
                "help": [
                    "I'm here to help! I can assist you with:\n• Product information and pricing\n• Account management\n• Technical support\n• Creating support tickets\n\nWhat would you like to know?",
                    "I can help you with various topics including product information, account issues, technical support, and more. What specific area do you need assistance with?",
                    "I'm your virtual assistant! I can answer questions, provide information, and help you create support tickets. What can I help you with today?"
                ],
                "fallback": [
                    "I'm not sure I understand. Could you please rephrase that or ask me something else?",
                    "I didn't quite catch that. Can you try asking in a different way?",
                    "I'm still learning and that's a bit unclear to me. Could you try asking something else?",
                    "I'm not sure how to respond to that. Can you ask me about our products, services, or if you need help with something specific?"
                ],
                "escalation": [
                    "I understand this is important. Let me connect you with a human agent who can better assist you.",
                    "This seems like a complex issue that would be better handled by our support team. I'll create a ticket for you.",
                    "I want to make sure you get the best possible help. Let me escalate this to our support team."
                ],
                "unrelated_message": [
                    "I'm not sure I understand what you're asking. Could you please rephrase that or ask me about our products, services, account help, or technical support?",
                    "I didn't quite catch that. Can you try asking in a different way?",
                    "I'm still learning and that's a bit unclear to me. Could you try asking something else?"
                ],
                "unclear_intent": [
                    "I want to make sure I help you correctly. Could you please be more specific about what you need help with? I can assist with product information, account issues, technical support, billing, or creating support tickets."
                ]
            }
    
    def generate_response(self, message: str, nlp_result: Dict, context: List[Dict], 
                         user_id: str) -> Dict:
        """
        Generate an appropriate response based on the message and context.
        """
        intent = nlp_result.get('intent', 'general')
        confidence = nlp_result.get('confidence', 0.0)
        entities = nlp_result.get('entities', {})
        sentiment = nlp_result.get('sentiment', {})
        
        # Check if we need to escalate to human
        if self._should_escalate(message, nlp_result, context):
            return self._generate_escalation_response(user_id, message)
        
        # Handle specific intents with high priority
        if intent in ['greeting', 'goodbye', 'thanks', 'help']:
            response = self._get_template_response(intent)
        elif intent == 'support_ticket':
            response = self._handle_support_ticket_request(message, user_id)
        elif intent == 'product_info':
            response = self._handle_product_inquiry(message, entities)
        elif intent == 'pricing':
            response = self._handle_pricing_inquiry(message, entities)
        elif intent == 'account_help':
            response = self._get_template_response('account_help')
        elif intent == 'technical_support':
            response = self._get_template_response('technical_support')
        elif intent == 'billing_help':
            response = self._get_template_response('billing_help')
        elif intent in ['business_hours', 'password_reset', 'contact_support']:
            # For specific FAQ intents, try to find the matching FAQ
            faq_response = self._find_faq_for_intent(intent, message)
            if faq_response:
                response = faq_response
            else:
                response = self._get_template_response('fallback')
        else:
            # For general/unrelated queries, try FAQ first with very strict matching
            faq_response = self._find_faq_match(message)
            if faq_response and confidence > 0.7:  # Only use FAQ if confidence is high
                response = faq_response
            else:
                # If no good match found, provide a helpful fallback
                response = self._get_unrelated_response(message, intent, confidence)
        
        # Add suggestions based on intent
        suggestions = self._generate_suggestions(intent, context)
        
        # Determine if human intervention is needed
        requires_human = self._check_if_human_needed(message, nlp_result, context)
        
        return {
            'response': response,
            'confidence': confidence,
            'intent': intent,
            'suggestions': suggestions,
            'requires_human': requires_human,
            'entities': entities,
            'sentiment': sentiment
        }
    
    def _get_unrelated_response(self, message: str, intent: str, confidence: float) -> str:
        """Generate a response for unrelated or unclear messages."""
        message_lower = message.lower()
        
        # Check if it's a greeting that wasn't properly recognized
        greeting_words = ['hello', 'hi', 'hey', 'how are you', 'how r u', 'how\'s it going', 'whats up']
        if any(word in message_lower for word in greeting_words):
            return self._get_template_response('greeting')
        
        # Check if it's a goodbye that wasn't properly recognized
        goodbye_words = ['bye', 'goodbye', 'see you', 'take care', 'farewell']
        if any(word in message_lower for word in goodbye_words):
            return self._get_template_response('goodbye')
        
        # Check if it's a thank you that wasn't properly recognized
        thanks_words = ['thank', 'thanks', 'appreciate', 'grateful']
        if any(word in message_lower for word in thanks_words):
            return self._get_template_response('thanks')
        
        # For truly unrelated messages, provide helpful guidance
        if confidence < 0.3:
            return self._get_template_response('unrelated_message')
        
        # For messages with some confidence but unclear intent
        return self._get_template_response('unclear_intent')
    
    def _should_escalate(self, message: str, nlp_result: Dict, context: List[Dict]) -> bool:
        """Determine if the conversation should be escalated to a human."""
        # Check for urgent keywords
        urgent_words = ['urgent', 'emergency', 'critical', 'broken', 'down', 'not working']
        if any(word in message.lower() for word in urgent_words):
            return True
        
        # Check sentiment
        sentiment = nlp_result.get('sentiment', {})
        if sentiment.get('compound', 0) < -0.5:  # Very negative sentiment
            return True
        
        # Check if user is frustrated (repeated questions)
        if len(context) > 3:
            recent_messages = [ctx['message'] for ctx in context[-3:] if ctx.get('sender') == 'user']
            if len(set(recent_messages)) == 1:  # Same message repeated
                return True
        
        return False
    
    def _generate_escalation_response(self, user_id: str, message: str) -> str:
        """Generate response for escalation to human agent."""
        # First, give the escalation message
        escalation_templates = self.response_templates.get('escalation', [
            "I understand this is important and I want to make sure you get the best help possible. Let me connect you with one of our support specialists who can give you their full attention."
        ])
        
        response = random.choice(escalation_templates)
        
        # Add handoff message
        handoff_templates = self.response_templates.get('human_agent_handoff', [
            "Perfect! I'm connecting you with our support specialist now. They'll be with you in just a moment."
        ])
        
        response += f"\n\n{random.choice(handoff_templates)}"
        response += f"\n\nI've created a support ticket for you. A human agent will contact you shortly."
        
        return response
    
    def generate_human_agent_intro(self, context: List[Dict]) -> str:
        """Generate a realistic human agent introduction that continues the conversation naturally."""
        # Get a random human agent intro
        intro_templates = self.response_templates.get('human_agent_intro', [
            "Hi there! I'm Sarah from the support team. I can see you've been chatting with our AI assistant. How can I help you today?"
        ])
        
        intro = random.choice(intro_templates)
        
        # Add context-aware continuation if we have conversation history
        if context and len(context) > 0:
            continuation_templates = self.response_templates.get('human_agent_continuation', [
                "I can see from the conversation that you're dealing with an issue. Let me help you get this resolved."
            ])
            
            # Try to extract the main issue from context
            recent_messages = [ctx.get('message', '') for ctx in context[-3:] if ctx.get('sender') == 'user']
            if recent_messages:
                # Find common keywords to identify the issue
                issue_keywords = {
                    'password': 'password reset issue',
                    'billing': 'billing concern',
                    'technical': 'technical problem',
                    'account': 'account issue',
                    'payment': 'payment problem',
                    'subscription': 'subscription matter',
                    'support': 'support request'
                }
                
                issue_type = 'this issue'
                for keyword, issue_desc in issue_keywords.items():
                    if any(keyword in msg.lower() for msg in recent_messages):
                        issue_type = issue_desc
                        break
                
                continuation = random.choice(continuation_templates).replace('[issue]', issue_type)
                intro += f"\n\n{continuation}"
        
        return intro
    
    def _get_template_response(self, intent: str) -> str:
        """Get a random response template for the given intent. Always returns a valid fallback if nothing else matches."""
        templates = self.response_templates.get(intent)
        if not templates or not isinstance(templates, list) or len(templates) == 0:
            # Always return a default fallback if nothing else matches
            return "I'm not sure I understand. Could you please rephrase that or ask me something else?"
        return random.choice(templates)
    
    def _handle_support_ticket_request(self, message: str, user_id: str) -> str:
        """Handle support ticket creation requests."""
        response = "I can help you create a support ticket. "
        
        # Check if user provided details
        if len(message.split()) > 5:  # More than just "create ticket"
            response += "I've noted your issue. Let me create a ticket for you."
        else:
            response += "Please describe the issue you're experiencing, and I'll create a ticket for you."
        
        return response
    
    def _handle_product_inquiry(self, message: str, entities: Dict) -> str:
        """Handle product information requests."""
        products = self.knowledge_base.get('products', [])
        
        if not products:
            return "I'd be happy to provide product information. What specific details are you looking for?"
        
        # Check if user mentioned a specific product
        message_lower = message.lower()
        for product in products:
            if product['name'].lower() in message_lower:
                return self._format_product_info(product)
        
        # Return general product overview
        response = "Here are our available products:\n\n"
        for product in products:
            response += f"• **{product['name']}** - {product['description']} ({product['price']})\n"
        
        response += "\nWhich product would you like to know more about?"
        return response
    
    def _format_product_info(self, product: Dict) -> str:
        """Format product information for display."""
        response = f"**{product['name']}**\n"
        response += f"{product['description']}\n"
        response += f"Price: {product['price']}\n\n"
        response += "**Features:**\n"
        for feature in product.get('features', []):
            response += f"• {feature}\n"
        
        return response
    
    def _handle_pricing_inquiry(self, message: str, entities: Dict) -> str:
        """Handle pricing information requests."""
        products = self.knowledge_base.get('products', [])
        
        if not products:
            return "I can help you with pricing information. What product or service are you interested in?"
        
        response = "Here are our current pricing options:\n\n"
        for product in products:
            response += f"• **{product['name']}**: {product['price']}\n"
            response += f"  {product['description']}\n\n"
        
        response += "Would you like more details about any specific plan?"
        return response
    
    def _find_faq_match(self, message: str) -> Optional[str]:
        """Find a matching FAQ entry for the message."""
        if not self.knowledge_base or 'faqs' not in self.knowledge_base:
            return None
        
        message_lower = message.lower()
        best_match = None
        best_score = 0
        
        for faq in self.knowledge_base['faqs']:
            question = faq['question'].lower()
            keywords = [kw.lower() for kw in faq.get('keywords', [])]
            
            # Calculate score based on keyword matches
            score = 0
            
            # Check for exact keyword matches
            for keyword in keywords:
                if keyword in message_lower:
                    score += 2  # Higher weight for keyword matches
            
            # Check for question similarity (more flexible)
            question_words = set(question.split())
            message_words = set(message_lower.split())
            common_words = question_words.intersection(message_words)
            
            if len(common_words) >= 2:  # Require at least 2 common words
                score += len(common_words) * 1.0
            
            # Check for exact phrase matches
            if any(keyword in message_lower for keyword in keywords):
                score += 1
            
            # Special handling for business hours
            if 'business hours' in question and any(word in message_lower for word in ['hours', 'business', 'time', 'when', 'open']):
                score += 4
            
            # Special handling for password reset
            if 'password' in question and any(word in message_lower for word in ['password', 'reset', 'forgot', 'login']):
                score += 4
            
            # Special handling for contact/support
            if 'contact' in question and any(word in message_lower for word in ['contact', 'support', 'help', 'phone', 'email']):
                score += 4
            
            # Special handling for payment methods
            if 'payment' in question and any(word in message_lower for word in ['payment', 'credit card', 'paypal', 'money', 'billing']):
                score += 4
            
            # Penalize if message is too short for complex FAQ
            if len(message_lower.split()) < 3 and len(question.split()) > 5:
                score -= 1
            
            # Penalize if it's clearly a greeting but FAQ is about something else
            greeting_words = ['hello', 'hi', 'hey', 'how are you', 'how r u', 'whats up']
            if any(word in message_lower for word in greeting_words) and 'password' in question:
                score -= 5  # Heavy penalty for greeting matching password FAQ
            
            if score > best_score:
                best_score = score
                best_match = faq
        
        # Only return if we have a strong match (threshold >= 2.0)
        if best_score >= 2.0:
            return best_match['answer']
        
        return None
    
    def _find_faq_for_intent(self, intent: str, message: str) -> Optional[str]:
        """Find FAQ answer for specific intents."""
        if not self.knowledge_base or 'faqs' not in self.knowledge_base:
            return None
        
        # Map intents to FAQ keywords
        intent_faq_mapping = {
            'business_hours': ['business hours', 'hours', 'time', 'available'],
            'password_reset': ['password', 'reset', 'forgot', 'login'],
            'contact_support': ['contact', 'support', 'phone', 'email']
        }
        
        if intent not in intent_faq_mapping:
            return None
        
        target_keywords = intent_faq_mapping[intent]
        
        for faq in self.knowledge_base['faqs']:
            question = faq['question'].lower()
            keywords = [kw.lower() for kw in faq.get('keywords', [])]
            
            # Check if this FAQ matches our intent
            if any(keyword in question for keyword in target_keywords) or any(keyword in keywords for keyword in target_keywords):
                return faq['answer']
        
        return None
    
    def _generate_suggestions(self, intent: str, context: List[Dict]) -> List[str]:
        """Generate follow-up suggestions based on intent and context."""
        suggestions = []
        
        if intent == 'greeting':
            suggestions = [
                "Tell me about your products",
                "I need help with my account",
                "Create a support ticket",
                "What are your business hours?"
            ]
        elif intent == 'help':
            suggestions = [
                "Product information",
                "Account help",
                "Create support ticket",
                "Pricing information"
            ]
        elif intent == 'support_ticket':
            suggestions = [
                "Technical issue",
                "Billing problem",
                "Account access",
                "Feature request"
            ]
        elif intent == 'product_info':
            suggestions = [
                "Basic Plan details",
                "Pro Plan features",
                "Enterprise options",
                "Pricing information"
            ]
        elif intent == 'pricing':
            suggestions = [
                "Basic Plan pricing",
                "Pro Plan pricing",
                "Enterprise pricing",
                "Payment methods"
            ]
        else:
            suggestions = [
                "How can I help you?",
                "Tell me about your services",
                "I need support",
                "Account information"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _check_if_human_needed(self, message: str, nlp_result: Dict, context: List[Dict]) -> bool:
        """Check if human intervention is needed."""
        # Low confidence in intent recognition
        if nlp_result.get('confidence', 0) < 0.3:
            return True
        
        # Very negative sentiment
        sentiment = nlp_result.get('sentiment', {})
        if sentiment.get('compound', 0) < -0.7:
            return True
        
        # Complex technical questions
        technical_keywords = ['api', 'integration', 'configuration', 'setup', 'installation']
        if any(keyword in message.lower() for keyword in technical_keywords):
            return True
        
        # User explicitly asks for human
        human_keywords = ['human', 'person', 'agent', 'representative', 'real person']
        if any(keyword in message.lower() for keyword in human_keywords):
            return True
        
        return False
    
    def update_conversation_state(self, user_id: str, intent: str, response: str):
        """Update conversation state for the user."""
        if user_id not in self.conversation_states:
            self.conversation_states[user_id] = {
                'last_intent': None,
                'conversation_count': 0,
                'last_response_time': None
            }
        
        self.conversation_states[user_id]['last_intent'] = intent
        self.conversation_states[user_id]['conversation_count'] += 1
        self.conversation_states[user_id]['last_response_time'] = datetime.now()
    
    def get_conversation_state(self, user_id: str) -> Dict:
        """Get conversation state for a user."""
        return self.conversation_states.get(user_id, {})
    
    def health_check(self) -> Dict:
        """Perform health check on response manager."""
        return {
            'status': 'healthy',
            'knowledge_base_loaded': len(self.knowledge_base.get('faqs', [])) > 0,
            'response_templates_loaded': len(self.response_templates) > 0,
            'active_conversations': len(self.conversation_states),
            'faq_count': len(self.knowledge_base.get('faqs', [])),
            'product_count': len(self.knowledge_base.get('products', []))
        } 