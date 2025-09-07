// Enhanced Chat JavaScript for Research & Freelancing Chatbot

// Global utilities
window.showToast = function(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
};

// LaTeX Processing Utilities
window.processLaTeX = function(text) {
    // Convert LaTeX delimiters for MathJax
    text = text.replace(/\\\[(.*?)\\\]/gs, '$$1$');
    text = text.replace(/\\\((.*?)\\\)/g, '$$1$');
    
    // Handle equation environments
    text = text.replace(/\\begin\{equation\}(.*?)\\end\{equation\}/gs, '$$1$');
    text = text.replace(/\\begin\{align\}(.*?)\\end\{align\}/gs, '$\\begin{align}$1\\end{align}$');
    
    return text;
};

// Code Processing Utilities
window.processCodeBlocks = function(text) {
    // Convert markdown code blocks to HTML
    text = text.replace(/```(\w+)?\n(.*?)```/gs, (match, lang, code) => {
        const language = lang || 'text';
        return `<pre><code class="language-${language}">${code.trim()}</code></pre>`;
    });
    
    // Convert inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    return text;
};

// Enhanced Text Processing
window.processMessageContent = function(content, isAI = false) {
    if (!isAI) return content;
    
    // Process LaTeX first
    content = processLaTeX(content);
    
    // Process code blocks
    content = processCodeBlocks(content);
    
    // Convert URLs to links
    content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    
    // Convert newlines to breaks (but preserve code blocks)
    content = content.replace(/\n/g, '<br>');
    
    // Bold text for emphasis
    content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return content;
};

// Research Mode Utilities
window.ResearchUtils = {
    generateCitation: function(title, authors, year, journal) {
        return `${authors} (${year}). ${title}. <em>${journal}</em>.`;
    },
    
    formatLaTeX: function(latex) {
        return `<div class="math-display">$${latex}$</div>`;
    },
    
    suggestQuestions: function(mode) {
        const suggestions = {
            'data_science': [
                'Help me build a machine learning model for this dataset',
                'What preprocessing steps should I apply?',
                'How do I evaluate model performance?',
                'Suggest feature engineering techniques'
            ],
            'technical_writing': [
                'Help me write technical documentation',
                'Review this API documentation structure',
                'Create a user manual outline',
                'Improve technical content clarity'
            ],
            'general': [
                'What are the latest developments in this field?',
                'Can you help me write a literature review?',
                'What are the mathematical formulations?',
                'How can I implement this solution?'
            ]
        };
        return suggestions[mode] || suggestions['general'];
    }
};

// Freelancing Mode Utilities
window.FreelancingUtils = {
    generateProposal: function(projectType, skills) {
        return {
            intro: "I'm excited to help with your project...",
            experience: `I have extensive experience in ${skills.join(', ')}...`,
            approach: "My approach will be...",
            timeline: "Expected delivery timeline...",
            portfolio: "Relevant portfolio examples..."
        };
    },
    
    estimateProjectTime: function(complexity, scope) {
        const baseHours = {
            'simple': 10,
            'medium': 25,
            'complex': 50,
            'enterprise': 100
        };
        return baseHours[complexity] || 25;
    },
    
    suggestQuestions: function(mode) {
        const questions = {
            'web_development': [
                'How should I price this web development project?',
                'Help me write a proposal for a React application',
                'What technologies should I recommend?',
                'Create a project timeline estimate'
            ],
            'automation': [
                'Price this automation project',
                'Write a web scraping proposal',
                'Estimate time for this workflow',
                'Suggest automation tools'
            ],
            'business_intelligence': [
                'Create a BI dashboard proposal',
                'How to price analytics projects?',
                'Design KPI tracking system',
                'Build executive report structure'
            ],
            'data_visualization': [
                'Create visualization project proposal',
                'Price dashboard development',
                'Suggest chart types for this data',
                'Design interactive report'
            ],
            'api_development': [
                'Price API development project',
                'Write integration proposal',
                'Estimate API project timeline',
                'Suggest API architecture'
            ]
        };
        return questions[mode] || [
            "How should I price this project?",
            "Can you help me write a proposal?",
            "What's the best approach for this?",
            "How can I improve my portfolio?"
        ];
    }
};

// Mode Descriptions for UI
window.ModeDescriptions = {
    'general': 'Professional technical assistant for various tasks',
    'data_science': 'Machine learning, statistical analysis, and predictive modeling',
    'web_development': 'Full-stack development, responsive design, and modern frameworks',
    'automation': 'Process automation, web scraping, and workflow optimization',
    'business_intelligence': 'Dashboards, KPI tracking, and data-driven insights',
    'technical_writing': 'Documentation, API guides, and user manuals',
    'data_visualization': 'Interactive charts, dashboards, and business presentations',
    'api_development': 'REST APIs, integrations, and microservices'
};

// Session Management
window.SessionManager = {
    sessionId: localStorage.getItem('chatSessionId') || null,
    
    generateSessionId: function() {
        const id = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chatSessionId', id);
        this.sessionId = id;
        return id;
    },
    
    getSessionId: function() {
        if (!this.sessionId) {
            return this.generateSessionId();
        }
        return this.sessionId;
    },
    
    clearSession: function() {
        localStorage.removeItem('chatSessionId');
        this.sessionId = null;
    }
};

// File Processing Utilities
window.FileProcessor = {
    supportedTypes: ['.csv', '.xlsx', '.json', '.txt', '.py', '.tex'],
    maxSize: 10 * 1024 * 1024, // 10MB
    
    validateFile: function(file) {
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!this.supportedTypes.includes(ext)) {
            throw new Error(`Unsupported file type: ${ext}`);
        }
        
        if (file.size > this.maxSize) {
            throw new Error(`File too large. Maximum size: ${this.maxSize / 1024 / 1024}MB`);
        }
        
        return true;
    },
    
    getFileIcon: function(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'csv': 'bi-filetype-csv',
            'xlsx': 'bi-filetype-xlsx', 
            'json': 'bi-filetype-json',
            'txt': 'bi-filetype-txt',
            'py': 'bi-filetype-py',
            'tex': 'bi-filetype-tex'
        };
        return icons[ext] || 'bi-file-earmark';
    }
};

// Chat History Management
window.ChatHistory = {
    export: function(sessionId) {
        const messages = Array.from(document.querySelectorAll('.chat-message')).map(msg => ({
            type: msg.classList.contains('user-input') ? 'user' : 'assistant',
            content: msg.textContent,
            html_content: msg.innerHTML,
            timestamp: new Date().toISOString()
        }));
        
        const chatData = {
            session_id: sessionId,
            exported_at: new Date().toISOString(),
            total_messages: messages.length,
            messages: messages
        };
        
        return chatData;
    },
    
    download: function(sessionId, format = 'json') {
        const data = this.export(sessionId);
        let content, mimeType, extension;
        
        if (format === 'json') {
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
            extension = 'json';
        } else if (format === 'txt') {
            content = data.messages.map(msg => 
                `[${msg.type.toUpperCase()}]: ${msg.content}\n`
            ).join('\n');
            mimeType = 'text/plain';
            extension = 'txt';
        }
        
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_export_${new Date().toISOString().split('T')[0]}.${extension}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};

// Performance Monitoring
window.PerformanceMonitor = {
    startTime: null,
    endTime: null,
    
    startTimer: function() {
        this.startTime = performance.now();
    },
    
    endTimer: function() {
        this.endTime = performance.now();
        return this.endTime - this.startTime;
    },
    
    logResponseTime: function() {
        if (this.startTime && this.endTime) {
            const duration = this.endTime - this.startTime;
            console.log(`Response time: ${duration.toFixed(2)}ms`);
        }
    }
};

// Auto-save functionality
window.AutoSave = {
    interval: null,
    
    start: function(sessionId) {
        this.interval = setInterval(() => {
            const chatData = ChatHistory.export(sessionId);
            localStorage.setItem('chatBackup', JSON.stringify(chatData));
        }, 30000); // Save every 30 seconds
    },
    
    stop: function() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    },
    
    restore: function() {
        const backup = localStorage.getItem('chatBackup');
        if (backup) {
            try {
                return JSON.parse(backup);
            } catch (e) {
                console.error('Failed to restore chat backup:', e);
            }
        }
        return null;
    }
};

// Theme Management
window.ThemeManager = {
    currentTheme: localStorage.getItem('chatTheme') || 'light',
    
    init: function() {
        this.applyTheme(this.currentTheme);
    },
    
    toggle: function() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('chatTheme', this.currentTheme);
    },
    
    applyTheme: function(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        
        // Update theme-specific elements
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (theme === 'dark') {
                navbar.classList.remove('navbar-light', 'bg-light');
                navbar.classList.add('navbar-dark', 'bg-dark');
            } else {
                navbar.classList.remove('navbar-dark', 'bg-dark');
                navbar.classList.add('navbar-light', 'bg-light');
            }
        }
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    ThemeManager.init();
    
    // Start auto-save if on chat page
    if (window.location.pathname === '/') {
        const sessionId = SessionManager.getSessionId();
        AutoSave.start(sessionId);
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Alt+T to toggle theme
        if (e.ctrlKey && e.altKey && e.key === 't') {
            e.preventDefault();
            ThemeManager.toggle();
            showToast(`Switched to ${ThemeManager.currentTheme} theme`, 'info');
        }
        
        // Ctrl+Alt+E to export chat
        if (e.ctrlKey && e.altKey && e.key === 'e') {
            e.preventDefault();
            const sessionId = SessionManager.getSessionId();
            ChatHistory.download(sessionId);
        }
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showToast('An unexpected error occurred', 'danger');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('Network error occurred', 'warning');
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    AutoSave.stop();
    
    // Close WebSocket connections
    if (window.chatWebSocket) {
        window.chatWebSocket.close();
    }
});
