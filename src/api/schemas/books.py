"""Schemas for Torah books, chapters, and verses."""
from pydantic import BaseModel


class BookSummary(BaseModel):
    """Summary of a Torah book."""
    id: int
    name: str
    hebrew_name: str
    order: int
    total_chapters: int

    model_config = {"from_attributes": True}


class ChapterSummary(BaseModel):
    """Summary of a chapter."""
    number: int
    total_verses: int

    model_config = {"from_attributes": True}


class BookDetail(BaseModel):
    """Detailed book info with chapters."""
    id: int
    name: str
    hebrew_name: str
    order: int
    total_chapters: int
    chapters: list[ChapterSummary]

    model_config = {"from_attributes": True}


class VerseResponse(BaseModel):
    """Single verse response."""
    id: int
    ref: str
    he_ref: str
    text_hebrew: str
    text_english: str
    chapter: int
    verse: int
    processed: bool
    word_count: int | None = None
    gematria_standard_total: int | None = None
    gematria_katan_total: int | None = None

    model_config = {"from_attributes": True}


class ChapterResponse(BaseModel):
    """Chapter with all verses."""
    book_name: str
    chapter_number: int
    total_verses: int
    verses: list[VerseResponse]
