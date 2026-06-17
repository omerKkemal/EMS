  // Mobile menu toggle
const btn = document.querySelector('.mobile-menu-button');
if (btn) {
    btn.addEventListener('click', () => {
        const menu = document.querySelector('.md\\:flex');
        if (menu) menu.classList.toggle('hidden');
    });
}

// Admin dropdown toggle
function toggleDropdown() {
    const dropdown = document.getElementById('adminDropdown');
    dropdown.classList.toggle('hidden');
}

// Close dropdown when clicking outside
window.addEventListener('click', function(e) {
    const dropdown = document.getElementById('adminDropdown');
    const adminButton = document.querySelector('button[onclick="toggleDropdown()"]');
    if (dropdown && !dropdown.classList.contains('hidden')) {
        if (!dropdown.contains(e.target) && !adminButton.contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    }
});