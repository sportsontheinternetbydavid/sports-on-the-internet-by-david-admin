# Requirements — Public Site

What the public-facing "Sports! On the Internet. By David" site should do/look like — the read-only site anyone can visit. This is a strict subset of what the project used to be: it has **no admin mode, no data-entry UI, no `?admin` param, no mode toggle of any kind**. All of that now lives in a completely separate site, documented in `requirements-admin.md`. The two are not mirrors of each other — the admin site is a purpose-built internal tool, not "this site plus a toggle."

See `../00-index.md` for how this doc relates to `requirements-admin.md` and the rest of the project's docs.

## Overview

A tool for soccer fans to follow and compare how different continental confederations perform across FIFA World Cups — who's gaining rating ground, who's losing it, and how each tournament's results play out game by game. It does this by tracking ELO rating transfers between confederations as matches are played, across every World Cup from 1998 through 2026.

Where the underlying ELO/match data comes from, how it's stored, and how it gets entered are not this doc's concern — see `requirements-admin.md` for all of that.

---

## Homepage (`index.html`)

The homepage is the "Sports! On the Internet. By David" landing page. It reflects the brand: kids art room, construction paper and markers, handmade and enthusiastic.

### Layout
- Full-width page with a centered content column (max ~800px).
- Background is cream `#F5F0E8` — like posterboard that everything is stuck to.
- A site header at the top containing the site name and tagline.
- Feature sections below — one per sport category.

### Header
- Site name "Sports! On the Internet. By David" as an `<h1>` in Permanent Marker font — looks like it was written with a thick marker.
- Tagline: "Sports data and visualizations. On the internet." in body font below.
- No top border. The marker-style headline is the visual anchor.

### Feature sections
- Each sport category is a card that looks like a piece of construction paper stuck to the background — slight drop shadow, slightly imperfect border-radius.
- Each card has a section header strip in a construction paper color (one color per section), with the label written in Permanent Marker font.
- Within a sport section, features are grouped by competition type (e.g. "World Cup" under Football). The competition group label uses Permanent Marker font at a smaller size.
- Individual editions (e.g. 2026, 2022, 2018) are listed as links beneath the group label.
- Sport sections with no live features show a "COMING SOON" label styled like a sticky note or cut-paper badge — yellow construction paper color, slight rotation.
- There is no Basketball section.

### Typography
- Headlines and labels: Permanent Marker (Google Fonts) — marker-written feel.
- Body / links: Fredoka One (Google Fonts) — rounded, friendly, legible.
- Links use a construction paper color (dark blue `#1A5276`), bold.

### Colors
- Page background: cream `#F5F0E8`.
- Text: near-black `#1a1a1a`.
- Section header strips: one construction paper color each — Football uses red `#C0392B`, More Sports uses green `#1E8449`.
- "Coming Soon" badge: yellow `#F4D03F`, slight rotation, marker font.
- No clean web-safe primaries. Colors come from the construction paper palette in `../brand.md`.

### Handmade feel
- Cards use `border-radius` with slightly varied values (not perfectly round) to feel hand-cut.
- Cards have a soft drop shadow suggesting physical paper.
- Each section card has a very slight, fixed, unique rotation (±0.5deg or less) — like it was placed carefully but not perfectly.
- No hard pixel-perfect lines. The aesthetic is slightly imperfect, like something stuck to a bulletin board.

---

## World Cup pages (`1998.html`, `2002.html`, `2006.html`, `2010.html`, `2014.html`, `2018.html`, `2022.html`, `2026.html`)

Styling is defined in `shared.css` and inlined at build time. All eight pages share the same visual treatment.

### Typography
- Body font: Fredoka One (Google Fonts), loaded via `<link>` in the page `<head>`.
- There is no page `<h1>` — the nav (see *Navigation* below) is the first thing on the page and is the visual anchor; the current page is identified there, not by a separate heading.
- Links use dark blue `#1A5276`.

### Page background and header
- Page background: cream `#F5F0E8`.
- No top border, no top margin — the nav sits flush against the very top of the viewport.

### Navigation

The page is organized into four stacked **levels** — this is the standard vocabulary for the rest of this doc, and should be used consistently rather than switching between "row," "tier," "bar," etc.:

| Level | What it is | Example |
|-------|------------|---------|
| **Level 1** | Page nav: which page/tournament am I on | `Home`, `History`, `WC 98` … `WC 26`, `WC 30` |
| **Level 2** | Primary tabs: which view am I looking at | `Match List`, `Groups`, `Knockout`, `Rankings` |
| **Level 3** | View detail: controls specific to the active view | `ELO Shift` / `W / D / L` / `Stats`, round-range toggle, `Show eliminated`, etc. |
| **Level 4** | Column headers: labels for the columns/data below | Match List's `Date`/`Home`/`Away`/confederation headers, Rankings' gameset headers, Knockout's round labels |

Levels 1–3 are a single fused component (`<div class="page-nav">`) — every level shares the same red `#C0392B` background and spans the page's full content width (the same max width the rest of the page uses, `body`'s `max-width: 1100px` minus padding — not shrink-to-fit). Levels sit flush against each other with no gap, only a thin `1px solid rgba(0,0,0,0.15)` divider line, so the whole thing reads as one three-level control with rounded corners only on its outer top and bottom edges.

Level 4 is **not** part of `.page-nav` — it belongs to each view's own table/grid, since its exact markup necessarily differs per view (an HTML `<thead>` for Match List, a CSS grid header for Rankings, per-column round labels for Knockout). But it follows the nav's visual language regardless: same red background, white text, Permanent Marker font, fused flush against Level 3 with no gap, and **never wider than the nav above it** — if a view's columns would naturally need more width (e.g. Match List with many confederation columns), the table/grid caps at the nav's width and scrolls horizontally within that bound, rather than the page growing wider than the nav. This keeps Levels 1 through 4 sharing one consistent left/right edge on every view, all the way down to the data.

On tournament pages (`1998.html`–`2026.html`), Levels 1–3 always render, in this order, top to bottom:

1. **Level 1 — Utility bar** (`<nav class="utility-bar view-toggle">`) — a single flat row of equally-spaced segmented items, styled and behaving exactly like the primary tabs (it carries the `.view-toggle` class for that reason), in this order: `Home`, `History`, then one item per World Cup using a short `WC YY` label — `WC 98`, `WC 02`, `WC 06`, `WC 10`, `WC 14`, `WC 18`, `WC 22`, `WC 26`, `WC 30` — last two digits of the year, zero-padded. `WC 30` is a placeholder for the next tournament: there's no `2030.json` data and no `2030.html` page yet, so it renders as a plain disabled item (muted, no hover, not a link) rather than a dead link. The current page is shown the same way the current tab is shown one level down: a white `<strong class="active">` pill, non-linking. There is no Data Entry toggle, no mode switch, and no admin affordance of any kind on this site — see `requirements-admin.md` for where data entry actually happens.
2. **Level 2 — Primary tabs** (`.primary-tabs.view-toggle`) — the segmented Match List / Groups / Knockout / Rankings toggle, in that left-to-right order. This is the single most visually dominant level (larger font/padding than the others), because switching between these views is the main thing a user does.
3. **Level 3 — View detail** — detail controls for whichever of the four views is currently active. Every view has one, even Groups (which just holds a "coming soon" note — see *Group Stage*), so the nav is always the same three-level shape no matter which tab you're on; only one view's Level 3 content is populated/visible at a time, swapped by JS when you switch tabs. See each view's own section for what its Level 3 contains: *Confederation panel* (Match List), *Round toggles* (Knockout Bracket), *Show eliminated* / *True rank* toggles (Tournament ELO Rankings).

Pages without the primary tabs (`history.html`) show only Level 1, styled identically but standalone: all four corners rounded and its own bottom margin, instead of squaring off into a level below. Level 4 still applies there (the F4/F8/F16 table's header row).

#### General nav-bar characteristics (Levels 1–3)

These rules are the shared design system for every red nav level on the site — Level 1, Level 2, every Level 3 variant, and the History page's standalone F4/F8/F16 toggle. Any red nav control should follow all of them unless a specific section says otherwise; they exist precisely so a new nav level can be built by following this list rather than eyeballing an existing one. (Level 4 shares the color/font rules below but not the button-row layout — see *Navigation* above.)

- **Background & width**: red `#C0392B`, spanning the page's full content width (never shrink-to-fit).
- **Layout**: items are laid out in a horizontal row (`flex`) and stretch to evenly fill that full width, using `flex: 1 1 auto` — `auto` (not `0`) so a button's flex-basis is its own label's natural width, meaning growth only distributes *leftover* space and a long label (e.g. "Match List") never wraps to two lines.
- **Font**: Permanent Marker, on every item in every level — buttons and plain links alike. It's all navigation; it should read as one family regardless of the underlying HTML element.
- **Size — two tiers, not one**:
  - Level 2 (primary tabs), the single most important choice on the page: `0.95rem` font, `0.45rem 1.1rem` padding.
  - Every other level (Level 1, and every Level 3 variant): `0.75rem` font, `0.2rem 0.7rem` padding. Smaller and lighter, signaling "secondary to the primary tabs."
- **Height**: Levels 1–3 share one fixed `min-height` (`2.5rem`), always — regardless of which view is active, and regardless of what kind of content a Level 3 variant holds (plain buttons vs. checkboxes, which are natively a different size than text). Content is vertically centered (`align-items: center`) within that height rather than the level growing or shrinking to fit its content. This means Level 2's bigger font (see *Size* above) creates visual dominance without that level being taller — the height is identical everywhere, only the type looks bigger. The one exception is narrow viewports where a level's items wrap to a second line (`flex-wrap: wrap`): `min-height` (not a hard `height`) lets the level grow rather than clip the wrapped line, so this only matters at widths wide enough that nothing wraps.
- **Color — four states, used consistently everywhere red nav appears**:
  1. **Default** (nothing selected/hidden about this item): dimmed white text (`rgba(255,255,255,0.85)`) directly on the red background, brightening to solid white `#fff` on hover.
  2. **Active / current selection** (single-choice controls — which page, which view, which sub-view): a near-white pill (`rgba(255,255,255,0.95)` background) with red text. Means "you are here" — used by the primary tabs, Level 1's current-page item, the Match-view toggle, and the Rank/Scale toggle.
  3. **Shown** (multi-select range controls only — currently just the Knockout round toggle): bold solid white text blended directly into the bar, no pill.
  4. **Hidden** (multi-select range controls only): a pale-red translucent chip (`rgba(255,255,255,0.3)` background over the red bar).

  States 2 and 3 must never both mean "this is turned on" within the same control family — a single-select level (state 2) and a multi-select range level (state 3/4) are visually distinct on purpose, because state 2's white pill already means "current page" one level up; reusing it for "round is shown" would make the same color mean two different things depending which level you're looking at. See *Round toggles* for why the range toggle needs its own states 3/4 instead of reusing 1/2.
- **Dividers & corners**: stacked levels within one fused nav are separated by a `1px solid rgba(0,0,0,0.15)` line; corners are rounded `4px` only on the very top of the first level and the very bottom of the last level — everywhere else is square. A standalone level (not stacked with others) gets all four corners rounded.

### Table
- Page background `#F5F0E8` carries through — tables sit on the cream background.
- Table header row is this page's Level 4 (see *Navigation* above) — same red/white, Permanent Marker treatment as the rest of the nav.
- Row hover: a warm tint `#EDE8DC`.
- All other table layout and column behavior is unchanged.

### Flags
- Each flag icon is treated like a small photograph or sticker stuck flat onto the page.
- Each flag has a very slight, unique, deterministic rotation — derived from the team name so it's consistent across every appearance of that team. Rotation range: approximately ±1 degree.
- No drop shadow on flags — on something that small, a shadow reads as hovering, not pinned. The tilt alone conveys placement.
- Flags are slightly desaturated (`saturate(0.8)`) to feel like a printed sticker, not a crisp digital image.

---

## Match List

### Pages & URLs

- Each World Cup from 1998 through 2026 has its own page with its own URL (`1998.html`, `2002.html`, `2006.html`, `2010.html`, `2014.html`, `2018.html`, `2022.html`, `2026.html`), so it can be linked/bookmarked directly.
- `index.html` is a minimal landing page with a short summary and links to each World Cup's page.
- Each World Cup page has Level 1 (the utility bar) to switch between World Cup pages and back to the landing page — see *Navigation* under *World Cup pages* above for the full nav structure.

### Columns

The table has two groups of columns: **Game columns** and **Confederation columns**.

#### Game columns

- For the selected World Cup, list all games in chronological order.
- The table has a single header row (this is Level 4 — see *Navigation* under *World Cup pages*), full stop — no second header row. Date and # have their own header cells; Home and Away are super-headers spanning their respective columns.
- Column order, left to right:
  1. **Date** — no super-header; displayed in "Mon D" format (e.g. "Jun 2", "Jun 14", "Dec 12"), no year since the year is implied by the selected World Cup.
  2. **Game #** — no super-header; displayed as `#1`, `#2`, etc. The game number is the game's 1-based position in chronological order within that World Cup, stored in the data so it can be used as a stable identifier elsewhere (e.g. data entry).
  3. **[spacer]** — an empty column with no header, providing visual separation between the game identifiers and the Home/Away groups.
  4. **Home** super-header spanning: ELO, Flag, Score.
  5. **[score separator]** — a column displaying a literal `-` for every played game, visually joining the home and away scores (e.g. the row reads "3 - 1"). No super-header.
  6. **Away** super-header spanning: Score, Flag, ELO.
- The ELO column for each team combines pre-game ELO and delta into a single cell displayed as a concatenated string, e.g. `1873+4` or `1938-16`. When `eloChange` is null the cell is empty; when only `homeEloPre`/`awayEloPre` is null the pre-ELO portion is omitted and just the delta is shown.
- Each team is shown as its flag (an SVG image served from `../site/football/worldcup/flags/`, kept in sync with the source copy at `data/flags/`) only (no name), with the team's name shown on hover (e.g. via a tooltip).
- The header row stays fixed/visible at the top of the viewport when scrolling (plain CSS `position: sticky; top: 0` — no JS-measured offset needed, since there's only one row to pin).
- Each column is sized to fit its content — no fixed widths are set. The table never grows wider than the nav above it (Levels 1–3): if the columns need more room than that, the table scrolls horizontally within that width cap rather than pushing the page wider than the nav (see *Navigation* under *World Cup pages*).
- Rows are not clickable and there is no expand panel on this site. Data entry is a completely separate tool — see `requirements-admin.md`.

#### Confederation panel (right side, toggleable)

The right side of the table is a panel of confederation columns that can be toggled between three views: **ELO Shift**, **W / D / L**, and **Stats**. The toggle itself is *not* in the table — it's the Match List view's Level 3 in the fused nav (see *Navigation* under *World Cup pages*), styled like every other Level 3 control: the active view is a near-white pill with red text, the other two are plain white-ish text on the red bar. A left border (`2px solid rgba(255,255,255,0.3)`) on the first confederation header cell is the only visual seam separating the confederation columns from the game columns in the table itself. Switching views must not cause the game columns on the left to shift or resize — the game section width is fixed regardless of which view is active. The transition between views is a simple instant swap (no animation required).

Only confederations with at least one team participating in the selected World Cup get a column in any view (e.g. if Oceania has no teams in the tournament, it has no column in any view). All confederation columns within a view have equal width.

**View 1 — ELO Shift (default)**

- One column per confederation showing its running cumulative ELO delta across games played so far.
- For each game, the home team's confederation gets `+eloChange` and the away team's confederation gets `-eloChange`. If both teams are in the same confederation, the net change is 0.
- Each cell shows the cumulative running total up to and including that row.
- Columns are ordered left-to-right by their final cumulative ELO total (highest first). This same ordering is used for both View 1 and View 2, so column positions do not shift when toggling between those two views.
- Cells are color-coded on a gradient using the brand palette: 0 (neutral) is the page background beige `#F5F0E8`, +400 (max positive) is brand green `#27AE60`, -400 (max negative) is brand red `#C0392B`, interpolated linearly. Values beyond ±400 are clipped to the max color.
- **Color is always driven by the cumulative ELO shift**, regardless of which view is active. When toggling between ELO Shift and W/D/L, the cell background color stays identical — only the displayed text changes. This means a confederation showing a record of "2-3-5" will have the same background color as it had when showing its ELO total, since both reflect the same underlying performance.
- For a game whose `eloChange` is `null`, cells are left empty and the running total does not advance.

**View 2 — W/D/L Record**

- One column per confederation showing its cumulative W/D/L record across games played so far, using the same column order as View 1 (by final cumulative ELO, highest first).
- Each cell displays three numbers in W-D-L order, formatted as e.g. `5-1-2` (wins-draws-losses), representing the running totals up to and including that row. No labels — the W/D/L order is implied by the view name.
- **Sticky note diff highlight**: whichever digit changed from the previous row is overlaid with a small yellow sticky note. The sticky is rendered as an absolutely-positioned square (≈1.05em × 1.05em) centered over the digit, with the same number written on it at the same font size. The underlying digit remains in the normal text flow so spacing is unaffected; the sticky floats on top. Each sticky gets a small random tilt between −5° and +5° to reinforce the physical sticky-note aesthetic. The sticky color is always `#FAD7A0` (warm yellow) — no semantic color distinction between wins, draws, and losses.
- A win for a confederation is any game where a team from that confederation wins (outright, or on penalties). A loss is any game where a team from that confederation loses. A draw is any game that ends level after 90 minutes (regardless of penalty shootout outcome).
- If both teams are from the same confederation, the game counts as both a win and a loss for that confederation (one team won, one lost), or two draws in the case of a draw.
- For a game with `homeScore`/`awayScore` both `null`, the row's cells are empty and the running totals do not advance.

**View 3 — Competition Stats**

- Tournament-wide aggregate stats, not broken out by confederation — a fixed set of summary columns shown for the whole table.
- The total number of columns in View 3 must equal the number of confederation columns in Views 1 and 2, so the right panel stays the same total width across all three views. If there are N confederation columns, use N stat columns (padding with empty columns if N > 3, or merging if N < 3 — but in practice N is typically 5–6 so distribute the stats across N columns or group them sensibly).
- Core stats columns (always present):
  1. **Wins** — running count of decided games (games with a winner after 90 minutes).
  2. **Draws** — running count of drawn games (scores level after 90 minutes).
  3. **Win%** — running ratio of wins to total played games, displayed as a percentage (e.g. `62%`). A played game is any game where both scores are non-null.
- Remaining columns (to fill out to N total) are left blank (empty header, empty cells).
- Values accumulate row by row; unplayed games (`null` scores) leave the row empty and do not advance the totals.

---

## Group Stage

**Status: placeholder.** The tab strip includes a **Groups** tab (`#groups` hash) alongside Match List, Knockout, and Rankings. Its Level 3 (see *Navigation* under *World Cup pages*) holds a single muted, non-interactive note — "Group Stage view — coming soon." — centered in that row; there is no other content and nothing below it in the page body. Level 3 is kept present (not blank/hidden) so the nav is always the same three-level shape no matter which tab is active, and once this view is built out, the note is replaced with its own controls the same way every other view's Level 3 works.

Intended scope (not yet designed in detail): one standings table per group, each team's played/won/drawn/lost/goals-for/goals-against/goal-difference/points, ordered by tournament tiebreak rules, updating as group-stage results are entered.

---

## Knockout Bracket

**Status: implemented.** The **Knockout** tab (`#knockout` hash) renders a bracket-tree visualization of the selected tournament's knockout stage — one column per round, growing gaps between games each round, connected by simple stub lines. Distinct from `history.html`, which compares knockout fields *across* tournaments rather than visualizing a single bracket.

If the tournament has no bracket configured yet (see `requirements-admin.md` → *Knockout Bracket* for how that's set), the tab shows "Knockout bracket not yet configured for this tournament" instead.

### Rounds

The bracket's round sequence is determined by its **size** — the number of teams entering the knockout stage (32/16/8/4), set once per tournament in the admin site. Rounds halve down to the semifinals, followed by a **Final** round holding two games: the third-place playoff and the final (the earlier-numbered of the two is the third-place match).

| Size | Round sequence |
|------|----------------|
| 32 | Round of 32 → Round of 16 → Quarterfinals → Semifinals → Final |
| 16 | Round of 16 → Quarterfinals → Semifinals → Final |
| 8 | Quarterfinals → Semifinals → Final |
| 4 | Semifinals → Final |

Each round's name label above its column is this view's Level 4 (see *Navigation* under *World Cup pages*) — a small red `#C0392B` bar with white text, matching every other view's Level 4 coloring, rather than plain red text directly on the page background.

### Game boxes

Each bracket game shows its date and its two participants, top-to-bottom. A participant is either:
- A resolved team (flag + name), shown with its score once played. If the game is decided by a clear winner (not a draw), the winner is bolded and the loser dimmed — a draw settled on penalties shows neither, since penalty-shootout winners aren't tracked in the data (see `requirements-admin.md`).
- An unresolved slot, shown as italic placeholder text: "Winner of Game N" / "Loser of Game N" if the admin has recorded which earlier game feeds it, or "TBD" if not. "Date TBD" is shown in place of a date if it isn't set yet.

This placeholder behavior also applies to any knockout game appearing in the Match List before it's resolved — the flag cell shows the same placeholder text instead of a broken flag image.

### Round toggles

The Knockout view's Level 3 in the fused nav (see *Navigation* under *World Cup pages*) has one button per round in the tournament's configured sequence (e.g. Round of 32 / Round of 16 / Quarterfinals / Semifinals / Final), labelled with that round's name. All rounds are shown by default.

Unlike the primary tabs, this isn't a single either/or choice, but it isn't fully independent either — the set of shown rounds is always a **contiguous range**, so a round can never be hidden in isolation while its neighbors on both sides stay visible (no gaps in the middle of the tree):

- **Shrinking** removes one round at a time, and only from an end of the current range: clicking the leftmost or rightmost *shown* round hides it and closes that column, so later rounds slide over — there's no blank column left behind.
- **Growing** can jump straight to any *hidden* round in one click: clicking a hidden round reveals it and every round between it and the current range in a single step (e.g. from a range of just "Semifinals", clicking "Round of 32" reveals Round of 32, Round of 16, and Quarterfinals all at once).
- At least one round is always kept visible; clicking the only remaining shown round's button does nothing, since an all-hidden tree would just look broken rather than intentionally empty.
- A shown round that isn't at an edge of the range (so clicking it wouldn't do anything useful) is not clickable, but stays visually identical to the shown rounds that are clickable — see the color convention in *Navigation*, which deliberately keeps "shown" always the same bold/full-red look regardless of clickability, so it's never ambiguous whether a round is currently part of the bracket.

This state isn't persisted anywhere (URL, storage) — it's a browsing convenience that resets on reload, same as the Rankings view's toggles.

---

## Tournament ELO Rankings

A standalone view — only one page view is visible at a time. The World Cup page has a segmented toggle that switches between **Match List**, **Groups**, **Knockout**, and **Rankings**; they never appear simultaneously. Level 1 (links to other years) stays fixed regardless of which view is active. All eight World Cup pages (1998–2026) have the Rankings view, since all have `teamElos` data.

All of this view's own controls — **Show eliminated**, **True rank**, the debug checkbox, and the **Rank**/**Scale** toggle — live together in Level 3 of the fused nav (see *Navigation* under *World Cup pages*), left-aligned in that order, rather than inside the rankings panel itself. The panel below them starts clean.

Each view has its own URL via the hash fragment: `2026.html#matches`, `#rankings`, `#groups`, `#knockout`. Switching views updates the hash; loading the page with a hash pre-selects that view. The default (no hash) is Match List.

### Gamesets

A **gameset** is a batch of games in which each active team plays at most once — it is one "turn" for every team still in the tournament. Gamesets are defined per tournament by a fixed list of game-count boundaries, applied in chronological order. They are not stored in the game data — the boundaries are hardcoded per tournament and applied at render time. A gameset is complete when every team that has a game in its range has a recorded result; teams with no game in the range (already eliminated, or byes) do not count toward completion.

Gamesets are defined per tournament. The boundary for each gameset is `lastGameNumber` — games up to and including that number belong to the gameset.

**1998–2022** (32 teams, 64 games total):

| Gameset | Column label | Description | Game count | Last game # |
|---------|--------------|-------------|------------|-------------|
| 0 | Initial | Pre-tournament (starting `teamElos`) | — | 0 |
| 1 | MD1 | Group stage, matchday 1 | 16 | 16 |
| 2 | MD2 | Group stage, matchday 2 | 16 | 32 |
| 3 | MD3 | Group stage, matchday 3 | 16 | 48 |
| 4 | 16 | Round of 16 | 8 | 56 |
| 5 | 8 | Quarterfinals | 4 | 60 |
| 6 | 4 | Semifinals | 2 | 62 |
| 7 | Final | Third-place game + Final | 2 | 64 |

All 8 gameset columns are always shown for 1998–2022.

**2026** (48 teams, 104 games total):

| Gameset | Column label | Description | Game count | Last game # |
|---------|--------------|-------------|------------|-------------|
| 0 | Initial | Pre-tournament (starting `teamElos`) | — | 0 |
| 1 | Game 1 | Group stage, matchday 1 | 24 | 24 |
| 2 | Game 2 | Group stage, matchday 2 | 24 | 48 |
| 3 | Game 3 | Group stage, matchday 3 | 24 | 72 |
| 4 | 32 | Round of 32 | 16 | 88 |
| 5 | 16 | Round of 16 | 8 | 96 |
| 6 | 8 | Quarterfinals | 4 | 100 |
| 7 | 4 | Semifinals | 2 | 102 |
| 8 | Final | Third-place game + Final | 2 | 104 |

All 9 gameset columns are always shown for 2026. The Rankings view has a segmented toggle that switches between **Rank** and **Scale** views of the same gameset data — part of the Level 3 controls described above. Switching between Rank and Scale must not shift the gameset column positions — the horizontal layout is identical in both views.

### Ranking and ties

Teams are ranked by ELO descending within each gameset snapshot. Ties are broken by **stable sort**: if two teams have equal ELO, the one ranked higher in the previous snapshot remains ranked higher.

### Live gameset

At any point in the tournament there is exactly one **live gameset column**: the in-progress gameset if any games in its range have been played but it is not yet complete, or the next gameset if the most recent gameset just completed and the next hasn't started.

The live gameset column is always shown populated — it is never empty:

- It is seeded from the previous gameset's final ELOs (or from `teamElos` if it is the first gameset).
- As results come in, the column updates: each team's ELO and rank reflects all results recorded so far within the live gameset.
- Teams are always ranked by their current ELO, including mid-gameset. There is no hold on unplayed teams — the live standings shift with every result entered.

Teams that have a game scheduled in the live gameset's range but no result recorded yet are shown with a **"hasn't played" visual**: a muted grey distinct from the greyscale used for eliminated teams. Once their game result is entered, they revert to normal styling.

Only the live gameset column uses this treatment. Completed gameset columns always show final ELOs with no "hasn't played" styling. Future gameset columns (beyond the live one) show nothing.

### Eliminated teams

A team is considered **eliminated** as of the gameset after their last appearance in a game. Specifically: if a team played in gameset N but does not appear in any game in gameset N+1 or later, they are eliminated after gameset N. (For the group stage this naturally captures teams that don't qualify for the Round of 32; for knockout rounds it captures teams that lost.)

Eliminated teams are hidden by default in knockout columns (see *Show eliminated toggle* below). When shown, their flag is rendered in greyscale to visually distinguish them from active teams.

### Show eliminated toggle

A toggle labelled **"Show eliminated"** is available in both the Rank view and the Scale view. By default (off), eliminated teams are hidden in knockout columns. When on, all teams are always shown.

- **Group stage columns** (gamesets covering MD1–MD3): all teams are always shown regardless of this toggle, since every team participates in the group stage.
- **Knockout round columns** (gamesets from Round of 32 onward): when the toggle is off (default), eliminated teams' flags are hidden in any column where they are not participating. A team is considered eliminated for a given column if they have no game in that gameset and no game in any later gameset.
- **Layout is unchanged**: the column structure, ELO axis, column widths, and spacing are identical regardless of the toggle state. Only the flag elements are hidden — no reflow, no gaps closing.

### True rank toggle (Rank view only)

A toggle labelled **"True rank"** is available in the Rank view only. It is not shown at all in the Scale view, since the concept doesn't apply there.

- **Off (default)**: surviving teams are re-numbered starting from 1 in ELO order, and their flags are packed to fill the gaps.
- **On**: surviving teams keep their original rank numbers. A surviving team ranked #5 still appears at rank slot #5; slots for hidden eliminated teams appear empty.

Checking **"Show eliminated"** automatically checks "True rank" as well, since showing all teams in their packed positions would be misleading — the true rank slots are needed to make the eliminated flags readable. The user can uncheck "True rank" independently after.

### Rankings shared layout

Both Rank and Scale views share the same canvas structure: one vertical column per gameset, all columns equal width, with a leftmost axis column. Toggling between views causes no horizontal shift.

- *Flag dimensions*: each flag icon has a fixed pixel width and height, consistent across both views.
- *Column width*: every gameset column has a fixed minimum width of `3 × flag_width + 2 × gap` (where *gap* is a fixed small spacing between side-by-side flags, defined in the Scale view). This applies uniformly across both views. Column separator lines are always fully visible; no flag extends past its column boundary. (The `3 ×` derives from the Scale view cluster constraint — see `scale-algorithm.md`.)
- *Header row*: the row of gameset labels (Initial / MD1 / MD2 / … or Initial / Game 1 / … for 2026) is this view's Level 4 (see *Navigation* under *World Cup pages*) — red `#C0392B` background, white text, matching every other view's Level 4, fused flush against Level 3 above it with no gap.

---

### Flag info panel

Hovering any flag in the Rankings view populates a fixed side panel that sits to the left of the rankings grid, vertically centered on the viewport. The panel never overlaps the grid or its flags.

The panel always shows the same set of fields in the same order, so its height never changes while browsing:

| Field | Content |
|-------|---------|
| Flag | The team's flag image (large) |
| Name | Team name (bold) |
| ELO | ELO at that gameset snapshot |
| *(divider)* | |
| Date | Game date in "Mon D" format (e.g. "Jun 15"), or — if no game |
| Opponent | Opposing team name, or — |
| Score | Score from the hovered team's perspective (their goals first), or — |
| ELO Δ | ELO change, green for gain, red for loss, or — |

When there is no game in the column (Initial snapshot, or a team with no game scheduled in that gameset), the bottom four fields show —. For a pending game (live column, result not yet entered), Date and Opponent are shown but Score and ELO Δ show —.

**Behaviour:**
- The panel appears immediately when the cursor first lands on a flag.
- Moving between flags updates the panel content instantly with no flicker — the panel stays visible throughout.
- The panel hides 300 ms after the cursor leaves the rankings area entirely (same grace period as the highlight).

---

### Flag hover highlight

When the user hovers over any flag in the Rankings view, all flags belonging to **other** teams are dimmed (reduced opacity). The hovered team's flags across all gameset columns remain at full opacity, making it easy to trace a single team's ELO evolution across the tournament. The hovered team's flags are also brought to the front (highest z-index) so they are never obscured by overlapping flags.

The highlight uses debounced activation and deactivation to avoid flicker:
- **Activate delay (200 ms):** the highlight only appears after the cursor has rested on a flag for 200 ms. Brief passes don't trigger it.
- **Deactivate grace period (300 ms):** when the cursor moves to empty space or leaves the rankings area, the highlight holds for 300 ms before clearing. This prevents flicker when crossing flag edges.
- **Instant cancel:** if the cursor returns to the already-highlighted team's flag during the grace period, the deactivation is cancelled immediately with no re-delay.

### Result badge

While a team is highlighted, each of its flags across all gameset columns shows a small badge in its bottom-right corner: a single-letter result (**W** / **L** / **D**, green/red/gray) plus a miniature flag of that round's opponent. The badge is only visible on the highlighted team's flags — it is not shown by default, keeping the grid uncluttered when nothing is hovered.

- The result is derived from the score of the team's game in that gameset column (win/loss/draw from the hovered team's perspective). This is independent of the ELO Δ shown in the side panel — a team can win a game and still be shown losing ELO, or vice versa.
- No badge is shown when there is no game in that column (Initial snapshot, or no game scheduled that gameset) or when the game is pending (live column, result not yet entered).
- A draw settled on penalties still shows **D** — same caveat as the Knockout Bracket view, penalty-shootout winners aren't tracked in the data (see *Game boxes* in *Knockout Bracket*).

---

### Rank view

Flags are **evenly spaced** — each rank position occupies the same vertical height regardless of ELO magnitude. This is a positional ranking, not a proportional one.

Each flag occupies its rank slot for that gameset snapshot: rank 1 at the top, rank N at the bottom. A leftmost axis column shows rank numbers (1, 2, 3…) aligned to each rank slot. No ELO number is shown alongside the flag. Hovering a flag shows the info panel — see *Flag info panel* above.

A dotted horizontal line is drawn between every 4th and 5th rank (i.e. after ranks 4, 8, 12, …), spanning all columns, behind the flags.

---

### Scale view

Flags are **positioned proportionally to ELO** — a team's vertical position on the axis directly encodes its ELO value. Y position is never altered for any reason. The gameset column X-positions are identical to Rank view so toggling between the two causes no horizontal shift.

**Definitions (Scale view)**
- *Gap*: a fixed small spacing (a few pixels) between flags placed side by side.
- *Depth*: at any vertical point on the axis, the number of flags whose pixel intervals simultaneously cover that point. Two flags overlap when their top-to-top pixel distance is less than one flag height.

**Axis range**
The ELO axis spans from the lowest to the highest ELO of any team across all populated gameset snapshots. A flag's **top edge** sits at its ELO pixel position — not the center. This means a team rated 1998 reads as "just below 2000," matching the natural interpretation that a flag hangs down from its rating. Centering would make the team appear to straddle the line above, which is misleading.

A fixed pixel margin of `RANK_ROW_H / 2` is applied at the top and at the bottom (below the lowest flag's bottom edge), keeping the extreme flags inset from the axis ends symmetrically.

Note: the Scale view's vertical positioning is **independent of the Rank view** — only the horizontal column layout is shared. The Rank view spaces flags evenly by rank; the Scale view spaces them proportionally by ELO. Toggling between views changes flag vertical positions but not column positions.

**Axis height**
No visual overlap between flags is allowed. The axis height is the **minimum height at which the maximum depth across all gameset columns is ≤ 3** — ensuring every point on the axis is covered by at most 3 flags, which is the column's horizontal dodge capacity. A single height is computed across all gameset columns together so all columns share the same vertical scale and remain aligned. See `scale-algorithm.md` for the constraints, algorithm, and implementation.

Error case: if 4 or more teams share an identical ELO in the same gameset column, no axis height can resolve the cluster. A visible warning is shown in that column and the smallest achievable height is used.

**Y-axis tick marks**
The tick interval (ELO units between marks) is selected from `[200, 100, 50, 25, 10, 5, 2]`, largest first, choosing the first value whose pixel spacing falls between 150 px and 300 px. If no candidate falls in that range (e.g. the axis is extremely compressed or stretched), the candidate whose spacing is closest to 200 px is used as a fallback. Tick labels are shown at every multiple of the chosen interval within the axis range, once in the leftmost axis column. A dotted horizontal line is drawn at each tick, spanning all columns, behind the flags.

**Horizontal dodge**
Overlapping flags are fanned out into up to 3 horizontal lanes; Y positions are never altered. Isolated flags are centered; pairs are symmetric; full 3-flag clusters span left-centre-right. See `scale-algorithm.md` for the full algorithm.

**Flag display**
No ELO number is shown alongside the flag. Hovering a flag shows the info panel — see *Flag info panel* above. Z-index is determined by rank: higher-ranked teams (lower rank number) render on top.

---

## History page (`history.html`)

A year-over-year comparison of the knockout-round field across all tournaments (1998–2026). Generated by `build.py` alongside the per-year pages. Linked from the nav on every World Cup page and from the homepage.

### Layout

- Same visual treatment as the per-year pages: cream background, Permanent Marker headings, red construction-paper table header.
- The same Level 1 described in *Navigation* under *World Cup pages*, with `History` shown as the current-page item. This page has no Level 2 or Level 3, so Level 1 is standalone (all four corners rounded) rather than fused into a taller nav.
- Below that, three toggle buttons (F4 / F8 / F16) let the user show or hide each row tier. All three are on by default. Each button uses the existing `.view-toggle` style; active = highlighted, inactive = dim. This toggle is *not* part of the fused nav — it's this page's own standalone control, the same way it's always been.
- A single wide table below the toggles. The year column is on the left; 16 data columns fill the rest.

### Table structure

For each tournament, three rows are rendered as a visual group separated by red borders:

| Row | Teams shown | ELO snapshot |
|-----|-------------|--------------|
| F4 | 4 semi-finalists | ELO entering the semi-finals |
| F8 | All 8 QF entrants (includes F4 teams) | ELO entering the quarter-finals |
| F16 | All 16 R16 entrants (includes F8 teams) | ELO entering the round of 16 |

- Within each row, teams are sorted highest ELO → lowest, left to right.
- All three rows start at column 1 (no staggered offsets).
- 2026 shows "Not yet played" for rounds not yet reached.

### Year label

- The year label appears in the leftmost cell of the topmost *visible* row for each tournament group. This is handled entirely in CSS:
  - Default: year shown in F4 row, hidden in F8 and F16 rows.
  - If F4 is hidden: year shown in F8 row.
  - If F4 and F8 are hidden: year shown in F16 row.
- This means the year is never missing regardless of which row tiers are toggled off.

### Cells

- Each cell shows a flag icon (same style as per-year pages: slight deterministic tilt, desaturated) with the ELO number directly below it — no country name.
- Hovering a flag dims all cells from other countries across the entire table, highlighting every appearance of that country.

### Game number ranges used to identify rounds

| Format | R16 | QF | SF |
|--------|-----|----|----|
| 32-team (1998–2022) | games 49–56 | games 57–60 | games 61–62 |
| 48-team (2026) | games 89–96 | games 97–100 | games 101–102 |

Loser detection uses set subtraction (teams in round N who do not appear in round N+1), not score/eloChange parsing — this correctly handles penalty-shootout results.

---

## Favicon

**Why this exists:** many tabs are open at once during normal use, and it has to be obvious at a glance whether a given tab is pointed at your local machine or the live published site — e.g. so a local-only layout experiment is never mistaken for what visitors actually see.

Since this site has no admin mode at all, there is exactly one signal: **local vs. live → ring style.** Dashed ring = local dev server (`localhost` / `127.0.0.1` / `file://`). Solid ring = live/published. The fill is always cream background + dark blue icon — the same colors used everywhere else on this site (`#F5F0E8` / `#1A5276`); there is no red/admin variant here. (The admin site has its own, separate favicon scheme — see `requirements-admin.md`.)

**The two states:**

| State | Fill | Ring |
|-------|------|------|
| Local | cream | dashed |
| Live | cream | solid |

**Implementation:** the icon is not a static image file. It's a small inline SVG (a circle + a pentagon, evoking a soccer ball) built as a data URI at load time by `window.__setFavicon()`, deriving `isLocal` once from `location.hostname`. The function is duplicated in two places rather than shared, because it must run before any page-specific data exists: `worldcup/scripts/build.py`'s `FAVICON_SCRIPT` constant (reused for `history.html` and every year page) and a hand-copied version in `../site/index.html`, since the homepage is hand-authored and not a build artifact.

---

## Debug

Debug features are toggled via UI controls that are always visible but clearly labelled as debug. They are off by default and have no effect on normal rendering. In the nav, a debug control's label uses a dedicated warning pink (`#ffb3b3`) instead of any of the four color states described in *Navigation* — it isn't "shown/hidden" or "selected," it's a distinct "developer control, be careful" signal, so it deliberately doesn't borrow meaning from the other states.

**Show binding clusters** (Scale view only) — a checkbox labelled "debug: show binding clusters". When checked, a red outline is drawn around each depth-4 window that would appear if the axis were 1 pixel shorter — i.e. each set of flags whose vertical intervals would all overlap a common point at `scaleH − 1`. These are the flags forcing the axis to be as tall as it is: at the computed minimum height their depth is ≤ 3, but one pixel shorter it would reach 4 and overflow the column. Off by default.
