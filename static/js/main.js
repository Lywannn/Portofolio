document.addEventListener('DOMContentLoaded', () => {
  // Scroll reveal
  const observer = new IntersectionObserver(
    (entries) => entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } }),
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );
  document.querySelectorAll('.reveal').forEach((el, i) => {
    el.style.transitionDelay = `${Math.min(i % 6 * 60, 300)}ms`;
    observer.observe(el);
  });

  // Back to top
  const btt = document.getElementById('backToTop');
  if (btt) {
    window.addEventListener('scroll', () => btt.classList.toggle('visible', window.scrollY > 300), { passive: true });
    btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // Navbar shadow on scroll
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.style.boxShadow = window.scrollY > 10 ? 'var(--shadow-md)' : '';
    }, { passive: true });
  }

  // Hamburger menu
  const ham = document.getElementById('hamburger');
  const menu = document.getElementById('mobileMenu');
  if (ham && menu) {
    ham.addEventListener('click', () => {
      ham.classList.toggle('open');
      menu.classList.toggle('open');
    });
  }

  // Lang dot colors in filter buttons
  document.querySelectorAll('.filter-btn .lang-dot').forEach(dot => {
    const lang = dot.closest('[data-lang]')?.dataset.lang || dot.dataset.lang;
    if (lang) dot.setAttribute('data-lang', lang);
  });
});
