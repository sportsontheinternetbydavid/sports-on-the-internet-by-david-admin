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
| 5b | [worldcup/requirements-admin.md](worldcup/requirements-admin.md) | What the (separate, not-yet-built) admin site should be/do. Source of truth for the internal data-entry tool. Not a mirror of the public site — see the doc for why. |
| 6 | [worldcup/scale-algorithm.md](worldcup/scale-algorithm.md) | Deep-dive on the Scale view layout algorithm. Update when scale rendering logic changes. |
| 7 | [worldcup/scripts/build.py](worldcup/scripts/build.py) | Regenerates HTML pages in site/ from worldcup/data/*.json and worldcup/shared.js/shared.css. |
| 8 | [worldcup/scripts/set_result.py](worldcup/scripts/set_result.py) | Enters a game result and calls build.py. The normal data-entry path. |
| 9 | [worldcup/scripts/set_team_elo.py](worldcup/scripts/set_team_elo.py) | Sets a team's initial ELO and calls build.py. |
| 10 | [worldcup/data/](worldcup/data/) | Source data: 2014.json, 2018.json, 2022.json, 2026.json, teams.json. Not deployed directly. |
| 11 | [worldcup/shared.js](worldcup/shared.js) | Shared JS source — inlined into World Cup pages at build time. |
| 12 | [worldcup/shared.css](worldcup/shared.css) | Shared CSS source — inlined into World Cup pages at build time. |

## Site (deployed)

Everything under `site/` is what goes online. The static host points at this folder. All features' output lives here together, regardless of which feature folder generated it — `site/` never gets a `worldcup/` layer of its own inside it.

| Path | Responsibility |
|------|----------------|
| [site/index.html](site/index.html) | SportsOnTheInternet homepage. |
| [site/football/worldcup/history.html](site/football/worldcup/history.html) | Year-over-year knockout comparison (F4/F8/F16). Build artifact — do not edit directly. |
| [site/football/worldcup/2014.html](site/football/worldcup/2014.html) | World Cup 2014 page. Build artifact — do not edit directly. |
| [site/football/worldcup/2018.html](site/football/worldcup/2018.html) | World Cup 2018 page. Build artifact — do not edit directly. |
| [site/football/worldcup/2022.html](site/football/worldcup/2022.html) | World Cup 2022 page. Build artifact — do not edit directly. |
| [site/football/worldcup/2026.html](site/football/worldcup/2026.html) | World Cup 2026 page. Build artifact — do not edit directly. |
| [site/football/worldcup/flags/](site/football/worldcup/flags/) | Flag SVGs served alongside the World Cup pages. |

The admin site described in `worldcup/requirements-admin.md` has no output folder yet — it hasn't been built. When it is, its output goes in `admin/` (a new top-level folder, sibling to `site/`) — never under `site/`, since `site/` is what gets deployed to the public repo (see `way-of-working.md` → *Two-repo structure*) and the admin site must never end up there.

## Adding a new feature

1. Create a top-level folder for it (e.g. `basketball/`), holding that feature's requirements docs, scripts, data, and shared CSS/JS — mirroring how `worldcup/` is structured.
2. Create its output folder under `site/` (e.g. `site/basketball/`).
3. Add a link from `site/index.html`.
4. Update this index.
