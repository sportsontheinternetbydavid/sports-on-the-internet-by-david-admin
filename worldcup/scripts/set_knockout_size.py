#!/usr/bin/env python3
"""Configure a tournament's knockout-bracket size, tagging/scaffolding its games.

Usage:
  worldcup/scripts/set_knockout_size.py YEAR {32|16|8|4} [--start-game N]

Example (live tournament, only the entry round known so far):
  worldcup/scripts/set_knockout_size.py 2026 32

Example (complete historical tournament, every round already in the file):
  worldcup/scripts/set_knockout_size.py 1998 16 --start-game 49

SIZE is the number of teams entering the knockout stage (Round of 32/16,
Quarterfinals, or Semifinals). It determines the sequence of rounds via
worldcup/scripts/knockout.py — see that file for the round shape.

This is a one-time setup step per tournament. It walks the rounds in order
(entry round first) and, for each, checks whether that round's games
already exist in data/YEAR.json as ordinary games — real homeTeam/awayTeam
(and, if played, scores), exactly like every other game in the file. Entry-
round matchups (and any later round already known) always come from a
concrete source — group standings, or an already-played earlier round —
never a deferred placeholder, so they're always entered as plain games,
never scaffolded.

For each round, in order:
  - If that round's games already exist, they're tagged "round": <index>
    in place — nothing else about them is touched.
  - Otherwise, that round (and every round after it) is scaffolded: one stub
    game per slot is appended, with a gameNumber continuing on from the last
    existing game, and null homeTeam/awayTeam/date/scores. Fill these in
    with worldcup/scripts/set_bracket_game.py as each round's matchups and
    dates become known.

--start-game N tells the script the entry round's first game number — i.e.
where the group stage ends. Needed whenever the knockout stage already
extends past the entry round (e.g. a fully complete historical tournament),
since the script can no longer assume "the entry round is simply the last N
games in the file." Without --start-game, it makes exactly that assumption
— correct for the common case of a live tournament where only the entry
round has been entered so far.

Refuses to run if the tournament already has a "knockoutSize" set — this
script only scaffolds once. Use worldcup/scripts/set_result.py as usual
once a knockout game (including the entry round) is played.

After scaffolding, the script commits and pushes the change to the private
admin repo, then deploys the rebuilt site/ (same as set_result.py). Pass
--no-push to update local files only.
"""
import argparse
import json
import sys
from pathlib import Path

import build
import gitops
import knockout

ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("year")
    parser.add_argument("size", type=int, choices=knockout.VALID_SIZES)
    parser.add_argument("--start-game", type=int, default=None,
                         help="gameNumber the entry round starts at (where the group stage ends). "
                              "Defaults to treating the last entry-round-sized batch of existing "
                              "games as the entry round.")
    parser.add_argument("--no-push", action="store_true", help="Update local files only — skip the admin-repo commit/push and public deploy.")
    args = parser.parse_args()

    path = ROOT / "data" / f"{args.year}.json"
    if not path.exists():
        sys.exit(f"No data file for year {args.year}.")

    data = json.load(open(path))
    if not isinstance(data, dict):
        sys.exit(f"{path}: expected the {{teamElos, games}} dict format — run set_team_elo.py first to upgrade it.")

    if data.get("knockoutSize") is not None:
        sys.exit(f"{args.year} already has knockoutSize={data['knockoutSize']}. This script only scaffolds once; edit data/{args.year}.json directly to change it.")

    rounds = knockout.rounds_for_size(args.size)
    entry_label, entry_count = rounds[0]

    games = data["games"]
    games_sorted = sorted(games, key=lambda g: g["gameNumber"])

    if args.start_game is not None:
        matches = [i for i, g in enumerate(games_sorted) if g["gameNumber"] == args.start_game]
        if not matches:
            sys.exit(f"No game numbered {args.start_game} found in {args.year}.")
        start_idx = matches[0]
    else:
        if len(games_sorted) < entry_count:
            sys.exit(f"Expected at least {entry_count} existing games for the '{entry_label}' entry round "
                     f"(size {args.size}); found {len(games_sorted)} total. Add the entry round's games first, "
                     f"the same way any other game is added — or pass --start-game if the knockout stage "
                     f"already extends past the entry round (e.g. a complete historical tournament).")
        start_idx = len(games_sorted) - entry_count

    # Walk rounds in order: tag whichever already exist, scaffold the rest.
    cursor = start_idx
    tagged = []       # (label, [gameNumbers])
    scaffolded = []   # (label, [gameNumbers])
    for round_idx, (label, count) in enumerate(rounds):
        available = len(games_sorted) - cursor
        if available >= count:
            block = games_sorted[cursor:cursor + count]
            if any(g.get("round") is not None for g in block):
                sys.exit(f"Some of the games that would become the '{label}' round already have a 'round' "
                         f"set — {args.year} may already be partially configured. Check data/{args.year}.json.")
            for g in block:
                g["round"] = round_idx
            tagged.append((label, [g["gameNumber"] for g in block]))
            cursor += count
        else:
            next_gn = games_sorted[-1]["gameNumber"] + 1 if games_sorted else 1
            for round_idx2, (label2, count2) in enumerate(rounds[round_idx:], start=round_idx):
                nums = []
                for _ in range(count2):
                    games.append({
                        "gameNumber": next_gn,
                        "homeTeam": None,
                        "homeScore": None,
                        "awayTeam": None,
                        "awayScore": None,
                        "date": None,
                        "eloChange": None,
                        "round": round_idx2,
                        "homeFrom": None,
                        "awayFrom": None,
                    })
                    nums.append(next_gn)
                    next_gn += 1
                scaffolded.append((label2, nums))
            break

    data["knockoutSize"] = args.size
    data["games"] = games
    path.write_text(json.dumps(data, indent=2) + "\n")

    print(f"Set {args.year} knockoutSize={args.size}.")
    for label, nums in tagged:
        print(f"  {label}: tagged existing #{nums[0]}-#{nums[-1]}")
    for label, nums in scaffolded:
        print(f"  {label}: created #{nums[0]}-#{nums[-1]}")

    build.main()

    if args.no_push:
        print("Done (--no-push: skipped commit/push/deploy).")
    else:
        gitops.push_to_github(f"Data: {args.year} knockout bracket configured (size {args.size})")
        print("Done.")


if __name__ == "__main__":
    main()
