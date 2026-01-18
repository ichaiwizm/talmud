"""Divine names routes."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter
from src.db.models.theological import DivineNameOccurrence, DivineNameType, ContextType

router = APIRouter()


@router.get("")
def get_divine_names(
    name: str | None = None,
    context: str | None = None,
    book: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = (
        db.query(DivineNameOccurrence, TorahVerse)
        .join(TorahVerse, DivineNameOccurrence.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
    )

    if name:
        query = query.filter(DivineNameOccurrence.divine_name == name)
    if context:
        query = query.filter(DivineNameOccurrence.context_type == context)
    if book:
        query = query.filter(TorahBook.name == book)

    total = query.count()
    results = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "occurrences": [
            {
                "id": occ.id,
                "divine_name": occ.divine_name.value if occ.divine_name else None,
                "divine_name_hebrew": occ.divine_name_hebrew,
                "context_type": occ.context_type.value if occ.context_type else None,
                "speaker_type": occ.speaker_type,
                "theological_note": occ.theological_note,
                "verse": {
                    "id": verse.id,
                    "ref": verse.ref,
                    "text_hebrew": verse.text_hebrew,
                    "text_english": verse.text_english,
                },
            }
            for occ, verse in results
        ],
    }


@router.get("/distribution")
def get_distribution(db: Session = Depends(get_db)):
    """Get distribution of divine names by book and type."""
    results = (
        db.query(
            TorahBook.name,
            DivineNameOccurrence.divine_name,
            func.count(DivineNameOccurrence.id).label("count"),
        )
        .join(TorahVerse, DivineNameOccurrence.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .group_by(TorahBook.name, DivineNameOccurrence.divine_name)
        .all()
    )

    distribution = {}
    for book_name, divine_name, count in results:
        if book_name not in distribution:
            distribution[book_name] = {}
        distribution[book_name][divine_name.value if divine_name else "unknown"] = count

    return distribution


@router.get("/by-context")
def get_by_context(db: Session = Depends(get_db)):
    """Get divine names grouped by context type."""
    results = (
        db.query(
            DivineNameOccurrence.context_type,
            DivineNameOccurrence.divine_name,
            func.count(DivineNameOccurrence.id).label("count"),
        )
        .group_by(DivineNameOccurrence.context_type, DivineNameOccurrence.divine_name)
        .all()
    )

    by_context = {}
    for context, name, count in results:
        ctx_key = context.value if context else "unknown"
        if ctx_key not in by_context:
            by_context[ctx_key] = {}
        by_context[ctx_key][name.value if name else "unknown"] = count

    return by_context


@router.get("/types")
def get_types():
    """Get available divine name types and contexts."""
    return {
        "divine_names": [e.value for e in DivineNameType],
        "contexts": [e.value for e in ContextType],
    }
