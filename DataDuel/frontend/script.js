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

  // Make applyTheme available globally for theme toggle button
  window.applyTheme = applyTheme;
})();

// Theme toggle button functionality
(function() {
  // Create theme toggle button if it doesn't exist
  function createThemeToggle() {
    const existing = document.getElementById('themeToggle');
    if (existing) return;
    
    const toggle = document.createElement('button');
    toggle.id = 'themeToggle';
    toggle.className = 'theme-toggle';
    toggle.setAttribute('aria-label', 'Toggle dark mode');
    toggle.innerHTML = '<span id="themeIcon">🌙</span>';
    
    // Find header or create one
    let header = document.querySelector('.header');
    if (!header) {
      header = document.createElement('header');
      header.className = 'header';
      
      // Try to get page title from h1 in main content
      const mainTitle = document.querySelector('main .card h1');
      let titleText;
      if (mainTitle) {
        titleText = mainTitle.textContent;
      } else {
        // Fallback title based on page
        const path = location.pathname.split('/').pop() || 'index.html';
        const pageTitles = {
          'index.html': 'DataDuel',
          'profile.html': 'Profile',
          'settings.html': 'Settings',
          'social.html': 'Social',
          'routes.html': 'Routes',
          'leaderboards.html': 'Leaderboards',
          'login.html': 'Login',
          'register.html': 'Register',
          'profile-challenges.html': 'Challenges & Badges',
          'profile-stats.html': 'Stats',
          'profile-edit.html': 'Edit Profile',
          'Strava.html': 'Connect Strava'
        };
        titleText = pageTitles[path] || 'DataDuel';
      }
      
      header.innerHTML = `<h1>${titleText}</h1>`;
      
      document.body.insertBefore(header, document.body.firstChild);
    }
    
    header.appendChild(toggle);
    
    // Update icon based on current theme
    function updateIcon() {
      const icon = document.getElementById('themeIcon');
      if (!icon) return;
      const theme = document.documentElement.dataset.theme;
      icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    
    toggle.addEventListener('click', () => {
      const current = document.documentElement.dataset.theme;
      const newTheme = current === 'dark' ? 'light' : 'dark';
      if (window.applyTheme) {
        window.applyTheme(newTheme);
      } else {
        document.documentElement.dataset.theme = newTheme;
        try { localStorage.setItem('dd_theme', newTheme); } catch {}
      }
      updateIcon();
      
      // Also update settings dropdown if present
      const select = document.getElementById('theme');
      if (select) {
        select.value = newTheme;
      }
    });
    
    // Initial icon update
    updateIcon();
    
    // Watch for theme changes
    const observer = new MutationObserver(updateIcon);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });
  }
  
  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createThemeToggle);
  } else {
    createThemeToggle();
  }
})();