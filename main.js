// Mobiles Menü und aktuelles Jahr im Footer
(function () {
  const header = document.querySelector('.header');
  const toggle = document.querySelector('.nav-toggle');

  if (header && toggle) {
    toggle.addEventListener('click', () => {
      const open = header.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
    });
    document.querySelectorAll('.nav a').forEach((a) => a.addEventListener('click', () => {
      header.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
    }));
  }

  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
