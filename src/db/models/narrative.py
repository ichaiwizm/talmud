"""Database models for narrative structure: units, parshaot, genealogy."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Float, Boolean, Integer, ForeignKey, DateTime, Index, JSON
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class NarrativeUnitType(str, Enum):
    """Types of narrative units."""
    STORY = "story"
    LAW_COLLECTION = "law_collection"
    GENEALOGY = "genealogy"
    POEM = "poem"
    SPEECH = "speech"
    DIALOGUE = "dialogue"
    BLESSING = "blessing"
    PROPHECY = "prophecy"
    ITINERARY = "itinerary"
    CENSUS = "census"
    INSTRUCTION = "instruction"


class NarrativeUnit(Base):
    """Narrative units (pericopes) in the Torah."""
    __tablename__ = "narrative_units"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    title_hebrew: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    traditional_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "Akeidah", "Lech Lecha"
    traditional_name_hebrew: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    unit_type: Mapped[NarrativeUnitType] = mapped_column(SQLEnum(NarrativeUnitType), nullable=False)

    verse_start_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    verse_end_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    verse_start_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    verse_end_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_hebrew: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    main_themes: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of theme strings
    main_characters: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of character IDs/names

    parent_unit_id: Mapped[Optional[int]] = mapped_column(ForeignKey("narrative_units.id"), nullable=True)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extraction_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_narrative_units_type", "unit_type"),
        Index("ix_narrative_units_verse_start", "verse_start_id"),
        Index("ix_narrative_units_parent", "parent_unit_id"),
    )

    def __repr__(self) -> str:
        return f"<NarrativeUnit {self.title}>"


class Parsha(Base):
    """Weekly Torah portions (Parshaot)."""
    __tablename__ = "parshaot"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_hebrew: Mapped[str] = mapped_column(String(100), nullable=False)
    name_transliterated: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    book_id: Mapped[int] = mapped_column(ForeignKey("torah_books.id"), nullable=False)
    parsha_order: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-54

    verse_start_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    verse_end_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    verse_start_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    verse_end_ref: Mapped[str] = mapped_column(String(50), nullable=False)

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verse_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_parshaot_order", "parsha_order"),
        Index("ix_parshaot_book", "book_id"),
    )

    def __repr__(self) -> str:
        return f"<Parsha {self.name}>"


class Genealogy(Base):
    """Structured genealogical data for Torah individuals."""
    __tablename__ = "genealogy"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("torah_names.id"), unique=True, nullable=False)

    father_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_names.id"), nullable=True)
    mother_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_names.id"), nullable=True)

    father_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mother_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    birth_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_firstborn: Mapped[bool] = mapped_column(Boolean, default=False)

    lifespan_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    age_at_first_child: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    age_at_death: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    generation_from_adam: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    generation_from_noah: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    generation_from_abraham: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    birth_verse_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_verses.id"), nullable=True)
    death_verse_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_verses.id"), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_genealogy_father", "father_id"),
        Index("ix_genealogy_mother", "mother_id"),
        Index("ix_genealogy_gen_adam", "generation_from_adam"),
        Index("ix_genealogy_gen_abraham", "generation_from_abraham"),
    )

    def __repr__(self) -> str:
        return f"<Genealogy person_id={self.person_id}>"


class Marriage(Base):
    """Marriage relationships in the Torah."""
    __tablename__ = "marriages"

    id: Mapped[int] = mapped_column(primary_key=True)

    husband_id: Mapped[int] = mapped_column(ForeignKey("torah_names.id"), nullable=False)
    wife_id: Mapped[int] = mapped_column(ForeignKey("torah_names.id"), nullable=False)

    husband_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    wife_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    marriage_order: Mapped[int] = mapped_column(Integer, default=1)  # For polygamous marriages

    verse_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_verses.id"), nullable=True)
    verse_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
    is_concubine: Mapped[bool] = mapped_column(Boolean, default=False)

    children_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_marriages_husband", "husband_id"),
        Index("ix_marriages_wife", "wife_id"),
        Index("ix_marriages_verse", "verse_id"),
    )

    def __repr__(self) -> str:
        return f"<Marriage {self.husband_name} + {self.wife_name}>"


class VerseTopic(Base):
    """Topics associated with verses."""
    __tablename__ = "verse_topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    topic_hebrew: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_verse_topics_verse", "verse_id"),
        Index("ix_verse_topics_topic", "topic"),
        Index("ix_verse_topics_unique", "verse_id", "topic", unique=True),
    )

    def __repr__(self) -> str:
        return f"<VerseTopic {self.topic} in verse {self.verse_id}>"


class VerseTheme(Base):
    """Themes associated with verses."""
    __tablename__ = "verse_themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    theme: Mapped[str] = mapped_column(String(100), nullable=False)
    theme_hebrew: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_verse_themes_verse", "verse_id"),
        Index("ix_verse_themes_theme", "theme"),
        Index("ix_verse_themes_unique", "verse_id", "theme", unique=True),
    )

    def __repr__(self) -> str:
        return f"<VerseTheme {self.theme} in verse {self.verse_id}>"
