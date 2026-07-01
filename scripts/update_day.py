#!/usr/bin/env python3
"""Update all results for a given day (default: yesterday) in one command.

Usage:
  scripts/update_day.py SCORE [SCORE ...]
  scripts/update_day.py --date YYYY-MM-DD SCORE [SCORE ...]
  scripts/update_day.py --list [--date YYYY-MM-DD]

SCORE format: HOME-AWAY  (e.g. 2-1, 0-0, 1-3)

Games are matched in chronological order (by gameNumber) for that date.
You must supply one score per game on that day, or fewer to partially update
(the first N games in order will be updated).

After updating the data and rebuilding the HTML, the script commits and
pushes the changes to the private admin repo (`origin`), then deploys the
rebuilt site/ to the public GitHub Pages repo (equivalent to running
scripts/deploy.py). Pass --no-push to skip both and only update local files.

Examples:
  # Update yesterday's 6 games:
  python scripts/update_day.py 2-1 0-0 1-3 2-0 1-0 3-2

  # List today's games without updating:
  python scripts/update_day.py --list

  # Update a specific date:
  python scripts/update_day.py --date 2026-06-24 3-0 1-1 2-0 4-1 0-2 1-0

  # Update without touching git (local files only):
  python scripts/update_day.py --no-push 2-1 0-0

ELO changes are not set by this script — use set_result.py afterwards if needed.
"""
import argparse
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import build

ROOT = Path(__file__).resolve().parent.parent
YEAR = 2026  # active tournament year


def load_data():
    path = ROOT / "data" / f"{YEAR}.json"
    data = json.load(open(path))
    return path, data


def games_for_date(games, target_date):
    return sorted(
        [g for g in games if g.get("date") == target_date],
        key=lambda g: g["gameNumber"],
    )


def parse_score(s):
    parts = s.split("-")
    if len(parts) != 2:
        sys.exit(f"Invalid score '{s}' — expected HOME-AWAY, e.g. 2-1")
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        sys.exit(f"Invalid score '{s}' — scores must be integers")


def push_to_github(target_date, scores):
    message = f"Data: {YEAR} results — {target_date}"

    print("\nCommitting and pushing to admin repo...")
    subprocess.run(["git", "-C", str(ROOT), "add", "data", "site"], check=True)
    status = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain", "--", "data", "site"],
        capture_output=True, text=True, check=True,
    )
    if not status.stdout.strip():
        print("Nothing to commit — admin repo already up to date.")
    else:
        subprocess.run(["git", "-C", str(ROOT), "commit", "-m", message], check=True)
        subprocess.run(["git", "-C", str(ROOT), "push", "origin"], check=True)

    print("\nDeploying to public site...")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "deploy.py"), "-m", message],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=None, help="Date to update (YYYY-MM-DD). Defaults to yesterday.")
    parser.add_argument("--list", action="store_true", help="List games for the date without updating.")
    parser.add_argument("--no-push", action="store_true", help="Update local files only — skip the admin-repo commit/push and public deploy.")
    parser.add_argument("scores", nargs="*", help="Scores in HOME-AWAY format, one per game in order.")
    args = parser.parse_args()

    target_date = args.date or str(date.today() - timedelta(days=1))

    path, data = load_data()
    games = data["games"] if isinstance(data, dict) else data
    day_games = games_for_date(games, target_date)

    if not day_games:
        sys.exit(f"No games found for {target_date} in {YEAR}.json")

    if args.list or not args.scores:
        print(f"\nGames on {target_date}:")
        for g in day_games:
            score = f"{g['homeScore']}-{g['awayScore']}" if g.get('homeScore') is not None else "TBD"
            print(f"  #{g['gameNumber']:>2}  {g['homeTeam']} vs {g['awayTeam']}  =>  {score}")
        if not args.scores:
            print("\nPass scores as arguments to update, e.g.:")
            example = " ".join("X-X" for _ in day_games)
            print(f"  python scripts/update_day.py {example}")
        return

    if len(args.scores) > len(day_games):
        sys.exit(f"{len(args.scores)} scores given but only {len(day_games)} games on {target_date}")

    scores = [parse_score(s) for s in args.scores]

    # Update the games list in-place
    game_by_num = {g["gameNumber"]: g for g in games}
    for game, (home_score, away_score) in zip(day_games, scores):
        g = game_by_num[game["gameNumber"]]
        g["homeScore"] = home_score
        g["awayScore"] = away_score
        print(f"  #{g['gameNumber']:>2}  {g['homeTeam']} {home_score}-{away_score} {g['awayTeam']}")

    if isinstance(data, dict):
        data["games"] = games
        path.write_text(json.dumps(data, indent=2) + "\n")
    else:
        path.write_text(json.dumps(games, indent=2) + "\n")

    print(f"\nUpdated {len(scores)} game(s) in {path.name}. Rebuilding HTML...")
    build.main()

    if args.no_push:
        print("Done (--no-push: skipped commit/push/deploy).")
    else:
        push_to_github(target_date, scores)
        print("Done.")


if __name__ == "__main__":
    main()
