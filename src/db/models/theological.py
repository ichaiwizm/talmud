"""Database models for theological content: divine names, mitzvot, covenants, blessings."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Float, Boolean, Integer, ForeignKey, DateTime, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class DivineNameType(str, Enum):
    """Types of divine names."""
    YHWH = "yhwh"
    ELOHIM = "elohim"
    EL_SHADDAI = "el_shaddai"
    EL_ELYON = "el_elyon"
    ADONAI = "adonai"
    EL = "el"
    EHYEH = "ehyeh"
    OTHER = "other"


class ContextType(str, Enum):
    """Context types for divine name usage."""
    CREATION = "creation"
    COVENANT = "covenant"
    JUDGMENT = "judgment"
    MERCY = "mercy"
    REVELATION = "revelation"
    BLESSING = "blessing"
    COMMAND = "command"
    NARRATIVE = "narrative"


class MitzvahType(str, Enum):
    """Types of commandments."""
    POSITIVE = "aseh"  # Do this
    NEGATIVE = "lo_taaseh"  # Don't do this


class MitzvahCategory(str, Enum):
    """Categories of commandments."""
    MISHPATIM = "mishpatim"  # Rational laws
    CHUKIM = "chukim"  # Statutes without rational explanation
    EDOT = "edot"  # Testimonies/commemorative laws


class MitzvahDomain(str, Enum):
    """Domains of commandments."""
    SHABBAT = "shabbat"
    KASHRUT = "kashrut"
    PURITY = "purity"
    CIVIL = "civil"
    CRIMINAL = "criminal"
    TEMPLE = "temple"
    PRAYER = "prayer"
    FAMILY = "family"
    AGRICULTURE = "agriculture"
    ETHICS = "ethics"
    IDOLATRY = "idolatry"
    FESTIVALS = "festivals"


class CovenantType(str, Enum):
    """Types of covenants."""
    UNCONDITIONAL = "unconditional"
    CONDITIONAL = "conditional"


class BlessingCurseType(str, Enum):
    """Types of blessings and curses."""
    BLESSING = "blessing"
    CURSE = "curse"


class BlessingCurseCategory(str, Enum):
    """Categories of blessings and curses."""
    PATRIARCHAL = "patriarchal"
    PRIESTLY = "priestly"
    MOSAIC = "mosaic"
    COVENANTAL = "covenantal"
    DEATHBED = "deathbed"
    PROPHETIC = "prophetic"


class DivineNameOccurrence(Base):
    """Occurrences of divine names in the Torah."""
    __tablename__ = "divine_name_occurrences"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    divine_name: Mapped[DivineNameType] = mapped_column(SQLEnum(DivineNameType), nullable=False)
    divine_name_hebrew: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    divine_name_surface: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    context_type: Mapped[Optional[ContextType]] = mapped_column(SQLEnum(ContextType), nullable=True)
    speaker_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # narrator, god_self, human, angel
    grammatical_form: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    theological_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_divine_names_verse", "verse_id"),
        Index("ix_divine_names_name", "divine_name"),
        Index("ix_divine_names_context", "context_type"),
    )

    def __repr__(self) -> str:
        return f"<DivineNameOccurrence {self.divine_name.value} in verse {self.verse_id}>"


class Mitzvah(Base):
    """Commandments (mitzvot) extracted from the Torah."""
    __tablename__ = "mitzvot"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    command_text: Mapped[str] = mapped_column(Text, nullable=False)
    command_text_hebrew: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    mitzvah_type: Mapped[MitzvahType] = mapped_column(SQLEnum(MitzvahType), nullable=False)
    category: Mapped[Optional[MitzvahCategory]] = mapped_column(SQLEnum(MitzvahCategory), nullable=True)
    domain: Mapped[Optional[MitzvahDomain]] = mapped_column(SQLEnum(MitzvahDomain), nullable=True)

    applies_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # all_israel, priests, men, women
    penalty: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    traditional_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Rambam numbering
    rambam_reference: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extraction_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_mitzvot_verse", "verse_id"),
        Index("ix_mitzvot_type", "mitzvah_type"),
        Index("ix_mitzvot_domain", "domain"),
        Index("ix_mitzvot_number", "traditional_number"),
    )

    def __repr__(self) -> str:
        return f"<Mitzvah {self.mitzvah_type.value}: {self.command_text[:50]}>"


class Covenant(Base):
    """Covenants (britot) in the Torah."""
    __tablename__ = "covenants"

    id: Mapped[int] = mapped_column(primary_key=True)

    covenant_name: Mapped[str] = mapped_column(String(100), nullable=False)
    covenant_name_hebrew: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    party_divine: Mapped[str] = mapped_column(String(100), default="God")
    party_human: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Noah, Abraham, Israel
    party_human_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_names.id"), nullable=True)

    covenant_sign: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # rainbow, circumcision, shabbat
    covenant_type: Mapped[CovenantType] = mapped_column(SQLEnum(CovenantType), nullable=False)

    verse_start_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)
    verse_end_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_verses.id"), nullable=True)

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    elements: Mapped[List["CovenantElement"]] = relationship(
        back_populates="covenant", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_covenants_party_human", "party_human"),
        Index("ix_covenants_verse_start", "verse_start_id"),
    )

    def __repr__(self) -> str:
        return f"<Covenant {self.covenant_name} with {self.party_human}>"


class CovenantElement(Base):
    """Elements of covenants (promises, obligations, signs, ceremonies)."""
    __tablename__ = "covenant_elements"

    id: Mapped[int] = mapped_column(primary_key=True)
    covenant_id: Mapped[int] = mapped_column(ForeignKey("covenants.id"), nullable=False)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    element_type: Mapped[str] = mapped_column(String(50), nullable=False)  # promise, obligation, sign, ceremony
    element_content: Mapped[str] = mapped_column(Text, nullable=False)
    element_content_hebrew: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    covenant: Mapped["Covenant"] = relationship(back_populates="elements")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_covenant_elements_covenant", "covenant_id"),
        Index("ix_covenant_elements_verse", "verse_id"),
    )

    def __repr__(self) -> str:
        return f"<CovenantElement {self.element_type} in covenant {self.covenant_id}>"


class BlessingCurse(Base):
    """Blessings and curses in the Torah."""
    __tablename__ = "blessings_curses"

    id: Mapped[int] = mapped_column(primary_key=True)
    verse_id: Mapped[int] = mapped_column(ForeignKey("torah_verses.id"), nullable=False)

    blessing_type: Mapped[BlessingCurseType] = mapped_column(SQLEnum(BlessingCurseType), nullable=False)
    category: Mapped[Optional[BlessingCurseCategory]] = mapped_column(
        SQLEnum(BlessingCurseCategory), nullable=True
    )

    giver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_names.id"), nullable=True)
    giver_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    recipient_id: Mapped[Optional[int]] = mapped_column(ForeignKey("torah_names.id"), nullable=True)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hebrew: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_conditional: Mapped[bool] = mapped_column(Boolean, default=False)
    condition_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_divine: Mapped[bool] = mapped_column(Boolean, default=False)
    is_prophetic: Mapped[bool] = mapped_column(Boolean, default=False)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_blessings_curses_verse", "verse_id"),
        Index("ix_blessings_curses_type", "blessing_type"),
        Index("ix_blessings_curses_giver", "giver_id"),
        Index("ix_blessings_curses_recipient", "recipient_id"),
    )

    def __repr__(self) -> str:
        return f"<BlessingCurse {self.blessing_type.value} in verse {self.verse_id}>"
