// Shared rendering logic for all World Cup pages.
// Each page must define the following globals before this script runs:
//   teams          — array from the embedded data block
//   GAMES          — alias for the page's games constant
//   YEAR           — e.g. 2018, 2022, 2026
//   CONFEDERATIONS — ordered array of confederation name strings
//   tbody          — document.getElementById('games')
//   thead          — document.querySelector('#matches-view thead')

const confByTeam = {};
for (const t of teams) confByTeam[t.name] = t.confederation;
const flagByTeam = {};
for (const t of teams) flagByTeam[t.name] = t.flag;

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function formatDate(dateStr) {
  if (!dateStr) return '';
  const [, month, day] = dateStr.split('-').map(Number);
  return `${MONTHS[month - 1]} ${day}`;
}

function signedElo(val) {
  if (typeof val !== 'number') return '';
  return val >= 0 ? `+${val}` : String(val);
}

function eloCell(preElo, delta) {
  if (delta !== '') return preElo != null ? `${preElo}${delta}` : delta;
  return preElo != null ? String(preElo) : '';
}

const ELO_GRADIENT_MAX = 400;
function eloColor(value) {
  const ratio = Math.max(-1, Math.min(1, value / ELO_GRADIENT_MAX));
  if (ratio >= 0) return `rgb(${255 - ratio * 105}, 255, ${255 - ratio * 105})`;
  return `rgb(255, ${255 + ratio * 105}, ${255 + ratio * 105})`;
}

let currentView = 'elo';
let currentColCount = 10;
let openExpandRow = null;
let openGameRow = null;

function gameColsHeader() {
  return (
    `<th class="narrow" rowspan="2">Date</th>` +
    `<th class="narrow" rowspan="2">#</th>` +
    `<th class="spacer" rowspan="2"></th>` +
    `<th colspan="3" rowspan="2" style="text-align:center">Home</th>` +
    `<th class="score-sep" rowspan="2"></th>` +
    `<th colspan="3" rowspan="2" style="text-align:center">Away</th>`
  );
}

function toggleCellHtml(colspan) {
  return `<th colspan="${colspan}" class="toggle-cell">` +
    `<div class="view-toggle">` +
    `<button data-view="elo"${currentView === 'elo' ? ' class="active"' : ''}>ELO Shift</button>` +
    `<button data-view="wld"${currentView === 'wld' ? ' class="active"' : ''}>W / L / D</button>` +
    `<button data-view="stats"${currentView === 'stats' ? ' class="active"' : ''}>Stats</button>` +
    `</div></th>`;
}

function gameRowCells(game) {
  const change = game.eloChange;
  const homeEloDelta = signedElo(change);
  const awayEloDelta = typeof change === 'number' ? signedElo(-change) : '';
  const homeScore = game.homeScore ?? '';
  const awayScore = game.awayScore ?? '';
  return (
    `<td class="narrow">${formatDate(game.date)}</td>` +
    `<td class="narrow">#${game.gameNumber}</td>` +
    `<td class="spacer"></td>` +
    `<td class="elo">${eloCell(game.homeEloPre, homeEloDelta)}</td>` +
    `<td class="flag"><span class="icon" style="background-image:url('data/flags/${flagByTeam[game.homeTeam]}.svg')" title="${game.homeTeam}"></span></td>` +
    `<td class="narrow">${homeScore}</td>` +
    `<td class="score-sep">-</td>` +
    `<td class="narrow">${awayScore}</td>` +
    `<td class="flag"><span class="icon" style="background-image:url('data/flags/${flagByTeam[game.awayTeam]}.svg')" title="${game.awayTeam}"></span></td>` +
    `<td class="elo">${eloCell(game.awayEloPre, awayEloDelta)}</td>`
  );
}

function wireToggle() {
  thead.querySelectorAll('.view-toggle button').forEach(btn => {
    btn.addEventListener('click', () => { currentView = btn.dataset.view; render(); });
  });
}

function render() {
  const games = GAMES;
  const participating = new Set();
  for (const game of games) {
    const hc = confByTeam[game.homeTeam];
    const ac = confByTeam[game.awayTeam];
    if (hc) participating.add(hc);
    if (ac) participating.add(ac);
  }
  const confederations = CONFEDERATIONS.filter(c => participating.has(c));

  tbody.innerHTML = '';
  openExpandRow = null;
  openGameRow = null;

  if (games.length === 0) {
    thead.innerHTML = `<tr><th>No games</th></tr><tr></tr>`;
    tbody.innerHTML = `<tr><td>No games yet</td></tr>`;
    return;
  }

  const eloTotals = {};
  for (const c of confederations) eloTotals[c] = 0;
  for (const game of games) {
    if (typeof game.eloChange === 'number') {
      const hc = confByTeam[game.homeTeam];
      const ac = confByTeam[game.awayTeam];
      if (hc) eloTotals[hc] += game.eloChange;
      if (ac) eloTotals[ac] -= game.eloChange;
    }
  }
  const ordered = [...confederations].sort((a, b) => eloTotals[b] - eloTotals[a]);

  if (currentView === 'elo') renderElo(games, ordered);
  else if (currentView === 'wld') renderWld(games, ordered);
  else renderStats(games, ordered);

  wireToggle();
}

function renderElo(games, ordered) {
  const totals = {};
  for (const c of ordered) totals[c] = 0;
  const rowTotals = [];
  for (const game of games) {
    if (typeof game.eloChange === 'number') {
      const hc = confByTeam[game.homeTeam];
      const ac = confByTeam[game.awayTeam];
      if (hc) totals[hc] += game.eloChange;
      if (ac) totals[ac] -= game.eloChange;
    }
    rowTotals.push({ ...totals });
  }
  const N = ordered.length;
  currentColCount = 10 + N;

  thead.innerHTML =
    `<tr>${gameColsHeader()}${toggleCellHtml(N)}</tr>` +
    `<tr>${ordered.map(c => `<th class="conf">${c}</th>`).join('')}</tr>`;

  games.forEach((game, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = gameRowCells(game) +
      ordered.map(c =>
        typeof game.eloChange === 'number'
          ? `<td class="num conf" style="background-color:${eloColor(rowTotals[i][c])}">${rowTotals[i][c]}</td>`
          : `<td class="num conf"></td>`
      ).join('');
    tr.addEventListener('click', () => toggleExpand(game, tr));
    tbody.appendChild(tr);
  });
}

function renderWld(games, ordered) {
  const totals = {};
  for (const c of ordered) totals[c] = { w: 0, l: 0, d: 0 };
  const rowTotals = [];
  for (const game of games) {
    const hs = game.homeScore;
    const as_ = game.awayScore;
    if (hs !== null && as_ !== null) {
      const hc = confByTeam[game.homeTeam];
      const ac = confByTeam[game.awayTeam];
      if (hs > as_) {
        if (hc) totals[hc].w++;
        if (ac) totals[ac].l++;
      } else if (as_ > hs) {
        if (ac) totals[ac].w++;
        if (hc) totals[hc].l++;
      } else {
        if (hc) totals[hc].d++;
        if (ac) totals[ac].d++;
      }
    }
    const snap = {};
    for (const c of ordered) snap[c] = { ...totals[c] };
    rowTotals.push(snap);
  }
  const N = ordered.length;
  currentColCount = 10 + N;

  thead.innerHTML =
    `<tr>${gameColsHeader()}${toggleCellHtml(N)}</tr>` +
    `<tr>${ordered.map(c => `<th class="conf">${c}</th>`).join('')}</tr>`;

  games.forEach((game, i) => {
    const played = game.homeScore !== null && game.awayScore !== null;
    const tr = document.createElement('tr');
    tr.innerHTML = gameRowCells(game) +
      ordered.map(c => {
        if (!played) return `<td class="num conf"></td>`;
        const { w, l, d } = rowTotals[i][c];
        return `<td class="num conf">${w}-${d}-${l}</td>`;
      }).join('');
    tr.addEventListener('click', () => toggleExpand(game, tr));
    tbody.appendChild(tr);
  });
}

function renderStats(games, ordered) {
  const N = ordered.length;
  currentColCount = 10 + N;
  const extra = Math.max(0, N - 3);
  const emptyTh = Array(extra).fill('<th class="conf"></th>').join('');
  thead.innerHTML =
    `<tr>${gameColsHeader()}${toggleCellHtml(N)}</tr>` +
    `<tr><th class="conf">Wins</th><th class="conf">Draws</th><th class="conf">Win%</th>${emptyTh}</tr>`;

  const emptyTd = Array(N).fill('<td class="num conf"></td>').join('');
  let wins = 0, draws = 0;
  games.forEach(game => {
    const hs = game.homeScore;
    const as_ = game.awayScore;
    const played = hs !== null && as_ !== null;
    const tr = document.createElement('tr');
    if (played) {
      if (hs !== as_) wins++;
      else draws++;
      const total = wins + draws;
      const pct = Math.round(wins / total * 100) + '%';
      const extraTd = Array(extra).fill('<td class="num conf"></td>').join('');
      tr.innerHTML = gameRowCells(game) +
        `<td class="num conf">${wins}</td><td class="num conf">${draws}</td><td class="num conf">${pct}</td>${extraTd}`;
    } else {
      tr.innerHTML = gameRowCells(game) + emptyTd;
    }
    tr.addEventListener('click', () => toggleExpand(game, tr));
    tbody.appendChild(tr);
  });
}

function toggleExpand(game, tr) {
  const colCount = currentColCount;
  if (openExpandRow) {
    openExpandRow.remove();
    openExpandRow = null;
    if (openGameRow === tr) { openGameRow = null; return; }
  }
  openGameRow = tr;
  const expandTr = document.createElement('tr');
  expandTr.className = 'expand-row';
  const td = document.createElement('td');
  td.colSpan = colCount;

  const hsVal = game.homeScore != null ? game.homeScore : '';
  const asVal = game.awayScore != null ? game.awayScore : '';
  const eloVal = game.eloChange != null ? Math.abs(game.eloChange) : '';
  const gainsVal = game.eloChange != null ? (game.eloChange >= 0 ? 'home' : 'away') : '';
  const isDraw = hsVal !== '' && asVal !== '' && hsVal === asVal;

  td.innerHTML = `
    <div class="ur-line"><strong>#${game.gameNumber}: ${game.homeTeam} vs ${game.awayTeam}</strong></div>
    <div class="ur-line">
      <label>Home score: <input class="ur-hs" type="number" min="0" value="${hsVal}"></label>
      <label>Away score: <input class="ur-as" type="number" min="0" value="${asVal}"></label>
      <label>ELO magnitude (opt): <input class="ur-elo" type="number" min="0" value="${eloVal}"></label>
      <label class="ur-gains-wrap" style="display:${isDraw ? 'flex' : 'none'}">Who gains ELO:
        <select class="ur-gains">
          <option value="" ${gainsVal === '' ? 'selected' : ''}>—</option>
          <option value="home" ${gainsVal === 'home' ? 'selected' : ''}>${game.homeTeam}</option>
          <option value="away" ${gainsVal === 'away' ? 'selected' : ''}>${game.awayTeam}</option>
        </select>
      </label>
    </div>
    <div class="ur-line">
      <button class="ur-gen">Generate command</button>
      <input class="ur-cmd" type="text" readonly placeholder="command will appear here">
      <button class="ur-copy">Copy</button>
    </div>`;

  td.addEventListener('click', e => e.stopPropagation());

  function updateGainsVisibility() {
    const hs = td.querySelector('.ur-hs').value;
    const as_ = td.querySelector('.ur-as').value;
    const draw = hs !== '' && as_ !== '' && hs === as_;
    td.querySelector('.ur-gains-wrap').style.display = draw ? 'flex' : 'none';
  }
  td.querySelector('.ur-hs').addEventListener('input', updateGainsVisibility);
  td.querySelector('.ur-as').addEventListener('input', updateGainsVisibility);

  td.querySelector('.ur-gen').addEventListener('click', () => {
    const hs = td.querySelector('.ur-hs').value;
    const as_ = td.querySelector('.ur-as').value;
    const elo = td.querySelector('.ur-elo').value;
    const gains = td.querySelector('.ur-gains').value;
    const draw = hs !== '' && as_ !== '' && hs === as_;
    let cmd = `python3 scripts/set_result.py ${YEAR} ${game.gameNumber} ${hs} ${as_}`;
    if (elo !== '') cmd += ` ${elo} --gains ${draw ? (gains || '???') : (Number(hs) > Number(as_) ? 'home' : 'away')}`;
    td.querySelector('.ur-cmd').value = cmd;
  });

  td.querySelector('.ur-copy').addEventListener('click', () => {
    const cmdInput = td.querySelector('.ur-cmd');
    cmdInput.select();
    navigator.clipboard.writeText(cmdInput.value);
  });

  expandTr.appendChild(td);
  tr.after(expandTr);
  openExpandRow = expandTr;
}
