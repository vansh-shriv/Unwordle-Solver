from enum import Enum

class Color(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    GRAY = "gray"

def get_feedback(guess: str, solution: str) -> list[Color]:
    guess = guess.upper()
    solution = solution.upper()
    n = len(solution)

    if len(guess) != n:
        raise ValueError(
            f"Length mismatch: guess has {len(guess)} letters, "
            f"solution has {n} letters."
        )

    feedback: list[Color | None] = [None] * n
    sol_chars: list[str | None] = list(solution)
    guess_chars: list[str | None] = list(guess)

    for i in range(n):
        if guess_chars[i] == sol_chars[i]:
            feedback[i] = Color.GREEN
            sol_chars[i] = None
            guess_chars[i] = None

    pool: dict[str, int] = {}
    for c in sol_chars:
        if c is not None:
            pool[c] = pool.get(c, 0) + 1

    for i in range(n):
        if guess_chars[i] is None:
            continue
        c = guess_chars[i]
        if pool.get(c, 0) > 0:
            feedback[i] = Color.YELLOW
            pool[c] -= 1
        else:
            feedback[i] = Color.GRAY

    return feedback 


def check_hard_mode_constraint(guess: str,prev_word: str,prev_feedback: list[Color],) -> bool:
    guess = guess.upper()
    prev_word = prev_word.upper()
    n = len(guess)

    if len(prev_word) != n or len(prev_feedback) != n:
        return False

    for j in range(n):
        fb = prev_feedback[j]
        if fb == Color.GREEN and guess[j] != prev_word[j]:
            return False
        if fb == Color.YELLOW and guess[j] == prev_word[j]:
            return False

    letter_counts_prev: dict[str, dict[str, int]] = {}
    for j, char in enumerate(prev_word):
        if char not in letter_counts_prev:
            letter_counts_prev[char] = {"gy": 0, "gray": 0}
        fb = prev_feedback[j]
        if fb in (Color.GREEN, Color.YELLOW):
            letter_counts_prev[char]["gy"] += 1
        else:
            letter_counts_prev[char]["gray"] += 1
            if guess[j] == char:
                return False

    guess_char_counts: dict[str, int] = {}
    for char in guess:
        guess_char_counts[char] = guess_char_counts.get(char, 0) + 1

    for char, counts in letter_counts_prev.items():
        gy_count = counts["gy"]
        gray_count = counts["gray"]
        actual_count = guess_char_counts.get(char, 0)

        if gy_count > 0 and actual_count < gy_count:
            return False
        if gray_count > 0 and actual_count > gy_count:
            return False

    return True


def is_hard_mode_valid(guess: str,history: list[tuple[str, list[Color]]],) -> bool:
    for prev_word, prev_feedback in history:
        if not check_hard_mode_constraint(guess, prev_word, prev_feedback):
            return False
    return True

