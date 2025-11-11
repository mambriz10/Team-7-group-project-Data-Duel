// Highlights the current tab based on filename.
// (We can add more logic later; keeping this tiny for now.)
document.addEventListener('DOMContentLoaded', () => {
  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('nav.tabs a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path) a.classList.add('active');
  });
});


(function () {
  const KEY = 'dd_theme';

  function systemPref() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark' : 'light';
  }

  function applyTheme(t) {
    document.documentElement.dataset.theme = t;
    try { localStorage.setItem(KEY, t); } catch {}
  }

  // Initialize on every page
  const saved = (() => { try { return localStorage.getItem(KEY); } catch { return null; } })();
  applyTheme(saved || systemPref());

  // Wire the Settings dropdown if present
  const select = document.getElementById('theme');
  if (select) {
    select.value = document.documentElement.dataset.theme;
    select.addEventListener('change', () => applyTheme(select.value));
  }
})();