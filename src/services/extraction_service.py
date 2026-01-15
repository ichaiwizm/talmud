import json
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.db.models.torah import TorahVerse, TorahChapter
from src.db.models.names import TorahName, TorahNameOccurrence, NameType
from src.providers.claude.client import ClaudeClient, ExtractedName, ExtractionResult

logger = logging.getLogger(__name__)


@dataclass
class VerseContext:
    """Verse with its context for extraction."""
    verse_id: int
    verse_ref: str
    text_hebrew: str
    text_english: str
    context_before: List[str]
    context_after: List[str]


class NameExtractionService:
    """Service for extracting names from Torah verses."""

    def __init__(self, db: Session, model: str = None, max_workers: int = 5):
        self.db = db
        self.model = model
        self.max_workers = max_workers

    def extract_all_pending(self, limit: Optional[int] = None, parallel: bool = False) -> dict:
        """Extract names from all unprocessed verses."""
        if parallel:
            return self._extract_parallel(limit)
        return self._extract_sequential(limit)

    def _extract_sequential(self, limit: Optional[int] = None) -> dict:
        """Sequential extraction (original method)."""
        query = (
            self.db.query(TorahVerse)
            .filter(TorahVerse.processed == False)
            .order_by(TorahVerse.id)
        )

        if limit:
            query = query.limit(limit)

        verses = query.all()
        stats = {"processed": 0, "names_found": 0, "errors": 0}
        claude = ClaudeClient(model=self.model)

        for verse in verses:
            try:
                result = self._extract_single_verse(verse, claude)
                stats["processed"] += 1
                stats["names_found"] += result["names_count"]
                self.db.commit()
                logger.info(f"Processed {verse.ref}: {result['names_count']} names")

            except Exception as e:
                stats["errors"] += 1
                verse.extraction_error = str(e)
                self.db.commit()
                logger.error(f"Error processing {verse.ref}: {e}")

        return stats

    def _extract_parallel(self, limit: Optional[int] = None, batch_size: int = 50) -> dict:
        """Parallel extraction using ThreadPoolExecutor with batch commits."""
        stats = {"processed": 0, "names_found": 0, "errors": 0}

        while True:
            # Get next batch of verses to process
            query = (
                self.db.query(TorahVerse)
                .filter(TorahVerse.processed == False)
                .order_by(TorahVerse.id)
                .limit(batch_size)
            )

            verses = query.all()
            if not verses:
                break

            # Check if we've hit the limit
            if limit and stats["processed"] >= limit:
                break

            # Adjust batch if we're near the limit
            if limit:
                remaining = limit - stats["processed"]
                verses = verses[:remaining]

            # Prepare verse contexts (with DB access)
            verse_contexts = []
            for verse in verses:
                ctx = VerseContext(
                    verse_id=verse.id,
                    verse_ref=verse.ref,
                    text_hebrew=verse.text_hebrew,
                    text_english=verse.text_english,
                    context_before=self._get_context_before(verse, count=3),
                    context_after=self._get_context_after(verse, count=3),
                )
                verse_contexts.append(ctx)

            # Run extractions in parallel (no DB access needed)
            logger.info(f"Batch: extracting {len(verse_contexts)} verses with {self.max_workers} workers")
            batch_results: List[Tuple[VerseContext, ExtractionResult]] = []

            def extract_one(ctx: VerseContext) -> Tuple[VerseContext, ExtractionResult]:
                claude = ClaudeClient(model=self.model)
                result = claude.extract_names(
                    verse_ref=ctx.verse_ref,
                    text_hebrew=ctx.text_hebrew,
                    text_english=ctx.text_english,
                    context_before=ctx.context_before,
                    context_after=ctx.context_after,
                )
                return ctx, result

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(extract_one, ctx): ctx for ctx in verse_contexts}
                for future in as_completed(futures):
                    ctx, result = future.result()
                    batch_results.append((ctx, result))
                    status = "OK" if result.success else "ERR"
                    logger.info(f"Extracted {ctx.verse_ref}: {status} - {len(result.names)} names")

            # Save batch results and commit
            for ctx, result in batch_results:
                verse = self.db.get(TorahVerse, ctx.verse_id)
                if not verse:
                    continue

                if result.success:
                    for extracted in result.names:
                        self._save_name_occurrence(verse, extracted, ctx.context_before, ctx.context_after)
                    stats["names_found"] += len(result.names)
                    verse.extraction_error = None
                else:
                    verse.extraction_error = result.error
                    stats["errors"] += 1

                verse.processed = True
                verse.processed_at = datetime.utcnow()
                stats["processed"] += 1

            # Commit after each batch
            self.db.commit()
            logger.info(f"Committed batch. Total: {stats['processed']} processed, {stats['names_found']} names, {stats['errors']} errors")

            if limit and stats["processed"] >= limit:
                break

        return stats

    def extract_bulk(self, limit: Optional[int] = None, batch_size: int = 50, parallel: bool = False, workers: int = 1) -> dict:
        """Bulk extraction: send multiple verses per request, commit after each verse.

        Args:
            limit: Maximum verses to process
            batch_size: Verses per Claude request
            parallel: Use parallel requests (max 10 workers)
            workers: Number of parallel workers (1-10)
        """
        if parallel:
            return self._extract_bulk_parallel(limit, batch_size, min(workers, 10))
        return self._extract_bulk_sequential(limit, batch_size)

    def _extract_bulk_sequential(self, limit: Optional[int], batch_size: int) -> dict:
        """Sequential bulk extraction."""
        stats = {"processed": 0, "names_found": 0, "errors": 0}
        claude = ClaudeClient(model=self.model)

        while True:
            # Get next batch of verses
            query = (
                self.db.query(TorahVerse)
                .filter(TorahVerse.processed == False)
                .order_by(TorahVerse.id)
                .limit(batch_size)
            )

            verses = query.all()
            if not verses:
                break

            # Check limit
            if limit and stats["processed"] >= limit:
                break

            # Adjust batch if near limit
            if limit:
                remaining = limit - stats["processed"]
                verses = verses[:remaining]

            # Prepare verses for bulk request
            verses_data = [
                {
                    "ref": v.ref,
                    "text_hebrew": v.text_hebrew,
                    "text_english": v.text_english,
                }
                for v in verses
            ]

            logger.info(f"Bulk extracting {len(verses_data)} verses...")

            # Call Claude with all verses at once
            results = claude.extract_names_bulk(verses_data)

            # Save each verse IMMEDIATELY with commit
            for verse in verses:
                names = results.get(verse.ref, [])

                if names is not None:  # Success (even if empty)
                    for extracted in names:
                        self._save_name_occurrence(verse, extracted, [], [])
                    stats["names_found"] += len(names)
                    verse.extraction_error = None
                else:
                    verse.extraction_error = "Bulk extraction failed"
                    stats["errors"] += 1

                verse.processed = True
                verse.processed_at = datetime.utcnow()
                stats["processed"] += 1

                # Commit IMMEDIATELY after each verse
                self.db.commit()
                logger.info(f"Saved {verse.ref}: {len(names)} names")

            logger.info(f"Batch complete. Total: {stats['processed']} processed, {stats['names_found']} names")

            if limit and stats["processed"] >= limit:
                break

        return stats

    def _extract_bulk_parallel(self, limit: Optional[int], batch_size: int, workers: int) -> dict:
        """Parallel bulk extraction: multiple Claude requests in parallel."""
        stats = {"processed": 0, "names_found": 0, "errors": 0}

        while True:
            # Get enough verses for all workers
            total_batch = batch_size * workers
            query = (
                self.db.query(TorahVerse)
                .filter(TorahVerse.processed == False)
                .order_by(TorahVerse.id)
                .limit(total_batch)
            )

            all_verses = query.all()
            if not all_verses:
                break

            # Check limit
            if limit and stats["processed"] >= limit:
                break

            # Adjust if near limit
            if limit:
                remaining = limit - stats["processed"]
                all_verses = all_verses[:remaining]

            # Split into batches for each worker
            batches = []
            for i in range(0, len(all_verses), batch_size):
                batch_verses = all_verses[i:i + batch_size]
                batches.append(batch_verses)

            logger.info(f"Parallel bulk: {len(batches)} batches x {batch_size} verses with {workers} workers")

            # Prepare all batch data
            def process_batch(verses):
                claude = ClaudeClient(model=self.model)
                verses_data = [
                    {"ref": v.ref, "text_hebrew": v.text_hebrew, "text_english": v.text_english}
                    for v in verses
                ]
                results = claude.extract_names_bulk(verses_data)
                return verses, results

            # Run batches in parallel
            batch_results = []
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(process_batch, batch): batch for batch in batches}
                for future in as_completed(futures):
                    verses, results = future.result()
                    batch_results.append((verses, results))
                    logger.info(f"Completed batch of {len(verses)} verses")

            # Save all results with immediate commits
            for verses, results in batch_results:
                for verse in verses:
                    names = results.get(verse.ref, [])

                    if names is not None:
                        for extracted in names:
                            self._save_name_occurrence(verse, extracted, [], [])
                        stats["names_found"] += len(names)
                        verse.extraction_error = None
                    else:
                        verse.extraction_error = "Bulk extraction failed"
                        stats["errors"] += 1

                    verse.processed = True
                    verse.processed_at = datetime.utcnow()
                    stats["processed"] += 1

                    self.db.commit()
                    logger.info(f"Saved {verse.ref}: {len(names)} names")

            logger.info(f"Parallel batch complete. Total: {stats['processed']} processed, {stats['names_found']} names")

            if limit and stats["processed"] >= limit:
                break

        return stats

    def extract_verse(self, verse: TorahVerse) -> dict:
        """Extract names from a specific verse."""
        claude = ClaudeClient(model=self.model)
        return self._extract_single_verse(verse, claude)

    def _extract_single_verse(self, verse: TorahVerse, claude: ClaudeClient) -> dict:
        """Internal method to extract from a single verse."""
        context_before = self._get_context_before(verse, count=3)
        context_after = self._get_context_after(verse, count=3)

        result = claude.extract_names(
            verse_ref=verse.ref,
            text_hebrew=verse.text_hebrew,
            text_english=verse.text_english,
            context_before=context_before,
            context_after=context_after,
        )

        if not result.success:
            verse.extraction_error = result.error
            verse.processed = True
            verse.processed_at = datetime.utcnow()
            return {"names_count": 0, "error": result.error}

        names_count = 0
        for extracted in result.names:
            self._save_name_occurrence(verse, extracted, context_before, context_after)
            names_count += 1

        verse.processed = True
        verse.processed_at = datetime.utcnow()
        verse.extraction_error = None

        return {"names_count": names_count}

    def _get_context_before(self, verse: TorahVerse, count: int) -> List[str]:
        """Get N previous verses."""
        same_chapter = (
            self.db.query(TorahVerse)
            .filter(
                and_(
                    TorahVerse.chapter_id == verse.chapter_id,
                    TorahVerse.number < verse.number,
                    TorahVerse.number >= verse.number - count,
                )
            )
            .order_by(TorahVerse.number)
            .all()
        )

        context = [f"{v.ref}: {v.text_english[:200]}" for v in same_chapter]

        if len(context) < count:
            remaining = count - len(context)
            prev_chapter = (
                self.db.query(TorahChapter)
                .filter(
                    and_(
                        TorahChapter.book_id == verse.chapter.book_id,
                        TorahChapter.number == verse.chapter.number - 1,
                    )
                )
                .first()
            )

            if prev_chapter:
                prev_verses = (
                    self.db.query(TorahVerse)
                    .filter(TorahVerse.chapter_id == prev_chapter.id)
                    .order_by(TorahVerse.number.desc())
                    .limit(remaining)
                    .all()
                )

                prev_context = [f"{v.ref}: {v.text_english[:200]}" for v in reversed(prev_verses)]
                context = prev_context + context

        return context

    def _get_context_after(self, verse: TorahVerse, count: int) -> List[str]:
        """Get N following verses."""
        same_chapter = (
            self.db.query(TorahVerse)
            .filter(
                and_(
                    TorahVerse.chapter_id == verse.chapter_id,
                    TorahVerse.number > verse.number,
                    TorahVerse.number <= verse.number + count,
                )
            )
            .order_by(TorahVerse.number)
            .all()
        )

        context = [f"{v.ref}: {v.text_english[:200]}" for v in same_chapter]

        if len(context) < count:
            remaining = count - len(context)
            next_chapter = (
                self.db.query(TorahChapter)
                .filter(
                    and_(
                        TorahChapter.book_id == verse.chapter.book_id,
                        TorahChapter.number == verse.chapter.number + 1,
                    )
                )
                .first()
            )

            if next_chapter:
                next_verses = (
                    self.db.query(TorahVerse)
                    .filter(TorahVerse.chapter_id == next_chapter.id)
                    .order_by(TorahVerse.number)
                    .limit(remaining)
                    .all()
                )

                next_context = [f"{v.ref}: {v.text_english[:200]}" for v in next_verses]
                context = context + next_context

        return context

    def _save_name_occurrence(
        self,
        verse: TorahVerse,
        extracted: ExtractedName,
        context_before: List[str],
        context_after: List[str],
    ):
        """Save an extracted name and its occurrence."""
        name = (
            self.db.query(TorahName)
            .filter_by(name_canonical=extracted.name)
            .first()
        )

        if not name:
            try:
                name_type = NameType(extracted.name_type)
            except ValueError:
                name_type = NameType.UNKNOWN

            name = TorahName(
                name_canonical=extracted.name,
                name_hebrew=extracted.name_hebrew,
                name_type=name_type,
                first_mention_ref=verse.ref,
            )
            self.db.add(name)
            self.db.flush()

        occurrence = TorahNameOccurrence(
            verse_id=verse.id,
            name_id=name.id,
            surface_form=extracted.surface_form,
            surface_form_hebrew=extracted.surface_form_hebrew,
            context_before=json.dumps(context_before),
            context_after=json.dumps(context_after),
            confidence=extracted.confidence,
            extraction_notes=extracted.notes,
        )
        self.db.add(occurrence)

    def get_extraction_status(self) -> dict:
        """Return extraction status."""
        total_verses = self.db.query(TorahVerse).count()
        processed = (
            self.db.query(TorahVerse).filter(TorahVerse.processed == True).count()
        )
        with_errors = (
            self.db.query(TorahVerse)
            .filter(TorahVerse.extraction_error.isnot(None))
            .count()
        )
        unique_names = self.db.query(TorahName).count()
        total_occurrences = self.db.query(TorahNameOccurrence).count()

        return {
            "total_verses": total_verses,
            "processed": processed,
            "pending": total_verses - processed,
            "with_errors": with_errors,
            "unique_names": unique_names,
            "total_occurrences": total_occurrences,
            "progress_percent": (
                round(processed / total_verses * 100, 2) if total_verses > 0 else 0
            ),
        }

    def retry_errors(self, limit: Optional[int] = None) -> dict:
        """Retry extraction on verses with errors."""
        query = self.db.query(TorahVerse).filter(
            and_(
                TorahVerse.processed == True,
                TorahVerse.extraction_error.isnot(None),
            )
        )

        if limit:
            query = query.limit(limit)

        verses = query.all()

        for verse in verses:
            verse.processed = False
            verse.extraction_error = None

        self.db.commit()

        return self.extract_all_pending(limit=limit)
