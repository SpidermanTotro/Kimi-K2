// THE FORGE AI - Interactive JavaScript

class ForgeAI {
    constructor() {
        this.currentCategory = 'programming';
        this.isDarkMode = true;
        this.conversationHistory = [];
        this.activeTools = new Set();
        this.userPreferences = {
            model: 'THE FORGE AI (1T params)',
            language: 'English',
            theme: 'Dark'
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startLoadingAnimation();
        this.initializeWebSocket();
        this.loadUserPreferences();
    }

    setupEventListeners() {
        // Navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchCategory(e.target.closest('.nav-btn')));
        });

        // Panel tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target));
        });

        // Chat input
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        chatInput.addEventListener('input', () => {
            this.autoResizeTextarea(chatInput);
        });

        sendButton.addEventListener('click', () => this.sendMessage());

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.performSearch(e.target.value));
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.toggleSearch();
                }
            });
        }

        // Quick tools
        document.querySelectorAll('.quick-tool').forEach(btn => {
            btn.addEventListener('click', (e) => this.activateQuickTool(e.target.closest('.quick-tool')));
        });

        // Tool close buttons
        document.querySelectorAll('.tool-close').forEach(btn => {
            btn.addEventListener('click', (e) => this.deactivateTool(e.target.closest('.tool-item')));
        });

        // Search overlay click outside
        document.getElementById('searchOverlay')?.addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.toggleSearch();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'k':
                        e.preventDefault();
                        this.toggleSearch();
                        break;
                    case '/':
                        e.preventDefault();
                        document.getElementById('chatInput')?.focus();
                        break;
                }
            }
        });
    }

    startLoadingAnimation() {
        const loadingProgress = document.getElementById('loadingProgress');
        const loadingText = document.getElementById('loadingText');
        let progress = 0;
        
        const loadingMessages = [
            'Initializing THE FORGE AI...',
            'Loading 1 trillion parameters...',
            'Activating 575+ skills...',
            'Configuring neural networks...',
            'Calibrating multilingual support...',
            'Setting up book writing engines...',
            'Initializing gaming enhancement systems...',
            'Loading multimedia tools...',
            'Connecting to GitHub APIs...',
            'Finalizing workspace setup...'
        ];

        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 100) progress = 100;
            
            loadingProgress.style.width = progress + '%';
            
            const messageIndex = Math.floor((progress / 100) * loadingMessages.length);
            if (messageIndex < loadingMessages.length) {
                loadingText.textContent = loadingMessages[messageIndex];
            }
            
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    loadingText.textContent = 'Ready to launch!';
                    setTimeout(() => this.enterMainInterface(), 1000);
                }, 500);
            }
        }, 200);
    }

    enterMainInterface() {
        const startupScreen = document.getElementById('startupScreen');
        const mainInterface = document.getElementById('mainInterface');
        
        startupScreen.style.opacity = '0';
        startupScreen.style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            startupScreen.classList.add('hidden');
            mainInterface.classList.remove('hidden');
            setTimeout(() => {
                mainInterface.classList.add('active');
            }, 50);
        }, 300);
    }

    switchCategory(navBtn) {
        // Update active state
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        navBtn.classList.add('active');
        
        // Update content
        const category = navBtn.dataset.category;
        this.currentCategory = category;
        
        const titles = {
            'programming': 'Programming & Development',
            'writing': 'Book Writing & Publishing',
            'gaming': 'Gaming Enhancement',
            'multimedia': 'Multimedia Production',
            'github': 'GitHub & Version Control'
        };
        
        const descriptions = {
            'programming': 'Advanced code generation and analysis powered by 1 trillion parameters',
            'writing': 'Professional publishing-quality content creation with 50+ genre mastery',
            'gaming': 'Revolutionary game enhancement for 50+ Pokémon games and MMO servers',
            'multimedia': 'Professional video editing, photo enhancement, and YouTube optimization',
            'github': 'Complete repository management, CI/CD automation, and collaboration tools'
        };
        
        document.getElementById('categoryTitle').textContent = titles[category];
        document.getElementById('categoryDescription').textContent = descriptions[category];
        
        // Update quick tools based on category
        this.updateQuickTools(category);
    }

    updateQuickTools(category) {
        // This would dynamically update the quick tools based on the selected category
        console.log(`Updating quick tools for category: ${category}`);
    }

    switchTab(tabBtn) {
        // Update active state
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        tabBtn.classList.add('active');
        
        // Show corresponding content
        const tabName = tabBtn.dataset.tab;
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}Tab`).classList.add('active');
    }

    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        input.value = '';
        this.autoResizeTextarea(input);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Simulate AI response (in real implementation, this would call the backend)
        setTimeout(() => {
            this.hideTypingIndicator();
            const response = this.generateAIResponse(message);
            this.addMessage(response, 'ai');
        }, 1000 + Math.random() * 2000);
    }

    addMessage(content, type) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `${type}-message`;
        
        if (type === 'ai') {
            // Process markdown-like content
            content = this.processMessageContent(content);
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">${content}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Save to history
        this.conversationHistory.push({ type, content, timestamp: new Date() });
    }

    processMessageContent(content) {
        // Basic markdown processing
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        content = content.replace(/`(.*?)`/g, '<code>$1</code>');
        content = content.replace(/\n/g, '<br>');
        return content;
    }

    generateAIResponse(userMessage) {
        const responses = {
            'programming': [
                "I can help you generate code in 20+ programming languages. What would you like to build today? I can create anything from simple scripts to complete applications.",
                "My code generation capabilities include bug detection, security scanning, performance optimization, and comprehensive documentation. What programming challenge are you facing?",
                "I excel at Python, JavaScript, Java, C++, Go, Rust, and many more languages. Just describe what you want to create, and I'll generate production-ready code with proper documentation and testing."
            ],
            'writing': [
                "I'm a professional-grade book writing system that can take your ideas from concept to published book. I can handle character development, plot structure, and maintain perfect consistency across entire series.",
                "With publishing-quality output and 50+ genre mastery, I can help you write anything from technical textbooks to fantasy novels. I also handle all the marketing materials and publishing preparation.",
                "My never-forget memory system ensures perfect character and plot continuity across book series. I can detect sequels, manage timelines, and maintain consistency throughout your entire literary universe."
            ],
            'gaming': [
                "I can enhance ALL 50+ Pokémon games from every generation, upscaling them to modern 4K/8K quality with neural networks. I also create MMO private servers for all 12 WoW expansions.",
                "My gaming enhancement system includes neural upscaling, texture generation, smooth 60 FPS animations, and modern lighting effects. Which classic game would you like to transform?",
                "I handle everything from Game Boy originals to Nintendo 3DS titles, plus complete MMO server setup with database management and authentication systems."
            ],
            'multimedia': [
                "I'm a complete multimedia production suite with professional video editing, photo enhancement, and YouTube optimization tools. I can handle everything from basic edits to professional color grading.",
                "My capabilities include 4K/8K video upscaling, professional photo editing with layers and masks, audio processing with podcast production tools, and comprehensive YouTube analytics.",
                "I can help you create professional content with 100+ video transitions, advanced color grading, motion tracking, and complete YouTube channel optimization."
            ]
        };
        
        const categoryResponses = responses[this.currentCategory] || responses['programming'];
        return categoryResponses[Math.floor(Math.random() * categoryResponses.length)];
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="ai-message">
                <div class="message-content">
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    toggleSearch() {
        const searchOverlay = document.getElementById('searchOverlay');
        searchOverlay.classList.toggle('hidden');
        
        if (!searchOverlay.classList.contains('hidden')) {
            document.getElementById('searchInput').focus();
        }
    }

    performSearch(query) {
        if (!query) {
            this.showDefaultSearchResults();
            return;
        }
        
        // Simulate search results (in real implementation, this would search the skills database)
        console.log(`Searching for: ${query}`);
    }

    showDefaultSearchResults() {
        // Show default search categories
        const searchResults = document.getElementById('searchResults');
        // Results are already in HTML, this would be dynamically generated
    }

    activateQuickTool(toolBtn) {
        const toolName = toolBtn.querySelector('span').textContent;
        this.activeTools.add(toolName);
        this.updateActiveToolsList();
        
        // Add system message about tool activation
        this.addMessage(`Activated ${toolName}. I'm ready to help you with this capability!`, 'system');
        
        // Visual feedback
        toolBtn.style.background = 'var(--primary-color)';
        toolBtn.style.color = 'white';
        setTimeout(() => {
            toolBtn.style.background = '';
            toolBtn.style.color = '';
        }, 300);
    }

    deactivateTool(toolItem) {
        const toolName = toolItem.querySelector('span').textContent;
        this.activeTools.delete(toolName);
        this.updateActiveToolsList();
    }

    updateActiveToolsList() {
        const toolList = document.querySelector('.tool-list');
        toolList.innerHTML = '';
        
        this.activeTools.forEach(toolName => {
            const toolItem = document.createElement('div');
            toolItem.className = 'tool-item active';
            toolItem.innerHTML = `
                <i class="fas fa-tools"></i>
                <span>${toolName}</span>
                <button class="tool-close" onclick="forgeAI.deactivateTool(this.closest('.tool-item'))">
                    <i class="fas fa-times"></i>
                </button>
            `;
            toolList.appendChild(toolItem);
        });
    }

    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        // In a real implementation, this would toggle between light and dark themes
        console.log(`Theme toggled to: ${this.isDarkMode ? 'dark' : 'light'}`);
    }

    toggleSettings() {
        // Switch to settings tab
        const settingsTab = document.querySelector('[data-tab="settings"]');
        if (settingsTab) {
            this.switchTab(settingsTab);
        }
    }

    showHelp() {
        this.addMessage(`
            <strong>THE FORGE AI Help</strong><br><br>
            I'm your comprehensive AI assistant with 575+ integrated skills. Here's how to get started:<br><br>
            <strong>Quick Actions:</strong><br>
            • Use the toolbar at the top to switch between categories<br>
            • Click quick tools in the sidebar to activate specific capabilities<br>
            • Type your questions in the chat below<br><br>
            <strong>Keyboard Shortcuts:</strong><br>
            • Ctrl+K: Open search<br>
            • Ctrl+/: Focus chat input<br>
            • Enter: Send message<br>
            • Shift+Enter: New line<br><br>
            <strong>What I can do:</strong><br>
            • Generate code in 20+ programming languages<br>
            • Write professional books with publishing quality<br>
            • Enhance 50+ Pokémon games with modern graphics<br>
            • Create MMO servers for all WoW expansions<br>
            • Professional video and photo editing<br>
            • YouTube channel optimization<br>
            • Complete GitHub repository management<br>
            • And 565+ more capabilities!<br><br>
            Just ask me what you want to create!
        `, 'system');
    }

    attachFile() {
        // Create file input and trigger click
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '*/*';
        fileInput.onchange = (e) => this.handleFileUpload(e.target.files[0]);
        fileInput.click();
    }

    handleFileUpload(file) {
        if (!file) return;
        
        this.addMessage(`File uploaded: ${file.name} (${this.formatFileSize(file.size)})`, 'system');
        
        // In a real implementation, this would process the file
        console.log('File uploaded:', file);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    insertCode() {
        const input = document.getElementById('chatInput');
        input.value += '\n```\n// Your code here\n```\n';
        input.focus();
    }

    insertImage() {
        this.addMessage('Image insertion activated. Please describe the image you want to create or upload an image file.', 'system');
    }

    insertTable() {
        const input = document.getElementById('chatInput');
        input.value += '\n| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Row 1    | Data     | Data     |\n| Row 2    | Data     | Data     |\n';
        input.focus();
    }

    voiceInput() {
        this.addMessage('Voice input activated. Click the microphone button and start speaking...', 'system');
        // In a real implementation, this would use the Web Speech API
    }

    initializeWebSocket() {
        // Initialize WebSocket connection for real-time features
        // In a real implementation, this would connect to the backend
        console.log('WebSocket initialized');
    }

    loadUserPreferences() {
        // Load user preferences from localStorage
        const saved = localStorage.getItem('forgeAI_preferences');
        if (saved) {
            this.userPreferences = { ...this.userPreferences, ...JSON.parse(saved) };
        }
    }

    saveUserPreferences() {
        localStorage.setItem('forgeAI_preferences', JSON.stringify(this.userPreferences));
    }

    // Quick tool activation functions
    startCodeGeneration() {
        this.addMessage('Code Generator activated! I can generate code in 20+ languages. What would you like me to create?', 'system');
        document.getElementById('chatInput').focus();
    }

    startCodeReview() {
        this.addMessage('Code Review activated! Please paste your code for comprehensive analysis, bug detection, and optimization suggestions.', 'system');
    }

    startBugFix() {
        this.addMessage('Bug Fixer activated! Describe the bug or paste the problematic code, and I\'ll identify and fix the issues.', 'system');
    }

    startBookWriting() {
        this.addMessage('Professional Book Writing activated! I can create publishing-quality books with perfect character consistency and plot development. Tell me about your book idea.', 'system');
    }

    startEditing() {
        this.addMessage('Content Editor activated! I provide professional editing with style consistency, grammar perfection, and quality upscaling. Share your content for editing.', 'system');
    }

    startPublishing() {
        this.addMessage('Publishing Prep activated! I\'ll help you prepare your book for publication with ISBN guidance, cover design, and marketing materials.', 'system');
    }

    startPokemonEnhance() {
        this.addMessage('Pokémon Enhancement activated! I can enhance ALL 50+ Pokémon games from every generation to modern 4K/8K quality. Which game would you like to enhance?', 'system');
    }

    startWoWServer() {
        this.addMessage('WoW Server Creator activated! I can set up private servers for all 12 WoW expansions with complete database and authentication systems. Which expansion would you like?', 'system');
    }

    startGraphics() {
        this.addMessage('Graphics Enhancement activated! I provide neural upscaling, texture generation, and modern visual effects for classic games.', 'system');
    }

    startVideoEdit() {
        this.addMessage('Professional Video Editor activated! I offer multi-track editing, color grading, motion tracking, and export optimization. What video project are you working on?', 'system');
    }

    startPhotoEdit() {
        this.addMessage('Professional Photo Editor activated! I provide layer-based editing, advanced color correction, retouching tools, and batch processing. What photos would you like to enhance?', 'system');
    }

    startAudioEdit() {
        this.addMessage('Audio Production Suite activated! I offer multi-track recording, professional effects, voice processing, and podcast production tools. What audio project can I help with?', 'system');
    }

    showQuickTour() {
        this.addMessage(`
            <strong>Welcome to THE FORGE AI Quick Tour!</strong><br><br>
            <strong>🚀 What makes THE FORGE special:</strong><br>
            • 575+ integrated skills in one platform<br>
            • 1 trillion parameter AI model<br>
            • 128K context window for complex projects<br>
            • Professional publishing-quality output<br>
            • Complete gaming enhancement suite<br><br>
            
            <strong>🎯 Key Capabilities:</strong><br>
            • <strong>Programming:</strong> Generate code in 20+ languages with automatic testing and documentation<br>
            • <strong>Book Writing:</strong> Create professional books with perfect continuity across series<br>
            • <strong>Gaming:</strong> Enhance 50+ Pokémon games + create MMO servers for all WoW expansions<br>
            • <strong>Multimedia:</strong> Professional video/photo editing with YouTube optimization<br>
            • <strong>GitHub:</strong> Complete repository management and CI/CD automation<br><br>
            
            <strong>💡 Getting Started:</strong><br>
            1. Use the toolbar to select your area of interest<br>
            2. Click quick tools or just type what you want to create<br>
            3. I'll handle all the technical details automatically<br><br>
            
            Ready to create something amazing? Just ask!
        `, 'system');
    }
}

// Global functions for onclick handlers
function enterMainInterface() {
    forgeAI.enterMainInterface();
}

function showQuickTour() {
    forgeAI.showQuickTour();
}

function toggleSearch() {
    forgeAI.toggleSearch();
}

function toggleSettings() {
    forgeAI.toggleSettings();
}

function toggleTheme() {
    forgeAI.toggleTheme();
}

function showHelp() {
    forgeAI.showHelp();
}

function sendMessage() {
    forgeAI.sendMessage();
}

function attachFile() {
    forgeAI.attachFile();
}

function insertCode() {
    forgeAI.insertCode();
}

function insertImage() {
    forgeAI.insertImage();
}

function insertTable() {
    forgeAI.insertTable();
}

function voiceInput() {
    forgeAI.voiceInput();
}

function startCodeGeneration() {
    forgeAI.startCodeGeneration();
}

function startCodeReview() {
    forgeAI.startCodeReview();
}

function startBugFix() {
    forgeAI.startBugFix();
}

function startBookWriting() {
    forgeAI.startBookWriting();
}

function startEditing() {
    forgeAI.startEditing();
}

function startPublishing() {
    forgeAI.startPublishing();
}

function startPokemonEnhance() {
    forgeAI.startPokemonEnhance();
}

function startWoWServer() {
    forgeAI.startWoWServer();
}

function startGraphics() {
    forgeAI.startGraphics();
}

function startVideoEdit() {
    forgeAI.startVideoEdit();
}

function startPhotoEdit() {
    forgeAI.startPhotoEdit();
}

function startAudioEdit() {
    forgeAI.startAudioEdit();
}

// Initialize the application
const forgeAI = new ForgeAI();

// Export for global access
window.forgeAI = forgeAI;