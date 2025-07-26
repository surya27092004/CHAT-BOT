/**
 * Chat Interface JavaScript
 * Handles chat interactions, API calls, and UI functionality
 */

class ChatInterface {
    constructor() {
        this.userId = this.generateUserId();
        this.sessionId = this.generateSessionId();
        this.isTyping = false;
        this.messageHistory = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadSettings();
        this.updateQuickSuggestions();
    }
    
    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.quickSuggestions = document.getElementById('quickSuggestions');
        
        // Modal elements
        this.settingsModal = document.getElementById('settingsModal');
        this.ticketModal = document.getElementById('ticketModal');
        this.notification = document.getElementById('notification');
        
        // Settings elements
        this.userIdInput = document.getElementById('userId');
        this.themeSelect = document.getElementById('themeSelect');
        this.generateUserIdBtn = document.getElementById('generateUserId');
        
        // Ticket elements
        this.ticketSubject = document.getElementById('ticketSubject');
        this.ticketDescription = document.getElementById('ticketDescription');
        this.ticketPriority = document.getElementById('ticketPriority');
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
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
        
        // Quick suggestions
        this.quickSuggestions.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn')) {
                const suggestion = e.target.dataset.suggestion;
                this.messageInput.value = suggestion;
                this.sendMessage();
            }
        });
        
        // Header actions
        document.getElementById('humanAgent').addEventListener('click', () => this.connectToHumanAgent());
        document.getElementById('clearChat').addEventListener('click', () => this.clearChat());
        document.getElementById('settings').addEventListener('click', () => this.showSettings());
        
        // Modal events
        document.getElementById('closeSettings').addEventListener('click', () => this.hideSettings());
        document.getElementById('closeTicket').addEventListener('click', () => this.hideTicketModal());
        document.getElementById('cancelTicket').addEventListener('click', () => this.hideTicketModal());
        
        // Settings events
        this.generateUserIdBtn.addEventListener('click', () => this.generateNewUserId());
        this.themeSelect.addEventListener('change', (e) => this.changeTheme(e.target.value));
        
        // Ticket events
        document.getElementById('submitTicket').addEventListener('click', () => this.createTicket());
        
        // Export/Import events
        document.getElementById('exportHistory').addEventListener('click', () => this.exportChat());
        document.getElementById('importHistory').addEventListener('click', () => this.importChat());
        
        // Close modals on outside click
        window.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) this.hideSettings();
            if (e.target === this.ticketModal) this.hideTicketModal();
        });
    }
    
    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);
    }
    
    generateNewUserId() {
        this.userId = this.generateUserId();
        this.userIdInput.value = this.userId;
        this.saveSettings();
        this.showNotification('New User ID generated!', 'success');
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.autoResizeTextarea();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await this.callChatAPI(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addMessage(response.response, 'bot');
            
            // Update quick suggestions if provided
            if (response.suggestions && response.suggestions.length > 0) {
                this.updateQuickSuggestions(response.suggestions);
            }
            
            // Handle escalation
            if (response.requires_human) {
                this.showNotification('Connecting you to a human agent...', 'success');
                try {
                    const humanResponse = await this.callHumanAgentAPI();
                    this.addMessage(humanResponse.response, 'human-agent');
                    this.updateQuickSuggestions(humanResponse.suggestions);
                } catch (humanError) {
                    console.error('Human agent API error:', humanError);
                    this.addMessage('I apologize, but I\'m having trouble connecting to a human agent right now. Please try again in a moment.', 'bot');
                }
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            console.error('Chat API error:', error);
            
            // Provide more specific error messages
            let errorMessage = 'I apologize, but I\'m having trouble processing your request right now.';
            
            if (error.message.includes('Failed to fetch')) {
                errorMessage = 'I\'m having trouble connecting to the server. Please check your internet connection and try again.';
            } else if (error.message.includes('Failed to get response')) {
                errorMessage = 'I received an unexpected response from the server. Please try again.';
            } else if (error.message.includes('NetworkError')) {
                errorMessage = 'Network error occurred. Please check your connection and try again.';
            }
            
            this.addMessage(errorMessage, 'bot');
            this.showNotification('Connection issue detected. Please try again.', 'error');
        }
    }
    
    async callChatAPI(message) {
        try {
            console.log('Sending message to API:', message);
            
            const response = await fetch('/api/chat', {
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
            
            console.log('API Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('API Response data:', data);
            
            if (data.success) {
                return data;
            } else {
                throw new Error(data.error || 'Failed to get response');
            }
        } catch (error) {
            console.error('Error calling chat API:', error);
            throw error;
        }
    }
    
    async callHumanAgentAPI() {
        try {
            const response = await fetch('/api/human-agent', {
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
                return data;
            } else {
                throw new Error(data.error || 'Failed to connect to human agent');
            }
        } catch (error) {
            console.error('Error calling human agent API:', error);
            throw error;
        }
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        if (sender === 'bot') {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        } else if (sender === 'human-agent') {
            avatar.innerHTML = '<i class="fas fa-user-tie"></i>'; // New avatar for human agent
            messageDiv.classList.add('human-agent-message');
        } else {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        }
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = text;
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.formatTime(new Date());
        
        content.appendChild(messageText);
        content.appendChild(messageTime);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store in history
        this.messageHistory.push({
            text: text,
            sender: sender,
            timestamp: new Date().toISOString()
        });
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
    }
    
    updateQuickSuggestions(suggestions = null) {
        if (!suggestions) {
            // Default suggestions
            suggestions = [
                "Tell me about your products",
                "I need help with my account",
                "Create a support ticket",
                "What are your business hours?"
            ];
        }
        
        this.quickSuggestions.innerHTML = '';
        suggestions.forEach(suggestion => {
            const btn = document.createElement('button');
            btn.className = 'suggestion-btn';
            btn.dataset.suggestion = suggestion;
            btn.textContent = suggestion;
            this.quickSuggestions.appendChild(btn);
        });
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.chatMessages.innerHTML = '';
            this.messageHistory = [];
            
            // Add welcome message back
            this.addMessage('Hello! 👋 I\'m your customer support assistant. How can I help you today?', 'bot');
            
            this.showNotification('Chat history cleared!', 'success');
        }
    }
    
    showSettings() {
        this.userIdInput.value = this.userId;
        this.settingsModal.classList.add('show');
    }
    
    hideSettings() {
        this.settingsModal.classList.remove('show');
    }
    
    showTicketModal() {
        this.ticketModal.classList.add('show');
    }
    
    hideTicketModal() {
        this.ticketModal.classList.remove('show');
        this.ticketSubject.value = '';
        this.ticketDescription.value = '';
        this.ticketPriority.value = 'medium';
    }
    
    async createTicket() {
        const subject = this.ticketSubject.value.trim();
        const description = this.ticketDescription.value.trim();
        const priority = this.ticketPriority.value;
        
        if (!subject || !description) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/ticket', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subject: subject,
                    description: description,
                    priority: priority,
                    user_id: this.userId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Support ticket created successfully!', 'success');
                this.hideTicketModal();
                this.ticketSubject.value = '';
                this.ticketDescription.value = '';
                this.ticketPriority.value = 'medium';
            } else {
                this.showNotification(data.error || 'Failed to create ticket', 'error');
            }
        } catch (error) {
            console.error('Error creating ticket:', error);
            this.showNotification('Failed to create ticket. Please try again.', 'error');
        }
    }
    
    async connectToHumanAgent() {
        try {
            this.showNotification('Connecting you to a human agent...', 'info');
            
            const humanResponse = await this.callHumanAgentAPI();
            
            // Add a small delay to simulate connection time
            setTimeout(() => {
                this.addMessage(humanResponse.response, 'human-agent');
                this.showNotification('Connected to human agent!', 'success');
            }, 1500);
            
        } catch (error) {
            console.error('Error connecting to human agent:', error);
            this.showNotification('Failed to connect to human agent. Please try again.', 'error');
        }
    }
    
    exportChat() {
        const data = {
            userId: this.userId,
            sessionId: this.sessionId,
            messages: this.messageHistory,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Chat exported successfully!', 'success');
    }
    
    importChat() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    
                    if (data.messages && Array.isArray(data.messages)) {
                        this.chatMessages.innerHTML = '';
                        this.messageHistory = data.messages;
                        
                        data.messages.forEach(msg => {
                            this.addMessage(msg.text, msg.sender);
                        });
                        
                        this.showNotification('Chat imported successfully!', 'success');
                    } else {
                        this.showNotification('Invalid chat export file.', 'error');
                    }
                } catch (error) {
                    this.showNotification('Error importing chat file.', 'error');
                    console.error('Import error:', error);
                }
            };
            reader.readAsText(file);
        };
        
        input.click();
    }
    
    changeTheme(theme) {
        document.body.className = `theme-${theme}`;
        this.saveSettings();
        this.showNotification(`Theme changed to ${theme}!`, 'success');
    }
    
    loadSettings() {
        const settings = JSON.parse(localStorage.getItem('chatbot-settings') || '{}');
        
        if (settings.userId) {
            this.userId = settings.userId;
        }
        
        if (settings.theme) {
            this.themeSelect.value = settings.theme;
            this.changeTheme(settings.theme);
        }
        
        this.userIdInput.value = this.userId;
    }
    
    saveSettings() {
        const settings = {
            userId: this.userId,
            theme: this.themeSelect.value
        };
        localStorage.setItem('chatbot-settings', JSON.stringify(settings));
    }
    
    showNotification(message, type = 'success') {
        this.notification.className = `notification ${type} show`;
        this.notification.querySelector('.notification-message').textContent = message;
        
        setTimeout(() => {
            this.notification.classList.remove('show');
        }, 3000);
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    formatTime(date) {
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diff < 86400000) { // Less than 1 day
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatInterface = new ChatInterface();
});

// Handle ticket creation from chat
window.createSupportTicket = function() {
    window.chatInterface.showTicketModal();
}; 