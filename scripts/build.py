#!/usr/bin/env python3
"""Regenerate the embedded data blocks in 2018.html / 2022.html / 2026.html
from data/*.json. Run this after editing any data/*.json file by hand,
or use scripts/set_result.py for a one-line score update.

For tournament files that include a top-level "teamElos" key, homeEloPre and
awayEloPre are derived automatically and written back to the JSON before the
HTML is regenerated.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YEARS = [2018, 2022, 2026]


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
            delta = game["eloChange"]
            if home in current and home not in broken:
                current[home] += delta
            if away in current and away not in broken:
                current[away] -= delta
        else:
            broken.add(home)
            broken.add(away)

    return data["games"]


def replace_block(html, name, content):
    """Replace the content between // BEGIN:name and // END:name sentinels."""
    pattern = rf'// BEGIN:{re.escape(name)}\n.*?// END:{re.escape(name)}'
    replacement = f'// BEGIN:{name}\n{content}\n// END:{name}'
    result, n = re.subn(pattern, replacement, html, flags=re.DOTALL)
    if n == 0:
        raise ValueError(f"Sentinel '// BEGIN:{name}' not found in {html[:40]!r}...")
    return result


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    teams = load("teams.json")
    teams_js = "const teams = [\n" + "\n".join(
        '  {"name": %s, "shorthand": %s, "confederation": %s, "flag": %s},'
        % (json.dumps(t["name"]), json.dumps(t["shorthand"]), json.dumps(t["confederation"]), json.dumps(t["flag"]))
        for t in teams
    ) + "\n];"

    for year in YEARS:
        data_path = ROOT / "data" / f"{year}.json"
        data = json.load(open(data_path))

        games = derive_elos(data)

        if isinstance(data, dict):
            data["games"] = games
            data_path.write_text(json.dumps(data, indent=2) + "\n")

        games_js = f"const games{year} = " + json.dumps(games, indent=2) + ";"

        path = ROOT / f"{year}.html"
        html = path.read_text()
        html = replace_block(html, f"games{year}", games_js)
        html = replace_block(html, "teams", teams_js)
        if isinstance(data, dict) and "teamElos" in data:
            team_elos_js = f"const teamElos{year} = " + json.dumps(data["teamElos"], separators=(',', ':')) + ";"
            html = replace_block(html, f"teamElos{year}", team_elos_js)
        path.write_text(html)
        print(f"Updated {year}.html")


if __name__ == "__main__":
    main()
