"""
Python Customer Support Chatbot Package

A comprehensive chatbot solution for customer support and interactive communication.
"""

__version__ = "1.0.0"
__author__ = "Chatbot Developer"

from .core import Chatbot
from .nlp import NLPProcessor
from .database import DatabaseManager
from .responses import ResponseManager

__all__ = ['Chatbot', 'NLPProcessor', 'DatabaseManager', 'ResponseManager'] 