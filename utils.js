/* =============================================
   RESUME KOMBAT AI — FOOTER & SHARED INCLUDES
   ============================================= */

// Inject site footer into pages that need it
function injectFooter() {
  // Check if footer already exists
  if (document.querySelector('.site-footer')) return;

  const footer = document.createElement('footer');
  footer.className = 'site-footer';
  footer.innerHTML = `
    <div class="footer-inner">
      <div class="footer-brand">
        <div class="footer-logo">
          <span class="logo-rk">RK</span>
          <span class="logo-text">RESUME<span class="logo-accent">KOMBAT</span> AI</span>
        </div>
        <p class="footer-desc">AI-powered resume battle platform for modern recruiters and job seekers.</p>
      </div>
      <div class="footer-links">
        <div class="footer-col">
          <div class="footer-col-title">Product</div>
          <a href="battle.html" class="footer-link">Battle Arena</a>
          <a href="tournament.html" class="footer-link">Tournament</a>
          <a href="analytics.html" class="footer-link">Analytics</a>
        </div>
        <div class="footer-col">
          <div class="footer-col-title">Info</div>
          <a href="about.html" class="footer-link">About</a>
          <a href="about.html#how" class="footer-link">How It Works</a>
          <a href="about.html#tech" class="footer-link">Tech Stack</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2025 Resume Kombat AI — Built with Claude AI</span>
      <span class="footer-sep">|</span>
      <span>Original IP. No copyrighted assets.</span>
    </div>
  `;
  document.body.appendChild(footer);
}

// Active nav highlighting
function highlightActiveNav() {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    link.classList.toggle('active', href === path);
  });
}

// Page transition effect
function initPageTransitions() {
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    // Only internal links, not anchors or external
    if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto')) return;
    link.addEventListener('click', function(e) {
      // Allow normal navigation but add a tiny fade
      document.body.style.transition = 'opacity 0.15s';
      document.body.style.opacity = '0';
      setTimeout(() => {
        document.body.style.opacity = '';
        document.body.style.transition = '';
      }, 200);
    });
  });
}

// Toast notification system
function showToast(message, type = 'info') {
  const existing = document.getElementById('rk-toast');
  if (existing) existing.remove();

  const colors = {
    info: 'var(--neon-cyan)',
    success: 'var(--neon-green)',
    error: 'var(--neon-orange)',
    warning: 'var(--neon-yellow)'
  };

  const toast = document.createElement('div');
  toast.id = 'rk-toast';
  toast.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:9999;
    background:var(--bg-card); border:1px solid ${colors[type]};
    border-radius:var(--radius-sm); padding:12px 20px;
    font-family:var(--font-head); font-size:11px; letter-spacing:1px;
    color:${colors[type]}; max-width:320px;
    box-shadow:0 0 20px rgba(0,0,0,0.5);
    animation:fadeInUp 0.3s ease both;
    transition: opacity 0.3s ease;
  `;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Copy to clipboard utility
async function copyToClipboard(text, label = 'Copied') {
  try {
    await navigator.clipboard.writeText(text);
    showToast(`✓ ${label}`, 'success');
  } catch {
    showToast('Copy failed — try manual copy', 'error');
  }
}

// Smooth scroll to section
function scrollTo(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Print / export battle results
function printResults() {
  window.print();
}

// Check if mobile
function isMobile() {
  return window.innerWidth < 768;
}

// Format large numbers
function formatNum(n) {
  if (n >= 1000000) return (n/1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n/1000).toFixed(1) + 'K';
  return String(n);
}

// Debounce
function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// Init on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  injectFooter();
  highlightActiveNav();
  initPageTransitions();

  // Fade in body
  document.body.style.opacity = '0';
  requestAnimationFrame(() => {
    document.body.style.transition = 'opacity 0.3s ease';
    document.body.style.opacity = '1';
    setTimeout(() => { document.body.style.transition = ''; }, 400);
  });
});