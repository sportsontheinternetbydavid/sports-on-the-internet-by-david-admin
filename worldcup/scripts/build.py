#!/usr/bin/env python3
"""Regenerate 2018.html / 2022.html / 2026.html from data/*.json and the
page template defined in this file. Also regenerates the homepage (via
build_home.py) and the admin site's pages (via build_admin.py) at the end,
so every surface's shared nav component and embedded data stay in sync from
a single call — see build_home.py for why the homepage is a build artifact
too, and build_admin.py for why it also embeds rather than serving over
HTTP.

Run this after editing any data/*.json file by hand, or use
worldcup/scripts/set_result.py for a one-line score update.

For tournament files that include a top-level "teamElos" key, homeEloPre and
awayEloPre are derived automatically and written back to the JSON before the
HTML is regenerated.

The three HTML files are pure build artifacts — edit the template here, not
the HTML files directly.
"""
import json
import sys
from pathlib import Path

import build_admin
import build_home
import knockout
import nav

ROOT = Path(__file__).resolve().parent.parent  # worldcup/ — data/, shared.css, shared.js live here
PROJECT_ROOT = ROOT.parent  # repo root — site/ (deployed output) lives here, not under worldcup/
YEARS = [1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026]

# Per-year static configuration: gameset boundaries and the comment that
# describes the tournament format. These are the only parts of the page that
# differ by year beyond the data blocks.
PER_YEAR_CONFIG = {
    1998: {
        'gamesets_comment': '// Gameset boundaries: [label, lastGameNumber]. 32-team format: 3 group-stage matchdays + knockout.',
        'gamesets': [
            ('Initial',  0),
            ('MD1',     16),
            ('MD2',     32),
            ('MD3',     48),
            ('16',      56),
            ('8',       60),
            ('4',       62),
            ('Final',   64),
        ],
    },
    2002: {
        'gamesets_comment': '// Gameset boundaries: [label, lastGameNumber]. 32-team format: 3 group-stage matchdays + knockout.',
        'gamesets': [
            ('Initial',  0),
            ('MD1',     16),
            ('MD2',     32),
            ('MD3',     48),
            ('16',      56),
            ('8',       60),
            ('4',       62),
            ('Final',   64),
        ],
    },
    2006: {
        'gamesets_comment': '// Gameset boundaries: [label, lastGameNumber]. 32-team format: 3 group-stage matchdays + knockout.',
        'gamesets': [
            ('Initial',  0),
            ('MD1',     16),
            ('MD2',     32),
            ('MD3',     48),
            ('16',      56),
            ('8',       60),
            ('4',       62),
            ('Final',   64),
        ],
    },
    2010: {
        'gamesets_comment': '// Gameset boundaries: [label, lastGameNumber]. 32-team format: 3 group-stage matchdays + knockout.',
        'gamesets': [
            ('Initial',  0),
            ('MD1',     16),
            ('MD2',     32),
            ('MD3',     48),
            ('16',      56),
            ('8',       60),
            ('4',       62),
            ('Final',   64),
        ],
    },
    2014: {
        'gamesets_comment': '// Gameset boundaries: [label, lastGameNumber]. 32-team format: 3 group-stage matchdays + knockout.',
        'gamesets': [
            ('Initial',  0),
            ('MD1',     16),
            ('MD2',     32),
            ('MD3',     48),
            ('16',      56),
            ('8',       60),
            ('4',       62),
            ('Final',   64),
        ],
    },
    2018: {
        'gamesets_comment': '// Gameset boundaries: [label, lastGameNumber]. 32-team format: 3 group-stage matchdays + knockout.',
        'gamesets': [
            ('Initial',  0),
            ('MD1',     16),
            ('MD2',     32),
            ('MD3',     48),
            ('16',      56),
            ('8',       60),
            ('4',       62),
            ('Final',   64),
        ],
    },
    2022: {
        'gamesets_comment': '// Gameset boundaries: [label, lastGameNumber]. 32-team format: 3 group-stage matchdays + knockout.',
        'gamesets': [
            ('Initial',  0),
            ('MD1',     16),
            ('MD2',     32),
            ('MD3',     48),
            ('16',      56),
            ('8',       60),
            ('4',       62),
            ('Final',   64),
        ],
    },
    2026: {
        'gamesets_comment': '// Gameset boundaries: [label, lastGameNumber]. lastGameNumber=0 means pre-tournament.',
        'gamesets': [
            ('Initial',  0),
            ('Game 1',  24),
            ('Game 2',  48),
            ('Game 3',  72),
            ('32',      88),
            ('16',      96),
            ('8',      100),
            ('4',      102),
            ('Final',  104),
        ],
    },
}

CONFEDERATIONS = ["Europe", "Asia", "Africa", "South America", "North America", "Oceania"]

# Favicon: distinguishes local-vs-live at a glance across many open browser
# tabs. This site has no admin mode, so there's exactly one signal — ring
# style: dashed = local dev server, solid = live/published. Fill is always
# cream+blue, the same colors used everywhere else on this site.
# window.__setFavicon() runs once at load, deriving isLocal from location.hostname.
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


def load(name):
    return json.load(open(ROOT / "data" / name))


def derive_elos(data):
    """Compute homeEloPre/awayEloPre for all games in-place from teamElos.

    Returns the games list. If data has no teamElos, games are returned
    unchanged (existing homeEloPre/awayEloPre values are preserved).
    """
    if isinstance(data, list) or "teamElos" not in data:
        return data if isinstance(data, list) else data["games"]

    current = dict(data["teamElos"])
    broken = set()  # teams whose ELO chain has hit an unplayed game

    for game in data["games"]:
        home = game["homeTeam"]
        away = game["awayTeam"]

        game["homeEloPre"] = current[home] if home in current and home not in broken else None
        game["awayEloPre"] = current[away] if away in current and away not in broken else None

        if game.get("eloChange") is not None:
            # eloChange sign convention: positive = home gained, negative = away gained.
            delta = game["eloChange"]
            if home in current and home not in broken:
                current[home] += delta
            if away in current and away not in broken:
                current[away] -= delta
        else:
            broken.add(home)
            broken.add(away)

    return data["games"]


def validate(data, year, team_names):
    """Validate a tournament data file. Raises ValueError on the first problem found."""
    if not isinstance(data, dict):
        raise ValueError(f"{year}.json: top-level value must be a JSON object, got {type(data).__name__}")
    if "games" not in data:
        raise ValueError(f"{year}.json: missing required key 'games'")

    games = data["games"]
    if not isinstance(games, list):
        raise ValueError(f"{year}.json: 'games' must be an array")

    knockout_size = data.get("knockoutSize")
    kr = None
    if knockout_size is not None:
        if knockout_size not in knockout.VALID_SIZES:
            raise ValueError(f"{year}.json: 'knockoutSize' must be one of {knockout.VALID_SIZES}, got {knockout_size!r}")
        kr = knockout.rounds_for_size(knockout_size)

    seen_numbers = {}
    for i, g in enumerate(games):
        ctx = f"{year}.json game #{g.get('gameNumber', f'[index {i}]')}"

        # Required fields present
        for field in ("gameNumber", "homeTeam", "awayTeam", "date"):
            if field not in g:
                raise ValueError(f"{ctx}: missing required field '{field}'")

        # gameNumber must be a positive integer
        gn = g["gameNumber"]
        if not isinstance(gn, int) or gn < 1:
            raise ValueError(f"{ctx}: 'gameNumber' must be a positive integer, got {gn!r}")
        if gn in seen_numbers:
            raise ValueError(f"{ctx}: duplicate gameNumber {gn} (first seen at index {seen_numbers[gn]})")
        seen_numbers[gn] = i

        # 'round' identifies a knockout-bracket game (0-based index into this
        # tournament's knockout.rounds_for_size(knockoutSize)). Only bracket
        # games may leave homeTeam/awayTeam null, via homeFrom/awayFrom
        # ({"game": N, "result": "winner"|"loser"}) referencing an earlier
        # game instead of naming a team directly.
        round_idx = g.get("round")
        if round_idx is not None:
            if kr is None:
                raise ValueError(f"{ctx}: has 'round' but tournament has no 'knockoutSize' set")
            if not isinstance(round_idx, int) or not (0 <= round_idx < len(kr)):
                raise ValueError(f"{ctx}: 'round' {round_idx!r} out of range for knockoutSize {knockout_size} (0..{len(kr)-1})")

        # Team names must exist in teams.json, unless this is an unresolved
        # knockout-bracket slot deferring to an earlier game's winner/loser.
        for side, from_key in (("homeTeam", "homeFrom"), ("awayTeam", "awayFrom")):
            name = g.get(side)
            if name is None:
                if round_idx is None:
                    raise ValueError(f"{ctx}: '{side}' is null but game has no 'round' — only knockout-bracket games may leave a team unresolved")
                frm = g.get(from_key)
                if frm is not None:
                    if not isinstance(frm, dict) or set(frm) != {"game", "result"}:
                        raise ValueError(f"{ctx}: '{from_key}' must be an object with exactly 'game' and 'result'")
                    if not isinstance(frm["game"], int):
                        raise ValueError(f"{ctx}: '{from_key}.game' must be an integer gameNumber")
                    if frm["result"] not in ("winner", "loser"):
                        raise ValueError(f"{ctx}: '{from_key}.result' must be 'winner' or 'loser', got {frm['result']!r}")
            elif name not in team_names:
                raise ValueError(f"{ctx}: {side} '{name}' not found in data/teams.json")

        # Scores must be non-negative integers or null
        for side in ("homeScore", "awayScore"):
            v = g.get(side)
            if v is not None and (not isinstance(v, int) or v < 0):
                raise ValueError(f"{ctx}: '{side}' must be a non-negative integer or null, got {v!r}")

        # eloChange must be an integer or null
        ec = g.get("eloChange")
        if ec is not None and not isinstance(ec, int):
            raise ValueError(f"{ctx}: 'eloChange' must be an integer or null, got {ec!r}")

        # eloChange sign must match the score result (fix #8)
        hs = g.get("homeScore")
        as_ = g.get("awayScore")
        if ec is not None and hs is not None and as_ is not None:
            if hs > as_ and ec < 0:
                raise ValueError(
                    f"{ctx}: eloChange={ec} is negative but home team won ({hs}–{as_}). "
                    f"Positive = home gained; negative = away gained."
                )
            if as_ > hs and ec > 0:
                raise ValueError(
                    f"{ctx}: eloChange={ec} is positive but away team won ({as_}–{hs}). "
                    f"Positive = home gained; negative = away gained."
                )

    # gameNumbers must be contiguous from 1
    if seen_numbers:
        actual = sorted(seen_numbers)
        expected = list(range(1, len(actual) + 1))
        if actual != expected:
            missing = sorted(set(expected) - set(actual))
            raise ValueError(f"{year}.json: game numbers are not contiguous from 1; missing: {missing}")

    # homeFrom/awayFrom must reference an earlier, existing game
    for g in games:
        for from_key in ("homeFrom", "awayFrom"):
            frm = g.get(from_key)
            if frm is None:
                continue
            if frm["game"] not in seen_numbers:
                raise ValueError(f"{year}.json game #{g['gameNumber']}: {from_key} references game #{frm['game']} which does not exist")
            if frm["game"] >= g["gameNumber"]:
                raise ValueError(f"{year}.json game #{g['gameNumber']}: {from_key} must reference an earlier game (#{frm['game']} is not before #{g['gameNumber']})")

    # Each knockout round is either fully scaffolded (exact expected game
    # count) or not yet created (0) — catches a partial/corrupted scaffold.
    if kr is not None:
        round_counts = {}
        for g in games:
            r = g.get("round")
            if r is not None:
                round_counts[r] = round_counts.get(r, 0) + 1
        for idx, (label, expected_count) in enumerate(kr):
            actual_count = round_counts.get(idx, 0)
            if actual_count not in (0, expected_count):
                raise ValueError(
                    f"{year}.json: round {idx} ('{label}') has {actual_count} games, expected {expected_count}"
                )


def build_nav(current_year):
    """Utility bar: Home, then a WC-YY item per tournament year plus a
    disabled WC 30 placeholder for the next one — Level 1 of the shared
    nav (see nav.py and ../nav.css), same component the homepage uses
    (build_home.py). This is the first tier of the 3-row nav on tournament
    pages (see page_html) — history.html does not use this; see
    build_history_nav below for why it's standalone instead."""
    items = [('Home', '../../index.html', None)]
    for y in YEARS:
        label = f'WC {str(y)[-2:]}'
        items.append((label, f'{y}.html', 'active' if y == current_year else None))
    items.append(('WC 30', None, 'disabled'))  # placeholder — no 2030 data/page yet

    return nav.render_row(items, 'utility-bar')


def build_history_nav():
    """history.html's Level 1: a single Home chip, not the WC-years utility
    bar — see requirements/public.md -> History page. History compares
    across tournaments rather than switching between them, so it isn't one
    of the tournament pages' Level 1 destinations; it's reached only via
    the homepage's Football -> History link, and this single chip is how
    you navigate back."""
    return nav.render_row([('Home', '../../index.html', None)], 'utility-bar')


def build_history_round_toggle(default='f16'):
    """history.html's Level 2: single-choice Final 4/8/16 round switch — a
    real part of .page-nav now (see requirements/public.md -> History page ->
    Layout), styled like every other page's Level 2 primary tabs rather than
    the old standalone three-checkbox control with its own one-off
    background hack (the fused-red-bar bug that replaced)."""
    rounds = [('f4', 'Final 4'), ('f8', 'Final 8'), ('f16', 'Final 16')]
    buttons = ''.join(
        f'<button id="tab-{key}" class="{"active" if key == default else ""}" '
        f'onclick="setHistRound(\'{key}\')">{label}</button>'
        for key, label in rounds
    )
    return f'<nav class="page-toggle primary-tabs view-toggle">{buttons}</nav>'


def flag_rotation(team_name):
    """Deterministic flag tilt matching the JS flagRotation() function."""
    h = 0
    for ch in team_name:
        h = (h * 31 + ord(ch)) & 0xffff
    return ((h % 21) - 10) * 0.1


def build_history_page(shared_css):
    """Generate the year-over-year knockout round comparison page.

    One row per tournament; which round it shows is a client-side choice
    (Level 2's Final 4/8/16 tabs — see build_history_round_toggle), not three
    stacked rows per tournament like the old version. Each round's ranking:
      F4  — 4 semi-finalists, ELO entering SFs, ranked by ELO
      F8  — all 8 QF entrants, ELO entering QFs, ranked by ELO
      F16 — all 16 R16 entrants, ELO entering R16, ranked by ELO

    All three rounds' row HTML is precomputed here and embedded as a JS
    object (HIST_ROWS), so switching rounds client-side is a tbody.innerHTML
    swap with no server round-trip — see the fly transition in the returned
    <script> block.
    """
    # (r16_range, qf_range, sf_range) — inclusive game-number ranges per year
    ROUND_RANGES = {
        # 32-team format: R16=49-56, QF=57-60, SF=61-62
        1998: (range(49, 57), range(57, 61), range(61, 63)),
        2002: (range(49, 57), range(57, 61), range(61, 63)),
        2006: (range(49, 57), range(57, 61), range(61, 63)),
        2010: (range(49, 57), range(57, 61), range(61, 63)),
        2014: (range(49, 57), range(57, 61), range(61, 63)),
        2018: (range(49, 57), range(57, 61), range(61, 63)),
        2022: (range(49, 57), range(57, 61), range(61, 63)),
        # 48-team format: R16=89-96, QF=97-100, SF=101-102
        2026: (range(89, 97), range(97, 101), range(101, 103)),
    }

    teams_by_name = {t['name']: t for t in load('teams.json')}

    def team_info(name, elo):
        t = teams_by_name.get(name, {})
        return {'name': name, 'flag': t.get('flag', ''), 'elo': elo}

    def round_participants(games_by_num, game_range):
        """Return dict of {team_name: team_info} for all teams in the given games.

        A knockout-bracket game's homeTeam/awayTeam may still be null (not yet
        decided by an earlier round) — such a slot simply contributes no
        participant yet, same as if the game didn't exist.
        """
        result = {}
        for gn in game_range:
            g = games_by_num.get(gn)
            if g is None:
                continue
            if g['homeTeam'] is not None:
                result[g['homeTeam']] = team_info(g['homeTeam'], g.get('homeEloPre'))
            if g['awayTeam'] is not None:
                result[g['awayTeam']] = team_info(g['awayTeam'], g.get('awayEloPre'))
        return result

    year_data = []
    for year in reversed(YEARS):
        data_path = ROOT / 'data' / f'{year}.json'
        if not data_path.exists():
            continue
        data = json.load(open(data_path))
        games = derive_elos(data)
        games_by_num = {g['gameNumber']: g for g in games}

        r16_range, qf_range, sf_range = ROUND_RANGES[year]

        # Participants dict per round: {name: team_info}
        r16 = round_participants(games_by_num, r16_range)
        qf  = round_participants(games_by_num, qf_range)
        sf  = round_participants(games_by_num, sf_range)

        # F4: all 4 SF entrants, ELO entering SFs
        # F8: all 8 QF entrants, ELO entering QFs (includes those who advanced)
        # F16: all 16 R16 entrants, ELO entering R16 (includes those who advanced)
        f4  = sorted(sf.values(),  key=lambda x: x['elo'] or 0, reverse=True)
        f8  = sorted(qf.values(),  key=lambda x: x['elo'] or 0, reverse=True)
        f16 = sorted(r16.values(), key=lambda x: x['elo'] or 0, reverse=True)

        has_sf = bool(sf)
        has_qf = bool(qf)
        has_r16 = bool(r16)

        year_data.append({
            'year': year,
            'f4': f4 if has_sf else None,
            'f8': f8 if has_qf else None,
            'f16': f16 if has_r16 else None,
        })

    page_nav = nav.render_page_nav(build_history_nav(), build_history_round_toggle())

    def flag_cell(team):
        flag = team['flag']
        name = team['name']
        elo = team['elo']
        rot = flag_rotation(name)
        elo_str = str(elo) if elo is not None else '—'
        safe_name = name.replace('"', '&quot;')
        icon = (f'<span class="icon" style="background-image:url(\'flags/{flag}.svg\');'
                f'transform:rotate({rot}deg)" title="{safe_name}"></span>') if flag else name
        return (f'<td class="hist-cell" data-team="{safe_name}">'
                f'<div class="hist-inner">{icon}'
                f'<span class="hist-elo">{elo_str}</span></div></td>')

    def empty_cells(n):
        return ''.join('<td class="hist-cell"></td>' for _ in range(n))

    def pending_cell(colspan, msg='Not yet played'):
        return f'<td colspan="{colspan}" class="hist-pending">{msg}</td>'

    # All rounds render against the same 16 data columns (F4=4 populated,
    # F8=8, F16=16, rest left as trailing empties) so switching rounds never
    # changes the table's width. One row per tournament per round — the
    # year is simply that row's leftmost cell, no conditional visibility
    # logic needed since only one round's row exists in the DOM at a time.
    MAX_COLS = 16

    def round_tbody_html(round_key):
        rows = []
        for yd in year_data:
            participants = yd[round_key]
            rows.append(f'<tr><th class="year-cell">{yd["year"]}</th>')
            if participants:
                rows.append(''.join(flag_cell(t) for t in participants))
                rows.append(empty_cells(MAX_COLS - len(participants)))
            else:
                rows.append(pending_cell(MAX_COLS))
            rows.append('</tr>\n')
        return ''.join(rows)

    round_html = {r: round_tbody_html(r) for r in ('f4', 'f8', 'f16')}

    # 16 uniform data columns
    col_headers = ''.join('<th class="col-data"></th>' for _ in range(MAX_COLS))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>World Cup ELO - History</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Fredoka+One&display=swap" rel="stylesheet">
{FAVICON_SCRIPT}
<style>
{shared_css}
.year-cell {{
  font-family: 'Permanent Marker', cursive;
  font-size: 1.1rem;
  padding: 0.4rem 1rem 0.4rem 0.4rem;
  vertical-align: middle;
  white-space: nowrap;
  border-bottom: 2px solid #C0392B;
}}
.hist-caption {{
  color: #5a4a3a;
  font-style: italic;
  font-family: 'Fredoka One', cursive;
  font-size: 0.85rem;
  margin: 0.6rem 0 1rem;
}}
.hist-cell {{
  text-align: center;
  padding: 0.25rem 0.3rem;
  border-bottom: 2px solid #C0392B;
  vertical-align: middle;
  min-width: 2.6rem;
}}
.hist-inner {{
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}}
.hist-cell .icon {{
  display: block;
  width: 2.2em;
  height: 1.5em;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border: 1px solid #ccc;
  filter: saturate(0.8);
}}
.hist-elo {{
  font-size: 0.68rem;
  color: #555;
  line-height: 1;
}}
.hist-pending {{
  color: #bbb;
  font-style: italic;
  font-size: 0.8rem;
  vertical-align: middle;
  border-bottom: none;
}}
.col-data {{ background: #C0392B; min-width: 2.6rem; }}
thead th {{ border-bottom: none; }}
/* Hover: dim all cells except the hovered team */
table.dimming .hist-cell[data-team] {{ opacity: 0.15; transition: opacity 0.1s; }}
table.dimming .hist-cell.team-highlight {{ opacity: 1; }}
/* Round switch (Level 2 Final 4/8/16) — see requirements/public.md ->
   History page -> Layout. Only one <tbody> instance ever exists (its
   innerHTML is swapped, not stacked copies), because this table is also
   the thing .table-wrap scrolls horizontally when 16 columns don't fit —
   stacking three full-width copies the way build_home.py's homepage
   panels do would fight that scroll area. That also means the swap is
   sequential (old rows fly out, *then* new rows fly in) rather than
   simultaneous — reuses ../nav.css's shared .fly-panel (same universal
   pace and full off-screen distance, see *Navigation* -> *Transitions*),
   paired with .fly-scroll-lock on .table-wrap for the transition's
   duration only (see setHistRound) so flying fully off-screen doesn't
   corrupt the table's own horizontal scroll range at rest. Total
   wall-clock is roughly double a single .fly-panel leg, since out and in
   happen one after the other here instead of simultaneously. */
</style>
</head>
<body>
{page_nav}
<p class="hist-caption">ELO ranking of the teams entering the selected round, highest to lowest, left to right — not a final-standings table.</p>

<div class="table-wrap">
<table id="hist-table">
  <thead>
    <tr>
      <th>Year</th>
      {col_headers}
    </tr>
  </thead>
  <tbody id="hist-tbody">
{round_html['f16']}  </tbody>
</table>
</div>

<script>
var HIST_ROWS = {json.dumps(round_html)};
var __currentHistRound = 'f16';

function attachHistHoverHandlers() {{
  const table = document.getElementById('hist-table');
  const cells = Array.from(table.querySelectorAll('.hist-cell[data-team]'));

  cells.forEach(function(cell) {{
    cell.addEventListener('mouseenter', function() {{
      const team = cell.dataset.team;
      table.classList.add('dimming');
      cells.forEach(function(c) {{
        if (c.dataset.team === team) c.classList.add('team-highlight');
      }});
    }});
    cell.addEventListener('mouseleave', function() {{
      table.classList.remove('dimming');
      cells.forEach(function(c) {{ c.classList.remove('team-highlight'); }});
    }});
  }});
}}

// Read from ../nav.css's --fly-ms (the single source of truth) rather than
// a second hardcoded number that could drift out of sync with it.
const HIST_FLY_MS = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--fly-ms'));

function setHistRound(round) {{
  if (round === __currentHistRound) return;
  ['f4', 'f8', 'f16'].forEach(function(r) {{
    document.getElementById('tab-' + r).classList.toggle('active', r === round);
  }});
  const tbody = document.getElementById('hist-tbody');
  // Flying fully off-screen (see .fly-panel in ../nav.css) would otherwise
  // briefly inflate .table-wrap's own scrollable width — lock it for
  // exactly the transition, not permanently (16 data columns legitimately
  // need their own horizontal scroll at rest).
  const scrollEl = document.querySelector('.table-wrap');
  if (scrollEl) scrollEl.classList.add('fly-scroll-lock');
  tbody.classList.remove('fly-in-active');
  tbody.classList.add('fly-panel', 'fly-out');
  window.setTimeout(function() {{
    tbody.innerHTML = HIST_ROWS[round];
    attachHistHoverHandlers();
    tbody.classList.remove('fly-out');
    tbody.classList.add('fly-in-start');
    void tbody.offsetWidth;
    requestAnimationFrame(function() {{
      tbody.classList.remove('fly-in-start');
      tbody.classList.add('fly-in-active');
      window.setTimeout(function() {{
        tbody.classList.remove('fly-panel', 'fly-in-active');
        if (scrollEl) scrollEl.classList.remove('fly-scroll-lock');
      }}, HIST_FLY_MS);
    }});
  }}, HIST_FLY_MS);
  __currentHistRound = round;
}}

attachHistHoverHandlers();
</script>

</body>
</html>
"""


def format_gamesets_js(gamesets):
    """Format a list of (label, lastGameNumber) pairs as a JS array literal."""
    max_label_len = max(len(label) for label, _ in gamesets)
    lines = ['[']
    for label, last_gn in gamesets:
        padding = ' ' * (max_label_len - len(label))
        lines.append(f"  ['{label}',{padding} {last_gn:3d}],")
    lines[-1] = lines[-1].rstrip(',')  # no trailing comma on last entry
    lines.append(']')
    return '\n'.join(lines)


def build_script_block(year, games_js, teams_js, team_elos_js, config, knockout_size):
    conf_js = json.dumps(CONFEDERATIONS)
    gamesets_comment = config['gamesets_comment']
    gamesets_js = format_gamesets_js(config['gamesets'])

    parts = [
        f'// BEGIN:games{year}',
        games_js,
        f'// END:games{year}',
        '',
        '// BEGIN:teams',
        teams_js,
        '// END:teams',
    ]

    if team_elos_js:
        parts += [
            '',
            f'// BEGIN:teamElos{year}',
            team_elos_js,
            f'// END:teamElos{year}',
            '',
        ]
    else:
        parts.append('')

    parts += [
        f'const GAMES = games{year};',
        f'const YEAR = {year};',
        f'const TEAM_ELOS = teamElos{year};' if team_elos_js else 'const TEAM_ELOS = {};',
        f'const CONFEDERATIONS = {conf_js};',
        gamesets_comment,
        f'const GAMESETS = {gamesets_js};',
        f'const KNOCKOUT_SIZE = {json.dumps(knockout_size)}; // 32/16/8/4, or null if not yet configured',
        "const tbody = document.getElementById('games');",
        "const thead = document.querySelector('#matches-view thead');",
    ]

    return '\n'.join(parts)


def page_html(year, script_block, shared_css, shared_js):
    nav = build_nav(year)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>World Cup ELO - {year}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Fredoka+One&display=swap" rel="stylesheet">
{FAVICON_SCRIPT}
<style>
{shared_css}
</style>
</head>
<body>
<div class="page-nav">
{nav}
  <div class="page-toggle primary-tabs view-toggle">
    <button id="tab-matches" class="active" onclick="setPageView('matches')">Match List</button>
    <button id="tab-groups" onclick="setPageView('groups')">Groups</button>
    <button id="tab-knockout" onclick="setPageView('knockout')">Knockout</button>
    <button id="tab-rankings" onclick="setPageView('rankings')">Rankings</button>
  </div>
  <div id="match-view-toggle" class="match-view-toggle view-toggle"></div>
  <div id="rankings-view-toggle" class="rankings-view-toggle">
    <div class="rankings-checks">
      <label><input type="checkbox" id="chk-show-elim" onchange="toggleShowEliminated()"> Show eliminated</label>
      <label id="true-rank-label" style="opacity:1"><input type="checkbox" id="chk-true-rank" onchange="toggleTrueRank()"> True rank</label>
      <label class="debug-label">
        <input type="checkbox" id="debug-clusters" onchange="renderRankings()"> debug: show binding clusters
      </label>
    </div>
    <div class="rankings-toggle view-toggle">
      <button id="tab-rank" class="active" onclick="setRankView('rank')">Rank</button>
      <button id="tab-scale" onclick="setRankView('scale')">Scale</button>
    </div>
  </div>
  <div id="groups-view-toggle" class="groups-view-toggle view-toggle"><span class="disabled">Group Stage view — coming soon.</span></div>
  <div id="bracket-round-toggle" class="bracket-round-toggle view-toggle"></div>
</div>

<div id="matches-view">
  <div class="table-wrap">
    <table>
      <thead></thead>
      <tbody id="games"></tbody>
    </table>
  </div>
</div>

<div id="rankings-view">
  <div class="rankings-panel">
    <div id="rankings-outer">
      <div class="rankings-cols" id="rankings-cols">
        <div class="rankings-header" id="rankings-header"></div>
        <div class="rankings-body" id="rankings-body"></div>
      </div>
    </div>
  </div>
</div>
<!-- position:fixed, so a sibling of the views rather than nested inside
     #rankings-view — a transform on #rankings-view (see the fly transition
     in shared.js's setPageView) would otherwise create a new containing
     block and permanently re-anchor this to that box instead of the
     viewport once the view had flown in once. -->
<div id="rank-info"></div>

<div id="groups-view"></div>

<div id="knockout-view">
  <div id="knockout-outer"></div>
</div>

<script>
{script_block}
</script>
<script>
{shared_js}
</script>

</body>
</html>
"""


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    # nav.css (the shared Level 1-3 component, also used by build_home.py)
    # is concatenated ahead of shared.css so every page embeds one combined
    # stylesheet, even though the two are separate files for editing.
    shared_css = (ROOT / "nav.css").read_text() + "\n" + (ROOT / "shared.css").read_text()
    shared_js = (ROOT / "shared.js").read_text()

    teams = load("teams.json")
    team_names = {t["name"] for t in teams}
    teams_js = "const teams = [\n" + "\n".join(
        '  {"name": %s, "shorthand": %s, "confederation": %s, "flag": %s},'
        % (json.dumps(t["name"]), json.dumps(t["shorthand"]), json.dumps(t["confederation"]), json.dumps(t["flag"]))
        for t in teams
    ) + "\n];"

    for year in YEARS:
        data_path = ROOT / "data" / f"{year}.json"
        data = json.load(open(data_path))
        try:
            validate(data, year, team_names)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

        games = derive_elos(data)

        if isinstance(data, dict):
            data["games"] = games
            data_path.write_text(json.dumps(data, indent=2) + "\n")

        games_js = f"const games{year} = " + json.dumps(games, indent=2) + ";"

        team_elos_js = None
        if isinstance(data, dict) and "teamElos" in data:
            team_elos_js = f"const teamElos{year} = " + json.dumps(data["teamElos"], separators=(',', ':')) + ";"

        knockout_size = data.get("knockoutSize") if isinstance(data, dict) else None
        config = PER_YEAR_CONFIG[year]
        script_block = build_script_block(year, games_js, teams_js, team_elos_js, config, knockout_size)
        html = page_html(year, script_block, shared_css, shared_js)

        path = PROJECT_ROOT / "site" / "football" / "worldcup" / f"{year}.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        print(f"Updated site/football/worldcup/{year}.html")

    history_html = build_history_page(shared_css)
    history_path = PROJECT_ROOT / "site" / "football" / "worldcup" / "history.html"
    history_path.write_text(history_html)
    print("Updated site/football/worldcup/history.html")

    build_home.main()
    build_admin.main()


if __name__ == "__main__":
    main()
