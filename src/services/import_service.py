import logging
from typing import Optional

from sqlalchemy.orm import Session

from src.db.models.torah import TorahBook, TorahChapter, TorahVerse
from src.providers.sefaria.client import SefariaClient, TORAH_BOOKS

logger = logging.getLogger(__name__)


class TorahImportService:
    """Service for importing Torah text from Sefaria."""

    def __init__(self, db: Session, max_workers: int = 10):
        self.db = db
        self.sefaria = SefariaClient(max_workers=max_workers)

    def import_all_books(self) -> dict:
        """Import all Torah books."""
        stats = {"books": 0, "chapters": 0, "verses": 0, "errors": []}

        for order, book_name in enumerate(TORAH_BOOKS, start=1):
            try:
                result = self.import_book(book_name, order)
                stats["books"] += 1
                stats["chapters"] += result["chapters"]
                stats["verses"] += result["verses"]
                logger.info(
                    f"Imported {book_name}: {result['chapters']} chapters, "
                    f"{result['verses']} verses"
                )
            except Exception as e:
                error_msg = f"Failed to import {book_name}: {e}"
                stats["errors"].append(error_msg)
                logger.error(error_msg)

        return stats

    def import_book(self, book_name: str, order: int) -> dict:
        """Import a complete book using parallel fetching."""
        # Get book structure
        shape = self.sefaria.get_book_shape(book_name)

        # Create or get book
        book = self.db.query(TorahBook).filter_by(name=book_name).first()
        if not book:
            book = TorahBook(
                name=shape.name,
                hebrew_name=shape.hebrew_name,
                order=order,
                total_chapters=shape.total_chapters,
            )
            self.db.add(book)
            self.db.flush()
            logger.info(f"Created book: {book_name}")

        # Fetch all chapters in parallel
        logger.info(f"Fetching {shape.total_chapters} chapters in parallel...")
        all_chapters = self.sefaria.get_all_chapters_parallel(
            book_name, shape.total_chapters
        )

        stats = {"chapters": 0, "verses": 0}

        # Insert chapters and verses in order
        for chapter_num in range(1, shape.total_chapters + 1):
            verses_data = all_chapters.get(chapter_num, [])
            expected_verses = shape.verses_per_chapter[chapter_num - 1]

            # Check if chapter exists
            chapter = (
                self.db.query(TorahChapter)
                .filter_by(book_id=book.id, number=chapter_num)
                .first()
            )

            if chapter and len(chapter.verses) == expected_verses:
                logger.debug(f"Chapter {book_name} {chapter_num} already imported")
                continue

            if not chapter:
                chapter = TorahChapter(
                    book_id=book.id,
                    number=chapter_num,
                    total_verses=expected_verses,
                )
                self.db.add(chapter)
                self.db.flush()

            # Add verses
            verses_added = 0
            for verse_data in verses_data:
                existing = (
                    self.db.query(TorahVerse).filter_by(ref=verse_data.ref).first()
                )
                if existing:
                    continue

                verse = TorahVerse(
                    chapter_id=chapter.id,
                    number=verse_data.verse,
                    ref=verse_data.ref,
                    he_ref=verse_data.he_ref,
                    text_hebrew=verse_data.text_hebrew,
                    text_english=verse_data.text_english,
                    processed=False,
                )
                self.db.add(verse)
                verses_added += 1

            stats["chapters"] += 1
            stats["verses"] += verses_added

        # Commit all at once
        self.db.commit()
        logger.info(f"Committed {book_name}: {stats['chapters']} chapters, {stats['verses']} verses")

        return stats

    def get_import_status(self) -> dict:
        """Return import status."""
        books = self.db.query(TorahBook).count()
        chapters = self.db.query(TorahChapter).count()
        verses = self.db.query(TorahVerse).count()

        return {
            "books": books,
            "chapters": chapters,
            "verses": verses,
            "expected_books": len(TORAH_BOOKS),
        }

    def close(self):
        """Close resources."""
        self.sefaria.close()
