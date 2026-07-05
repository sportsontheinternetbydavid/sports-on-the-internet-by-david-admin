#!/usr/bin/env python3
"""Regenerate the admin site's per-year pages in admin/.

Same embedding pattern as build.py: each admin page embeds its tournament's
games (and the shared teams list) as JS constants at build time, so the
page opens directly via file:// with no server and no runtime fetch — just
like the public pages. build.py calls this automatically after every data
change, so the embedded copy stays in sync; run this script directly only
if you've changed the admin page template itself without touching data.

The admin site is local-only (see requirements/admin.md) — it has
no deployment target and must never be pushed to the public repo.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # worldcup/
PROJECT_ROOT = ROOT.parent  # repo root — admin/ output lives here, not under worldcup/
YEARS = [1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026]

# Favicon: this site is 100% admin, so unlike the public site's favicon there's
# no non-admin state to distinguish — the fill is always the admin red/white.
# The only signal is local vs. live, same mechanism as the public site.
FAVICON_SCRIPT = """<script>
(function() {
  function faviconHref(isLocal) {
    var dash = isLocal ? ' stroke-dasharray="3 2.5"' : '';
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
      + '<circle cx="16" cy="16" r="14" fill="#C0392B" stroke="#FFFFFF" stroke-width="2.5"' + dash + '/>'
      + '<path d="M16,10 L21.7,14.2 L19.5,20.9 L12.5,20.9 L10.3,14.2 Z" fill="#FFFFFF"/>'
      + '</svg>';
    return 'data:image/svg+xml,' + encodeURIComponent(svg);
  }
  window.__setFavicon = function() {
    var isLocal = ['localhost', '127.0.0.1', ''].indexOf(location.hostname) !== -1;
    var link = document.createElement('link');
    link.rel = 'icon';
    link.type = 'image/svg+xml';
    link.href = faviconHref(isLocal);
    document.head.appendChild(link);
  };
  window.__setFavicon();
})();
</script>"""

ADMIN_CSS = """
* { box-sizing: border-box; }
html { color-scheme: light; }
body { font-family: system-ui, sans-serif; font-size: 0.95rem; margin: 0 auto; max-width: 900px; padding: 1.5rem 1.5rem 4rem; color: #1a1a1a; background: #fff; }
h1 { font-size: 1.3rem; margin: 0.5rem 0 1rem; }
nav { margin-bottom: 1rem; font-size: 0.85rem; }
nav a { margin-right: 0.6rem; color: #1A5276; }
nav strong { margin-right: 0.6rem; }
table { border-collapse: collapse; width: 100%; }
th, td { padding: 0.4rem 0.6rem; text-align: left; border-bottom: 1px solid #ddd; }
th { background: #eee; }
tbody tr { cursor: pointer; }
tbody tr:hover { background: #f5f5f5; }
.flag-cell { display: flex; align-items: center; gap: 0.4rem; }
.flag-cell .icon { display: inline-block; width: 1.6em; height: 1.1em; background-size: cover; background-position: center; background-repeat: no-repeat; border: 1px solid #ccc; }
.score { width: 2.5em; text-align: center; }
.expand-row td { background: #f4f8ff; cursor: default; padding: 0.6rem 0.8rem; }
.ur-line { display: flex; gap: 0.8rem; align-items: center; flex-wrap: wrap; margin: 0.35rem 0; }
.ur-line label { display: flex; align-items: center; gap: 0.3rem; white-space: nowrap; }
.ur-line input[type=number] { width: 4.5rem; padding: 0.2rem; }
.ur-cmd { font-family: monospace; flex: 1; min-width: 16rem; padding: 0.3rem; }
h2 { font-size: 1.05rem; margin: 2rem 0 0.6rem; }
.tab-strip { display: flex; gap: 0.4rem; margin-bottom: 1rem; }
.tab-strip button { padding: 0.35rem 0.9rem; cursor: pointer; border: 1px solid #ccc; background: #f2f2f2; }
.tab-strip button.active { background: #333; color: #fff; border-color: #333; }
#groups-view, #knockout-view { display: none; }
.br-size-picker { display: flex; gap: 0.5rem; align-items: center; margin-bottom: 1rem; }
.br-size-picker button { padding: 0.3rem 0.8rem; cursor: pointer; }
.br-slot { display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap; }
.br-slot select, .br-slot input[type=text], .br-slot input[type=number] { padding: 0.2rem; }
.br-slot input[type=text] { width: 5.5rem; }
.br-slot input[type=number] { width: 4rem; }
.ab-wrap { display: flex; align-items: stretch; gap: 2rem; overflow-x: auto; padding: 0.5rem 0 1rem; }
.ab-round { display: flex; flex-direction: column; min-width: 170px; }
.ab-round-label { font-weight: bold; text-align: center; margin-bottom: 0.5rem; color: #333; }
.ab-round-games { flex: 1; display: flex; flex-direction: column; justify-content: space-around; }
.ab-round:not(:first-child) .ab-game-wrap { position: relative; }
.ab-round:not(:first-child) .ab-game-wrap::before { content: ''; position: absolute; left: -1rem; top: 50%; width: 1rem; height: 0; border-top: 1px solid #999; }
.ab-game-wrap { padding: 0.3rem 0; }
.ab-game { border: 1px solid #ccc; border-radius: 4px; background: #fff; font-size: 0.82rem; cursor: pointer; overflow: hidden; }
.ab-game:hover { border-color: #888; }
.ab-game.selected { border-color: #333; box-shadow: 0 0 0 1px #333; }
.ab-sub { font-size: 0.68rem; color: #888; text-align: center; padding: 0.15rem 0.3rem 0; }
.ab-date { font-size: 0.68rem; color: #888; text-align: center; padding: 0.2rem 0.3rem; border-bottom: 1px solid #eee; }
.ab-team { display: flex; align-items: center; gap: 0.35rem; padding: 0.3rem 0.5rem; }
.ab-team + .ab-team { border-top: 1px solid #eee; }
.ab-team .icon { display: inline-block; width: 1.4em; height: 1em; flex: none; background-size: cover; background-position: center; background-repeat: no-repeat; border: 1px solid #ccc; }
.ab-team-name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ab-team.winner { font-weight: bold; }
.ab-team.loser { opacity: 0.55; }
.ab-score { font-weight: bold; }
.ab-team.loser .ab-score { font-weight: normal; }
.ab-tbd { color: #999; font-style: italic; font-size: 0.72rem; }
#bracket-edit-panel:not(:empty) { border: 1px solid #ccc; border-radius: 4px; padding: 0.6rem 0.8rem; background: #f4f8ff; margin-top: 0.5rem; }
"""


def build_admin_page(year, data, teams):
    parts = []
    for y in YEARS:
        parts.append(f'<strong>{y}</strong>' if y == year else f'<a href="{y}.html">{y}</a>')
    nav = '<nav>' + ''.join(parts) + '</nav>'

    data_js = json.dumps(data, indent=2)
    teams_js = json.dumps(teams, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admin — World Cup {year}</title>
{FAVICON_SCRIPT}
<style>{ADMIN_CSS}</style>
</head>
<body>
{nav}
<h1>World Cup {year} — Admin</h1>

<div class="tab-strip">
  <button id="tab-matches" class="active" onclick="setView('matches')">Match List</button>
  <button id="tab-groups" onclick="setView('groups')">Groups</button>
  <button id="tab-knockout" onclick="setView('knockout')">Knockout</button>
</div>

<div id="matches-view">
<table>
  <thead><tr><th>Date</th><th>#</th><th>Home</th><th>Away</th></tr></thead>
  <tbody id="games"></tbody>
</table>
</div>

<div id="groups-view">
<p style="opacity:0.6; font-style:italic;">Group Stage — coming soon.</p>
</div>

<div id="knockout-view">
<div id="knockout-admin"></div>
</div>

<script>
const YEAR = {year};
// BEGIN:data{year} — embedded from worldcup/data/{year}.json, kept in sync by build.py
const DATA = {data_js};
// END:data{year}
// BEGIN:teams — embedded from worldcup/data/teams.json, kept in sync by build.py
const teams = {teams_js};
// END:teams

function esc(s) {{
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}}

function flagIcon(flag, name) {{
  return flag
    ? `<span class="icon" style="background-image:url('../site/football/worldcup/flags/${{flag}}.svg')" title="${{esc(name)}}"></span>`
    : '';
}}

// A knockout-bracket game may not have a concrete team yet — it defers to
// an earlier game's winner/loser via homeFrom/awayFrom (see set_bracket_game.py).
function feedLabel(from) {{
  if (!from) return 'TBD';
  return `${{from.result === 'loser' ? 'Loser' : 'Winner'}} of Game ${{from.game}}`;
}}

function teamCellHtml(game, side, flagByTeam) {{
  const team = game[side + 'Team'];
  if (!team) return `<em style="color:#888">${{esc(feedLabel(game[side + 'From']))}}</em>`;
  return `${{flagIcon(flagByTeam[team], team)}}${{esc(team)}}`;
}}

let expandRow = null;
let expandGameNumber = null;

function toggleExpand(game, tr, flagByTeam) {{
  if (expandRow) {{
    expandRow.remove();
    expandRow = null;
    if (expandGameNumber === game.gameNumber) {{ expandGameNumber = null; return; }}
  }}
  expandGameNumber = game.gameNumber;

  const hsVal = game.homeScore != null ? game.homeScore : '';
  const asVal = game.awayScore != null ? game.awayScore : '';
  const eloVal = game.eloChange != null ? Math.abs(game.eloChange) : '';
  const gainsVal = game.eloChange != null ? (game.eloChange >= 0 ? 'home' : 'away') : '';
  const isDraw = hsVal !== '' && asVal !== '' && hsVal === asVal;

  const expandTr = document.createElement('tr');
  expandTr.className = 'expand-row';
  const td = document.createElement('td');
  td.colSpan = 4;
  td.innerHTML = `
    <div class="ur-line"><strong>#${{game.gameNumber}}: ${{esc(game.homeTeam)}} vs ${{esc(game.awayTeam)}}</strong></div>
    <div class="ur-line">
      <label>Home score: <input class="ur-hs score" type="number" min="0" value="${{hsVal}}"></label>
      <label>Away score: <input class="ur-as score" type="number" min="0" value="${{asVal}}"></label>
      <label>ELO magnitude (opt): <input class="ur-elo" type="number" min="0" value="${{eloVal}}"></label>
      <label class="ur-gains-wrap" style="display:${{isDraw ? 'flex' : 'none'}}">Who gains ELO:
        <select class="ur-gains">
          <option value="" ${{gainsVal === '' ? 'selected' : ''}}>—</option>
          <option value="home" ${{gainsVal === 'home' ? 'selected' : ''}}>${{esc(game.homeTeam)}}</option>
          <option value="away" ${{gainsVal === 'away' ? 'selected' : ''}}>${{esc(game.awayTeam)}}</option>
        </select>
      </label>
    </div>
    <div class="ur-line">
      <button class="ur-gen">Generate command</button>
      <input class="ur-cmd" type="text" readonly placeholder="command will appear here">
      <button class="ur-copy">Copy</button>
    </div>`;

  td.addEventListener('click', e => e.stopPropagation());

  function updateGainsVisibility() {{
    const hs = td.querySelector('.ur-hs').value;
    const as_ = td.querySelector('.ur-as').value;
    const draw = hs !== '' && as_ !== '' && hs === as_;
    td.querySelector('.ur-gains-wrap').style.display = draw ? 'flex' : 'none';
  }}
  td.querySelector('.ur-hs').addEventListener('input', updateGainsVisibility);
  td.querySelector('.ur-as').addEventListener('input', updateGainsVisibility);

  td.querySelector('.ur-gen').addEventListener('click', () => {{
    const hs = td.querySelector('.ur-hs').value;
    const as_ = td.querySelector('.ur-as').value;
    const elo = td.querySelector('.ur-elo').value;
    const gains = td.querySelector('.ur-gains').value;
    const draw = hs !== '' && as_ !== '' && hs === as_;
    let cmd = `python3 worldcup/scripts/set_result.py ${{YEAR}} ${{game.gameNumber}} ${{hs}} ${{as_}}`;
    if (elo !== '') cmd += ` ${{elo}} --gains ${{draw ? (gains || '???') : (Number(hs) > Number(as_) ? 'home' : 'away')}}`;
    td.querySelector('.ur-cmd').value = cmd;
  }});

  td.querySelector('.ur-copy').addEventListener('click', () => {{
    const cmdInput = td.querySelector('.ur-cmd');
    cmdInput.select();
    navigator.clipboard.writeText(cmdInput.value);
  }});

  expandTr.appendChild(td);
  tr.after(expandTr);
  expandRow = expandTr;
}}

// Mirrors knockout.py's rounds_for_size() — see that file for the round
// shape rationale. Keep the two in sync if this ever changes.
const KNOCKOUT_ROUND_LABELS = {{ 32: 'Round of 32', 16: 'Round of 16', 8: 'Quarterfinals', 4: 'Semifinals' }};
function knockoutRounds(size) {{
  const rounds = [];
  let n = size;
  while (n > 4) {{ rounds.push([KNOCKOUT_ROUND_LABELS[n], n / 2]); n /= 2; }}
  rounds.push(['Semifinals', 2]);
  rounds.push(['Final', 2]);
  return rounds;
}}

let selectedBracketGameNumber = null;

function bracketAdminTeamHtml(game, side, flagByTeam, decided) {{
  const team = game[side + 'Team'];
  if (!team) return `<div class="ab-team ab-tbd">${{esc(feedLabel(game[side + 'From']))}}</div>`;
  const score = game[side + 'Score'];
  const otherScore = game[side === 'home' ? 'awayScore' : 'homeScore'];
  let cls = 'ab-team';
  if (decided && score !== otherScore) cls += score > otherScore ? ' winner' : ' loser';
  const scoreHtml = score != null ? `<span class="ab-score">${{score}}</span>` : '';
  return `<div class="${{cls}}">${{flagIcon(flagByTeam[team], team)}}<span class="ab-team-name">${{esc(team)}}</span>${{scoreHtml}}</div>`;
}}

function renderKnockoutAdmin(data, teams, flagByTeam) {{
  const container = document.getElementById('knockout-admin');
  const shorthandByName = {{}};
  for (const t of teams) shorthandByName[t.name] = t.shorthand;

  if (!data.knockoutSize) {{
    container.innerHTML = `
      <p>No bracket configured yet for ${{YEAR}}.</p>
      <div class="br-size-picker">
        ${{[32, 16, 8, 4].map(s => `<button data-size="${{s}}">${{s}}</button>`).join('')}}
      </div>
      <div class="ur-line"><input class="ur-cmd" id="size-cmd" type="text" readonly placeholder="pick a size above"><button id="size-copy">Copy</button></div>
    `;
    container.querySelectorAll('.br-size-picker button').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.getElementById('size-cmd').value = `python3 worldcup/scripts/set_knockout_size.py ${{YEAR}} ${{btn.dataset.size}}`;
      }});
    }});
    document.getElementById('size-copy').addEventListener('click', () => {{
      const cmdInput = document.getElementById('size-cmd');
      cmdInput.select();
      navigator.clipboard.writeText(cmdInput.value);
    }});
    return;
  }}

  const rounds = knockoutRounds(data.knockoutSize);
  const lastRound = rounds.length - 1;
  const koGames = data.games.filter(g => g.round != null).sort((a, b) => a.gameNumber - b.gameNumber);

  container.innerHTML = `
    <p>Bracket size: ${{data.knockoutSize}} (starts at ${{rounds[0][0]}})</p>
    <div class="ab-wrap" id="ab-wrap"></div>
    <div id="bracket-edit-panel"></div>
  `;

  const wrap = document.getElementById('ab-wrap');
  rounds.forEach(([label], roundIdx) => {{
    const roundGames = koGames.filter(g => g.round === roundIdx);

    const roundDiv = document.createElement('div');
    roundDiv.className = 'ab-round';
    roundDiv.innerHTML = `<div class="ab-round-label">${{esc(label)}}</div><div class="ab-round-games"></div>`;
    const gamesDiv = roundDiv.querySelector('.ab-round-games');

    roundGames.forEach((game, gameIdx) => {{
      const decided = game.homeScore != null && game.awayScore != null;
      const sub = roundIdx === lastRound
        ? `<div class="ab-sub">${{gameIdx === 0 ? 'Third-Place Match' : 'Final'}}</div>`
        : '';
      const wrapDiv = document.createElement('div');
      wrapDiv.className = 'ab-game-wrap';
      const box = document.createElement('div');
      box.className = 'ab-game';
      box.dataset.game = game.gameNumber;
      box.innerHTML = sub +
        `<div class="ab-date">${{game.date ? esc(game.date) : 'Date TBD'}}</div>` +
        bracketAdminTeamHtml(game, 'home', flagByTeam, decided) +
        bracketAdminTeamHtml(game, 'away', flagByTeam, decided);
      box.addEventListener('click', () => selectBracketGame(game, box, shorthandByName));
      wrapDiv.appendChild(box);
      gamesDiv.appendChild(wrapDiv);
    }});

    wrap.appendChild(roundDiv);
  }});
}}

function selectBracketGame(game, box, shorthandByName) {{
  const panel = document.getElementById('bracket-edit-panel');
  const allBoxes = document.querySelectorAll('.ab-game');

  if (selectedBracketGameNumber === game.gameNumber) {{
    selectedBracketGameNumber = null;
    panel.innerHTML = '';
    allBoxes.forEach(b => b.classList.remove('selected'));
    return;
  }}
  selectedBracketGameNumber = game.gameNumber;
  allBoxes.forEach(b => b.classList.toggle('selected', Number(b.dataset.game) === game.gameNumber));

  const homeShorthand = game.homeTeam ? (shorthandByName[game.homeTeam] || '') : '';
  const awayShorthand = game.awayTeam ? (shorthandByName[game.awayTeam] || '') : '';
  const homeMode = game.homeTeam ? 'team' : 'from';
  const awayMode = game.awayTeam ? 'team' : 'from';
  const homeFromGame = game.homeFrom ? game.homeFrom.game : '';
  const homeFromResult = game.homeFrom ? game.homeFrom.result : 'winner';
  const awayFromGame = game.awayFrom ? game.awayFrom.game : '';
  const awayFromResult = game.awayFrom ? game.awayFrom.result : 'winner';

  function slotHtml(side, mode, shorthand, fromGame, fromResult) {{
    return `
      <div class="br-slot">
        <strong>${{side === 'home' ? 'Home' : 'Away'}}:</strong>
        <select class="br-${{side}}-mode">
          <option value="team" ${{mode === 'team' ? 'selected' : ''}}>Team</option>
          <option value="from" ${{mode === 'from' ? 'selected' : ''}}>From game</option>
        </select>
        <input class="br-${{side}}-team" type="text" placeholder="shorthand e.g. CAN" value="${{esc(shorthand)}}" style="display:${{mode === 'team' ? 'inline-block' : 'none'}}">
        <span class="br-${{side}}-from-wrap" style="display:${{mode === 'from' ? 'inline-flex' : 'none'}};gap:0.4rem;align-items:center">
          <input class="br-${{side}}-from-game" type="number" placeholder="game #" value="${{fromGame}}">
          <select class="br-${{side}}-from-result">
            <option value="winner" ${{fromResult === 'winner' ? 'selected' : ''}}>winner</option>
            <option value="loser" ${{fromResult === 'loser' ? 'selected' : ''}}>loser</option>
          </select>
        </span>
      </div>`;
  }}

  panel.innerHTML = `
    <div class="ur-line"><strong>#${{game.gameNumber}}</strong></div>
    <div class="ur-line"><label>Date: <input class="br-date" type="date" value="${{game.date || ''}}"></label></div>
    <div class="ur-line">${{slotHtml('home', homeMode, homeShorthand, homeFromGame, homeFromResult)}}</div>
    <div class="ur-line">${{slotHtml('away', awayMode, awayShorthand, awayFromGame, awayFromResult)}}</div>
    <div class="ur-line">
      <button class="ur-gen">Generate command</button>
      <input class="ur-cmd" type="text" readonly placeholder="command will appear here">
      <button class="ur-copy">Copy</button>
    </div>
  `;

  ['home', 'away'].forEach(side => {{
    panel.querySelector(`.br-${{side}}-mode`).addEventListener('change', e => {{
      const isTeam = e.target.value === 'team';
      panel.querySelector(`.br-${{side}}-team`).style.display = isTeam ? 'inline-block' : 'none';
      panel.querySelector(`.br-${{side}}-from-wrap`).style.display = isTeam ? 'none' : 'inline-flex';
    }});
  }});

  panel.querySelector('.ur-gen').addEventListener('click', () => {{
    let cmd = `python3 worldcup/scripts/set_bracket_game.py ${{YEAR}} ${{game.gameNumber}}`;
    const date = panel.querySelector('.br-date').value;
    if (date) cmd += ` --date ${{date}}`;
    ['home', 'away'].forEach(side => {{
      const mode = panel.querySelector(`.br-${{side}}-mode`).value;
      if (mode === 'team') {{
        const shorthand = panel.querySelector(`.br-${{side}}-team`).value.trim();
        if (shorthand) cmd += ` --${{side}} ${{shorthand}}`;
      }} else {{
        const gameNum = panel.querySelector(`.br-${{side}}-from-game`).value;
        const result = panel.querySelector(`.br-${{side}}-from-result`).value;
        if (gameNum) cmd += ` --${{side}}-from ${{gameNum}}:${{result}}`;
      }}
    }});
    panel.querySelector('.ur-cmd').value = cmd;
  }});

  panel.querySelector('.ur-copy').addEventListener('click', () => {{
    const cmdInput = panel.querySelector('.ur-cmd');
    cmdInput.select();
    navigator.clipboard.writeText(cmdInput.value);
  }});
}}

function main() {{
  const games = DATA.games;
  const flagByTeam = {{}};
  for (const t of teams) flagByTeam[t.name] = t.flag;

  const tbody = document.getElementById('games');
  tbody.innerHTML = '';
  if (games.length === 0) {{
    tbody.innerHTML = '<tr><td colspan="4">No games</td></tr>';
    renderKnockoutAdmin(DATA, teams, flagByTeam);
    return;
  }}

  for (const game of games) {{
    const tr = document.createElement('tr');
    const hs = game.homeScore != null ? game.homeScore : '';
    const as_ = game.awayScore != null ? game.awayScore : '';
    tr.innerHTML = `
      <td>${{game.date || ''}}</td>
      <td>#${{game.gameNumber}}</td>
      <td><div class="flag-cell">${{teamCellHtml(game, 'home', flagByTeam)}} <strong>${{hs}}</strong></div></td>
      <td><div class="flag-cell"><strong>${{as_}}</strong> ${{teamCellHtml(game, 'away', flagByTeam)}}</div></td>
    `;
    tr.addEventListener('click', () => toggleExpand(game, tr, flagByTeam));
    tbody.appendChild(tr);
  }}

  renderKnockoutAdmin(DATA, teams, flagByTeam);
}}

const VIEWS = ['matches', 'groups', 'knockout'];

function setView(view) {{
  if (!VIEWS.includes(view)) view = 'matches';
  for (const v of VIEWS) {{
    document.getElementById(v + '-view').style.display = v === view ? 'block' : 'none';
    document.getElementById('tab-' + v).classList.toggle('active', v === view);
  }}
  if (location.hash.slice(1) !== view) history.replaceState(null, '', '#' + view);
}}
window.addEventListener('hashchange', () => setView(location.hash.slice(1)));

main();
setView(location.hash.slice(1) || 'matches');
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    teams = json.load(open(ROOT / "data" / "teams.json"))

    for year in YEARS:
        data = json.load(open(ROOT / "data" / f"{year}.json"))
        html = build_admin_page(year, data, teams)
        path = PROJECT_ROOT / "admin" / f"{year}.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        print(f"Updated admin/{year}.html")


if __name__ == "__main__":
    main()
