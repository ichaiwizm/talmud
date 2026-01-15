"""Hebrew text processing and gematria calculations.

Simple API for frontend usage:
    from src.utils.hebrew import calculate_all
    result = calculate_all("אברהם")
    # {"standard": 248, "katan": 14, "ordinal": 41, "atbash": 779}
"""

from .gematria import (
    GematriaMethod,
    calculate,
    calculate_all,
    calculate_standard,
    calculate_katan,
    calculate_ordinal,
    calculate_atbash,
)
from .normalize import remove_nikud, normalize_final_letters, extract_words
from .constants import HEBREW_LETTERS

__all__ = [
    # Main API
    "calculate_all",
    "calculate",
    "GematriaMethod",
    # Individual calculations
    "calculate_standard",
    "calculate_katan",
    "calculate_ordinal",
    "calculate_atbash",
    # Normalization
    "remove_nikud",
    "normalize_final_letters",
    "extract_words",
    # Constants
    "HEBREW_LETTERS",
]
