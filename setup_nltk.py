#!/usr/bin/env python3
"""
NLTK Data Setup Script

Downloads required NLTK data for the chatbot deployment.
This script should be run during the build process.
"""

import nltk
import ssl
import os

def download_nltk_data():
    """Download required NLTK data with error handling."""
    try:
        # Handle SSL certificate issues
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        
        # Set NLTK data path
        nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir)
        
        # Download required NLTK data
        required_data = [
            'punkt',
            'stopwords', 
            'wordnet',
            'averaged_perceptron_tagger',
            'vader_lexicon'
        ]
        
        print("Downloading NLTK data...")
        for data_name in required_data:
            try:
                nltk.download(data_name, quiet=True)
                print(f"✓ Downloaded {data_name}")
            except Exception as e:
                print(f"✗ Failed to download {data_name}: {e}")
        
        print("NLTK data setup complete!")
        return True
        
    except Exception as e:
        print(f"Error setting up NLTK data: {e}")
        return False

if __name__ == "__main__":
    download_nltk_data()
