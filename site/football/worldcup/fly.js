// Shared item-level fly primitive — see requirements/public.md -> Navigation
// -> Transitions -> "The invisible hands" and brand-guidelines.md -> Motion.
// Loaded on every page (year pages, history.html, index.html) before any
// page-specific script that flies individual chips/rows/cards/cells in or
// out with a small random stagger, never a whole board's worth at once.
//
// This file holds only the item-level primitive, not the board-level one
// (see ../nav.css's .fly-panel, orchestrated per-page by shared.js's own
// flyOut()/flyIn(), or build_home.py's .home-group system) — those two
// mechanisms are deliberately different (sequential single-panel swap vs.
// permanently-coexisting parallel swap) and stay where they are.

// NAV_FLY_KEY is the sessionStorage protocol cross-page navigation (Home <->
// History) uses to signal "this page was reached by an internal click, play
// the arrival flurry" across the navigation boundary — see
// requirements/public.md -> Navigation -> Cross-page navigation. Defining it
// once here, rather than duplicating the string independently in build.py
// and build_home.py, makes the two sides structurally guaranteed to agree
// instead of merely documented to.
const NAV_FLY_KEY = 'sotibd-nav-fly';

// Read from ../nav.css's --fly-item-ms (the single source of truth) rather
// than a second hardcoded number that could drift out of sync with it.
const FLY_ITEM_MS = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--fly-item-ms'));
// The random-jitter window each item's move is offset within — see
// requirements/public.md -> Navigation -> Transitions -> "Stagger". Not a
// CSS custom property like --fly-item-ms, since it's consumed here as a JS
// number (Math.random() * this), not applied directly as a style value.
const FLY_ITEM_JITTER_MS = 250;

// True if `el` is at least partially within the vertical viewport — used to
// scope flying to what's actually in frame (see requirements/public.md ->
// Navigation -> Cross-page navigation -> "Scoped to what's actually in
// frame").
function inFrame(el) {
  const r = el.getBoundingClientRect();
  return r.bottom > 0 && r.top < (window.innerHeight || document.documentElement.clientHeight);
}

// Flies each of `items` out to the right individually — a small random
// delay per item (see FLY_ITEM_JITTER_MS above) rather than one synchronized
// move — and resolves once the slowest one has finished. See
// brand-guidelines.md -> Motion -> The invisible hands: a hundred items get
// a hundred small staggered movements, never one big one. Same distance/
// direction as the sitewide .fly-panel (out right, in left — see
// requirements/public.md -> Navigation -> Transitions), just per item.
function flyOutItems(items) {
  return new Promise(function(resolve) {
    if (!items.length) { resolve(); return; }
    let maxDelay = 0;
    items.forEach(function(item) {
      const delay = Math.random() * FLY_ITEM_JITTER_MS;
      if (delay > maxDelay) maxDelay = delay;
      item.style.transitionDelay = delay + 'ms';
      item.classList.add('fly-item', 'fly-item-out');
    });
    window.setTimeout(resolve, FLY_ITEM_MS + maxDelay);
  });
}

// Flies each of `items` in from the left individually, same jitter idea as
// flyOutItems above — see requirements/public.md -> Navigation ->
// Transitions -> "Stagger". Resolves once the slowest one has settled, so
// the caller can release any scroll lock it applied.
function flyInItems(items) {
  return new Promise(function(resolve) {
    if (!items.length) { resolve(); return; }
    items.forEach(function(item) { item.classList.add('fly-item', 'fly-item-in-start'); });
    void (items[0] && items[0].offsetWidth);
    requestAnimationFrame(function() {
      let maxDelay = 0;
      items.forEach(function(item) {
        const delay = Math.random() * FLY_ITEM_JITTER_MS;
        if (delay > maxDelay) maxDelay = delay;
        item.style.transitionDelay = delay + 'ms';
        item.classList.remove('fly-item-in-start');
        item.classList.add('fly-item-in-active');
      });
      window.setTimeout(function() {
        items.forEach(function(item) {
          item.classList.remove('fly-item', 'fly-item-in-active');
          item.style.transitionDelay = '';
        });
        resolve();
      }, FLY_ITEM_MS + maxDelay);
    });
  });
}

// Sticky-note name label on flag hover — see requirements/public.md ->
// World Cup pages -> Flags -> "Name on hover". Every flag on the site
// (Match List, Knockout, History) marks itself with data-team="<name>"
// instead of a native `title` attribute — a browser tooltip is unstyled
// system chrome with no brand material, and it contradicts
// brand-guidelines.md -> Flags, Not Names's own framing of the hover-name
// as "a label under a fingertip" (something designed, not raw OS UI).
// Delegated on document rather than per-flag listeners, so it works
// across every page/re-render without each view having to wire it up.
(function() {
  let noteEl = null;

  function hideNote() {
    if (noteEl) { noteEl.remove(); noteEl = null; }
  }

  function showNote(el) {
    hideNote();
    const name = el.getAttribute('data-team');
    if (!name) return;
    const rect = el.getBoundingClientRect();
    noteEl = document.createElement('div');
    noteEl.className = 'flag-name-note';
    noteEl.textContent = name;
    // Same #FAD7A0 sticky material and random tilt as the W/D/L diff
    // highlight (see shared.js's renderWld) — one sticky-note look reused,
    // not a second one invented for this.
    noteEl.style.transform = `rotate(${(Math.random() * 10 - 5).toFixed(1)}deg)`;
    document.body.appendChild(noteEl);
    const noteRect = noteEl.getBoundingClientRect();
    noteEl.style.left = (rect.left + rect.width / 2 - noteRect.width / 2) + 'px';
    noteEl.style.top = (rect.top - noteRect.height - 4) + 'px';
  }

  document.addEventListener('mouseover', function(e) {
    const el = e.target.closest('[data-team]');
    if (el) showNote(el);
  });
  document.addEventListener('mouseout', function(e) {
    const el = e.target.closest('[data-team]');
    if (el && !el.contains(e.relatedTarget)) hideNote();
  });
  // A wheel/trackpad scroll moves content under a stationary cursor without
  // firing mouseout — hide on any scroll (capture phase, so this also
  // catches .table-wrap's own nested scroll) rather than leaving a
  // position:fixed note stranded over unrelated content.
  window.addEventListener('scroll', hideNote, true);
})();
