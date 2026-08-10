import pytest

from app.core.feedback import Color, get_feedback

G = Color.GREEN
Y = Color.YELLOW
X = Color.GRAY

SPEC_VECTORS = [
    (
        "TRACE",
        "CRANE",
        [X, G, G, Y, G],
        "baseline — no duplicate letters",
    ),
    (
        "ERASE",
        "SPEED",
        [Y, X, X, Y, Y],
        "solution has 2×E, guess has 2×E in different spots — both register",
    ),
    (
        "OXOOX",
        "ROBOT",
        [Y, X, X, G, X],
        "guess has 3×O, solution has 2×O — one green, one yellow, one extra gray",
    ),
    (
        "CRANE",
        "CRANE",
        [G, G, G, G, G],
        "exact match — all green",
    ),
    (
        "XXXXX",
        "CRANE",
        [X, X, X, X, X],
        "no overlap at all — all gray",
    ),
    (
        "EEEEE",
        "SPEED",
        [X, X, G, G, X],
        (
            "classic trap: both E's in SPEED are consumed by the two green matches "
            "at index 2-3, leaving zero E's in the pool — so E's at index 0,1,4 "
            "must be GRAY, not yellow"
        ),
    ),
]


@pytest.mark.parametrize("guess,solution,expected,description", SPEC_VECTORS)
def test_spec_vector(guess: str, solution: str, expected: list, description: str):
    result = get_feedback(guess, solution)
    assert result == expected, (
        f"\nTest: {description}\n"
        f"  guess    = {guess!r}\n"
        f"  solution = {solution!r}\n"
        f"  expected = {[c.value for c in expected]}\n"
        f"  got      = {[c.value for c in result]}\n"
    )


def test_case_insensitive_guess():
    """get_feedback normalizes both inputs to uppercase internally."""
    lower = get_feedback("trace", "crane")
    upper = get_feedback("TRACE", "CRANE")
    assert lower == upper


def test_case_insensitive_solution():
    lower = get_feedback("TRACE", "crane")
    upper = get_feedback("TRACE", "CRANE")
    assert lower == upper


def test_length_mismatch_raises():
    with pytest.raises(ValueError, match="[Ll]ength"):
        get_feedback("TRACE", "CRANES")  # 5 vs 6


def test_single_letter_word():
    assert get_feedback("A", "A") == [G]
    assert get_feedback("A", "B") == [X]


def test_all_same_letter_guess_solution_has_one():
    result = get_feedback("AAAAA", "CRANE")
    assert result == [X, X, G, X, X]


def test_solution_with_triple_duplicate():
    result = get_feedback("AAAAA", "AAABB")
    assert result == [G, G, G, X, X]


def test_yellow_does_not_exceed_available_copies():
    result = get_feedback("AAXXX", "ABCDE")
    assert result == [G, X, X, X, X]
