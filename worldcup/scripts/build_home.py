#!/usr/bin/env python3
"""Regenerate the homepage (site/index.html) from the nav config below.

The homepage's fused Level 1-3 nav is the exact same component (nav.py) and
CSS (../nav.css) as every World Cup page's own nav — see
requirements/public.md -> Navigation. Making the homepage a build artifact,
same as every other public page, means that shared component has exactly
one implementation instead of a hand-maintained second copy that could
silently drift from it.

build.py calls this automatically after every data change, so site/index.html
never falls out of sync with the shared nav component. Run this script
directly only if you've changed the homepage template (this file) itself.
"""
import sys
from pathlib import Path

import nav

ROOT = Path(__file__).resolve().parent.parent  # worldcup/ — nav.css lives here
PROJECT_ROOT = ROOT.parent  # repo root — site/index.html lives here

# Level 1 — one segment per sport category. href=None means no destination
# yet, rendered as the shared disabled state (see nav.py). 'active' means
# "you are here" — Football is the only sport with any content today.
LEVEL_1 = [
    ('Football', None, 'active'),
    ('Hockey', None, 'disabled'),
    ('Swimming', None, 'disabled'),
]

# Level 2 — one segment per competition within the selected sport. Football
# has exactly one today, so this renders as a single full-width active
# segment (see requirements/public.md -> Homepage -> Navigation).
LEVEL_2 = [
    ('World Cup', None, 'active'),
]

# Level 3 — two equal segments. Tournaments lands on the current/latest
# year; from there, that page's own Level 1 reaches any other year.
LEVEL_3 = [
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

# Homepage-only CSS: the header/tagline and page layout below the nav. The
# nav's own CSS lives in ../nav.css, loaded separately at build time so it
# stays the single source of truth shared with build.py's pages.
HOME_CSS = """*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Fredoka One', cursive; font-size: 1rem; line-height: 1.5; background: #F5F0E8; color: #1a1a1a; }
.page { max-width: 800px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }
.site-header h1 { font-family: 'Permanent Marker', cursive; font-size: 3rem; color: #1a1a1a; line-height: 1.1; text-align: center; }
.site-header .tagline { margin-top: 0.5rem; font-size: 1.1rem; color: #555; text-align: center; }"""


def build_home_html(nav_css):
    page_nav = nav.render_page_nav(
        nav.render_row(LEVEL_1, 'utility-bar'),
        nav.render_row(LEVEL_2, 'page-toggle primary-tabs'),
        nav.render_row(LEVEL_3, 'detail-bar'),
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
<style>
{nav_css}
{HOME_CSS}
</style>
</head>
<body>
{page_nav}
<div class="page">
  <header class="site-header">
    <h1>Sports! On the Internet. By David</h1>
    <p class="tagline">Sports data and visualizations. On the internet.</p>
  </header>
</div>
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
