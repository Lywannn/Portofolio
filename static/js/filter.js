document.addEventListener('DOMContentLoaded', () => {
  const grid = document.getElementById('projectsGrid');
  const searchInput = document.getElementById('searchInput');
  const langBtns = document.querySelectorAll('#filterLangs .filter-btn');
  const visibleCount = document.getElementById('visibleCount');
  const noResults = document.getElementById('noResults');

  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll('.project-card'));
  let activeLang = 'all';
  let searchQuery = '';

  function updateURL() {
    const params = new URLSearchParams();
    if (activeLang !== 'all') params.set('lang', activeLang);
    if (searchQuery) params.set('q', searchQuery);
    const str = params.toString();
    history.replaceState(null, '', str ? `?${str}` : window.location.pathname);
  }

  function applyFilters() {
    let count = 0;
    cards.forEach(card => {
      const lang = card.dataset.lang || '';
      const name = (card.dataset.name || '').toLowerCase();
      const desc = (card.dataset.desc || '').toLowerCase();
      const q = searchQuery.toLowerCase();

      const langMatch = activeLang === 'all' || lang === activeLang;
      const searchMatch = !q || name.includes(q) || desc.includes(q);

      const show = langMatch && searchMatch;
      card.style.display = show ? '' : 'none';
      if (show) count++;
    });

    if (visibleCount) visibleCount.textContent = count;
    if (noResults) noResults.classList.toggle('hidden', count > 0);
    updateURL();
  }

  langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      langBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeLang = btn.dataset.lang;
      applyFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      searchQuery = searchInput.value;
      applyFilters();
    });
  }

  // Restore from URL params
  const params = new URLSearchParams(window.location.search);
  if (params.get('lang')) {
    activeLang = params.get('lang');
    langBtns.forEach(b => {
      b.classList.toggle('active', b.dataset.lang === activeLang);
    });
  }
  if (params.get('q') && searchInput) {
    searchQuery = params.get('q');
    searchInput.value = searchQuery;
  }
  applyFilters();
});
