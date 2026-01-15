"""Search routes for names and verses."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas.names import NameSummary
from src.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/names", response_model=list[NameSummary])
def search_names(
    q: str = Query(..., min_length=1, description="Search query"),
    exact: bool = Query(False, description="Exact match only"),
    include_hebrew: bool = Query(False, description="Also search Hebrew names"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Search for names by query."""
    service = SearchService(db)
    results = service.search_name(q, exact=exact, include_hebrew=include_hebrew)
    return [
        NameSummary(
            id=r["id"], name=r["name"], hebrew=r.get("hebrew"),
            type=r["type"], occurrences=r["occurrences"], first_mention=r.get("first_mention")
        )
        for r in results[:limit]
    ]


@router.get("/verses")
def search_verses(
    q: str = Query(..., min_length=1, description="Search query"),
    book: str | None = Query(None, description="Filter by book name"),
    hebrew: bool = Query(False, description="Search in Hebrew text"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Search for verses containing text."""
    service = SearchService(db)
    return service.search_verses(q, book_name=book, search_hebrew=hebrew, limit=limit)
