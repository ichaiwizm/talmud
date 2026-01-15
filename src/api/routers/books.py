"""Routes for Torah books, chapters, and verses."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from src.api.deps import get_db
from src.api.schemas.books import BookSummary, BookDetail, ChapterResponse, VerseResponse, ChapterSummary
from src.db.models.torah import TorahBook, TorahChapter, TorahVerse

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[BookSummary])
def list_books(db: Session = Depends(get_db)):
    """List all Torah books."""
    books = db.query(TorahBook).order_by(TorahBook.order).all()
    return [BookSummary.model_validate(b) for b in books]


@router.get("/{book_name}", response_model=BookDetail)
def get_book(book_name: str, db: Session = Depends(get_db)):
    """Get book details with chapters."""
    book = db.query(TorahBook).options(
        joinedload(TorahBook.chapters)
    ).filter(TorahBook.name == book_name).first()

    if not book:
        raise HTTPException(404, f"Book '{book_name}' not found")

    chapters = [ChapterSummary(number=c.number, total_verses=c.total_verses)
                for c in sorted(book.chapters, key=lambda c: c.number)]

    return BookDetail(
        id=book.id, name=book.name, hebrew_name=book.hebrew_name,
        order=book.order, total_chapters=book.total_chapters, chapters=chapters
    )


@router.get("/{book_name}/chapters/{chapter}", response_model=ChapterResponse)
def get_chapter(book_name: str, chapter: int, db: Session = Depends(get_db)):
    """Get chapter with all verses."""
    book = db.query(TorahBook).filter(TorahBook.name == book_name).first()
    if not book:
        raise HTTPException(404, f"Book '{book_name}' not found")

    ch = db.query(TorahChapter).filter(
        TorahChapter.book_id == book.id, TorahChapter.number == chapter
    ).first()
    if not ch:
        raise HTTPException(404, f"Chapter {chapter} not found")

    verses = db.query(TorahVerse).filter(
        TorahVerse.chapter_id == ch.id
    ).order_by(TorahVerse.number).all()

    return ChapterResponse(
        book_name=book_name, chapter_number=chapter, total_verses=ch.total_verses,
        verses=[_verse_response(v, chapter) for v in verses]
    )


@router.get("/{book_name}/chapters/{chapter}/verses/{verse}", response_model=VerseResponse)
def get_verse(book_name: str, chapter: int, verse: int, db: Session = Depends(get_db)):
    """Get single verse."""
    ref = f"{book_name} {chapter}:{verse}"
    v = db.query(TorahVerse).filter(TorahVerse.ref == ref).first()
    if not v:
        raise HTTPException(404, f"Verse '{ref}' not found")
    return _verse_response(v, chapter)


@router.get("/verses/{ref:path}", response_model=VerseResponse)
def get_verse_by_ref(ref: str, db: Session = Depends(get_db)):
    """Get verse by reference (e.g., 'Genesis 1:1')."""
    v = db.query(TorahVerse).filter(TorahVerse.ref == ref).first()
    if not v:
        raise HTTPException(404, f"Verse '{ref}' not found")
    parts = ref.split()
    chapter = int(parts[-1].split(":")[0]) if len(parts) > 1 else 1
    return _verse_response(v, chapter)


def _verse_response(v: TorahVerse, chapter: int) -> VerseResponse:
    """Convert verse to response."""
    return VerseResponse(
        id=v.id, ref=v.ref, he_ref=v.he_ref,
        text_hebrew=v.text_hebrew, text_english=v.text_english,
        chapter=chapter, verse=v.number, processed=v.processed,
        word_count=v.word_count, gematria_standard_total=v.gematria_standard_total,
        gematria_katan_total=v.gematria_katan_total
    )
