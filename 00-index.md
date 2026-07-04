# Index of Docs

This project has the following documents, each with one job. Don't blur these responsibilities.

## Project docs (not deployed)

Docs that apply to the whole site (not any one feature) live at the root:

| # | Doc | Responsibility |
|---|-----|----------------|
| 1 | [00-index.md](00-index.md) | This file. Map of the project — what each doc does and where things live. |
| 2 | [way-of-working.md](way-of-working.md) | How we (human + AI) operate this project. Workflow, process, brand, visual direction. |
| 3 | [brand.md](brand.md) | SportsOnTheInternet brand: concept, audience, voice, visual direction. |
| 4 | [open-questions.md](open-questions.md) | Unresolved project-level questions (naming, hosting, etc.) that don't block work but shouldn't be forgotten. |

Everything specific to a single feature lives in its own top-level folder, named after the feature. World Cup ELO is the first (and so far only) feature:

| # | Doc | Responsibility |
|---|-----|----------------|
| 5a | [worldcup/requirements-public.md](worldcup/requirements-public.md) | What the public World Cup ELO site should be/do. Source of truth for desired behavior on the site anyone can visit — no admin/data-entry content. |
| 5b | [worldcup/requirements-admin.md](worldcup/requirements-admin.md) | What the admin site should be/do. Source of truth for the internal data-entry tool. Not a mirror of the public site — see the doc for why. |
| 6 | [worldcup/scale-algorithm.md](worldcup/scale-algorithm.md) | Deep-dive on the Scale view layout algorithm. Update when scale rendering logic changes. |
| 7 | [worldcup/scripts/build.py](worldcup/scripts/build.py) | Regenerates the public HTML pages in site/ from worldcup/data/*.json and worldcup/shared.js/shared.css. |
| 8 | [worldcup/scripts/build_admin.py](worldcup/scripts/build_admin.py) | Regenerates the admin site's per-year pages in admin/. Data is fetched at runtime, not embedded. |
| 9 | [worldcup/scripts/set_result.py](worldcup/scripts/set_result.py) | Enters a game result and calls build.py. The normal data-entry path. |
| 10 | [worldcup/scripts/set_team_elo.py](worldcup/scripts/set_team_elo.py) | Sets a team's initial ELO and calls build.py. |
| 11 | [worldcup/data/](worldcup/data/) | Source data: one JSON file per World Cup (1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026) plus teams.json. Not deployed directly. |
| 12 | [worldcup/shared.js](worldcup/shared.js) | Shared JS source — inlined into World Cup pages at build time. |
| 13 | [worldcup/shared.css](worldcup/shared.css) | Shared CSS source — inlined into World Cup pages at build time. |

## Site (deployed)

Everything under `site/` is what goes online. The static host points at this folder. All features' output lives here together, regardless of which feature folder generated it — `site/` never gets a `worldcup/` layer of its own inside it.

| Path | Responsibility |
|------|----------------|
| [site/index.html](site/index.html) | SportsOnTheInternet homepage. |
| [site/football/worldcup/history.html](site/football/worldcup/history.html) | Year-over-year knockout comparison (F4/F8/F16). Build artifact — do not edit directly. |
| [site/football/worldcup/1998.html](site/football/worldcup/1998.html) | World Cup 1998 page (and one per other year: 2002, 2006, 2010, 2014, 2018, 2022, 2026). Build artifact — do not edit directly. |
| [site/football/worldcup/flags/](site/football/worldcup/flags/) | Flag SVGs served alongside the World Cup pages. |

## Admin (local-only, not deployed)

The admin site described in `worldcup/requirements-admin.md` lives in `admin/` — a top-level folder, sibling to `site/`, never nested under it. Unlike `site/`, this is never deployed anywhere: no static host points at it, and it must never be pushed to the public repo (see `way-of-working.md` → *Two-repo structure*). It's served locally only, e.g. `python3 -m http.server --directory .` from the repo root, so its pages can fetch `worldcup/data/*.json` at runtime.

| Path | Responsibility |
|------|----------------|
| [admin/2026.html](admin/2026.html) | World Cup 2026 admin page (and one per other year). Build artifact — do not edit directly. |

## Adding a new feature

1. Create a top-level folder for it (e.g. `basketball/`), holding that feature's requirements docs, scripts, data, and shared CSS/JS — mirroring how `worldcup/` is structured.
2. Create its output folder under `site/` (e.g. `site/basketball/`).
3. Add a link from `site/index.html`.
4. Update this index.
