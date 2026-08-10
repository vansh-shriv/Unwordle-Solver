"""
Pattern index builder and row solver.

Implements the efficient precompute-once-per-solution design from spec §5.2:

  Instead of calling get_feedback on every word for every row (O(rows × library)),
  we make ONE pass over the library to bucket every word by the pattern it produces
  for the given solution.  Then every row lookup is O(1).

  The index is LRU-cached by solution string so a daily puzzle (same solution all day)
  never rebuilds the index on repeated requests.

Ranking heuristic (spec §5.3):
  The word list has no frequency/rank metadata, so best_guess falls back to
  alphabetically-first among candidates — stable and deterministic.
"""

from __future__ import annotations

import functools
import logging
from collections import defaultdict

from app.core.feedback import Color, get_feedback, is_hard_mode_valid

logger = logging.getLogger(__name__)

# Cache up to 128 different solutions in memory.
# For a daily puzzle this is effectively permanent; for Unlimited mode
# it evicts the least-recently-used solution if > 128 distinct ones accumulate.
_CACHE_SIZE = 128


def build_pattern_index(
    word_library: list[str],
    solution: str,
) -> dict[tuple[Color, ...], list[str]]:
    """
    Build a mapping: (pattern tuple) → [list of matching words].
    """
    n = len(solution)
    index: dict[tuple[Color, ...], list[str]] = defaultdict(list)

    for word in word_library:
        if len(word) != n:
            continue
        pattern = tuple(get_feedback(word, solution))
        index[pattern].append(word)

    return dict(index)


@functools.lru_cache(maxsize=_CACHE_SIZE)
def _cached_build_pattern_index(
    word_library_tuple: tuple[str, ...],
    solution: str,
) -> dict[tuple[Color, ...], list[str]]:
    return build_pattern_index(list(word_library_tuple), solution)


def get_cached_index(
    word_library: list[str],
    solution: str,
) -> dict[tuple[Color, ...], list[str]]:
    return _cached_build_pattern_index(tuple(word_library), solution.upper())


def solve_row(
    index: dict[tuple[Color, ...], list[str]],
    row_pattern: list[str],
    *,
    max_candidates: int = 20,
    excluded_words: set[str] | None = None,
) -> list[str]:
    pattern_key = tuple(Color(c) for c in row_pattern)
    candidates = index.get(pattern_key, [])

    if excluded_words:
        candidates = [w for w in candidates if w not in excluded_words]

    return candidates[:max_candidates]


def pick_best_guess(candidates: list[str]) -> str | None:
    if not candidates:
        return None
    return candidates[0]


def solve_full_puzzle(
    word_library: list[str],
    solution: str,
    row_patterns: list[list[str]],
    *,
    max_candidates_per_row: int = 20,
    distinct_words: bool = True,
) -> tuple[list[str | None], dict[int, list[str]]]:
    """
    Solve a full multi-row Unwordle puzzle by performing backtracking search
    over all rows to find joint sequences of words (W_1, W_2, ..., W_m) that satisfy:
      1. get_feedback(W_i, solution) == row_patterns[i] for all i.
      2. W_i satisfies Wordle Hard Mode rules against all preceding rows W_1..W_{i-1}.
      3. No duplicate words across rows (if distinct_words=True).

    Returns
    -------
    (best_solution_path, row_candidates_map)
      best_solution_path: list of best_guess words [W_1, W_2, ...] forming a valid path
      row_candidates_map: dict mapping row_index -> list of valid candidate words
    """
    index = get_cached_index(word_library, solution)
    m = len(row_patterns)
    pattern_keys = [tuple(Color(c) for c in pat) for pat in row_patterns]

    raw_candidates: list[list[str]] = [index.get(pk, []) for pk in pattern_keys]

    all_paths: list[list[str]] = []
    valid_words_per_row: list[set[str]] = [set() for _ in range(m)]

    def backtrack(row_idx: int, current_path: list[str], current_history: list[tuple[str, list[Color]]]):
        if len(all_paths) >= 100:
            return

        if row_idx == m:
            all_paths.append(list(current_path))
            for r, w in enumerate(current_path):
                valid_words_per_row[r].add(w)
            return

        cands = raw_candidates[row_idx]
        pk = pattern_keys[row_idx]

        for word in cands:
            if distinct_words and word in current_path:
                continue

            if is_hard_mode_valid(word, current_history):
                current_path.append(word)
                current_history.append((word, list(pk)))

                backtrack(row_idx + 1, current_path, current_history)

                current_path.pop()
                current_history.pop()

                if len(all_paths) >= 100:
                    break

    backtrack(0, [], [])

    best_path: list[str | None] = [None] * m
    row_candidates_map: dict[int, list[str]] = {}

    if all_paths:
        first_path = all_paths[0]
        for i in range(m):
            best_path[i] = first_path[i]
            cands = [w for w in raw_candidates[i] if w in valid_words_per_row[i]]
            row_candidates_map[i] = cands[:max_candidates_per_row]
    else:
        for i in range(m):
            row_candidates_map[i] = raw_candidates[i][:max_candidates_per_row]
            best_path[i] = raw_candidates[i][0] if raw_candidates[i] else None

    return best_path, row_candidates_map

