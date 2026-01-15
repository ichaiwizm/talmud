import click
import logging

from src.db.base import SessionLocal, init_db
from src.db.models.torah import TorahVerse
from src.db.models.names import TorahName, TorahNameOccurrence
from src.services.import_service import TorahImportService
from src.services.extraction_service import NameExtractionService
from src.providers.sefaria.client import TORAH_BOOKS
from src.config.settings import settings

# Import new CLI command modules
from src.cli.stats import stats_commands
from src.cli.search import search_commands
from src.cli.relations import relation_commands
from src.cli.gematria import gematria_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Torah Names Extraction CLI."""
    pass


@cli.command("init-db")
def init_database():
    """Initialize the database schema."""
    init_db()
    click.echo("Database initialized successfully")


@cli.command("import-torah")
@click.option("--book", "-b", help="Import only this book (e.g., Genesis)")
def import_torah(book: str):
    """Import Torah text from Sefaria API."""
    db = SessionLocal()
    try:
        service = TorahImportService(db)

        if book:
            if book not in TORAH_BOOKS:
                click.echo(f"Invalid book. Choose from: {TORAH_BOOKS}")
                return
            order = TORAH_BOOKS.index(book) + 1
            result = service.import_book(book, order)
            click.echo(
                f"Imported {book}: {result['chapters']} chapters, "
                f"{result['verses']} verses"
            )
        else:
            result = service.import_all_books()
            click.echo(
                f"Import complete: {result['books']} books, "
                f"{result['chapters']} chapters, {result['verses']} verses"
            )
            if result["errors"]:
                click.echo(f"Errors: {result['errors']}")

        service.close()
    finally:
        db.close()


@cli.command("import-status")
def import_status():
    """Show import status."""
    db = SessionLocal()
    try:
        service = TorahImportService(db)
        status = service.get_import_status()
        click.echo(f"Books: {status['books']}/{status['expected_books']}")
        click.echo(f"Chapters: {status['chapters']}")
        click.echo(f"Verses: {status['verses']}")
    finally:
        db.close()


@cli.command("extract-names")
@click.option("--limit", "-l", type=int, help="Maximum verses to process")
@click.option("--model", "-m", default=None, help="Claude model to use (default from settings)")
@click.option("--bulk", "-b", is_flag=True, help="Use bulk extraction (multiple verses per request)")
@click.option("--batch-size", "-s", type=int, default=None, help="Verses per bulk request (default from settings)")
@click.option("--parallel", "-p", is_flag=True, help="Use parallel requests")
@click.option("--workers", "-w", type=int, default=1, help="Number of parallel workers (max 10 for bulk)")
def extract_names(limit: int, model: str, bulk: bool, batch_size: int, parallel: bool, workers: int):
    """Extract names from Torah verses using Claude."""
    model = model or settings.claude_model
    batch_size = batch_size or settings.bulk_size

    db = SessionLocal()
    try:
        service = NameExtractionService(db, model=model, max_workers=workers)

        if bulk:
            if parallel:
                workers = min(workers, 10)
                click.echo(f"Starting parallel bulk extraction: {model}, {batch_size} verses/request, {workers} workers...")
            else:
                click.echo(f"Starting bulk extraction with {model}, {batch_size} verses per request...")
            result = service.extract_bulk(limit=limit, batch_size=batch_size, parallel=parallel, workers=workers)
        elif parallel:
            click.echo(f"Starting parallel extraction with {workers} workers (legacy mode)...")
            result = service.extract_all_pending(limit=limit, parallel=parallel)
        else:
            result = service.extract_all_pending(limit=limit, parallel=False)

        click.echo(f"Processed: {result['processed']} verses")
        click.echo(f"Names found: {result['names_found']}")
        click.echo(f"Errors: {result['errors']}")
    finally:
        db.close()


@cli.command("extraction-status")
def extraction_status():
    """Show extraction status."""
    db = SessionLocal()
    try:
        service = NameExtractionService(db)
        status = service.get_extraction_status()
        click.echo(f"Total verses: {status['total_verses']}")
        click.echo(f"Processed: {status['processed']} ({status['progress_percent']}%)")
        click.echo(f"Pending: {status['pending']}")
        click.echo(f"With errors: {status['with_errors']}")
        click.echo(f"Unique names: {status['unique_names']}")
        click.echo(f"Total occurrences: {status['total_occurrences']}")
    finally:
        db.close()


@cli.command("retry-errors")
@click.option("--limit", "-l", type=int, help="Maximum verses to retry")
def retry_errors(limit: int):
    """Retry extraction on verses with errors."""
    db = SessionLocal()
    try:
        service = NameExtractionService(db)
        result = service.retry_errors(limit=limit)
        click.echo(f"Retried: {result['processed']} verses")
        click.echo(f"Names found: {result['names_found']}")
        click.echo(f"Still failing: {result['errors']}")
    finally:
        db.close()


@cli.command("reset-extraction")
@click.option("--confirm", is_flag=True, help="Confirm deletion without prompt")
def reset_extraction(confirm: bool):
    """Reset all extraction data (delete names and occurrences)."""
    if not confirm:
        click.confirm(
            "This will delete ALL extracted names and occurrences. Continue?",
            abort=True,
        )

    db = SessionLocal()
    try:
        # Delete occurrences first (FK constraint)
        occ_count = db.query(TorahNameOccurrence).delete()
        click.echo(f"Deleted {occ_count} occurrences")

        # Delete names
        name_count = db.query(TorahName).delete()
        click.echo(f"Deleted {name_count} names")

        # Reset processed flag on all verses
        verse_count = db.query(TorahVerse).update(
            {TorahVerse.processed: False, TorahVerse.processed_at: None, TorahVerse.extraction_error: None}
        )
        click.echo(f"Reset {verse_count} verses")

        db.commit()
        click.echo("Extraction data reset complete")
    finally:
        db.close()


# Register new commands
for cmd in stats_commands:
    cli.add_command(cmd)

for cmd in search_commands:
    cli.add_command(cmd)

for cmd in relation_commands:
    cli.add_command(cmd)

for cmd in gematria_commands:
    cli.add_command(cmd)


if __name__ == "__main__":
    cli()
