"""Database models for linguistic analysis: roots, formulas, literary structures."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Float, Integer, ForeignKey, DateTime, Index, JSON
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class VerbForm(str, Enum):
    """Hebrew verb forms (binyanim)."""
    QAL = "qal"
    NIPHAL = "niphal"
    PIEL = "piel"
    PUAL = "pual"
    HIPHIL = "hiphil"
    HOPHAL = "hophal"
    HITPAEL = "hitpael"
    OTHER = "other"


class FormulaType(str, Enum):
    """Types of formulaic expressions."""
    TOLEDOT = "toledot"  # "These are the generations of..."
    WAYYOMER = "wayyomer"  # "And he said..."
    BLESSING = "blessing"
    COVENANT = "covenant"
    CREATION = "creation"  # "And it was evening and it was morning..."
    GENEALOGY = "genealogy"
    NARRATIVE_TRANSITION = "narrative_transition"
    LEGAL = "legal"
    SUMMARY = "summary"
    OTHER = "other"


class LiteraryStructureType(str, Enum):
    """Types of literary structures."""
    CHIASMUS = "chiasmus"  # ABBA pattern
    PARALLELISM = "parallelism"  # AB / A'B' pattern
    INCLUSIO = "inclusio"  # Bookended structure
    ACROSTIC = "acrostic"
    REPETITION = "repetition"
    SANDWICH = "sandwich"  # ABA pattern
    STAIRCASE = "staircase"  # ABC / A'B'C' / A''B''C''
    ENVELOPE = "envelope"
    CONCATENATION = "concatenation"  # Linked sections
    OTHER = "other"


class HebrewRoot(Base):
    """Hebrew root letters (shoreshim)."""
    __tablename__ = "hebrew_roots"

    id: Mapped[int] = mapped_column(primary_key=True)

    root_letters: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # e.g., "ברא"
    root_transliteration: Mapped[str] = mapped_column(String(20), nullable=False)
    basic_meaning: Mapped[str] = mapped_column(Text, nullable=False)
    basic_meaning_hebrew: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    semantic_field: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    related_roots: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of related root IDs
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    word_roots: Mapped[List["WordRoot"]] = relationship(
        back_populates="root", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_hebrew_roots_letters", "root_letters"),
        Index("ix_hebrew_roots_transliteration", "root_transliteration"),
    )

    def __repr__(self) -> str:
        return f"<HebrewRoot {self.root_letters} ({self.root_transliteration})>"


class WordRoot(Base):
    """Mapping of Torah words to their Hebrew roots."""
    __tablename__ = "word_roots"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("torah_words.id"), nullable=False)
    root_id: Mapped[int] = mapped_column(ForeignKey("hebrew_roots.id"), nullable=False)

    verb_form: Mapped[Optional[VerbForm]] = mapped_column(SQLEnum(VerbForm), nullable=True)
    grammatical_features: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    # Features like: {"tense": "perfect", "person": "3", "number": "singular", "gender": "masculine"}

    word_meaning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    root: Mapped["HebrewRoot"] = relationship(back_populates="word_roots")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_word_roots_word", "word_id"),
        Index("ix_word_roots_root", "root_id"),
        Index("ix_word_roots_verb_form", "verb_form"),
    )

    def __repr__(self) -> str:
        return f"<WordRoot word={self.word_id} root={self.root_id}>"


class FormulaicExpression(Base):
    """Repeated formulaic expressions in the Torah."""
    __tablename__ = "formulaic_expressions"

    id: Mapped[int] = mapped_column(primary_key=True)

    formula_hebrew: Mapped[str] = mapped_column(Text, nullable=False)
    formula_english: Mapped[str] = mapped_column(Text, nullable=False)
    formula_transliteration: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    formula_type: Mapped[FormulaType] = mapped_column(SQLEnum(FormulaType), nullable=False)
    function: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # What role does it play?

    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    pattern_regex: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # For matching variations

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    occurrences: Mapped[List["FormulaOccurrence"]] = relationship(
        back_populates="formula", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_formulaic_expressions_type", "formula_type"),
    )

    def __repr__(self) -> str:
        return f"<FormulaicExpression {self.formula_type.value}: {self.formula_english[:50]}>"


class FormulaOccurrence(Base):
    """Occurrences of formulaic expressions in verses."""
    __tablename__ = "formula_occurrences"

    id: Mapped[int] = mapped_column(primary_key=True)
    formula_id: Mapped[int] = mapped_column(ForeignKey("formulaic_expressions.id"), nullable=False)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    surface_form: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Actual text in verse
    position_in_verse: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # start, middle, end
    variation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    formula: Mapped["FormulaicExpression"] = relationship(back_populates="occurrences")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_formula_occurrences_formula", "formula_id"),
        Index("ix_formula_occurrences_verse", "verse_id"),
    )

    def __repr__(self) -> str:
        return f"<FormulaOccurrence formula={self.formula_id} verse={self.verse_id}>"


class LiteraryStructure(Base):
    """Literary structures spanning multiple verses."""
    __tablename__ = "literary_structures"

    id: Mapped[int] = mapped_column(primary_key=True)

    verse_start_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    verse_end_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    verse_start_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    verse_end_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    structure_type: Mapped[LiteraryStructureType] = mapped_column(
        SQLEnum(LiteraryStructureType), nullable=False
    )
    pattern_notation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "ABCB'A'"

    focal_point_verse_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_verses.id"), nullable=True)
    focal_point_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    structural_elements: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    # Elements like: [{"label": "A", "verse_refs": ["Gen 1:1-2"], "content": "Creation begins"}]

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    scholarly_reference: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_literary_structures_type", "structure_type"),
        Index("ix_literary_structures_verse_start", "verse_start_id"),
    )

    def __repr__(self) -> str:
        return f"<LiteraryStructure {self.structure_type.value} {self.verse_start_ref}-{self.verse_end_ref}>"
