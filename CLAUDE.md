# Working on this project

Start at [00-index.md](00-index.md) — the map of every doc in this project and what each one is responsible for.

[way-of-working.md](way-of-working.md) is the one to read first: it's the human+AI operating process — the requirements-doc-driven loop, git rhythm, and the milestone-tracking convention (`workbench/`). [technical.md](technical.md) is the architecture reference alongside it: the two-repo structure, every script's job, the build pipeline, and where CSS/JS/markup changes go. Anything durable learned while working on this project — a gotcha, a rule, a correction — belongs in a doc in this repo (this file, `way-of-working.md`, `technical.md`, or the relevant feature doc), not in AI-tool-side memory outside the repo. See `way-of-working.md` → *Local & session state* for why.

**Before editing `worldcup/nav.css`, `worldcup/shared.css`, or `worldcup/shared.js`, or previewing anything under `site/`/`admin/`, read `technical.md` → *Shape of the system* and *Where CSS and JS changes go*.** Every page under `site/` and `admin/` is a build artifact with these files' contents inlined at build time — nothing there links to the source files at runtime. Editing a source file has zero visible effect until `python3 worldcup/scripts/build.py` is run; verifying against a stale `site/` page will look identical to no change at all having been made.
