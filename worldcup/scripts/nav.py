"""Shared fused-nav-bar rendering — the Level 1-3 component used by both the
homepage (build_home.py) and every World Cup page (build.py). Not a script:
no CLI, imported like knockout.py. See ../nav.css for the CSS this markup
depends on, and requirements/public.md -> Navigation for the full spec.

Only covers the "flat row of equal-width links" shape (Level 1 everywhere,
Level 2 and a plain Level 3 on the homepage). World Cup pages' own Level 2
(JS-driven view-switching buttons) and bespoke Level 3 variants (Rankings'
checkboxes, the Knockout round toggle, etc.) are different enough in
behavior that they stay hand-written in build.py — this module isn't trying
to cover every possible nav row, only the part that's genuinely identical
everywhere it appears.
"""


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def render_row(items, extra_classes, elem_id=None):
    """Render one flat, equal-width nav row.

    items: list of (label, href, state) tuples.
      - state 'active'   -> <strong class="active"> — current selection, non-linking, href ignored.
      - state 'disabled' -> <span class="disabled"> — no destination yet, non-linking, href ignored.
      - state None       -> <a href="..."> — a normal link; href is required.

    extra_classes: the row's own wrapper class(es) alongside "view-toggle",
    e.g. "utility-bar" (Level 1), "page-toggle primary-tabs" (Level 2),
    "detail-bar" (a plain Level 3).

    elem_id: optional id attribute on the <nav> itself, for a row a page
    needs to target directly (e.g. to show/hide it via CSS/JS) rather than
    relying on class selectors alone.
    """
    parts = []
    for label, href, state in items:
        if state == 'active':
            parts.append(f'<strong class="active">{esc(label)}</strong>')
        elif state == 'disabled':
            parts.append(f'<span class="disabled">{esc(label)}</span>')
        else:
            parts.append(f'<a href="{href}">{esc(label)}</a>')
    id_attr = f' id="{elem_id}"' if elem_id else ''
    return f'<nav{id_attr} class="{extra_classes} view-toggle">{"".join(parts)}</nav>'


def render_page_nav(*rows):
    """Fuse already-rendered rows into the Levels 1-3 .page-nav wrapper."""
    return '<div class="page-nav">' + ''.join(rows) + '</div>'
