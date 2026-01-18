"""Base extraction service for LLM-based data extraction from Torah verses."""
import json
import re
import subprocess
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict, Any, TypeVar, Generic
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.db.models.torah import TorahVerse, TorahChapter
from src.config.settings import settings

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ExtractionContext:
    """Context for a verse being extracted."""
    verse_id: int
    verse_ref: str
    text_hebrew: str
    text_english: str
    context_before: List[str]
    context_after: List[str]


@dataclass
class BulkExtractionResult:
    """Result of bulk extraction."""
    processed: int
    items_found: int
    errors: int
    error_details: List[str]


class BaseExtractionService(ABC, Generic[T]):
    """Base class for extraction services using Claude CLI."""

    # Subclasses should override these
    EXTRACTION_NAME = "base"
    PROCESSED_FIELD = "processed"  # Field to mark on verse when processed

    def __init__(self, db: Session, model: str = None, max_workers: int = 5):
        self.db = db
        self.model = model or settings.claude_model
        self.max_workers = max_workers
        self.timeout = settings.claude_timeout

    @abstractmethod
    def build_prompt(self, verses_data: List[Dict]) -> str:
        """Build the extraction prompt for Claude.

        Args:
            verses_data: List of dicts with keys: ref, text_hebrew, text_english

        Returns:
            Prompt string for Claude CLI
        """
        pass

    @abstractmethod
    def parse_response(self, response_text: str, verses_data: List[Dict]) -> Dict[str, List[T]]:
        """Parse Claude's response into structured data.

        Args:
            response_text: Raw text response from Claude
            verses_data: Original verse data for reference

        Returns:
            Dict mapping verse_ref to list of extracted items
        """
        pass

    @abstractmethod
    def save_extraction(self, verse: TorahVerse, items: List[T]) -> int:
        """Save extracted items to database.

        Args:
            verse: The verse the items were extracted from
            items: List of extracted items

        Returns:
            Number of items saved
        """
        pass

    def get_pending_verses(self, limit: Optional[int] = None) -> List[TorahVerse]:
        """Get verses that haven't been processed yet for this extraction type.

        Override this method if you need custom filtering logic.
        """
        query = (
            self.db.query(TorahVerse)
            .filter(TorahVerse.processed == True)  # Only process verses with names extracted
            .order_by(TorahVerse.id)
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    def extract_bulk(
        self,
        limit: Optional[int] = None,
        batch_size: int = 50,
        parallel: bool = False,
        workers: int = 1
    ) -> BulkExtractionResult:
        """Extract data from verses in bulk.

        Args:
            limit: Maximum verses to process
            batch_size: Verses per Claude request
            parallel: Use parallel requests
            workers: Number of parallel workers (1-10)

        Returns:
            BulkExtractionResult with statistics
        """
        if parallel:
            return self._extract_bulk_parallel(limit, batch_size, min(workers, 10))
        return self._extract_bulk_sequential(limit, batch_size)

    def _extract_bulk_sequential(
        self,
        limit: Optional[int],
        batch_size: int
    ) -> BulkExtractionResult:
        """Sequential bulk extraction."""
        stats = BulkExtractionResult(processed=0, items_found=0, errors=0, error_details=[])

        verses = self.get_pending_verses(limit)
        if not verses:
            logger.info(f"{self.EXTRACTION_NAME}: No pending verses found")
            return stats

        # Process in batches
        for i in range(0, len(verses), batch_size):
            batch = verses[i:i + batch_size]
            verses_data = [
                {
                    "ref": v.ref,
                    "text_hebrew": v.text_hebrew,
                    "text_english": v.text_english,
                }
                for v in batch
            ]

            logger.info(f"{self.EXTRACTION_NAME}: Processing batch of {len(verses_data)} verses...")

            try:
                # Call Claude
                response_text = self._call_claude(verses_data)

                # Parse response
                results = self.parse_response(response_text, verses_data)

                # Save each verse immediately
                for verse in batch:
                    items = results.get(verse.ref, [])
                    if items is not None:
                        saved = self.save_extraction(verse, items)
                        stats.items_found += saved
                    else:
                        stats.errors += 1
                        stats.error_details.append(f"{verse.ref}: extraction failed")

                    stats.processed += 1
                    self.db.commit()
                    logger.info(f"{self.EXTRACTION_NAME}: Saved {verse.ref}: {len(items) if items else 0} items")

            except Exception as e:
                logger.error(f"{self.EXTRACTION_NAME}: Batch error: {e}")
                stats.errors += len(batch)
                stats.error_details.append(f"Batch error: {str(e)}")
                self.db.rollback()

        return stats

    def _extract_bulk_parallel(
        self,
        limit: Optional[int],
        batch_size: int,
        workers: int
    ) -> BulkExtractionResult:
        """Parallel bulk extraction."""
        stats = BulkExtractionResult(processed=0, items_found=0, errors=0, error_details=[])

        verses = self.get_pending_verses(limit)
        if not verses:
            logger.info(f"{self.EXTRACTION_NAME}: No pending verses found")
            return stats

        # Split into batches
        batches = []
        for i in range(0, len(verses), batch_size):
            batches.append(verses[i:i + batch_size])

        logger.info(f"{self.EXTRACTION_NAME}: Processing {len(batches)} batches with {workers} workers")

        def process_batch(batch_verses):
            verses_data = [
                {"ref": v.ref, "text_hebrew": v.text_hebrew, "text_english": v.text_english}
                for v in batch_verses
            ]
            response_text = self._call_claude(verses_data)
            results = self.parse_response(response_text, verses_data)
            return batch_verses, results

        # Run batches in parallel
        batch_results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(process_batch, batch): batch for batch in batches}
            for future in as_completed(futures):
                try:
                    batch_verses, results = future.result()
                    batch_results.append((batch_verses, results))
                    logger.info(f"{self.EXTRACTION_NAME}: Completed batch of {len(batch_verses)} verses")
                except Exception as e:
                    batch = futures[future]
                    stats.errors += len(batch)
                    stats.error_details.append(f"Batch error: {str(e)}")
                    logger.error(f"{self.EXTRACTION_NAME}: Batch failed: {e}")

        # Save all results
        for batch_verses, results in batch_results:
            for verse in batch_verses:
                items = results.get(verse.ref, [])
                if items is not None:
                    try:
                        saved = self.save_extraction(verse, items)
                        stats.items_found += saved
                    except Exception as e:
                        stats.errors += 1
                        stats.error_details.append(f"{verse.ref}: save error - {str(e)}")
                        self.db.rollback()
                        continue
                else:
                    stats.errors += 1

                stats.processed += 1
                self.db.commit()

        return stats

    def _call_claude(self, verses_data: List[Dict]) -> str:
        """Call Claude CLI with the extraction prompt."""
        prompt = self.build_prompt(verses_data)

        result = subprocess.run(
            [
                "claude",
                "-p",
                prompt,
                "--model",
                self.model,
                "--tools",
                "",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI error: {result.stderr}")

        response_data = json.loads(result.stdout)
        response_text = response_data.get("result", "")

        if not response_text:
            content = response_data.get("content", [])
            if content and isinstance(content, list):
                response_text = content[0].get("text", "")

        return response_text

    def parse_json_response(self, response_text: str) -> Any:
        """Helper to extract JSON from Claude's response."""
        # Look for JSON block in response
        json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_text.strip()

        return json.loads(json_str)

    def get_context_before(self, verse: TorahVerse, count: int = 3) -> List[str]:
        """Get N previous verses as context."""
        from sqlalchemy import and_

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

        return [f"{v.ref}: {v.text_english[:200]}" for v in same_chapter]

    def get_context_after(self, verse: TorahVerse, count: int = 3) -> List[str]:
        """Get N following verses as context."""
        from sqlalchemy import and_

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

        return [f"{v.ref}: {v.text_english[:200]}" for v in same_chapter]

    def get_extraction_status(self) -> Dict[str, Any]:
        """Get status of this extraction type."""
        total_verses = self.db.query(TorahVerse).filter(TorahVerse.processed == True).count()
        return {
            "extraction_type": self.EXTRACTION_NAME,
            "total_eligible_verses": total_verses,
        }
