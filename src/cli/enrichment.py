"""CLI commands for Torah enrichment extraction (relationships, theological, narrative, linguistic, sentiment)."""
import click
import logging

from src.db.base import SessionLocal
from src.config.settings import settings

logger = logging.getLogger(__name__)


# ============== EXTRACTION COMMANDS ==============

@click.command("extract-relationships")
@click.option("--limit", "-l", type=int, help="Maximum verses to process")
@click.option("--model", "-m", default=None, help="Claude model to use")
@click.option("--batch-size", "-s", type=int, default=30, help="Verses per request")
@click.option("--parallel", "-p", is_flag=True, help="Use parallel requests")
@click.option("--workers", "-w", type=int, default=3, help="Number of parallel workers")
def extract_relationships(limit: int, model: str, batch_size: int, parallel: bool, workers: int):
    """Extract entity relationships, events, and direct speech from Torah verses."""
    from src.services.relationship_extraction_service import RelationshipExtractionService

    model = model or settings.claude_model
    db = SessionLocal()
    try:
        service = RelationshipExtractionService(db, model=model, max_workers=workers)
        click.echo(f"Starting relationship extraction: {model}, {batch_size} verses/request...")

        result = service.extract_bulk(limit=limit, batch_size=batch_size, parallel=parallel, workers=workers)

        click.echo(f"Processed: {result.processed} verses")
        click.echo(f"Items extracted: {result.items_found}")
        click.echo(f"Errors: {result.errors}")
    finally:
        db.close()


@click.command("extract-theological")
@click.option("--limit", "-l", type=int, help="Maximum verses to process")
@click.option("--model", "-m", default=None, help="Claude model to use")
@click.option("--batch-size", "-s", type=int, default=30, help="Verses per request")
@click.option("--parallel", "-p", is_flag=True, help="Use parallel requests")
@click.option("--workers", "-w", type=int, default=3, help="Number of parallel workers")
def extract_theological(limit: int, model: str, batch_size: int, parallel: bool, workers: int):
    """Extract theological content: divine names, mitzvot, blessings/curses."""
    from src.services.theological_extraction_service import TheologicalExtractionService

    model = model or settings.claude_model
    db = SessionLocal()
    try:
        service = TheologicalExtractionService(db, model=model, max_workers=workers)
        click.echo(f"Starting theological extraction: {model}, {batch_size} verses/request...")

        result = service.extract_bulk(limit=limit, batch_size=batch_size, parallel=parallel, workers=workers)

        click.echo(f"Processed: {result.processed} verses")
        click.echo(f"Items extracted: {result.items_found}")
        click.echo(f"Errors: {result.errors}")
    finally:
        db.close()


@click.command("extract-narrative")
@click.option("--limit", "-l", type=int, help="Maximum verses to process")
@click.option("--model", "-m", default=None, help="Claude model to use")
@click.option("--batch-size", "-s", type=int, default=30, help="Verses per request")
@click.option("--parallel", "-p", is_flag=True, help="Use parallel requests")
@click.option("--workers", "-w", type=int, default=3, help="Number of parallel workers")
def extract_narrative(limit: int, model: str, batch_size: int, parallel: bool, workers: int):
    """Extract narrative structure: genealogy, marriages, topics, themes."""
    from src.services.narrative_extraction_service import NarrativeExtractionService

    model = model or settings.claude_model
    db = SessionLocal()
    try:
        service = NarrativeExtractionService(db, model=model, max_workers=workers)
        click.echo(f"Starting narrative extraction: {model}, {batch_size} verses/request...")

        result = service.extract_bulk(limit=limit, batch_size=batch_size, parallel=parallel, workers=workers)

        click.echo(f"Processed: {result.processed} verses")
        click.echo(f"Items extracted: {result.items_found}")
        click.echo(f"Errors: {result.errors}")
    finally:
        db.close()


@click.command("extract-linguistic")
@click.option("--limit", "-l", type=int, help="Maximum verses to process")
@click.option("--model", "-m", default=None, help="Claude model to use")
@click.option("--batch-size", "-s", type=int, default=20, help="Verses per request")
@click.option("--parallel", "-p", is_flag=True, help="Use parallel requests")
@click.option("--workers", "-w", type=int, default=3, help="Number of parallel workers")
def extract_linguistic(limit: int, model: str, batch_size: int, parallel: bool, workers: int):
    """Extract linguistic data: Hebrew roots, formulaic expressions."""
    from src.services.linguistic_extraction_service import LinguisticExtractionService

    model = model or settings.claude_model
    db = SessionLocal()
    try:
        service = LinguisticExtractionService(db, model=model, max_workers=workers)
        click.echo(f"Starting linguistic extraction: {model}, {batch_size} verses/request...")

        result = service.extract_bulk(limit=limit, batch_size=batch_size, parallel=parallel, workers=workers)

        click.echo(f"Processed: {result.processed} verses")
        click.echo(f"Items extracted: {result.items_found}")
        click.echo(f"Errors: {result.errors}")
    finally:
        db.close()


@click.command("extract-enrichment")
@click.option("--limit", "-l", type=int, help="Maximum verses to process")
@click.option("--model", "-m", default=None, help="Claude model to use")
@click.option("--batch-size", "-s", type=int, default=25, help="Verses per request")
@click.option("--parallel", "-p", is_flag=True, help="Use parallel requests")
@click.option("--workers", "-w", type=int, default=3, help="Number of parallel workers")
def extract_enrichment(limit: int, model: str, batch_size: int, parallel: bool, workers: int):
    """Extract enrichments: sentiment, symbols, numbers."""
    from src.services.enrichment_extraction_service import EnrichmentExtractionService

    model = model or settings.claude_model
    db = SessionLocal()
    try:
        service = EnrichmentExtractionService(db, model=model, max_workers=workers)
        click.echo(f"Starting enrichment extraction: {model}, {batch_size} verses/request...")

        result = service.extract_bulk(limit=limit, batch_size=batch_size, parallel=parallel, workers=workers)

        click.echo(f"Processed: {result.processed} verses")
        click.echo(f"Items extracted: {result.items_found}")
        click.echo(f"Errors: {result.errors}")
    finally:
        db.close()


@click.command("extract-all")
@click.option("--limit", "-l", type=int, help="Maximum verses to process per extraction type")
@click.option("--model", "-m", default=None, help="Claude model to use")
@click.option("--batch-size", "-s", type=int, default=25, help="Verses per request")
@click.option("--parallel", "-p", is_flag=True, help="Use parallel requests")
@click.option("--workers", "-w", type=int, default=3, help="Number of parallel workers")
@click.option("--types", "-t", multiple=True,
              type=click.Choice(["relationships", "theological", "narrative", "linguistic", "enrichment"]),
              help="Specific extraction types to run (default: all)")
def extract_all(limit: int, model: str, batch_size: int, parallel: bool, workers: int, types: tuple):
    """Run all extraction types sequentially."""
    from src.services.relationship_extraction_service import RelationshipExtractionService
    from src.services.theological_extraction_service import TheologicalExtractionService
    from src.services.narrative_extraction_service import NarrativeExtractionService
    from src.services.linguistic_extraction_service import LinguisticExtractionService
    from src.services.enrichment_extraction_service import EnrichmentExtractionService

    model = model or settings.claude_model
    types_to_run = types if types else ("relationships", "theological", "narrative", "linguistic", "enrichment")

    db = SessionLocal()
    try:
        services = {
            "relationships": (RelationshipExtractionService, "Relationships/Events/Speech"),
            "theological": (TheologicalExtractionService, "Divine Names/Mitzvot/Blessings"),
            "narrative": (NarrativeExtractionService, "Genealogy/Topics/Themes"),
            "linguistic": (LinguisticExtractionService, "Hebrew Roots/Formulas"),
            "enrichment": (EnrichmentExtractionService, "Sentiment/Symbols/Numbers"),
        }

        total_processed = 0
        total_items = 0
        total_errors = 0

        for ext_type in types_to_run:
            if ext_type not in services:
                continue

            service_class, description = services[ext_type]
            click.echo(f"\n{'=' * 50}")
            click.echo(f"Extracting: {description}")
            click.echo(f"{'=' * 50}")

            service = service_class(db, model=model, max_workers=workers)
            result = service.extract_bulk(limit=limit, batch_size=batch_size, parallel=parallel, workers=workers)

            click.echo(f"  Processed: {result.processed}")
            click.echo(f"  Items: {result.items_found}")
            click.echo(f"  Errors: {result.errors}")

            total_processed += result.processed
            total_items += result.items_found
            total_errors += result.errors

        click.echo(f"\n{'=' * 50}")
        click.echo("TOTAL EXTRACTION SUMMARY")
        click.echo(f"{'=' * 50}")
        click.echo(f"Total processed: {total_processed}")
        click.echo(f"Total items extracted: {total_items}")
        click.echo(f"Total errors: {total_errors}")
    finally:
        db.close()


# ============== STATUS COMMANDS ==============

@click.command("enrichment-status")
def enrichment_status():
    """Show status of all enrichment extractions."""
    from src.services.relationship_extraction_service import RelationshipExtractionService
    from src.services.theological_extraction_service import TheologicalExtractionService
    from src.services.narrative_extraction_service import NarrativeExtractionService
    from src.services.linguistic_extraction_service import LinguisticExtractionService
    from src.services.enrichment_extraction_service import EnrichmentExtractionService

    db = SessionLocal()
    try:
        click.echo("\n=== RELATIONSHIP EXTRACTION ===")
        rel_service = RelationshipExtractionService(db)
        rel_status = rel_service.get_extraction_status()
        for key, value in rel_status.items():
            click.echo(f"  {key}: {value}")

        click.echo("\n=== THEOLOGICAL EXTRACTION ===")
        theo_service = TheologicalExtractionService(db)
        theo_status = theo_service.get_extraction_status()
        for key, value in theo_status.items():
            click.echo(f"  {key}: {value}")

        click.echo("\n=== NARRATIVE EXTRACTION ===")
        narr_service = NarrativeExtractionService(db)
        narr_status = narr_service.get_extraction_status()
        for key, value in narr_status.items():
            click.echo(f"  {key}: {value}")

        click.echo("\n=== LINGUISTIC EXTRACTION ===")
        ling_service = LinguisticExtractionService(db)
        ling_status = ling_service.get_extraction_status()
        for key, value in ling_status.items():
            click.echo(f"  {key}: {value}")

        click.echo("\n=== ENRICHMENT EXTRACTION ===")
        enr_service = EnrichmentExtractionService(db)
        enr_status = enr_service.get_extraction_status()
        for key, value in enr_status.items():
            click.echo(f"  {key}: {value}")

    finally:
        db.close()


# ============== QUERY COMMANDS ==============

@click.command("query-relationships")
@click.option("--source", "-s", help="Source entity name")
@click.option("--target", "-t", help="Target entity name")
@click.option("--type", "-r", "rel_type", help="Relationship type")
@click.option("--category", "-c", help="Relationship category (family, political, spiritual, spatial)")
@click.option("--limit", "-l", type=int, default=20, help="Maximum results")
def query_relationships(source: str, target: str, rel_type: str, category: str, limit: int):
    """Query entity relationships."""
    from src.db.models.relationships import EntityRelationship
    from src.db.models.names import TorahName

    db = SessionLocal()
    try:
        query = db.query(EntityRelationship)

        if source:
            source_name = db.query(TorahName).filter(TorahName.name_canonical.ilike(f"%{source}%")).first()
            if source_name:
                query = query.filter(EntityRelationship.source_entity_id == source_name.id)

        if target:
            target_name = db.query(TorahName).filter(TorahName.name_canonical.ilike(f"%{target}%")).first()
            if target_name:
                query = query.filter(EntityRelationship.target_entity_id == target_name.id)

        if rel_type:
            query = query.filter(EntityRelationship.relationship_type == rel_type)

        if category:
            query = query.filter(EntityRelationship.relationship_category == category)

        results = query.limit(limit).all()

        if not results:
            click.echo("No relationships found")
            return

        click.echo(f"\nFound {len(results)} relationships:\n")
        for rel in results:
            src = db.query(TorahName).get(rel.source_entity_id)
            tgt = db.query(TorahName).get(rel.target_entity_id)
            click.echo(f"  {src.name_canonical if src else '?'} --[{rel.relationship_type.value}]--> {tgt.name_canonical if tgt else '?'}")
            click.echo(f"    Category: {rel.relationship_category.value}, Confidence: {rel.confidence}")
    finally:
        db.close()


@click.command("query-events")
@click.option("--type", "-t", "event_type", help="Event type (birth, death, marriage, covenant, miracle, etc.)")
@click.option("--person", "-p", help="Person involved in event")
@click.option("--miraculous", "-m", is_flag=True, help="Only miraculous events")
@click.option("--limit", "-l", type=int, default=20, help="Maximum results")
def query_events(event_type: str, person: str, miraculous: bool, limit: int):
    """Query events in the Torah narrative."""
    from src.db.models.relationships import Event, EventParticipant
    from src.db.models.names import TorahName
    from src.db.models.torah import TorahVerse

    db = SessionLocal()
    try:
        query = db.query(Event)

        if event_type:
            query = query.filter(Event.event_type == event_type)

        if miraculous:
            query = query.filter(Event.is_miraculous == True)

        if person:
            person_name = db.query(TorahName).filter(TorahName.name_canonical.ilike(f"%{person}%")).first()
            if person_name:
                participant_events = db.query(EventParticipant.event_id).filter(
                    EventParticipant.entity_id == person_name.id
                ).subquery()
                query = query.filter(Event.id.in_(participant_events))

        results = query.limit(limit).all()

        if not results:
            click.echo("No events found")
            return

        click.echo(f"\nFound {len(results)} events:\n")
        for event in results:
            verse = db.query(TorahVerse).get(event.verse_start_id)
            click.echo(f"  [{event.event_type.value}] {event.description}")
            click.echo(f"    Verse: {verse.ref if verse else '?'}")
            if event.is_miraculous:
                click.echo(f"    Miraculous: Yes, Divine involvement: {event.divine_involvement}")

            participants = db.query(EventParticipant).filter(EventParticipant.event_id == event.id).all()
            if participants:
                parts = []
                for p in participants:
                    name = db.query(TorahName).get(p.entity_id)
                    parts.append(f"{name.name_canonical if name else '?'} ({p.role.value})")
                click.echo(f"    Participants: {', '.join(parts)}")
            click.echo()
    finally:
        db.close()


@click.command("query-divine-names")
@click.option("--name", "-n", help="Divine name type (yhwh, elohim, el_shaddai, etc.)")
@click.option("--context", "-c", help="Context type (creation, covenant, judgment, mercy, etc.)")
@click.option("--book", "-b", help="Book name")
@click.option("--limit", "-l", type=int, default=20, help="Maximum results")
def query_divine_names(name: str, context: str, book: str, limit: int):
    """Query divine name occurrences."""
    from src.db.models.theological import DivineNameOccurrence
    from src.db.models.torah import TorahVerse, TorahChapter, TorahBook

    db = SessionLocal()
    try:
        query = db.query(DivineNameOccurrence).join(TorahVerse)

        if name:
            query = query.filter(DivineNameOccurrence.divine_name == name)

        if context:
            query = query.filter(DivineNameOccurrence.context_type == context)

        if book:
            book_obj = db.query(TorahBook).filter(TorahBook.name.ilike(f"%{book}%")).first()
            if book_obj:
                query = query.join(TorahChapter).filter(TorahChapter.book_id == book_obj.id)

        results = query.limit(limit).all()

        if not results:
            click.echo("No divine name occurrences found")
            return

        click.echo(f"\nFound {len(results)} occurrences:\n")
        for dn in results:
            verse = db.query(TorahVerse).get(dn.verse_id)
            click.echo(f"  {dn.divine_name.value} ({dn.divine_name_hebrew or ''}) - {verse.ref if verse else '?'}")
            if dn.context_type:
                click.echo(f"    Context: {dn.context_type.value}")
            if dn.theological_note:
                click.echo(f"    Note: {dn.theological_note[:100]}")
    finally:
        db.close()


@click.command("query-genealogy")
@click.option("--person", "-p", help="Person name")
@click.option("--father", "-f", help="Father's name")
@click.option("--generation", "-g", type=int, help="Generation from Adam")
@click.option("--limit", "-l", type=int, default=20, help="Maximum results")
def query_genealogy(person: str, father: str, generation: int, limit: int):
    """Query genealogical data."""
    from src.db.models.narrative import Genealogy
    from src.db.models.names import TorahName

    db = SessionLocal()
    try:
        query = db.query(Genealogy)

        if person:
            person_name = db.query(TorahName).filter(TorahName.name_canonical.ilike(f"%{person}%")).first()
            if person_name:
                query = query.filter(Genealogy.person_id == person_name.id)

        if father:
            father_name = db.query(TorahName).filter(TorahName.name_canonical.ilike(f"%{father}%")).first()
            if father_name:
                query = query.filter(Genealogy.father_id == father_name.id)

        if generation is not None:
            query = query.filter(Genealogy.generation_from_adam == generation)

        results = query.limit(limit).all()

        if not results:
            click.echo("No genealogy entries found")
            return

        click.echo(f"\nFound {len(results)} entries:\n")
        for gen in results:
            person_name = db.query(TorahName).get(gen.person_id)
            father_name = db.query(TorahName).get(gen.father_id) if gen.father_id else None
            mother_name = db.query(TorahName).get(gen.mother_id) if gen.mother_id else None

            click.echo(f"  {person_name.name_canonical if person_name else '?'}")
            if father_name or gen.father_name:
                click.echo(f"    Father: {father_name.name_canonical if father_name else gen.father_name or '?'}")
            if mother_name or gen.mother_name:
                click.echo(f"    Mother: {mother_name.name_canonical if mother_name else gen.mother_name or '?'}")
            if gen.lifespan_years:
                click.echo(f"    Lifespan: {gen.lifespan_years} years")
            if gen.generation_from_adam:
                click.echo(f"    Generation from Adam: {gen.generation_from_adam}")
            click.echo()
    finally:
        db.close()


@click.command("query-roots")
@click.option("--root", "-r", help="Hebrew root letters")
@click.option("--meaning", "-m", help="Root meaning (partial match)")
@click.option("--limit", "-l", type=int, default=20, help="Maximum results")
def query_roots(root: str, meaning: str, limit: int):
    """Query Hebrew roots."""
    from src.db.models.linguistic import HebrewRoot

    db = SessionLocal()
    try:
        query = db.query(HebrewRoot)

        if root:
            query = query.filter(HebrewRoot.root_letters.ilike(f"%{root}%"))

        if meaning:
            query = query.filter(HebrewRoot.basic_meaning.ilike(f"%{meaning}%"))

        query = query.order_by(HebrewRoot.occurrence_count.desc())
        results = query.limit(limit).all()

        if not results:
            click.echo("No roots found")
            return

        click.echo(f"\nFound {len(results)} roots:\n")
        for r in results:
            click.echo(f"  {r.root_letters} ({r.root_transliteration})")
            click.echo(f"    Meaning: {r.basic_meaning}")
            click.echo(f"    Occurrences: {r.occurrence_count}")
    finally:
        db.close()


@click.command("query-sentiment")
@click.option("--emotion", "-e", help="Primary emotion")
@click.option("--divine", "-d", help="Divine sentiment")
@click.option("--book", "-b", help="Book name")
@click.option("--limit", "-l", type=int, default=20, help="Maximum results")
def query_sentiment(emotion: str, divine: str, book: str, limit: int):
    """Query verse sentiment data."""
    from src.db.models.enrichment import VerseSentiment
    from src.db.models.torah import TorahVerse, TorahChapter, TorahBook

    db = SessionLocal()
    try:
        query = db.query(VerseSentiment).join(TorahVerse)

        if emotion:
            query = query.filter(VerseSentiment.primary_emotion == emotion)

        if divine:
            query = query.filter(VerseSentiment.divine_sentiment == divine)

        if book:
            book_obj = db.query(TorahBook).filter(TorahBook.name.ilike(f"%{book}%")).first()
            if book_obj:
                query = query.join(TorahChapter).filter(TorahChapter.book_id == book_obj.id)

        results = query.limit(limit).all()

        if not results:
            click.echo("No sentiment data found")
            return

        click.echo(f"\nFound {len(results)} entries:\n")
        for sent in results:
            verse = db.query(TorahVerse).get(sent.verse_id)
            click.echo(f"  {verse.ref if verse else '?'}")
            click.echo(f"    Emotion: {sent.primary_emotion.value if sent.primary_emotion else '?'}")
            click.echo(f"    Polarity: {sent.sentiment_polarity}, Tension: {sent.tension_level}")
            if sent.divine_sentiment:
                click.echo(f"    Divine: {sent.divine_sentiment.value}")
    finally:
        db.close()


# List of all enrichment commands
enrichment_commands = [
    # Extraction commands
    extract_relationships,
    extract_theological,
    extract_narrative,
    extract_linguistic,
    extract_enrichment,
    extract_all,
    # Status command
    enrichment_status,
    # Query commands
    query_relationships,
    query_events,
    query_divine_names,
    query_genealogy,
    query_roots,
    query_sentiment,
]
