class ChatbotUI {
    constructor() {
        this.userId = this.generateUserId();
        this.sessionId = null;
        this.isTyping = false;
        this.apiBase = '/.netlify/functions';
        
        this.initializeElements();
        this.bindEvents();
        this.loadSettings();
        this.loadChatHistory();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.quickSuggestions = document.getElementById('quickSuggestions');
        
        // Modal elements
        this.settingsModal = document.getElementById('settingsModal');
        this.ticketModal = document.getElementById('ticketModal');
        this.userIdInput = document.getElementById('userId');
        
        // Set user ID in settings
        if (this.userIdInput) {
            this.userIdInput.value = this.userId;
        }
    }

    bindEvents() {
        // Send message events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });

        // Quick suggestions
        this.quickSuggestions.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn')) {
                const suggestion = e.target.getAttribute('data-suggestion');
                this.messageInput.value = suggestion;
                this.sendMessage();
            }
        });

        // Header actions
        document.getElementById('clearChat')?.addEventListener('click', () => this.clearChat());
        document.getElementById('humanAgent')?.addEventListener('click', () => this.requestHumanAgent());
        document.getElementById('settings')?.addEventListener('click', () => this.openSettings());

        // Settings modal
        document.getElementById('closeSettings')?.addEventListener('click', () => this.closeSettings());
        document.getElementById('generateUserId')?.addEventListener('click', () => this.generateNewUserId());
        document.getElementById('exportHistory')?.addEventListener('click', () => this.exportHistory());
        document.getElementById('clearHistory')?.addEventListener('click', () => this.clearHistory());

        // Ticket modal
        document.getElementById('closeTicket')?.addEventListener('click', () => this.closeTicketModal());
        document.getElementById('submitTicket')?.addEventListener('click', () => this.submitTicket());
        document.getElementById('cancelTicket')?.addEventListener('click', () => this.closeTicketModal());

        // Theme selector
        document.getElementById('themeSelect')?.addEventListener('change', (e) => {
            this.setTheme(e.target.value);
        });

        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';

        // Show typing indicator
        this.showTyping();

        try {
            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.sessionId = data.session_id;
                this.addMessage(data.response, 'bot');
                
                // Update suggestions if provided
                if (data.suggestions && data.suggestions.length > 0) {
                    this.updateSuggestions(data.suggestions);
                }

                // Handle human agent request
                if (data.requires_human) {
                    this.requestHumanAgent();
                }

                // Save to local storage
                this.saveChatHistory();
            } else {
                this.addMessage(data.response || 'Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I\'m having trouble connecting. Please check your internet connection and try again.', 'bot');
        } finally {
            this.hideTyping();
        }
    }

    addMessage(text, sender, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const time = timestamp || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-time">${time}</div>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTyping() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    updateSuggestions(suggestions) {
        this.quickSuggestions.innerHTML = '';
        suggestions.forEach(suggestion => {
            const btn = document.createElement('button');
            btn.className = 'suggestion-btn';
            btn.setAttribute('data-suggestion', suggestion);
            btn.textContent = suggestion;
            this.quickSuggestions.appendChild(btn);
        });
    }

    clearChat() {
        // Keep only the welcome message
        const welcomeMessage = this.chatMessages.querySelector('.bot-message');
        this.chatMessages.innerHTML = '';
        if (welcomeMessage) {
            this.chatMessages.appendChild(welcomeMessage);
        }
        this.sessionId = null;
        this.clearChatHistory();
    }

    async requestHumanAgent() {
        this.showTyping();
        
        try {
            const response = await fetch(`${this.apiBase}/human-agent`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage('I\'m sorry, but I\'m unable to connect you to a human agent right now. Please try creating a support ticket instead.', 'bot');
            }
        } catch (error) {
            console.error('Error requesting human agent:', error);
            this.addMessage('I\'m sorry, but I\'m unable to connect you to a human agent right now. Please try again later.', 'bot');
        } finally {
            this.hideTyping();
        }
    }

    openSettings() {
        this.settingsModal.style.display = 'block';
    }

    closeSettings() {
        this.settingsModal.style.display = 'none';
    }

    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }

    generateNewUserId() {
        this.userId = this.generateUserId();
        this.userIdInput.value = this.userId;
        this.saveSettings();
        this.clearChat();
    }

    openTicketModal() {
        this.ticketModal.style.display = 'block';
    }

    closeTicketModal() {
        this.ticketModal.style.display = 'none';
        // Clear form
        document.getElementById('ticketSubject').value = '';
        document.getElementById('ticketDescription').value = '';
        document.getElementById('ticketPriority').value = 'medium';
    }

    async submitTicket() {
        const subject = document.getElementById('ticketSubject').value.trim();
        const description = document.getElementById('ticketDescription').value.trim();
        const priority = document.getElementById('ticketPriority').value;

        if (!subject || !description) {
            alert('Please fill in all required fields.');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/ticket`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    subject: subject,
                    description: description,
                    priority: priority
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.addMessage(`✅ ${data.message}`, 'bot');
                this.closeTicketModal();
            } else {
                alert('Failed to create ticket: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error creating ticket:', error);
            alert('Failed to create ticket. Please try again.');
        }
    }

    setTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('chatbot_theme', theme);
    }

    loadSettings() {
        const savedUserId = localStorage.getItem('chatbot_user_id');
        const savedTheme = localStorage.getItem('chatbot_theme');
        
        if (savedUserId) {
            this.userId = savedUserId;
            if (this.userIdInput) {
                this.userIdInput.value = this.userId;
            }
        }
        
        if (savedTheme) {
            this.setTheme(savedTheme);
            const themeSelect = document.getElementById('themeSelect');
            if (themeSelect) {
                themeSelect.value = savedTheme;
            }
        }
    }

    saveSettings() {
        localStorage.setItem('chatbot_user_id', this.userId);
    }

    saveChatHistory() {
        const messages = Array.from(this.chatMessages.children).map(msg => ({
            text: msg.querySelector('.message-text').textContent,
            sender: msg.classList.contains('user-message') ? 'user' : 'bot',
            time: msg.querySelector('.message-time').textContent
        }));
        localStorage.setItem('chatbot_history', JSON.stringify(messages));
    }

    loadChatHistory() {
        const history = localStorage.getItem('chatbot_history');
        if (history) {
            try {
                const messages = JSON.parse(history);
                // Clear existing messages except welcome
                const welcomeMessage = this.chatMessages.querySelector('.bot-message');
                this.chatMessages.innerHTML = '';
                if (welcomeMessage) {
                    this.chatMessages.appendChild(welcomeMessage);
                }
                
                // Add saved messages (skip the first welcome message if it exists)
                messages.slice(1).forEach(msg => {
                    this.addMessage(msg.text, msg.sender, msg.time);
                });
            } catch (error) {
                console.error('Error loading chat history:', error);
            }
        }
    }

    clearChatHistory() {
        localStorage.removeItem('chatbot_history');
    }

    clearHistory() {
        this.clearChatHistory();
        this.clearChat();
    }

    exportHistory() {
        const history = localStorage.getItem('chatbot_history');
        if (history) {
            const blob = new Blob([history], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chatbot_history_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } else {
            alert('No chat history to export.');
        }
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ChatbotUI();
    
    // Check if we need to open ticket modal based on URL or message
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('action') === 'ticket') {
        setTimeout(() => window.chatbot.openTicketModal(), 500);
    }
});
