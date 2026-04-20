/**
 * Credits Gallery Embed
 * Usage: <div id="mm-credits"></div>
 *        <script src="credits-embed.js"></script>
 */
(function () {
  const DATA_URL = 'https://hyraniemus.github.io/NEWS-MM/data/credits.json';
  const BASE_URL = 'https://hyraniemus.github.io/NEWS-MM/';

  const CSS = `
    #mm-credits * { box-sizing: border-box; margin: 0; padding: 0; }
    #mm-credits {
      --bg:       #0a0a0a;
      --surface:  #141414;
      --border:   rgba(255,255,255,0.07);
      --text:     #e8e8e8;
      --muted:    #666;
      --mono:     'Space Mono','IBM Plex Mono','Courier New',monospace;
      --sans:     'Inter',system-ui,sans-serif;
      font-family: var(--sans);
    }
    .mm-filter-bar {
      display: flex; gap: 0.25rem; flex-wrap: wrap;
      margin-bottom: 2rem;
    }
    .mm-filter-btn {
      padding: 0.3rem 0.75rem;
      border: 1px solid transparent;
      border-radius: 2px;
      background: transparent;
      color: var(--muted);
      font-family: var(--mono);
      font-size: 0.6875rem;
      letter-spacing: 0.08em;
      text-transform: lowercase;
      cursor: pointer;
      transition: all 0.2s;
    }
    .mm-filter-btn:hover { color: #aaa; border-color: rgba(255,255,255,0.12); }
    .mm-filter-btn.active { color: var(--text); border-color: rgba(255,255,255,0.15); background: rgba(255,255,255,0.05); }
    .mm-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1px;
      background: var(--border);
      border: 1px solid var(--border);
    }
    @media (max-width: 1024px) { .mm-grid { grid-template-columns: repeat(3,1fr); } }
    @media (max-width: 680px)  { .mm-grid { grid-template-columns: repeat(2,1fr); } }
    @media (max-width: 380px)  { .mm-grid { grid-template-columns: 1fr; } }
    .mm-card {
      position: relative;
      background: var(--surface);
      cursor: default;
      transition: background 0.2s;
      display: flex; flex-direction: column;
    }
    .mm-card:hover { background: #1a1a1a; }
    .mm-card[data-url] { cursor: pointer; }
    .mm-img-wrap {
      position: relative;
      aspect-ratio: 2/3;
      overflow: hidden;
    }
    .mm-img-wrap img {
      width:100%; height:100%; object-fit:cover;
      transition: transform 0.5s ease;
    }
    .mm-card:hover .mm-img-wrap img { transform: scale(1.04); }
    .mm-badge {
      position: absolute; top: 0.5rem; right: 0.5rem; z-index: 10;
      height: 24px; min-width: 40px;
      display: flex; align-items: center; justify-content: center;
      border-radius: 2px; padding: 0 5px;
      font-family: var(--mono); font-size: 0.625rem;
      font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;
    }
    .mm-bc-ARD  { background:#003CA6; color:#fff; }
    .mm-bc-ZDF  { background:#FF6600; color:#fff; }
    .mm-bc-RTLP { background:#E40046; color:#fff; font-style:italic; }
    .mm-bc-Sky  { background:#000; color:#fff; border:1px solid #444; }
    .mm-bc-Joyn { background:#FF5C00; color:#fff; }
    .mm-bc-kino { background:rgba(255,255,255,0.1); color:rgba(255,255,255,0.6); border:1px solid rgba(255,255,255,0.12); }
    .mm-bc-TV   { background:rgba(255,255,255,0.1); color:rgba(255,255,255,0.6); border:1px solid rgba(255,255,255,0.12); }
    .mm-overlay {
      position: absolute; inset: 0;
      background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.35) 45%, transparent 100%);
      display: flex; flex-direction: column; justify-content: flex-end;
      padding: 1rem; opacity: 0; transition: opacity 0.22s;
    }
    .mm-card:hover .mm-overlay { opacity: 1; }
    .mm-overlay-role {
      font-family: var(--mono); font-size: 0.625rem;
      letter-spacing: 0.12em; text-transform: uppercase; color: #fff;
      margin-bottom: 0.25rem;
    }
    .mm-overlay-prod { font-size: 0.7rem; color: rgba(255,255,255,0.45); margin-bottom: 0.625rem; }
    .mm-overlay-link {
      display: inline-flex; align-items: center; gap: 0.3rem;
      font-family: var(--mono); font-size: 0.5625rem; letter-spacing: 0.1em;
      text-transform: lowercase; color: #aaa; text-decoration: none;
      border: 1px solid rgba(255,255,255,0.2); padding: 0.2rem 0.5rem;
      width: fit-content; transition: all 0.2s;
    }
    .mm-overlay-link:hover { color: #fff; border-color: rgba(255,255,255,0.5); }
    .mm-meta { padding: 0.625rem 0.875rem; }
    .mm-title {
      font-size: 0.8125rem; font-weight: 500; color: var(--text);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .mm-sub { display: flex; align-items: center; gap: 0.4rem; margin-top: 0.25rem; }
    .mm-year { font-family: var(--mono); font-size: 0.6875rem; color: var(--muted); }
    .mm-type {
      font-family: var(--mono); font-size: 0.5625rem; letter-spacing: 0.06em;
      text-transform: lowercase; color: var(--muted);
    }
    .mm-type::before { content: "( "; }
    .mm-type::after  { content: " )"; }
    .mm-placeholder {
      width:100%; height:100%; display:flex; flex-direction:column;
      align-items:center; justify-content:center; gap:0.5rem;
      background:#111; color:#333;
      font-family:var(--mono); font-size:0.625rem; letter-spacing:0.06em;
      text-align:center; padding:1rem;
    }
  `;

  const BC_LABEL = { ARD:'ARD', ZDF:'ZDF', 'RTL+':'RTL+', Sky:'Sky', Joyn:'Joyn', kino:'▶ Kino', TV:'TV' };
  const BC_CLASS = { ARD:'mm-bc-ARD', ZDF:'mm-bc-ZDF', 'RTL+':'mm-bc-RTLP', Sky:'mm-bc-Sky', Joyn:'mm-bc-Joyn', kino:'mm-bc-kino', TV:'mm-bc-TV' };

  function esc(s) {
    return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function card(p) {
    const poster  = p.poster ? BASE_URL + p.poster.replace(/^\//, '') : '';
    const hasLink = p.crewUnited;
    const bc      = p.broadcaster || '';
    const badge   = bc ? `<span class="mm-badge ${BC_CLASS[bc]||'mm-bc-TV'}">${BC_LABEL[bc]||esc(bc)}</span>` : '';
    const img     = poster
      ? `<img src="${esc(poster)}" alt="${esc(p.title)}" loading="lazy">`
      : `<div class="mm-placeholder">${esc(p.title)}</div>`;
    const link    = hasLink
      ? `<a class="mm-overlay-link" href="${esc(p.crewUnited)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">crew-united ↗</a>`
      : '';

    return `<article class="mm-card"${hasLink ? ` data-url="${esc(p.crewUnited)}"` : ''}>
      <div class="mm-img-wrap">
        ${img}${badge}
        <div class="mm-overlay">
          <p class="mm-overlay-role">${esc(p.role)}</p>
          ${p.production ? `<p class="mm-overlay-prod">${esc(p.production)}</p>` : ''}
          ${link}
        </div>
      </div>
      <div class="mm-meta">
        <p class="mm-title" title="${esc(p.title)}">${esc(p.title)}</p>
        <div class="mm-sub">
          <span class="mm-year">${esc(String(p.year||''))}</span>
          ${p.type ? `<span class="mm-type">${esc(p.type)}</span>` : ''}
        </div>
      </div>
    </article>`;
  }

  function render(projects, grid) {
    if (!projects.length) { grid.innerHTML = '<p style="color:#444;padding:2rem;font-family:monospace">Keine Projekte.</p>'; return; }
    grid.innerHTML = projects.map(card).join('');
    grid.querySelectorAll('.mm-card[data-url]').forEach(c => {
      c.addEventListener('click', () => window.open(c.dataset.url, '_blank', 'noopener'));
    });
  }

  async function init() {
    const root = document.getElementById('mm-credits');
    if (!root) return;

    // Inject CSS once
    if (!document.getElementById('mm-credits-css')) {
      const style = document.createElement('style');
      style.id = 'mm-credits-css';
      style.textContent = CSS;
      document.head.appendChild(style);
    }

    // Fetch data
    let projects = [];
    try {
      const r = await fetch(DATA_URL);
      projects = (await r.json()).projects || [];
      projects.sort((a, b) => b.year - a.year);
    } catch (e) {
      root.innerHTML = '<p style="color:#666;font-family:monospace;padding:1rem">Credits konnten nicht geladen werden.</p>';
      return;
    }

    // Filter bar
    const bar = document.createElement('div');
    bar.className = 'mm-filter-bar';
    bar.innerHTML = ['all','Kinofilm','Serie','Dokumentation'].map((f,i) =>
      `<button class="mm-filter-btn${i===0?' active':''}" data-f="${f}">${f==='all'?'Alle':f==='Kinofilm'?'Kino':f==='Dokumentation'?'Doku':f}</button>`
    ).join('');

    const grid = document.createElement('div');
    grid.className = 'mm-grid';

    root.appendChild(bar);
    root.appendChild(grid);
    render(projects, grid);

    bar.addEventListener('click', e => {
      const btn = e.target.closest('.mm-filter-btn');
      if (!btn) return;
      bar.querySelectorAll('.mm-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const f = btn.dataset.f;
      render(f === 'all' ? projects : projects.filter(p => p.type === f), grid);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
