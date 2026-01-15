"""Gematria search service."""

from typing import Optional, List
from sqlalchemy import func, desc
from sqlalchemy.orm import Session, joinedload

from src.db.models.torah import TorahVerse, TorahChapter, TorahBook
from src.db.models.gematria import TorahWord
from src.utils.hebrew import GematriaMethod, calculate


def search_words_by_gematria(
    db: Session,
    value: int,
    method: str = GematriaMethod.STANDARD,
    book_name: Optional[str] = None,
    limit: int = 100,
) -> List[dict]:
    """Find all words with a specific gematria value."""
    column_map = {
        GematriaMethod.STANDARD: TorahWord.gematria_standard,
        GematriaMethod.KATAN: TorahWord.gematria_katan,
        GematriaMethod.ORDINAL: TorahWord.gematria_ordinal,
        GematriaMethod.ATBASH: TorahWord.gematria_atbash,
    }

    column = column_map.get(method)
    if not column:
        raise ValueError(f"Unknown method: {method}")

    query = (
        db.query(TorahWord)
        .options(joinedload(TorahWord.verse))
        .filter(column == value)
    )

    if book_name:
        query = (
            query.join(TorahVerse)
            .join(TorahChapter)
            .join(TorahBook)
            .filter(TorahBook.name == book_name)
        )

    results = query.order_by(TorahWord.id).limit(limit).all()

    return [
        {
            "word": w.word_original,
            "word_normalized": w.word_normalized,
            "verse_ref": w.verse.ref,
            "position": w.position,
            "gematria": getattr(w, f"gematria_{method}"),
            "verse_text_hebrew": w.verse.text_hebrew,
            "verse_text_english": w.verse.text_english,
        }
        for w in results
    ]


def search_verses_by_gematria(
    db: Session,
    value: int,
    method: str = GematriaMethod.STANDARD,
    book_name: Optional[str] = None,
    limit: int = 50,
) -> List[dict]:
    """Find all verses with a specific total gematria."""
    column_map = {
        GematriaMethod.STANDARD: TorahVerse.gematria_standard_total,
        GematriaMethod.KATAN: TorahVerse.gematria_katan_total,
    }

    column = column_map.get(method)
    if not column:
        raise ValueError(f"Verse-level gematria not available for: {method}")

    query = db.query(TorahVerse).filter(column == value)

    if book_name:
        query = (
            query.join(TorahChapter)
            .join(TorahBook)
            .filter(TorahBook.name == book_name)
        )

    results = query.order_by(TorahVerse.id).limit(limit).all()

    return [
        {
            "ref": v.ref,
            "text_hebrew": v.text_hebrew,
            "text_english": v.text_english,
            "gematria_total": getattr(v, f"gematria_{method}_total"),
            "word_count": v.word_count,
        }
        for v in results
    ]


def find_gematria_matches(
    db: Session,
    text: str,
    method: str = GematriaMethod.STANDARD,
    search_type: str = "words",
    book_name: Optional[str] = None,
    limit: int = 50,
) -> dict:
    """Find words/verses matching the gematria of given text."""
    value = calculate(text, GematriaMethod(method))

    if search_type == "words":
        matches = search_words_by_gematria(db, value, method, book_name, limit)
    else:
        matches = search_verses_by_gematria(db, value, method, book_name, limit)

    return {
        "input_text": text,
        "method": method,
        "calculated_value": value,
        "match_count": len(matches),
        "matches": matches,
    }


def get_gematria_stats(db: Session, book_name: Optional[str] = None) -> dict:
    """Get gematria statistics."""
    query = db.query(TorahWord)

    if book_name:
        query = (
            query.join(TorahVerse)
            .join(TorahChapter)
            .join(TorahBook)
            .filter(TorahBook.name == book_name)
        )

    total_words = query.count()

    # Most common gematria values
    top_values = (
        db.query(
            TorahWord.gematria_standard, func.count(TorahWord.id).label("count")
        )
        .group_by(TorahWord.gematria_standard)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    # Verses populated
    verses_with_words = (
        db.query(TorahVerse).filter(TorahVerse.word_count.isnot(None)).count()
    )
    total_verses = db.query(TorahVerse).count()

    return {
        "book": book_name or "All",
        "total_words": total_words,
        "verses_populated": verses_with_words,
        "total_verses": total_verses,
        "population_percent": round(verses_with_words / total_verses * 100, 1)
        if total_verses
        else 0,
        "top_gematria_values": [
            {"value": val, "count": cnt} for val, cnt in top_values
        ],
    }
