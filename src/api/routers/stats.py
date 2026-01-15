"""Statistics routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas.stats import GlobalStats
from src.api.schemas.names import NameSummary, NamePair, GraphResponse, GraphNode, GraphEdge
from src.services.stats_service import StatsService
from src.services.relation_service import RelationService

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("", response_model=GlobalStats)
def get_global_stats(db: Session = Depends(get_db)):
    """Get global statistics."""
    service = StatsService(db)
    result = service.get_global_stats()
    return GlobalStats(**result)


@router.get("/by-book/{book_name}", response_model=GlobalStats)
def get_book_stats(book_name: str, db: Session = Depends(get_db)):
    """Get statistics for a specific book."""
    service = StatsService(db)
    result = service.get_global_stats(book_name)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return GlobalStats(**result)


@router.get("/top-names", response_model=list[NameSummary])
def get_top_names(
    limit: int = Query(20, le=100),
    name_type: str | None = Query(None, description="Filter by type"),
    book: str | None = Query(None, description="Filter by book"),
    db: Session = Depends(get_db),
):
    """Get top names by occurrence count."""
    service = StatsService(db)
    results = service.get_top_names(limit=limit, name_type=name_type, book_name=book)
    return [
        NameSummary(
            id=i, name=r["name"], hebrew=r.get("hebrew"),
            type=r["type"], occurrences=r["occurrences"], first_mention=r.get("first_mention")
        )
        for i, r in enumerate(results)
    ]


@router.get("/pairs", response_model=list[NamePair])
def get_name_pairs(
    limit: int = Query(20, le=100),
    name_type: str | None = Query(None, description="Filter by type"),
    db: Session = Depends(get_db),
):
    """Get most frequent pairs of names appearing together."""
    service = RelationService(db)
    results = service.get_name_pairs(name_type=name_type, limit=limit)
    return [NamePair(**r) for r in results]


@router.get("/graph", response_model=GraphResponse)
def get_graph(
    min_weight: int = Query(2, ge=1),
    name_type: str | None = Query(None, description="Filter by type"),
    db: Session = Depends(get_db),
):
    """Export co-occurrence data as graph structure for visualization."""
    service = RelationService(db)
    result = service.export_graph(min_weight=min_weight, name_type=name_type)
    return GraphResponse(
        nodes=[GraphNode(**n, occurrences=0) for n in result["nodes"]],
        edges=[GraphEdge(**e) for e in result["edges"]]
    )
