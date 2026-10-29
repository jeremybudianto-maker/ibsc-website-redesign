/* All published course entries remain readable without this enhancement. */
(() => {
  'use strict';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const animations = new Set();
  function setup(browser) {
    if (browser.dataset.courseReady) return;
    const controls = browser.querySelector('.academic-filters');
    const buttons = [...browser.querySelectorAll('[data-course-filter]')];
    const courses = [...browser.querySelectorAll('[data-course-group]')];
    const collection = browser.querySelector('#course-collection');
    const count = browser.querySelector('[data-course-count]');
    if (!controls || !collection || !count || !courses.length || !buttons.length) return;
    function select(group) {
      if (!buttons.some(button => button.dataset.courseFilter === group)) return;
      let shown = 0;
      courses.forEach(course => {
        course.hidden = group !== 'all' && course.dataset.courseGroup !== group;
        if (!course.hidden) shown++;
      });
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.courseFilter === group)));
      count.textContent = `${shown} published course ${shown === 1 ? 'entry' : 'entries'}`;
      animations.forEach(animation => animation.cancel());
      animations.clear();
      if (!reduced.matches && collection.animate) {
        const animation = collection.animate([{ opacity: .8, transform: 'translateY(4px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 180, easing: 'ease-out' });
        animations.add(animation);
        animation.finished.catch(() => {}).finally(() => animations.delete(animation));
      }
    }
    buttons.forEach(button => button.addEventListener('click', () => select(button.dataset.courseFilter)));
    document.querySelectorAll('[data-course-jump]').forEach(anchor => anchor.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      select(anchor.dataset.courseJump);
    }));
    controls.hidden = false;
    browser.dataset.courseReady = 'true';
  }
  function init() { document.querySelectorAll('[data-course-browser]').forEach(setup); }
  const cancelMotion = () => { if (reduced.matches) { animations.forEach(animation => animation.cancel()); animations.clear(); } };
  if (reduced.addEventListener) reduced.addEventListener('change', cancelMotion);
  else reduced.addListener(cancelMotion);
  window.IBSCAcademics = { init };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
