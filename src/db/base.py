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
    from src.db.models import (
        TorahBook,
        TorahChapter,
        TorahVerse,
        TorahName,
        TorahNameAlias,
        TorahNameOccurrence,
    )

    Base.metadata.create_all(bind=engine)
