# Way of Working

A tiny project: a couple of requirements docs + an implementation. Keep it that way.

There are two requirements docs, for two separate sites — see `00-index.md` for the full doc map:
- [requirements-public.md](requirements-public.md) — the public World Cup ELO site (`site/`). No admin/data-entry content of any kind.
- [requirements-admin.md](requirements-admin.md) — the (not yet built) internal admin site for entering results. Not a mirror of the public site.

## The loop

1. **Update requirements** — Human (with AI help) edits the relevant requirements doc to describe a desired change.
2. **Update implementation** — AI reads that doc and updates the corresponding implementation to match it.
3. **Review** — Human opens the implementation in a browser and checks it matches what the doc describes.
4. Repeat.

## Rules of thumb

- Each requirements doc describes *what its site* should do/look like, including scope/structure — that's defined there, not here.
- Each requirements doc is the source of truth for its own site. If the implementation and a requirements doc ever disagree, that's a bug — fix one to match the other.
- Keep the implementation as simple as the requirements docs allow — no npm, no bundler, no framework. `scripts/build.py` is the one build step; it regenerates embedded data in the HTML pages and is the intentional exception to this rule.

## Git

- Commit before running `scripts/set_result.py` or editing data files by hand. `build.py` writes directly to the HTML pages; a clean working tree is your only rollback if something goes wrong.
- Normal commit rhythm: one commit per session, or one per result batch if entering several games at once.

## Two-repo structure

This project uses two GitHub repos under the `sportsontheworldwideweb` account:

| Repo | Visibility | Purpose |
|------|------------|---------|
| `sportsontheworldwidewebadmin` | Private | Everything — source data, scripts, docs, shared.js/css, build tooling. This is where all work happens. |
| `sportsontheworldwideweb.github.io` | Public | Only the built `site/` output. What the world sees. No source files, no scripts, no docs. |

**What goes in the public repo:** the contents of `site/` only — HTML pages, flags, nothing else. Think of it as the website, not the project.

**What stays private:** `data/`, `scripts/`, `shared.js`, `shared.css`, `requirements-public.md`, `requirements-admin.md`, `way-of-working.md`, all docs. Anything that isn't a finished published page.

**Deploying:** run `scripts/deploy.py` to push the current `site/` contents to the public repo. Do this after a build when you're happy with the result. `scripts/update_day.py` and `scripts/set_result.py` are the automatic triggers — both commit/push to the admin repo and deploy to the public repo by default after updating scores, via the shared `scripts/gitops.py` helper (pass `--no-push` to opt out and update local files only).

**Remotes in the private repo:**
- `origin` → `sportsontheworldwidewebadmin` (private, push here normally)
- `public` → `sportsontheworldwideweb.github.io` (public, push via deploy script only)

**Admin site (future):** per `requirements-admin.md`, the admin site is local-only for now and has no deployment target. When it gets one, it should follow the same pattern as above — its own repo, pushed via its own deploy step, never mixed into either repo above. It must never end up in the public repo.

## Where CSS and JS changes go

The rendering logic is split across three layers:

- **`shared.css`** — all CSS shared across the three World Cup pages (base styles, table layout, toggle buttons, Rankings view styles). Changes here affect all years simultaneously.
- **`shared.js`** — all JS shared across the three World Cup pages: match-list rendering, the data-entry expand panel, ELO color logic, the Rankings view (Rank/Scale), and page-view switching. Changes here affect all years simultaneously.
- **Inline `<script>` in the page** — page-specific setup only: the embedded data constants (`games`, `teams`, `teamElos`), and the page configuration constants (`GAMES`, `YEAR`, `TEAM_ELOS`, `GAMESETS`, `CONFEDERATIONS`, DOM refs). Nothing else belongs here.

When in doubt: if the change would need to be made in more than one HTML file, it belongs in `shared.css` or `shared.js`.
