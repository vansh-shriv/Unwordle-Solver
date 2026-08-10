from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException
from app.core.feedback import get_feedback
import app.library.loader as _loader_module
from app.models import (
    MAX_CANDIDATES_HARD_CEILING,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    MismatchDetail,
    RowResult,
    SolveRequest,
    SolveResponse,
    ValidateRequest,
    ValidateResponse,
)
from app.solver.pattern_index import get_cached_index, pick_best_guess, solve_full_puzzle, solve_row
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")

def _get_library():
    if _loader_module.WORD_LIBRARY is None:
        raise HTTPException(
            status_code=503,
            detail="Word library is not loaded. The service may still be starting up.",
        )
    return _loader_module.WORD_LIBRARY

@router.post("/puzzle/solve", response_model=SolveResponse, tags=["Solver"])
async def solve_puzzle(req: SolveRequest) -> SolveResponse:
    library = _get_library()
    solution = req.solution
    word_len = len(solution)
    
    max_cands = min(
        req.options.max_candidates_per_row,
        MAX_CANDIDATES_HARD_CEILING,
    )

    word_list = library.get_words(word_len)
    row_patterns = [row.pattern for row in req.rows]

    best_path, row_candidates_map = solve_full_puzzle(
        word_list,
        solution,
        row_patterns,
        max_candidates_per_row=max_cands,
        distinct_words=req.options.distinct_words_across_rows,
    )

    row_results: list[RowResult] = []
    unsolvable_row_ids: list[str] = []

    for i, row in enumerate(req.rows):
        candidates = row_candidates_map.get(i, [])
        best = best_path[i] if i < len(best_path) else None

        if not candidates:
            unsolvable_row_ids.append(row.id)
            logger.debug(
                "Row '%s' is unsolvable for solution '%s' with pattern %s",
                row.id,
                solution,
                row.pattern,
            )

        row_results.append(
            RowResult(
                id=row.id,
                pattern=row.pattern,
                candidate_count=len(candidates),
                candidates=candidates,
                best_guess=best,
            )
        )

    return SolveResponse(
        solution=solution,
        word_length=word_len,
        rows=row_results,
        unsolvable_row_ids=unsolvable_row_ids,
    )

@router.post("/feedback/compute", response_model=FeedbackResponse, tags=["Utilities"])
async def compute_feedback(req: FeedbackRequest) -> FeedbackResponse:
    pattern = [c.value for c in get_feedback(req.guess, req.solution)]
    return FeedbackResponse(pattern=pattern)

@router.post("/guess/validate", response_model=ValidateResponse, tags=["Utilities"])
async def validate_guess(req: ValidateRequest) -> ValidateResponse:
    library = _get_library()

    is_real_word = library.contains(req.guess)

    if not is_real_word:
        return ValidateResponse(
            valid=False,
            is_real_word=False,
            computed_pattern=None,
            mismatches=[],
        )

    computed = [c.value for c in get_feedback(req.guess, req.solution)]
    target = req.target_pattern

    mismatches: list[MismatchDetail] = []
    for i, (expected_color, actual_color) in enumerate(zip(target, computed)):
        if expected_color != actual_color:
            mismatches.append(
                MismatchDetail(
                    index=i,
                    expected=expected_color,
                    actual=actual_color,
                    letter=req.guess[i],
                )
            )

    return ValidateResponse(
        valid=len(mismatches) == 0,
        is_real_word=True,
        computed_pattern=computed,
        mismatches=mismatches,
    )

@router.get("/health", response_model=HealthResponse, tags=["Meta"])
async def health_check() -> HealthResponse:
    if _loader_module.WORD_LIBRARY is None:
        return HealthResponse(
            status="degraded",
            library_size=0,
            word_length_distribution={},
        )

    lib = _loader_module.WORD_LIBRARY
    return HealthResponse(
        status="ok",
        library_size=lib.total_words,
        word_length_distribution=lib.length_distribution(),
    )
