#!/usr/bin/env python3
"""
Setup script for Customer Support Chatbot

This script helps users set up the chatbot environment and install dependencies.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print the setup banner."""
    print("=" * 60)
    print("🤖 Customer Support Chatbot Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def download_nltk_data():
    """Download required NLTK data."""
    print("🧠 Downloading NLTK data...")
    
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        print("✅ NLTK data downloaded successfully!")
    except ImportError:
        print("⚠️  NLTK not available, using fallback methods")
    except Exception as e:
        print(f"⚠️  Warning: Could not download NLTK data: {e}")

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    directories = [
        "database",
        "data",
        "static/css",
        "static/js",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def check_files():
    """Check if all required files exist."""
    print("📋 Checking files...")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "chatbot/__init__.py",
        "chatbot/core.py",
        "chatbot/nlp.py",
        "chatbot/database.py",
        "chatbot/responses.py",
        "templates/index.html",
        "static/css/style.css",
        "static/js/chat.js",
        "data/knowledge_base.json",
        "data/responses.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ Found: {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def test_imports():
    """Test if all modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from chatbot import Chatbot
        print("✅ Chatbot module imported successfully!")
    except ImportError as e:
        print(f"❌ Error importing chatbot module: {e}")
        return False
    
    try:
        import flask
        import nltk
        import sklearn
        import numpy
        import pandas
        print("✅ All dependencies imported successfully!")
    except ImportError as e:
        print(f"❌ Error importing dependencies: {e}")
        return False
    
    return True

def create_config():
    """Create default configuration file."""
    config_path = Path("data/config.json")
    
    if not config_path.exists():
        print("⚙️  Creating default configuration...")
        
        config = {
            "name": "Customer Support Bot",
            "version": "1.0.0",
            "language": "en",
            "max_context_length": 10,
            "response_timeout": 5.0,
            "enable_sentiment": True,
            "enable_learning": True,
            "database": {
                "path": "database/chatbot.db",
                "backup_enabled": True,
                "backup_interval": 24
            },
            "nlp": {
                "confidence_threshold": 0.3,
                "max_entities": 10,
                "enable_fallback": True
            },
            "web": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": True,
                "threaded": True
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration file created!")

def run_health_check():
    """Run a basic health check."""
    print("🏥 Running health check...")
    
    try:
        from chatbot import Chatbot
        bot = Chatbot()
        health = bot.health_check()
        
        if health['status'] == 'healthy':
            print("✅ Health check passed!")
            return True
        else:
            print(f"⚠️  Health check issues: {health}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    check_python_version()
    print()
    
    # Create directories
    create_directories()
    print()
    
    # Check files
    if not check_files():
        print("❌ Setup failed: Missing required files")
        sys.exit(1)
    print()
    
    # Install dependencies
    install_dependencies()
    print()
    
    # Download NLTK data
    download_nltk_data()
    print()
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed: Import errors")
        sys.exit(1)
    print()
    
    # Create configuration
    create_config()
    print()
    
    # Health check
    if run_health_check():
        print()
        print("🎉 Setup completed successfully!")
        print()
        print("To start the chatbot:")
        print("  python app.py")
        print()
        print("Then open your browser and go to:")
        print("  http://localhost:5000")
        print()
        print("For API documentation:")
        print("  http://localhost:5000/api/health")
        print()
    else:
        print("⚠️  Setup completed with warnings")
        print("The chatbot may not work properly")

if __name__ == "__main__":
    main() 