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

// Cross-page navigation (Home <-> WC YY <-> Tournaments <-> History) — see
// requirements/public.md -> Navigation -> Cross-page navigation and
// brand-guidelines.md -> Motion -> "Walking to a different poster". No
// native View Transition (its only primitive is one whole-page snapshot,
// which arrives pre-assembled as one image — exactly the "component
// dropped in" effect that section rules out); instead every in-frame nav
// chip flies out individually before leaving, and every in-frame one on
// the arriving page flies in the same way, via a hand-rolled click-
// intercept + sessionStorage protocol.
//
// One shared implementation, not one hand-copied into every page's own
// script — click-intercept, sessionStorage handoff, scroll-locking, and the
// fonts.ready race-avoidance are identical everywhere and were exactly the
// part that went wrong from being duplicated instead of shared: this used
// to be hand-copied per page (build_home.py's homeDepartureItems() +
// its own click/arrival code, build.py's historyFlyItems() + its own
// click/arrival code) and, tellingly, only ever got built for the Home <->
// History pair — every other cross-page link (Home <-> WC YY, Home <->
// Tournaments) was simply never wired up, so those navigations silently
// fell back to a plain, un-animated browser navigation.
//
// What *does* still vary by page is which elements actually fly, so
// `setupCrossPageNav` takes a function for that: pageNavFlyItems() below is
// the right default for a page whose nav chips are the whole story (every
// page's nav lives in the same `.page-nav` wrapper — see nav.py's
// render_page_nav — so "every nav chip at every level" is gathered the same
// way regardless of which page it is), but a page can pass its own function
// instead, either to add further in-frame content (History's table cells,
// alongside its own nav chips) or to override nav-chip gathering entirely
// (the homepage's Sports!-signature exemption: see brand-guidelines.md ->
// "The homepage signature is exempt" — it must fly as the single
// `#sports-group` piece, not as the separate chips a plain `.view-toggle >
// *` scan would otherwise see it as, since it happens to share that class
// for layout reasons alone).
function pageNavFlyItems() {
  return Array.from(document.querySelectorAll('.page-nav .view-toggle > *'));
}

function setupCrossPageNav(getFlyItems) {
  function allFlyItems() {
    const items = (typeof getFlyItems === 'function') ? getFlyItems() : pageNavFlyItems();
    return items.filter(Boolean).filter(inFrame);
  }

  // Any scrollable ancestor a flying item might live inside (a table's own
  // `.table-wrap`, a bracket's `.bracket`) plus `body` itself — an
  // off-screen translate briefly inflates whichever ancestor's scrollable
  // width otherwise, the same reason .fly-panel always needed this (see
  // ../nav.css). Queried fresh each time rather than cached, since which of
  // these exist differs by page and (for the bracket) can change between
  // renders.
  function scrollLockEls() {
    return Array.from(document.querySelectorAll('.table-wrap, .bracket')).concat([document.body]);
  }

  // Departure — intercept a click on any link that actually leaves this
  // document (not a same-page `#hash`, not an external/new-tab link — this
  // mechanism only ever has something to say about navigating to another
  // page *of this site*). A chip that isn't currently a real destination
  // (the active selection, a disabled item) renders as `<strong>`/`<span>`
  // instead of `<a>` (see nav.py), so a plain `a[href]` selector already
  // only ever matches a genuine clickable cross-page link — nothing to
  // exclude by hand, and nothing to keep in sync with as pages change.
  document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href]');
    if (!link || link.target === '_blank') return;
    const href = link.getAttribute('href');
    if (!href || href.charAt(0) === '#' || /^[a-z][a-z0-9+.-]*:/i.test(href)) return;
    e.preventDefault();
    const locked = scrollLockEls();
    locked.forEach(function(el) { el.classList.add('fly-scroll-lock'); });
    flyOutItems(allFlyItems()).then(function() {
      sessionStorage.setItem(NAV_FLY_KEY, '1');
      window.location.href = href;
    });
  });

  // Arrival — only a same-site click sets NAV_FLY_KEY, so this never fires
  // on a direct load/refresh, matching the sitewide "nothing flies on
  // load" default (see requirements/public.md -> Navigation -> Initial
  // display) with its one sanctioned exception.
  if (sessionStorage.getItem(NAV_FLY_KEY) === '1') {
    sessionStorage.removeItem(NAV_FLY_KEY);
    const arrivalItems = allFlyItems();
    // Pinned off-screen the instant they exist — before any paint — but the
    // actual flight waits on document.fonts.ready: a render-blocking font
    // fetch racing against this script's synchronous class mutations could
    // otherwise let the whole staggered arrival execute before the browser
    // ever shows a frame of it, which reads as one clump landing instantly
    // rather than individually staggered pieces. See requirements/public.md
    // -> Cross-page navigation -> "The board must already be standing
    // before the first item moves — never a race."
    arrivalItems.forEach(function(item) { item.classList.add('fly-item', 'fly-item-in-start'); });
    document.fonts.ready.then(function() {
      const locked = scrollLockEls();
      locked.forEach(function(el) { el.classList.add('fly-scroll-lock'); });
      flyInItems(arrivalItems).then(function() {
        locked.forEach(function(el) { el.classList.remove('fly-scroll-lock'); });
      });
    });
  }
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
