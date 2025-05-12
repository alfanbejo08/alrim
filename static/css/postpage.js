// Mobile menu toggle (re-used)
const btn = document.querySelector('.hamburger');
const nav = document.querySelector('.main-nav');
btn?.addEventListener('click', () => {
  nav.classList.toggle('open');
});

// Smooth scroll for in-page links (optional enhancement)
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    document.querySelector(link.getAttribute('href'))
            ?.scrollIntoView({ behavior: 'smooth' });
  });
});

// Fade In Content when Scrolling
const content = document.querySelectorAll('.post-card');
window.addEventListener('scroll', () => {
  content.forEach(item => {
    const position = item.getBoundingClientRect().top;
    const windowHeight = window.innerHeight;
    if (position < windowHeight - 100) {
      item.classList.add('active');
    }
  });
});
// Get the theme toggle button and body element
const themeToggleButton = document.getElementById('theme-toggle');
const body = document.body;

// Load user’s theme preference from localStorage
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
  body.classList.add(savedTheme);
} else {
  // Default to dark mode if no preference is saved
  body.classList.add('dark-mode');
}

// Toggle theme when button is clicked
themeToggleButton.addEventListener('click', () => {
  if (body.classList.contains('dark-mode')) {
    body.classList.replace('dark-mode', 'light-mode');
    localStorage.setItem('theme', 'light-mode');
  } else {
    body.classList.replace('light-mode', 'dark-mode');
    localStorage.setItem('theme', 'dark-mode');
  }
});
