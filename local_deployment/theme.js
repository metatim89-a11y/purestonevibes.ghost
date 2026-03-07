// Run on load
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    updateAuthUI();
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
        }
    }
}

function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('currentUser');
    window.location.reload();
}
