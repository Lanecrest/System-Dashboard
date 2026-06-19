// Theme Switching Behavior
const savedTheme = localStorage.getItem('dashboard-theme') || 'P1';
document.documentElement.setAttribute('theme', savedTheme);

export function initThemeToggle() {
    const themeButton = document.getElementById('theme-toggle');
    if (!themeButton) return;

    const currentTheme = document.documentElement.getAttribute('theme');
    themeButton.innerText = currentTheme === 'P3' ? 'P1 Phosphor' : 'P3 Phosphor';

    themeButton.addEventListener('click', () => {
        const activeTheme = document.documentElement.getAttribute('theme');
        
        if (activeTheme === 'P3') {
            document.documentElement.setAttribute('theme', 'P1');
            themeButton.innerText = 'P3 Phosphor';
            localStorage.setItem('dashboard-theme', 'P1');
        }
        else {
            document.documentElement.setAttribute('theme', 'P3');
            themeButton.innerText = 'P1 Phosphor';
            localStorage.setItem('dashboard-theme', 'P3');
        }
    });
}

// Card Collapse Behavior
export function initCardCollapse() {
    document.querySelectorAll('.card .title').forEach(title => {
        title.addEventListener('click', () => {
            title.parentElement.classList.toggle('collapsed');
        });
    });
}