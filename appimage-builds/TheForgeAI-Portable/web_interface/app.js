// THE FORGE AI - ChatGPT 2.0 Style Interface
// Main Application Logic

class ForgeAI {
    constructor() {
        this.conversations = [];
        this.currentConversation = null;
        this.currentModel = 'kimi-k2';
        this.isOnline = true;
        this.settings = this.loadSettings();
        
        this.init();
    }
    
    init() {
        this.loadConversations();
        this.setupEventListeners();
        this.applyTheme();
        this.checkOnlineStatus();
        this.autoResizeTextarea();
    }
    
    setupEventListeners() {
        // New chat button
        document.getElementById('newChatBtn').addEventListener('click', () => this.createNewChat());
        
        // Send message
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input handling
        const messageInput = document.getElementById('messageInput');
        messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.toggleSendButton();
            this.autoResizeTextarea();
        });
        
        // Model selector
        document.getElementById('modelSelect').addEventListener('change', (e) => {
            this.currentModel = e.target.value;
            document.getElementById('currentModel').textContent = this.getModelName(e.target.value);
        });
        
        // Settings
        document.getElementById('settingsBtn').addEventListener('click', () => this.openSettings());
        document.getElementById('closeSettings').addEventListener('click', () => this.closeSettings());
        
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());
        document.getElementById('themeSelect').addEventListener('change', (e) => {
            this.settings.theme = e.target.value;
            this.applyTheme();
            this.saveSettings();
        });
        
        // Temperature slider
        document.getElementById('temperature').addEventListener('input', (e) => {
            document.getElementById('tempValue').textContent = e.target.value;
            this.settings.temperature = parseFloat(e.target.value);
            this.saveSettings();
        });
        
        // File attachment
        document.getElementById('attachBtn').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });
        
        // Menu toggle (mobile)
        document.getElementById('menuToggle').addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('hidden');
        });
        
        // Data management
        document.getElementById('exportData').addEventListener('click', () => this.exportData());
        document.getElementById('clearData').addEventListener('click', () => this.clearData());
        
        // Close modal on outside click
        document.getElementById('settingsModal').addEventListener('click', (e) => {
            if (e.target.id === 'settingsModal') {
                this.closeSettings();
            }
        });
    }
    
    createNewChat() {
        const conversation = {
            id: Date.now().toString(),
            title: 'New Chat',
            messages: [],
            createdAt: new Date().toISOString(),
            model: this.currentModel
        };
        
        this.conversations.unshift(conversation);
        this.currentConversation = conversation;
        this.saveConversations();
        this.renderConversations();
        this.renderMessages();
        this.showWelcomeScreen(false);
    }
    
    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Create conversation if none exists
        if (!this.currentConversation) {
            this.createNewChat();
        }
        
        // Add user message
        const userMessage = {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        };
        
        this.currentConversation.messages.push(userMessage);
        
        // Update title if first message
        if (this.currentConversation.messages.length === 1) {
            this.currentConversation.title = message.substring(0, 50) + (message.length > 50 ? '...' : '');
        }
        
        // Clear input
        input.value = '';
        this.updateCharCount();
        this.toggleSendButton();
        this.autoResizeTextarea();
        
        // Render messages
        this.renderMessages();
        this.showWelcomeScreen(false);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Get AI response
        try {
            const response = await this.getAIResponse(message);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add assistant message
            const assistantMessage = {
                role: 'assistant',
                content: response,
                timestamp: new Date().toISOString(),
                model: this.currentModel
            };
            
            this.currentConversation.messages.push(assistantMessage);
            
            // Save and render
            this.saveConversations();
            this.renderConversations();
            this.renderMessages();
            
        } catch (error) {
            this.hideTypingIndicator();
            this.showError('Failed to get response. Please try again.');
            console.error('Error getting AI response:', error);
        }
    }
    
    async getAIResponse(message) {
        // Check if online
        if (!this.isOnline && this.currentModel !== 'local') {
            return "⚠️ You're offline. Please switch to a local model or connect to the internet.";
        }
        
        // Simulate API call (replace with actual API integration)
        await this.delay(1000 + Math.random() * 2000);
        
        // Mock response based on model
        const responses = {
            'kimi-k2': `🔥 THE FORGE AI (Kimi K2) responding to: "${message}"\n\nThis is a demonstration response. In production, this would connect to the actual Kimi K2 model and provide intelligent responses based on all 575+ capabilities including:\n\n- Programming in 20+ languages\n- Content creation and book writing\n- Multimedia editing\n- Code analysis and review\n- And much more!\n\nThe system is ready to handle your request with full context awareness and multi-turn conversation support.`,
            'gpt-4': `GPT-4 response to: "${message}"\n\nThis would connect to OpenAI's GPT-4 API.`,
            'claude-3': `Claude 3 response to: "${message}"\n\nThis would connect to Anthropic's Claude API.`,
            'local': `Local LLM response to: "${message}"\n\nThis would use a locally deployed model (Ollama, LM Studio, etc.)`
        };
        
        return responses[this.currentModel] || responses['kimi-k2'];
    }
    
    renderMessages() {
        const container = document.getElementById('messagesContainer');
        
        if (!this.currentConversation || this.currentConversation.messages.length === 0) {
            container.innerHTML = '';
            return;
        }
        
        container.innerHTML = this.currentConversation.messages.map(msg => `
            <div class="message ${msg.role}">
                <div class="message-header">
                    <div class="message-avatar">
                        ${msg.role === 'user' ? 'U' : '🔥'}
                    </div>
                    <div class="message-role">${msg.role === 'user' ? 'You' : 'THE FORGE AI'}</div>
                </div>
                <div class="message-content">${this.formatMessage(msg.content)}</div>
                <div class="message-actions">
                    <button class="message-action-btn" onclick="forgeAI.copyMessage('${msg.content.replace(/'/g, "\\'")}')">
                        Copy
                    </button>
                    ${msg.role === 'assistant' ? `
                        <button class="message-action-btn" onclick="forgeAI.regenerateResponse()">
                            Regenerate
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }
    
    formatMessage(content) {
        // Basic markdown-like formatting
        let formatted = content
            .replace(/\n/g, '<br>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Code blocks
        formatted = formatted.replace(/```(\w+)?\n([\s\S]+?)```/g, (match, lang, code) => {
            return `<pre><code class="language-${lang || 'text'}">${code.trim()}</code></pre>`;
        });
        
        return formatted;
    }
    
    showTypingIndicator() {
        const container = document.getElementById('messagesContainer');
        const indicator = document.createElement('div');
        indicator.className = 'message assistant typing';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="message-header">
                <div class="message-avatar">🔥</div>
                <div class="message-role">THE FORGE AI</div>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        container.appendChild(indicator);
        container.scrollTop = container.scrollHeight;
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    renderConversations() {
        const container = document.getElementById('conversationsList');
        
        if (this.conversations.length === 0) {
            container.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">No conversations yet</div>';
            return;
        }
        
        container.innerHTML = this.conversations.map(conv => `
            <div class="conversation-item ${conv.id === this.currentConversation?.id ? 'active' : ''}" 
                 onclick="forgeAI.loadConversation('${conv.id}')">
                <div class="conversation-title">${conv.title}</div>
            </div>
        `).join('');
    }
    
    loadConversation(id) {
        this.currentConversation = this.conversations.find(c => c.id === id);
        this.renderConversations();
        this.renderMessages();
        this.showWelcomeScreen(false);
        
        // Hide sidebar on mobile
        if (window.innerWidth <= 768) {
            document.getElementById('sidebar').classList.add('hidden');
        }
    }
    
    showWelcomeScreen(show = true) {
        const welcome = document.getElementById('welcomeScreen');
        const messages = document.getElementById('messagesContainer');
        
        if (show) {
            welcome.style.display = 'flex';
            messages.style.display = 'none';
        } else {
            welcome.style.display = 'none';
            messages.style.display = 'block';
        }
    }
    
    updateCharCount() {
        const input = document.getElementById('messageInput');
        const count = document.getElementById('charCount');
        count.textContent = `${input.value.length} / 4000`;
    }
    
    toggleSendButton() {
        const input = document.getElementById('messageInput');
        const btn = document.getElementById('sendBtn');
        btn.disabled = input.value.trim().length === 0;
    }
    
    autoResizeTextarea() {
        const textarea = document.getElementById('messageInput');
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
    
    openSettings() {
        document.getElementById('settingsModal').classList.add('active');
        
        // Load current settings
        document.getElementById('themeSelect').value = this.settings.theme;
        document.getElementById('defaultModel').value = this.settings.defaultModel || 'kimi-k2';
        document.getElementById('temperature').value = this.settings.temperature || 0.7;
        document.getElementById('tempValue').textContent = this.settings.temperature || 0.7;
        document.getElementById('codeHighlight').checked = this.settings.codeHighlight !== false;
        document.getElementById('autoSave').checked = this.settings.autoSave !== false;
        document.getElementById('soundEffects').checked = this.settings.soundEffects || false;
    }
    
    closeSettings() {
        document.getElementById('settingsModal').classList.remove('active');
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.settings.theme = newTheme;
        this.applyTheme();
        this.saveSettings();
    }
    
    applyTheme() {
        const theme = this.settings.theme || 'dark';
        if (theme === 'auto') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }
    }
    
    checkOnlineStatus() {
        this.isOnline = navigator.onLine;
        this.updateStatusIndicator();
        
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.updateStatusIndicator();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.updateStatusIndicator();
        });
    }
    
    updateStatusIndicator() {
        const indicator = document.getElementById('statusIndicator');
        const dot = indicator.querySelector('.status-dot');
        const text = indicator.querySelector('.status-text');
        
        if (this.isOnline) {
            dot.classList.add('online');
            text.textContent = 'Online';
        } else {
            dot.classList.remove('online');
            text.textContent = 'Offline';
        }
    }
    
    handleFileUpload(files) {
        if (files.length === 0) return;
        
        // Handle file upload (implement file processing)
        console.log('Files uploaded:', files);
        alert(`${files.length} file(s) selected. File processing will be implemented.`);
    }
    
    copyMessage(content) {
        navigator.clipboard.writeText(content).then(() => {
            // Show success feedback
            alert('Message copied to clipboard!');
        });
    }
    
    regenerateResponse() {
        if (!this.currentConversation || this.currentConversation.messages.length < 2) return;
        
        // Remove last assistant message
        this.currentConversation.messages.pop();
        
        // Get last user message
        const lastUserMessage = this.currentConversation.messages[this.currentConversation.messages.length - 1];
        
        // Regenerate
        this.renderMessages();
        this.showTypingIndicator();
        
        this.getAIResponse(lastUserMessage.content).then(response => {
            this.hideTypingIndicator();
            
            const assistantMessage = {
                role: 'assistant',
                content: response,
                timestamp: new Date().toISOString(),
                model: this.currentModel
            };
            
            this.currentConversation.messages.push(assistantMessage);
            this.saveConversations();
            this.renderMessages();
        });
    }
    
    exportData() {
        const data = {
            conversations: this.conversations,
            settings: this.settings,
            exportedAt: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `forge-ai-export-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    clearData() {
        if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
            this.conversations = [];
            this.currentConversation = null;
            localStorage.removeItem('forge_conversations');
            this.renderConversations();
            this.showWelcomeScreen(true);
            alert('All data cleared successfully.');
        }
    }
    
    saveConversations() {
        localStorage.setItem('forge_conversations', JSON.stringify(this.conversations));
    }
    
    loadConversations() {
        const saved = localStorage.getItem('forge_conversations');
        if (saved) {
            this.conversations = JSON.parse(saved);
            this.renderConversations();
        }
    }
    
    saveSettings() {
        localStorage.setItem('forge_settings', JSON.stringify(this.settings));
    }
    
    loadSettings() {
        const saved = localStorage.getItem('forge_settings');
        return saved ? JSON.parse(saved) : {
            theme: 'dark',
            defaultModel: 'kimi-k2',
            temperature: 0.7,
            codeHighlight: true,
            autoSave: true,
            soundEffects: false
        };
    }
    
    getModelName(modelId) {
        const names = {
            'kimi-k2': 'Kimi K2',
            'gpt-4': 'GPT-4',
            'claude-3': 'Claude 3',
            'local': 'Local LLM'
        };
        return names[modelId] || modelId;
    }
    
    showError(message) {
        // Simple error display (can be enhanced)
        alert(message);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize app
const forgeAI = new ForgeAI();

// Service Worker registration for PWA
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').then(registration => {
        console.log('Service Worker registered:', registration);
    }).catch(error => {
        console.log('Service Worker registration failed:', error);
    });
}