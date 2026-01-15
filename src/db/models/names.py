from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Float, ForeignKey, DateTime, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class NameType(str, Enum):
    PERSON = "person"
    DEITY = "deity"
    PLACE = "place"
    PEOPLE_GROUP = "people_group"
    ANGEL = "angel"
    UNKNOWN = "unknown"


class TorahName(Base):
    __tablename__ = "torah_names"

    id: Mapped[int] = mapped_column(primary_key=True)

    name_canonical: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_hebrew: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    name_type: Mapped[NameType] = mapped_column(
        SQLEnum(NameType), default=NameType.UNKNOWN, nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_mention_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    occurrences: Mapped[List["TorahNameOccurrence"]] = relationship(
        back_populates="name", cascade="all, delete-orphan"
    )
    aliases: Mapped[List["TorahNameAlias"]] = relationship(
        back_populates="canonical_name", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<TorahName {self.name_canonical}>"


class TorahNameAlias(Base):
    __tablename__ = "torah_name_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_id: Mapped[int] = mapped_column(ForeignKey("torah_names.id"), nullable=False)
    alias: Mapped[str] = mapped_column(String(100), nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en")

    canonical_name: Mapped["TorahName"] = relationship(back_populates="aliases")

    __table_args__ = (Index("ix_torah_name_aliases_alias", "alias"),)

    def __repr__(self) -> str:
        return f"<TorahNameAlias {self.alias}>"


class TorahNameOccurrence(Base):
    __tablename__ = "torah_name_occurrences"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    name_id: Mapped[int] = mapped_column(ForeignKey("torah_names.id"), nullable=False)

    surface_form: Mapped[str] = mapped_column(String(100), nullable=False)
    surface_form_hebrew: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    context_before: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context_after: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extraction_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    verse: Mapped["TorahVerse"] = relationship(
        "TorahVerse", back_populates="name_occurrences"
    )
    name: Mapped["TorahName"] = relationship(back_populates="occurrences")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_torah_name_occurrences_verse", "verse_id"),
        Index("ix_torah_name_occurrences_name", "name_id"),
    )

    def __repr__(self) -> str:
        return f"<TorahNameOccurrence {self.surface_form} in {self.verse_id}>"


