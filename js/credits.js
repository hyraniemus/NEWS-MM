(async () => {
  const grid = document.getElementById('creditsGrid');
  const filterBar = document.getElementById('filterBar');

  let allProjects = [];
  let activeFilter = 'all';

  // ── Load data ────────────────────────────────────────────────────────
  try {
    const res = await fetch('data/credits.json');
    if (!res.ok) throw new Error(res.status);
    const data = await res.json();
    allProjects = data.projects ?? [];
  } catch (err) {
    grid.innerHTML = `<p class="empty-state">Projektdaten konnten nicht geladen werden.</p>`;
    return;
  }

  // Sort descending by year
  allProjects.sort((a, b) => b.year - a.year);

  // ── Render ───────────────────────────────────────────────────────────
  function render(projects) {
    if (!projects.length) {
      grid.innerHTML = `<p class="empty-state">Keine Projekte in dieser Kategorie.</p>`;
      return;
    }

    grid.innerHTML = projects.map(p => buildCard(p)).join('');

    // Open crew-united link on card click (if URL present)
    grid.querySelectorAll('.poster-card[data-url]').forEach(card => {
      card.addEventListener('click', () => {
        window.open(card.dataset.url, '_blank', 'noopener,noreferrer');
      });
    });
  }

  function buildCard(p) {
    const hasImage = p.poster && p.poster.trim();
    const hasLink  = p.crewUnited && p.crewUnited.trim();
    const typeLabel = escHtml(p.type ?? '');
    const year     = escHtml(String(p.year ?? ''));
    const title    = escHtml(p.title ?? '');
    const role     = escHtml(p.role ?? '');
    const prod     = escHtml(p.production ?? '');

    const imageContent = hasImage
      ? `<img src="${escHtml(p.poster)}" alt="Filmplakat ${title}" loading="lazy">`
      : `<div class="poster-placeholder">
           <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
             <rect x="2" y="3" width="20" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
             <polyline points="21 15 16 10 5 21"/>
           </svg>
           <span>${title}</span>
         </div>`;

    const linkContent = hasLink
      ? `<a class="overlay-link" href="${escHtml(p.crewUnited)}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation()">
           <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
             <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
           </svg>
           crew-united
         </a>`
      : '';

    return `
      <article class="poster-card" ${hasLink ? `data-url="${escHtml(p.crewUnited)}"` : ''}>
        <div class="poster-image-wrap">
          ${imageContent}
          <div class="poster-overlay">
            <p class="overlay-role">${role}</p>
            ${prod ? `<p class="overlay-production">${prod}</p>` : ''}
            ${linkContent}
          </div>
        </div>
        <div class="poster-meta">
          <p class="poster-meta-title" title="${title}">${title}</p>
          <div class="poster-meta-sub">
            <span class="poster-year">${year}</span>
            ${typeLabel ? `<span class="poster-type">${typeLabel}</span>` : ''}
          </div>
        </div>
      </article>`;
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // ── Filter ───────────────────────────────────────────────────────────
  filterBar?.addEventListener('click', e => {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;

    activeFilter = btn.dataset.filter;
    filterBar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const filtered = activeFilter === 'all'
      ? allProjects
      : allProjects.filter(p => p.type === activeFilter);

    render(filtered);
  });

  render(allProjects);
})();
