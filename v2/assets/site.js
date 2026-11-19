// NCN v2 – Navigation, Seekarte, Gastgeber-Rad
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Kopfleiste: über dem Hero transparent, danach fest
  const bar = document.getElementById('top-bar');
  const hero = document.getElementById('start');
  if (bar) {
    const solid = () => bar.classList.toggle('is-solid', !hero || window.scrollY > hero.offsetHeight - 90);
    solid(); window.addEventListener('scroll', solid, { passive: true });
    if (!hero) bar.classList.add('is-solid');
  }

  // Menü auf kleinen Bildschirmen
  const burger = document.querySelector('.burger');
  if (bar && burger) {
    const set = (open) => { bar.classList.toggle('is-open', open); burger.setAttribute('aria-expanded', String(open)); burger.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen'); };
    burger.addEventListener('click', () => set(!bar.classList.contains('is-open')));
    document.querySelectorAll('#menu a').forEach((a) => a.addEventListener('click', () => set(false)));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
  }

  // Seekarte und Register: eine Stadt hervorheben, ihre Verbindungen leuchten
  const chart = document.querySelector('.chart svg');
  if (chart) {
    const cities = chart.querySelectorAll('.city');
    const links = chart.querySelectorAll('.link');
    const rows = document.querySelectorAll('.register a[data-city]');
    const on = (id) => {
      cities.forEach((c) => c.classList.toggle('is-on', c.dataset.city === id));
      links.forEach((l) => l.classList.toggle('is-on', !!id && (l.dataset.a === id || l.dataset.b === id)));
      rows.forEach((r) => r.classList.toggle('is-on', r.dataset.city === id));
    };
    const bind = (el) => {
      el.addEventListener('mouseenter', () => on(el.dataset.city));
      el.addEventListener('mouseleave', () => on(null));
      el.addEventListener('focus', () => on(el.dataset.city));
      el.addEventListener('blur', () => on(null));
    };
    cities.forEach(bind); rows.forEach(bind);
  }

  // Gastgeber-Rad: die Rolle wandert von Stadt zu Stadt
  const wheel = document.getElementById('wheel');
  if (wheel) {
    const nodes = [...wheel.querySelectorAll('.node')];
    const label = document.getElementById('wheel-host');
    let i = Math.max(0, nodes.findIndex((n) => n.dataset.host === 'Greifswald'));
    const show = () => { nodes.forEach((n, j) => n.classList.toggle('is-host', j === i)); label.textContent = nodes[i].dataset.host; };
    show();
    if (!reduce) {
      // läuft nur, solange das Rad sichtbar ist
      setInterval(() => {
        const r = wheel.getBoundingClientRect();
        if (document.hidden || r.bottom < 0 || r.top > innerHeight) return;
        i = (i + 1) % nodes.length; show();
      }, 2200);
    }
  }

  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
