"""Emotional Topology API routes."""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter, TorahName
from src.db.models.enrichment import (
    VerseSentiment,
    CharacterEmotion,
    EmotionType,
    DivineSentiment,
)

router = APIRouter()

# Emotion colors for visualization
EMOTION_COLORS = {
    "joy": "#22c55e",        # Green
    "fear": "#7c3aed",       # Purple
    "anger": "#ef4444",      # Red
    "sorrow": "#3b82f6",     # Blue
    "love": "#ec4899",       # Pink
    "awe": "#f59e0b",        # Amber
    "gratitude": "#14b8a6",  # Teal
    "jealousy": "#84cc16",   # Lime
    "shame": "#6b7280",      # Gray
    "hope": "#06b6d4",       # Cyan
    "despair": "#1e293b",    # Slate dark
    "compassion": "#f97316", # Orange
    "neutral": "#94a3b8",    # Slate
}

DIVINE_SENTIMENT_COLORS = {
    "pleased": "#22c55e",
    "displeased": "#f59e0b",
    "angry": "#ef4444",
    "merciful": "#3b82f6",
    "jealous": "#7c3aed",
    "grieved": "#6b7280",
    "neutral": "#94a3b8",
}


@router.get("/terrain")
def get_terrain_data(
    book: Optional[str] = Query(None, description="Filter by book name"),
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
):
    """Get terrain data for 3D visualization - verses with emotional intensity."""
    query = (
        db.query(VerseSentiment, TorahVerse, TorahChapter, TorahBook)
        .join(TorahVerse, VerseSentiment.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
    )

    if book:
        query = query.filter(TorahBook.name == book)

    results = query.order_by(TorahVerse.id).limit(limit).all()

    terrain_points = []
    for sentiment, verse, chapter, book_obj in results:
        terrain_points.append({
            "verse_id": verse.id,
            "ref": verse.ref,
            "book": book_obj.name,
            "chapter": chapter.chapter_number,
            "verse_num": verse.verse_number,
            "x": verse.id,  # Sequential position
            "y": sentiment.emotional_intensity or 0.5,  # Height
            "z": sentiment.tension_level or 0.5,  # Depth
            "polarity": sentiment.sentiment_polarity or 0,
            "emotion": sentiment.primary_emotion.value if sentiment.primary_emotion else "neutral",
            "secondary_emotion": sentiment.secondary_emotion.value if sentiment.secondary_emotion else None,
            "divine_sentiment": sentiment.divine_sentiment.value if sentiment.divine_sentiment else None,
            "color": EMOTION_COLORS.get(
                sentiment.primary_emotion.value if sentiment.primary_emotion else "neutral",
                "#94a3b8"
            ),
            "text_preview": verse.text_hebrew[:50] if verse.text_hebrew else "",
        })

    return {
        "book": book,
        "count": len(terrain_points),
        "points": terrain_points,
    }


@router.get("/chapters")
def get_chapter_emotions(
    book: Optional[str] = Query(None, description="Filter by book name"),
    db: Session = Depends(get_db),
):
    """Get aggregated emotions by chapter for overview."""
    query = (
        db.query(
            TorahBook.name,
            TorahChapter.chapter_number,
            func.avg(VerseSentiment.emotional_intensity).label("avg_intensity"),
            func.avg(VerseSentiment.sentiment_polarity).label("avg_polarity"),
            func.avg(VerseSentiment.tension_level).label("avg_tension"),
            func.count(VerseSentiment.id).label("verse_count"),
        )
        .join(TorahVerse, VerseSentiment.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
    )

    if book:
        query = query.filter(TorahBook.name == book)

    results = (
        query.group_by(TorahBook.name, TorahChapter.chapter_number)
        .order_by(TorahBook.id, TorahChapter.chapter_number)
        .all()
    )

    chapters = []
    for book_name, chapter_num, avg_intensity, avg_polarity, avg_tension, count in results:
        chapters.append({
            "book": book_name,
            "chapter": chapter_num,
            "avg_intensity": round(float(avg_intensity or 0), 3),
            "avg_polarity": round(float(avg_polarity or 0), 3),
            "avg_tension": round(float(avg_tension or 0), 3),
            "verse_count": count,
        })

    return chapters


@router.get("/distribution")
def get_emotion_distribution(
    book: Optional[str] = Query(None, description="Filter by book name"),
    db: Session = Depends(get_db),
):
    """Get distribution of emotions across the text."""
    query = (
        db.query(
            VerseSentiment.primary_emotion,
            func.count(VerseSentiment.id).label("count"),
            func.avg(VerseSentiment.emotional_intensity).label("avg_intensity"),
        )
        .join(TorahVerse, VerseSentiment.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .filter(VerseSentiment.primary_emotion.isnot(None))
    )

    if book:
        query = query.filter(TorahBook.name == book)

    results = (
        query.group_by(VerseSentiment.primary_emotion)
        .order_by(desc("count"))
        .all()
    )

    distribution = []
    for emotion, count, avg_intensity in results:
        emotion_value = emotion.value if emotion else "neutral"
        distribution.append({
            "emotion": emotion_value,
            "count": count,
            "avg_intensity": round(float(avg_intensity or 0), 3),
            "color": EMOTION_COLORS.get(emotion_value, "#94a3b8"),
        })

    return distribution


@router.get("/divine-sentiment")
def get_divine_sentiment_distribution(
    book: Optional[str] = Query(None, description="Filter by book name"),
    db: Session = Depends(get_db),
):
    """Get distribution of divine sentiments."""
    query = (
        db.query(
            VerseSentiment.divine_sentiment,
            func.count(VerseSentiment.id).label("count"),
        )
        .join(TorahVerse, VerseSentiment.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .filter(VerseSentiment.divine_sentiment.isnot(None))
    )

    if book:
        query = query.filter(TorahBook.name == book)

    results = (
        query.group_by(VerseSentiment.divine_sentiment)
        .order_by(desc("count"))
        .all()
    )

    distribution = []
    for sentiment, count in results:
        sentiment_value = sentiment.value if sentiment else "neutral"
        distribution.append({
            "sentiment": sentiment_value,
            "count": count,
            "color": DIVINE_SENTIMENT_COLORS.get(sentiment_value, "#94a3b8"),
        })

    return distribution


@router.get("/characters")
def get_character_emotions(
    book: Optional[str] = Query(None, description="Filter by book name"),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
):
    """Get emotions by character (for character journey visualization)."""
    query = (
        db.query(
            CharacterEmotion.character_name,
            CharacterEmotion.emotion,
            func.count(CharacterEmotion.id).label("count"),
        )
        .join(TorahVerse, CharacterEmotion.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
    )

    if book:
        query = query.filter(TorahBook.name == book)

    results = (
        query.group_by(CharacterEmotion.character_name, CharacterEmotion.emotion)
        .order_by(desc("count"))
        .limit(100)
        .all()
    )

    # Group by character
    characters = {}
    for char_name, emotion, count in results:
        if char_name not in characters:
            characters[char_name] = {"name": char_name, "emotions": {}, "total": 0}
        emotion_value = emotion.value if emotion else "neutral"
        characters[char_name]["emotions"][emotion_value] = count
        characters[char_name]["total"] += count

    # Sort by total and limit
    sorted_chars = sorted(characters.values(), key=lambda x: x["total"], reverse=True)[:limit]

    return sorted_chars


@router.get("/character-journey/{character_name}")
def get_character_journey(
    character_name: str,
    db: Session = Depends(get_db),
):
    """Get emotional journey of a specific character through the narrative."""
    results = (
        db.query(CharacterEmotion, TorahVerse, TorahChapter, TorahBook)
        .join(TorahVerse, CharacterEmotion.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .filter(CharacterEmotion.character_name == character_name)
        .order_by(TorahVerse.id)
        .all()
    )

    journey = []
    for emotion, verse, chapter, book in results:
        emotion_value = emotion.emotion.value if emotion.emotion else "neutral"
        journey.append({
            "verse_id": verse.id,
            "ref": verse.ref,
            "book": book.name,
            "chapter": chapter.chapter_number,
            "emotion": emotion_value,
            "color": EMOTION_COLORS.get(emotion_value, "#94a3b8"),
            "trigger": emotion.trigger,
            "resulting_action": emotion.resulting_action,
            "text_preview": verse.text_hebrew[:50] if verse.text_hebrew else "",
        })

    return {
        "character": character_name,
        "journey_length": len(journey),
        "journey": journey,
    }


@router.get("/peaks")
def get_emotional_peaks(
    book: Optional[str] = Query(None, description="Filter by book name"),
    threshold: float = Query(0.8, description="Intensity threshold"),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
):
    """Get verses with highest emotional intensity (peaks in the terrain)."""
    query = (
        db.query(VerseSentiment, TorahVerse, TorahChapter, TorahBook)
        .join(TorahVerse, VerseSentiment.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .filter(VerseSentiment.emotional_intensity >= threshold)
    )

    if book:
        query = query.filter(TorahBook.name == book)

    results = (
        query.order_by(desc(VerseSentiment.emotional_intensity))
        .limit(limit)
        .all()
    )

    peaks = []
    for sentiment, verse, chapter, book_obj in results:
        emotion_value = sentiment.primary_emotion.value if sentiment.primary_emotion else "neutral"
        peaks.append({
            "verse_id": verse.id,
            "ref": verse.ref,
            "book": book_obj.name,
            "chapter": chapter.chapter_number,
            "intensity": sentiment.emotional_intensity,
            "polarity": sentiment.sentiment_polarity,
            "tension": sentiment.tension_level,
            "emotion": emotion_value,
            "color": EMOTION_COLORS.get(emotion_value, "#94a3b8"),
            "text_hebrew": verse.text_hebrew,
            "text_english": verse.text_english,
            "context": sentiment.context_notes,
        })

    return peaks


@router.get("/stats")
def get_emotional_stats(
    book: Optional[str] = Query(None, description="Filter by book name"),
    db: Session = Depends(get_db),
):
    """Get overall emotional statistics."""
    query = db.query(VerseSentiment).join(TorahVerse).join(TorahChapter).join(TorahBook)

    if book:
        query = query.filter(TorahBook.name == book)

    total = query.count()

    # Average metrics
    avg_query = db.query(
        func.avg(VerseSentiment.emotional_intensity).label("avg_intensity"),
        func.avg(VerseSentiment.sentiment_polarity).label("avg_polarity"),
        func.avg(VerseSentiment.tension_level).label("avg_tension"),
        func.max(VerseSentiment.emotional_intensity).label("max_intensity"),
        func.min(VerseSentiment.emotional_intensity).label("min_intensity"),
    ).join(TorahVerse).join(TorahChapter).join(TorahBook)

    if book:
        avg_query = avg_query.filter(TorahBook.name == book)

    avgs = avg_query.first()

    # Character emotion count
    char_count = db.query(CharacterEmotion).join(TorahVerse).join(TorahChapter).join(TorahBook)
    if book:
        char_count = char_count.filter(TorahBook.name == book)

    return {
        "book": book or "All",
        "total_verses_analyzed": total,
        "character_emotions_count": char_count.count(),
        "avg_intensity": round(float(avgs.avg_intensity or 0), 3),
        "avg_polarity": round(float(avgs.avg_polarity or 0), 3),
        "avg_tension": round(float(avgs.avg_tension or 0), 3),
        "max_intensity": round(float(avgs.max_intensity or 0), 3),
        "min_intensity": round(float(avgs.min_intensity or 0), 3),
    }


@router.get("/emotion-types")
def get_emotion_types():
    """Get available emotion types with their colors."""
    return [
        {"type": e.value, "color": EMOTION_COLORS.get(e.value, "#94a3b8")}
        for e in EmotionType
    ]


@router.get("/divine-sentiment-types")
def get_divine_sentiment_types():
    """Get available divine sentiment types with their colors."""
    return [
        {"type": s.value, "color": DIVINE_SENTIMENT_COLORS.get(s.value, "#94a3b8")}
        for s in DivineSentiment
    ]
