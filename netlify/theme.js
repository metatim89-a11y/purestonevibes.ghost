// Run on load
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    updateAuthUI();
    displayAppVersion();
});

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
    }
}

function toggleTheme() {
    document.body.classList.toggle('light-theme');
    const isLight = document.body.classList.contains('light-theme');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
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

            // Dynamically add the Dashboard link if it isn't there
            if (!document.getElementById('nav-dashboard-link')) {
                const dash = document.createElement('a');
                dash.id = 'nav-dashboard-link';
                dash.href = 'dashboard.html';
                dash.className = 'text-white hover:text-pink-400 transition ml-2 border-b border-pink-500/30 pb-0.5';
                dash.textContent = 'Dashboard';
                // Insert it before the username
                userDisplay.insertBefore(dash, userVal);
            }
        }
    }
}

function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('currentUser');
    window.location.reload();
}

async function displayAppVersion() {
    try {
        const response = await fetch('/version.json');
        if (response.ok) {
            const data = await response.json();
            const versionDiv = document.createElement('div');
            // Fixed to bottom right, subtle text
            versionDiv.className = 'fixed bottom-2 right-2 text-[9px] text-zinc-500 font-mono z-50 pointer-events-none opacity-50 tracking-widest';
            versionDiv.textContent = `v${data.version}`;
            document.body.appendChild(versionDiv);
        }
    } catch (e) {
        console.error("Failed to load app version", e);
    }
}
