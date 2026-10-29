(() => {
  'use strict';

  // Calling init again is safe after a CMS inserts more content.
  if (window.IBSCInteractions) {
    window.IBSCInteractions.init();
    return;
  }

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const animations = new Map();
  const journeys = new Map();
  const routeNames = {
    international: 'International applicants',
    domestic: 'Domestic applicants',
    overseas: 'Overseas compatriot, Hong Kong and Macau applicants'
  };

  function cancelAnimation(element) {
    animations.get(element)?.cancel();
    animations.delete(element);
  }

  function animateContent(element, distance = 6, duration = 220, opacity = 0.94) {
    if (!element || reducedMotion.matches || typeof element.animate !== 'function') return;
    cancelAnimation(element);
    const animation = element.animate([
      { opacity, transform: `translateY(${distance}px)` },
      { opacity: 1, transform: 'translateY(0)' }
    ], { duration, easing: 'cubic-bezier(.2,.8,.2,1)' });
    animations.set(element, animation);
    const cleanup = () => {
      if (animations.get(element) === animation) animations.delete(element);
    };
    animation.addEventListener('finish', cleanup, { once: true });
    animation.addEventListener('cancel', cleanup, { once: true });
  }

  function setVisible(element, visible) {
    if (!visible) cancelAnimation(element);
    element.hidden = !visible;
    element.inert = !visible;
    element.toggleAttribute('inert', !visible);
  }

  function plainClick(event) {
    return event.button === 0 && !event.metaKey && !event.ctrlKey &&
      !event.shiftKey && !event.altKey;
  }

  function setupStoryBrowser(browser) {
    if (browser.dataset.ibscStoryReady) return;
    const panels = [...browser.querySelectorAll('.story-panel[data-story-panel]')];
    const selectors = [...browser.querySelectorAll('[data-story-select]')];
    const count = browser.querySelector('[data-story-count]');
    const previous = browser.querySelector('[data-story-prev]');
    const next = browser.querySelector('[data-story-next]');
    const buttons = new Map();
    selectors.forEach(button => {
      const index = Number(button.dataset.storySelect);
      if (Number.isInteger(index) && index >= 0 && index < panels.length) {
        buttons.set(index, button);
      }
    });
    // Incomplete components keep their readable, static presentation.
    if (!panels.length || buttons.size !== panels.length || !count || !previous || !next) return;
    if (panels.some((panel, index) =>
      !panel.id || buttons.get(index).getAttribute('aria-controls') !== panel.id)) return;

    let activeIndex = -1;
    function select(index, { announce = false, focus = false, animate = false } = {}) {
      index = ((index % panels.length) + panels.length) % panels.length;
      const changed = index !== activeIndex;
      panels.forEach((panel, panelIndex) => setVisible(panel, panelIndex === index));
      buttons.forEach((button, buttonIndex) => {
        const current = buttonIndex === index;
        button.setAttribute('aria-pressed', String(current));
        button.classList.toggle('is-current', current);
      });
      activeIndex = index;
      browser.dataset.activeIndex = String(index);
      if (changed) {
        count.setAttribute('aria-live', announce ? 'polite' : 'off');
        count.setAttribute('aria-atomic', 'true');
        count.textContent = `Story ${index + 1} of ${panels.length}`;
        if (animate) animateContent(panels[index]);
      }
      if (focus) buttons.get(index).focus();
    }

    buttons.forEach((button, index) => {
      button.type = 'button';
      button.addEventListener('click', () => select(index, { announce: true, animate: true }));
      button.addEventListener('keydown', event => {
        if (event.altKey || event.ctrlKey || event.metaKey) return;
        const destinations = {
          ArrowLeft: index - 1,
          ArrowRight: index + 1,
          Home: 0,
          End: panels.length - 1
        };
        if (!(event.key in destinations)) return;
        event.preventDefault();
        select(destinations[event.key], { announce: true, focus: true, animate: true });
      });
    });
    previous.type = next.type = 'button';
    previous.addEventListener('click', () =>
      select(activeIndex - 1, { announce: true, animate: true }));
    next.addEventListener('click', () =>
      select(activeIndex + 1, { announce: true, animate: true }));

    select(0);
    browser.querySelectorAll('[data-story-controls], .story-toolbar, .story-selector-list')
      .forEach(control => { control.hidden = false; });
    browser.classList.add('is-enhanced');
    browser.dataset.ibscStoryReady = 'true';
  }

  function routeFromHash(hash) {
    let id;
    try { id = decodeURIComponent(hash.replace(/^#/, '')); } catch { return null; }
    const route = id.startsWith('journey-') ? id.slice(8) : id.replace(/-guide$/, '');
    if (Object.hasOwn(routeNames, route) &&
        (id === `journey-${route}` || id === `${route}-guide`)) return route;
    return id === 'individual-guide' ? 'domestic' : null;
  }

  function setupJourney(journey) {
    if (journey.dataset.ibscJourneyReady) return;
    const choices = [...journey.querySelectorAll('.journey-choices [data-journey-route]')];
    const panels = new Map([...journey.querySelectorAll('.journey-route[data-journey-panel]')]
      .map(panel => [panel.dataset.journeyPanel, panel]));
    const status = journey.querySelector('[data-journey-status]');
    const prompt = journey.querySelector('.journey-prompt');
    if (!status || !Object.keys(routeNames).every(route =>
      panels.has(route) && choices.some(choice => choice.dataset.journeyRoute === route))) return;

    let activeRoute = null;
    function select(route, { announce = false, animate = false } = {}) {
      if (route !== null && !panels.has(route)) return;
      const changed = route !== activeRoute;
      panels.forEach((panel, key) => setVisible(panel, key === route));
      choices.forEach(choice => {
        const current = choice.dataset.journeyRoute === route;
        if (current) choice.setAttribute('aria-current', 'true');
        else choice.removeAttribute('aria-current');
        choice.classList.toggle('is-current', current);
      });
      if (prompt) prompt.hidden = Boolean(route);
      activeRoute = route;
      journey.dataset.activeRoute = route || '';
      if (changed || !route) {
        status.setAttribute('aria-live', announce ? 'polite' : 'off');
        status.setAttribute('aria-atomic', 'true');
        status.textContent = route ? `${routeNames[route]} guidance is shown below.` : '';
        if (route && animate) animateContent(panels.get(route));
      }
    }

    choices.forEach(choice => {
      choice.addEventListener('click', event => {
        if (!plainClick(event) || event.defaultPrevented) return;
        const route = choice.dataset.journeyRoute;
        if (!Object.hasOwn(routeNames, route) || !panels.has(route)) return;
        // Handle these choices before app.js's document-level guide navigation.
        event.preventDefault();
        select(route, { announce: true, animate: true });
        const hash = `#journey-${route}`;
        if (location.hash !== hash) {
          try { history.replaceState(history.state, '', hash); }
          catch { /* The guidance still works in contexts that restrict history. */ }
        }
      });
    });

    select(routeFromHash(location.hash));
    journey.classList.add('is-enhanced');
    journey.dataset.ibscJourneyReady = 'true';
    journeys.set(journey, select);
  }

  function syncJourneys(hash, announce = false) {
    const route = routeFromHash(hash);
    if (route || !hash) journeys.forEach(select => select(route, { announce }));
  }

  function setupDisclosure(details) {
    if (details.dataset.ibscMotionReady) return;
    const content = [...details.children].find(child =>
      child.tagName !== 'SUMMARY' && child.tagName === 'DIV');
    let wasOpen = details.open;
    details.addEventListener('toggle', event => {
      if (event.target !== details) return;
      if (details.open && !wasOpen) animateContent(content, 6, 180);
      if (!details.open && content) cancelAnimation(content);
      wasOpen = details.open;
    });
    details.dataset.ibscMotionReady = 'true';
  }

  let revealObserver;
  const pendingReveals = new Set();
  function setupReveals() {
    if (reducedMotion.matches || !('IntersectionObserver' in window)) return;
    if (!revealObserver) {
      revealObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          revealObserver.unobserve(entry.target);
          pendingReveals.delete(entry.target);
          animateContent(entry.target, 8, 340, 0.92);
        });
      }, { threshold: 0.08 });
    }
    document.querySelectorAll('[data-reveal]').forEach(element => {
      if (element.dataset.ibscRevealReady) return;
      element.dataset.ibscRevealReady = 'true';
      const rect = element.getBoundingClientRect();
      const alreadyVisible = rect.width > 0 && rect.height > 0 &&
        rect.bottom > 0 && rect.top < window.innerHeight;
      if (!alreadyVisible) pendingReveals.add(element);
    });
    // Resume pending elements when the live motion preference returns to normal.
    pendingReveals.forEach(element => revealObserver.observe(element));
  }

  function init() {
    document.querySelectorAll('[data-story-browser]').forEach(setupStoryBrowser);
    document.querySelectorAll('[data-admission-journey]').forEach(setupJourney);
    document.querySelectorAll('.info-disclosure, .experience-disclosure, .journey-readiness, .academic-theme, .academic-field')
      .forEach(setupDisclosure);
    setupReveals();
  }

  // Normal guide links retain app.js's native disclosure opening, focus and scroll.
  // Its pushState call has no hashchange event, so mirror only the route selection.
  document.addEventListener('click', event => {
    if (!plainClick(event)) return;
    const anchor = event.target.closest?.('a[href]');
    if (!anchor || anchor.matches('[data-journey-route]')) return;
    const destination = new URL(anchor.href, location.href);
    const pagePath = path => path.replace(/\/+$/, '').replace(/\.html$/, '') || '/';
    if (destination.origin === location.origin &&
        pagePath(destination.pathname) === pagePath(location.pathname)) {
      syncJourneys(destination.hash, true);
    }
  });
  window.addEventListener('hashchange', () => syncJourneys(location.hash, true));
  window.addEventListener('popstate', () => syncJourneys(location.hash, true));

  const motionChanged = () => {
    if (reducedMotion.matches) {
      animations.forEach(animation => animation.cancel());
      animations.clear();
      revealObserver?.disconnect();
    } else setupReveals();
  };
  if (reducedMotion.addEventListener) reducedMotion.addEventListener('change', motionChanged);
  else reducedMotion.addListener(motionChanged);

  window.IBSCInteractions = { init };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
