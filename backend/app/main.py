from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.library.loader as _loader_module
from app.api.routes import router
from app.library.loader import load_library

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

_DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "unwordle.txt"
DATA_PATH = Path(os.environ.get("DATA_PATH", str(_DEFAULT_DATA_PATH)))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading word library from: %s", DATA_PATH)
    try:
        _loader_module.WORD_LIBRARY = load_library(DATA_PATH)
        logger.info(
            "Word library ready — %d total words.",
            _loader_module.WORD_LIBRARY.total_words,
        )
    except (FileNotFoundError, ValueError) as exc:
        logger.critical("FATAL: Failed to load word library: %s", exc)
        raise RuntimeError(f"Word library load failure: {exc}") from exc

    yield

    logger.info("UnWordle solver shutting down.")

app = FastAPI(
    title="UnWordle Solver API",
    version="1.0.0",
    description=(
        "Backend solver for unwordle.org — given a puzzle's solution word and "
        "each row's locked color pattern, returns all valid candidate words."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
