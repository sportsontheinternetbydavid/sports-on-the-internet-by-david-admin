# Milestone: Public Launch

Goal: get the project into a state comfortable to share with friends — new infra, consistent branding, no legacy references, organized docs. Not about new features.

Decisions locked:
- Brand name: **Sports! On the Internet. By David**
- Long-lived project info stays in this (admin) repo — no third repo. `operations.md` added for accounts/domain/DNS/hosting. This file (via `workbench/`) is the pattern for tracking future milestones too.
- No legacy ties outside this repo to unwind (no other domains/DNS/services).

## Phase 1 — Repo & infra migration
- [x] Add `site/CNAME` (`sports-on-the-internet-by-david.com`)
- [x] Repoint `origin`/`public` remotes → new org/repos
- [x] Update `deploy.py`'s `PUBLIC_REMOTE` and printed URL → new public repo/domain
- [ ] Push full history to new admin repo — **blocked**: local git credentials are for the old account (`sportsontheworldwideweb`), which has no access to the new repos. Needs `gh auth login` (or one manual push) as `sportsontheinternetbydavid`.
- [ ] Run `deploy.py` against new public repo; confirm CNAME survives
- [ ] Verify GitHub Pages settings (custom domain + HTTPS) on new public repo
- [ ] Verify live domain end-to-end in a browser

## Phase 2 — Remove "World Wide Web" branding
- [x] `way-of-working.md` — two-repo structure table + remotes
- [x] `open-questions.md` — resolve/remove naming question
- [x] `worldcup/requirements-admin.md` — old repo name reference
- [x] `brand.md` — name, domain, email
- [x] Final grep pass for zero remaining hits (outside intentional legacy references in `operations.md`/here)

## Phase 3 — Site branding polish
- [x] `site/index.html`: `<title>`/`<h1>` match finalized name (verified in preview — wraps cleanly at both desktop and mobile widths)
- [x] Favicon: no text/brand name baked in, unaffected
- [x] Spot-checked `brand.md` voice/visual vs. built site — no drift

## Phase 4 — Codebase & doc simplification
- [x] `00-index.md` matches actual files (added `operations.md`, `site/CNAME`, `workbench/` note; renumbered feature docs)
- [x] Confirmed every script in `worldcup/scripts/` is used and documented in `way-of-working.md`
- [x] `.gitignore` sufficient — no untracked junk found beyond `.DS_Store`
- [x] `.claude/settings.local.json` reviewed — globally gitignored, machine-local only, not part of the shared repo; left as-is
- [x] Added `operations.md` (accounts, domain/DNS, hosting)

## Phase 5 — Retire legacy repos/account
- [ ] Confirm new site fully replaces old one in actual use
- [ ] Archive (then delete) old repos under `sportsontheworldwideweb`
- [ ] Decide fate of old GitHub account/email
- [ ] Flag any external bookmarks/links still pointing at old URL

## Phase 6 — Definition of done
- [ ] Real domain serves full site over HTTPS, finalized branding
- [ ] Admin repo is sole source of truth; remotes/deploy.py point at new org
- [ ] Zero "World Wide Web" references anywhere
- [ ] Old repos archived/deleted, old account retired or knowingly kept dormant
- [ ] All docs match reality
- [ ] `workbench/` milestone convention documented in `way-of-working.md`
- [ ] User comfortable sharing the live URL
