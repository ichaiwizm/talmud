"""Gematria-related database models."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.torah import TorahVerse


class TorahWord(Base):
    """Individual word from Torah with gematria values."""

    __tablename__ = "torah_words"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(
        ForeignKey("torah_verses.id"), nullable=False
    )

    # Position within verse (1-indexed)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    # Word as it appears (with nikud)
    word_original: Mapped[str] = mapped_column(String(100), nullable=False)

    # Normalized word (letters only, no nikud)
    word_normalized: Mapped[str] = mapped_column(String(100), nullable=False)

    # Gematria values for each method
    gematria_standard: Mapped[int] = mapped_column(Integer, nullable=False)
    gematria_katan: Mapped[int] = mapped_column(Integer, nullable=False)
    gematria_ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    gematria_atbash: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationship
    verse: Mapped["TorahVerse"] = relationship(
        "TorahVerse", back_populates="words"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_torah_words_verse_pos", "verse_id", "position", unique=True),
        Index("ix_torah_words_gematria_std", "gematria_standard"),
        Index("ix_torah_words_gematria_katan", "gematria_katan"),
        Index("ix_torah_words_normalized", "word_normalized"),
    )

    def __repr__(self) -> str:
        return f"<TorahWord {self.word_normalized}={self.gematria_standard}>"
