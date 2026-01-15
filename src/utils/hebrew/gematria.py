"""Gematria calculation functions."""

from enum import Enum
from typing import Dict

from .constants import (
    GEMATRIA_STANDARD,
    GEMATRIA_KATAN,
    GEMATRIA_ORDINAL,
    ATBASH_MAP,
)
from .normalize import remove_nikud


class GematriaMethod(str, Enum):
    """Available gematria calculation methods."""

    STANDARD = "standard"  # Mispar Gadol
    KATAN = "katan"  # Mispar Katan (small)
    ORDINAL = "ordinal"  # Position in alphabet (1-22)
    ATBASH = "atbash"  # Atbash cipher then standard


def calculate_standard(word: str) -> int:
    """Calculate standard gematria (Mispar Gadol).

    א=1, ב=2... י=10, כ=20... ק=100, ר=200, ש=300, ת=400
    """
    return sum(GEMATRIA_STANDARD.get(c, 0) for c in word)


def calculate_katan(word: str) -> int:
    """Calculate small gematria (Mispar Katan).

    Reduces values to 1-9 cycle (ignores tens and hundreds).
    """
    return sum(GEMATRIA_KATAN.get(c, 0) for c in word)


def calculate_ordinal(word: str) -> int:
    """Calculate ordinal gematria.

    Each letter's position in the alphabet (1-22).
    """
    return sum(GEMATRIA_ORDINAL.get(c, 0) for c in word)


def calculate_atbash(word: str) -> int:
    """Calculate Atbash gematria.

    First applies Atbash cipher (א↔ת, ב↔ש, etc.),
    then calculates standard gematria on the result.
    """
    atbash_word = "".join(ATBASH_MAP.get(c, c) for c in word)
    return calculate_standard(atbash_word)


def calculate_all(text: str) -> Dict[str, int]:
    """Calculate all gematria methods for a text.

    Automatically normalizes the text (removes nikud).

    Args:
        text: Hebrew text (may include nikud/vowels)

    Returns:
        Dictionary with all gematria values:
        {"standard": ..., "katan": ..., "ordinal": ..., "atbash": ...}
    """
    # Normalize: remove nikud, keep only letters
    clean = remove_nikud(text)
    letters_only = "".join(c for c in clean if c.strip())

    return {
        "standard": calculate_standard(letters_only),
        "katan": calculate_katan(letters_only),
        "ordinal": calculate_ordinal(letters_only),
        "atbash": calculate_atbash(letters_only),
    }


def calculate(text: str, method: GematriaMethod = GematriaMethod.STANDARD) -> int:
    """Calculate gematria for text using specified method.

    Args:
        text: Hebrew text (may include nikud)
        method: Gematria method to use

    Returns:
        Gematria value
    """
    clean = remove_nikud(text)
    letters_only = "".join(c for c in clean if c.strip())

    if method == GematriaMethod.STANDARD:
        return calculate_standard(letters_only)
    elif method == GematriaMethod.KATAN:
        return calculate_katan(letters_only)
    elif method == GematriaMethod.ORDINAL:
        return calculate_ordinal(letters_only)
    elif method == GematriaMethod.ATBASH:
        return calculate_atbash(letters_only)
    else:
        raise ValueError(f"Unknown gematria method: {method}")
