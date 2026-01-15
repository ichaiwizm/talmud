"""Timeline service for name tracking."""
from collections import defaultdict
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session, joinedload

from src.db.models.torah import TorahVerse, TorahChapter
from src.db.models.names import TorahName, TorahNameOccurrence


class TimelineService:
    """Service for timeline and proximity analysis."""

    def __init__(self, db: Session):
        self.db = db

    def _find_name(self, name_query: str) -> TorahName | None:
        return self.db.query(TorahName).filter(TorahName.name_canonical.ilike(f"%{name_query}%")).first()

    def _name_to_dict(self, name: TorahName) -> dict:
        return {"name": name.name_canonical, "hebrew": name.name_hebrew, "type": name.name_type.value}

    def get_nearby_names(self, name_query: str, radius: int = 3, limit: int = 20) -> dict:
        """Get names that appear within N verses of the given name."""
        target = self._find_name(name_query)
        if not target:
            return {"error": f"Name '{name_query}' not found"}

        target_verse_ids = [
            v[0] for v in self.db.query(TorahNameOccurrence.verse_id)
            .filter(TorahNameOccurrence.name_id == target.id).all()
        ]
        if not target_verse_ids:
            return {"error": f"No occurrences found for '{name_query}'"}

        # Find nearby verses
        nearby_ids = set()
        for vid in target_verse_ids:
            nearby = self.db.query(TorahVerse.id).filter(
                and_(TorahVerse.id >= vid - radius, TorahVerse.id <= vid + radius, TorahVerse.id != vid)
            ).all()
            nearby_ids.update(v[0] for v in nearby)

        results = (
            self.db.query(TorahName, func.count(TorahNameOccurrence.id).label("count"))
            .join(TorahNameOccurrence)
            .filter(TorahNameOccurrence.verse_id.in_(list(nearby_ids)))
            .filter(TorahName.id != target.id)
            .group_by(TorahName.id)
            .order_by(desc("count")).limit(limit).all()
        )

        return {
            "target": self._name_to_dict(target),
            "radius": radius,
            "nearby_names": [{**self._name_to_dict(n), "count": c} for n, c in results],
        }

    def get_timeline(self, name_query: str, limit: int | None = None) -> dict:
        """Get chronological timeline of name occurrences."""
        target = self._find_name(name_query)
        if not target:
            return {"error": f"Name '{name_query}' not found"}

        query = (
            self.db.query(TorahNameOccurrence)
            .options(joinedload(TorahNameOccurrence.verse).joinedload(TorahVerse.chapter).joinedload(TorahChapter.book))
            .filter(TorahNameOccurrence.name_id == target.id)
            .join(TorahVerse).order_by(TorahVerse.id)
        )
        if limit:
            query = query.limit(limit)

        occurrences = query.all()
        by_book: dict[str, int] = defaultdict(int)
        timeline = []

        for occ in occurrences:
            book = occ.verse.chapter.book.name
            by_book[book] += 1
            timeline.append({
                "ref": occ.verse.ref, "book": book,
                "chapter": occ.verse.chapter.number, "verse": occ.verse.number,
                "surface_form": occ.surface_form,
            })

        return {
            "name": {"canonical": target.name_canonical, "hebrew": target.name_hebrew,
                    "type": target.name_type.value, "first_mention": target.first_mention_ref},
            "total_occurrences": len(occurrences),
            "by_book": dict(by_book),
            "timeline": timeline,
        }
