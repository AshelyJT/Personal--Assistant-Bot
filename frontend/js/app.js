class ChatApp {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.chatForm = document.getElementById('chat-form');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.clearBtn = document.getElementById('clear-chat');
        this.exportBtn = document.getElementById('export-chat');
        this.charCount = document.getElementById('char-count');
        this.storageKey = 'resumeAssistantTranscript';
        this.messages = [];
        this.isSending = false;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.restoreTranscript();
        this.updateCharCount();
        this.userInput.focus();
    }

    setupEventListeners() {
        this.chatForm.addEventListener('submit', (event) => {
            event.preventDefault();
            this.sendMessage();
        });

        this.userInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                this.sendMessage();
            }
        });

        this.userInput.addEventListener('input', () => {
            this.autoResizeInput();
            this.updateCharCount();
        });

        this.clearBtn.addEventListener('click', () => this.clearTranscript());
        this.exportBtn.addEventListener('click', () => this.exportTranscript());

        document.querySelectorAll('[data-question]').forEach((button) => {
            button.addEventListener('click', () => {
                this.userInput.value = button.getAttribute('data-question');
                this.updateActiveTopic(button);
                this.sendMessage();
            });
        });
    }

    addMessage(message, sender = 'bot', shouldPersist = true) {
        const row = document.createElement('div');
        row.className = `message-row ${sender === 'user' ? 'user-row' : 'bot-row'}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? 'You' : 'AI';

        const bubble = document.createElement('article');
        bubble.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
        bubble.innerHTML = sender === 'user' ? escapeHtml(message) : formatMessage(message);

        const meta = document.createElement('footer');
        meta.className = 'message-meta';
        meta.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        bubble.appendChild(meta);

        if (sender === 'bot') {
            const copyButton = document.createElement('button');
            copyButton.type = 'button';
            copyButton.className = 'copy-btn';
            copyButton.textContent = 'Copy';
            copyButton.addEventListener('click', () => this.copyMessage(message, copyButton));
            bubble.appendChild(copyButton);
        }

        row.appendChild(avatar);
        row.appendChild(bubble);
        this.chatMessages.appendChild(row);
        this.scrollToBottom();

        if (shouldPersist) {
            this.messages.push({ sender, message, timestamp: new Date().toISOString() });
            this.saveTranscript();
        }
    }

    showTyping() {
        this.typingIndicator.classList.add('visible');
        this.scrollToBottom();
    }

    hideTyping() {
        this.typingIndicator.classList.remove('visible');
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    autoResizeInput() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = `${Math.min(this.userInput.scrollHeight, 140)}px`;
    }

    updateCharCount() {
        this.charCount.textContent = `${this.userInput.value.length}/500`;
    }

    updateActiveTopic(activeButton) {
        document.querySelectorAll('.topic-btn').forEach((button) => {
            button.classList.toggle('active', button === activeButton);
        });
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message || this.isSending) return;

        this.isSending = true;
        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.autoResizeInput();
        this.updateCharCount();
        this.sendBtn.disabled = true;
        this.showTyping();

        try {
            const response = await this.fetchBotResponse(message);
            this.hideTyping();
            this.addMessage(response, 'bot');
        } catch (error) {
            console.error('Error:', error);
            this.hideTyping();
            this.addMessage('Sorry, I could not reach the assistant service. Please try again.', 'bot');
        } finally {
            this.isSending = false;
            this.sendBtn.disabled = false;
            this.userInput.focus();
        }
    }

    async fetchBotResponse(message) {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.response || 'Network response was not ok');
        }

        return data.response;
    }

    saveTranscript() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.messages.slice(-50)));
    }

    restoreTranscript() {
        const saved = localStorage.getItem(this.storageKey);
        if (!saved) return;

        try {
            this.messages = JSON.parse(saved);
            this.messages.forEach((item) => this.addMessage(item.message, item.sender, false));
        } catch (error) {
            localStorage.removeItem(this.storageKey);
        }
    }

    clearTranscript() {
        this.messages = [];
        localStorage.removeItem(this.storageKey);
        this.chatMessages.querySelectorAll('.message-row:not(:first-child)').forEach((row) => row.remove());
    }

    exportTranscript() {
        const transcript = this.messages
            .map((item) => `${item.sender.toUpperCase()}: ${item.message}`)
            .join('\n\n');
        const blob = new Blob([transcript || 'No conversation yet.'], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'resume-assistant-transcript.txt';
        link.click();
        URL.revokeObjectURL(url);
    }

    async copyMessage(message, button) {
        try {
            await navigator.clipboard.writeText(message);
            button.textContent = 'Copied';
            setTimeout(() => {
                button.textContent = 'Copy';
            }, 1400);
        } catch (error) {
            button.textContent = 'Copy failed';
        }
    }
}

function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatMessage(text) {
    return escapeHtml(text)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/^- (.*)$/gm, '<span class="list-item">$1</span>')
        .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
        .replace(/\n/g, '<br>');
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
