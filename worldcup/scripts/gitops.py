"""Shared helper for scripts that commit data/HTML changes and publish them.

Commits data/, site/, and admin/ to the admin repo (origin), then runs
deploy.py to push the rebuilt site/ to the public GitHub Pages repo. Used by
update_day.py, set_result.py, set_knockout_size.py, and set_bracket_game.py
after they write a result and rebuild the HTML.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # worldcup/
PROJECT_ROOT = ROOT.parent  # repo root — site/ lives here, not under worldcup/


def push_to_github(message):
    print("\nCommitting and pushing to admin repo...")
    subprocess.run(["git", "-C", str(PROJECT_ROOT), "add", "worldcup/data", "site", "admin"], check=True)
    status = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT), "status", "--porcelain", "--", "worldcup/data", "site", "admin"],
        capture_output=True, text=True, check=True,
    )
    if not status.stdout.strip():
        print("Nothing to commit — admin repo already up to date.")
    else:
        subprocess.run(["git", "-C", str(PROJECT_ROOT), "commit", "-m", message], check=True)
        subprocess.run(["git", "-C", str(PROJECT_ROOT), "push", "origin"], check=True)

    print("\nDeploying to public site...")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "deploy.py"), "-m", message],
        check=True,
    )
