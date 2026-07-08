# Way of Working

A tiny project: a couple of requirements docs + an implementation. Keep it that way. This doc is about how we (human + AI) work together — the requirements-doc loop, git rhythm, session/state hygiene. For how the system is actually built (two-repo structure, scripts, the build pipeline, where CSS/JS changes go), see `technical.md`.

There are two requirements docs, for two separate sites — see `00-index.md` for the full doc map:
- [requirements/public.md](requirements/public.md) — the public site (`site/`): the homepage plus every public feature under it, currently just World Cup. No admin/data-entry content of any kind.
- [requirements/admin.md](requirements/admin.md) — the internal admin site for entering results. Not a mirror of the public site.

## The loop

1. **Update requirements** — Human (with AI help) edits the relevant requirements doc to describe a desired change.
2. **Update implementation** — AI reads that doc and updates the corresponding implementation to match it.
3. **Review** — Human opens the implementation in a browser and checks it matches what the doc describes.
4. Repeat.

## Rules of thumb

- Each requirements doc describes *what its site* should do/look like, including scope/structure — that's defined there, not here.
- Each requirements doc is the source of truth for its own site. If the implementation and a requirements doc ever disagree, that's a bug — fix one to match the other.
- Keep the implementation as simple as the requirements docs allow — see `technical.md` → *Shape of the system* for the specific constraints (no npm/bundler/framework, the one build-step exception).
- Never remove working functionality just because a requirements doc says it belongs somewhere else, unless the replacement already exists and works, or the human has explicitly confirmed the interim gap is fine. Rewriting a requirements doc to describe a future split (e.g. "this belongs on a separate admin site now") is not authorization to delete the current implementation before that split is actually built.
- When verifying a CSS transition/animation via the browser preview tool, trust a screenshot over `getComputedStyle`/`getBoundingClientRect` read through `eval`. In practice those reads have gone stale for an element whose classList was mutated by an *earlier* `eval` call in the same session — reporting the pre-mutation style back with no error — while the actual rendered frame (and a fresh screenshot of it) was correct. A screenshot goes through the real render pipeline; a follow-up `eval` read of computed style doesn't reliably do the same in this environment.

## Git

- Commit before running `worldcup/scripts/set_result.py` or editing data files by hand. `build.py` writes directly to the HTML pages; a clean working tree is your only rollback if something goes wrong.
- Normal commit rhythm: one commit per session, or one per result batch if entering several games at once.

## Local & session state

Nothing this project needs should live *only* outside version control. Two specific cases:

**Setup dependencies** — if a workflow step needs specific local machine setup to work, that dependency must be named somewhere in this repo, not just assumed or discovered by hitting an error. Currently just one: git authentication for pushing (either remote, or via `worldcup/scripts/deploy.py`) — see `operations.md` → *Push access* for the required account and how to check/switch it.

**Ephemeral working artifacts** — AI tooling creates files outside this repo while working (plan-mode plan files, scratch/temp directories used to clone or inspect something, etc.). These are disposable by design: fine to use mid-session, expected to be discardable by the end of it. Anything that needs to survive past the session — a decision, a checklist, a doc update — must be written into this repo (typically `workbench/<milestone-name>.md` for in-flight plans, or the relevant root doc for a settled decision) before the session ends. Never leave a durable outcome resting only in a tool-managed file the project doesn't own.

See `technical.md` → *Architecture boundary* for the related rule about this repo not depending on anything outside itself.

## Milestones

Work that spans multiple sessions (a rebrand, an infra migration, anything bigger than one loop of *The loop* above) is tracked as a checklist in `workbench/<milestone-name>.md`. Check items off as they land. When the milestone is done, delete the file — git history keeps the record, and the outcome belongs in the commit message, not a changelog doc.
