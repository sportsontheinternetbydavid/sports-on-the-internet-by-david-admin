# Operations

Account inventory, domain/DNS, and hosting facts for the live project. Reference only — not a build doc. Passwords are never stored here; they live on paper at home.

## Domain & hosting

- Public domain: `sports-on-the-internet-by-david.com`
- Registrar & DNS provider: Porkbun
- Hosting: GitHub Pages
- GitHub Pages hostname: `sportsontheinternetbydavid.github.io`

### DNS records

- Apex `A` records (GitHub Pages):
  - `185.199.108.153`
  - `185.199.109.153`
  - `185.199.110.153`
  - `185.199.111.153`
- `CNAME`: `www` → `sportsontheinternetbydavid.github.io`

## Accounts

- **Project Gmail**: `sports.on.the.internet.by.david@gmail.com` — exists specifically for this project; backs the project GitHub account. Password on paper at home.
- **Project GitHub account**: username `sportsontheinternetbydavid`, email `sports.on.the.internet.by.david@gmail.com`. Password on paper at home.
- **Porkbun account**: username `DavidSharpe`. Primary email is the personal email (not the project Gmail); backup email is the project Gmail. Password on paper at home.

## Repositories

- Public: `sportsontheinternetbydavid/sports-on-the-internet-by-david` — GitHub Pages source, custom domain configured via `site/CNAME`.
- Admin (private): `sportsontheinternetbydavid/sports-on-the-internet-by-david-admin` — everything else (see `way-of-working.md` → *Two-repo structure*).

### Push access

Pushing to either repo (directly, or via `worldcup/scripts/deploy.py`) requires whichever machine is doing the push to have git authenticated as the `sportsontheinternetbydavid` account. No token or password is recorded here — only the requirement and how to check it, per `way-of-working.md` → *Local & session state*:
- Check: `gh auth status`
- Switch/add account: `gh auth login`
- Git on macOS typically caches HTTPS credentials via the `osxkeychain` credential helper (`git config credential.helper`), keyed by host (`github.com`) — not by account. Authenticating as a different GitHub account on the same machine replaces the cached credential for anyone using that helper.

## Legacy (to retire)

- **GitHub account**: `sportsontheworldwideweb`, backed by Google account `sportsontheworldwideweb@gmail.com`.
- **GitHub repo**: `sportsontheworldwideweb/sportsontheworldwideweb.github.io` — the only repo that ever existed under this account (no custom domain; served from the default `sportsontheworldwideweb.github.io` hostname). A previously assumed private admin repo (`sportsontheworldwidewebadmin`) was never actually created on GitHub, despite being referenced as existing in older project docs — confirmed via a direct API check.

Retirement status tracked in `workbench/public-launch-milestone.md`.
