"""Routes for Torah names."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas.names import (
    NameSummary, NameDetail, NameTimeline, CoOccurrenceResponse,
    CoOccurrence, VerseOccurrence, NamePair, GraphResponse
)
from src.api.schemas.common import PaginatedResponse
from src.services.search_service import SearchService
from src.services.stats_service import StatsService
from src.services.timeline_service import TimelineService
from src.services.relation_service import RelationService

router = APIRouter(prefix="/names", tags=["Names"])


@router.get("", response_model=PaginatedResponse[NameSummary])
def list_names(
    name_type: str | None = None,
    book: str | None = None,
    sort_by: str = Query("frequency", enum=["frequency", "alpha"]),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all names with filtering."""
    service = StatsService(db)
    names = service.list_names(name_type=name_type, book_name=book, sort_by=sort_by, limit=limit + offset)
    items = names[offset:offset + limit]

    return PaginatedResponse(
        items=[NameSummary(id=i, name=n["name"], hebrew=n.get("hebrew"),
                          type=n["type"], occurrences=n["occurrences"])
               for i, n in enumerate(items, offset)],
        total=len(names), limit=limit, offset=offset, has_more=offset + limit < len(names)
    )


@router.get("/{name}", response_model=NameDetail)
def get_name(name: str, db: Session = Depends(get_db)):
    """Get detailed name information."""
    service = SearchService(db)
    result = service.get_name_detail(name)
    if not result:
        raise HTTPException(404, f"Name '{name}' not found")

    return NameDetail(
        id=result["id"], name=result["name"], hebrew=result.get("hebrew"),
        type=result["type"], first_mention=result.get("first_mention"),
        description=result.get("description"), occurrences=result["occurrences"],
        verses=[VerseOccurrence(ref=v["ref"], text=v["text"], hebrew=v["hebrew"],
                                surface_form=v["surface_form"]) for v in result["verses"]]
    )


@router.get("/{name}/occurrences")
def get_name_occurrences(
    name: str,
    book: str | None = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Get all verses containing a name."""
    service = SearchService(db)
    return service.find_verses_by_name(name, book_name=book, limit=limit)


@router.get("/{name}/timeline", response_model=NameTimeline)
def get_name_timeline(name: str, limit: int | None = None, db: Session = Depends(get_db)):
    """Get chronological timeline of name occurrences."""
    service = TimelineService(db)
    result = service.get_timeline(name, limit)
    if "error" in result:
        raise HTTPException(404, result["error"])

    return NameTimeline(
        name=result["name"]["canonical"], hebrew=result["name"].get("hebrew"),
        total_occurrences=result["total_occurrences"], by_book=result["by_book"],
        timeline=result["timeline"]
    )


@router.get("/{name}/co-occurrences", response_model=CoOccurrenceResponse)
def get_co_occurrences(
    name: str,
    min_count: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """Get names appearing in same verses."""
    service = RelationService(db)
    result = service.get_co_occurrences(name, min_count, limit)
    if "error" in result:
        raise HTTPException(404, result["error"])

    return CoOccurrenceResponse(
        target_name=result["target"]["name"],
        co_occurrences=[CoOccurrence(**c) for c in result["co_occurrences"]]
    )


@router.get("/{name}/nearby")
def get_nearby_names(
    name: str,
    radius: int = Query(3, ge=1, le=10),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """Get names appearing within N verses."""
    service = TimelineService(db)
    result = service.get_nearby_names(name, radius, limit)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result
