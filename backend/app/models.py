from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, model_validator

VALID_COLORS = {"green", "yellow", "gray"}
MAX_CANDIDATES_HARD_CEILING = 200

class RowRequest(BaseModel):
    id: str = Field(..., description="Caller-supplied row identifier, e.g. 'row_1'.")
    pattern: list[str] = Field(
        ...,
        description="Ordered list of color strings: 'green', 'yellow', or 'gray'.",
    )
    @field_validator("pattern", mode="before")
    @classmethod
    def normalize_pattern(cls, v: list) -> list[str]:
        return [c.lower() if isinstance(c, str) else c for c in v]


class SolveOptions(BaseModel):
    max_candidates_per_row: int = Field(
        default=20,
        ge=1,
        description="Maximum candidates to return per row. Hard-capped server-side at 200.",
    )
    distinct_words_across_rows: bool = Field(
        default=False,
        description=(
            "If true, exclude words already used in earlier rows from subsequent rows. "
            "Uses greedy exclusion; dead-ends are reported in unsolvable_row_ids."
        ),
    )


class SolveRequest(BaseModel):
    solution: str = Field(..., description="The known final word for this puzzle.")
    rows: list[RowRequest] = Field(..., min_length=1, description="The puzzle rows.")
    options: SolveOptions = Field(default_factory=SolveOptions)

    @field_validator("solution", mode="before")
    @classmethod
    def normalize_solution(cls, v: str) -> str:
        return v.strip().upper()

    @model_validator(mode="after")
    def validate_lengths_and_colors(self) -> "SolveRequest":
        word_len = len(self.solution)
        for row in self.rows:
            # Pattern length must match solution length
            if len(row.pattern) != word_len:
                raise ValueError(
                    f"Row '{row.id}': pattern has {len(row.pattern)} colors but "
                    f"solution '{self.solution}' has {word_len} letters. "
                    "Pattern length must equal solution length."
                )
            # All color values must be valid
            bad = [c for c in row.pattern if c not in VALID_COLORS]
            if bad:
                raise ValueError(
                    f"Row '{row.id}': invalid color value(s) {bad!r}. "
                    "Each color must be 'green', 'yellow', or 'gray'."
                )
        return self


class FeedbackRequest(BaseModel):
    guess: str = Field(..., description="The word to score.")
    solution: str = Field(..., description="The known solution to score against.")

    @field_validator("guess", "solution", mode="before")
    @classmethod
    def normalize(cls, v: str) -> str:
        return v.strip().upper()

    @model_validator(mode="after")
    def validate_same_length(self) -> "FeedbackRequest":
        if len(self.guess) != len(self.solution):
            raise ValueError(
                f"'guess' ({len(self.guess)} letters) and 'solution' "
                f"({len(self.solution)} letters) must be the same length."
            )
        return self


class ValidateRequest(BaseModel):
    guess: str = Field(..., description="The word to validate.")
    solution: str = Field(..., description="The known solution.")
    target_pattern: list[str] = Field(
        ..., description="The row's locked color pattern."
    )

    @field_validator("guess", "solution", mode="before")
    @classmethod
    def normalize(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("target_pattern", mode="before")
    @classmethod
    def normalize_pattern(cls, v: list) -> list[str]:
        return [c.lower() if isinstance(c, str) else c for c in v]

    @model_validator(mode="after")
    def validate_lengths_and_colors(self) -> "ValidateRequest":
        word_len = len(self.solution)
        if len(self.guess) != word_len:
            raise ValueError(
                f"'guess' length ({len(self.guess)}) must equal "
                f"'solution' length ({word_len})."
            )
        if len(self.target_pattern) != word_len:
            raise ValueError(
                f"'target_pattern' length ({len(self.target_pattern)}) must equal "
                f"'solution' length ({word_len})."
            )
        bad = [c for c in self.target_pattern if c not in VALID_COLORS]
        if bad:
            raise ValueError(
                f"Invalid color value(s) in target_pattern: {bad!r}. "
                "Must be 'green', 'yellow', or 'gray'."
            )
        return self

class RowResult(BaseModel):
    id: str
    pattern: list[str]
    candidate_count: int
    candidates: list[str]
    best_guess: str | None


class SolveResponse(BaseModel):
    solution: str
    word_length: int
    rows: list[RowResult]
    unsolvable_row_ids: list[str]


class FeedbackResponse(BaseModel):
    pattern: list[str]


class MismatchDetail(BaseModel):
    index: int
    expected: str
    actual: str
    letter: str


class ValidateResponse(BaseModel):
    valid: bool
    is_real_word: bool
    computed_pattern: list[str] | None
    mismatches: list[MismatchDetail]

class HealthResponse(BaseModel):
    status: str
    library_size: int
    word_length_distribution: dict[str, int]
