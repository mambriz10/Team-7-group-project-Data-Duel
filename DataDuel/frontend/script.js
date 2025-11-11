// Highlights the current tab based on filename.
// (We can add more logic later; keeping this tiny for now.)
document.addEventListener('DOMContentLoaded', () => {
  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('nav.tabs a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path) a.classList.add('active');
  });
});

