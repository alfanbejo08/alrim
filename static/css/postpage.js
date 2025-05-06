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
