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
  all.forEach((d) => d.addEventListener('toggle', () => {
    const r = d.parentElement.dataset.route;
    if (d.open) { all.forEach((o) => { if (o !== d) o.open = false; }); pinned = r; }
    else if (pinned === r) pinned = '';
    set(pinned);
  }));
  // Klick auf eine Route in der Karte klappt ihren Eintrag auf
  ride.querySelectorAll('.route, .start').forEach((el) => el.addEventListener('click', () => {
    const d = ride.querySelector(`li[data-route="${el.dataset.route}"] details`);
    if (!d) return;
    d.open = true;
    d.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
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
