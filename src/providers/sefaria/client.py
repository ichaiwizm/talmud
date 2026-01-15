import re
import asyncio
import logging
from dataclasses import dataclass
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

from src.config.settings import settings

logger = logging.getLogger(__name__)

SEFARIA_BASE_URL = "https://www.sefaria.org/api"
TORAH_BOOKS = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
TORAH_BOOKS_HEBREW = ["בראשית", "שמות", "ויקרא", "במדבר", "דברים"]


@dataclass
class BookShape:
    """Structure of a book (chapters and verses)."""

    name: str
    hebrew_name: str
    total_chapters: int
    verses_per_chapter: List[int]


@dataclass
class VerseData:
    """Data for a single verse."""

    ref: str
    he_ref: str
    text_hebrew: str
    text_english: str
    chapter: int
    verse: int


class SefariaClient:
    """Client for Sefaria API with parallel fetching."""

    def __init__(self, timeout: float = None, max_workers: int = 10):
        self.timeout = timeout or settings.sefaria_timeout
        self.max_workers = max_workers
        self.client = httpx.Client(
            base_url=SEFARIA_BASE_URL,
            timeout=self.timeout,
            headers={"User-Agent": "TalmudProject/1.0"},
        )

    def get_book_shape(self, book: str) -> BookShape:
        """Get the structure of a book (number of chapters/verses)."""
        response = self.client.get(f"/shape/{book}")
        response.raise_for_status()
        data = response.json()

        # API returns a list, take the first element
        if isinstance(data, list):
            data = data[0]

        book_index = TORAH_BOOKS.index(book)
        return BookShape(
            name=book,
            hebrew_name=data.get("heTitle", TORAH_BOOKS_HEBREW[book_index]),
            total_chapters=data["length"],
            verses_per_chapter=data["chapters"],
        )

    def get_chapter(self, book: str, chapter: int) -> List[VerseData]:
        """Get all verses of a chapter."""
        ref = f"{book}.{chapter}"

        # Get Hebrew text
        response = self.client.get(f"/v3/texts/{ref}")
        response.raise_for_status()
        data = response.json()

        hebrew_texts = []
        english_texts = []
        he_ref_base = data.get("heRef", "")

        # Extract Hebrew text (first source version)
        for version in data.get("versions", []):
            if version.get("language") == "he" and version.get("isSource"):
                hebrew_texts = version.get("text", [])
                break

        # Extract English text
        for version in data.get("versions", []):
            if version.get("language") == "en":
                english_texts = version.get("text", [])
                break

        # If no English found, try with specific version
        if not english_texts:
            try:
                response_en = self.client.get(
                    f"/v3/texts/{ref}",
                    params={"version": "english"},
                )
                if response_en.status_code == 200:
                    data_en = response_en.json()
                    for version in data_en.get("versions", []):
                        if version.get("language") == "en":
                            english_texts = version.get("text", [])
                            break
            except Exception as e:
                logger.warning(f"Failed to get English version for {ref}: {e}")

        # Build verses
        verses = []
        max_verses = max(len(hebrew_texts), len(english_texts), 1)

        for i in range(max_verses):
            he_text = hebrew_texts[i] if i < len(hebrew_texts) else ""
            en_text = english_texts[i] if i < len(english_texts) else ""

            he_text_clean = self._clean_html(he_text) if he_text else ""
            en_text_clean = self._clean_html(en_text) if en_text else ""

            verse_num = i + 1
            verses.append(
                VerseData(
                    ref=f"{book} {chapter}:{verse_num}",
                    he_ref=f"{he_ref_base}:{self._to_hebrew_num(verse_num)}",
                    text_hebrew=he_text_clean,
                    text_english=en_text_clean,
                    chapter=chapter,
                    verse=verse_num,
                )
            )

        return verses

    def get_all_chapters_parallel(self, book: str, total_chapters: int) -> dict:
        """Fetch all chapters in parallel. Returns dict {chapter_num: [verses]}."""
        results = {}

        def fetch_chapter(chapter_num):
            # Create a new client for each thread (httpx.Client is not thread-safe)
            with httpx.Client(
                base_url=SEFARIA_BASE_URL,
                timeout=self.timeout,
                headers={"User-Agent": "TalmudProject/1.0"},
            ) as client:
                try:
                    return chapter_num, self._fetch_chapter_with_client(client, book, chapter_num)
                except Exception as e:
                    logger.error(f"Error fetching {book} chapter {chapter_num}: {e}")
                    return chapter_num, []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(fetch_chapter, ch): ch
                for ch in range(1, total_chapters + 1)
            }

            for future in as_completed(futures):
                chapter_num, verses = future.result()
                results[chapter_num] = verses
                logger.info(f"Fetched {book} chapter {chapter_num}: {len(verses)} verses")

        return results

    def _fetch_chapter_with_client(self, client: httpx.Client, book: str, chapter: int) -> List[VerseData]:
        """Fetch a chapter using provided client."""
        ref = f"{book}.{chapter}"

        response = client.get(f"/v3/texts/{ref}")
        response.raise_for_status()
        data = response.json()

        hebrew_texts = []
        english_texts = []
        he_ref_base = data.get("heRef", "")

        for version in data.get("versions", []):
            if version.get("language") == "he" and version.get("isSource"):
                hebrew_texts = version.get("text", [])
                break

        for version in data.get("versions", []):
            if version.get("language") == "en":
                english_texts = version.get("text", [])
                break

        if not english_texts:
            try:
                response_en = client.get(f"/v3/texts/{ref}", params={"version": "english"})
                if response_en.status_code == 200:
                    data_en = response_en.json()
                    for version in data_en.get("versions", []):
                        if version.get("language") == "en":
                            english_texts = version.get("text", [])
                            break
            except Exception:
                pass

        verses = []
        max_verses = max(len(hebrew_texts), len(english_texts), 1)

        for i in range(max_verses):
            he_text = hebrew_texts[i] if i < len(hebrew_texts) else ""
            en_text = english_texts[i] if i < len(english_texts) else ""

            verses.append(
                VerseData(
                    ref=f"{book} {chapter}:{i + 1}",
                    he_ref=f"{he_ref_base}:{self._to_hebrew_num(i + 1)}",
                    text_hebrew=self._clean_html(he_text) if he_text else "",
                    text_english=self._clean_html(en_text) if en_text else "",
                    chapter=chapter,
                    verse=i + 1,
                )
            )

        return verses

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        if not text:
            return ""
        return re.sub(r"<[^>]+>", "", text)

    def _to_hebrew_num(self, num: int) -> str:
        """Convert number to Hebrew numeral (simplified)."""
        hebrew_digits = {
            1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה",
            6: "ו", 7: "ז", 8: "ח", 9: "ט", 10: "י",
            20: "כ", 30: "ל", 40: "מ", 50: "נ",
        }
        if num <= 10:
            return hebrew_digits.get(num, str(num))
        if num < 20:
            return f"י{hebrew_digits.get(num - 10, '')}"
        tens = (num // 10) * 10
        ones = num % 10
        result = hebrew_digits.get(tens, "")
        if ones:
            result += hebrew_digits.get(ones, "")
        return result

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
