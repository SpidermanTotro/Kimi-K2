// THE FORGE AI - Frontend Application

let currentMode = 'chat';
let capabilities = {};
let stats = {};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔥 THE FORGE AI - Initializing...');
    updateTime();
    setInterval(updateTime, 1000);
});

async function initializeApp() {
    try {
        // Initialize THE FORGE
        const response = await fetch('/api/init');
        stats = await response.json();
        
        // Update UI with stats
        document.getElementById('capCount').textContent = stats.total_capabilities;
        document.getElementById('docCount').textContent = stats.documents_loaded;
        document.getElementById('statusBadge').textContent = 'Ready';
        document.getElementById('statusBadge').style.background = 'var(--success)';
        
        // Load capabilities
        loadCapabilities();
        
        console.log('✅ THE FORGE AI initialized successfully!');
    } catch (error) {
        console.error('❌ Initialization error:', error);
        document.getElementById('statusBadge').textContent = 'Error';
        document.getElementById('statusBadge').style.background = 'var(--error)';
    }
}

async function loadCapabilities() {
    try {
        const response = await fetch('/api/capabilities');
        capabilities = await response.json();
        
        // Display capabilities
        const capList = document.getElementById('capabilitiesList');
        capList.innerHTML = '';
        
        for (const [category, caps] of Object.entries(capabilities)) {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'capability-category';
            
            const categoryTitle = document.createElement('h4');
            categoryTitle.innerHTML = `<i class="fas fa-folder"></i> ${category} (${caps.length})`;
            categoryDiv.appendChild(categoryTitle);
            
            caps.slice(0, 5).forEach(cap => {
                const capItem = document.createElement('div');
                capItem.className = 'capability-item';
                capItem.innerHTML = `
                    <strong>${cap.name || cap.description.substring(0, 30)}</strong>
                    <small>${cap.description.substring(0, 60)}...</small>
                `;
                categoryDiv.appendChild(capItem);
            });
            
            capList.appendChild(categoryDiv);
        }
    } catch (error) {
        console.error('Error loading capabilities:', error);
    }
}

function showPanel(panelName) {
    const panels = {
        'capabilities': 'capabilitiesPanel',
        'tools': 'toolsPanel',
        'docs': 'docsPanel',
        'settings': 'settingsPanel'
    };
    
    const panel = document.getElementById(panels[panelName]);
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'flex' : 'none';
    }
}

function hidePanel(panelName) {
    const panels = {
        'capabilities': 'capabilitiesPanel',
        'tools': 'toolsPanel',
        'docs': 'docsPanel',
        'settings': 'settingsPanel'
    };
    
    const panel = document.getElementById(panels[panelName]);
    if (panel) {
        panel.style.display = 'none';
    }
}

// Mode switching
document.querySelectorAll('.tool-btn[data-mode]').forEach(btn => {
    btn.addEventListener('click', () => {
        currentMode = btn.dataset.mode;
        
        // Update active state
        document.querySelectorAll('.tool-btn[data-mode]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update mode indicator
        const icons = {
            'chat': 'fa-comments',
            'code': 'fa-code',
            'book': 'fa-book',
            'video': 'fa-video',
            'photo': 'fa-image',
            'word': 'fa-file-word'
        };
        
        const modeNames = {
            'chat': 'Chat Mode',
            'code': 'Code Mode',
            'book': 'Book Writing Mode',
            'video': 'Video Editing Mode',
            'photo': 'Photo Editing Mode',
            'word': 'Document Mode'
        };
        
        const indicator = document.getElementById('modeIndicator');
        indicator.innerHTML = `<i class="fas ${icons[currentMode]}"></i><span>${modeNames[currentMode]}</span>`;
        
        document.getElementById('currentMode').textContent = modeNames[currentMode];
    });
});

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    input.value = '';
    
    try {
        // Send to server
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, mode: currentMode })
        });
        
        const data = await response.json();
        
        // Add AI response
        addMessage(data.message, 'ai');
        
        // Update status
        if (data.capabilities_used && data.capabilities_used.length > 0) {
            document.getElementById('statusMessage').textContent = 
                `Used capabilities: ${data.capabilities_used.join(', ')}`;
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('Error: Could not process your request.', 'ai');
    }
}

function addMessage(text, type) {
    const messages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message`;
    messageDiv.textContent = text;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

async function executeTool(toolName) {
    document.getElementById('statusMessage').textContent = `Executing ${toolName}...`;
    
    try {
        const response = await fetch(`/api/tools/${toolName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        // Add result to chat
        addMessage(`🔧 ${data.name}: ${data.result}`, 'ai');
        
        document.getElementById('statusMessage').textContent = `${data.name} completed`;
    } catch (error) {
        console.error('Tool execution error:', error);
        document.getElementById('statusMessage').textContent = 'Tool execution failed';
    }
}

function filterCapabilities() {
    const searchTerm = document.getElementById('capSearch').value.toLowerCase();
    const capItems = document.querySelectorAll('.capability-item');
    
    capItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(searchTerm) ? 'block' : 'none';
    });
}

function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        timeElement.textContent = timeStr;
    }
}

// Handle Enter key in chat input
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});
