# Index of Docs

This project has the following documents, each with one job. Don't blur these responsibilities.

[CLAUDE.md](CLAUDE.md), at the repo root, is the entry point an AI session loads automatically — it points here. Not listed in the table below since it's not part of the doc map itself, just the door into it.

## Project docs (not deployed)

Docs that apply to the whole site (not any one feature) live at the root:

| # | Doc | Responsibility |
|---|-----|----------------|
| 1 | [00-index.md](00-index.md) | This file. Map of the project — what each doc does and where things live. |
| 2 | [way-of-working.md](way-of-working.md) | How we (human + AI) operate this project. Workflow, process, brand, visual direction. |
| 3 | [brand.md](brand.md) | "Sports! On the Internet. By David" brand: concept, audience, voice, visual direction. |
| 4 | [open-questions.md](open-questions.md) | Unresolved project-level questions (naming, hosting, etc.) that don't block work but shouldn't be forgotten. |
| 5 | [operations.md](operations.md) | Account inventory, domain/DNS, and hosting/deployment facts. Not a build doc — reference only. |

Multi-session milestones (a rebrand, an infra migration) are tracked as a checklist in `workbench/<milestone-name>.md` — see `way-of-working.md` → *Milestones*. The folder is empty between milestones, so it has no permanent entry here.

Everything specific to a single feature lives in its own top-level folder, named after the feature. World Cup ELO is the first (and so far only) feature:

| # | Doc | Responsibility |
|---|-----|----------------|
| 6a | [worldcup/requirements-public.md](worldcup/requirements-public.md) | What the public World Cup ELO site should be/do. Source of truth for desired behavior on the site anyone can visit — no admin/data-entry content. |
| 6b | [worldcup/requirements-admin.md](worldcup/requirements-admin.md) | What the admin site should be/do. Source of truth for the internal data-entry tool. Not a mirror of the public site — see the doc for why. |
| 7 | [worldcup/scale-algorithm.md](worldcup/scale-algorithm.md) | Deep-dive on the Scale view layout algorithm. Update when scale rendering logic changes. |
| 8 | [worldcup/scripts/build.py](worldcup/scripts/build.py) | Regenerates the public HTML pages in site/ from worldcup/data/*.json and worldcup/shared.js/shared.css. Also calls build_admin.py, so one run keeps both sites in sync. |
| 9 | [worldcup/scripts/build_admin.py](worldcup/scripts/build_admin.py) | Regenerates the admin site's per-year pages in admin/. Same embed-at-build-time pattern as build.py — no server, no runtime fetch. |
| 10 | [worldcup/scripts/set_result.py](worldcup/scripts/set_result.py) | Enters a game result and calls build.py. The normal data-entry path. |
| 11 | [worldcup/scripts/set_team_elo.py](worldcup/scripts/set_team_elo.py) | Sets a team's initial ELO and calls build.py. |
| 12 | [worldcup/scripts/knockout.py](worldcup/scripts/knockout.py) | Shared knockout-bracket round-shape logic (no CLI) — used by build.py and the two scripts below. |
| 13 | [worldcup/scripts/set_knockout_size.py](worldcup/scripts/set_knockout_size.py) | One-time per-tournament setup: sets the bracket size and scaffolds its games. |
| 14 | [worldcup/scripts/set_bracket_game.py](worldcup/scripts/set_bracket_game.py) | Sets a knockout game's date and/or participants (team or feed reference) and calls build.py. |
| 15 | [worldcup/data/](worldcup/data/) | Source data: one JSON file per World Cup (1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026) plus teams.json. Not deployed directly. |
| 16 | [worldcup/shared.js](worldcup/shared.js) | Shared JS source — inlined into World Cup pages at build time. |
| 17 | [worldcup/shared.css](worldcup/shared.css) | Shared CSS source — inlined into World Cup pages at build time. |

## Site (deployed)

Everything under `site/` is what goes online. The static host points at this folder. All features' output lives here together, regardless of which feature folder generated it — `site/` never gets a `worldcup/` layer of its own inside it.

| Path | Responsibility |
|------|----------------|
| [site/index.html](site/index.html) | "Sports! On the Internet. By David" homepage. |
| [site/CNAME](site/CNAME) | GitHub Pages custom-domain file (`sports-on-the-internet-by-david.com`). Committed as-is; `deploy.py` wipes and replaces the public repo's contents on every deploy, so this must exist in `site/` or the live domain breaks. |
| [site/football/worldcup/history.html](site/football/worldcup/history.html) | Year-over-year knockout comparison (F4/F8/F16). Build artifact — do not edit directly. |
| [site/football/worldcup/1998.html](site/football/worldcup/1998.html) | World Cup 1998 page (and one per other year: 2002, 2006, 2010, 2014, 2018, 2022, 2026). Build artifact — do not edit directly. |
| [site/football/worldcup/flags/](site/football/worldcup/flags/) | Flag SVGs served alongside the World Cup pages. |

## Admin (local-only, not deployed)

The admin site described in `worldcup/requirements-admin.md` lives in `admin/` — a top-level folder, sibling to `site/`, never nested under it. Unlike `site/`, this is never deployed anywhere: no static host points at it, and it must never be pushed to the public repo (see `way-of-working.md` → *Two-repo structure*). Like `site/`, its pages open directly via `file://` — no server — since `worldcup/scripts/build_admin.py` embeds each page's data at build time, same as the public site. (In the future we'll add an actual backend; see `worldcup/requirements-admin.md` → *Hosting*.)

| Path | Responsibility |
|------|----------------|
| [admin/2026.html](admin/2026.html) | World Cup 2026 admin page (and one per other year). Build artifact — do not edit directly. |

## Adding a new feature

1. Create a top-level folder for it (e.g. `basketball/`), holding that feature's requirements docs, scripts, data, and shared CSS/JS — mirroring how `worldcup/` is structured.
2. Create its output folder under `site/` (e.g. `site/basketball/`).
3. Add a link from `site/index.html`.
4. Update this index.
