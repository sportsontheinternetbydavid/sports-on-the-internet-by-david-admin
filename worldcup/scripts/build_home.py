#!/usr/bin/env python3
"""Regenerate the homepage (site/index.html) from the nav config below.

The homepage's nav is the exact same component (nav.py) and CSS (../nav.css)
as every World Cup page's own nav — see requirements/public.md -> Navigation.
Making the homepage a build artifact, same as every other public page, means
that shared component has exactly one implementation instead of a
hand-maintained second copy that could silently drift from it.

Unlike every other page, this one has up to four levels instead of three:
while "Sports!" is selected (the default/landing state), Levels 2-4 are the
site's signature (name + tagline) instead of a separate header block — see
requirements/public.md -> Homepage -> Navigation.

build.py calls this automatically after every data change, so site/index.html
never falls out of sync with the shared nav component. Run this script
directly only if you've changed the homepage template (this file) itself.
"""
import sys
from pathlib import Path

import nav

ROOT = Path(__file__).resolve().parent.parent  # worldcup/ — nav.css lives here
PROJECT_ROOT = ROOT.parent  # repo root — site/index.html lives here

# Level 1 is a client-side toggle between "Sports!" (the default/landing
# state) and "Football" — see requirements/public.md -> Homepage ->
# Navigation. Hand-written below (like build.py's JS-driven view toggles)
# rather than via nav.render_row, which only covers static flat rows with no
# client-side behavior.

# "Sports!" state — Levels 2-3 are the site's signature, one line per level,
# in place of a separate header block.
SPORTS_LEVEL_2 = [('On the Internet.', None, 'active')]
SPORTS_LEVEL_3 = [('By David', None, 'active')]

# "Football" state — Level 2: one segment per major football tournament.
# World Cup is the only one with any content today; the rest are the next
# posters waiting to be made.
FOOTBALL_LEVEL_2 = [
    ('World Cup', None, 'active'),
    ('Euros', None, 'disabled'),
    ('Copa América', None, 'disabled'),
    ('Gold Cup', None, 'disabled'),
]

# "Football" state — Level 3: two equal segments. Tournaments lands on the
# current/latest year; from there, that page's own Level 1 reaches any other
# year.
FOOTBALL_LEVEL_3 = [
    ('History', 'football/worldcup/history.html', None),
    ('Tournaments', 'football/worldcup/2026.html', None),
]

FAVICON_SCRIPT = """<script>
(function() {
  function faviconHref(isLocal) {
    var dash = isLocal ? ' stroke-dasharray="3 2.5"' : '';
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
      + '<circle cx="16" cy="16" r="14" fill="#F5F0E8" stroke="#1A5276" stroke-width="2.5"' + dash + '/>'
      + '<path d="M16,10 L21.7,14.2 L19.5,20.9 L12.5,20.9 L10.3,14.2 Z" fill="#1A5276"/>'
      + '</svg>';
    return 'data:image/svg+xml,' + encodeURIComponent(svg);
  }
  window.__setFavicon = function() {
    var isLocal = ['localhost', '127.0.0.1', ''].indexOf(location.hostname) !== -1;
    var link = document.querySelector('link[rel="icon"]');
    if (!link) {
      link = document.createElement('link');
      link.rel = 'icon';
      document.head.appendChild(link);
    }
    link.type = 'image/svg+xml';
    link.href = faviconHref(isLocal);
  };
  window.__setFavicon();
})();
</script>"""

# Homepage-only CSS: the page's base look, plus the Sports!/Football fly
# in/out transition (its own richer per-child-stagger choreography — see
# .home-group below — rather than nav.css's simpler single-element
# .fly-panel primitive that other pages use for their own swaps). The
# chip material/color/tape system itself lives entirely in ../nav.css now
# (originally piloted homepage-only, since promoted everywhere), loaded
# separately at build time so it stays the single source of truth shared
# with build.py's pages.
HOME_CSS = """*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { overflow: hidden; }
/* max-width + margin:0 auto matches shared.css's body rule (used by every
   World Cup page) — see requirements/public.md -> Navigation: the nav
   "spans the page's full content width (the same max width the rest of
   the page uses ... not shrink-to-fit)". Without this, the row is full
   raw-viewport width, so on a wide monitor the centered signature (which
   centers within that row) ends up centered relative to the whole screen
   instead of a reasonable content column, drifting far from the
   left-aligned Level 1 chips above it. */
body { font-family: 'Fredoka One', cursive; font-size: 1rem; line-height: 1.5; background: #F5F0E8; color: #1a1a1a; overflow: hidden; max-width: 1100px; margin: 0 auto; }
/* The parked (not-currently-shown) group rests at translateX(+/-105vw) —
   fully off-screen, but position:absolute content still counts toward the
   page's scrollable area, which would otherwise stretch the document far
   past the viewport width. This page never needs to scroll on either axis
   (see requirements/public.md -> Homepage -> Layout — the nav *is* the
   page), so overflow:hidden on both html and body clips it outright,
   rather than just overflow-x — hiding only one axis makes the other
   axis's overflow compute to `auto` per spec, which let a few stray
   pixels of vertical overflow (from a chip's shadow/tape poking past the
   last row) trigger a real vertical scrollbar that silently ate into the
   content width and threw off centering. */
/* The "Sports!" signature (On the Internet. / By David / the tagline) is
   the site's byline, not a choice — see requirements/public.md -> Navigation
   -> "The homepage signature is exempt". No chip styling at all: no fill,
   no shadow, no tape, no rotation, just handwritten/printed text directly
   on the page, sized down in weight level by level. */
/* Every row is left-aligned everywhere else on the site (see
   requirements/public.md -> Navigation -> General nav chip characteristics)
   because those pages are functional multi-page toolbars. The homepage
   isn't — it's one splash/title composition ("the nav *is* the page"), so
   every row centers here instead: Level 1 above, and both states' Level 2/3
   below it (Football's World Cup/Euros/etc and History/Tournaments, not
   just the Sports! signature). Left-aligning some rows and centering others
   within the same wide content column left them individually correct but
   visually disconnected from each other — centering everything is what
   makes the whole block read as one thing, in either state. Deliberate
   homepage-only exception, not a change to the general rule. */
#page-nav .view-toggle { justify-content: center; }
#sports-level2 strong.active { background: none; box-shadow: none; transform: none; color: #C0392B; font-size: 1.4rem; padding: 0; }
#sports-level2 strong.active::before { display: none; }
#sports-level3 strong.active { background: none; box-shadow: none; transform: none; color: #5a4a3a; font-size: 1.1rem; padding: 0; }
#sports-level3 strong.active::before { display: none; }
/* A little breathing room on all sides so a chip's shadow/tape isn't
   clipped by the viewport edge (or, since overflow:hidden above means
   clipping is literal, cut off outright) — not a "top margin above the
   nav" in the sense requirements/public.md rules out, just enough for the
   paper material's own shadow/rotation/scale to render. Left/right matter
   most for a *selected* chip flush against the row's edge: its
   scale(1.06) pushes the transformed edge a few px past the unscaled
   edge, which needs somewhere to go now that overflow is clipped rather
   than just unreachable by scroll. */
#page-nav { padding: 10px 8px; }

/* Both groups are stacked in the same box (position:absolute, same
   top/left) instead of being normal-flow siblings — otherwise, for the
   moment both are visible mid-crossfade, whichever is second in the DOM
   gets pushed down by the other's height, then pops into its real position
   once the other is hidden. #home-groups-wrap reserves height explicitly
   (see setHomeView) since neither absolutely positioned child contributes
   to it automatically. */
#home-groups-wrap { position: relative; transition: height 0.6s ease; }
.home-group { position: absolute; top: 0; left: 0; width: 100%; display: flex; flex-direction: column; gap: 10px; }
/* Speed is an experimental homepage-only override — see
   requirements/public.md -> Navigation -> Transitions -> "Homepage
   exception": production feedback called the original ~100-150ms pacing
   too fast to read as physical paper sliding. Every other use of this
   transition elsewhere on the site keeps the fast/under-200ms pacing until
   this is validated. */
/* Transform only, never opacity — see requirements/public.md's -> Motion
   in brand-guidelines.md: physical paper doesn't dissolve, it slides. A
   group stays fully opaque throughout; leaving/entering the frame is what
   makes it disappear/appear. */
.home-group > * { transition: transform 0.85s linear; }
.home-group > *:nth-child(2) { transition-delay: 0.2s; }
/* Exit off one side (right — taken off), enter from the other (left — put
   on): a one-way conveyor, not things retracing the same path. */
.home-group.fly-out { pointer-events: none; }
.home-group.fly-out > * { transform: translateX(105vw) rotate(8deg); }
.home-group.fly-in-start { pointer-events: none; }
.home-group.fly-in-start > * { transform: translateX(-105vw) rotate(-8deg); transition: none !important; }
.home-group.fly-in-active > * { transform: translateX(0) rotate(0deg); transition: transform 0.85s cubic-bezier(.1,.6,.2,1); }
.home-group.fly-in-active > *:nth-child(2) { transition-delay: 0.2s; }"""

# Level 1's own JS toggle between "Sports!" and "Football" — see
# requirements/public.md -> Homepage -> Navigation -> Transitions. No page
# reload; the two groups are always both present (position:absolute, see
# HOME_CSS) and only ever differ by class, so switching never has to fight
# document flow for layout.
HOME_SCRIPT = """<script>
var __currentHomeView = 'sports';
function setHomeView(view) {
  if (view === __currentHomeView) return;
  document.getElementById('tab-sports').classList.toggle('active', view === 'sports');
  document.getElementById('tab-football').classList.toggle('active', view === 'football');

  var outgoing = document.getElementById(__currentHomeView + '-group');
  var incoming = document.getElementById(view + '-group');

  outgoing.classList.remove('fly-in-active');
  outgoing.classList.add('fly-out');

  incoming.classList.remove('fly-out');
  incoming.classList.add('fly-in-start');
  void incoming.offsetWidth;
  requestAnimationFrame(function() {
    incoming.classList.remove('fly-in-start');
    incoming.classList.add('fly-in-active');
  });

  document.getElementById('home-groups-wrap').style.height = incoming.scrollHeight + 'px';
  __currentHomeView = view;
}
window.addEventListener('DOMContentLoaded', function() {
  document.getElementById('home-groups-wrap').style.height = document.getElementById('sports-group').scrollHeight + 'px';
});
</script>"""


def build_home_html(nav_css):
    level_1 = ('<nav class="utility-bar view-toggle">'
               '<button id="tab-sports" class="active" onclick="setHomeView(\'sports\')">Sports!</button>'
               '<button id="tab-football" onclick="setHomeView(\'football\')">Football</button>'
               '<span class="disabled">Hockey</span>'
               '<span class="disabled">Swimming</span>'
               '</nav>')
    sports_level_2 = nav.render_row(SPORTS_LEVEL_2, 'page-toggle primary-tabs', elem_id='sports-level2')
    sports_level_3 = nav.render_row(SPORTS_LEVEL_3, 'detail-bar', elem_id='sports-level3')
    football_level_2 = nav.render_row(FOOTBALL_LEVEL_2, 'page-toggle primary-tabs', elem_id='football-level2')
    football_level_3 = nav.render_row(FOOTBALL_LEVEL_3, 'detail-bar', elem_id='football-level3')
    # Both groups are always present (position:absolute, see HOME_CSS) —
    # "football-group" starts parked in its resting hidden state (fly-out)
    # rather than display:none, and setHomeView (see HOME_SCRIPT) never has
    # to toggle display at all, only these two classes.
    page_nav = (
        '<div class="page-nav" id="page-nav">'
        f'{level_1}'
        '<div id="home-groups-wrap">'
        f'<div id="sports-group" class="home-group fly-in-active">{sports_level_2}{sports_level_3}</div>'
        f'<div id="football-group" class="home-group fly-out">{football_level_2}{football_level_3}</div>'
        '</div>'
        '</div>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sports! On the Internet. By David</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Fredoka+One&display=swap" rel="stylesheet">
{FAVICON_SCRIPT}
{HOME_SCRIPT}
<style>
{nav_css}
{HOME_CSS}
</style>
</head>
<body>
{page_nav}
</body>
</html>
"""


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    nav_css = (ROOT / "nav.css").read_text()
    html = build_home_html(nav_css)
    path = PROJECT_ROOT / "site" / "index.html"
    path.write_text(html)
    print("Updated site/index.html")


if __name__ == "__main__":
    main()
