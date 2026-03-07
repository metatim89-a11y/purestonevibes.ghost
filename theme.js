const APP_VERSION = "v1.051";
// Run on load
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    updateAuthUI();
    injectChatWidget();
});

/**
 * Dynamically injects the Live Chat widget into the page.
 * Why: This allows all pages to share the chat functionality without 
 * repeating the HTML markup in every file.
 */
function injectChatWidget() {
    const chatContainer = document.createElement('div');
    chatContainer.innerHTML = `
        <div id="chat-bubble" onclick="toggleChat()" title="Contact Fish Live">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
            </svg>
        </div>
        <div id="chat-box" class="glass-panel">
            <div class="chat-header">
                <div>
                    <h4 class="font-bold text-sm tracking-widest uppercase">Live Connection</h4>
                    <p class="text-[9px] opacity-70">Fish is usually online</p>
                </div>
                <button onclick="toggleChat()" class="opacity-50 hover:opacity-100 transition">&times;</button>
            </div>
            <div id="chat-messages" class="chat-messages">
                <div class="message fish">Peace be with you. How can I help you connect with a stone today?</div>
            </div>
            <div class="chat-input-area">
                <input type="text" id="chat-input" class="chat-input" placeholder="Type your vibration..." onkeypress="if(event.key==='Enter') sendChatMessage()">
                <button onclick="sendChatMessage()" class="chat-send">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                    </svg>
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(chatContainer);
}

function toggleChat() {
    const box = document.getElementById('chat-box');
    const isOpening = !box.classList.contains('open');

    if (isOpening) {
        box.style.display = 'flex';
        setTimeout(() => box.classList.add('open'), 10);
    } else {
        box.classList.remove('open');
        setTimeout(() => box.style.display = 'none', 500);
    }
}

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    const container = document.getElementById('chat-messages');

    // User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'message user';
    userDiv.textContent = msg;
    container.appendChild(userDiv);

    input.value = '';
    container.scrollTop = container.scrollHeight;

    // Simulate "Fish" response
    setTimeout(() => {
        const fishDiv = document.createElement('div');
        fishDiv.className = 'message fish';
        fishDiv.textContent = "Thank you for sharing that energy. Fish will respond to you personally very soon.";
        container.appendChild(fishDiv);
        container.scrollTop = container.scrollHeight;
    }, 1500);
}

/**
 * VIBE SYSTEM: Multi-theme cycling
 */
const VIBES = ['vibe-rose', 'vibe-amethyst', 'vibe-emerald', 'vibe-sapphire', 'vibe-amber'];

function initTheme() {
    const savedVibe = localStorage.getItem('currentVibe') || 'vibe-rose';
    applyVibe(savedVibe);
}

function toggleTheme() {
    const currentVibe = localStorage.getItem('currentVibe') || 'vibe-rose';
    const currentIndex = VIBES.indexOf(currentVibe);
    const nextIndex = (currentIndex + 1) % VIBES.length;
    const nextVibe = VIBES[nextIndex];
    
    applyVibe(nextVibe);
}

function applyVibe(vibeClass) {
    // Remove all vibe classes
    VIBES.forEach(v => document.body.classList.remove(v));
    
    // Add new one (rose is the base, so we don't need a class for it if it's the default)
    if (vibeClass !== 'vibe-rose') {
        document.body.classList.add(vibeClass);
    }
    
    localStorage.setItem('currentVibe', vibeClass);
    console.log(`Vibe Shift: ${vibeClass.replace('vibe-', '')}`);
}

function updateAuthUI() {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const loginBtn = document.getElementById('login-link');
    const userDisplay = document.getElementById('user-display');

    if (isLoggedIn) {
        if (loginBtn) loginBtn.classList.add('hidden');
        if (userDisplay) {
            userDisplay.classList.remove('hidden');
            const userVal = document.getElementById('username-val');
            if (userVal) userVal.textContent = localStorage.getItem('currentUser');
        }
    }
}

function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('currentUser');
    window.location.reload();
}
