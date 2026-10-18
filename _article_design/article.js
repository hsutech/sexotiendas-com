/* Navigation and reading aids: progressive enhancement, no tracking. */
(() => {
  const page = document.body;
  page.classList.add('j-enhanced');
  const toggle = document.querySelector('.j-toggle');
  const menu = document.querySelector('.j-menu');
  function closeMenu(returnFocus = false) {
    toggle.setAttribute('aria-expanded', 'false');
    menu.classList.remove('j-menu-open');
    if (returnFocus) toggle.focus();
  }
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('j-menu-open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') closeMenu(true);
  });
  menu.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  const narrow = matchMedia('(max-width: 800px)');
  const toc = document.querySelector('.j-toc');
  const adapt = () => { toc.open = !narrow.matches; closeMenu(); };
  adapt();
  narrow.addEventListener('change', adapt);
  toc.addEventListener('click', event => { if (narrow.matches && event.target.closest('a')) toc.open = false; });
  const links = [...toc.querySelectorAll('a')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        for (const a of links) {
          if (a.hash === '#' + entry.target.id) a.setAttribute('aria-current', 'location');
          else a.removeAttribute('aria-current');
        }
      }
    }, { rootMargin: '-8% 0px -65% 0px' });
    document.querySelectorAll('.j-copy h2[id]').forEach(h => observer.observe(h));
  }
})();
