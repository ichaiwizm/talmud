from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.config.settings import settings


class Base(DeclarativeBase):
    pass


def get_engine():
    connect_args = {}
    if "sqlite" in settings.database_url:
        connect_args["check_same_thread"] = False

    return create_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args=connect_args,
    )


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    # Core models
    from src.db.models import (
        TorahBook,
        TorahChapter,
        TorahVerse,
        TorahName,
        TorahNameAlias,
        TorahNameOccurrence,
        TorahWord,
    )

    # Relationship models
    from src.db.models import (
        EntityRelationship,
        Event,
        EventParticipant,
        DirectSpeech,
    )

    # Theological models
    from src.db.models import (
        DivineNameOccurrence,
        Mitzvah,
        Covenant,
        CovenantElement,
        BlessingCurse,
    )

    # Narrative models
    from src.db.models import (
        NarrativeUnit,
        Parsha,
        Genealogy,
        Marriage,
        VerseTopic,
        VerseTheme,
    )

    # Linguistic models
    from src.db.models import (
        HebrewRoot,
        WordRoot,
        FormulaicExpression,
        FormulaOccurrence,
        LiteraryStructure,
    )

    # Enrichment models
    from src.db.models import (
        VerseSentiment,
        CharacterEmotion,
        SymbolicNumber,
        SymbolicElement,
        RecurringMotif,
        MotifOccurrence,
        CrossReference,
    )

    Base.metadata.create_all(bind=engine)
