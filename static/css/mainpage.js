// static/css/mainpage.js

// ——— Mobile menu toggle —————————————————
const btn = document.querySelector('.hamburger');
const nav = document.querySelector('.main-nav');
if (btn && nav) {
  btn.addEventListener('click', () => nav.classList.toggle('open'));
}

// ——— Counter animation —————————————————
const counters = document.querySelectorAll('.count');
const speed    = 200;
counters.forEach(counter => {
  const update = () => {
    const target = +counter.getAttribute('data-target');
    const count  = +counter.innerText;
    const inc    = Math.ceil(target / speed);
    if (count < target) {
      counter.innerText = count + inc;
      setTimeout(update, 20);
    } else {
      counter.innerText = target;
    }
  };
  update();
});

// ——— Live search filter ——————————————
const searchInput = document.getElementById('post-search');
const cards       = document.querySelectorAll('.post-card');

if (searchInput) {
  searchInput.addEventListener('input', e => {
    const q = e.target.value.trim().toLowerCase();
    cards.forEach(card => {
      const title = card.dataset.title || '';
      // hide when no match, otherwise reset to default display
      card.style.display = title.includes(q) ? '' : 'none';
    });
  });
}
