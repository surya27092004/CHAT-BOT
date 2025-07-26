# Python Customer Support Chatbot

A comprehensive Python-based chatbot designed for customer support and interactive communication, featuring natural language processing, web interface, and database integration.

## Features

- **Natural Language Processing**: Understands and responds to user queries intelligently
- **Customer Support**: Handles FAQs, creates support tickets, and provides assistance
- **Interactive Communication**: Engaging conversations with context awareness
- **Web Interface**: Modern, responsive web UI for easy access
- **Database Integration**: Stores conversation history and user data
- **Customizable Responses**: Easy to configure and extend
- **Multi-threaded**: Handles multiple conversations simultaneously

## Project Structure

```
CHATBOT/
├── app.py                 # Main Flask application
├── chatbot/
│   ├── __init__.py       # Chatbot package initialization
│   ├── core.py           # Core chatbot engine
│   ├── nlp.py            # Natural language processing
│   ├── database.py       # Database operations
│   └── responses.py      # Response templates and logic
├── static/
│   ├── css/
│   │   └── style.css     # Styling for web interface
│   └── js/
│       └── chat.js       # Frontend JavaScript
├── templates/
│   └── index.html        # Main web interface
├── data/
│   ├── knowledge_base.json  # FAQ and knowledge base
│   └── responses.json       # Response templates
├── database/
│   └── chatbot.db          # SQLite database
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

1. **Clone or download the project**
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLTK data** (first time only):
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the chatbot**:
   Open your browser and go to `http://localhost:5000`

## Usage

### Web Interface
- Open the web interface in your browser
- Start typing messages in the chat input
- The chatbot will respond based on your queries

### API Endpoints
- `POST /api/chat` - Send a message and get a response
- `GET /api/history` - Get conversation history
- `POST /api/ticket` - Create a support ticket

### Configuration
- Edit `data/knowledge_base.json` to customize FAQs
- Modify `data/responses.json` to change response templates
- Update `chatbot/responses.py` for advanced response logic

## Features in Detail

### Natural Language Processing
- Tokenization and preprocessing
- Intent recognition
- Entity extraction
- Context awareness

### Customer Support
- FAQ handling with intelligent matching
- Support ticket creation
- Escalation to human agents
- Knowledge base integration

### Interactive Communication
- Conversation flow management
- User preference learning
- Multi-turn conversations
- Sentiment analysis

## Customization

### Adding New Responses
1. Edit `data/knowledge_base.json` to add new FAQs
2. Update `data/responses.json` for new response patterns
3. Modify `chatbot/responses.py` for complex logic

### Styling
- Customize `static/css/style.css` for UI changes
- Modify `templates/index.html` for layout changes

### Database
- The chatbot uses SQLite for data storage
- Database file: `database/chatbot.db`
- Tables: conversations, users, tickets

## Troubleshooting

### Common Issues
1. **NLTK data not found**: Run the NLTK download command above
2. **Port already in use**: Change the port in `app.py`
3. **Database errors**: Delete `database/chatbot.db` to reset

### Logs
- Check console output for error messages
- Database logs are stored in the database file

## Contributing

Feel free to contribute by:
- Adding new features
- Improving response quality
- Enhancing the UI
- Fixing bugs

## License

This project is open source and available under the MIT License. 