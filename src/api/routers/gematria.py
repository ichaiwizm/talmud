"""Gematria calculation and search routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas.gematria import (
    GematriaMethod, GematriaCalculation, WordMatch, VerseMatch, GematriaStats
)
from src.utils.hebrew import calculate_all, GematriaMethod as GM
from src.services.gematria.search import (
    search_words_by_gematria, search_verses_by_gematria,
    find_gematria_matches, get_gematria_stats
)

router = APIRouter(prefix="/gematria", tags=["Gematria"])


@router.get("/calculate", response_model=GematriaCalculation)
def calculate_gematria(text: str = Query(..., min_length=1, description="Hebrew text")):
    """Calculate gematria for Hebrew text using all 4 methods."""
    results = calculate_all(text)
    return GematriaCalculation(text=text, **results)


@router.get("/words", response_model=list[WordMatch])
def search_words(
    value: int = Query(..., ge=1, description="Gematria value to search"),
    method: GematriaMethod = Query(GematriaMethod.STANDARD),
    book: str | None = Query(None, description="Filter by book name"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Search words by gematria value."""
    results = search_words_by_gematria(db, value, method.value, book, limit)
    return [WordMatch(**r) for r in results]


@router.get("/verses", response_model=list[VerseMatch])
def search_verses(
    value: int = Query(..., ge=1, description="Gematria value to search"),
    method: GematriaMethod = Query(GematriaMethod.STANDARD),
    book: str | None = Query(None, description="Filter by book name"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Search verses by total gematria value."""
    results = search_verses_by_gematria(db, value, method.value, book, limit)
    return [VerseMatch(**r) for r in results]


@router.get("/match")
def find_matches(
    text: str = Query(..., min_length=1, description="Text to find matches for"),
    method: GematriaMethod = Query(GematriaMethod.STANDARD),
    search_type: str = Query("words", enum=["words", "verses"]),
    book: str | None = Query(None, description="Filter by book name"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Find words/verses with same gematria as input text."""
    return find_gematria_matches(db, text, method.value, search_type, book, limit)


@router.get("/stats", response_model=GematriaStats)
def gematria_stats(book: str | None = None, db: Session = Depends(get_db)):
    """Get gematria statistics."""
    result = get_gematria_stats(db, book)
    return GematriaStats(
        book=result.get("book"),
        total_words=result["total_words"],
        verses_populated=result["verses_populated"],
        total_verses=result["total_verses"],
        population_percent=result["population_percent"],
        top_values=result["top_gematria_values"]
    )
