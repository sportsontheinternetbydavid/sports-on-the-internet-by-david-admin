# Requirements — Admin Site

What the admin site should do/look like. This is a **completely separate site** from the public one (see `requirements-public.md`) — not a mirror of it, not the public site with a toggle flipped. It exists for exactly one job: entering/correcting match results. Nothing here is meant for a visitor to ever see.

**Terminology note**, because "admin" gets used two different ways in this project and they must not be conflated:
- The **private admin repo** (`sportsontheworldwidewebadmin`) is where all source code lives — scripts, data, docs, `shared.js`/`shared.css`, and the templates for *both* sites. This already exists and is unchanged by this doc; see `../way-of-working.md`.
- The **admin site** is a second, separate deployable website described by this doc — a small internal tool for data entry. It is new. It does not exist yet as a build target.

## Status

Implemented. `scripts/build_admin.py` generates one page per year into `../admin/` (e.g. `../admin/2026.html`). The old single-site behavior (a `?admin` URL param / Data Entry toggle bolted onto the public pages) has been retired — see `requirements-public.md`, which describes the public site with all of that removed.

## Hosting

Local-only for now — served the same way the public site is previewed today, via a local HTTP server (e.g. `python3 -m http.server`), never deployed anywhere reachable from outside your machine. Later, this can get its own repo and its own deployment (mirroring the existing public two-repo split described in `../way-of-working.md`), gated by a login. Nothing in this doc should assume a particular future hosting/auth mechanism — the site's behavior shouldn't need to change when that gets added.

Because it is only ever served over HTTP (never opened via `file://`, unlike the public pages), the admin site is **not** bound by the public site's "must embed data as JS constants" constraint (see `requirements-public.md` → this doc's own *Data* section below). It may fetch `data/<year>.json` directly at runtime. This is a meaningful simplification and the intended default, but open to revision.

## Overview

A minimal internal tool, used by one person (you), for entering and correcting World Cup match results — including old, already-played tournaments, since a mistake in historical data needs the same fix path as a live one. It intentionally does not replicate the public site's visualizations (Rankings, Groups, Knockout, confederation shift panel). Those are for exploring the data after it's correct; this tool exists to make it correct in the first place.

## Pages & navigation

- One page per World Cup year (1998–2026), same year set as the public site.
- A simple year switcher at the top to jump between years — no `History`, no `Home`, no link back to the public site. This tool has one purpose; there's nothing else to navigate to.
- No Match List / Rankings / Groups / Knockout tab strip — there is only ever the match list, since that's the only view this site has.
- No brand styling requirement. Legible and fast beats polished — flags are shown plainly for identification, not as the public site's tilted/desaturated "stickers." Construction-paper aesthetic (`../brand.md`) does not apply here.

## Match list

Same underlying game data as the public site's Match List (see `requirements-public.md`), but trimmed to only what's needed to find and correct a game:

- Columns: Date, Game #, Home (flag + team name + score), Away (score + flag + team name).
- No confederation panel, no ELO-shift columns, no W/D/L/Stats views. Nothing here helps you find or fix a result; all of it was cut.
- Every row is clickable, always — there is no mode toggle, no `?admin` param, no distinction between "regular" and "admin" viewing. The whole site is this.

### Row click — data entry panel

Clicking a game row expands an inline panel directly below that row (spanning the full table width). The panel has:

1. The game label (e.g. "#7: Haiti vs Scotland").
2. Home score, away score, ELO magnitude (optional), and — only when both scores are filled in and equal (a draw) — a "Who gains ELO?" selector showing the two team names.
3. A "Generate command" button, a read-only copyable text field showing the resulting `scripts/set_result.py` command, and a "Copy" button. (See *Data → Scripts* below for the command format.)

All inputs are pre-filled with the game's existing values if already set. The "Who gains" selector is pre-selected based on the sign of the existing `eloChange`. Clicking the same row again (or a different row) collapses the open panel. Only one panel is open at a time.

This still only *generates* a command — it does not submit or write anything itself. You still copy it into a terminal and run it, same as before. That hasn't changed; only where this UI lives has.

## Favicon

Same mechanism as the public site (see `requirements-public.md` → *Favicon*), but this site only ever renders the **admin** fill, since there's no non-admin state to distinguish — every page on this site is data entry. The only signal is local vs. live.

| State | Fill | Ring |
|-------|------|------|
| Local | red | dashed |
| Live | red | solid |

Red + white is reused here for the same reason it was reused on the public site: it already means "this can change data" everywhere else this project has used it. "Live" for this site won't be reachable until it has its own deployment (see *Hosting* above), but the favicon logic doesn't need to know that — it already renders correctly the moment this site is served from a non-local host.

---

## Data Sources

ELO ratings and match results come from [eloratings.net](https://www.eloratings.net):

- 2014: https://www.eloratings.net/2014_World_Cup_results
- 2018: https://www.eloratings.net/2018_World_Cup_results
- 2022: https://www.eloratings.net/2022_World_Cup_results
- 2026 (live): https://www.eloratings.net/latest — the dedicated tournament page is created only after the tournament ends

### TSV API

The site's pages are JavaScript-rendered, but the underlying data is served as plain TSV files at the same URL slug with `.tsv` appended:

```
https://www.eloratings.net/<Page_Name>.tsv
```

For example: `https://www.eloratings.net/2014_World_Cup_results.tsv`

This is a machine-readable endpoint — no scraping or browser automation needed. It returns all matches eloratings.net tracks for that page, including friendlies. Filter to rows where column 8 (`Type`) equals `WC` to get World Cup games only.

### TSV column format

16 tab-separated columns, 0-indexed:

| # | Name | Notes |
|---|------|-------|
| 0 | Year | 4-digit year |
| 1 | Month | 1–12 |
| 2 | Day | 1–31 |
| 3 | Team1 | Home team — ISO 3-char code (see team code map below) |
| 4 | Team2 | Away team |
| 5 | Goals1 | Home goals (90+AET only; penalties not counted) |
| 6 | Goals2 | Away goals |
| 7 | Type | `WC` for World Cup, `F` for friendly, etc. |
| 8 | Location | Host country code, or empty if played in home country |
| 9 | EloChange | Signed integer. **Positive = Team1 gained, negative = Team2 gained.** |
| 10 | EloAfter1 | Team1's ELO after this game |
| 11 | EloAfter2 | Team2's ELO after this game |
| 12 | RankChange1 | Team1's world rank change |
| 13 | RankChange2 | Team2's world rank change |
| 14 | RankAfter1 | Team1's world rank after this game |
| 15 | RankAfter2 | Team2's world rank after this game |

The `EloChange` sign convention matches our `eloChange` field exactly: positive means the home team (Team1) gained ELO.

### Deriving pre-tournament ELOs

Each team's `teamElos` entry is derived from their **first appearance** in the filtered WC rows:

- If they appear as **Team1**: `teamElos[team] = EloAfter1 − EloChange`
- If they appear as **Team2**: `teamElos[team] = EloAfter2 + EloChange`

### Penalty shootout treatment

eloratings.net calculates ELO from the 90+AET result only — the shootout winner is irrelevant. A game that ended 0-0 after extra time is treated as a 0-0 draw for ELO purposes regardless of who won on penalties. Consequently:

- `homeScore`/`awayScore` in the JSON store goals only (not penalty kicks).
- `eloChange` for a penalty game is calculated as if it ended at the AET score.
- The build.py sign-check validator accepts this correctly, since a draw allows eloChange in either direction.

### Team code map

The TSV uses 2–3 character ISO codes that don't always match FIFA codes or our team names:

| TSV code | Team name in teams.json |
|----------|------------------------|
| AR | Argentina |
| AU | Australia |
| BA | Bosnia |
| BE | Belgium |
| BR | Brazil |
| CH | Switzerland |
| CI | Ivory Coast |
| CL | Chile |
| CM | Cameroon |
| CO | Colombia |
| CR | Costa Rica |
| DE | Germany |
| DZ | Algeria |
| EC | Ecuador |
| EN | England |
| ES | Spain |
| FR | France |
| GH | Ghana |
| GR | Greece |
| HN | Honduras |
| HR | Croatia |
| IR | Iran |
| IT | Italy |
| JP | Japan |
| KR | South Korea |
| MX | Mexico |
| NG | Nigeria |
| NL | Netherlands |
| PT | Portugal |
| RU | Russia |
| UY | Uruguay |
| US | USA |

### Game ordering and gameset boundaries

The TSV is in chronological order by kick-off time. Near the end of MD1, the schedule sometimes places a MD2 game on the same calendar day as the last MD1 game. When this happens, the TSV interleaves them, breaking the clean 16/32/48 gameset boundaries.

Fix: when a MD2 game appears before the final MD1 game in the TSV, swap their positions so all MD1 games occupy slots 1–16 and MD2 begins at slot 17. This was required for 2014, where Brazil–Mexico (MD2) appeared at TSV row 16 and Russia–South Korea (the last MD1 game) appeared at row 17.

### Checklist: adding a historical World Cup

1. Fetch `https://www.eloratings.net/<Year>_World_Cup_results.tsv`
2. Filter rows to `Type == WC`
3. Derive `teamElos` from each team's first appearance (see above)
4. Map TSV team codes to `teams.json` names (see code map above)
5. Build the `games` array in TSV order, applying any MD boundary swaps
6. Check `data/teams.json` for any teams not yet present; add them with confederation and flag-icons code
7. Download missing flag SVGs from `https://github.com/lipis/flag-icons/tree/main/flags/4x3` into **both** `data/flags/` and `../site/football/worldcup/flags/` — the HTML pages load flags from the latter; `data/flags/` is the source copy kept in sync
8. Add the year to `YEARS` and a matching entry to `PER_YEAR_CONFIG` in `scripts/build.py` (32-team format uses the same gameset structure as 2018/2022)
9. Run `scripts/build.py`

## Data

### Storage & delivery

- Match data is stored in separate data files (one per World Cup, e.g. `data/2018.json`), plus `data/teams.json`. These files are the source of truth.
- The public site's pages open directly via `file://` with no server (per `../way-of-working.md`), so they cannot `fetch` the data files at runtime — each World Cup page embeds the contents of its corresponding data file plus `data/teams.json` as JS constants. The embedded constants must be kept in sync with the data files and are clearly marked (e.g. a comment noting the source file) so it's obvious they are a copy, not hand-edited separately.
- The admin site is always served over HTTP (see *Hosting* above), so it is not bound by this constraint and may fetch `data/<year>.json` directly instead of requiring embedded constants.

### Scripts

Entering the result of a played game is done via a command-line script, not by hand-editing files. The row-click panel in the admin site's match list (see *Row click — data entry panel* above) generates the command for you.

- `scripts/fetch_results.py` is the primary daily-update tool for the live 2026 tournament. It fetches `https://www.eloratings.net/latest.tsv`, finds any WC games in `2026.json` with null scores that now have results, sets `homeScore`/`awayScore`/`eloChange` for all of them, and runs `build.py`. Run it once (or a few times throughout the day) with no arguments. Supports `--dry-run` to preview changes and `--all` to also include future-dated games. The TSV lists teams in eloratings.net order, which may differ from our home/away assignment; the script detects and corrects for this automatically.
- `scripts/update_day.py [--date YYYY-MM-DD] SCORE [SCORE ...]` is a manual fallback for when the TSV hasn't caught up yet. Accepts scores in `HOME-AWAY` format (e.g. `2-1 0-0`) in game-number order for the given date (default: yesterday). Updates scores only — ELO changes must be set separately with `set_result.py`. Use `--list` to preview the day's games without updating. After updating the data and rebuilding the HTML, it commits and pushes the change to the private admin repo, then deploys the rebuilt site to the public GitHub Pages repo (same as running `deploy.py`) — pass `--no-push` to update local files only.
- `scripts/set_team_elo.py YEAR TEAM_SHORTHAND ELO` sets a team's initial ELO in the `teamElos` dict of `data/YEAR.json`, then runs `build.py`. If the data file is a plain list (legacy format), it is automatically upgraded to the `{"teamElos": {}, "games": [...]}` dict format. Use this for 2018 and 2022 data entry before entering game results.
- `scripts/set_result.py YEAR GAME_NUMBER HOME_SCORE AWAY_SCORE [ELO_CHANGE --gains {home|away}]` finds the game with that `gameNumber` in `data/YEAR.json`, sets its `homeScore`/`awayScore` (and `eloChange` if provided), then runs `build.py` to regenerate derived fields and embedded data. Like `update_day.py`, it then commits and pushes the change to the private admin repo and deploys the rebuilt site to the public GitHub Pages repo by default — pass `--no-push` to update local files only.
- When supplying an ELO change, two things are required: the magnitude as a positive number, and which team gains it (`--gains home` or `--gains away`). The script applies the sign and stores the result.
- `scripts/set_result.py --list-teams` prints the index of every team's shorthand, full name, and confederation, sourced from `data/teams.json`.
- `scripts/build.py` computes `homeEloPre`/`awayEloPre` for every game (chaining `teamElos` starting ratings through prior results), then regenerates the embedded data in all three `*.html` pages. Run this after any manual edit to a data file.
- All scripts are plain Python 3 with no dependencies and support `-h` / `--help`.

### Tournament data file structure

Each World Cup data file (`data/2018.json`, `data/2022.json`, `data/2026.json`) is a JSON object with two top-level keys:

- **`teamElos`** — an object mapping each participating team's name to its ELO rating at the start of the tournament. This is the source of truth for pre-tournament ratings; per-game pre-ELOs are derived from this by `build.py`.
- **`games`** — the ordered list of game records (see below).

`homeEloPre`/`awayEloPre` in each game record are **derived fields** computed by `build.py` and written back into the JSON. They must not be hand-edited; they will be overwritten on the next build.

For each team, `build.py` walks games in `gameNumber` order, tracking a running ELO that starts at `teamElos[team]`. For each game the team appears in, `homeEloPre`/`awayEloPre` is set to the running ELO at that point. After the game, if `eloChange` is non-null (game is played), the running ELO is updated. If `eloChange` is null (game not yet played), the chain stops — all subsequent games for that team get `null` pre-ELO, because the outcome of this game isn't known yet.

If a tournament JSON has no `teamElos` key (e.g. 2018, 2022), `build.py` leaves any existing `homeEloPre`/`awayEloPre` values in place and does not attempt to derive them.

### Game records

Each entry in the `games` array:

| Field | Type | Notes |
|-------|------|-------|
| gameNumber | number | 1-based, chronological order within the World Cup. Stable identifier used by `scripts/set_result.py`. |
| homeTeam | string | |
| homeScore | number \| null | `null` if not yet played. |
| awayTeam | string | |
| awayScore | number \| null | `null` if not yet played. |
| date | string (YYYY-MM-DD) \| null | `null` if not yet known. |
| eloChange | number \| null | ELO points transferred from away team to home team (positive = shift toward home team). `null` if not yet known. |
| homeEloPre | number \| null | Derived by `build.py`. Home team's ELO immediately before this game. `null` if the team has no entry in `teamElos`. |
| awayEloPre | number \| null | Derived by `build.py`. Away team's ELO immediately before this game. `null` if the team has no entry in `teamElos`. |

### Teams data

A single shared file `data/teams.json`, used across all World Cups.

| Field | Type | Notes |
|-------|------|-------|
| name | string | Must match team names used in game records |
| shorthand | string | FIFA 3-letter code, e.g. `BEL`. Used as a shorthand identifier in `scripts/set_result.py` |
| confederation | string | One of: Europe, Asia, Africa, South America, North America, Oceania |
| flag | string | [flag-icons](https://github.com/lipis/flag-icons) code for the team's flag (e.g. `be`), used to look up the SVG at `../site/football/worldcup/flags/<flag>.svg` (also kept in `data/flags/`) |

To add a new team: add its row to `data/teams.json` with the appropriate flag-icons code, download the corresponding SVG from the [flag-icons 4x3 flags folder](https://github.com/lipis/flag-icons/tree/main/flags/4x3) into **both** `data/flags/<flag>.svg` and `../site/football/worldcup/flags/<flag>.svg` (the HTML loads flags from the latter; `data/flags/` is kept in sync as the source copy), then run `scripts/build.py`.
