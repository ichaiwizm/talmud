"""Hebrew letter constants and gematria value mappings."""

# All Hebrew letters (including final forms)
HEBREW_LETTERS = set("אבגדהוזחטיכלמנסעפצקרשתךםןףץ")

# Final letters (sofit) to regular form mapping
FINAL_LETTERS_MAP = {
    "ך": "כ",  # Final Kaf
    "ם": "מ",  # Final Mem
    "ן": "נ",  # Final Nun
    "ף": "פ",  # Final Pe
    "ץ": "צ",  # Final Tsade
}

# Standard Gematria (Mispar Gadol)
# א=1, ב=2... י=10, כ=20... ק=100, ר=200...
GEMATRIA_STANDARD = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5,
    "ו": 6, "ז": 7, "ח": 8, "ט": 9, "י": 10,
    "כ": 20, "ך": 20,
    "ל": 30,
    "מ": 40, "ם": 40,
    "נ": 50, "ן": 50,
    "ס": 60,
    "ע": 70,
    "פ": 80, "ף": 80,
    "צ": 90, "ץ": 90,
    "ק": 100, "ר": 200, "ש": 300, "ת": 400,
}

# Mispar Katan (small value, 1-9 cycle, ignores tens/hundreds)
GEMATRIA_KATAN = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5,
    "ו": 6, "ז": 7, "ח": 8, "ט": 9,
    "י": 1, "כ": 2, "ך": 2, "ל": 3,
    "מ": 4, "ם": 4, "נ": 5, "ן": 5,
    "ס": 6, "ע": 7, "פ": 8, "ף": 8,
    "צ": 9, "ץ": 9, "ק": 1, "ר": 2,
    "ש": 3, "ת": 4,
}

# Ordinal Gematria (position in alphabet, 1-22)
GEMATRIA_ORDINAL = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5,
    "ו": 6, "ז": 7, "ח": 8, "ט": 9, "י": 10,
    "כ": 11, "ך": 11, "ל": 12,
    "מ": 13, "ם": 13, "נ": 14, "ן": 14,
    "ס": 15, "ע": 16, "פ": 17, "ף": 17,
    "צ": 18, "ץ": 18, "ק": 19, "ר": 20,
    "ש": 21, "ת": 22,
}

# Atbash cipher mapping (first letter <-> last letter)
# א <-> ת, ב <-> ש, ג <-> ר, etc.
ATBASH_MAP = {
    "א": "ת", "ב": "ש", "ג": "ר", "ד": "ק", "ה": "צ",
    "ו": "פ", "ז": "ע", "ח": "ס", "ט": "נ", "י": "מ",
    "כ": "ל", "ל": "כ", "מ": "י", "נ": "ט", "ס": "ח",
    "ע": "ז", "פ": "ו", "צ": "ה", "ק": "ד", "ר": "ג",
    "ש": "ב", "ת": "א",
    # Final forms map to their base equivalent's atbash
    "ך": "ל", "ם": "י", "ן": "ט", "ף": "ו", "ץ": "ה",
}
