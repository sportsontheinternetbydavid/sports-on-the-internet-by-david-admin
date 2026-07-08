# Requirements — Public Site

What the public-facing "Sports! On the Internet. By David" site should do/look like — the read-only site anyone can visit. Covers the whole public site: the homepage and every public feature under it (currently just World Cup). It has **no admin mode, no data-entry UI, no `?admin` param, no mode toggle of any kind**, anywhere on this site. All of that lives in a completely separate site, documented in `admin.md` in this same folder. The two are not mirrors of each other — the admin site is a purpose-built internal tool, not "this site plus a toggle."

See `../00-index.md` for how this doc relates to `admin.md` and the rest of the project's docs.

---

## Homepage (`site/index.html`)

The homepage is the entry point into the whole site and the top of its navigation hierarchy — Level 1 of the shared nav (see *Navigation* below) starts here, not on a per-feature page. It reflects the brand: kids art room, construction paper and markers, handmade and enthusiastic.

### Layout
- Full-width page. The nav (see *Navigation* below — up to **four** levels here, one more than any other page) sits flush against the very top of the viewport — no top border, no top margin — same as every other page on the site.
- Background cream `#F5F0E8`, carrying through below the nav.
- No cards, no "Coming Soon" badges. Every sport/competition/section choice is made through the nav itself — a disabled nav item (see *Navigation*) is what a "coming soon" sport looks like now.
- No separate content area below the nav. The site's signature (name + tagline) used to live in its own header block here; it's now folded into the nav itself (see *Navigation* → `Sports!` below) — the nav *is* the page.

### Navigation
Uses the same `.page-nav` component and general characteristics described in *Navigation* below — this page doesn't get its own visual variant, only its own content per level. Like every other page, it has no Level 4 (see the general Level table in *Navigation* below) — just Levels 1 through 3.

- **Level 1 — Sport**: four chips — `Sports!`, `Football`, `Hockey`, `Swimming`. `Sports!` and `Football` are both real, selectable items: a single-choice, client-side toggle (no page reload) that controls what Levels 2 and 3 show below, using the fly in/out transition described in *Navigation* → *Transitions*. `Hockey` and `Swimming` render as disabled items — muted, no hover, not a link, the same treatment `WC 30` gets on tournament pages (see *World Cup pages* below). There is no Basketball item.
- **`Sports!` (default/landing state)** — Levels 2 and 3 become the site's signature, one line per level, replacing the old separate header block entirely. This is the one place on the site where the *Navigation* → *The homepage signature is exempt* rule applies — no chip styling, just handwritten/printed text directly on the page:
  - **Level 2**: `On the Internet.` — the largest line, in the brand red.
  - **Level 3**: `By David` — smaller, one level down in visual weight.
- **`Football`** — Levels 2 and 3 switch to the tournament content below:
  - **Level 2 — Competition**: one segment per major football tournament — `World Cup`, `Euros`, `Copa América`, `Gold Cup`. `World Cup` is the only active (linkable) item; the other three render as disabled, same treatment as `Hockey`/`Swimming` above — they're the next posters waiting to be made, not a second live competition yet.
  - **Level 3 — Section**: two equal segments, `History` and `Tournaments`. `History` links directly to `history.html`. `Tournaments` links to the current/latest tournament page (`2026.html` today) — from there, that page's own Level 1 (see *World Cup pages* below) is how you reach any other year.
- **Transition:** board — nothing shared between the two states; `Sports!`'s Levels 2/3 and `Football`'s Levels 2/3 are two independent chip sets with no structure in common (Level 1 above is the one thing that never moves, in either state). Item — one chip in `Football`'s state; the whole `Sports!` signature is the one exception, moving as a single typographic composition rather than a set of chips (see *The homepage signature is exempt*). How — both sets stay permanently in the DOM, stacked and swapping in parallel (see *Transitions* → *Implementation note*); each chip flies the standard horizontal conveyor, out right/in left, individually staggered.
- **On load:** matches the sitewide default (see *Initial display*) — `Sports!` is already there in its resting position; it never flies in. `Football`'s chip set is already present in the DOM but parked off-screen at rest (not merely hidden), so its *first* activation still gets the normal Transition treatment above rather than needing special-cased handling.

### Typography
- Headlines and labels: Permanent Marker (Google Fonts) — marker-written feel.
- Body / links: Fredoka One (Google Fonts) — rounded, friendly, legible.

### Colors
- Page background: cream `#F5F0E8`.
- Text: near-black `#1a1a1a`.
- Nav colors follow *Navigation*'s general characteristics below (red `#C0392B`, etc.) — no separate palette for this page.
- No clean web-safe primaries. Colors come from the construction paper palette in `../brand-guidelines.md`.

---

## Navigation

**Style: "sticky notes."** Reused everywhere nav appears on the public site — the homepage, every World Cup page, and (with fewer levels) `history.html`. This section is the shared vocabulary and shared visual rulebook; each page's own section (*Homepage* above, *World Cup pages* below) says what specifically populates each level there.

This replaced an earlier "fused bar" style — one continuous red background block with every level squared flush against the next. That style read as too clean/corporate for the brand (see `../brand-guidelines.md`) and has been fully replaced, not layered on top of. There is no longer a shared continuous background of any kind behind Levels 1–3.

The nav is organized into up to four stacked **levels** — the standard vocabulary for the rest of this doc, used consistently rather than switching between "row," "tier," "bar," etc.:

| Level | What it is |
|-------|------------|
| **Level 1** | Top-level choice: which section of the site am I in |
| **Level 2** | Next choice down, within Level 1's selection |
| **Level 3** | Detail controls for the current Level 1/2 selection |
| **Level 4** | Column headers for the data below — only present on pages with a table/grid (World Cup pages); the homepage has none |

Levels 1–3 sit inside one wrapper (`<div class="page-nav">`) that spans the page's full content width (the same max width the rest of the page uses, `body`'s `max-width: 1100px` minus padding — not shrink-to-fit), but the wrapper itself is invisible — no background, no border, no shared corner radius. Each level is its own loosely-wrapping row of independent items with a small gap between rows (~10px). No page has a top border or top margin above the nav — it sits flush against the very top of the viewport everywhere it appears, including the homepage.

Level 4, where it exists, is **not** part of `.page-nav` — it belongs to each view's own table/grid, since its exact markup necessarily differs per view (an HTML `<thead>` for Match List, a CSS grid header for Rankings, per-column round labels for Knockout). It picks up the same paper material language as Levels 1–3 — a soft drop shadow lifting it off the page, and a rough/torn top edge instead of a crisp rectangular corner — but adapted for what it structurally is: one continuous, column-aligned row, not a set of independent chips. No per-item rotation and no gaps between columns — either would misalign it with the data below, which is the one hard constraint chips don't have to respect. It stays red `#C0392B` with white Permanent Marker text, sitting just below Level 3 with a small gap (not fused flush — Level 3 no longer has a continuous edge to fuse against), and **never wider than the nav above it** — if a view's columns would naturally need more width (e.g. Match List with many confederation columns), the table/grid caps at the nav's width and scrolls horizontally within that bound, rather than the page growing wider than the nav. See *World Cup pages* below for where Level 4 actually appears.

### General nav chip characteristics (Levels 1–3)

These rules are the shared design system for every nav level on the site — Level 1, Level 2 (including History's Final 4/8/16), and every Level 3 variant. Any nav control should follow all of them unless a specific section says otherwise.

- **Shape, not a bar**: each item is its own small paper cutout, not a segment of a shared background (see *Material* below for the cutout's actual shape/shadow), plus a small independent rotation (roughly ±1–2°). Rotation is deterministic per item (alternating by position), not random per page load — same principle as the flag rotation in *World Cup pages* → *Flags* below.
- **Layout**: items size to their own label's natural width (no stretch-to-fill) and wrap onto additional lines as needed, with a small gap (~8–10px) between items in both directions. A row is left-aligned; it does not spread items to fill the full content width.
- **Font**: Permanent Marker, on every item in every level — buttons and plain links alike. It's all navigation; it should read as one family regardless of the underlying HTML element.
- **Size — two tiers, not one**:
  - Level 2, on any page (the homepage's `World Cup` segment, World Cup pages' primary tabs): `0.95rem` font, `0.45rem 1.1rem` padding — the single most visually dominant level, wherever it appears. Dominance comes from size alone — it shares the same color system as every other level (below) rather than a special always-red default.
  - Every other level (Level 1, and every Level 3 variant, on any page): `0.75rem` font, `0.2rem 0.7rem` padding. Smaller and lighter, signaling "secondary to Level 2."
- **Material — irregular cut + visible thickness**: each chip's outline is an irregular hand-cut polygon (cycling through 4 distinct shapes by position — no two neighboring chips share the same corner cuts), not a uniform rounded rectangle. The shadow is a hard, unblurred offset, reading as a thick physical edge (poster board) rather than a thin sheet floating above the page.
- **Color — paper color variety, always black text**: chips are not uniformly one color — each one draws from the construction paper palette (`../brand-guidelines.md`: red, blue, yellow, green, orange, plus a cream default), assigned deterministically by position (cycling independently from the shape cycle above, so color and cut don't repeat in lockstep), so a row reads as several different sheets pulled from the stack rather than one repeated color. Text is always dark/near-black regardless of the chip's paper color — real marker only comes in black, so a colored background never gets white/light text. Disabled chips are the one exception to the color variety (see below) — they stay a fixed muted gray-tan regardless of position, so "not available yet" is never mistaken for a color choice.
- **Tape on every chip**: every chip — default, selected, and disabled alike — has a piece of masking tape holding it down, since a real piece of board needs it regardless of whether it's the current selection. Tape size and angle vary by position, the same way the cut shape and paper color do — its own deterministic cycle, using a different cycle length than the shape (4) and color (5) cycles so tape variety never repeats in lockstep with either. A row of chips should never look like it reused one identical strip of tape.
- **Selected**: no color change — a chip's paper color stays whatever it already was. Selection is shown instead by a stronger shadow and a slight scale-up (visibly picked up and pressed down) — tape stays exactly the size/angle it already was, never resized for selection, since real tape doesn't grow because the thing under it got picked up. This is the one look for what used to be two separate states — single-choice "current selection" and multi-select "shown" (a currently-visible Knockout round) both get it, since both mean "this is on."
- **Independent on/off toggles** (Show eliminated, True rank, the debug toggle, and each Knockout round chip): unlike tabs, these aren't one choice from a mutually-exclusive set — each is its own switch, and more than one can be on at once. They get the same chip + Selected treatment as above, plus one more cue on top: a small dot sticker in the chip's corner, muted gray when off and brand green when on — so a row of independent switches reads as on/off at a glance rather than as a multiple-choice picker.
- **Disabled**: a muted gray-tan paper chip (fixed, not part of the color cycle), dimmed near-black text, minimal/flatter shadow than a live chip, no hover response, not a link. Still gets the same cut and tape treatment as every other chip. Used for an item with no destination yet (the homepage's `Hockey`/`Swimming`, `WC 30` on tournament pages) and the Groups placeholder note.
- **Hover**: no hover effect. A clickable chip doesn't lift, shift, or shadow-change on hover — tried as a translateY lift and then as a tape-anchored peel/hinge, both rejected (see `way-of-working.md` history): a lift reads as the chip floating off the board (`brand-guidelines.md` → *Layout* → "nothing floats"), and a peel would require the tape to visually stay put while the paper tilts under it — impossible while the tape is a `::before` of the same element, since a pseudo-element rotates rigidly with its parent. Fixing that needs the tape rendered as an independent sibling anchor, which is a shared-component restructuring this doc doesn't call for. Disabled chips likewise never respond to hover, same as every other chip.
- **No dividers, no shared corners**: nothing ties adjacent chips together visually except the gap between them — no border, no divider line, no shared cut/corner scheme. Each chip is shaped independently regardless of what's next to it or which level it's in.

### The homepage signature is exempt

The homepage's `Sports!` state (`On the Internet.` / `By David` / the tagline — see *Homepage* → *Navigation* above) is the site's byline, not a choice, so it does **not** get the chip treatment at all: no fill, no shadow, no tape, no rotation. It's plain handwritten/printed text sitting directly on the page background, sized down in visual weight level by level (large marker headline → smaller marker line → small italic printed caption). Only the real choices — Level 1's sport picker, and `Football`'s Level 2/3 — use chips.

### Transitions (fly in/out)

**Hard requirement, not a stylistic preference: every feature section in this document that has anything appear or disappear on screen must state, explicitly and in that feature's own section, two things:**
1. **Transition** — what stays (the board), what goes (the item), and how it moves (direction/mechanism), for any change that happens *after* the page has already loaded — even when the answer is "nothing flies, it's instant."
2. **On load** — not a description of what's shown first or what it looks like (that's specified elsewhere in the same section, e.g. "Final 16 is the default"). It answers one narrow question only: does this feature's default state *animate* into view, or *was it already there* — already assembled, already pinned up — before the page ever opened? Nothing "appears": either something moves into place (animation), or it was never absent to begin with. An arrival-mechanism question, not a content/appearance one — see *Initial display (on load)* below for the sitewide default (answer: always already there, never animated) every feature starts from.

A feature section that adds a toggle, a view switch, or any other appearing/disappearing content without both of these is an incomplete requirements doc, not a finished one — the same way a feature missing its data model or its layout would be. Look for the bolded **Transition:** and **On load:** lines in each feature's own section below; that's where its specific answers live. This exists because guessing the unit by analogy to another feature is exactly how a past mistake happened: an early pass animated a whole History table row instead of just its individual flags, reasoning wrongly from Match List's row-is-the-item case. Getting this wrong reads as a real bug on screen (the wrong thing visibly flies, or flies when it shouldn't have loaded that way at all), not just a documentation gap — so it's enforced here, in the requirements themselves, rather than left as a process reminder elsewhere.

Every appearance/disappearance on this site follows one mental model — see `brand-guidelines.md` → *Motion* → *The invisible hands*: someone standing at the poster board, taking individual items down and pinning new ones up, one at a time. They never pick up the whole board unless the board itself is what's changing.

An item's own selected/active look is never a reason it sits out its own fly — the currently-selected tab flies with everything else when its view is what's leaving, and the arriving page's default-selected tab flies in with everything else on arrival, exactly the same as a non-selected chip. (See `technical.md` → *A resting-state rule must never outrank a fly-transition rule* for the implementation discipline this requires.)

**The unit that moves, by action.** The shared vocabulary and shared answer key every feature's own **Transition:** line points back to:

| Action | The board (never moves) | The item (flies individually) |
|--------|--------------------------|--------------------------------|
| Homepage `Sports!` ↔ `Football` | Nothing shared — two independent chip sets, no structure between them | One chip. (The `Sports!` signature is the one exception — see *The homepage signature is exempt* — it's one typographic composition, not a collection of chips, so it moves as a single piece.) |
| World Cup page Level 2 switch (Match List/Groups/Knockout/Rankings) | Nothing shared between outgoing/incoming — a table, a bracket, a flag grid share no structure, so the whole outgoing board exits as one piece and a new one flies in to replace it | Each of the outgoing/incoming view's own rows/cards — see that view's own row in this table |
| Match List's confederation panel (ELO Shift/W-D-L/Stats) | The confederation column headers (names) + the fixed game columns | Each confederation's cell **value**, one per row |
| Knockout's round toggle | Nothing — a round's column has its own fixed horizontal slot that never shifts (see *Knockout Bracket* → *Round toggles*) | Each game card within the round being shown/hidden |
| History's F4/F8/F16 tier toggle | The table itself: header row, the year column/labels, every row's position, the 16-column width | Each flag+ELO cell's **content** within a row — not the row itself, which never moves (see *History page* → *Table structure*) |
| Any cross-page link (`Home`, `WC YY`, `Tournaments`, `History`) | None — two separate documents share no board to speak of (see *Cross-page navigation* below); structural chrome common to both (the cream background, a table's frame/axis, the red Level 4 strip) simply doesn't move, the same as it never moves within a single page | Every in-frame nav chip at every level, plus every in-frame piece of whichever view is showing, each individually — Match List is the one exception to its own row-level grain above (see *Cross-page navigation*'s note on why); every other view already flies at its finest grain (a game card, a Rankings flag, a History flag cell) |

**The test for "board" vs. "item"**, when adding a new one: does this piece only make sense as part of the whole record around it, or is it independently meaningful on its own? A Match List row is one game — every cell in it describes that same one game, so the row is the item, not each cell. A History row, by contrast, holds several teams' entries side by side — each flag is its own independent fact (that team's ranking), unrelated to its row-mates except by coincidence of sharing a year, so the *flag* is the item and the row (and the year identifying it) is part of the board. Get this test wrong and the wrong thing ends up flying — a whole row lifting away when only its contents changed reads as the year itself being replaced, which it never was.

**A nav bar never passes this test as a board, at any level, on any page** — see `../brand-guidelines.md` → *Motion* → *The board stays on the wall* for why: a board is one physical surface (a table's frame, an axis, a bracket's trellis), and a nav bar is a row of independently cut-out chips (see *General nav chip characteristics* → *Material* above), never a surface, however many chips it has and however new they are to the screen. Every chip in it is always an item, flying individually. This is what makes the whole-page slide the old cross-document view-transition implementation used (see *Cross-page navigation* below) wrong — a nav bar and a full table arriving as one pre-assembled image reads as a component being dropped in, not as pieces being placed.

**Direction: the same horizontal conveyor as a board-level swap** — out fully off-screen to the right, in from the left — just faster (see *Item pace* below), for every item in the table above except one. **Knockout's game cards are the one exception**, moving vertically instead: a round's game cards belong to a column that has its own fixed horizontal slot (see *Knockout Bracket* → *Round toggles*) and must never shift sideways, so there's nowhere horizontal for a card to fly to — it lifts up and off, or drops down into place, within that same fixed column instead.

**Structural chrome — table headers, an axis column, a bracket's connector lines, a year label — never moves.** It's the board, not an item pinned to it, so it stays exactly where it is while the items on it fly out and new ones fly in.

**Chrome only moves when the chrome itself is what's changing** — switching between Match List/Groups/Knockout/Rankings, whose boards (a table, a bracket, a flag grid) share nothing with each other. There, the outgoing board exits **fully off-screen** to the right, rotating slightly, as one piece (it's a single fixture, not a collection of independent items) — while, alongside it, the outgoing view's own individual items (its rows/cards) fly out too, each on its own. The new board then flies in, entering from the **left**, rotating back to flat as it settles, and its own items fly in individually behind it. This is a one-way conveyor, not the incoming board retracing the outgoing one's path — an earlier version used a modest nearby shift instead for panels living inside a horizontally-scrollable width-bound area, but production feedback said that read as barely moving, not "flying in," so a board-level exit always goes fully off-screen. Paired with a scroll lock on whatever scrollable ancestor it lives inside (a `.table-wrap`, a bracket's own scroll area, the page itself) for exactly the transition's duration — long enough to keep an off-screen fly from briefly corrupting that ancestor's scrollable width, short enough that scrolling works normally again the moment it settles.

- **Item pace — quick, around 420ms, same distance as the board-level pace below**: fully off-screen, out to the right and in from the left, the same one-way conveyor as a board-level swap — not a token nearby nudge. An early pass tried a short ~16px lift instead, and it read as barely moving/glitchy rather than "picked up," the exact lesson the board-level pace already learned once (see below) — a small shift doesn't read as flying at either scale. What actually differs between item and board scale is speed, not distance: a small light item is quicker for the invisible hand to move than a whole board.
- **Item pace numbers are still first estimates**, expected to need the same kind of tuning the panel pace below got.
- **Stagger — random jitter, not a fixed per-item delay**: each item's start is offset by a small random amount within a fixed window (around 250ms), not a strict per-item increment. A swap of 5 items and a swap of 100 items both finish in roughly the same total time (~350ms plus the jitter window) — a fast pair of hands working through a stack, not an assembly line that gets slower the longer the stack is. This replaces every fixed per-index stagger this site used to have (the old ~0.2s-per-row homepage pacing, Knockout's old 90ms-per-column reveal).
- **Chrome pace — ~0.85s**, unchanged from before — a board-level swap is still the same kind of big single-piece move it always was. Piloted on the homepage first (production feedback called an earlier, much faster pacing too quick to read as physical paper sliding) and promoted as the universal pace for this specific case.
- **Never an opacity fade, at either scale**: a board and an item both stay fully opaque throughout; they leave and enter by moving, the way physical paper and index cards actually do (see `brand-guidelines.md` → *Motion*).
- **Settling clears the transform**: once anything finishes flying in — board or item — its fly styles/classes are removed entirely rather than left at a resting `transform: translateX(0)` (or `translateY(0)`) — an identity transform still creates a new containing block, which would silently break any `position: fixed` descendant (Rankings' flag info panel is why this matters — see *Flag info panel*). A board-level scroll lock is released at the same moment.
- **Scope**: this is the site's default for any control that **replaces** content with different content:
  - The homepage `Sports!` ↔ `Football` switch, and a World Cup page's Level 2 tab switch (Match List/Groups/Knockout/Rankings) — a board-level swap (see above), each side's individual items flying alongside it.
  - Match List's confederation panel toggle (ELO Shift / W-D-L / Stats) — see *Confederation panel* below. Board stays; cells swap.
  - Knockout's round toggle — see *Knockout Bracket* → *Round toggles*. No board to speak of; each hidden/revealed round's game cards fly individually.
  - History's F4/F8/F16 tier toggle — see *History page*. Board stays; rows swap.
  - Any cross-page link (`Home`, `WC YY`, `Tournaments`, `History`) — see *Cross-page navigation* below. No board; every nav chip and every row/card on both the outgoing and incoming page flies individually.

  It does **not** apply to Rankings' **Show eliminated**, **True rank**, or **Rank**/**Scale** toggles. Those don't make anything appear or disappear — they reposition individual flags already on screen, within a layout that must not otherwise shift (see *Rankings shared layout* and each toggle's own section). Repositioning-in-place is a different animation question from flying in/out, and remains not-yet-designed, so for now they stay an instant in-place update.
- **Implementation note (homepage only)**: the homepage keeps both `Sports!`/`Football` item sets permanently in the DOM, stacked and swapping in parallel, rather than sequentially — cheap since it's just a couple of nav rows' worth of chips. They must be taken out of normal document flow and stacked in the same position (both `position: absolute` inside a `position: relative` wrapper, sized explicitly to whichever set is currently active) rather than left as normal-flow siblings — two normal-flow siblings both present mid-swap push each other's vertical position around, and whichever is later in the DOM visibly pops into place once the other is removed. Everywhere else, the swap is sequential instead: the outgoing board/items fly out, *then* the incoming board is rendered and its items fly in.

### Initial display (on load)

**The sitewide default: nothing flies in on load, ever — because nothing "arrives" on load at all.** See `brand-guidelines.md` → *Motion* → *Nothing appears from nothing*: a poster doesn't flicker into existence when someone looks at it, it was already taped to the wall. Opening a page is walking into the room, not watching the room get built. Whatever a page shows by default — its default view, its default toggle states — was already there, already assembled, already pinned up, before the page was ever opened. It does not fly in, fade in, or animate into being in any way, because there is no moment of it *coming into being* for an animation to depict — it simply already was. This is a deliberate requirement, not just "we haven't built the entrance animation yet": animating something into place on load would claim it was just now being assembled, and it wasn't. The invisible hands (see *The invisible hands*) had already finished before anyone arrived; there's nothing left for them to do at the moment of arrival, so nothing moves.

This holds **regardless of how the page was reached** — including a direct link or reload landing on a non-default state via URL hash (e.g. loading `2026.html#knockout` directly, or `history.html` with a future deep-linkable round). Whichever view/state is shown first was already the resting state, exactly as if it had always been that way — never a "switch into it" the way a same-session click would trigger. A page load has no "before" state for a transition to depict, because a transition needs two states and a page load only ever has one: the one already there.

Content belonging to a **non-default** state that isn't shown on load (e.g. the homepage's `Football` chips while `Sports!` is showing, or a World Cup page's Groups/Knockout/Rankings views while Match List is showing) simply isn't part of what's on the wall yet — parked off-screen or absent from the DOM entirely, per that feature's own implementation — so that the *first* switch to it, later, still gets the normal Transition treatment described above (that later switch is a real change with a real "before," which on load there isn't). Only the state already on screen at load is exempt from flying in; nothing about a later switch into a different state is exempt from anything.

Every feature's own **On load:** line (alongside its **Transition:** line) confirms this default applies, or calls out the specific exception if one genuinely exists.

### Cross-page navigation

Every link that leaves the current page for a different HTML document — `Home`, any `WC YY`, `Tournaments`, `History` — is a real browser navigation, not a client-side swap: there's no shared DOM for the fly in/out mechanics above to act on, and no shared board either (see `../brand-guidelines.md` → *Motion* → *The board stays on the wall* — a nav bar or a table full of rows never qualifies as one, no matter how big or how new to the screen). This site is still one motion system regardless (see `../brand-guidelines.md` → *Motion* → *Walking to a different poster*): every visible piece on the page being left flies out individually, staggered, the same item-level treatment used everywhere else on the site; every visible piece on the destination page flies in the same way once it's reached. Structural chrome shared in kind across every page (the cream background, a table's frame lines and axis, the red Level 4 header strip) never moves — it's simply present on both ends, the same as it is within a single page.

**Scoped to what's actually in frame.** Only pieces within the viewport at the moment of leaving/arriving fly — nothing below the fold (a Match List can run 50+ rows deep) animates just because it exists somewhere on the page. Content outside the viewport is simply present, unanimated, whenever the reader scrolls to it; this is the same *Nothing appears from nothing* default every off-screen, not-yet-seen thing on this site already gets, not a special case invented for this feature.

**The item, for a row-based view (Match List), is finer than the in-page row-swap grain.** Elsewhere on this site a Match List row is the item (see *Transitions* → *The test for "board" vs. "item"* — every cell in a row describes the same one game). On cross-page arrival, flying a whole row in as one wide strip reads as the same "component dropped in" problem a nav bar has — a full-width block landing intact, edge to edge, doesn't read as several things being placed. So here specifically, each of a row's own independently visible pieces — each flag, each score, each ELO figure, each confederation cell — flies in on its own, not the row as a unit. Every other view already flies at this granularity by default (Knockout's game cards are single physical cutouts so the card stays the item; Rankings' flags and History's flag+ELO cells are already the finest unit in their own views) and needs no special case here.

**Not** implemented via the browser's native cross-document View Transitions API (`@view-transition { navigation: auto }`). That API's only real primitive is a single before/after snapshot of the whole page — an entire poster, nav bar and all, arriving pre-assembled as one image — which is exactly the "component dropped in from the side" effect *Walking to a different poster* rules out. Instead: an internal link click plays the standard item fly-out (see *Transitions* → *Item pace* / *Stagger*) across every in-frame piece at the granularity above, then navigates; the destination page, once it detects it was reached by an internal click rather than a direct load, starts every in-frame piece in its off-screen fly-in-start position and plays the same fly-in, staggered, before the reader ever sees them settled in place.

**The board must already be standing before the first item moves — never a race.** Placing an item is a distinct beat that comes *after* the board is there, not a beat that might get skipped if the page is slow to render (see brand-guidelines.md → *Motion* → *Walking to a different poster*: someone puts the backboard up, *then* pins pieces to it one at a time — never both at once, and never pinning before the board exists). A page's fonts are a render-blocking resource; if the browser is still waiting on them when the fly-in would otherwise start, starting anyway risks the whole staggered arrival executing before the page ever gets a frame to paint it in — which reads as everything landing at once in a single clump, not as individually staggered pieces, because the reader never actually saw the individual motion happen. So an item is pinned off-screen the instant it exists (before any paint, same as always — this part never waits on anything), but the flight itself — the actual animated placement — doesn't begin until the page is actually ready to render it smoothly.

**Transition:** board — none, only structural chrome, which never moves; item — every in-frame nav chip at every level, plus every in-frame piece of the active view at that view's finest independently-meaningful grain (see above), individually, on both the outgoing and incoming page; how — the standard horizontal conveyor at item pace (see *Transitions* → *Item pace*), same direction as everywhere else on the site (out right, in left).

**On load:** a direct load (typed URL, bookmark, refresh) has no page to exit from, so it follows the sitewide default above — every piece is simply already there, nothing flies. Only a same-site link click, where a reader is already looking at a page and choosing to leave it, gets the arrival flurry — the one sanctioned exception to *Nothing appears from nothing*, and even then, never as one assembled image, and never beyond what's actually in frame.

---

## World Cup

A tool for soccer fans to follow and compare how different continental confederations perform across FIFA World Cups — who's gaining rating ground, who's losing it, and how each tournament's results play out game by game. It does this by tracking ELO rating transfers between confederations as matches are played, across every World Cup from 1998 through 2026.

Where the underlying ELO/match data comes from, how it's stored, and how it gets entered are not this doc's concern — see `admin.md` for all of that.

#### World Cup pages (`1998.html`, `2002.html`, `2006.html`, `2010.html`, `2014.html`, `2018.html`, `2022.html`, `2026.html`)

Styling is defined in `worldcup/shared.css` and inlined at build time. All eight pages share the same visual treatment.

#### Typography
- Body font: Fredoka One (Google Fonts), loaded via `<link>` in the page `<head>`.
- There is no page `<h1>` — the nav (see *Navigation* below) is the first thing on the page and is the visual anchor; the current page is identified there, not by a separate heading.
- Links use dark blue `#1A5276`.

#### Page background and header
- Page background: cream `#F5F0E8`.
- No top border, no top margin — the nav sits flush against the very top of the viewport.

#### Navigation

Uses the shared `.page-nav` component and general characteristics described in *Navigation* above. On tournament pages (`1998.html`–`2026.html`), Levels 1–3 always render, in this order, top to bottom:

1. **Level 1 — Utility bar** (`<nav class="utility-bar view-toggle">`) — a loosely-wrapping row of chip items, in this order: `Home`, then one item per World Cup using a short `WC YY` label — `WC 98`, `WC 02`, `WC 06`, `WC 10`, `WC 14`, `WC 18`, `WC 22`, `WC 26`, `WC 30` — last two digits of the year, zero-padded. `Home` links back to the homepage. `WC 30` is a placeholder for the next tournament: there's no `2030.json` data and no `2030.html` page yet, so it renders as the disabled-item state (see *Navigation* above) rather than a dead link. The current page is shown the same way the current tab is shown one level down: the selected-chip treatment described in *Navigation* → *General nav chip characteristics*, non-linking. There is no Data Entry toggle, no mode switch, and no admin affordance of any kind on this site — see `admin.md` for where data entry actually happens. There is no `History` item here — see *History page* below for why, and how it's reached instead.
2. **Level 2 — Primary tabs** (`.primary-tabs.view-toggle`) — the segmented Match List / Groups / Knockout / Rankings toggle, in that left-to-right order. This is the single most visually dominant level (larger font/padding than the others — see *Navigation* → *General nav chip characteristics* → *Size*), because switching between these views is the main thing a user does. Switching tabs uses the fly in/out transition described in *Navigation* → *Transitions* — the view content below flies out and the new view flies in. **Transition:** board — nothing shared between the outgoing/incoming view (a table, a bracket, a flag grid share no structure), so the outgoing view's board exits fully off-screen as one piece; item — each outgoing/incoming view's own rows/cards, individually staggered alongside it (see that view's own *Transition* line for specifics); how — the standard horizontal conveyor, board out right/in left at board pace, items the same direction at item pace.
3. **Level 3 — View detail** — detail controls for whichever of the four views is currently active. Every view has one, even Groups (which just holds a "coming soon" note — see *Group Stage*), so the nav is always the same three-level shape no matter which tab you're on; only one view's Level 3 content is populated/visible at a time, swapped by JS when you switch tabs. See each view's own section for what its Level 3 contains: *Confederation panel* (Match List), *Round toggles* (Knockout Bracket), *Show eliminated* / *True rank* toggles (Tournament ELO Rankings).
4. **On load:** matches the sitewide default (see *Navigation* → *Initial display*) — whichever view is selected on arrival (Match List by default, or another view via URL hash, e.g. `#knockout`) is already there, fully in place, regardless of how it was reached; it never flies in. The other three views' content doesn't exist on the page at all until first selected, at which point they get the normal Transition treatment from item 2 above like any later switch.

Pages without the primary tabs (`history.html`) show only Level 1, styled identically — chips look the same whether or not there's a level below them, since nothing about the chip treatment depends on stacking position. Level 4 still applies there (the F4/F8/F16 table's header row).

#### Table
- Page background `#F5F0E8` carries through — tables sit on the cream background.
- Table header row is this page's Level 4 (see *Navigation* above) — same red/white, Permanent Marker treatment as the rest of the nav.
- Row hover: a warm tint `#EDE8DC`.
- All other table layout and column behavior is unchanged.

#### Flags
- Each flag icon is treated like a small photograph or sticker stuck flat onto the page.
- Each flag has a very slight, unique, deterministic rotation — derived from the team name so it's consistent across every appearance of that team. Rotation range: approximately ±1 degree.
- No drop shadow on flags — on something that small, a shadow reads as hovering, not pinned. The tilt alone conveys placement.
- Flags are slightly desaturated (`saturate(0.8)`) to feel like a printed sticker, not a crisp digital image.
- **Name on hover**: every flag on the site — Match List, Knockout game boxes, History — shows the team's name on hover the same way. **Not** the browser's native `title` tooltip: that's unstyled system chrome with no brand material at all, and it contradicts `brand-guidelines.md` → *Flags, Not Names*'s own framing of the hover-name as "a label under a fingertip" — implying something designed, not raw OS UI. Instead it's a small sticky note (the same `#FAD7A0` yellow and material as the W/D/L diff highlight's sticky — see *Confederation panel* → *View 2*), sized to its text, with a small random tilt, appearing right at the hovered flag and disappearing the instant the cursor leaves. One shared treatment, reused everywhere a name needs to surface rather than reinvented per view.

---

### Match List

#### Pages & URLs

- Each World Cup from 1998 through 2026 has its own page with its own URL (`1998.html`, `2002.html`, `2006.html`, `2010.html`, `2014.html`, `2018.html`, `2022.html`, `2026.html`), so it can be linked/bookmarked directly.
- `index.html` is the homepage — see *Homepage* above. It has no year links of its own; its Level 3 `Tournaments` item is the entry point into this section, landing on the current/latest year.
- Each World Cup page has Level 1 (the utility bar) to switch between World Cup pages and back to the homepage — see *Navigation* under *World Cup pages* above for the full nav structure.

#### Columns

The table has two groups of columns: **Game columns** and **Confederation columns**.

##### Game columns

- For the selected World Cup, list all games in chronological order.
- The table has a single header row (this is Level 4 — see *Navigation* under *World Cup pages*), full stop — no second header row. Date and # have their own header cells; Home and Away are super-headers spanning their respective columns.
- Column order, left to right:
  1. **Date** — no super-header; displayed in "Mon D" format (e.g. "Jun 2", "Jun 14", "Dec 12"), no year since the year is implied by the selected World Cup.
  2. **Game #** — no super-header; displayed as `#1`, `#2`, etc. The game number is the game's 1-based position in chronological order within that World Cup, stored in the data so it can be used as a stable identifier elsewhere (e.g. data entry).
  3. **[spacer]** — an empty column with no header, providing visual separation between the game identifiers and the Home/Away groups.
  4. **Home** super-header spanning: ELO, Flag, Score.
  5. **[score separator]** — a column displaying a literal `-` for every played game, visually joining the home and away scores (e.g. the row reads "3 - 1"). No super-header.
  6. **Away** super-header spanning: Score, Flag, ELO.
- The ELO column for each team combines pre-game ELO and delta into a single cell displayed as a concatenated string, e.g. `1873+4` or `1938-16`. When `eloChange` is null the cell is empty; when only `homeEloPre`/`awayEloPre` is null the pre-ELO portion is omitted and just the delta is shown.
- Each team is shown as its flag (an SVG image served from `../site/football/worldcup/flags/`, kept in sync with the source copy at `worldcup/data/flags/`) only — never a printed name, see `brand-guidelines.md` → *Flags, Not Names* — with the team's name shown on hover (see *Flags* above for the sticky-note label treatment).
- The header row stays fixed/visible at the top of the viewport when scrolling (plain CSS `position: sticky; top: 0` — no JS-measured offset needed, since there's only one row to pin).
- Each column is sized to fit its content — no fixed widths are set. The table never grows wider than the nav above it (Levels 1–3): if the columns need more room than that, the table scrolls horizontally within that width cap rather than pushing the page wider than the nav (see *Navigation* under *World Cup pages*).
- Rows are not clickable and there is no expand panel on this site. Data entry is a completely separate tool — see `admin.md`.
- **Transition:** board — the Level 4 header row (Date/#/Home/Away); item — one table row (one game), all of its cells describing that same one game, so the row (not each cell) is the unit; how — only relevant when Match List itself is being replaced by a different view (see *World Cup pages* → *Navigation* → Level 2), where each row flies the standard horizontal conveyor alongside the outgoing/incoming board. Match List has no internal toggle of its own beyond the confederation panel (see below).
- **On load:** matches the sitewide default — when Match List is the view shown on arrival (the default, or via `#matches`), every row is already there, fully populated; no row flies in.

##### Confederation panel (right side, toggleable)

The right side of the table is a panel of confederation columns that can be toggled between three views: **ELO Shift**, **W / D / L**, and **Stats**. The toggle itself is *not* in the table — it's the Match List view's Level 3 in the nav (see *Navigation* under *World Cup pages*), styled like every other Level 3 control: the selected view uses the selected-chip treatment, the other two sit at the default chip look. A left border (`2px solid rgba(255,255,255,0.3)`) on the first confederation header cell is the only visual seam separating the confederation columns from the game columns in the table itself. Switching views must not cause the game columns on the left to shift or resize — the game section width is fixed regardless of which view is active.

**Transition:** board — the confederation column headers (the confederation names never move) plus the fixed game columns to the left; item — each row's confederation-cell **value**, not the whole column and not the whole row (a confederation's own running tally is independently meaningful, unlike a Match List row where every cell describes the same one game); how — the old value flies out to the right, the new one flies in from the left, individually staggered row by row at item pace, rather than the whole confederation panel moving as one block (see *Navigation* → *Transitions*).

**On load:** matches the sitewide default — **ELO Shift** (the default view) is already there; its values never fly in. The other two views' values don't exist on the page until first selected, at which point switching to them gets the normal Transition treatment above.

Only confederations with at least one team participating in the selected World Cup get a column in any view (e.g. if Oceania has no teams in the tournament, it has no column in any view). All confederation columns within a view have equal width.

**View 1 — ELO Shift (default)**

- One column per confederation showing its running cumulative ELO delta across games played so far.
- For each game, the home team's confederation gets `+eloChange` and the away team's confederation gets `-eloChange`. If both teams are in the same confederation, the net change is 0.
- Each cell shows the cumulative running total up to and including that row.
- Columns are ordered left-to-right by their final cumulative ELO total (highest first). This same ordering is used for both View 1 and View 2, so column positions do not shift when toggling between those two views.
- Cells are color-coded on a gradient using the brand palette: 0 (neutral) is the page background beige `#F5F0E8`, +400 (max positive) is brand green `#27AE60`, -400 (max negative) is brand red `#C0392B`, interpolated linearly. Values beyond ±400 are clipped to the max color.
- **Color is always driven by the cumulative ELO shift**, regardless of which view is active. When toggling between ELO Shift and W/D/L, the cell background color stays identical — only the displayed text changes. This means a confederation showing a record of "2-3-5" will have the same background color as it had when showing its ELO total, since both reflect the same underlying performance.
- For a game whose `eloChange` is `null`, cells are left empty and the running total does not advance.

**View 2 — W/D/L Record**

- One column per confederation showing its cumulative W/D/L record across games played so far, using the same column order as View 1 (by final cumulative ELO, highest first).
- Each cell displays three numbers in W-D-L order, formatted as e.g. `5-1-2` (wins-draws-losses), representing the running totals up to and including that row. No labels — the W/D/L order is implied by the view name.
- **Sticky note diff highlight**: whichever digit changed from the previous row is overlaid with a small yellow sticky note. The sticky is rendered as an absolutely-positioned square (≈1.05em × 1.05em) centered over the digit, with the same number written on it at the same font size. The underlying digit remains in the normal text flow so spacing is unaffected; the sticky floats on top. Each sticky gets a small random tilt between −5° and +5° to reinforce the physical sticky-note aesthetic. The sticky color is always `#FAD7A0` (warm yellow) — no semantic color distinction between wins, draws, and losses.
- A win for a confederation is any game where a team from that confederation wins (outright, or on penalties). A loss is any game where a team from that confederation loses. A draw is any game that ends level after 90 minutes (regardless of penalty shootout outcome).
- If both teams are from the same confederation, the game counts as both a win and a loss for that confederation (one team won, one lost), or two draws in the case of a draw.
- For a game with `homeScore`/`awayScore` both `null`, the row's cells are empty and the running totals do not advance.

**View 3 — Competition Stats**

- Tournament-wide aggregate stats, not broken out by confederation — a fixed set of summary columns shown for the whole table.
- The total number of columns in View 3 must equal the number of confederation columns in Views 1 and 2, so the right panel stays the same total width across all three views. If there are N confederation columns, use N stat columns (padding with empty columns if N > 3, or merging if N < 3 — but in practice N is typically 5–6 so distribute the stats across N columns or group them sensibly).
- Core stats columns (always present):
  1. **Wins** — running count of decided games (games with a winner after 90 minutes).
  2. **Draws** — running count of drawn games (scores level after 90 minutes).
  3. **Win%** — running ratio of wins to total played games, displayed as a percentage (e.g. `62%`). A played game is any game where both scores are non-null.
- Remaining columns (to fill out to N total) are left blank (empty header, empty cells).
- Values accumulate row by row; unplayed games (`null` scores) leave the row empty and do not advance the totals.

---

### Group Stage

**Status: placeholder.** The tab strip includes a **Groups** tab (`#groups` hash) alongside Match List, Knockout, and Rankings. Its Level 3 (see *Navigation* under *World Cup pages*) holds a single muted, non-interactive note — "Group Stage view — coming soon." — centered in that row; there is no other content and nothing below it in the page body. Level 3 is kept present (not blank/hidden) so the nav is always the same three-level shape no matter which tab is active, and once this view is built out, the note is replaced with its own controls the same way every other view's Level 3 works.

Intended scope (not yet designed in detail): one standings table per group, each team's played/won/drawn/lost/goals-for/goals-against/goal-difference/points, ordered by tournament tiebreak rules, updating as group-stage results are entered.

**Transition:** none of its own yet — this view has no internal toggle, just the disabled placeholder note. It only appears/disappears as part of the Level 2 board-level switch (see *World Cup pages* → *Navigation*), same as every other tab.

**On load:** matches the sitewide default — if reached directly via `#groups`, the placeholder note is already there; it never flies in.

---

### Knockout Bracket

**Status: implemented.** The **Knockout** tab (`#knockout` hash) renders a bracket-tree visualization of the selected tournament's knockout stage — one column per round, growing gaps between games each round, connected by simple stub lines. Distinct from `history.html`, which compares knockout fields *across* tournaments rather than visualizing a single bracket.

If the tournament has no bracket configured yet (see `admin.md` → *Knockout Bracket* for how that's set), the tab shows "Knockout bracket not yet configured for this tournament" instead.

#### Rounds

The bracket's round sequence is determined by its **size** — the number of teams entering the knockout stage (32/16/8/4), set once per tournament in the admin site. Rounds halve down to the semifinals, followed by a **Final** round holding two games: the third-place playoff and the final (the earlier-numbered of the two is the third-place match).

| Size | Round sequence |
|------|----------------|
| 32 | Round of 32 → Round of 16 → Quarterfinals → Semifinals → Final |
| 16 | Round of 16 → Quarterfinals → Semifinals → Final |
| 8 | Quarterfinals → Semifinals → Final |
| 4 | Semifinals → Final |

This view has no Level 4 (see the Level table in *Navigation*) — the round toggle buttons below already name each round, so a column doesn't repeat its own round name above it.

#### Game boxes

Each bracket game is its own paper-card cutout — white, a hard offset shadow rather than a soft one, and a tiny per-game rotation (a deterministic hash of the game number, not random-per-load — same principle as flag rotation below), so a column of cards reads as individually placed rather than machine-stamped. It shows a date and its two participants, top-to-bottom. A participant is either:
- A resolved team, shown as its flag only — never a printed name, see `brand-guidelines.md` → *Flags, Not Names* — with its score once played. Hovering the flag shows the team's name via the sitewide sticky-note label (see *Flags* above), same as every other flag on the site. If the game is decided by a clear winner (not a draw), the winning row gets a light green tint and its score is colored green; the losing row is dimmed and its flag is rendered in greyscale — the same treatment Rankings gives an eliminated team's flag, reused rather than inventing a second convention. A draw settled on penalties shows neither treatment, since penalty-shootout winners aren't tracked in the data (see `admin.md`).
- An unresolved slot, shown as italic placeholder text: "Winner of Game N" / "Loser of Game N" if the admin has recorded which earlier game feeds it, or "TBD" if not. "Date TBD" is shown in place of a date if it isn't set yet.

This placeholder behavior also applies to any knockout game appearing in the Match List before it's resolved — the flag cell shows the same placeholder text instead of a broken flag image.

#### Round toggles

The Knockout view's Level 3 in the nav (see *Navigation* under *World Cup pages*) has one button per round in the tournament's configured sequence (e.g. Round of 32 / Round of 16 / Quarterfinals / Semifinals / Final), labelled with that round's name. All rounds are shown by default.

Unlike the primary tabs, this isn't a single either/or choice, but it isn't fully independent either — the set of shown rounds is always a **contiguous range**, so a round can never be hidden in isolation while its neighbors on both sides stay visible (no gaps in the middle of the tree).

**Transition:** board — nothing; a round's column has its own fixed horizontal slot (below) that must never shift sideways, so there's no shared structure for a "board" to even mean here; item — each game card within the round being shown/hidden, not the column as a whole; how — vertical, the one exception to the sitewide horizontal conveyor (see *Navigation* → *Transitions* → *Direction*): a card lifts up and off when hidden, or drops down into place when shown, each individually staggered.

**On load:** matches the sitewide default — all rounds are shown by default (see below), and every visible round's game cards are already there in their fixed slots; none of them drop in, regardless of whether Knockout is the view shown on arrival or reached directly via `#knockout`.

**Each round has a fixed horizontal slot, aligned to its own toggle button** directly above it — same left position, same width, not a fixed column size. A column is only ever as wide as its own round's label needs (a narrow "Final" column stays narrow rather than stretching to match "Round of 32"), and it's positioned by its own place in the tournament's round sequence (first round always leftmost, Final always rightmost) — not by how many rounds currently happen to be shown. Showing or hiding a round never shifts any *other* round horizontally, and there's no board here to speak of (see *Navigation* → *Transitions*) — a round's own game cards are the items that fly: each one lifts up and off individually (a small random stagger between cards, not a single synchronized column-wide move) when its round is hidden, or drops down into its slot individually when shown, rather than the bracket reflowing to close/open a gap. The one thing that does move sideways-adjacent is vertical: each visible round's games are spaced down the shared column height (the tallest currently-visible round's height, same as before), so hiding the tallest round can change that shared height and reflow the remaining rounds' games vertically within their own unmoved columns.

- **Shrinking** removes one round at a time, and only from an end of the current range: clicking the leftmost or rightmost *shown* round hides it — that round's game cards each lift up and off individually, out of the bracket's frame.
- **Growing** can jump straight to any *hidden* round in one click: clicking a hidden round reveals it and every round between it and the current range in a single step (e.g. from a range of just "Semifinals", clicking "Round of 32" reveals Round of 32, Round of 16, and Quarterfinals all at once). Each newly-revealed round's game cards drop down into their fixed slot individually, one small stagger apart — a big jump reads as a flurry of cards snapping into place in quick succession, not the whole column arriving at once.
- At least one round is always kept visible; clicking the only remaining shown round's button does nothing, since an all-hidden tree would just look broken rather than intentionally empty.
- A shown round that isn't at an edge of the range (so clicking it wouldn't do anything useful) is not clickable, but stays visually identical to the shown rounds that are clickable — see the color convention in *Navigation*, which deliberately keeps "shown" always the same selected-chip look regardless of clickability, so it's never ambiguous whether a round is currently part of the bracket.

This state isn't persisted anywhere (URL, storage) — it's a browsing convenience that resets on reload, same as the Rankings view's toggles.

---

### Tournament ELO Rankings

A standalone view — only one page view is visible at a time. The World Cup page has a segmented toggle that switches between **Match List**, **Groups**, **Knockout**, and **Rankings**; they never appear simultaneously. Level 1 (links to other years) stays fixed regardless of which view is active. All eight World Cup pages (1998–2026) have the Rankings view, since all have `teamElos` data.

All of this view's own controls — the **Rank**/**Scale** toggle, **Show eliminated**, **True rank**, and the debug toggle — live together in Level 3 of the nav (see *Navigation* under *World Cup pages*), left-aligned in that order, rather than inside the rankings panel itself. The panel below them starts clean.

Each view has its own URL via the hash fragment: `2026.html#matches`, `#rankings`, `#groups`, `#knockout`. Switching views updates the hash; loading the page with a hash pre-selects that view. The default (no hash) is Match List.

#### Gamesets

A **gameset** is a batch of games in which each active team plays at most once — it is one "turn" for every team still in the tournament. Gamesets are defined per tournament by a fixed list of game-count boundaries, applied in chronological order. They are not stored in the game data — the boundaries are hardcoded per tournament and applied at render time. A gameset is complete when every team that has a game in its range has a recorded result; teams with no game in the range (already eliminated, or byes) do not count toward completion.

Gamesets are defined per tournament. The boundary for each gameset is `lastGameNumber` — games up to and including that number belong to the gameset.

**1998–2022** (32 teams, 64 games total):

| Gameset | Column label | Description | Game count | Last game # |
|---------|--------------|-------------|------------|-------------|
| 0 | Initial | Pre-tournament (starting `teamElos`) | — | 0 |
| 1 | MD1 | Group stage, matchday 1 | 16 | 16 |
| 2 | MD2 | Group stage, matchday 2 | 16 | 32 |
| 3 | MD3 | Group stage, matchday 3 | 16 | 48 |
| 4 | 16 | Round of 16 | 8 | 56 |
| 5 | 8 | Quarterfinals | 4 | 60 |
| 6 | 4 | Semifinals | 2 | 62 |
| 7 | Final | Third-place game + Final | 2 | 64 |

All 8 gameset columns are always shown for 1998–2022.

**2026** (48 teams, 104 games total):

| Gameset | Column label | Description | Game count | Last game # |
|---------|--------------|-------------|------------|-------------|
| 0 | Initial | Pre-tournament (starting `teamElos`) | — | 0 |
| 1 | Game 1 | Group stage, matchday 1 | 24 | 24 |
| 2 | Game 2 | Group stage, matchday 2 | 24 | 48 |
| 3 | Game 3 | Group stage, matchday 3 | 24 | 72 |
| 4 | 32 | Round of 32 | 16 | 88 |
| 5 | 16 | Round of 16 | 8 | 96 |
| 6 | 8 | Quarterfinals | 4 | 100 |
| 7 | 4 | Semifinals | 2 | 102 |
| 8 | Final | Third-place game + Final | 2 | 104 |

All 9 gameset columns are always shown for 2026. The Rankings view has a segmented toggle that switches between **Rank** and **Scale** views of the same gameset data — part of the Level 3 controls described above. Switching between Rank and Scale must not shift the gameset column positions — the horizontal layout is identical in both views.

**Transition:** none — this toggle is explicitly excluded from the fly in/out treatment (see *Navigation* → *Transitions* → *Scope*). Nothing appears or disappears; existing flags reposition in place within a layout that must not otherwise shift, a different, not-yet-designed animation question, so board/item/how don't apply here — it's an instant update.

**On load:** matches the sitewide default — **Rank** (the default) is already there, no animation. Moot beyond that, since this toggle has no animation at any point (see Transition above) — there's nothing an on-load exemption would even need to skip.

#### Ranking and ties

Teams are ranked by ELO descending within each gameset snapshot. Ties are broken by **stable sort**: if two teams have equal ELO, the one ranked higher in the previous snapshot remains ranked higher.

#### Live gameset

At any point in the tournament there is exactly one **live gameset column**: the in-progress gameset if any games in its range have been played but it is not yet complete, or the next gameset if the most recent gameset just completed and the next hasn't started.

The live gameset column is always shown populated — it is never empty:

- It is seeded from the previous gameset's final ELOs (or from `teamElos` if it is the first gameset).
- As results come in, the column updates: each team's ELO and rank reflects all results recorded so far within the live gameset.
- Teams are always ranked by their current ELO, including mid-gameset. There is no hold on unplayed teams — the live standings shift with every result entered.

Teams that have a game scheduled in the live gameset's range but no result recorded yet are shown with a **"hasn't played" visual**: a muted grey distinct from the greyscale used for eliminated teams. Once their game result is entered, they revert to normal styling.

Only the live gameset column uses this treatment. Completed gameset columns always show final ELOs with no "hasn't played" styling. Future gameset columns (beyond the live one) show nothing.

#### Eliminated teams

A team is considered **eliminated** as of the gameset after their last appearance in a game. Specifically: if a team played in gameset N but does not appear in any game in gameset N+1 or later, they are eliminated after gameset N. (For the group stage this naturally captures teams that don't qualify for the Round of 32; for knockout rounds it captures teams that lost.)

Eliminated teams are hidden by default in knockout columns (see *Show eliminated toggle* below). When shown, their flag is rendered in greyscale to visually distinguish them from active teams.

#### Show eliminated toggle

A toggle labelled **"Show eliminated"** is available in both the Rank view and the Scale view. By default (off), eliminated teams are hidden in knockout columns. When on, all teams are always shown.

- **Group stage columns** (gamesets covering MD1–MD3): all teams are always shown regardless of this toggle, since every team participates in the group stage.
- **Knockout round columns** (gamesets from Round of 32 onward): when the toggle is off (default), eliminated teams' flags are hidden in any column where they are not participating. A team is considered eliminated for a given column if they have no game in that gameset and no game in any later gameset.
- **Layout is unchanged**: the column structure, ELO axis, column widths, and spacing are identical regardless of the toggle state. Only the flag elements are hidden — no reflow, no gaps closing.

**Transition:** none — like Rank/Scale above, this toggle is excluded from the fly in/out treatment (see *Navigation* → *Transitions* → *Scope*): nothing appears/disappears, existing flags just show/hide in place, so it's an instant update, not board/item/how.

**On load:** off (the default) — eliminated teams are already hidden, no animation, same reasoning as Rank/Scale above.

#### True rank toggle (Rank view only)

A toggle labelled **"True rank"** is available in the Rank view only. It is not shown at all in the Scale view, since the concept doesn't apply there.

- **Off (default)**: surviving teams are re-numbered starting from 1 in ELO order, and their flags are packed to fill the gaps.
- **On**: surviving teams keep their original rank numbers. A surviving team ranked #5 still appears at rank slot #5; slots for hidden eliminated teams appear empty.

Checking **"Show eliminated"** automatically checks "True rank" as well, since showing all teams in their packed positions would be misleading — the true rank slots are needed to make the eliminated flags readable. The user can uncheck "True rank" independently after.

**Transition:** none — same reasoning as Show eliminated and Rank/Scale above: existing flags reposition in place, nothing appears/disappears, so it's excluded from the fly in/out treatment and stays an instant update.

**On load:** off (the default) — teams are already re-numbered/packed, no animation.

#### Rankings shared layout

Both Rank and Scale views share the same canvas structure: one vertical column per gameset, all columns equal width, with a leftmost axis column. Toggling between views causes no horizontal shift.

- *Flag dimensions*: each flag icon has a fixed pixel width and height, consistent across both views.
- *Column width*: every gameset column has a fixed minimum width of `3 × flag_width + 2 × gap` (where *gap* is a fixed small spacing between side-by-side flags, defined in the Scale view). This applies uniformly across both views. Column separator lines are always fully visible; no flag extends past its column boundary. (The `3 ×` derives from the Scale view cluster constraint — see `scale-algorithm.md`.)
- *Header row*: the row of gameset labels (Initial / MD1 / MD2 / … or Initial / Game 1 / … for 2026) is this view's Level 4 (see *Navigation* under *World Cup pages*) — red `#C0392B` background, white text, matching every other view's Level 4, sitting just below Level 3 above it.

---

#### Flag info panel

Hovering any flag in the Rankings view populates a fixed side panel that sits to the left of the rankings grid, vertically centered on the viewport. The panel never overlaps the grid or its flags.

The panel always shows the same set of fields in the same order, so its height never changes while browsing:

| Field | Content |
|-------|---------|
| Flag | The team's flag image (large) |
| Name | Team name (bold) |
| ELO | ELO at that gameset snapshot |
| *(divider)* | |
| Date | Game date in "Mon D" format (e.g. "Jun 15"), or — if no game |
| Opponent | Opposing team name, or — |
| Score | Score from the hovered team's perspective (their goals first), or — |
| ELO Δ | ELO change, green for gain, red for loss, or — |

When there is no game in the column (Initial snapshot, or a team with no game scheduled in that gameset), the bottom four fields show —. For a pending game (live column, result not yet entered), Date and Opponent are shown but Score and ELO Δ show —.

**Behaviour:**
- The panel appears immediately when the cursor first lands on a flag.
- Moving between flags updates the panel content instantly with no flicker — the panel stays visible throughout.
- The panel hides 300 ms after the cursor leaves the rankings area entirely (same grace period as the highlight).

**Transition:** none — a hover tooltip, not a navigation-driven appear/disappear, so it's outside the scope of *Navigation* → *Transitions* entirely: instant show, a timed instant hide, never a fly.

**On load:** not shown — the panel only ever exists in response to a hover, so there's nothing to display before the first one.

---

#### Flag hover highlight

When the user hovers over any flag in the Rankings view, all flags belonging to **other** teams are dimmed (reduced opacity). The hovered team's flags across all gameset columns remain at full opacity, making it easy to trace a single team's ELO evolution across the tournament. The hovered team's flags are also brought to the front (highest z-index) so they are never obscured by overlapping flags.

The highlight uses debounced activation and deactivation to avoid flicker:
- **Activate delay (200 ms):** the highlight only appears after the cursor has rested on a flag for 200 ms. Brief passes don't trigger it.
- **Deactivate grace period (300 ms):** when the cursor moves to empty space or leaves the rankings area, the highlight holds for 300 ms before clearing. This prevents flicker when crossing flag edges.
- **Instant cancel:** if the cursor returns to the already-highlighted team's flag during the grace period, the deactivation is cancelled immediately with no re-delay.

**Transition:** none — a debounced hover dim/highlight, not a navigation-driven appear/disappear, so outside the scope of *Navigation* → *Transitions*.

**On load:** no highlight active — every flag is already at full opacity until the first hover.

#### Result badge

While a team is highlighted, each of its flags across all gameset columns shows a small badge in its bottom-right corner: a single-letter result (**W** / **L** / **D**, green/red/gray) plus a miniature flag of that round's opponent. The badge is only visible on the highlighted team's flags — it is not shown by default, keeping the grid uncluttered when nothing is hovered.

- The result is derived from the score of the team's game in that gameset column (win/loss/draw from the hovered team's perspective). This is independent of the ELO Δ shown in the side panel — a team can win a game and still be shown losing ELO, or vice versa.
- No badge is shown when there is no game in that column (Initial snapshot, or no game scheduled that gameset) or when the game is pending (live column, result not yet entered).
- A draw settled on penalties still shows **D** — same caveat as the Knockout Bracket view, penalty-shootout winners aren't tracked in the data (see *Game boxes* in *Knockout Bracket*).

---

#### Rank view

Flags are **evenly spaced** — each rank position occupies the same vertical height regardless of ELO magnitude. This is a positional ranking, not a proportional one.

Each flag occupies its rank slot for that gameset snapshot: rank 1 at the top, rank N at the bottom. A leftmost axis column shows rank numbers (1, 2, 3…) aligned to each rank slot. No ELO number is shown alongside the flag. Hovering a flag shows the info panel — see *Flag info panel* above.

A dotted horizontal line is drawn between every 4th and 5th rank (i.e. after ranks 4, 8, 12, …), spanning all columns, behind the flags.

---

#### Scale view

Flags are **positioned proportionally to ELO** — a team's vertical position on the axis directly encodes its ELO value. Y position is never altered for any reason. The gameset column X-positions are identical to Rank view so toggling between the two causes no horizontal shift.

**Definitions (Scale view)**
- *Gap*: a fixed small spacing (a few pixels) between flags placed side by side.
- *Depth*: at any vertical point on the axis, the number of flags whose pixel intervals simultaneously cover that point. Two flags overlap when their top-to-top pixel distance is less than one flag height.

**Axis range**
The ELO axis spans from the lowest to the highest ELO of any team across all populated gameset snapshots. A flag's **top edge** sits at its ELO pixel position — not the center. This means a team rated 1998 reads as "just below 2000," matching the natural interpretation that a flag hangs down from its rating. Centering would make the team appear to straddle the line above, which is misleading.

A fixed pixel margin of `RANK_ROW_H / 2` is applied at the top and at the bottom (below the lowest flag's bottom edge), keeping the extreme flags inset from the axis ends symmetrically.

Note: the Scale view's vertical positioning is **independent of the Rank view** — only the horizontal column layout is shared. The Rank view spaces flags evenly by rank; the Scale view spaces them proportionally by ELO. Toggling between views changes flag vertical positions but not column positions.

**Axis height**
No visual overlap between flags is allowed. The axis height is the **minimum height at which the maximum depth across all gameset columns is ≤ 3** — ensuring every point on the axis is covered by at most 3 flags, which is the column's horizontal dodge capacity. A single height is computed across all gameset columns together so all columns share the same vertical scale and remain aligned. See `scale-algorithm.md` for the constraints, algorithm, and implementation.

Error case: if 4 or more teams share an identical ELO in the same gameset column, no axis height can resolve the cluster. A visible warning is shown in that column and the smallest achievable height is used.

**Y-axis tick marks**
The tick interval (ELO units between marks) is selected from `[200, 100, 50, 25, 10, 5, 2]`, largest first, choosing the first value whose pixel spacing falls between 150 px and 300 px. If no candidate falls in that range (e.g. the axis is extremely compressed or stretched), the candidate whose spacing is closest to 200 px is used as a fallback. Tick labels are shown at every multiple of the chosen interval within the axis range, once in the leftmost axis column. A dotted horizontal line is drawn at each tick, spanning all columns, behind the flags.

**Horizontal dodge**
Overlapping flags are fanned out into up to 3 horizontal lanes; Y positions are never altered. Isolated flags are centered; pairs are symmetric; full 3-flag clusters span left-centre-right. See `scale-algorithm.md` for the full algorithm.

**Flag display**
No ELO number is shown alongside the flag. Hovering a flag shows the info panel — see *Flag info panel* above. Z-index is determined by rank: higher-ranked teams (lower rank number) render on top.

---

### History page (`history.html`)

A year-over-year comparison of the knockout-round field across all tournaments (1998–2026). Generated by `build.py` alongside the per-year pages.

**Standalone, not part of the World Cup pages' shared nav.** This page isn't one of the tournament pages' Level 1 destinations — it doesn't appear in their `Home` / `WC YY` utility bar at all (see *Navigation* under *World Cup pages*). It's reached exactly one way: the homepage's `Football` → Level 3 `History` item (see *Homepage* → *Navigation*). This is deliberate — History compares *across* tournaments, so it doesn't belong nested inside the per-year pages' own switcher, which is about moving between individual tournaments.

#### Layout

- Same visual treatment as the per-year pages: cream background, Permanent Marker headings, red construction-paper table header.
- **Level 1 is a single `Home` chip** — not the multi-item WC-years utility bar every other page gets. Same chip styling as everywhere else (see *Navigation* → *General nav chip characteristics*), just one item, and it's how you navigate back: it links to the homepage, the same destination `Home` links to everywhere else on the site.
- **Level 2 — Round**: a real part of `.page-nav` now (not a standalone control with its own one-off CSS, which is what caused the fused-red-bar bug this replaces — see *Table structure* below) — a `primary-tabs` segmented choice, same dominant styling as the World Cup pages' Match List/Groups/Knockout/Rankings tabs: **Final 4**, **Final 8**, **Final 16**. Single-choice, not multi-select like the old three-checkbox version — exactly one is selected at a time. **Final 16 is the default** on load. Switching rounds uses the fly in/out transition from *Navigation* → *Transitions*. **Transition:** board — the table itself: header row, year column/labels, every row's position, and the 16-column width, none of which ever change (see *Layout* below); item — each flag+ELO cell's **content**, not the row and not the table; how — the outgoing round's flag flies out to the right, the incoming round's flag for that same slot flies in from the left, individually staggered flag by flag at item pace, rather than the whole row (or the whole table) moving as one block. A row's year never moves — only what's placed in it does. This page has no Level 3.
- **On load:** matches the sitewide default — **Final 16** (the default) is already there, every row's flags already in place; none of them fly in. This is the page in its resting state, not a "switch into Final 16" — the flags for Final 4/8 don't exist on the page yet, waiting to be flown in; they simply aren't there until one of those tabs is clicked.
- A single wide table below the nav. The year column is on the left; 16 data columns fill the rest, regardless of which round is selected (Final 4 only populates 4 of them) — so switching rounds never shifts the table's width.
- A short caption above the table states plainly what the numbers are: the teams' ELO ranking on entering the selected round, highest to lowest, left to right — not a final standings/result table. Avoids the old bare "F4/F8/F16" labels reading as final placements.

#### Table structure

**One row per tournament** (not three) — whichever round is currently selected in Level 2 determines what that tournament's row shows:

| Selected round | Teams shown | ELO snapshot |
|----------------|-------------|--------------|
| Final 4 | 4 semi-finalists | ELO entering the semi-finals |
| Final 8 | All 8 QF entrants (includes the eventual F4 teams) | ELO entering the quarter-finals |
| Final 16 | All 16 R16 entrants (includes the eventual F8 teams) | ELO entering the round of 16 |

- Within the row, teams are sorted highest ELO → lowest, left to right.
- Every row starts at column 1 (no staggered offsets).
- A red border separates each tournament's row from the next (a group of one now, not three).
- 2026 shows "Not yet played" in place of the row's cells if the selected round hasn't been reached yet.
- The year label is simply the leftmost cell of each tournament's one row — no conditional CSS needed for "topmost visible row" anymore, since there's only ever one.

#### Cells

- Each cell shows a flag icon (same style as per-year pages: slight deterministic tilt, desaturated) with the ELO number directly below it — no country name. Hovering a flag shows its name via the sitewide sticky-note label (see *Flags* above), same as every other flag on the site.
- Hovering a flag dims all cells from other countries across the entire table, highlighting every appearance of that country.

**Transition:** none — a hover dim/highlight, not a navigation-driven appear/disappear, so outside the scope of *Navigation* → *Transitions*.

**On load:** no highlight active — every cell is already at full opacity until the first hover.

#### Game number ranges used to identify rounds

| Format | R16 | QF | SF |
|--------|-----|----|----|
| 32-team (1998–2022) | games 49–56 | games 57–60 | games 61–62 |
| 48-team (2026) | games 89–96 | games 97–100 | games 101–102 |

Loser detection uses set subtraction (teams in round N who do not appear in round N+1), not score/eloChange parsing — this correctly handles penalty-shootout results.

---

### Debug

Debug features are toggled via UI controls that are always visible but clearly labelled as debug. They are off by default and have no effect on normal rendering. In the nav, a debug control's label uses a dedicated warning pink (`#ffb3b3`) instead of any of the three color states described in *Navigation* — it isn't "shown/hidden" or "selected," it's a distinct "developer control, be careful" signal, so it deliberately doesn't borrow meaning from the other states.

**Show binding clusters** (Scale view only) — a toggle labelled "debug: show binding clusters". When on, a red outline is drawn around each depth-4 window that would appear if the axis were 1 pixel shorter — i.e. each set of flags whose vertical intervals would all overlap a common point at `scaleH − 1`. These are the flags forcing the axis to be as tall as it is: at the computed minimum height their depth is ≤ 3, but one pixel shorter it would reach 4 and overflow the column. Off by default.

**Transition:** none — the outline is drawn/removed instantly; it's a debug overlay, not content appearing/disappearing in the sense *Navigation* → *Transitions* covers.

**On load:** off (the default) — no outline present until switched on.

---

## Favicon

**Why this exists:** many tabs are open at once during normal use, and it has to be obvious at a glance whether a given tab is pointed at your local machine or the live published site — e.g. so a local-only layout experiment is never mistaken for what visitors actually see.

Since this site has no admin mode at all, there is exactly one signal: **local vs. live → ring style.** Dashed ring = local dev server (`localhost` / `127.0.0.1` / `file://`). Solid ring = live/published. The fill is always cream background + dark blue icon — the same colors used everywhere else on this site (`#F5F0E8` / `#1A5276`); there is no red/admin variant here. (The admin site has its own, separate favicon scheme — see `admin.md`.)

**The two states:**

| State | Fill | Ring |
|-------|------|------|
| Local | cream | dashed |
| Live | cream | solid |

**Implementation:** the icon is not a static image file. It's a small inline SVG (a circle + a pentagon, evoking a soccer ball) built as a data URI at load time by `window.__setFavicon()`, deriving `isLocal` once from `location.hostname`. The function is duplicated between `worldcup/scripts/build.py`'s `FAVICON_SCRIPT` constant (reused for `history.html` and every year page) and `worldcup/scripts/build_home.py`'s own copy, rather than shared, because it must run before any page-specific data exists — both are now build-time constants, since the homepage is a build artifact like every other public page.
