window.hallmarkSlots = (m) => { for (const [k, v] of Object.entries(m)) { const s = document.querySelector(`[data-slot="${k}"]`); if (!s) continue; const im = new Image(); im.src = typeof v === 'string' ? v : v.src; im.alt = (typeof v === 'object' && v.alt) || s.dataset.alt || ''; s.querySelectorAll(':scope > img').forEach((o) => o.remove()); s.prepend(im); } };
document.querySelectorAll('[data-slot] img').forEach((i) => { if (i.complete && !i.naturalWidth) i.remove(); else i.addEventListener('error', () => i.remove(), { once: true }); });
document.querySelectorAll('[data-slider]').forEach((slider) => {
  const track = slider.querySelector('.slider__track');
  const items = [...track.children];
  const controls = slider.querySelector('.slider__controls');
  const status = slider.querySelector('.slider__status');
  const word = status.textContent.split(' ')[0];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const current = () => { const x = track.scrollLeft; let best = 0; items.forEach((it, i) => { if (Math.abs(it.offsetLeft - track.offsetLeft - x) < Math.abs(items[best].offsetLeft - track.offsetLeft - x)) best = i; }); return best; };
  const update = () => { const i = current(); status.textContent = `${word} ${(document.body.dataset.of || '{i} von {n}').replace('{i}', i + 1).replace('{n}', items.length)}`; controls.querySelector('[data-dir="-1"]').disabled = track.scrollLeft < 4; controls.querySelector('[data-dir="1"]').disabled = track.scrollLeft + track.clientWidth > track.scrollWidth - 4; };
  controls.addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; const i = Math.min(Math.max(current() + Number(b.dataset.dir), 0), items.length - 1); track.scrollTo({ left: items[i].offsetLeft - track.offsetLeft, behavior: reduce.matches ? 'auto' : 'smooth' }); });
  track.addEventListener('scroll', () => requestAnimationFrame(update), { passive: true });
  controls.hidden = false; update();
});
const ride = document.querySelector('[data-ride]');
if (ride) {
  let pinned = '';
  const set = (r) => { ride.dataset.active = r; ride.querySelectorAll('[data-route]').forEach((el) => el.classList.toggle('is-active', el.dataset.route === r)); };
  ride.querySelectorAll('li[data-route], .route, .start').forEach((el) => {
    el.addEventListener('mouseenter', () => set(el.dataset.route));
    el.addEventListener('mouseleave', () => set(pinned));
  });
  // Aufgeklappte Route bleibt in der Karte hervorgehoben; immer nur eine ist offen
  const all = [...ride.querySelectorAll('li[data-route] details')];
  // Der aufgeklappte Eintrag rückt an den Anfang der Liste; die Seite stellt sich so ein, dass Karte und Eintrag gemeinsam im Bild sind
  const narrow = matchMedia('(max-width: 60rem)');
  const calm = matchMedia('(prefers-reduced-motion: reduce)');
  const frame = (li) => {
    const off = parseFloat(getComputedStyle(ride.querySelector('.map')).top) || 0;
    const b = li.getBoundingClientRect();
    if (!narrow.matches && b.top >= off && b.bottom <= innerHeight) return;
    scrollTo({ top: scrollY + ride.getBoundingClientRect().top - off, behavior: calm.matches ? 'auto' : 'smooth' });
  };
  all.forEach((d) => d.addEventListener('toggle', () => {
    const li = d.parentElement;
    const r = li.dataset.route;
    li.classList.toggle('is-open', d.open);
    if (d.open) { all.forEach((o) => { if (o !== d) o.open = false; }); pinned = r; requestAnimationFrame(() => frame(li)); }
    else if (pinned === r) pinned = '';
    set(pinned);
  }));
  // Klick auf eine Route in der Karte klappt ihren Eintrag auf
  ride.querySelectorAll('.route, .start').forEach((el) => el.addEventListener('click', () => {
    const d = ride.querySelector(`li[data-route="${el.dataset.route}"] details`);
    if (!d) return;
    if (d.open) frame(d.parentElement); else d.open = true;
  }));
}

document.querySelectorAll('[data-profile-figure]').forEach((fig) => {
  const svg = fig.querySelector('svg');
  const pts = JSON.parse(svg.dataset.profile);
  const x0 = +svg.dataset.x0, x1 = +svg.dataset.x1, e0 = +svg.dataset.y0, e1 = +svg.dataset.y1, top = +svg.dataset.top, bot = +svg.dataset.bottom;
  const total = pts[pts.length - 1][0];
  const cross = svg.querySelector('.prof-cross');
  const ns = 'http://www.w3.org/2000/svg';
  const dot = document.createElementNS(ns, 'circle'); dot.setAttribute('r', '6'); dot.setAttribute('class', 'prof-dot'); dot.setAttribute('visibility', 'hidden'); svg.appendChild(dot);
  const out = fig.querySelector('.profile__readout');
  const resting = out.textContent;
  const fmt = (v, d) => v.toFixed(d).replace('.', document.body.dataset.dec || ',');
  const show = (clientX) => {
    const r = svg.getBoundingClientRect();
    const vx = (clientX - r.left) / r.width * svg.viewBox.baseVal.width;
    const d = Math.min(Math.max((vx - x0) / (x1 - x0), 0), 1) * total;
    let best = pts[0];
    for (const p of pts) if (Math.abs(p[0] - d) < Math.abs(best[0] - d)) best = p;
    const x = x0 + (x1 - x0) * best[0] / total, y = top + (bot - top) * (1 - (best[1] - e0) / (e1 - e0));
    cross.setAttribute('x1', x); cross.setAttribute('x2', x); cross.setAttribute('visibility', 'visible');
    dot.setAttribute('cx', x); dot.setAttribute('cy', y); dot.setAttribute('visibility', 'visible');
    out.textContent = (document.body.dataset.elev || '{m} m über dem Meer bei Kilometer {km}').replace('{m}', best[1]).replace('{km}', fmt(best[0], 1));
  };
  const hide = () => { cross.setAttribute('visibility', 'hidden'); dot.setAttribute('visibility', 'hidden'); out.textContent = resting; };
  svg.addEventListener('pointermove', (e) => show(e.clientX));
  svg.addEventListener('pointerdown', (e) => show(e.clientX));
  svg.addEventListener('pointerleave', hide);
});

// Menü am Handy: nach dem Antippen eines Links, außerhalb oder mit Escape schließen
const menu = document.querySelector('details.menu');
if (menu) {
  menu.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => menu.removeAttribute('open')));
  document.addEventListener('click', (e) => { if (menu.open && !menu.contains(e.target)) menu.removeAttribute('open'); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && menu.open) { menu.removeAttribute('open'); menu.querySelector('summary').focus(); } });
}

// Sprachhinweis: richtet sich nach der zuletzt gewählten Sprache, sonst nach der Browser-Sprache. Leitet nie von selbst um.
(() => {
  const T = {
    de: ['Sprache', 'Diese Seite gibt es auch auf Deutsch.', 'Auf Deutsch lesen', 'Hinweis schließen'],
    sl: ['Jezik', 'Ta stran je na voljo tudi v slovenščini.', 'Preberite v slovenščini', 'Zapri obvestilo'],
    en: ['Language', 'This page is also available in English.', 'Read in English', 'Close notice'],
    hu: ['Nyelv', 'Ez az oldal magyarul is elérhető.', 'Olvasás magyarul', 'Értesítés bezárása'],
  };
  const KEY = 'gp-lang';
  const here = document.documentElement.lang;
  const keep = (l) => { try { localStorage.setItem(KEY, l); } catch (e) { /* privater Modus: dann eben ohne Merken */ } };
  let saved = '';
  try { saved = localStorage.getItem(KEY) || ''; } catch (e) { /* ohne Speicher weiter */ }
  // Wer selbst eine Sprache anklickt, hat gewählt
  document.querySelectorAll('a[hreflang]').forEach((a) => a.addEventListener('click', () => keep(a.hreflang)));
  if (/bot|crawl|spider|lighthouse|headless/i.test(navigator.userAgent)) return;
  const list = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ''];
  const browser = list.map((l) => l.slice(0, 2).toLowerCase()).find((l) => T[l]);
  const want = T[saved] ? saved : browser || 'en';
  const target = want !== here && document.querySelector(`.lang-switch a[hreflang="${want}"]`);
  if (!target) return;
  const [label, text, go, close] = T[want];
  const bar = document.createElement('div');
  bar.className = 'lang-hint'; bar.lang = want; bar.setAttribute('role', 'region'); bar.setAttribute('aria-label', label);
  const box = document.createElement('div'); box.className = 'container';
  const p = document.createElement('p'); p.textContent = text;
  const a = document.createElement('a'); a.className = 'btn btn--primary btn--small'; a.href = target.href; a.hreflang = want; a.textContent = go;
  a.addEventListener('click', () => keep(want));
  const x = document.createElement('button'); x.type = 'button'; x.className = 'lang-hint__close'; x.setAttribute('aria-label', close);
  x.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  box.append(p, a, x); bar.append(box); document.body.prepend(bar);
  // Die Kopfzeile liegt über dem Titelbild; sie rückt um die Höhe des Hinweises nach unten
  const root = document.documentElement;
  const fit = () => root.style.setProperty('--hint-h', `${bar.offsetHeight}px`);
  const watch = new ResizeObserver(fit); watch.observe(bar); fit();
  x.addEventListener('click', () => { watch.disconnect(); bar.remove(); root.style.removeProperty('--hint-h'); keep(here); });
})();
