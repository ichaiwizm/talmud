"""Constellation routes - verses as stars with connections."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter
from src.db.models.enrichment import VerseSentiment, CrossReference, EmotionType

router = APIRouter()


@router.get("/verses")
def get_constellation_verses(
    book: str | None = None,
    limit: int = Query(default=200, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get verses with sentiment data for constellation visualization."""
    query = (
        db.query(TorahVerse, VerseSentiment, TorahBook.name, TorahChapter.number)
        .outerjoin(VerseSentiment, TorahVerse.id == VerseSentiment.verse_id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
    )

    if book:
        query = query.filter(TorahBook.name == book)

    total = query.count()
    results = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "verses": [
            {
                "id": verse.id,
                "ref": verse.ref,
                "book": book_name,
                "chapter": chapter_num,
                "verse_num": verse.number,
                "text_preview": verse.text_english[:100] + "..." if len(verse.text_english) > 100 else verse.text_english,
                "gematria": verse.gematria_standard_total or 0,
                "emotion": sentiment.primary_emotion.value if sentiment and sentiment.primary_emotion else None,
                "intensity": sentiment.emotional_intensity if sentiment else 0.5,
                "polarity": sentiment.sentiment_polarity if sentiment else 0,
            }
            for verse, sentiment, book_name, chapter_num in results
        ],
    }


@router.get("/connections")
def get_connections(
    book: str | None = None,
    limit: int = Query(default=100, le=300),
    db: Session = Depends(get_db),
):
    """Get cross-references between verses."""
    query = db.query(CrossReference)

    if book:
        # Filter by book (source verse)
        query = (
            query.join(TorahVerse, CrossReference.source_verse_id == TorahVerse.id)
            .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
            .join(TorahBook, TorahChapter.book_id == TorahBook.id)
            .filter(TorahBook.name == book)
        )

    results = query.limit(limit).all()

    return [
        {
            "source_id": ref.source_verse_id,
            "target_id": ref.target_verse_id,
            "type": ref.reference_type.value if ref.reference_type else "thematic",
            "strength": ref.similarity_score or 0.5,
        }
        for ref in results
    ]


@router.get("/emotion-summary")
def get_emotion_summary(db: Session = Depends(get_db)):
    """Get summary of emotions across verses."""
    results = (
        db.query(
            VerseSentiment.primary_emotion,
            func.count(VerseSentiment.id).label("count"),
            func.avg(VerseSentiment.emotional_intensity).label("avg_intensity"),
        )
        .filter(VerseSentiment.primary_emotion.isnot(None))
        .group_by(VerseSentiment.primary_emotion)
        .all()
    )

    return {
        row.primary_emotion.value: {
            "count": row.count,
            "avg_intensity": round(row.avg_intensity or 0, 2),
        }
        for row in results
    }


@router.get("/book-summary")
def get_book_summary(db: Session = Depends(get_db)):
    """Get verse counts and sentiment summary by book."""
    results = (
        db.query(
            TorahBook.name,
            func.count(TorahVerse.id).label("verse_count"),
        )
        .join(TorahChapter, TorahBook.id == TorahChapter.book_id)
        .join(TorahVerse, TorahChapter.id == TorahVerse.chapter_id)
        .group_by(TorahBook.name)
        .order_by(TorahBook.order)
        .all()
    )

    return [{"book": row.name, "count": row.verse_count} for row in results]
