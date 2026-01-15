"""Admin routes for import, extraction, and population."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas.stats import (
    ImportStatus, ExtractionStatus, ExtractionRequest,
    PopulateRequest, GematriaPopulationStatus
)
from src.api.schemas.common import BackgroundTaskResponse
from src.services.import_service import TorahImportService
from src.services.extraction_service import NameExtractionService
from src.services.gematria.populate import populate_all_words, get_population_status
from src.providers.sefaria.client import TORAH_BOOKS
from src.db.base import SessionLocal

router = APIRouter(prefix="/admin", tags=["Admin"])


def _get_new_db():
    """Get a new DB session for background tasks."""
    return SessionLocal()


@router.get("/import/status", response_model=ImportStatus)
def import_status(db: Session = Depends(get_db)):
    """Get Torah import status."""
    service = TorahImportService(db)
    return ImportStatus(**service.get_import_status())


@router.post("/import/torah", response_model=BackgroundTaskResponse)
def import_torah(background_tasks: BackgroundTasks):
    """Import all Torah books (runs in background)."""
    def do_import():
        db = _get_new_db()
        try:
            service = TorahImportService(db)
            service.import_all_books()
            service.close()
        finally:
            db.close()

    background_tasks.add_task(do_import)
    return BackgroundTaskResponse(status="started", message="Torah import started")


@router.post("/import/book/{book_name}")
def import_book(book_name: str, db: Session = Depends(get_db)):
    """Import specific Torah book."""
    if book_name not in TORAH_BOOKS:
        raise HTTPException(400, f"Invalid book. Choose from: {TORAH_BOOKS}")

    service = TorahImportService(db)
    order = TORAH_BOOKS.index(book_name) + 1
    result = service.import_book(book_name, order)
    service.close()
    return result


@router.get("/extraction/status", response_model=ExtractionStatus)
def extraction_status(db: Session = Depends(get_db)):
    """Get name extraction status."""
    service = NameExtractionService(db)
    result = service.get_extraction_status()
    return ExtractionStatus(**result)


@router.post("/extraction/start", response_model=BackgroundTaskResponse)
def start_extraction(request: ExtractionRequest, background_tasks: BackgroundTasks):
    """Start name extraction (runs in background)."""
    def do_extraction():
        db = _get_new_db()
        try:
            service = NameExtractionService(db)
            service.extract_bulk(
                limit=request.limit, batch_size=request.batch_size,
                parallel=request.parallel, workers=request.workers
            )
        finally:
            db.close()

    background_tasks.add_task(do_extraction)
    return BackgroundTaskResponse(status="started", message="Extraction started")


@router.post("/extraction/retry")
def retry_extraction(limit: int | None = None, db: Session = Depends(get_db)):
    """Retry failed extractions."""
    service = NameExtractionService(db)
    return service.retry_errors(limit)


@router.get("/gematria/status", response_model=GematriaPopulationStatus)
def gematria_status(db: Session = Depends(get_db)):
    """Get gematria population status."""
    result = get_population_status(db)
    return GematriaPopulationStatus(**result)


@router.post("/gematria/populate", response_model=BackgroundTaskResponse)
def populate_gematria(request: PopulateRequest, background_tasks: BackgroundTasks):
    """Populate gematria data (runs in background)."""
    def do_populate():
        db = _get_new_db()
        try:
            populate_all_words(db, limit=request.limit, book_name=request.book)
        finally:
            db.close()

    background_tasks.add_task(do_populate)
    return BackgroundTaskResponse(status="started", message="Gematria population started")


@router.get("/health")
def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    """Database connectivity check."""
    from sqlalchemy import text
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(503, f"Database error: {e}")
