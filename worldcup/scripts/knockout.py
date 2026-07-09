"""Shared knockout-bracket round shape and structural-validation logic.

A tournament's bracket "size" (32/16/8/4) is the number of teams entering
the knockout stage. This determines the sequence of rounds and how many
games are in each round, halving each round down to the semifinals,
followed by a final round of 2 games (third-place playoff, then the final).

rounds_for_size() is used by build.py (validation + embedding into pages),
set_knockout_size.py (scaffolding stub games), and set_bracket_game.py
(editing them). Two independent JS mirrors of it exist, both named
knockoutRounds(): shared.js's copy (public World Cup pages) and
build_admin.py's own copy (admin pages). Keep all three in sync if this
ever changes.

check_from_ref() validates a single homeFrom/awayFrom reference — used by
build.py's validate() (every reference already in a data file) and
set_bracket_game.py (a single edit, before it's written) so the rule can't
drift between the two.
"""

VALID_SIZES = (32, 16, 8, 4)

ROUND_LABELS = {32: "Round of 32", 16: "Round of 16", 8: "Quarterfinals", 4: "Semifinals"}


def rounds_for_size(size):
    """Return [(label, game_count), ...] for a knockout bracket of the given size.

    The last two entries are always ("Semifinals", 2) and ("Final", 2) — the
    "Final" round holds the third-place playoff and the final, one game each.
    """
    if size not in VALID_SIZES:
        raise ValueError(f"knockout size must be one of {VALID_SIZES}, got {size!r}")

    rounds = []
    n = size
    while n > 4:
        rounds.append((ROUND_LABELS[n], n // 2))
        n //= 2
    rounds.append(("Semifinals", 2))
    rounds.append(("Final", 2))
    return rounds


def check_from_ref(games, this_game, from_key, frm, knockout_size):
    """Validate one homeFrom/awayFrom reference on `this_game` — shared by
    build.py's validate() (checking every reference already in a data file)
    and set_bracket_game.py (checking a single edit before writing it), so
    the rule can't drift between the two the way the JS round-shape mirrors
    already do (see this module's own docstring).

    `games` is the tournament's full game list, including `this_game` in
    whatever state it will be written in (this_game["round"] must already
    be set — only knockout-bracket games have a from-ref to check).
    `from_key` is "homeFrom" or "awayFrom" (for the error message only).
    `frm` is the already-shape-validated {"game": N, "result": "winner" |
    "loser"} dict (see build.py's validate() for the shape check itself —
    this function assumes it's already correct).

    Raises ValueError describing exactly what's wrong; returns None if the
    reference is valid. Checks, in order:
      1. The referenced game exists and is itself a knockout-bracket game.
      2. It's in the immediately preceding round — a slot can only defer to
         the round right before it, never an earlier or later one (or
         itself), since that's the only round shape a real bracket has.
      3. "loser" is only used on the last round (the third-place game) —
         every other round's advancement is always by winner.
      4. No other slot in the bracket already defers to this same
         game+result — a given result can only feed one slot.
    """
    this_gn = this_game["gameNumber"]
    this_round = this_game["round"]
    ctx = f"game #{this_gn} '{from_key}'"

    by_number = {g["gameNumber"]: g for g in games}
    ref = by_number.get(frm["game"])
    if ref is None or ref.get("round") is None:
        raise ValueError(f"{ctx}: references game #{frm['game']}, which doesn't exist or isn't a knockout-bracket game")
    if ref["round"] != this_round - 1:
        raise ValueError(
            f"{ctx}: references game #{frm['game']} (round {ref['round']}), which must be in the "
            f"immediately preceding round (round {this_round - 1}) — a slot can only defer to the round right before it"
        )

    if frm["result"] == "loser":
        last_round = len(rounds_for_size(knockout_size)) - 1
        if this_round != last_round:
            raise ValueError(f"{ctx}: 'loser' is only meaningful for the last round's third-place game, not round {this_round}")

    for g in games:
        if g is this_game:
            continue
        for other_key in ("homeFrom", "awayFrom"):
            other = g.get(other_key)
            if other and other.get("game") == frm["game"] and other.get("result") == frm["result"]:
                raise ValueError(
                    f"{ctx}: game #{frm['game']}'s {frm['result']} already feeds game #{g['gameNumber']} "
                    f"'{other_key}' — a result can only feed one bracket slot"
                )
