// Mobile menu toggle
const btn = document.querySelector('.hamburger');
const nav = document.querySelector('.main-nav');
btn?.addEventListener('click', () => {
  nav.classList.toggle('open');
});

// Counter animation
const counters = document.querySelectorAll('.count');
const speed = 200; // lower = faster

counters.forEach(counter => {
  const update = () => {
    const target = +counter.getAttribute('data-target');
    const count = +counter.innerText;
    const inc = Math.ceil(target / speed);
    if (count < target) {
      counter.innerText = count + inc;
      setTimeout(update, 20);
    } else {
      counter.innerText = target;
    }
  };
  update();
});
