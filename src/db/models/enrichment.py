"""Database models for enrichments: sentiment, symbols, cross-references."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Float, Boolean, Integer, ForeignKey, DateTime, Index, JSON
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class EmotionType(str, Enum):
    """Types of emotions in the text."""
    JOY = "joy"
    FEAR = "fear"
    ANGER = "anger"
    SORROW = "sorrow"
    LOVE = "love"
    AWE = "awe"
    GRATITUDE = "gratitude"
    JEALOUSY = "jealousy"
    SHAME = "shame"
    HOPE = "hope"
    DESPAIR = "despair"
    COMPASSION = "compassion"
    NEUTRAL = "neutral"


class DivineSentiment(str, Enum):
    """Divine sentiment expressed."""
    PLEASED = "pleased"
    DISPLEASED = "displeased"
    ANGRY = "angry"
    MERCIFUL = "merciful"
    JEALOUS = "jealous"
    GRIEVED = "grieved"
    NEUTRAL = "neutral"


class SymbolicElementType(str, Enum):
    """Types of symbolic elements."""
    ANIMAL = "animal"
    PLANT = "plant"
    COLOR = "color"
    NUMBER = "number"
    OBJECT = "object"
    NATURAL_ELEMENT = "natural_element"
    BODY_PART = "body_part"
    DIRECTION = "direction"
    TIME = "time"
    MATERIAL = "material"


class CrossReferenceType(str, Enum):
    """Types of cross-references between verses."""
    PARALLEL = "parallel"  # Similar content
    QUOTATION = "quotation"  # Direct quote
    FULFILLMENT = "fulfillment"  # Promise fulfilled
    THEMATIC = "thematic"  # Shared theme
    VERBAL = "verbal"  # Shared vocabulary
    CONTRAST = "contrast"  # Opposite content
    TYPOLOGY = "typology"  # Foreshadowing
    ALLUSION = "allusion"  # Indirect reference


class VerseSentiment(Base):
    """Sentiment analysis for verses."""
    __tablename__ = "verse_sentiment"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), unique=True, nullable=False)

    primary_emotion: Mapped[Optional[EmotionType]] = mapped_column(SQLEnum(EmotionType), nullable=True)
    secondary_emotion: Mapped[Optional[EmotionType]] = mapped_column(SQLEnum(EmotionType), nullable=True)

    sentiment_polarity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # -1 to +1
    emotional_intensity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0 to 1
    tension_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0 to 1

    divine_sentiment: Mapped[Optional[DivineSentiment]] = mapped_column(
        SQLEnum(DivineSentiment), nullable=True
    )

    emotional_keywords: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of words
    context_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_verse_sentiment_emotion", "primary_emotion"),
        Index("ix_verse_sentiment_divine", "divine_sentiment"),
        Index("ix_verse_sentiment_polarity", "sentiment_polarity"),
    )

    def __repr__(self) -> str:
        return f"<VerseSentiment verse={self.verse_id} emotion={self.primary_emotion}>"


class CharacterEmotion(Base):
    """Emotions expressed by specific characters."""
    __tablename__ = "character_emotions"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    character_id: Mapped[int] = mapped_column(ForeignKey("torah_names.id"), nullable=False)

    character_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    emotion: Mapped[EmotionType] = mapped_column(SQLEnum(EmotionType), nullable=False)

    trigger: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # What caused the emotion
    resulting_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # What action resulted
    expressed_how: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # How was it shown

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_character_emotions_verse", "verse_id"),
        Index("ix_character_emotions_character", "character_id"),
        Index("ix_character_emotions_emotion", "emotion"),
    )

    def __repr__(self) -> str:
        return f"<CharacterEmotion {self.character_name}: {self.emotion.value}>"


class SymbolicNumber(Base):
    """Symbolic numbers in the Torah."""
    __tablename__ = "symbolic_numbers"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    number_value: Mapped[int] = mapped_column(Integer, nullable=False)
    number_hebrew: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    context: Mapped[str] = mapped_column(Text, nullable=False)  # What is being counted/measured

    symbolic_meaning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_literal: Mapped[bool] = mapped_column(Boolean, default=True)
    is_symbolic: Mapped[bool] = mapped_column(Boolean, default=False)

    pattern_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Pattern with other occurrences
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_symbolic_numbers_verse", "verse_id"),
        Index("ix_symbolic_numbers_value", "number_value"),
    )

    def __repr__(self) -> str:
        return f"<SymbolicNumber {self.number_value} in verse {self.verse_id}>"


class SymbolicElement(Base):
    """Symbolic elements (animals, plants, objects, etc.)."""
    __tablename__ = "symbolic_elements"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    element_name: Mapped[str] = mapped_column(String(100), nullable=False)
    element_name_hebrew: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    element_type: Mapped[SymbolicElementType] = mapped_column(
        SQLEnum(SymbolicElementType), nullable=False
    )

    symbolic_meaning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_positive: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_negative: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    related_themes: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_symbolic_elements_verse", "verse_id"),
        Index("ix_symbolic_elements_type", "element_type"),
        Index("ix_symbolic_elements_name", "element_name"),
    )

    def __repr__(self) -> str:
        return f"<SymbolicElement {self.element_name} ({self.element_type.value})>"


class RecurringMotif(Base):
    """Recurring motifs across the Torah."""
    __tablename__ = "recurring_motifs"

    id: Mapped[int] = mapped_column(primary_key=True)

    motif_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    motif_name_hebrew: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    thematic_significance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    first_occurrence_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    related_motifs: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of related motif IDs
    examples: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # Sample verse refs

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_recurring_motifs_name", "motif_name"),
    )

    def __repr__(self) -> str:
        return f"<RecurringMotif {self.motif_name}>"


class MotifOccurrence(Base):
    """Occurrences of motifs in verses."""
    __tablename__ = "motif_occurrences"

    id: Mapped[int] = mapped_column(primary_key=True)
    motif_id: Mapped[int] = mapped_column(ForeignKey("recurring_motifs.id"), nullable=False)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    significance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    variation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_motif_occurrences_motif", "motif_id"),
        Index("ix_motif_occurrences_verse", "verse_id"),
    )

    def __repr__(self) -> str:
        return f"<MotifOccurrence motif={self.motif_id} verse={self.verse_id}>"


class CrossReference(Base):
    """Cross-references between Torah verses."""
    __tablename__ = "cross_references"

    id: Mapped[int] = mapped_column(primary_key=True)

    source_verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    target_verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    source_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_ref: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    reference_type: Mapped[CrossReferenceType] = mapped_column(
        SQLEnum(CrossReferenceType), nullable=False
    )

    shared_vocabulary: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of shared words
    shared_themes: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of shared themes

    similarity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_bidirectional: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_cross_references_source", "source_verse_id"),
        Index("ix_cross_references_target", "target_verse_id"),
        Index("ix_cross_references_type", "reference_type"),
    )

    def __repr__(self) -> str:
        return f"<CrossReference {self.source_ref} -> {self.target_ref} ({self.reference_type.value})>"
