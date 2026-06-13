class ChatApp {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.chatForm = document.getElementById('chat-form');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.clearBtn = document.getElementById('clear-chat');
        this.exportBtn = document.getElementById('export-chat');
        this.profileToggle = document.getElementById('profile-toggle');
        this.sidebarClose = document.getElementById('sidebar-close');
        this.sidebarBackdrop = document.getElementById('sidebar-backdrop');
        this.charCount = document.getElementById('char-count');
        this.followups = document.getElementById('followups');
        this.dynamicLinks = document.getElementById('dynamic-links');
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
        this.profileToggle.addEventListener('click', () => this.setProfileSidebar(true));
        this.sidebarClose.addEventListener('click', () => this.setProfileSidebar(false));
        this.sidebarBackdrop.addEventListener('click', () => this.setProfileSidebar(false));

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') this.setProfileSidebar(false);
        });

        document.querySelectorAll('[data-question]').forEach((button) => {
            button.addEventListener('click', () => {
                this.userInput.value = button.getAttribute('data-question');
                this.updateActiveTopic(button);
                this.sendMessage();
            });
        });
    }

    setProfileSidebar(isOpen) {
        document.body.classList.toggle('profile-open', isOpen);
        this.profileToggle.setAttribute('aria-expanded', String(isOpen));
        this.sidebarBackdrop.tabIndex = isOpen ? 0 : -1;

        if (isOpen) {
            this.sidebarClose.focus();
        } else if (document.activeElement === this.sidebarClose || document.activeElement === this.sidebarBackdrop) {
            this.profileToggle.focus();
        }
    }

    addMessage(message, sender = 'bot', shouldPersist = true) {
        this.chatMessages.classList.add('chat-active');

        const row = document.createElement('div');
        row.className = `message-row ${sender === 'user' ? 'user-row' : 'bot-row'}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        const avatarLabel = document.createElement('span');
        avatarLabel.textContent = sender === 'user' ? 'You' : 'AI';
        avatar.appendChild(avatarLabel);

        const bubble = document.createElement('article');
        bubble.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
        bubble.innerHTML = sender === 'user' ? escapeHtml(message) : formatMessage(message);

        if (sender === 'bot') {
            const copyButton = document.createElement('button');
            copyButton.type = 'button';
            copyButton.className = 'copy-btn';
            copyButton.innerHTML = '<span aria-hidden="true">&#9634;</span> Copy';
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
            const answer = await this.fetchBotResponse(message);
            this.hideTyping();
            this.addMessage(answer.response, 'bot');
            this.renderFollowups(answer.suggestions || []);
            this.renderLinks(answer.links || []);
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

        return data;
    }

    renderFollowups(suggestions) {
        this.followups.innerHTML = '';
        this.followups.hidden = suggestions.length === 0;

        suggestions.forEach((suggestion) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'followup-btn';
            button.textContent = suggestion;
            button.addEventListener('click', () => {
                this.userInput.value = suggestion;
                this.sendMessage();
            });
            this.followups.appendChild(button);
        });
    }

    renderLinks(links) {
        this.dynamicLinks.innerHTML = '';
        this.dynamicLinks.hidden = links.length === 0;

        links.forEach((link) => {
            const anchor = document.createElement('a');
            anchor.href = link.url;
            anchor.target = '_blank';
            anchor.rel = 'noopener noreferrer';
            anchor.textContent = link.label;
            this.dynamicLinks.appendChild(anchor);
        });
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
        this.chatMessages.querySelectorAll('.message-row').forEach((row) => row.remove());
        this.chatMessages.classList.remove('chat-active');
        this.followups.hidden = true;
        this.dynamicLinks.hidden = true;
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
            button.innerHTML = '<span aria-hidden="true">&#10003;</span> Copied';
            setTimeout(() => {
                button.innerHTML = '<span aria-hidden="true">&#9634;</span> Copy';
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
    const lines = text.split(/\r?\n/);
    const blocks = [];
    let listItems = [];

    const flushList = () => {
        if (!listItems.length) return;
        blocks.push(`<ul class="response-list">${listItems.join('')}</ul>`);
        listItems = [];
    };

    lines.forEach((rawLine) => {
        const line = rawLine.trim();

        if (!line) {
            flushList();
            return;
        }

        if (line.startsWith('- ')) {
            listItems.push(`<li>${formatInline(line.slice(2))}</li>`);
            return;
        }

        flushList();

        const heading = line.match(/^\*\*(.+?)\*\*$/);
        if (heading) {
            blocks.push(`<h4 class="response-heading">${formatInline(heading[1])}</h4>`);
            return;
        }

        const labelledDetail = line.match(/^([A-Za-z][A-Za-z ]{1,24}):\s*(.+)$/);
        if (labelledDetail) {
            blocks.push(
                `<p class="response-detail"><strong>${escapeHtml(labelledDetail[1])}:</strong> ${formatInline(labelledDetail[2])}</p>`
            );
            return;
        }

        blocks.push(`<p class="response-paragraph">${formatInline(line)}</p>`);
    });

    flushList();
    return `<div class="response-content">${blocks.join('')}</div>`;
}

function formatInline(text) {
    return escapeHtml(text)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(
            /(https?:\/\/[^\s<]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
