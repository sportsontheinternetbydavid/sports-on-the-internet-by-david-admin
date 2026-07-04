# Milestone: Public Launch

Goal: get the project into a state comfortable to share with friends — new infra, consistent branding, no legacy references, organized docs. Not about new features.

Decisions locked:
- Brand name: **Sports! On the Internet. By David**
- Long-lived project info stays in this (admin) repo — no third repo. `operations.md` added for accounts/domain/DNS/hosting. This file (via `workbench/`) is the pattern for tracking future milestones too.
- No legacy ties outside this repo to unwind (no other domains/DNS/services).

## Phase 1 — Repo & infra migration
- [ ] Add `site/CNAME` (`sports-on-the-internet-by-david.com`)
- [ ] Repoint `origin` remote → `sportsontheinternetbydavid/sports-on-the-internet-by-david-admin`
- [ ] Update `deploy.py`'s `PUBLIC_REMOTE` and printed URL → new public repo/domain
- [ ] Push full history to new admin repo
- [ ] Run `deploy.py` against new public repo; confirm CNAME survives
- [ ] Verify GitHub Pages settings (custom domain + HTTPS) on new public repo
- [ ] Verify live domain end-to-end in a browser

## Phase 2 — Remove "World Wide Web" branding
- [ ] `way-of-working.md` — two-repo structure table + remotes
- [ ] `open-questions.md` — resolve/remove naming question
- [ ] `worldcup/requirements-admin.md` — old repo name reference
- [ ] `brand.md` — name, domain, email
- [ ] Final grep pass for zero remaining hits

## Phase 3 — Site branding polish
- [ ] `site/index.html` + public pages: `<title>`/headers match finalized name
- [ ] Favicon/meta tags match
- [ ] Spot-check `brand.md` voice/visual vs. built site

## Phase 4 — Codebase & doc simplification
- [ ] `00-index.md` matches actual files
- [ ] Confirm every script in `worldcup/scripts/` is used
- [ ] `.gitignore` covers what it should
- [ ] Trim stale entries in `.claude/settings.local.json`
- [ ] Add `operations.md` (accounts, domain/DNS, hosting)

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
