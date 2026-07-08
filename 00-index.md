# Index of Docs

This project has the following documents, each with one job. Don't blur these responsibilities.

[CLAUDE.md](CLAUDE.md), at the repo root, is the entry point an AI session loads automatically — it points here. Not listed in the table below since it's not part of the doc map itself, just the door into it.

## Project docs (not deployed)

Docs that apply to the whole site (not any one feature) live at the root:

| # | Doc | Responsibility |
|---|-----|----------------|
| 1 | [00-index.md](00-index.md) | This file. Map of the project — what each doc does and where things live. |
| 2 | [way-of-working.md](way-of-working.md) | How we (human + AI) operate this project: the requirements-doc loop, git rhythm, session/state hygiene. Process, not architecture — see `technical.md` for that. |
| 3 | [technical.md](technical.md) | How the system is actually built: two-repo structure, every script's job, the build pipeline, where CSS/JS/markup changes go. Architecture reference, not process. |
| 4 | [brand-guidelines.md](brand-guidelines.md) | "Sports! On the Internet. By David" brand: concept, audience, voice, visual direction. Applies to the public site only — not admin. |
| 5 | [requirements/public.md](requirements/public.md) | What the public-facing site should be/do — the homepage plus every public feature under it (currently just World Cup). Source of truth for desired behavior on the site anyone can visit — no admin/data-entry content. |
| 6 | [requirements/navigation.md](requirements/navigation.md) | Deep-dive on the shared nav "sticky notes" design system and the sitewide fly in/out transition rules — factored out of `public.md` since it's cross-cutting infrastructure used by every page/feature, not any one feature's own content. A requirements doc, so it lives alongside public.md/admin.md rather than in a feature's own folder. |
| 7 | [requirements/admin.md](requirements/admin.md) | What the admin site should be/do — source of truth for the internal data-entry tool, covering every feature that has one (currently just World Cup). Not a mirror of the public site — see the doc for why. |
| 8 | [requirements/scale-algorithm.md](requirements/scale-algorithm.md) | Deep-dive on the World Cup Rankings Scale view's layout algorithm — a requirements doc, so it lives alongside public.md/admin.md rather than in the feature's own folder. Update when scale rendering logic changes. |
| 9 | [open-questions.md](open-questions.md) | Unresolved project-level questions (naming, hosting, etc.) that don't block work but shouldn't be forgotten. |
| 10 | [operations.md](operations.md) | Account inventory, domain/DNS, and hosting/deployment facts. Not a build doc — reference only. |

Multi-session milestones (a rebrand, an infra migration) are tracked as a checklist in `workbench/<milestone-name>.md` — see `way-of-working.md` → *Milestones*. The folder is empty between milestones, so it has no permanent entry here.

A feature's own requirements (what it does, page by page — including any deep-dive docs, like the scale-algorithm one above) live in `requirements/`, not in the feature's own folder. The feature folder holds everything else: scripts, data, and shared CSS/JS. World Cup ELO is the first (and so far only) feature:

| # | Doc | Responsibility |
|---|-----|----------------|
| 11 | [worldcup/scripts/build.py](worldcup/scripts/build.py) | Regenerates the public HTML pages in site/ from worldcup/data/*.json and worldcup/shared.js/shared.css. Also calls build_home.py and build_admin.py, so one run keeps all three surfaces in sync. |
| 12 | [worldcup/scripts/build_home.py](worldcup/scripts/build_home.py) | Regenerates the homepage (site/index.html) from a small nav config — see nav.py. Homepage is a build artifact for exactly this reason: so its nav has one implementation, not a hand-maintained second copy. |
| 13 | [worldcup/scripts/build_admin.py](worldcup/scripts/build_admin.py) | Regenerates the admin site's per-year pages in admin/. Same embed-at-build-time pattern as build.py — no server, no runtime fetch. |
| 14 | [worldcup/scripts/nav.py](worldcup/scripts/nav.py) | Shared fused-nav-bar rendering (no CLI) — used by build.py (Level 1 on every World Cup page) and build_home.py (the homepage's whole nav). See ../nav.css for the CSS it depends on. |
| 15 | [worldcup/nav.css](worldcup/nav.css) | Single source of truth for the fused Level 1-3 nav's visual rules, shared between World Cup pages and the homepage. Page-specific Level 3 variants (Rankings, Knockout, etc.) keep their own CSS in shared.css. |
| 16 | [worldcup/scripts/set_result.py](worldcup/scripts/set_result.py) | Enters a game result and calls build.py. The normal data-entry path. |
| 17 | [worldcup/scripts/set_team_elo.py](worldcup/scripts/set_team_elo.py) | Sets a team's initial ELO and calls build.py. |
| 18 | [worldcup/scripts/knockout.py](worldcup/scripts/knockout.py) | Shared knockout-bracket round-shape logic (no CLI) — used by build.py and the two scripts below. |
| 19 | [worldcup/scripts/set_knockout_size.py](worldcup/scripts/set_knockout_size.py) | One-time per-tournament setup: sets the bracket size and scaffolds its games. |
| 20 | [worldcup/scripts/set_bracket_game.py](worldcup/scripts/set_bracket_game.py) | Sets a knockout game's date and/or participants (team or feed reference) and calls build.py. |
| 21 | [worldcup/data/](worldcup/data/) | Source data: one JSON file per World Cup (1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026) plus teams.json. Not deployed directly. |
| 22 | [worldcup/shared.js](worldcup/shared.js) | Shared JS source — inlined into World Cup pages at build time. |
| 23 | [worldcup/shared.css](worldcup/shared.css) | Shared CSS source (World Cup pages' own Level 3 variants, tables, flags, rankings, bracket, etc.) — inlined into World Cup pages at build time. |
| 24 | [worldcup/fly.js](worldcup/fly.js) | Shared JS source for the item-level fly primitive and the cross-page nav protocol — used by the homepage *and* every World Cup page. Unlike 22/23 above, not inlined: `build.py`/`build_home.py` copy it verbatim to `site/` (see below) and every page loads it via `<script src="fly.js">`. See `technical.md` → *Where CSS and JS changes go*. |

## Site (deployed)

Everything under `site/` is what goes online. The static host points at this folder. All features' output lives here together, regardless of which feature folder generated it — `site/` never gets a `worldcup/` layer of its own inside it.

| Path | Responsibility |
|------|----------------|
| [site/index.html](site/index.html) | "Sports! On the Internet. By David" homepage. Build artifact (generated by `worldcup/scripts/build_home.py`) — do not edit directly. |
| [site/CNAME](site/CNAME) | GitHub Pages custom-domain file (`sports-on-the-internet-by-david.com`). Committed as-is; `deploy.py` wipes and replaces the public repo's contents on every deploy, so this must exist in `site/` or the live domain breaks. |
| [site/fly.js](site/fly.js) | Verbatim copy of `worldcup/fly.js`, loaded by `index.html` via `<script src>`. Build artifact — do not edit directly; edit `worldcup/fly.js` and rebuild. |
| [site/football/worldcup/history.html](site/football/worldcup/history.html) | Year-over-year knockout comparison (F4/F8/F16). Build artifact — do not edit directly. |
| [site/football/worldcup/1998.html](site/football/worldcup/1998.html) | World Cup 1998 page (and one per other year: 2002, 2006, 2010, 2014, 2018, 2022, 2026). Build artifact — do not edit directly. |
| [site/football/worldcup/fly.js](site/football/worldcup/fly.js) | Verbatim copy of `worldcup/fly.js`, loaded by every World Cup page and `history.html` via `<script src>`. Build artifact — do not edit directly; edit `worldcup/fly.js` and rebuild. |
| [site/football/worldcup/flags/](site/football/worldcup/flags/) | Flag SVGs served alongside the World Cup pages. |

## Admin (local-only, not deployed)

The admin site described in `requirements/admin.md` lives in `admin/` — a top-level folder, sibling to `site/`, never nested under it. Unlike `site/`, this is never deployed anywhere: no static host points at it, and it must never be pushed to the public repo (see `technical.md` → *Two-repo structure*). Like `site/`, its pages open directly via `file://` — no server — since `worldcup/scripts/build_admin.py` embeds each page's data at build time, same as the public site. (In the future we'll add an actual backend; see `requirements/admin.md` → *Hosting*.)

| Path | Responsibility |
|------|----------------|
| [admin/2026.html](admin/2026.html) | World Cup 2026 admin page (and one per other year). Build artifact — do not edit directly. |

## Adding a new feature

1. Create a top-level folder for it (e.g. `basketball/`), holding that feature's scripts, data, and shared CSS/JS — mirroring how `worldcup/` is structured.
2. Add a section for it to `requirements/public.md` (and `requirements/admin.md` if it needs data entry). Nav/motion behavior is already covered by `requirements/navigation.md` — reuse it rather than re-describing it, unless the new feature genuinely needs a nav rule that doc doesn't already have.
3. Create its output folder under `site/` (e.g. `site/basketball/`).
4. Add it to `worldcup/scripts/build_home.py`'s nav config (`LEVEL_1`/`LEVEL_2`/`LEVEL_3`) — that's what puts it on the homepage; `site/index.html` is a build artifact, not hand-edited.
5. Update this index.
