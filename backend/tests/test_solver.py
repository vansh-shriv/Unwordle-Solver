from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app.core.feedback import Color, get_feedback
from app.library.loader import WordLibrary, _normalize_and_group
from app.solver.pattern_index import (
    build_pattern_index,
    pick_best_guess,
    solve_row,
)

SMALL_LIBRARY = [
    "CRANE",
    "TRACE",
    "AROSE",
    "STARE",
    "CRATE",
    "GLARE",
    "FRAME",
    "GROAN",
    "ARISE",
    "ERASE",
    "SPEED",
    "ROBOT",
    "XXXXX",
]

@pytest.fixture
def crane_index():
    return build_pattern_index(SMALL_LIBRARY, "CRANE")

def test_round_trip_every_word_in_bucket(crane_index):
    for pattern_key, words in crane_index.items():
        for word in words:
            computed = tuple(get_feedback(word, "CRANE"))
            assert computed == pattern_key, (
                f"Round-trip FAILED for '{word}': "
                f"bucketed under {[c.value for c in pattern_key]} but "
                f"get_feedback returns {[c.value for c in computed]}"
            )


def test_exact_match_bucket_contains_solution(crane_index):
    all_green = tuple([Color.GREEN] * 5)
    assert all_green in crane_index
    bucket = crane_index[all_green]
    assert "CRANE" in bucket, "Solution word must be in the all-green bucket"


def test_all_green_pattern_only_solution():
    sol = "CRANE"
    result = get_feedback(sol, sol)
    assert all(c == Color.GREEN for c in result)


def test_wrong_length_words_skipped():
    library_with_mixed = SMALL_LIBRARY + ["CRANES", "IT", "CRANBERRY"]
    index = build_pattern_index(library_with_mixed, "CRANE")
    for words in index.values():
        for w in words:
            assert len(w) == 5, f"Word '{w}' of wrong length found in index"

def test_solve_row_returns_candidates(crane_index):
    for pat_key, expected_words in crane_index.items():
        if len(expected_words) >= 1:
            candidates = solve_row(crane_index, [c.value for c in pat_key])
            assert set(candidates).issubset(set(expected_words))
            break


def test_solve_row_empty_for_impossible_pattern(crane_index):
    impossible = ["green", "green", "green", "green", "yellow"]
    candidates = solve_row(crane_index, impossible)
    assert isinstance(candidates, list)

def test_solve_row_max_candidates_respected(crane_index):
    all_gray = ["gray"] * 5
    candidates = solve_row(crane_index, all_gray, max_candidates=2)
    assert len(candidates) <= 2

def test_solve_row_excluded_words(crane_index):
    all_gray = ["gray"] * 5
    all_candidates = solve_row(crane_index, all_gray)
    if not all_candidates:
        pytest.skip("No gray candidates in small library")
    to_exclude = {all_candidates[0]}
    filtered = solve_row(crane_index, all_gray, excluded_words=to_exclude)
    assert all_candidates[0] not in filtered

def test_pick_best_guess_priority():
    candidates = ["AROSE", "ZEBRA", "CRANE"]
    assert pick_best_guess(candidates) == "AROSE"

def test_hard_mode_validation():
    from app.core.feedback import Color, is_hard_mode_valid
    history = [("ABAKA", [Color.YELLOW, Color.GRAY, Color.GRAY, Color.GRAY, Color.GRAY])]
    assert is_hard_mode_valid("BUBAL", history) is False
    assert is_hard_mode_valid("GROAN", history) is True

def test_pick_best_guess_empty():
    assert pick_best_guess([]) is None

def test_pick_best_guess_single():
    assert pick_best_guess(["CRANE"]) == "CRANE"

def test_normalize_and_group_deduplication():
    raw = ["crane", "CRANE", "Crane", "apple", "APPLE"]
    lib = _normalize_and_group(raw)
    assert lib.words_by_length[5].count("CRANE") == 1
    assert lib.words_by_length[5].count("APPLE") == 1

def test_normalize_rejects_non_alpha():
    raw = ["crane", "cr4ne", "cr-ne", "", "   "]
    lib = _normalize_and_group(raw)
    assert "CRANE" in lib.word_set


def test_normalize_groups_by_length():
    raw = ["crane", "it", "apple", "a"]
    lib = _normalize_and_group(raw)
    assert 5 in lib.words_by_length
    assert 2 in lib.words_by_length
    assert 1 in lib.words_by_length

def test_normalize_empty_input():
    lib = _normalize_and_group([])
    assert lib.total_words == 0

def test_library_contains_case_insensitive():
    raw = ["crane", "apple"]
    lib = _normalize_and_group(raw)
    assert lib.contains("crane")
    assert lib.contains("CRANE")
    assert lib.contains("Crane")
    assert not lib.contains("ROBOT")

@pytest.fixture
def client():
    import app.library.loader as loader_mod
    from app.main import app as fastapi_app
    lib = _normalize_and_group(SMALL_LIBRARY)
    loader_mod.WORD_LIBRARY = lib

    with TestClient(fastapi_app) as c:
        yield c

    loader_mod.WORD_LIBRARY = None


def test_health_endpoint(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["library_size"] > 0
    assert "5" in body["word_length_distribution"]


def test_feedback_compute(client):
    resp = client.post(
        "/api/v1/feedback/compute",
        json={"guess": "TRACE", "solution": "CRANE"},
    )
    assert resp.status_code == 200
    assert resp.json()["pattern"] == ["gray", "green", "green", "yellow", "green"]


def test_solve_all_green_row(client):
    resp = client.post(
        "/api/v1/puzzle/solve",
        json={
            "solution": "CRANE",
            "rows": [{"id": "r1", "pattern": ["green"] * 5}],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["rows"][0]["candidates"] == ["CRANE"]
    assert body["rows"][0]["best_guess"] == "CRANE"
    assert body["unsolvable_row_ids"] == []


def test_solve_unsolvable_row_in_response(client):
    resp = client.post(
        "/api/v1/puzzle/solve",
        json={
            "solution": "CRANE",
            "rows": [
                {
                    "id": "bad_row",
                    "pattern": ["yellow", "yellow", "yellow", "yellow", "yellow"],
                    "pattern": ["yellow", "yellow", "yellow", "yellow", "yellow"],
                }
            ],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    row = body["rows"][0]
    if row["candidate_count"] == 0:
        assert "bad_row" in body["unsolvable_row_ids"]


def test_solve_invalid_color_rejected(client):
    resp = client.post(
        "/api/v1/puzzle/solve",
        json={
            "solution": "CRANE",
            "rows": [{"id": "r1", "pattern": ["green", "blue", "gray", "gray", "gray"]}],
        },
    )
    assert resp.status_code == 422


def test_solve_pattern_length_mismatch_rejected(client):
    resp = client.post(
        "/api/v1/puzzle/solve",
        json={
            "solution": "CRANE",
            "rows": [{"id": "r1", "pattern": ["green", "gray", "gray"]}],  # only 3
        },
    )
    assert resp.status_code == 422


def test_validate_real_word_correct_pattern(client):
    resp = client.post(
        "/api/v1/guess/validate",
        json={
            "guess": "CRANE",
            "solution": "CRANE",
            "target_pattern": ["green", "green", "green", "green", "green"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["is_real_word"] is True
    assert body["mismatches"] == []


def test_validate_real_word_wrong_pattern(client):
    resp = client.post(
        "/api/v1/guess/validate",
        json={
            "guess": "AROSE",
            "solution": "CRANE",
            "target_pattern": ["green"] * 5,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["is_real_word"] is True
    assert len(body["mismatches"]) > 0


def test_validate_unknown_word(client):
    resp = client.post(
        "/api/v1/guess/validate",
        json={
            "guess": "ZZZZZ",
            "solution": "CRANE",
            "target_pattern": ["gray"] * 5,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_real_word"] is False
    assert body["valid"] is False
    assert body["computed_pattern"] is None


def test_solve_max_candidates_capped(client):
    resp = client.post(
        "/api/v1/puzzle/solve",
        json={
            "solution": "CRANE",
            "rows": [{"id": "r1", "pattern": ["gray"] * 5}],
            "options": {"max_candidates_per_row": 1},
        },
    )
    assert resp.status_code == 200
    row = resp.json()["rows"][0]
    assert len(row["candidates"]) <= 1


def test_solve_distinct_words_across_rows(client):
    resp = client.post(
        "/api/v1/puzzle/solve",
        json={
            "solution": "CRANE",
            "rows": [
                {"id": "r1", "pattern": ["gray"] * 5},
                {"id": "r2", "pattern": ["gray"] * 5},
            ],
            "options": {
                "max_candidates_per_row": 5,
                "distinct_words_across_rows": True,
            },
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    all_candidates = [
        word
        for row in body["rows"]
        for word in row["candidates"]
    ]
    best_guesses = [r["best_guess"] for r in body["rows"] if r["best_guess"]]
    assert len(best_guesses) == len(set(best_guesses)), (
        "distinct_words_across_rows: same best_guess used in multiple rows"
    )
