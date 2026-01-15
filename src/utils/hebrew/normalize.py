"""Hebrew text normalization utilities."""

import re
import unicodedata
from typing import List, Tuple

from .constants import HEBREW_LETTERS, FINAL_LETTERS_MAP


def remove_nikud(text: str) -> str:
    """Remove Hebrew vowel points (nikud) and cantillation marks.

    Preserves only Hebrew letters, spaces, and basic punctuation.
    """
    result = []
    for char in text:
        category = unicodedata.category(char)
        # Keep letters (Lo = other letter, includes Hebrew)
        # Keep spaces and tabs
        # Keep Hebrew punctuation (maqaf ־, sof pasuk ׃)
        if category.startswith("L") or char in " \t\n" or char in "־׃":
            result.append(char)
        # Skip marks (Mn = non-spacing mark, includes nikud/cantillation)
    return "".join(result)


def normalize_final_letters(text: str) -> str:
    """Convert final letters (sofit) to their regular forms.

    ך → כ, ם → מ, ן → נ, ף → פ, ץ → צ
    """
    return "".join(FINAL_LETTERS_MAP.get(c, c) for c in text)


def extract_words(verse_text: str) -> List[Tuple[str, str]]:
    """Extract words from a Hebrew verse.

    Args:
        verse_text: Hebrew text (may include nikud)

    Returns:
        List of (original_word, normalized_word) tuples.
        - original_word: as it appears in text (with nikud)
        - normalized_word: letters only, no nikud
    """
    # Split on spaces and Hebrew punctuation (maqaf ־, sof pasuk ׃)
    raw_words = re.split(r"[\s־׃]+", verse_text)

    result = []
    for word in raw_words:
        if not word:
            continue

        # Check if word contains any Hebrew letters
        if not any(c in HEBREW_LETTERS for c in remove_nikud(word)):
            continue

        # Normalize: remove nikud, keep only Hebrew letters
        clean = remove_nikud(word)
        normalized = "".join(c for c in clean if c in HEBREW_LETTERS)

        if normalized:
            result.append((word, normalized))

    return result
