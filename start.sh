#!/bin/bash
# Start script for Render deployment

# Download NLTK data
python setup_nltk.py

# Start the Flask application
python app.py
