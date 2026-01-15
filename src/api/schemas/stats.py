"""Schemas for statistics and admin operations."""
from pydantic import BaseModel


class GlobalStats(BaseModel):
    """Global statistics."""
    book: str | None = None
    books: int
    chapters: int
    verses: int
    processed: int
    progress_percent: float
    unique_names: int
    total_occurrences: int
    type_distribution: dict[str, int]


class ImportStatus(BaseModel):
    """Torah import status."""
    books: int
    chapters: int
    verses: int
    expected_books: int = 5


class ExtractionStatus(BaseModel):
    """Name extraction status."""
    total_verses: int
    processed: int
    pending: int
    with_errors: int
    unique_names: int
    total_occurrences: int
    progress_percent: float


class ExtractionRequest(BaseModel):
    """Request to start extraction."""
    limit: int | None = None
    batch_size: int = 50
    parallel: bool = False
    workers: int = 1


class PopulateRequest(BaseModel):
    """Request to populate gematria."""
    limit: int | None = None
    book: str | None = None


class GematriaPopulationStatus(BaseModel):
    """Gematria population status."""
    total_verses: int
    verses_populated: int
    pending: int
    total_words: int
    progress_percent: float
