"""Database models for entity relationships, events, and direct speech."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Float, Boolean, Integer, ForeignKey, DateTime, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class RelationshipCategory(str, Enum):
    """Categories of relationships between entities."""
    FAMILY = "family"
    POLITICAL = "political"
    SPIRITUAL = "spiritual"
    SPATIAL = "spatial"


class RelationshipType(str, Enum):
    """Specific types of relationships."""
    # Family
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    SPOUSE_OF = "spouse_of"
    SIBLING_OF = "sibling_of"
    ANCESTOR_OF = "ancestor_of"
    DESCENDANT_OF = "descendant_of"

    # Political
    RULES_OVER = "rules_over"
    SERVES = "serves"
    ALLY_OF = "ally_of"
    ENEMY_OF = "enemy_of"
    SUCCESSOR_OF = "successor_of"

    # Spiritual
    BLESSES = "blesses"
    CURSES = "curses"
    SPEAKS_TO = "speaks_to"
    APPEARS_TO = "appears_to"
    WORSHIPS = "worships"
    COVENANTS_WITH = "covenants_with"

    # Spatial
    LIVES_IN = "lives_in"
    TRAVELS_TO = "travels_to"
    BORN_IN = "born_in"
    DIES_IN = "dies_in"
    BURIED_IN = "buried_in"
    FLEES_TO = "flees_to"


class EventType(str, Enum):
    """Types of events in the Torah narrative."""
    BIRTH = "birth"
    DEATH = "death"
    MARRIAGE = "marriage"
    COVENANT = "covenant"
    BATTLE = "battle"
    MIRACLE = "miracle"
    THEOPHANY = "theophany"
    JOURNEY = "journey"
    CONSTRUCTION = "construction"
    SACRIFICE = "sacrifice"
    BLESSING = "blessing"
    CURSE = "curse"
    PROPHECY = "prophecy"
    LAW_GIVING = "law_giving"
    CREATION = "creation"
    DESTRUCTION = "destruction"
    NAMING = "naming"
    CIRCUMCISION = "circumcision"


class ParticipantRole(str, Enum):
    """Roles of participants in events."""
    AGENT = "agent"
    PATIENT = "patient"
    BENEFICIARY = "beneficiary"
    WITNESS = "witness"
    INSTRUMENT = "instrument"
    LOCATION = "location"


class SpeechType(str, Enum):
    """Types of direct speech."""
    COMMAND = "command"
    QUESTION = "question"
    BLESSING = "blessing"
    CURSE = "curse"
    PROPHECY = "prophecy"
    PRAYER = "prayer"
    PROMISE = "promise"
    WARNING = "warning"
    NARRATIVE = "narrative"
    DIALOGUE = "dialogue"


class EntityRelationship(Base):
    """Relationships between Torah entities (people, places, etc.)."""
    __tablename__ = "entity_relationships"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_entity_id: Mapped[int] = mapped_column(ForeignKey("torah_names.id"), nullable=False)
    target_entity_id: Mapped[int] = mapped_column(ForeignKey("torah_names.id"), nullable=False)

    relationship_type: Mapped[RelationshipType] = mapped_column(
        SQLEnum(RelationshipType), nullable=False
    )
    relationship_category: Mapped[RelationshipCategory] = mapped_column(
        SQLEnum(RelationshipCategory), nullable=False
    )

    verse_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_verses.id"), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bidirectional: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Processing flags
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    extraction_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_entity_rel_source", "source_entity_id"),
        Index("ix_entity_rel_target", "target_entity_id"),
        Index("ix_entity_rel_type", "relationship_type"),
        Index("ix_entity_rel_category", "relationship_category"),
        Index("ix_entity_rel_verse", "verse_id"),
    )

    def __repr__(self) -> str:
        return f"<EntityRelationship {self.source_entity_id} {self.relationship_type.value} {self.target_entity_id}>"


class Event(Base):
    """Events in the Torah narrative."""
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    event_type: Mapped[EventType] = mapped_column(SQLEnum(EventType), nullable=False)
    event_subtype: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_hebrew: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    verse_start_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    verse_end_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_verses.id"), nullable=True)

    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_names.id"), nullable=True)

    is_miraculous: Mapped[bool] = mapped_column(Boolean, default=False)
    divine_involvement: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # direct, indirect, none

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extraction_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    participants: Mapped[List["EventParticipant"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_events_type", "event_type"),
        Index("ix_events_verse_start", "verse_start_id"),
        Index("ix_events_location", "location_id"),
    )

    def __repr__(self) -> str:
        return f"<Event {self.event_type.value}: {self.description[:50] if self.description else 'N/A'}>"


class EventParticipant(Base):
    """Participants in Torah events."""
    __tablename__ = "event_participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    entity_id: Mapped[int] = mapped_column(ForeignKey("torah_names.id"), nullable=False)

    role: Mapped[ParticipantRole] = mapped_column(SQLEnum(ParticipantRole), nullable=False)
    role_detail: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    event: Mapped["Event"] = relationship(back_populates="participants")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_event_participants_event", "event_id"),
        Index("ix_event_participants_entity", "entity_id"),
    )

    def __repr__(self) -> str:
        return f"<EventParticipant {self.entity_id} as {self.role.value} in {self.event_id}>"


class DirectSpeech(Base):
    """Direct speech occurrences in the Torah."""
    __tablename__ = "direct_speech"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    speaker_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_names.id"), nullable=True)
    addressee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_names.id"), nullable=True)

    speech_type: Mapped[SpeechType] = mapped_column(SQLEnum(SpeechType), nullable=False)
    speech_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    speech_text_hebrew: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_divine_speech: Mapped[bool] = mapped_column(Boolean, default=False)
    is_quoted: Mapped[bool] = mapped_column(Boolean, default=False)  # Quoted from earlier

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extraction_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_direct_speech_verse", "verse_id"),
        Index("ix_direct_speech_speaker", "speaker_id"),
        Index("ix_direct_speech_type", "speech_type"),
        Index("ix_direct_speech_divine", "is_divine_speech"),
    )

    def __repr__(self) -> str:
        return f"<DirectSpeech {self.speech_type.value} in verse {self.verse_id}>"
