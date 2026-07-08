"""Shared team-lookup helpers — not a script itself, imported by
set_result.py, set_team_elo.py, and set_bracket_game.py. See
../data/teams.json for the data these read.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_teams():
    return json.load(open(ROOT / "data" / "teams.json"))


def list_teams():
    teams = load_teams()
    width = max(len(t["name"]) for t in teams)
    for t in sorted(teams, key=lambda t: t["name"]):
        print(f"{t['shorthand']}  {t['name']:<{width}}  {t['confederation']}")


def resolve_team(shorthand, teams):
    match = [t for t in teams if t["shorthand"].upper() == shorthand.upper()]
    if not match:
        sys.exit(f"Unknown team shorthand '{shorthand}'. Use set_result.py --list-teams to see valid codes.")
    return match[0]["name"]
