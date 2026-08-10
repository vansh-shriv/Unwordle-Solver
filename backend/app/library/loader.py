from __future__ import annotations

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# The maximum number of letters a word can have to be included.
# Practically this just keeps memory tidy; the solver always filters by
# len(solution) anyway.
_MAX_WORD_LEN = 20

# Regex: only pure A-Z letters are valid after normalization.
_ALPHA_RE = re.compile(r"^[A-Z]+$")


class WordLibrary:
    def __init__(self) -> None:
        self.words_by_length: dict[int, list[str]] = {}
        self.total_words: int = 0
        self.word_set: set[str] = set()
        self.word_ranks: dict[str, int] = {}

    def get_words(self, length: int) -> list[str]:
        return self.words_by_length.get(length, [])

    def contains(self, word: str) -> bool:
        return word.upper() in self.word_set

    def get_rank(self, word: str) -> int:
        return self.word_ranks.get(word.upper(), 999999)

    def length_distribution(self) -> dict[str, int]:
        return {str(k): len(v) for k, v in sorted(self.words_by_length.items())}


def load_library(path: Path) -> WordLibrary:
    if not path.exists():
        raise FileNotFoundError(
            f"Word library not found at '{path}'. "
            "Check DATA_PATH configuration and make sure the file exists."
        )

    suffix = path.suffix.lower()
    raw_entries: list[str] = []

    if suffix == ".txt":
        raw_entries = _load_txt(path)
    elif suffix == ".json":
        raw_entries = _load_json(path)
    else:
        raise ValueError(
            f"Unsupported word library format '{suffix}'. "
            "Expected .txt or .json."
        )

    if not raw_entries:
        raise ValueError(
            f"Word library at '{path}' loaded but contained zero entries. "
            "The file may be empty or all entries were rejected during normalization."
        )

    library = _normalize_and_group(raw_entries)

    if library.total_words == 0:
        raise ValueError(
            f"Word library at '{path}' contained entries but NONE survived "
            "normalization (must be pure A-Z after stripping whitespace). "
            "Check the file contents."
        )

    logger.info(
        "Word library loaded: %d total words, lengths: %s",
        library.total_words,
        library.length_distribution(),
    )
    return library

def _load_txt(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip()]


def _load_json(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, list):
        raise ValueError("JSON word library must be a top-level array.")

    entries: list[str] = []
    for item in data:
        if isinstance(item, str):
            entries.append(item)
        elif isinstance(item, dict):
            word = item.get("word", "")
            if isinstance(word, str) and word:
                entries.append(word)
            else:
                logger.warning("Skipping JSON object with no usable 'word' key: %r", item)
        else:
            logger.warning("Skipping unexpected JSON entry type %s: %r", type(item), item)
    return entries


def _normalize_and_group(raw: list[str]) -> WordLibrary:
    library = WordLibrary()
    seen: set[str] = set()
    rejected = 0
    rank = 0

    for raw_word in raw:
        cleaned = re.sub(r"[^A-Za-z]", "", raw_word.strip()).upper()

        if not cleaned:
            rejected += 1
            continue

        if not _ALPHA_RE.match(cleaned):
            logger.debug("Rejecting non-alphabetic entry after normalization: %r", raw_word)
            rejected += 1
            continue

        if len(cleaned) > _MAX_WORD_LEN:
            rejected += 1
            continue

        if cleaned in seen:
            continue

        seen.add(cleaned)
        library.word_ranks[cleaned] = rank
        rank += 1

        length = len(cleaned)
        library.words_by_length.setdefault(length, []).append(cleaned)

    library.word_set = seen
    library.total_words = sum(len(v) for v in library.words_by_length.values())

    if rejected:
        logger.info("Rejected %d entries during normalization.", rejected)

    return library

WORD_LIBRARY: WordLibrary | None = None
