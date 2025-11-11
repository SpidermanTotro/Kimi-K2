// THE FORGE AI - Splash Screen Animation Controller

let splashProgress = 0;
let splashComplete = false;

document.addEventListener('DOMContentLoaded', () => {
    console.log('🔥 THE FORGE AI - Starting Epic Splash Sequence...');
    startSplashSequence();
});

async function startSplashSequence() {
    // Animate stats counting up
    animateStats();
    
    // Sequence of system status updates
    await activateStatus(1, 'status1', 500);
    await updateProgress(15, 'Loading Neural Networks...');
    
    await activateStatus(2, 'status2', 800);
    await updateProgress(35, 'Knowledge Base Loaded...');
    
    await activateStatus(3, 'status3', 600);
    await updateProgress(55, 'Capabilities Activated...');
    
    await activateStatus(4, 'status4', 700);
    await updateProgress(75, '16GB KING Configuration Ready...');
    
    await activateStatus(5, 'status5', 900);
    await updateProgress(95, 'Intelligence Modules Calibrated...');
    
    await delay(500);
    await updateProgress(100, 'SYSTEM READY - MAXIMUM POWER!');
    
    await delay(1000);
    
    // Fade out splash, fade in main app
    completeSplash();
}

function animateStats() {
    // Capabilities counter
    animateCounter('capabilitiesLoading', 0, 865, 2000);
    
    // Documents counter
    animateCounter('documentsLoading', 0, 15, 1500);
    
    // Power level
    animatePowerLevel();
}

function animateCounter(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startTime = Date.now();
    const range = end - start;
    
    function update() {
        const now = Date.now();
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (range * easeOut));
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = end;
        }
    }
    
    requestAnimationFrame(update);
}

function animatePowerLevel() {
    const element = document.getElementById('powerLoading');
    if (!element) return;
    
    let power = 0;
    const interval = setInterval(() => {
        power += 2;
        if (power > 100) {
            power = 100;
            clearInterval(interval);
        }
        element.textContent = power + '%';
    }, 30);
}

async function activateStatus(index, statusId, duration) {
    const statusElement = document.getElementById(statusId);
    if (statusElement) {
        statusElement.classList.add('active');
        
        // Add typing effect to the text
        const text = statusElement.querySelector('span').textContent;
        statusElement.querySelector('span').textContent = '';
        
        for (let i = 0; i < text.length; i++) {
            await delay(20);
            statusElement.querySelector('span').textContent += text[i];
        }
    }
    
    return delay(duration);
}

async function updateProgress(percent, statusText) {
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressStatus = document.getElementById('progressStatus');
    
    if (progressFill) {
        progressFill.style.width = percent + '%';
    }
    
    if (progressPercent) {
        // Animate percentage
        const currentPercent = parseInt(progressPercent.textContent) || 0;
        await animatePercentage(currentPercent, percent, 500);
    }
    
    if (progressStatus && statusText) {
        progressStatus.textContent = statusText;
    }
    
    return delay(300);
}

async function animatePercentage(start, end, duration) {
    const element = document.getElementById('progressPercent');
    const startTime = Date.now();
    const range = end - start;
    
    return new Promise(resolve => {
        function update() {
            const now = Date.now();
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOut = 1 - Math.pow(1 - progress, 2);
            const current = Math.floor(start + (range * easeOut));
            
            element.textContent = current + '%';
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = end + '%';
                resolve();
            }
        }
        requestAnimationFrame(update);
    });
}

function completeSplash() {
    const splash = document.getElementById('splashScreen');
    const mainApp = document.getElementById('mainApp');
    
    if (splash && mainApp) {
        // Fade out splash
        splash.style.transition = 'opacity 1s ease-out';
        splash.style.opacity = '0';
        
        setTimeout(() => {
            splash.style.display = 'none';
            mainApp.style.display = 'flex';
            mainApp.style.opacity = '0';
            mainApp.style.flexDirection = 'column';
            
            // Fade in main app
            setTimeout(() => {
                mainApp.style.transition = 'opacity 0.8s ease-in';
                mainApp.style.opacity = '1';
                
                // Initialize main application
                initializeMainApp();
            }, 50);
        }, 1000);
    }
}

async function initializeMainApp() {
    console.log('✅ Main application loaded - THE FORGE AI is ready!');
    
    // Initialize the main app
    if (typeof initializeApp === 'function') {
        initializeApp();
    }
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Power option hover effects
document.addEventListener('DOMContentLoaded', () => {
    const powerOptions = document.querySelectorAll('.power-option');
    
    powerOptions.forEach(option => {
        option.addEventListener('mouseenter', () => {
            const fill = option.querySelector('.power-fill');
            if (fill && !fill.classList.contains('active')) {
                fill.style.width = '100%';
                fill.style.background = 'linear-gradient(90deg, #666, #999)';
            }
        });
        
        option.addEventListener('mouseleave', () => {
            const fill = option.querySelector('.power-fill');
            if (fill && !fill.classList.contains('active')) {
                fill.style.width = '0%';
            }
        });
    });
});
