"""Shared knockout-bracket round shape logic.

A tournament's bracket "size" (32/16/8/4) is the number of teams entering
the knockout stage. This determines the sequence of rounds and how many
games are in each round, halving each round down to the semifinals,
followed by a final round of 2 games (third-place playoff, then the final).

Used by build.py (validation + embedding into pages), set_knockout_size.py
(scaffolding stub games), and set_bracket_game.py (editing them). Two
independent JS mirrors of rounds_for_size() exist, both named
knockoutRounds(): shared.js's copy (public World Cup pages) and
build_admin.py's own copy (admin pages). Keep all three in sync if this
ever changes.
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
