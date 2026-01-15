"""Statistics service for Torah database."""
from typing import Any
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.db.models.torah import TorahBook, TorahChapter, TorahVerse
from src.db.models.names import TorahName, TorahNameOccurrence, NameType


class StatsService:
    """Service for statistics queries."""

    def __init__(self, db: Session):
        self.db = db

    def get_global_stats(self, book_name: str | None = None) -> dict[str, Any]:
        """Get global statistics, optionally filtered by book."""
        if book_name:
            book = self.db.query(TorahBook).filter(TorahBook.name == book_name).first()
            if not book:
                return {"error": f"Book '{book_name}' not found"}
            book_filter = TorahChapter.book_id == book.id
        else:
            book_filter = True

        total_books = self.db.query(TorahBook).count()
        total_chapters = self.db.query(TorahChapter).filter(book_filter).count()

        verse_query = self.db.query(TorahVerse).join(TorahChapter).filter(book_filter)
        total_verses = verse_query.count()
        processed_verses = verse_query.filter(TorahVerse.processed == True).count()

        if book_name:
            name_ids = (
                self.db.query(TorahNameOccurrence.name_id)
                .join(TorahVerse).join(TorahChapter).filter(book_filter).distinct()
            )
            unique_names = name_ids.count()
            total_occurrences = (
                self.db.query(TorahNameOccurrence)
                .join(TorahVerse).join(TorahChapter).filter(book_filter).count()
            )
        else:
            unique_names = self.db.query(TorahName).count()
            total_occurrences = self.db.query(TorahNameOccurrence).count()

        type_dist = self._get_type_distribution(book_name, book_filter)

        return {
            "book": book_name or "All",
            "books": total_books,
            "chapters": total_chapters,
            "verses": total_verses,
            "processed": processed_verses,
            "progress_percent": round(processed_verses / total_verses * 100, 1) if total_verses else 0,
            "unique_names": unique_names,
            "total_occurrences": total_occurrences,
            "type_distribution": type_dist,
        }

    def _get_type_distribution(self, book_name: str | None, book_filter) -> dict:
        """Get name type distribution."""
        type_dist = {}
        for name_type in NameType:
            if book_name:
                count = (
                    self.db.query(TorahName)
                    .join(TorahNameOccurrence).join(TorahVerse).join(TorahChapter)
                    .filter(book_filter).filter(TorahName.name_type == name_type)
                    .distinct().count()
                )
            else:
                count = self.db.query(TorahName).filter(TorahName.name_type == name_type).count()
            if count > 0:
                type_dist[name_type.value] = count
        return type_dist

    def get_top_names(self, limit: int = 20, name_type: str | None = None, book_name: str | None = None) -> list[dict]:
        """Get top names by occurrence count."""
        query = (
            self.db.query(TorahName, func.count(TorahNameOccurrence.id).label("occurrences"))
            .join(TorahNameOccurrence)
        )

        if book_name:
            query = query.join(TorahVerse).join(TorahChapter).join(TorahBook).filter(TorahBook.name == book_name)

        if name_type:
            try:
                query = query.filter(TorahName.name_type == NameType(name_type.lower()))
            except ValueError:
                pass

        results = query.group_by(TorahName.id).order_by(desc("occurrences")).limit(limit).all()
        return [self._name_to_dict(name, count) for name, count in results]

    def list_names(self, name_type: str | None = None, book_name: str | None = None,
                   sort_by: str = "frequency", limit: int = 100) -> list[dict]:
        """List names with filtering and sorting."""
        query = (
            self.db.query(TorahName, func.count(TorahNameOccurrence.id).label("occurrences"))
            .outerjoin(TorahNameOccurrence)
        )

        if book_name:
            query = (
                query.join(TorahVerse, TorahNameOccurrence.verse_id == TorahVerse.id)
                .join(TorahChapter).join(TorahBook).filter(TorahBook.name == book_name)
            )

        if name_type:
            try:
                query = query.filter(TorahName.name_type == NameType(name_type.lower()))
            except ValueError:
                pass

        query = query.group_by(TorahName.id)
        if sort_by == "alpha":
            query = query.order_by(TorahName.name_canonical)
        else:
            query = query.order_by(desc("occurrences"))

        results = query.limit(limit).all()
        return [{"name": n.name_canonical, "hebrew": n.name_hebrew, "type": n.name_type.value, "occurrences": c}
                for n, c in results]

    def _name_to_dict(self, name: TorahName, count: int) -> dict:
        """Convert name to dict with count."""
        return {
            "name": name.name_canonical,
            "hebrew": name.name_hebrew,
            "type": name.name_type.value,
            "occurrences": count,
            "first_mention": name.first_mention_ref,
        }
