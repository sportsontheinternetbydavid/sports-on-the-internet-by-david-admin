# Way of Working

A tiny project: a requirements doc + an implementation. Keep it that way.

## The loop

1. **Update requirements** — Human (with AI help) edits `requirements.md` to describe a desired change.
2. **Update implementation** — AI reads `requirements.md` and updates the implementation to match it.
3. **Review** — Human opens the implementation in a browser and checks it matches what `requirements.md` describes.
4. Repeat.

## Rules of thumb

- `requirements.md` describes *what* the site should do/look like, including scope/structure (e.g. single page vs multiple) — that's defined there, not here.
- `requirements.md` is the source of truth. If the implementation and `requirements.md` ever disagree, that's a bug — fix one to match the other.
- Keep the implementation as simple as `requirements.md` allows — no npm, no bundler, no framework. `scripts/build.py` is the one build step; it regenerates embedded data in the HTML pages and is the intentional exception to this rule.

## Git

- Commit before running `scripts/set_result.py` or editing data files by hand. `build.py` writes directly to the HTML pages; a clean working tree is your only rollback if something goes wrong.
- Normal commit rhythm: one commit per session, or one per result batch if entering several games at once.

## Where JS changes go

The rendering logic is split across two layers:

- **`shared.js`** — everything that applies to the match-list table on all three World Cup pages: rendering, the data-entry expand panel, ELO color logic, etc. Changes here affect all years simultaneously.
- **Inline `<script>` in the page** — page-specific setup (`GAMES`, `YEAR`, `CONFEDERATIONS`, DOM refs) plus any feature that only exists on that page (e.g. the Rankings view in `2026.html`). If a feature only makes sense for one year, it stays there.

When in doubt: if the change would need to be made in more than one HTML file, it belongs in `shared.js`.
