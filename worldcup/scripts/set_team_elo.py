#!/usr/bin/env python3
"""Set a team's initial ELO for a tournament and regenerate the HTML pages.

Usage:
  worldcup/scripts/set_team_elo.py YEAR TEAM_SHORTHAND ELO
  worldcup/scripts/set_team_elo.py --list-teams

Example:
  worldcup/scripts/set_team_elo.py 2018 FRA 1998

TEAM_SHORTHAND is the FIFA 3-letter code (use --list-teams to see all).
ELO is a positive integer — the team's rating at the start of the tournament.

If the tournament data file is stored as a plain list, it is automatically
upgraded to the {"teamElos": {}, "games": [...]} dict format. Running
build.py after setting all team ELOs will derive homeEloPre/awayEloPre for
every game in that tournament.

--list-teams prints every team's shorthand, full name, and confederation.
"""
import argparse
import json
import sys
from pathlib import Path

import build
from teams import load_teams, list_teams

ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    if len(sys.argv) == 2 and sys.argv[1] == "--list-teams":
        list_teams()
        sys.exit(0)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("year")
    parser.add_argument("team_shorthand")
    parser.add_argument("elo", type=int)
    args = parser.parse_args()

    if args.elo <= 0:
        sys.exit("ELO must be a positive integer.")

    teams = load_teams()
    match = [t for t in teams if t["shorthand"].upper() == args.team_shorthand.upper()]
    if not match:
        sys.exit(f"Unknown team shorthand '{args.team_shorthand}'. Use --list-teams to see valid codes.")
    team_name = match[0]["name"]

    path = ROOT / "data" / f"{args.year}.json"
    if not path.exists():
        sys.exit(f"No data file for year {args.year}.")

    raw = json.load(open(path))

    # Upgrade plain list → dict format
    if isinstance(raw, list):
        data = {"teamElos": {}, "games": raw}
    else:
        data = raw

    data["teamElos"][team_name] = args.elo
    path.write_text(json.dumps(data, indent=2) + "\n")

    print(f"Set {team_name} initial ELO to {args.elo} in {args.year}")
    build.main()


if __name__ == "__main__":
    main()
