# Cross-page nav: per-view content still doesn't fly on WC-year pages

`requirements/public.md` → *Cross-page navigation* (line ~151) requires that on a cross-page arrival/departure, not just nav chips but the active view's own content flies too — for Match List specifically, at sub-row grain (each flag/score/ELO figure/confederation cell individually, finer than its usual in-page row-swap grain), and for Groups/Knockout/Rankings at their existing finest grain (card/flag).

Fixed in this pass: every page now has working cross-page nav chip flying (`setupCrossPageNav()` in `fly.js`), including the WC-year pages that previously had none at all. **Not** fixed: the active view's own content on WC-year pages. `setupCrossPageNav()` is called there with no override, so it only flies nav chips — matching History's behavior for its own nav, but not matching History's *content* handling (History does fly its table cells, via its own extra-items function).

Why not just done alongside the nav-chip fix: Match List's rows are built by `shared.js`'s `renderElo`/`renderWld`/`renderStats` as raw `<td>` cells with no inner per-piece wrapper (unlike History's `.hist-inner` divs, purpose-built for exactly this). Giving Match List the same per-piece flyability needs those render functions to wrap each flag/score/ELO figure in its own element — a template change to the site's single most-used rendering path, not a one-line addition, and risky to rush alongside everything else in this session.

## To finish this

- [ ] Wrap Match List's per-cell pieces (flag, score, ELO figure, confederation cell) in flyable inner elements, mirroring History's `.hist-inner` pattern — needed in `renderElo`/`renderWld`/`renderStats` (`worldcup/shared.js`).
- [ ] Write a `matchListFlyItems()` (or similar) helper gathering those pieces, analogous to `histItems()`.
- [ ] Gather the *active* view's own items for Groups/Knockout/Rankings too — Knockout's game cards and Rankings' flags are already individually-meaningful elements (per requirements, no further restructuring needed there, just a gathering function); Groups has no real content yet (still a "coming soon" placeholder).
- [ ] Pass a combined extra-items function to `setupCrossPageNav()` in `build.py`'s `page_html()` template, switching on `currentPageView`, so departure flies whichever view is actually showing and arrival flies Match List (the only view a fresh cross-page arrival ever lands on today).
- [ ] Delete this file once done — the fix belongs in `build.py`/`shared.js`/`fly.js` and their own comments, not here.
