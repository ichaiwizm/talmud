"""Search service for Torah database."""
from sqlalchemy import func, desc, or_
from sqlalchemy.orm import Session, joinedload

from src.db.models.torah import TorahBook, TorahChapter, TorahVerse
from src.db.models.names import TorahName, TorahNameOccurrence


class SearchService:
    """Service for search queries."""

    def __init__(self, db: Session):
        self.db = db

    def search_name(self, query: str, exact: bool = False, include_hebrew: bool = False) -> list[dict]:
        """Search for names matching a query."""
        if exact:
            filters = [TorahName.name_canonical == query]
            if include_hebrew:
                filters.append(TorahName.name_hebrew == query)
        else:
            pattern = f"%{query}%"
            filters = [TorahName.name_canonical.ilike(pattern)]
            if include_hebrew:
                filters.append(TorahName.name_hebrew.ilike(pattern))

        results = (
            self.db.query(TorahName, func.count(TorahNameOccurrence.id).label("occurrences"))
            .outerjoin(TorahNameOccurrence)
            .filter(or_(*filters))
            .group_by(TorahName.id)
            .order_by(desc("occurrences"))
            .all()
        )

        return [{
            "id": name.id,
            "name": name.name_canonical,
            "hebrew": name.name_hebrew,
            "type": name.name_type.value,
            "occurrences": count,
            "first_mention": name.first_mention_ref,
        } for name, count in results]

    def get_name_detail(self, name_query: str) -> dict | None:
        """Get detailed information about a name."""
        name = (
            self.db.query(TorahName)
            .filter(TorahName.name_canonical.ilike(f"%{name_query}%"))
            .first()
        )
        if not name:
            return None

        occurrences = (
            self.db.query(TorahNameOccurrence)
            .options(joinedload(TorahNameOccurrence.verse))
            .filter(TorahNameOccurrence.name_id == name.id)
            .all()
        )

        return {
            "id": name.id,
            "name": name.name_canonical,
            "hebrew": name.name_hebrew,
            "type": name.name_type.value,
            "first_mention": name.first_mention_ref,
            "description": name.description,
            "occurrences": len(occurrences),
            "verses": [{"ref": o.verse.ref, "text": o.verse.text_english,
                       "hebrew": o.verse.text_hebrew, "surface_form": o.surface_form} for o in occurrences],
        }

    def find_verses_by_name(self, name_query: str, book_name: str | None = None, limit: int = 50) -> list[dict]:
        """Find all verses containing a name."""
        query = (
            self.db.query(TorahVerse, TorahNameOccurrence.surface_form)
            .join(TorahNameOccurrence).join(TorahName)
            .filter(TorahName.name_canonical.ilike(f"%{name_query}%"))
        )

        if book_name:
            query = query.join(TorahChapter).join(TorahBook).filter(TorahBook.name == book_name)

        results = query.order_by(TorahVerse.id).limit(limit).all()
        return [{"ref": v.ref, "text_english": v.text_english, "text_hebrew": v.text_hebrew,
                 "surface_form": sf} for v, sf in results]

    def search_verses(self, text_query: str, book_name: str | None = None,
                      search_hebrew: bool = False, limit: int = 50) -> list[dict]:
        """Search for verses containing text."""
        pattern = f"%{text_query}%"
        text_filter = TorahVerse.text_hebrew.ilike(pattern) if search_hebrew else TorahVerse.text_english.ilike(pattern)

        query = self.db.query(TorahVerse).filter(text_filter)
        if book_name:
            query = query.join(TorahChapter).join(TorahBook).filter(TorahBook.name == book_name)

        results = query.order_by(TorahVerse.id).limit(limit).all()
        return [{"ref": v.ref, "text_english": v.text_english, "text_hebrew": v.text_hebrew} for v in results]
