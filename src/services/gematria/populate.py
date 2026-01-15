"""Gematria word population service."""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from src.db.models.torah import TorahVerse, TorahChapter, TorahBook
from src.db.models.gematria import TorahWord
from src.utils.hebrew import (
    extract_words,
    calculate_standard,
    calculate_katan,
    calculate_ordinal,
    calculate_atbash,
)

logger = logging.getLogger(__name__)


def populate_words_for_verse(db: Session, verse: TorahVerse) -> int:
    """Extract words from a verse and save to database.

    Args:
        db: Database session
        verse: TorahVerse to process

    Returns:
        Number of words added
    """
    word_pairs = extract_words(verse.text_hebrew)

    words_added = 0
    total_standard = 0
    total_katan = 0

    for position, (original, normalized) in enumerate(word_pairs, start=1):
        # Check if word already exists at this position
        existing = (
            db.query(TorahWord)
            .filter_by(verse_id=verse.id, position=position)
            .first()
        )
        if existing:
            continue

        g_standard = calculate_standard(normalized)
        g_katan = calculate_katan(normalized)

        word = TorahWord(
            verse_id=verse.id,
            position=position,
            word_original=original,
            word_normalized=normalized,
            gematria_standard=g_standard,
            gematria_katan=g_katan,
            gematria_ordinal=calculate_ordinal(normalized),
            gematria_atbash=calculate_atbash(normalized),
        )
        db.add(word)
        words_added += 1

        total_standard += g_standard
        total_katan += g_katan

    # Update verse totals
    verse.word_count = len(word_pairs)
    verse.gematria_standard_total = total_standard
    verse.gematria_katan_total = total_katan

    return words_added


def populate_all_words(
    db: Session,
    limit: Optional[int] = None,
    book_name: Optional[str] = None,
) -> dict:
    """Populate words table for all verses.

    Args:
        db: Database session
        limit: Maximum verses to process
        book_name: Process only this book

    Returns:
        Statistics dictionary
    """
    query = db.query(TorahVerse)

    if book_name:
        query = (
            query.join(TorahChapter)
            .join(TorahBook)
            .filter(TorahBook.name == book_name)
        )

    # Filter verses without words populated
    query = query.filter(TorahVerse.word_count.is_(None))

    if limit:
        query = query.limit(limit)

    verses = query.all()
    stats = {"verses_processed": 0, "words_added": 0}

    for verse in verses:
        words_count = populate_words_for_verse(db, verse)
        stats["verses_processed"] += 1
        stats["words_added"] += words_count

        # Commit every 100 verses
        if stats["verses_processed"] % 100 == 0:
            db.commit()
            logger.info(
                f"Processed {stats['verses_processed']} verses, "
                f"{stats['words_added']} words"
            )

    db.commit()
    return stats


def get_population_status(db: Session) -> dict:
    """Get word population status.

    Returns:
        Status dictionary with progress info
    """
    total_verses = db.query(TorahVerse).count()
    populated = (
        db.query(TorahVerse)
        .filter(TorahVerse.word_count.isnot(None))
        .count()
    )
    total_words = db.query(TorahWord).count()

    return {
        "total_verses": total_verses,
        "verses_populated": populated,
        "pending": total_verses - populated,
        "total_words": total_words,
        "progress_percent": round(populated / total_verses * 100, 2)
        if total_verses
        else 0,
    }
