"""Schemas for gematria calculations."""
from pydantic import BaseModel
from enum import Enum


class GematriaMethod(str, Enum):
    """Gematria calculation methods."""
    STANDARD = "standard"
    KATAN = "katan"
    ORDINAL = "ordinal"
    ATBASH = "atbash"


class GematriaCalculation(BaseModel):
    """Result of gematria calculation."""
    text: str
    standard: int
    katan: int
    ordinal: int
    atbash: int


class WordMatch(BaseModel):
    """A word matching a gematria value."""
    word: str
    word_normalized: str
    verse_ref: str
    position: int
    gematria: int
    verse_text_hebrew: str
    verse_text_english: str


class VerseMatch(BaseModel):
    """A verse matching a gematria value."""
    ref: str
    text_hebrew: str
    text_english: str
    gematria_total: int
    word_count: int


class GematriaMatchResponse(BaseModel):
    """Response for gematria matching."""
    input_text: str
    method: str
    calculated_value: int
    match_count: int
    matches: list[WordMatch | VerseMatch]


class GematriaStats(BaseModel):
    """Statistics about gematria data."""
    book: str | None = None
    total_words: int
    verses_populated: int
    total_verses: int
    population_percent: float
    top_values: list[dict]
