#!/usr/bin/env python3
"""Set the date and/or participants of a knockout-bracket game.

Usage:
  worldcup/scripts/set_bracket_game.py YEAR GAME_NUMBER [options]

Options:
  --date YYYY-MM-DD              Set the game's date.
  --home TEAM_SHORTHAND          Set the home team directly (once known).
  --home-from GAME_NUMBER:RESULT Defer the home team to another game's
                                  outcome, e.g. "73:winner". RESULT is
                                  "winner" or "loser" (loser is only used
                                  for the third-place game).
  --away TEAM_SHORTHAND          Same as --home, for the away side.
  --away-from GAME_NUMBER:RESULT Same as --home-from, for the away side.

Example:
  worldcup/scripts/set_bracket_game.py 2026 89 --date 2026-07-04 \\
      --home-from 73:winner --away-from 76:winner

  # Later, once Game 73's result is in:
  worldcup/scripts/set_bracket_game.py 2026 89 --home CAN

Only the options you pass are changed — anything else about the game is
left as-is. GAME_NUMBER must already exist and belong to a knockout bracket
(created by worldcup/scripts/set_knockout_size.py); this script only edits
structure (date, who plays), not scores — use worldcup/scripts/set_result.py
for that once both teams and the result are known.

Setting --home/--away on a game clears any --home-from/--away-from on that
side (and vice versa) — a slot is either a concrete team or a deferred
reference, never both.

A --home-from/--away-from reference is checked before anything is written:
the game it points at must exist, must be in the immediately preceding
round (never an earlier or later one), "loser" must only be used on the
last round's third-place game, and no other slot may already defer to that
same game+result. A bad reference exits with a specific error instead of
writing structure that would only surface as a problem later.

After updating, the script commits and pushes the change to the private
admin repo, then deploys the rebuilt site/ (same as set_result.py). Pass
--no-push to update local files only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import build
import gitops
import knockout
from teams import load_teams, resolve_team

ROOT = Path(__file__).resolve().parent.parent


def parse_from(spec, flag_name):
    m = re.fullmatch(r"(\d+):(winner|loser)", spec)
    if not m:
        sys.exit(f"{flag_name} must look like GAME_NUMBER:winner or GAME_NUMBER:loser, got '{spec}'")
    return {"game": int(m.group(1)), "result": m.group(2)}


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("year")
    parser.add_argument("game_number", type=int)
    parser.add_argument("--date")
    parser.add_argument("--home")
    parser.add_argument("--home-from")
    parser.add_argument("--away")
    parser.add_argument("--away-from")
    parser.add_argument("--no-push", action="store_true", help="Update local files only — skip the admin-repo commit/push and public deploy.")
    args = parser.parse_args()

    if args.home and args.home_from:
        sys.exit("Pass only one of --home / --home-from.")
    if args.away and args.away_from:
        sys.exit("Pass only one of --away / --away-from.")
    if not any([args.date, args.home, args.home_from, args.away, args.away_from]):
        sys.exit("Nothing to update — pass at least one of --date/--home/--home-from/--away/--away-from.")
    if args.date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        sys.exit(f"--date must look like YYYY-MM-DD, got '{args.date}'.")

    path = ROOT / "data" / f"{args.year}.json"
    if not path.exists():
        sys.exit(f"No data file for year {args.year}.")

    data = json.load(open(path))
    games = data["games"] if isinstance(data, dict) else data

    matches = [g for g in games if g["gameNumber"] == args.game_number]
    if not matches:
        sys.exit(f"No game number {args.game_number} found in {args.year}.")
    game = matches[0]

    if game.get("round") is None:
        sys.exit(f"Game #{args.game_number} is not a knockout-bracket game (no 'round' field). "
                 f"Run set_knockout_size.py first, or use set_result.py for regular results.")

    teams = load_teams()
    changes = []

    if args.date:
        game["date"] = args.date
        changes.append(f"date={args.date}")

    if args.home:
        name = resolve_team(args.home, teams)
        game["homeTeam"] = name
        game["homeFrom"] = None
        changes.append(f"home={name}")
    elif args.home_from:
        game["homeFrom"] = parse_from(args.home_from, "--home-from")
        game["homeTeam"] = None
        changes.append(f"homeFrom={game['homeFrom']}")

    if args.away:
        name = resolve_team(args.away, teams)
        game["awayTeam"] = name
        game["awayFrom"] = None
        changes.append(f"away={name}")
    elif args.away_from:
        game["awayFrom"] = parse_from(args.away_from, "--away-from")
        game["awayTeam"] = None
        changes.append(f"awayFrom={game['awayFrom']}")

    # Catch a bad --home-from/--away-from before anything is written — a
    # reference to a game that doesn't exist, isn't in the immediately
    # preceding round, or already feeds a different slot. Same check
    # build.py's validate() runs on every game already in the file (see
    # knockout.check_from_ref), just run here first so a mistake is caught
    # with a clean message instead of silently writing bad structure (or
    # surfacing later as a build error against data that's already on disk).
    knockout_size = data.get("knockoutSize") if isinstance(data, dict) else None
    for from_key in ("homeFrom", "awayFrom"):
        frm = game.get(from_key)
        if frm is not None:
            try:
                knockout.check_from_ref(games, game, from_key, frm, knockout_size)
            except ValueError as e:
                sys.exit(str(e))

    if isinstance(data, dict):
        data["games"] = games
        path.write_text(json.dumps(data, indent=2) + "\n")
    else:
        path.write_text(json.dumps(games, indent=2) + "\n")

    print(f"Updated {path}: game #{args.game_number} — " + ", ".join(changes))

    build.main()

    if args.no_push:
        print("Done (--no-push: skipped commit/push/deploy).")
    else:
        gitops.push_to_github(f"Data: {args.year} bracket game #{args.game_number} — " + ", ".join(changes))
        print("Done.")


if __name__ == "__main__":
    main()
