"""Living Scroll routes - verses with words, roots, and speech."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter
from src.db.models.gematria import TorahWord
from src.db.models.enrichment import VerseSentiment
from src.db.models.linguistic import HebrewRoot, WordRoot
from src.db.models.relationships import DirectSpeech

router = APIRouter()


@router.get("/verses")
def get_scroll_verses(
    book: str = "Genesis",
    chapter: int = 1,
    db: Session = Depends(get_db),
):
    """Get verses with full text for a chapter."""
    query = (
        db.query(TorahVerse, VerseSentiment)
        .outerjoin(VerseSentiment, TorahVerse.id == VerseSentiment.verse_id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .filter(TorahBook.name == book)
        .filter(TorahChapter.number == chapter)
        .order_by(TorahVerse.number)
    )

    results = query.all()

    return [
        {
            "id": verse.id,
            "number": verse.number,
            "ref": verse.ref,
            "text_hebrew": verse.text_hebrew,
            "text_english": verse.text_english,
            "emotion": sentiment.primary_emotion.value if sentiment and sentiment.primary_emotion else None,
            "intensity": sentiment.emotional_intensity if sentiment else 0.5,
            "tension": sentiment.tension_level if sentiment else 0.3,
            "polarity": sentiment.sentiment_polarity if sentiment else 0,
        }
        for verse, sentiment in results
    ]


@router.get("/words/{verse_id}")
def get_verse_words(verse_id: int, db: Session = Depends(get_db)):
    """Get individual words for a verse with gematria and root info."""
    words = (
        db.query(TorahWord, WordRoot, HebrewRoot)
        .outerjoin(WordRoot, TorahWord.id == WordRoot.word_id)
        .outerjoin(HebrewRoot, WordRoot.root_id == HebrewRoot.id)
        .filter(TorahWord.verse_id == verse_id)
        .order_by(TorahWord.position)
        .all()
    )

    return [
        {
            "id": word.id,
            "position": word.position,
            "word": word.word_original,
            "normalized": word.word_normalized,
            "gematria": word.gematria_standard,
            "root": root.root_letters if root else None,
            "root_meaning": root.basic_meaning if root else None,
            "root_id": root.id if root else None,
        }
        for word, word_root, root in words
    ]


@router.get("/speech")
def get_direct_speech(
    book: str = "Genesis",
    chapter: int = 1,
    db: Session = Depends(get_db),
):
    """Get direct speech instances for a chapter."""
    query = (
        db.query(DirectSpeech, TorahVerse)
        .join(TorahVerse, DirectSpeech.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .filter(TorahBook.name == book)
        .filter(TorahChapter.number == chapter)
    )

    results = query.all()

    return [
        {
            "verse_id": speech.verse_id,
            "verse_num": verse.number,
            "speaker_name": speech.speaker_id,  # Would need join to get name
            "speech_type": speech.speech_type.value if speech.speech_type else None,
            "is_divine": speech.is_divine_speech,
            "text": speech.speech_text or "",
        }
        for speech, verse in results
    ]


@router.get("/roots/{root_id}/occurrences")
def get_root_occurrences(root_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Get all words sharing a Hebrew root."""
    words = (
        db.query(TorahWord, TorahVerse)
        .join(WordRoot, TorahWord.id == WordRoot.word_id)
        .join(TorahVerse, TorahWord.verse_id == TorahVerse.id)
        .filter(WordRoot.root_id == root_id)
        .limit(limit)
        .all()
    )

    return [
        {
            "word": word.word_original,
            "verse_ref": verse.ref,
            "verse_id": verse.id,
        }
        for word, verse in words
    ]


@router.get("/chapters")
def get_chapters(book: str = "Genesis", db: Session = Depends(get_db)):
    """Get list of chapters for a book."""
    chapters = (
        db.query(TorahChapter)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .filter(TorahBook.name == book)
        .order_by(TorahChapter.number)
        .all()
    )

    return [{"number": c.number, "verses": c.total_verses} for c in chapters]
