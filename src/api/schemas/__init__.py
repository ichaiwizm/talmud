"""Pydantic schemas for API."""
from .common import PaginatedResponse, ErrorResponse
from .books import BookSummary, BookDetail, ChapterResponse, VerseResponse
from .names import NameSummary, NameDetail, NameType, VerseOccurrence
from .gematria import GematriaMethod, GematriaCalculation, WordMatch, VerseMatch
from .stats import GlobalStats, ImportStatus, ExtractionStatus

__all__ = [
    "PaginatedResponse", "ErrorResponse",
    "BookSummary", "BookDetail", "ChapterResponse", "VerseResponse",
    "NameSummary", "NameDetail", "NameType", "VerseOccurrence",
    "GematriaMethod", "GematriaCalculation", "WordMatch", "VerseMatch",
    "GlobalStats", "ImportStatus", "ExtractionStatus",
]
