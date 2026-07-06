// Shared rendering logic for all World Cup pages.
// Each page must define the following globals before this script runs:
//   teams          — array from the embedded data block
//   GAMES          — alias for the page's games constant
//   YEAR           — e.g. 2018, 2022, 2026
//   TEAM_ELOS      — object mapping team name → pre-tournament ELO
//   GAMESETS       — array of [label, lastGameNumber] pairs defining tournament phases
//   CONFEDERATIONS — ordered array of confederation name strings
//   tbody          — document.getElementById('games')
//   thead          — document.querySelector('#matches-view thead')

// Early guards — must run before confByTeam/flagByTeam are built from these globals.
// Full structural validation (GAMESETS ordering, team-name coverage, etc.) runs at the
// bottom of this file once all functions are defined.
if (typeof teams === 'undefined') throw new Error('shared.js: page must define "teams" before loading this script');
if (typeof GAMES === 'undefined') throw new Error('shared.js: page must define "GAMES" before loading this script');

const confByTeam = {};
for (const t of teams) confByTeam[t.name] = t.confederation;
const flagByTeam = {};
for (const t of teams) flagByTeam[t.name] = t.flag;

// Universal fly in/out pacing — see requirements/public.md -> Navigation ->
// Transitions and ../nav.css's --fly-ms (the single source of truth; read
// here at runtime instead of a second hardcoded number that could drift
// out of sync with it). Every swap in this file is sequential (old content
// flies out, *then* new content is rendered and flies in) rather than the
// homepage's simultaneous dual-panel version, since these views hold
// heavier, dynamically-rendered content — so this constant is the out-leg's
// wait before swapping content, not a full round-trip.
const FLY_MS = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--fly-ms'));

// Shared fly-out/fly-in primitives — setPageView, setMatchView, and
// toggleBracketRound each swap different content (a whole view, a set of
// scattered table cells, one or more bracket columns), so this is a pair of
// small building blocks rather than one rigid "swap panel A for panel B"
// function. Callers own DOM mutation (removing/rendering content) and any
// scroll-lock lifecycle (see ../nav.css's .fly-scroll-lock) between the two.

// Flies `els` off-screen (see ../nav.css's .fly-panel) and resolves once the
// transition finishes. Leaves them in the flown-out state — hiding/removing
// them from the DOM afterward is the caller's job.
function flyOut(els) {
  return new Promise(function(resolve) {
    els.forEach(function(el) { el.classList.remove('fly-in-active'); el.classList.add('fly-panel', 'fly-out'); });
    window.setTimeout(resolve, FLY_MS);
  });
}

// Flies `els` in from off-screen, with an optional per-element stagger (ms)
// for a rapid-fire reveal of several at once (see Knockout's round toggle).
// Once settled, clears the fly classes back to no-transform rather than
// leaving `transform: translateX(0)` in place — see ../nav.css's .fly-panel
// comment for why a lingering identity transform is its own latent bug
// (breaks any position:fixed descendant, e.g. Rankings' #rank-info).
function flyIn(els, options) {
  const stagger = (options && options.stagger) || 0;
  const onSettled = options && options.onSettled;
  if (!els.length) { if (onSettled) onSettled(); return; }
  els.forEach(function(el, i) {
    el.classList.add('fly-panel', 'fly-in-start');
    if (stagger) el.style.transitionDelay = (i * stagger) + 'ms';
  });
  void els[0].offsetWidth;
  requestAnimationFrame(function() {
    els.forEach(function(el) { el.classList.remove('fly-in-start'); el.classList.add('fly-in-active'); });
    window.setTimeout(function() {
      els.forEach(function(el) {
        el.classList.remove('fly-panel', 'fly-in-active');
        if (stagger) el.style.transitionDelay = '';
      });
      if (onSettled) onSettled();
    }, FLY_MS);
  });
}

// Returns a deterministic slight rotation (±1deg) for a team's flag,
// derived from the team name so each team is consistent across all appearances.
function flagRotation(teamName) {
  let h = 0;
  for (let i = 0; i < teamName.length; i++) h = (h * 31 + teamName.charCodeAt(i)) & 0xffff;
  return ((h % 21) - 10) * 0.1; // -1.0 to +1.0 degrees
}

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

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
  // Neutral: page beige #F5F0E8 = rgb(245,240,232)
  // Max positive: brand green #27AE60 = rgb(39,174,96)
  // Max negative: brand red #C0392B = rgb(192,57,43)
  if (ratio >= 0) {
    const r = Math.round(245 + ratio * (39  - 245));
    const g = Math.round(240 + ratio * (174 - 240));
    const b = Math.round(232 + ratio * (96  - 232));
    return `rgb(${r},${g},${b})`;
  } else {
    const r = Math.round(245 + ratio * (245 - 192));
    const g = Math.round(240 + ratio * (240 - 57));
    const b = Math.round(232 + ratio * (232 - 43));
    return `rgb(${r},${g},${b})`;
  }
}

// Date, #, spacer, homeElo, homeFlag, homeScore, sep, awayScore, awayFlag, awayElo
const GAME_COL_COUNT = 10;
const matchState = { view: 'elo', colCount: GAME_COL_COUNT };

function gameColsHeader() {
  return (
    `<th class="narrow">Date</th>` +
    `<th class="narrow">#</th>` +
    `<th class="spacer"></th>` +
    `<th colspan="3" style="text-align:center">Home</th>` +
    `<th class="score-sep"></th>` +
    `<th colspan="3" style="text-align:center">Away</th>`
  );
}

// The first cell gets a divider border, separating the fixed game-info
// columns (built by gameColsHeader) from the confederation/stat columns.
function confHeaderRow(labels) {
  return labels.map((label, i) => `<th class="conf${i === 0 ? ' conf-first' : ''}">${label}</th>`).join('');
}

function renderMatchViewToggle() {
  const container = document.getElementById('match-view-toggle');
  const views = [['elo', 'ELO Shift'], ['wld', 'W / D / L'], ['stats', 'Stats']];
  container.innerHTML = views.map(([view, label]) =>
    `<button class="${matchState.view === view ? 'active' : ''}" onclick="setMatchView('${view}')">${label}</button>`
  ).join('');
}

function setMatchView(view) {
  if (view === matchState.view) return;
  // Only the confederation columns fly — every cell in both thead/tbody
  // shares the "conf" class (see confHeaderRow/renderElo/renderWld/
  // renderStats), so a class-driven fly transition applies identically and
  // simultaneously to all of them without touching the fixed game columns
  // to their left, matching requirements/public.md -> Match List ->
  // Confederation panel. render() always rebuilds the whole row (game
  // cells + conf cells together), so the fly-in step re-selects ".conf"
  // fresh after re-rendering rather than reusing the old (now removed) nodes.
  const scrollEl = document.querySelector('#matches-view .table-wrap');
  if (scrollEl) scrollEl.classList.add('fly-scroll-lock');
  flyOut(Array.from(document.querySelectorAll('#matches-view .conf'))).then(function() {
    matchState.view = view;
    render();
    flyIn(Array.from(document.querySelectorAll('#matches-view .conf')), {
      onSettled: function() { if (scrollEl) scrollEl.classList.remove('fly-scroll-lock'); }
    });
  });
}

// A knockout-bracket game may not have a concrete team yet — it defers to
// an earlier game's winner/loser via homeFrom/awayFrom instead. Everywhere a
// team would be shown, fall back to a "Winner/Loser of Game N" text label.
function feedLabel(from) {
  if (!from) return 'TBD';
  return `${from.result === 'loser' ? 'Loser' : 'Winner'} of Game ${from.game}`;
}

function flagCellHtml(game, side) {
  const team = game[side + 'Team'];
  if (team) {
    return `<td class="flag"><span class="icon" style="background-image:url('flags/${flagByTeam[team]}.svg');transform:rotate(${flagRotation(team)}deg)" title="${esc(team)}"></span></td>`;
  }
  return `<td class="flag tbd-slot">${esc(feedLabel(game[side + 'From']))}</td>`;
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
    flagCellHtml(game, 'home') +
    `<td class="narrow">${homeScore}</td>` +
    `<td class="score-sep">-</td>` +
    `<td class="narrow">${awayScore}</td>` +
    flagCellHtml(game, 'away') +
    `<td class="elo">${eloCell(game.awayEloPre, awayEloDelta)}</td>`
  );
}

// eloChange sign convention (matches data schema): positive = home team gained ELO, negative = away team gained.
// Every place that reads eloChange must apply this same sign: home += eloChange, away -= eloChange.
function computeEloRowTotals(games, confederations) {
  const totals = {};
  for (const c of confederations) totals[c] = 0;
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
  return rowTotals;
}

function computeWldRowTotals(games, confederations) {
  const totals = {};
  for (const c of confederations) totals[c] = { w: 0, d: 0, l: 0 };
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
    rowTotals.push(Object.fromEntries(confederations.map(c => [c, { ...totals[c] }])));
  }
  return rowTotals;
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

  if (games.length === 0) {
    thead.innerHTML = `<tr><th>No games</th></tr>`;
    tbody.innerHTML = `<tr><td>No games yet</td></tr>`;
    return;
  }

  // Build row-by-row ELO running totals once; derive column ordering from the last row.
  // Passing rowTotals into renderElo avoids a second identical walk over all games.
  const eloRowTotals = computeEloRowTotals(games, confederations);
  const finalTotals = eloRowTotals[eloRowTotals.length - 1];
  const ordered = [...confederations].sort((a, b) => (finalTotals[b] || 0) - (finalTotals[a] || 0));

  if (matchState.view === 'elo') renderElo(games, ordered, eloRowTotals);
  else if (matchState.view === 'wld') renderWld(games, ordered, eloRowTotals);
  else renderStats(games, ordered, eloRowTotals);

  renderMatchViewToggle();
}

function renderElo(games, ordered, rowTotals) {
  const N = ordered.length;
  matchState.colCount = GAME_COL_COUNT + N;

  thead.innerHTML = `<tr>${gameColsHeader()}${confHeaderRow(ordered)}</tr>`;

  games.forEach((game, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = gameRowCells(game) +
      ordered.map(c =>
        typeof game.eloChange === 'number'
          ? `<td class="num conf" style="background-color:${eloColor(rowTotals[i][c])}">${rowTotals[i][c]}</td>`
          : `<td class="num conf"></td>`
      ).join('');
    tbody.appendChild(tr);
  });
}

function renderWld(games, ordered, eloRowTotals) {
  const rowTotals = computeWldRowTotals(games, ordered);
  const N = ordered.length;
  matchState.colCount = GAME_COL_COUNT + N;

  thead.innerHTML = `<tr>${gameColsHeader()}${confHeaderRow(ordered)}</tr>`;

  const STICKY = '#FAD7A0';
  games.forEach((game, i) => {
    const played = game.homeScore !== null && game.awayScore !== null;
    const tr = document.createElement('tr');
    tr.innerHTML = gameRowCells(game) +
      ordered.map(c => {
        const bg = `background-color:${eloColor(eloRowTotals[i][c])}`;
        if (!played) return `<td class="num conf" style="${bg}"></td>`;
        const { w, l, d } = rowTotals[i][c];
        const prev = i > 0 ? rowTotals[i - 1][c] : { w: 0, d: 0, l: 0 };
        const hi = (val, key) => {
          if (rowTotals[i][c][key] !== prev[key]) {
            const tilt = (Math.random() * 10 - 5).toFixed(1);
            return `<span style="position:relative;display:inline-block">${val}<span style="position:absolute;width:1.05em;height:1.05em;top:50%;left:50%;transform:translate(-50%,-50%) rotate(${tilt}deg);background:${STICKY};display:flex;align-items:center;justify-content:center">${val}</span></span>`;
          }
          return val;
        };
        return `<td class="num conf" style="${bg}">${hi(w,'w')}-${hi(d,'d')}-${hi(l,'l')}</td>`;
      }).join('');
    tbody.appendChild(tr);
  });
}

function renderStats(games, ordered, _eloRowTotals) {
  const N = ordered.length;
  matchState.colCount = GAME_COL_COUNT + N;

  // Stat column definitions — trimmed to N if fewer than 3 confederations.
  const statDefs = [
    { label: 'Wins',  key: 'wins' },
    { label: 'Draws', key: 'draws' },
    { label: 'Win%',  key: 'pct'  },
  ].slice(0, N);
  const nStats = statDefs.length;
  const extra = N - nStats; // padding columns to reach N total

  const emptyTh = Array(extra).fill('<th class="conf"></th>').join('');
  thead.innerHTML = `<tr>${gameColsHeader()}${confHeaderRow(statDefs.map(d => d.label))}${emptyTh}</tr>`;

  const emptyTd = Array(N).fill('<td class="num conf"></td>').join('');
  const extraTd = Array(extra).fill('<td class="num conf"></td>').join('');
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
      const vals = { wins, draws, pct };
      tr.innerHTML = gameRowCells(game) +
        statDefs.map(d => `<td class="num conf">${vals[d.key]}</td>`).join('') + extraTd;
    } else {
      tr.innerHTML = gameRowCells(game) + emptyTd;
    }
    tbody.appendChild(tr);
  });
}

// ── Rankings view ──────────────────────────────────────────────────────────

function buildEloSnapshots() {
  const gamesByNumber = {};
  for (const g of GAMES) gamesByNumber[g.gameNumber] = g;

  const teamsInGameset = GAMESETS.map((_, i) => {
    if (i === 0) return null;
    const prevLast = GAMESETS[i - 1][1];
    const lastGame = GAMESETS[i][1];
    const s = new Set();
    for (let gn = prevLast + 1; gn <= lastGame; gn++) {
      const g = gamesByNumber[gn];
      if (g) { s.add(g.homeTeam); s.add(g.awayTeam); }
    }
    return s;
  });

  const eliminatedAfter = {};
  const allTeams = Object.keys(TEAM_ELOS);
  for (const team of allTeams) {
    let lastSeen = 0;
    for (let i = 1; i < GAMESETS.length; i++) {
      if (teamsInGameset[i] && teamsInGameset[i].has(team)) lastSeen = i;
    }
    eliminatedAfter[team] = lastSeen;
  }

  // ELO snapshots are derived from the pre-game ELOs written by build.py:
  //   post-game ELO for home team = homeEloPre + eloChange
  //   post-game ELO for away team = awayEloPre - eloChange
  // This makes the JS a reader of build.py's output rather than a parallel
  // reimplementation of the same chain, eliminating any risk of the two diverging.
  // Builds post-gameset ELO state by reading pre-game ELOs written by build.py.
  function applyGames(base, fromGn, toGn) {
    const next = { ...base };
    for (let gn = fromGn; gn <= toGn; gn++) {
      const g = gamesByNumber[gn];
      if (!g) continue;
      if (typeof g.eloChange === 'number') {
        if (g.homeEloPre !== null) next[g.homeTeam] = g.homeEloPre + g.eloChange;
        if (g.awayEloPre !== null) next[g.awayTeam] = g.awayEloPre - g.eloChange;
      }
    }
    return next;
  }

  const snapshots = [];
  // `baseline` is the ELO state after all completed gamesets; it carries forward
  // to teams that don't play in a given gameset.
  let baseline = { ...TEAM_ELOS };
  let liveFound = false;

  for (let i = 0; i < GAMESETS.length; i++) {
    if (i === 0) {
      snapshots.push({ label: 'Initial', complete: true, live: false, eloByTeam: { ...baseline } });
      continue;
    }
    const prevLast = GAMESETS[i - 1][1];
    const lastGame = GAMESETS[i][1];

    let allDone = true;
    for (let gn = prevLast + 1; gn <= lastGame; gn++) {
      const g = gamesByNumber[gn];
      if (!g) { console.warn(`shared.js: game #${gn} missing from data — treating gameset "${GAMESETS[i][0]}" as incomplete`); allDone = false; break; }
      if (g.eloChange === null) { allDone = false; break; }
    }

    if (allDone) {
      baseline = applyGames(baseline, prevLast + 1, lastGame);
      snapshots.push({ label: GAMESETS[i][0], complete: true, live: false, eloByTeam: { ...baseline } });
    } else if (!liveFound) {
      liveFound = true;
      const liveElo = applyGames(baseline, prevLast + 1, lastGame);
      const pendingTeams = new Set();
      for (let gn = prevLast + 1; gn <= lastGame; gn++) {
        const g = gamesByNumber[gn];
        if (g && g.eloChange === null) { pendingTeams.add(g.homeTeam); pendingTeams.add(g.awayTeam); }
      }
      snapshots.push({ label: GAMESETS[i][0], complete: false, live: true, eloByTeam: liveElo, pendingTeams });
    } else {
      snapshots.push({ label: GAMESETS[i][0], complete: false, live: false, eloByTeam: null });
    }
  }

  return { snapshots, eliminatedAfter };
}

function rankTeams(eloByTeam, prevRank) {
  const names = Object.keys(eloByTeam);
  names.sort((a, b) => {
    const diff = eloByTeam[b] - eloByTeam[a];
    if (diff !== 0) return diff;
    const pa = prevRank ? prevRank.indexOf(a) : -1;
    const pb = prevRank ? prevRank.indexOf(b) : -1;
    if (pa === -1 && pb === -1) return 0;
    if (pa === -1) return 1;
    if (pb === -1) return -1;
    return pa - pb;
  });
  return names;
}

const FLAG_PX_W = 35;
const FLAG_PX_H = 24;
const SCALE_GAP = 3;
const RANK_ROW_H = 36;

function scaleTopPx(elo, rawMin, rawMax, height) {
  const margin = RANK_ROW_H / 2;
  const drawH = height - 2 * margin - FLAG_PX_H;
  return Math.round(margin + drawH * (1 - (elo - rawMin) / (rawMax - rawMin)));
}

function maxClusterSizeForHeight(snapshots, ranked, rawMin, rawMax, height) {
  let maxSize = 1;
  snapshots.forEach((snap, si) => {
    if (!(snap.complete || snap.live) || !snap.eloByTeam || !ranked[si]) return;
    const tops = ranked[si]
      .map(team => scaleTopPx(snap.eloByTeam[team], rawMin, rawMax, height))
      .sort((a, b) => a - b);
    let lo = 0;
    for (let hi = 0; hi < tops.length; hi++) {
      while (tops[hi] - tops[lo] >= FLAG_PX_H) lo++;
      if (hi - lo + 1 > maxSize) maxSize = hi - lo + 1;
    }
  });
  return maxSize;
}

function computeScaleHeight(snapshots, ranked, rawMin, rawMax) {
  const MAX_H = 80000;
  if (maxClusterSizeForHeight(snapshots, ranked, rawMin, rawMax, MAX_H) >= 4) {
    return { height: MAX_H, hasError: true };
  }
  let lo = 100, hi = MAX_H;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (maxClusterSizeForHeight(snapshots, ranked, rawMin, rawMax, mid) >= 4) lo = mid;
    else hi = mid;
  }
  return { height: hi, hasError: false };
}

function computeTickStep(rawMin, rawMax, height) {
  const drawH = height - RANK_ROW_H;
  const pxPerElo = drawH / (rawMax - rawMin);
  const candidates = [200, 100, 50, 25, 10, 5, 2];
  for (const c of candidates) {
    const px = c * pxPerElo;
    if (px >= 150 && px <= 300) return c;
  }
  return candidates.reduce((best, c) =>
    Math.abs(c * pxPerElo - 200) < Math.abs(best * pxPerElo - 200) ? c : best
  );
}

const rankState = { view: 'rank', showElim: false, trueRank: false, model: null };

function setRankView(v) {
  rankState.view = v;
  document.getElementById('tab-rank').classList.toggle('active', v === 'rank');
  document.getElementById('tab-scale').classList.toggle('active', v === 'scale');
  updateRankingControls();
  renderRankings();
}

function toggleShowEliminated() {
  rankState.showElim = document.getElementById('chk-show-elim').checked;
  if (rankState.showElim) {
    rankState.trueRank = true;
    const chk = document.getElementById('chk-true-rank');
    if (chk) chk.checked = true;
  }
  updateRankingControls();
  renderRankings();
}

function toggleTrueRank() {
  rankState.trueRank = document.getElementById('chk-true-rank').checked;
  renderRankings();
}

function updateRankingControls() {
  const trueRankLabel = document.getElementById('true-rank-label');
  const trueRankChk = document.getElementById('chk-true-rank');
  if (!trueRankLabel || !trueRankChk) return;
  const isRank = rankState.view === 'rank';
  trueRankLabel.style.display = isRank ? '' : 'none';
}

// rankState.model is cached for the page lifetime — data is static (embedded at build time), so no invalidation needed.

function buildRankingsModel() {
  const { snapshots, eliminatedAfter } = buildEloSnapshots();

  const gnMap = {};
  for (const g of GAMES) gnMap[g.gameNumber] = g;
  const gamesByTeamInSnap = snapshots.map((snap, si) => {
    if (si === 0) return {};
    const prevLast = GAMESETS[si - 1][1];
    const lastGame = GAMESETS[si][1];
    const map = {};
    for (let gn = prevLast + 1; gn <= lastGame; gn++) {
      const g = gnMap[gn];
      if (g) { map[g.homeTeam] = g; map[g.awayTeam] = g; }
    }
    return map;
  });

  const ranked = [];
  let prevRank = null;
  for (const snap of snapshots) {
    if (snap.complete || snap.live) {
      const order = rankTeams(snap.eloByTeam, prevRank);
      ranked.push(order);
      prevRank = order;
    } else {
      ranked.push(prevRank);
    }
  }

  let rawMin = Infinity, rawMax = -Infinity;
  for (const snap of snapshots) {
    if (snap.eloByTeam) {
      for (const elo of Object.values(snap.eloByTeam)) {
        if (elo < rawMin) rawMin = elo;
        if (elo > rawMax) rawMax = elo;
      }
    }
  }

  const { height: scaleH, hasError: scaleHasError } = computeScaleHeight(snapshots, ranked, rawMin, rawMax);

  return { snapshots, eliminatedAfter, gamesByTeamInSnap, ranked, rawMin, rawMax, scaleH, scaleHasError };
}

function renderRankings() {
  if (!rankState.model) rankState.model = buildRankingsModel();
  const { snapshots, eliminatedAfter, gamesByTeamInSnap, ranked, rawMin, rawMax, scaleH, scaleHasError } = rankState.model;

  function buildTipHtml(team, elo, si) {
    const flag = flagByTeam[team] || '';
    const flagStyle = flag ? `background-image:url('flags/${flag}.svg')` : '';
    let html = `<div class="tip-flag" style="${flagStyle}"></div>`;
    html += `<div class="tip-name">${esc(team)}</div>`;
    html += `<div class="tip-elo-val">${elo !== null ? Math.round(elo) : '—'}</div>`;
    html += `<hr class="tip-sep">`;
    const g = si > 0 ? gamesByTeamInSnap[si][team] : null;
    const isHome = g && g.homeTeam === team;
    const opponent = g ? (isHome ? g.awayTeam : g.homeTeam) : null;
    html += `<div class="tip-label">Date</div><div class="tip-val">${g && g.date ? formatDate(g.date) : '—'}</div>`;
    html += `<div class="tip-label">Opponent</div><div class="tip-val">${opponent ? esc(opponent) : '—'}</div>`;
    if (g && typeof g.eloChange === 'number') {
      const score = isHome ? `${g.homeScore}–${g.awayScore}` : `${g.awayScore}–${g.homeScore}`;
      const delta = isHome ? g.eloChange : -g.eloChange;
      const cls = delta >= 0 ? 'tip-delta-pos' : 'tip-delta-neg';
      const sign = delta >= 0 ? '+' : '';
      html += `<div class="tip-label">Score</div><div class="tip-val">${score}</div>`;
      html += `<div class="tip-label">ELO</div><div class="tip-val"><span class="${cls}">${sign}${delta}</span></div>`;
    } else {
      html += `<div class="tip-label">Score</div><div class="tip-val">—</div>`;
      html += `<div class="tip-label">ELO</div><div class="tip-val">—</div>`;
    }
    return html;
  }

  function buildResultBadge(team, g) {
    if (!g || typeof g.homeScore !== 'number' || typeof g.awayScore !== 'number') return null;
    const isHome = g.homeTeam === team;
    const teamScore = isHome ? g.homeScore : g.awayScore;
    const oppScore = isHome ? g.awayScore : g.homeScore;
    const opponent = isHome ? g.awayTeam : g.homeTeam;
    const result = teamScore > oppScore ? 'w' : teamScore < oppScore ? 'l' : 'd';
    const oppFlag = flagByTeam[opponent] || '';

    const badge = document.createElement('span');
    badge.className = `result-badge result-${result}`;

    const letter = document.createElement('span');
    letter.className = 'result-letter';
    letter.textContent = result.toUpperCase();
    badge.appendChild(letter);

    if (oppFlag) {
      const oppIcon = document.createElement('span');
      oppIcon.className = 'result-opp-flag';
      oppIcon.style.backgroundImage = `url('flags/${oppFlag}.svg')`;
      badge.appendChild(oppIcon);
    }
    return badge;
  }

  const numTeams = ranked[0].length;
  const isScale = rankState.view === 'scale';

  // In compact rank mode (trueRank=off, showElim=off), the axis height is the
  // maximum number of visible teams in any single column. Group-stage columns
  // always show all teams, so for normal tournaments this equals numTeams.
  // Using an explicit max makes the code correct even if TEAM_ELOS ever
  // includes teams that appear in no game (they'd be in ranked[0] but never
  // assigned to a gameset, inflating numTeams beyond what the axis needs).
  const rankSlots = (() => {
    if (isScale || rankState.showElim || rankState.trueRank) return numTeams;
    let max = 0;
    snapshots.forEach((snap, si) => {
      if (!(snap.complete || snap.live) || !ranked[si]) return;
      let count = 0;
      for (const team of ranked[si]) {
        const elim = eliminatedAfter[team] > 0 && si > eliminatedAfter[team];
        if (!elim) count++;
      }
      if (count > max) max = count;
    });
    return max || numTeams;
  })();

  const bodyH = isScale ? scaleH : rankSlots * RANK_ROW_H;

  const header = document.getElementById('rankings-header');
  const body = document.getElementById('rankings-body');

  // Set grid columns dynamically based on number of gamesets
  const colTemplate = `4rem repeat(${snapshots.length}, minmax(111px, 1fr))`;
  header.style.gridTemplateColumns = colTemplate;
  body.style.gridTemplateColumns = colTemplate;

  header.innerHTML =
    `<div class="axis-head">${isScale ? '' : '#'}</div>` +
    snapshots.map(s => `<div>${s.label}</div>`).join('');

  body.innerHTML = '';

  const axisCol = document.createElement('div');
  axisCol.className = 'rankings-axis';
  axisCol.style.height = bodyH + 'px';

  const gridLineYs = [];
  if (isScale) {
    const step = computeTickStep(rawMin, rawMax, scaleH);
    const firstTick = Math.ceil(rawMin / step) * step;
    for (let tick = firstTick; tick <= rawMax; tick += step) {
      const y = scaleTopPx(tick, rawMin, rawMax, scaleH);
      gridLineYs.push(y);
      const lbl = document.createElement('div');
      lbl.className = 'axis-label';
      lbl.style.top = y + 'px';
      lbl.textContent = tick;
      axisCol.appendChild(lbl);
    }
  } else {
    for (let i = 0; i < rankSlots; i++) {
      const lbl = document.createElement('div');
      lbl.className = 'axis-label';
      lbl.style.top = (i * RANK_ROW_H + RANK_ROW_H / 2) + 'px';
      lbl.textContent = i + 1;
      axisCol.appendChild(lbl);
    }
    for (let n = 4; n < rankSlots; n += 4) {
      gridLineYs.push(n * RANK_ROW_H);
    }
  }

  function addGridLines(el) {
    gridLineYs.forEach(y => {
      const line = document.createElement('div');
      line.className = 'grid-line';
      line.style.top = y + 'px';
      el.appendChild(line);
    });
  }
  addGridLines(axisCol);
  body.appendChild(axisCol);

  const debugClustersCb = document.getElementById('debug-clusters');
  snapshots.forEach((snap, si) => {
    const col = document.createElement('div');
    col.className = 'snap-body-col';

    if ((snap.complete || snap.live) && ranked[si]) {
      const pinData = [];

      let compactSlot = 0;
      ranked[si].forEach((team, rankIdx) => {
        const elo = snap.eloByTeam ? snap.eloByTeam[team] : null;
        const flag = flagByTeam[team] || '';
        const elim = eliminatedAfter[team] > 0 && si > eliminatedAfter[team];
        const hidden = !rankState.showElim && elim;
        const pending = snap.live && snap.pendingTeams && snap.pendingTeams.has(team);

        if (hidden) return;

        const zIndex = isScale ? (numTeams - rankIdx) : 1;
        let topPx;
        if (isScale) {
          topPx = scaleTopPx(elo, rawMin, rawMax, scaleH);
        } else if (!rankState.trueRank) {
          topPx = compactSlot * RANK_ROW_H + (RANK_ROW_H - FLAG_PX_H) / 2;
        } else {
          topPx = rankIdx * RANK_ROW_H + (RANK_ROW_H - FLAG_PX_H) / 2;
        }
        compactSlot++;

        const pin = document.createElement('div');
        pin.className = 'flag-pin';
        pin.dataset.team = team;
        pin.dataset.baseZ = zIndex;
        pin.dataset.tipHtml = buildTipHtml(team, elo, si);
        pin.style.top = topPx + 'px';
        pin.style.zIndex = zIndex;

        const iconStyle = `background-image:url('flags/${flag}.svg');transform:rotate(${flagRotation(team)}deg)` +
          (elim ? ';filter:grayscale(100%);opacity:0.4'
                : pending ? ';filter:grayscale(80%);opacity:0.35'
                : ';filter:saturate(0.8)');
        const icon = document.createElement('span');
        icon.className = 'icon';
        icon.style.cssText = iconStyle;
        const g = si > 0 ? gamesByTeamInSnap[si][team] : null;
        const badge = buildResultBadge(team, g);
        if (badge) icon.appendChild(badge);
        pin.appendChild(icon);

        col.appendChild(pin);
        if (isScale) pinData.push({ el: pin, topPx });
      });

      if (isScale && pinData.length) {
        const STEP = FLAG_PX_W + SCALE_GAP;
        const sorted = [...pinData].sort((a, b) => a.topPx - b.topPx);

        // Pass 1: greedy lane assignment
        const nextFreeY = [-Infinity, -Infinity, -Infinity];
        const laneOf = new Map();
        sorted.forEach(p => {
          let best = -1;
          for (let l = 0; l < 3; l++) {
            if (nextFreeY[l] <= p.topPx) {
              if (best === -1 || nextFreeY[l] > nextFreeY[best]) best = l;
            }
          }
          if (best === -1) best = 1;
          laneOf.set(p, best);
          nextFreeY[best] = p.topPx + FLAG_PX_H;
        });

        // Pass 2: visual centering per transitive cluster
        let gi = 0;
        while (gi < sorted.length) {
          let gj = gi + 1;
          while (gj < sorted.length && sorted[gj].topPx - sorted[gj - 1].topPx < FLAG_PX_H) gj++;
          const group = sorted.slice(gi, gj);
          const lanes = [...new Set(group.map(p => laneOf.get(p)))];
          const spread = (lanes.length - 1) * STEP;
          const laneMinTop = Object.fromEntries(lanes.map(l => [l, Math.min(...group.filter(p => laneOf.get(p) === l).map(p => p.topPx))]));
          const laneOffset = {};
          [...lanes].sort((a, b) => laneMinTop[a] - laneMinTop[b]).forEach((l, k) => { laneOffset[l] = -spread / 2 + k * STEP; });
          group.forEach(p => {
            p.el.style.left = `calc(50% + ${laneOffset[laneOf.get(p)]}px)`;
          });
          gi = gj;
        }
      }

      const debugCb = debugClustersCb;
      if (isScale && debugCb && debugCb.checked && pinData.length) {
        const atOneLess = pinData
          .map(p => ({ el: p.el, topPx: scaleTopPx(snap.eloByTeam[p.el.dataset.team], rawMin, rawMax, scaleH - 1) }))
          .sort((a, b) => a.topPx - b.topPx);
        let lo = 0;
        for (let hi = 0; hi < atOneLess.length; hi++) {
          while (atOneLess[hi].topPx - atOneLess[lo].topPx >= FLAG_PX_H) lo++;
          if (hi - lo + 1 >= 4) {
            const actualTops = atOneLess.slice(lo, hi + 1).map(p => pinData.find(q => q.el === p.el).topPx);
            const top = Math.min(...actualTops);
            const bottom = Math.max(...actualTops) + FLAG_PX_H;
            const box = document.createElement('div');
            box.className = 'debug-cluster';
            box.style.top = (top - 2) + 'px';
            box.style.height = (bottom - top + 4) + 'px';
            col.appendChild(box);
          }
        }
      }
    }

    addGridLines(col);

    if (isScale && scaleHasError && (snap.complete || snap.live) && snap.eloByTeam) {
      const warn = document.createElement('div');
      warn.className = 'scale-error';
      warn.textContent = '⚠ 4+ equal ELOs';
      col.appendChild(warn);
    }

    body.appendChild(col);
  });

}

// ── Rankings hover & info panel ───────────────────────────────────────────

function initRankingsHover() {
  const container = document.getElementById('rankings-cols');
  const infoPanel = document.getElementById('rank-info');
  let activeTeam = null;
  let activateTimer = null;
  let resetTimer = null;

  const updateInfoPosition = () => {
    const gridRect = container.getBoundingClientRect();
    const panelW = infoPanel.offsetWidth;
    const x = Math.max(8, gridRect.left - panelW);
    const panelH = infoPanel.offsetHeight;
    const y = Math.max(8, (window.innerHeight - panelH) / 2);
    infoPanel.style.left = x + 'px';
    infoPanel.style.top = y + 'px';
  };

  const showInfo = pin => {
    infoPanel.innerHTML = pin.dataset.tipHtml || '';
    updateInfoPosition();
    infoPanel.style.visibility = 'visible';
  };

  const hideInfo = () => { infoPanel.style.visibility = 'hidden'; };

  const applyHighlight = team => {
    activeTeam = team;
    container.querySelectorAll('[data-team]').forEach(el => {
      const isHovered = el.dataset.team === team;
      el.style.opacity = isHovered ? '1' : '0.15';
      el.style.zIndex = isHovered ? '9999' : (el.dataset.baseZ || '');
      el.classList.toggle('flag-highlighted', isHovered);
    });
  };

  const applyReset = () => {
    activeTeam = null;
    container.querySelectorAll('[data-team]').forEach(el => {
      el.style.opacity = '';
      el.style.zIndex = el.dataset.baseZ || '';
      el.classList.remove('flag-highlighted');
    });
  };

  const scheduleReset = () => {
    clearTimeout(activateTimer); activateTimer = null;
    if (!resetTimer) resetTimer = setTimeout(() => { resetTimer = null; applyReset(); hideInfo(); }, 300);
  };

  container.addEventListener('mouseover', e => {
    const pin = e.target.closest('[data-team]');
    if (!pin) { scheduleReset(); return; }
    const team = pin.dataset.team;
    clearTimeout(resetTimer); resetTimer = null;
    showInfo(pin);
    if (team === activeTeam) return;
    clearTimeout(activateTimer);
    activateTimer = setTimeout(() => { activateTimer = null; applyHighlight(team); }, 200);
  });

  container.addEventListener('mouseleave', scheduleReset);
}

// ── Knockout bracket view ─────────────────────────────────────────────────

// Mirrors knockout.py's rounds_for_size() — see that file for the round
// shape rationale. Keep the two in sync if this ever changes.
const KNOCKOUT_ROUND_LABELS = { 32: 'Round of 32', 16: 'Round of 16', 8: 'Quarterfinals', 4: 'Semifinals' };
function knockoutRounds(size) {
  const rounds = [];
  let n = size;
  while (n > 4) {
    rounds.push([KNOCKOUT_ROUND_LABELS[n], n / 2]);
    n /= 2;
  }
  rounds.push(['Semifinals', 2]);
  rounds.push(['Final', 2]);
  return rounds;
}

function bracketTeamRowHtml(game, side, decided) {
  const team = game[side + 'Team'];
  const score = game[side + 'Score'];
  if (!team) {
    return `<div class="bracket-team bracket-tbd">${esc(feedLabel(game[side + 'From']))}</div>`;
  }
  const otherScore = game[side === 'home' ? 'awayScore' : 'homeScore'];
  let cls = 'bracket-team';
  if (decided && score !== otherScore) cls += score > otherScore ? ' winner' : ' loser';
  const flag = flagByTeam[team]
    ? `<span class="icon" style="background-image:url('flags/${flagByTeam[team]}.svg');transform:rotate(${flagRotation(team)}deg)"></span>`
    : '';
  const scoreHtml = score != null ? `<span class="bracket-score">${score}</span>` : '';
  return `<div class="${cls}">${flag}<span class="bracket-team-name">${esc(team)}</span>${scoreHtml}</div>`;
}

// Which contiguous range of rounds [lo, hi] (inclusive, by round index) is
// visible in the bracket tree. hi: null means "through the last round" —
// resolved lazily in bracketRange() since KNOCKOUT_SIZE may not be known yet
// when this runs. Resets on reload — not meant to be a durable/shareable
// setting, just decluttering while browsing. Kept contiguous (shrinking only
// moves one edge in at a time; growing can jump straight to any hidden
// round) so the visible set never has a gap in the middle.
const bracketState = { lo: 0, hi: null };

function bracketRange() {
  const lastRound = knockoutRounds(KNOCKOUT_SIZE).length - 1;
  return { lo: bracketState.lo, hi: bracketState.hi === null ? lastRound : bracketState.hi };
}

function bracketColumnEl(roundIdx) {
  return document.querySelector(`.bracket-round[data-round-idx="${roundIdx}"]`);
}

// Flies newly-added columns in, staggered rapid-fire per
// requirements/public.md -> Knockout Bracket -> Round toggles.
function bracketScrollEl() {
  return document.querySelector('#knockout-outer .bracket');
}

// Flies newly-revealed round columns in, staggered rapid-fire per
// requirements/public.md -> Knockout Bracket -> Round toggles. Re-locks the
// (possibly freshly-rendered) .bracket for the duration, since flying even
// a single column fully off-screen can inflate its scroll width otherwise.
function revealBracketColumns(added) {
  if (!added.length) return;
  const scrollEl = bracketScrollEl();
  if (scrollEl) scrollEl.classList.add('fly-scroll-lock');
  const cols = added.slice().sort((a, b) => a - b).map(bracketColumnEl).filter(Boolean);
  flyIn(cols, {
    stagger: 90,
    onSettled: function() { if (scrollEl) scrollEl.classList.remove('fly-scroll-lock'); }
  });
}

function toggleBracketRound(roundIdx) {
  const before = bracketRange();
  const { lo, hi } = before;
  if (roundIdx >= lo && roundIdx <= hi) {
    // Hiding a visible round: only the two edges can shrink, one round at a
    // time, and never past a single remaining round — an all-hidden tree
    // reads as broken.
    if (lo === hi) return;
    if (roundIdx === lo) bracketState.lo = lo + 1;
    else if (roundIdx === hi) bracketState.hi = hi - 1;
    else return;
  } else if (roundIdx < lo) {
    // Revealing: jump straight to whichever hidden round was clicked,
    // showing everything between it and the current edge in one click.
    bracketState.lo = roundIdx;
  } else if (roundIdx > hi) {
    bracketState.hi = roundIdx;
  }
  const after = bracketRange();
  const removed = [];
  for (let i = before.lo; i <= before.hi; i++) if (i < after.lo || i > after.hi) removed.push(i);
  const added = [];
  for (let i = after.lo; i <= after.hi; i++) if (i < before.lo || i > before.hi) added.push(i);

  if (removed.length === 0) {
    // Pure growth — nothing to wait on flying out, render immediately and
    // fly the newly-revealed columns in.
    renderKnockout();
    revealBracketColumns(added);
    return;
  }
  // Shrinking always removes exactly one edge column (see the guard above) —
  // fly it out, then rebuild once it's clear and fly any newly-revealed
  // columns in (a shrink never also reveals a column, but kept generic).
  // renderKnockout() below replaces .bracket entirely, so this lock only
  // needs to cover the brief fly-out; revealBracketColumns re-locks the
  // fresh .bracket itself if there's anything to fly in afterward.
  const scrollEl = bracketScrollEl();
  if (scrollEl) scrollEl.classList.add('fly-scroll-lock');
  flyOut(removed.map(bracketColumnEl).filter(Boolean)).then(function() {
    renderKnockout();
    revealBracketColumns(added);
  });
}

function renderKnockout() {
  const container = document.getElementById('knockout-outer');
  const toggleContainer = document.getElementById('bracket-round-toggle');
  if (!KNOCKOUT_SIZE) {
    toggleContainer.innerHTML = '';
    container.innerHTML = '<p style="opacity:0.6; font-style:italic;">Knockout bracket not yet configured for this tournament.</p>';
    return;
  }

  const rounds = knockoutRounds(KNOCKOUT_SIZE);
  const lastRound = rounds.length - 1;
  const { lo, hi } = bracketRange();

  toggleContainer.innerHTML = rounds.map(([label], roundIdx) => {
    const visible = roundIdx >= lo && roundIdx <= hi;
    // Hidden rounds are always clickable (jump straight to them). Visible
    // rounds are only clickable at the current edge, one step at a time.
    const clickable = visible ? lo !== hi && (roundIdx === lo || roundIdx === hi) : true;
    return `<button class="${visible ? 'active' : ''}"${clickable ? '' : ' disabled'} onclick="toggleBracketRound(${roundIdx})">${esc(label)}</button>`;
  }).join('');

  const html = rounds.map(([label, count], roundIdx) => {
    if (roundIdx < lo || roundIdx > hi) return '';
    const games = GAMES.filter(g => g.round === roundIdx).sort((a, b) => a.gameNumber - b.gameNumber);
    // The last round bundles the Final (higher game number) and the
    // Third-Place Match (lower game number, scheduled earlier). Show the
    // Final on top since it's the headline game.
    const orderedGames = roundIdx === lastRound ? [...games].reverse() : games;
    const gamesHtml = orderedGames.map((game, gameIdx) => {
      const decided = game.homeScore != null && game.awayScore != null;
      const sub = roundIdx === lastRound
        ? `<div class="bracket-game-sub">${gameIdx === 0 ? 'Final' : 'Third-Place Match'}</div>`
        : '';
      return `<div class="bracket-game-wrap"><div class="bracket-game">` +
        sub +
        `<div class="bracket-date">${game.date ? formatDate(game.date) : 'Date TBD'}</div>` +
        bracketTeamRowHtml(game, 'home', decided) +
        bracketTeamRowHtml(game, 'away', decided) +
        `</div></div>`;
    }).join('');
    return `<div class="bracket-round" data-round-idx="${roundIdx}"><div class="bracket-round-label">${esc(label)}</div><div class="bracket-round-games">${gamesHtml}</div></div>`;
  }).join('');

  container.innerHTML = `<div class="bracket">${html}</div>`;
}

// ── Page view (Match List / Rankings / Groups / Knockout) ────────────────

const PAGE_VIEWS = ['matches', 'rankings', 'groups', 'knockout'];
// Every view's second-tier row in the fused nav — see .page-nav in shared.css.
const VIEW_TOGGLE_ID = { matches: 'match-view-toggle', rankings: 'rankings-view-toggle', groups: 'groups-view-toggle', knockout: 'bracket-round-toggle' };
let currentPageView = null;

function renderPageView(view) {
  if (view === 'matches') render();
  if (view === 'rankings') renderRankings();
  if (view === 'knockout') renderKnockout();
}

function setPageView(view) {
  if (!PAGE_VIEWS.includes(view)) view = 'matches';
  if (view === currentPageView) return;
  const outgoing = currentPageView;
  currentPageView = view;
  for (const v of PAGE_VIEWS) {
    document.getElementById('tab-' + v).classList.toggle('active', v === view);
    document.getElementById(VIEW_TOGGLE_ID[v]).style.display = v === view ? 'flex' : 'none';
  }
  const incoming = document.getElementById(view + '-view');
  if (!outgoing) {
    // First load (page just opened, possibly via a #hash) — show the target
    // view directly, no fly; there's nothing on screen yet to fly out of.
    for (const v of PAGE_VIEWS) document.getElementById(v + '-view').style.display = v === view ? 'block' : 'none';
    renderPageView(view);
    if (location.hash.slice(1) !== view) history.replaceState(null, '', '#' + view);
    return;
  }
  const outEl = document.getElementById(outgoing + '-view');
  // Flying a whole view fully off-screen (see .fly-panel in ../nav.css)
  // would otherwise briefly inflate body's own scrollable width — lock it
  // for exactly the transition, not permanently (a view's inner table/
  // bracket may legitimately need its own horizontal scroll at rest).
  document.body.classList.add('fly-scroll-lock');
  flyOut([outEl]).then(function() {
    outEl.style.display = 'none';
    outEl.classList.remove('fly-out', 'fly-panel');
    incoming.style.display = 'block';
    renderPageView(view);
    flyIn([incoming], { onSettled: function() { document.body.classList.remove('fly-scroll-lock'); } });
  });
  if (location.hash.slice(1) !== view) history.replaceState(null, '', '#' + view);
}

function validateContract() {
  const required = { teams, GAMES, YEAR, TEAM_ELOS, GAMESETS, CONFEDERATIONS, tbody, thead };
  for (const [k, v] of Object.entries(required)) {
    if (typeof v === 'undefined') throw new Error(`shared.js: page must define "${k}" before loading this script`);
  }
  if (!(tbody instanceof Element)) throw new Error('shared.js: "tbody" must be a DOM element — check that id="games" exists in the page');
  if (!(thead instanceof Element)) throw new Error('shared.js: "thead" must be a DOM element — check that #matches-view thead exists in the page');
  if (!Array.isArray(GAMESETS) || GAMESETS.length < 1 || GAMESETS[0][1] !== 0) {
    throw new Error('GAMESETS must be an array whose first entry has lastGameNumber = 0 (the pre-tournament snapshot)');
  }
  for (let i = 1; i < GAMESETS.length; i++) {
    if (GAMESETS[i][1] <= GAMESETS[i - 1][1]) {
      throw new Error(`GAMESETS[${i}] lastGameNumber (${GAMESETS[i][1]}) must be greater than GAMESETS[${i-1}] (${GAMESETS[i-1][1]})`);
    }
  }
  if (!Array.isArray(CONFEDERATIONS) || CONFEDERATIONS.length === 0) {
    throw new Error('CONFEDERATIONS must be a non-empty array');
  }
  const teamNames = new Set(teams.map(t => t.name));
  for (const g of GAMES) {
    // Knockout-bracket games may legitimately have a null team pending an
    // earlier game's result (see homeFrom/awayFrom) — only warn when a team
    // name is actually present but unrecognized.
    if (g.homeTeam != null && !teamNames.has(g.homeTeam)) console.warn(`shared.js: game #${g.gameNumber} homeTeam "${g.homeTeam}" not found in teams — flag and confederation will be missing`);
    if (g.awayTeam != null && !teamNames.has(g.awayTeam)) console.warn(`shared.js: game #${g.gameNumber} awayTeam "${g.awayTeam}" not found in teams — flag and confederation will be missing`);
  }
  // Full ELO chain sync check: walk every game in order, tracking each team's
  // running ELO from TEAM_ELOS through completed results (mirrors derive_elos in
  // build.py). Once a team hits a null eloChange its chain is broken and we stop
  // checking it — subsequent homeEloPre/awayEloPre values will be null by design.
  if (Object.keys(TEAM_ELOS).length > 0) {
    const current = { ...TEAM_ELOS };
    const broken = new Set();
    for (const g of GAMES) {
      const home = g.homeTeam;
      const away = g.awayTeam;
      if (home in TEAM_ELOS && !broken.has(home) && g.homeEloPre !== current[home]) {
        throw new Error(`shared.js: homeEloPre mismatch for "${home}" in game #${g.gameNumber}: embedded ${g.homeEloPre} ≠ expected ${current[home]} — run scripts/build.py to resync`);
      }
      if (away in TEAM_ELOS && !broken.has(away) && g.awayEloPre !== current[away]) {
        throw new Error(`shared.js: awayEloPre mismatch for "${away}" in game #${g.gameNumber}: embedded ${g.awayEloPre} ≠ expected ${current[away]} — run scripts/build.py to resync`);
      }
      if (typeof g.eloChange === 'number') {
        if (home in TEAM_ELOS && !broken.has(home)) current[home] += g.eloChange;
        if (away in TEAM_ELOS && !broken.has(away)) current[away] -= g.eloChange;
      } else {
        broken.add(home);
        broken.add(away);
      }
    }
  }
}
validateContract();

window.addEventListener('hashchange', () => setPageView(location.hash.slice(1)));
setPageView(location.hash.slice(1) || 'matches');
initRankingsHover();
