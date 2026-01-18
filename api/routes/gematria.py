"""Gematria API routes."""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc, distinct
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter
from src.db.models.gematria import TorahWord
from src.utils.hebrew import (
    calculate_all,
    GematriaMethod,
    HEBREW_LETTERS,
)
from src.utils.hebrew.constants import GEMATRIA_STANDARD
from src.services.gematria.search import (
    search_words_by_gematria,
    search_verses_by_gematria,
    get_gematria_stats,
)

router = APIRouter()

# Notable numbers with spiritual significance
NOTABLE_NUMBERS = [
    {"value": 26, "hebrew": "יהוה", "name": "YHWH", "description": "Le Tétragramme, le Nom ineffable"},
    {"value": 86, "hebrew": "אלהים", "name": "Elohim", "description": "Dieu, le Créateur"},
    {"value": 18, "hebrew": "חי", "name": "Chai", "description": "Vie, vivant"},
    {"value": 13, "hebrew": "אחד", "name": "Echad", "description": "Un, unité"},
    {"value": 13, "hebrew": "אהבה", "name": "Ahavah", "description": "Amour"},
    {"value": 72, "hebrew": "חסד", "name": "Chesed", "description": "Bonté, miséricorde"},
    {"value": 611, "hebrew": "תורה", "name": "Torah", "description": "La Torah, la Loi"},
    {"value": 314, "hebrew": "שדי", "name": "Shaddai", "description": "Le Tout-Puissant"},
    {"value": 45, "hebrew": "אדם", "name": "Adam", "description": "Homme, humanité"},
    {"value": 50, "hebrew": "כל", "name": "Kol", "description": "Tout, totalité"},
    {"value": 248, "hebrew": "אברהם", "name": "Abraham", "description": "Abraham, père des nations"},
    {"value": 541, "hebrew": "ישראל", "name": "Israel", "description": "Israël"},
    {"value": 358, "hebrew": "משיח", "name": "Mashiach", "description": "Messie, l'oint"},
    {"value": 358, "hebrew": "נחש", "name": "Nachash", "description": "Serpent"},
    {"value": 40, "hebrew": "מים", "name": "Mayim", "description": "Eau"},
    {"value": 91, "hebrew": "אמן", "name": "Amen", "description": "Amen, ainsi soit-il"},
]


@router.get("/calculate")
def calculate_gematria(
    text: str = Query(..., description="Hebrew text to calculate gematria for"),
):
    """Calculate all 4 gematria values for the given text with letter breakdown."""
    values = calculate_all(text)

    # Create letter breakdown
    breakdown = []
    for char in text:
        if char in GEMATRIA_STANDARD:
            breakdown.append({
                "letter": char,
                "standard": GEMATRIA_STANDARD.get(char, 0),
            })

    return {
        "input": text,
        "values": values,
        "letter_count": len(breakdown),
        "breakdown": breakdown,
    }


@router.get("/search/words")
def search_words(
    value: int = Query(..., description="Gematria value to search for"),
    method: str = Query("standard", description="Gematria method"),
    book: Optional[str] = Query(None, description="Filter by book name"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Find all words with a specific gematria value."""
    results = search_words_by_gematria(db, value, method, book, limit)
    return {
        "value": value,
        "method": method,
        "book": book,
        "count": len(results),
        "words": results,
    }


@router.get("/search/verses")
def search_verses(
    value: int = Query(..., description="Gematria value to search for"),
    method: str = Query("standard", description="Gematria method"),
    book: Optional[str] = Query(None, description="Filter by book name"),
    limit: int = Query(30, le=100),
    db: Session = Depends(get_db),
):
    """Find all verses with a specific total gematria value."""
    results = search_verses_by_gematria(db, value, method, book, limit)
    return {
        "value": value,
        "method": method,
        "book": book,
        "count": len(results),
        "verses": results,
    }


@router.get("/notable-numbers")
def get_notable_numbers():
    """Get list of spiritually significant numbers with metadata."""
    # Calculate gematria values to verify
    for item in NOTABLE_NUMBERS:
        computed = calculate_all(item["hebrew"])
        item["computed_standard"] = computed["standard"]

    return NOTABLE_NUMBERS


@router.get("/distribution")
def get_distribution(
    book: Optional[str] = Query(None, description="Filter by book name"),
    limit: int = Query(30, le=100),
    db: Session = Depends(get_db),
):
    """Get frequency distribution of gematria values."""
    query = db.query(
        TorahWord.gematria_standard,
        func.count(TorahWord.id).label("count"),
    )

    if book:
        query = (
            query.join(TorahVerse, TorahWord.verse_id == TorahVerse.id)
            .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
            .join(TorahBook, TorahChapter.book_id == TorahBook.id)
            .filter(TorahBook.name == book)
        )

    results = (
        query.filter(TorahWord.gematria_standard.isnot(None))
        .group_by(TorahWord.gematria_standard)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )

    return [
        {"value": value, "count": count}
        for value, count in results
    ]


@router.get("/connections")
def get_connections(
    value: int = Query(..., description="Gematria value to find connections for"),
    limit: int = Query(30, le=100),
    db: Session = Depends(get_db),
):
    """Get all distinct words sharing a gematria value (for network visualization)."""
    # Get distinct words with this value
    results = (
        db.query(
            TorahWord.word_normalized,
            TorahWord.word_original,
            func.count(TorahWord.id).label("occurrence_count"),
        )
        .filter(TorahWord.gematria_standard == value)
        .group_by(TorahWord.word_normalized, TorahWord.word_original)
        .order_by(desc("occurrence_count"))
        .limit(limit)
        .all()
    )

    # Get sample verse references for each word
    connections = []
    for word_norm, word_orig, count in results:
        # Get a few sample verses
        samples = (
            db.query(TorahVerse.ref)
            .join(TorahWord, TorahWord.verse_id == TorahVerse.id)
            .filter(TorahWord.word_normalized == word_norm)
            .limit(3)
            .all()
        )

        connections.append({
            "word": word_orig,
            "word_normalized": word_norm,
            "occurrences": count,
            "sample_refs": [ref for (ref,) in samples],
        })

    return {
        "value": value,
        "unique_words": len(connections),
        "connections": connections,
    }


@router.get("/stats")
def get_stats(
    book: Optional[str] = Query(None, description="Filter by book name"),
    db: Session = Depends(get_db),
):
    """Get gematria statistics."""
    return get_gematria_stats(db, book)


@router.get("/letters")
def get_hebrew_letters():
    """Get all Hebrew letters with their gematria values."""
    # Standard 22-letter alphabet in order
    ordered_letters = "אבגדהוזחטיכלמנסעפצקרשת"

    letters = []
    for i, letter in enumerate(ordered_letters):
        letters.append({
            "letter": letter,
            "position": i + 1,
            "standard": GEMATRIA_STANDARD.get(letter, 0),
        })

    return letters


@router.get("/methods")
def get_methods():
    """Get available gematria calculation methods."""
    return {
        "methods": [
            {
                "id": "standard",
                "name": "Mispar Gadol",
                "description": "Standard gematria (א=1, ב=2... י=10, כ=20... ק=100...)",
            },
            {
                "id": "katan",
                "name": "Mispar Katan",
                "description": "Small gematria (reduces to 1-9 cycle)",
            },
            {
                "id": "ordinal",
                "name": "Mispar Siduri",
                "description": "Ordinal position in alphabet (1-22)",
            },
            {
                "id": "atbash",
                "name": "Atbash",
                "description": "Atbash cipher (א↔ת, ב↔ש...) then standard",
            },
        ]
    }
