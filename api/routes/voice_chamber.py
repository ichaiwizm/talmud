"""Voice Chamber routes - direct speech analysis and visualization."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, case, distinct
from sqlalchemy.orm import Session
from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter, TorahName
from src.db.models.relationships import DirectSpeech, SpeechType

router = APIRouter()


@router.get("/speeches")
def get_speeches(
    book: str | None = None,
    speaker: str | None = None,
    speech_type: str | None = None,
    divine_only: bool = False,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    """Get direct speeches with speaker and addressee info."""
    query = (
        db.query(
            DirectSpeech,
            TorahVerse,
            TorahName.name_canonical.label("speaker_name"),
        )
        .join(TorahVerse, DirectSpeech.verse_id == TorahVerse.id)
        .outerjoin(TorahName, DirectSpeech.speaker_id == TorahName.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
    )

    if book:
        query = query.filter(TorahBook.name == book)
    if divine_only:
        query = query.filter(DirectSpeech.is_divine_speech == True)
    if speech_type:
        query = query.filter(DirectSpeech.speech_type == speech_type)

    query = query.order_by(TorahVerse.id).limit(limit)
    results = query.all()

    # Get addressee names separately
    addressee_ids = [r[0].addressee_id for r in results if r[0].addressee_id]
    addressee_names = {}
    if addressee_ids:
        addressees = db.query(TorahName.id, TorahName.name_canonical).filter(TorahName.id.in_(addressee_ids)).all()
        addressee_names = {a.id: a.name_canonical for a in addressees}

    return [
        {
            "id": speech.id,
            "verse_id": speech.verse_id,
            "verse_ref": verse.ref,
            "speaker": speaker_name or ("God" if speech.is_divine_speech else "Unknown"),
            "addressee": addressee_names.get(speech.addressee_id, "Unknown") if speech.addressee_id else None,
            "speech_type": speech.speech_type.value if speech.speech_type else None,
            "text": speech.speech_text or "",
            "text_hebrew": speech.speech_text_hebrew or "",
            "is_divine": speech.is_divine_speech,
            "is_quoted": speech.is_quoted,
        }
        for speech, verse, speaker_name in results
    ]


@router.get("/speakers")
def get_speakers(db: Session = Depends(get_db)):
    """Get list of speakers with their speech counts."""
    # Named speakers
    named_speakers = (
        db.query(
            TorahName.id,
            TorahName.name_canonical,
            func.count(DirectSpeech.id).label("speech_count"),
            func.sum(case((DirectSpeech.is_divine_speech == True, 1), else_=0)).label("divine_count"),
        )
        .join(DirectSpeech, TorahName.id == DirectSpeech.speaker_id)
        .group_by(TorahName.id, TorahName.name_canonical)
        .order_by(func.count(DirectSpeech.id).desc())
        .limit(30)
        .all()
    )

    # Divine speeches without named speaker
    divine_anonymous = (
        db.query(func.count(DirectSpeech.id))
        .filter(DirectSpeech.is_divine_speech == True)
        .filter(DirectSpeech.speaker_id == None)
        .scalar()
    )

    result = [
        {
            "id": s.id,
            "name": s.name_canonical,
            "speech_count": s.speech_count,
            "divine_count": s.divine_count or 0,
        }
        for s in named_speakers
    ]

    # Add God as speaker if there are divine speeches
    if divine_anonymous and divine_anonymous > 0:
        result.insert(0, {
            "id": None,
            "name": "God",
            "speech_count": divine_anonymous,
            "divine_count": divine_anonymous,
        })

    return result


@router.get("/speech-types")
def get_speech_types(db: Session = Depends(get_db)):
    """Get distribution of speech types."""
    results = (
        db.query(
            DirectSpeech.speech_type,
            func.count(DirectSpeech.id).label("count"),
            func.sum(case((DirectSpeech.is_divine_speech == True, 1), else_=0)).label("divine_count"),
        )
        .group_by(DirectSpeech.speech_type)
        .order_by(func.count(DirectSpeech.id).desc())
        .all()
    )

    return [
        {
            "type": r.speech_type.value if r.speech_type else "unknown",
            "count": r.count,
            "divine_count": r.divine_count or 0,
        }
        for r in results
    ]


@router.get("/network")
def get_speech_network(
    book: str | None = None,
    min_connections: int = 1,
    db: Session = Depends(get_db),
):
    """Get speaker -> addressee network for visualization."""
    query = (
        db.query(
            DirectSpeech.speaker_id,
            DirectSpeech.addressee_id,
            DirectSpeech.is_divine_speech,
            func.count(DirectSpeech.id).label("count"),
        )
        .join(TorahVerse, DirectSpeech.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .filter(DirectSpeech.addressee_id != None)
        .group_by(DirectSpeech.speaker_id, DirectSpeech.addressee_id, DirectSpeech.is_divine_speech)
        .having(func.count(DirectSpeech.id) >= min_connections)
    )

    if book:
        query = query.filter(TorahBook.name == book)

    results = query.all()

    # Get all unique entity IDs
    entity_ids = set()
    for r in results:
        if r.speaker_id:
            entity_ids.add(r.speaker_id)
        if r.addressee_id:
            entity_ids.add(r.addressee_id)

    # Get names
    names = {}
    if entity_ids:
        name_results = db.query(TorahName.id, TorahName.name_canonical).filter(TorahName.id.in_(entity_ids)).all()
        names = {n.id: n.name_canonical for n in name_results}

    # Build nodes and links
    nodes = []
    node_ids = set()

    for r in results:
        speaker_name = names.get(r.speaker_id, "God" if r.is_divine_speech else "Unknown")
        speaker_key = r.speaker_id or "god"
        if speaker_key not in node_ids:
            nodes.append({
                "id": speaker_key,
                "name": speaker_name,
                "is_divine": r.is_divine_speech and not r.speaker_id,
            })
            node_ids.add(speaker_key)

        addressee_name = names.get(r.addressee_id, "Unknown")
        if r.addressee_id and r.addressee_id not in node_ids:
            nodes.append({
                "id": r.addressee_id,
                "name": addressee_name,
                "is_divine": False,
            })
            node_ids.add(r.addressee_id)

    links = [
        {
            "source": r.speaker_id or "god",
            "target": r.addressee_id,
            "count": r.count,
            "is_divine": r.is_divine_speech,
        }
        for r in results
        if r.addressee_id
    ]

    return {"nodes": nodes, "links": links}


@router.get("/by-book")
def get_speeches_by_book(db: Session = Depends(get_db)):
    """Get speech counts by book."""
    results = (
        db.query(
            TorahBook.name,
            func.count(DirectSpeech.id).label("total"),
            func.sum(case((DirectSpeech.is_divine_speech == True, 1), else_=0)).label("divine"),
        )
        .join(TorahChapter, TorahBook.id == TorahChapter.book_id)
        .join(TorahVerse, TorahChapter.id == TorahVerse.chapter_id)
        .join(DirectSpeech, TorahVerse.id == DirectSpeech.verse_id)
        .group_by(TorahBook.name)
        .order_by(TorahBook.id)
        .all()
    )

    return [
        {
            "book": r.name,
            "total": r.total,
            "divine": r.divine or 0,
            "human": r.total - (r.divine or 0),
        }
        for r in results
    ]
