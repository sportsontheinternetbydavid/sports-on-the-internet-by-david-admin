// Shared item-level and board-level fly primitives — see
// requirements/public.md -> Navigation -> Transitions -> "The invisible
// hands" and brand-guidelines.md -> Motion. Loaded on every page (year
// pages, history.html, index.html) before any page-specific script that
// flies individual chips/rows/cards/cells in or out with a small random
// stagger, or a whole board in or out as one piece.
//
// The board-level primitive (flyOut()/flyIn() below) lives here rather than
// only in shared.js because cross-page navigation's own board phase (see
// requirements/transitions.md -> Cross-page navigation) needs it on pages
// that don't load shared.js at all — the homepage, History. shared.js's
// setPageView/setMatchView/toggleBracketRound use this same pair for their
// own within-page board swaps rather than keeping a second copy. The
// homepage's `.home-group` system is still a third, deliberately different
// mechanism (permanently-coexisting parallel swap, not a sequential single-
// panel one), used only for the homepage's own internal Sports!/Football
// toggle — not to be confused with this file's board-level fly, which
// setupCrossPageNav below uses for cross-page navigation's board phase on
// every page that has a board of its own (the homepage simply has none, so
// it never supplies one).

// NAV_FLY_KEY is the sessionStorage protocol cross-page navigation (Home <->
// History) uses to signal "this page was reached by an internal click, play
// the arrival flurry" across the navigation boundary — see
// requirements/public.md -> Navigation -> Cross-page navigation. Defining it
// once here, rather than duplicating the string independently in build.py
// and build_home.py, makes the two sides structurally guaranteed to agree
// instead of merely documented to.
const NAV_FLY_KEY = 'sotibd-nav-fly';

// Set alongside NAV_FLY_KEY only when this specific departure found a Home
// chip that persists onto the destination page unmoved — see
// requirements/transitions.md -> "The general rule" and -> Cross-page
// navigation ("A nav chip that's identical on both ends of a specific link
// never flies"). The arrival side reads it to know whether to leave its own
// Home chip alone too, rather than re-deriving "did the departure page have
// an identical one" after the fact, which the arriving document has no way
// to check on its own.
const NAV_PERSIST_HOME_KEY = 'sotibd-nav-persist-home';

// Read from ../nav.css's --fly-item-ms (the single source of truth) rather
// than a second hardcoded number that could drift out of sync with it.
const FLY_ITEM_MS = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--fly-item-ms'));
// The random-jitter window each item's move is offset within — see
// requirements/public.md -> Navigation -> Transitions -> "Stagger". Not a
// CSS custom property like --fly-item-ms, since it's consumed here as a JS
// number (Math.random() * this), not applied directly as a style value.
const FLY_ITEM_JITTER_MS = 250;

// Read from ../nav.css's --fly-ms (the single source of truth) rather than a
// second hardcoded number that could drift out of sync with it — see
// requirements/transitions.md -> Transitions -> "Chrome pace".
const FLY_MS = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--fly-ms'));

// Flies `els` off-screen (see ../nav.css's .fly-panel) and resolves once the
// transition finishes. Leaves them in the flown-out state — hiding/removing
// them from the DOM afterward is the caller's job.
function flyOut(els) {
  return new Promise(function(resolve) {
    els.forEach(function(el) { el.classList.remove('fly-in-active'); el.classList.add('fly-panel', 'fly-out'); });
    window.setTimeout(resolve, FLY_MS);
  });
}

// Flies `els` in from off-screen, with an optional per-element stagger (ms)
// for a rapid-fire reveal of several at once (see Knockout's round toggle).
// Once settled, clears the fly classes back to no-transform rather than
// leaving `transform: translateX(0)` in place — see ../nav.css's .fly-panel
// comment for why a lingering identity transform is its own latent bug
// (breaks any position:fixed descendant, e.g. Rankings' #rank-info).
function flyIn(els, options) {
  const stagger = (options && options.stagger) || 0;
  const onSettled = options && options.onSettled;
  return new Promise(function(resolve) {
    if (!els.length) { if (onSettled) onSettled(); resolve(); return; }
    els.forEach(function(el, i) {
      el.classList.add('fly-panel', 'fly-in-start');
      if (stagger) el.style.transitionDelay = (i * stagger) + 'ms';
    });
    void els[0].offsetWidth;
    requestAnimationFrame(function() {
      els.forEach(function(el) { el.classList.remove('fly-in-start'); el.classList.add('fly-in-active'); });
      window.setTimeout(function() {
        els.forEach(function(el) {
          el.classList.remove('fly-panel', 'fly-in-active');
          if (stagger) el.style.transitionDelay = '';
        });
        if (onSettled) onSettled();
        resolve();
      }, FLY_MS);
    });
  });
}

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
// What *does* still vary by page is which elements actually fly, and nav,
// board, and content fly as three separate, ordered phases now — see
// requirements/transitions.md -> Transitions -> "Layering": content clears,
// then the board (if any), then nav, on the way out; nav settles, then the
// board (if any), then content, on the way in — never simultaneously.
// `setupCrossPageNav` takes one function per layer: pageNavFlyItems() below
// is the right default for `getNavFlyItems` on a page whose nav chips are
// the whole story (every page's nav lives in the same `.page-nav` wrapper —
// see nav.py's render_page_nav — so "every nav chip at every level" is
// gathered the same way regardless of which page it is); `getContentFlyItems`
// and `getBoardEl` have no sitewide default (a page with nothing beyond its
// nav, like the homepage, simply omits both). A page overrides
// `getNavFlyItems` only to change nav-chip gathering itself — the
// homepage's Sports!-signature exemption is the one case (see
// brand-guidelines.md -> "The homepage signature is exempt" — it must fly
// as the single `#sports-group` piece, not as the separate chips a plain
// `.view-toggle > *` scan would otherwise see it as, since it happens to
// share that class for layout reasons alone) — and overrides
// `getContentFlyItems`/`getBoardEl` to supply whatever a page's own
// view/table/bracket contributes beyond its nav: `getContentFlyItems` for
// its own finest-grain items (History's table cells, a World Cup page's
// active view's rows/cards), `getBoardEl` for the one element that is that
// page's own board, if it has one (History's `#hist-table`, a World Cup
// page's active view container) — see requirements/transitions.md ->
// Cross-page navigation for why this can't just be assumed "already there"
// the way truly universal chrome (the cream background, the red Level 4
// strip's own styling) can: the two documents on either end of a link don't
// necessarily share an equivalent board (the homepage has none at all), so
// a page-specific board flies at board pace, same mechanism as a within-page
// board swap (flyOut()/flyIn() above), rather than sitting there unanimated.
function pageNavFlyItems() {
  return Array.from(document.querySelectorAll('.page-nav .view-toggle > *'));
}

// The `Home` chip is the identical link — same label, same href, same slot
// — on every tournament page and on history.html (see build.py's
// tournamentUtilityBar()/historyUtilityBar()), so it's the one chip this
// site currently has that can genuinely persist across a cross-page link
// (see requirements/transitions.md -> "The general rule"). Found by href
// rather than a dedicated class/id: nothing else on any page points at the
// homepage this way, and it naturally returns null on pages with no such
// chip at all (the homepage itself, whose own utility-bar buttons have no
// href), so callers don't need a separate page-type check.
function homeChip() {
  return document.querySelector('.page-nav .utility-bar a[href="../../index.html"]');
}

function setupCrossPageNav(getNavFlyItems, getContentFlyItems, getBoardEl) {
  function navFlyItems() {
    const items = (typeof getNavFlyItems === 'function') ? getNavFlyItems() : pageNavFlyItems();
    return items.filter(Boolean).filter(inFrame);
  }
  function contentFlyItems() {
    const items = (typeof getContentFlyItems === 'function') ? getContentFlyItems() : [];
    return items.filter(Boolean).filter(inFrame);
  }
  function boardEl() {
    const el = (typeof getBoardEl === 'function') ? getBoardEl() : null;
    return (el && inFrame(el)) ? el : null;
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
    const departingBoard = boardEl();
    // The Home chip persists onto the destination unmoved whenever the
    // destination has an identical one to land on — i.e. any link within
    // the World Cup/History pages except the Home chip's own link, which
    // leaves for the homepage, where no equivalent chip exists to persist
    // onto. See requirements/transitions.md -> "The general rule" and ->
    // Cross-page navigation.
    const home = homeChip();
    const homePersists = !!home && link !== home;
    // Content clears first, then the board (if this page has one), then nav
    // — see requirements/transitions.md -> Transitions -> "Layering". Each
    // phase must fully settle before the next starts, so this is chained
    // promises, not everything flying together. flyOut (board-level, from
    // above) resolves immediately via Promise.resolve() when there's no
    // board, same as flyOutItems already does for an empty item list — a
    // phase with nothing to do is skipped, not paused for.
    flyOutItems(contentFlyItems()).then(function() {
      return departingBoard ? flyOut([departingBoard]) : Promise.resolve();
    }).then(function() {
      const items = homePersists ? navFlyItems().filter(function(el) { return el !== home; }) : navFlyItems();
      return flyOutItems(items);
    }).then(function() {
      sessionStorage.setItem(NAV_FLY_KEY, '1');
      if (homePersists) {
        sessionStorage.setItem(NAV_PERSIST_HOME_KEY, '1');
      } else {
        sessionStorage.removeItem(NAV_PERSIST_HOME_KEY);
      }
      window.location.href = href;
    });
  });

  // Arrival — only a same-site click sets NAV_FLY_KEY, so this never fires
  // on a direct load/refresh, matching the sitewide "nothing flies on
  // load" default (see requirements/transitions.md -> Initial display)
  // with its one sanctioned exception.
  if (sessionStorage.getItem(NAV_FLY_KEY) === '1') {
    sessionStorage.removeItem(NAV_FLY_KEY);
    // Mirrors the departure side's `homePersists` — read once, here, rather
    // than re-derived, since this document has no way to inspect the page
    // that was just left. When true, the arriving Home chip is left out of
    // arrivalNavItems entirely below, so it's never pinned off-screen and
    // never flies in — it was already exactly where it needs to be.
    const homePersisted = sessionStorage.getItem(NAV_PERSIST_HOME_KEY) === '1';
    sessionStorage.removeItem(NAV_PERSIST_HOME_KEY);
    const persistedHome = homePersisted ? homeChip() : null;
    const arrivalNavItems = persistedHome ? navFlyItems().filter(function(el) { return el !== persistedHome; }) : navFlyItems();
    const arrivalContentItems = contentFlyItems();
    const arrivalBoard = boardEl();
    // Pinned off-screen the instant they exist — before any paint — but the
    // actual flight waits on document.fonts.ready: a render-blocking font
    // fetch racing against this script's synchronous class mutations could
    // otherwise let the whole staggered arrival execute before the browser
    // ever shows a frame of it, which reads as one clump landing instantly
    // rather than individually staggered pieces. See requirements/transitions.md
    // -> Cross-page navigation -> "Nav must already be standing before the
    // first thing behind it moves — never a race." This must cover the
    // board too, not just nav/content — a page's own board (its year
    // column, its table frame) is ordinary DOM content like anything else
    // on the page; nothing about it is exempt from being pinned before
    // first paint just because it never animates *within* a single page.
    arrivalNavItems.concat(arrivalContentItems).forEach(function(item) { item.classList.add('fly-item', 'fly-item-in-start'); });
    if (arrivalBoard) arrivalBoard.classList.add('fly-panel', 'fly-in-start');
    document.fonts.ready.then(function() {
      const locked = scrollLockEls();
      locked.forEach(function(el) { el.classList.add('fly-scroll-lock'); });
      // Nav settles first, then the board (if any), then content — the
      // reverse of the departure order above, per the same Layering rule.
      // Content items live nested inside the board element when there is
      // one (History's .hist-inner cells inside #hist-table, a World Cup
      // page's rows/cards inside its view container) — flying the board in
      // while a content item is still pinned at its own off-screen offset
      // composes correctly (the item's translate is relative to its
      // now-settling parent), so it stays correctly hidden until its own
      // phase starts, no special-casing needed here for that nesting.
      flyInItems(arrivalNavItems).then(function() {
        return arrivalBoard ? flyIn([arrivalBoard]) : Promise.resolve();
      }).then(function() {
        return flyInItems(arrivalContentItems);
      }).then(function() {
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
