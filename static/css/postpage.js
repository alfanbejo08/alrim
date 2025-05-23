// Add header scroll effect
window.addEventListener('scroll', () => {
  const header = document.querySelector('.site-header');
  const scrollY = window.scrollY;

  // Add the 'scrolled' class when the user scrolls down
  if (scrollY > 100) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});

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
