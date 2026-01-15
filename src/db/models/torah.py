from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.gematria import TorahWord


class TorahBook(Base):
    __tablename__ = "torah_books"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hebrew_name: Mapped[str] = mapped_column(String(50), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    total_chapters: Mapped[int] = mapped_column(Integer, nullable=False)

    chapters: Mapped[List["TorahChapter"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<TorahBook {self.name}>"


class TorahChapter(Base):
    __tablename__ = "torah_chapters"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("torah_books.id"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    total_verses: Mapped[int] = mapped_column(Integer, nullable=False)

    book: Mapped["TorahBook"] = relationship(back_populates="chapters")
    verses: Mapped[List["TorahVerse"]] = relationship(
        back_populates="chapter", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_torah_chapters_book_number", "book_id", "number", unique=True),
    )

    def __repr__(self) -> str:
        return f"<TorahChapter {self.book.name if self.book else '?'} {self.number}>"


class TorahVerse(Base):
    __tablename__ = "torah_verses"

    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("torah_chapters.id"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)

    ref: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    he_ref: Mapped[str] = mapped_column(String(100), nullable=False)

    text_hebrew: Mapped[str] = mapped_column(Text, nullable=False)
    text_english: Mapped[str] = mapped_column(Text, nullable=False)

    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    extraction_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Gematria totals for the verse
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gematria_standard_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gematria_katan_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    chapter: Mapped["TorahChapter"] = relationship(back_populates="verses")
    name_occurrences: Mapped[List["TorahNameOccurrence"]] = relationship(
        "TorahNameOccurrence", back_populates="verse", cascade="all, delete-orphan"
    )
    words: Mapped[List["TorahWord"]] = relationship(
        "TorahWord", back_populates="verse", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_torah_verses_chapter_number", "chapter_id", "number", unique=True),
    )

    def __repr__(self) -> str:
        return f"<TorahVerse {self.ref}>"


