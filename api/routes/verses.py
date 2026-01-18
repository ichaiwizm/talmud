"""Verse routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter

router = APIRouter()


@router.get("")
def get_verses(
    book: str | None = None,
    chapter: int | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(TorahVerse).join(TorahChapter).join(TorahBook)

    if book:
        query = query.filter(TorahBook.name == book)
    if chapter:
        query = query.filter(TorahChapter.number == chapter)

    total = query.count()
    verses = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "verses": [
            {
                "id": v.id,
                "ref": v.ref,
                "he_ref": v.he_ref,
                "text_hebrew": v.text_hebrew,
                "text_english": v.text_english,
                "gematria_total": v.gematria_standard_total,
            }
            for v in verses
        ],
    }


@router.get("/books")
def get_books(db: Session = Depends(get_db)):
    books = db.query(TorahBook).order_by(TorahBook.order).all()
    return [
        {"id": b.id, "name": b.name, "hebrew_name": b.hebrew_name, "chapters": b.total_chapters}
        for b in books
    ]
