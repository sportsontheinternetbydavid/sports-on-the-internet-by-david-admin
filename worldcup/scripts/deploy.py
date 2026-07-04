#!/usr/bin/env python3
"""Push the built site/ folder to the public GitHub Pages repo.

Usage: python worldcup/scripts/deploy.py [-m "commit message"]
"""

import argparse
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # repo root — site/ lives here, not under worldcup/
SITE = PROJECT_ROOT / "site"
PUBLIC_REMOTE = "https://github.com/sportsontheworldwideweb/sportsontheworldwideweb.github.io.git"


def run(cmd, **kwargs):
    result = subprocess.run(cmd, check=True, **kwargs)
    return result


def main():
    parser = argparse.ArgumentParser(description="Deploy site/ to the public GitHub Pages repo.")
    parser.add_argument("-m", "--message", default="Deploy", help="Commit message")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without pushing")
    args = parser.parse_args()

    if not SITE.exists():
        print("ERROR: site/ folder not found. Run worldcup/scripts/build.py first.")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Clone the public repo (shallow)
        print(f"Cloning public repo...")
        run(["git", "clone", "--depth=1", PUBLIC_REMOTE, str(tmp)])

        # Wipe everything except .git
        for item in tmp.iterdir():
            if item.name == ".git":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        # Copy site/ contents into the clone root
        shutil.copytree(SITE, tmp, dirs_exist_ok=True)

        # Stage all changes
        run(["git", "-C", str(tmp), "add", "-A"])

        # Check if there's anything to commit
        status = subprocess.run(
            ["git", "-C", str(tmp), "status", "--porcelain"],
            capture_output=True, text=True
        )
        if not status.stdout.strip():
            print("Nothing to deploy — public repo is already up to date.")
            return

        print(status.stdout)

        if args.dry_run:
            print("DRY RUN — not pushing.")
            return

        run(["git", "-C", str(tmp), "commit", "-m", args.message])
        print("Pushing to public repo...")
        run(["git", "-C", str(tmp), "push"])
        print("Done. Site is live at https://sportsontheworldwideweb.github.io/")


if __name__ == "__main__":
    main()
