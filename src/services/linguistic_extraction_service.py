"""Service for extracting linguistic data: roots, formulas, literary structures."""
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.db.models.torah import TorahVerse
from src.db.models.gematria import TorahWord
from src.db.models.linguistic import (
    HebrewRoot,
    WordRoot,
    FormulaicExpression,
    FormulaOccurrence,
    LiteraryStructure,
    VerbForm,
    FormulaType,
    LiteraryStructureType,
)
from src.services.base_extraction_service import BaseExtractionService

logger = logging.getLogger(__name__)


@dataclass
class ExtractedRoot:
    """Extracted Hebrew root."""
    root_letters: str
    transliteration: str
    meaning: str
    word: str
    verb_form: Optional[str] = None
    confidence: float = 0.8


@dataclass
class ExtractedFormula:
    """Extracted formulaic expression."""
    formula_hebrew: str
    formula_english: str
    formula_type: str
    function: Optional[str] = None
    confidence: float = 0.8


class LinguisticExtractionService(BaseExtractionService):
    """Service for extracting linguistic data from Torah verses."""

    EXTRACTION_NAME = "linguistic"

    def __init__(self, db: Session, model: str = None, max_workers: int = 5):
        super().__init__(db, model, max_workers)
        self._root_cache: Dict[str, int] = {}
        self._word_cache: Dict[int, Dict[str, int]] = {}  # verse_id -> {word_text: word_id}

    def build_prompt(self, verses_data: List[Dict]) -> str:
        """Build prompt for linguistic extraction."""
        verses_text = "\n".join(
            f"{i+1}. {v['ref']} | {v['text_hebrew']}"
            for i, v in enumerate(verses_data)
        )

        return f"""Expert en linguistique hebraique biblique. Tache: analyser les RACINES et FORMULES.

VERSETS A ANALYSER ({len(verses_data)} versets):
{verses_text}

===== RACINES HEBRAIQUES =====
Pour chaque mot significatif, identifier:
- root_letters: les 3 (ou 2/4) lettres de la racine hebraique
- transliteration: romanisation (ex: "ברא" -> "bra")
- meaning: sens fondamental de la racine
- word: le mot dans le texte
- verb_form: si verbe, le binyan (qal, niphal, piel, pual, hiphil, hophal, hitpael)

===== FORMULES REPETEES =====
Identifier les expressions formulaires connues:
Types: toledot, wayyomer, blessing, covenant, creation, genealogy, narrative_transition, legal, summary

Exemples:
- "ויהי ערב ויהי בקר" (creation formula)
- "אלה תולדות" (toledot formula)
- "ויאמר יהוה/אלהים" (wayyomer formula)
- "ויברך... לאמר" (blessing formula)

===== FORMAT JSON =====
{{
  "Genesis 1:1": {{
    "roots": [
      {{
        "root_letters": "ברא",
        "transliteration": "bra",
        "meaning": "to create (ex nihilo)",
        "word": "ברא",
        "verb_form": "qal",
        "confidence": 0.95
      }},
      {{
        "root_letters": "ראש",
        "transliteration": "rosh",
        "meaning": "head, beginning",
        "word": "בראשית",
        "verb_form": null,
        "confidence": 0.9
      }}
    ],
    "formulas": []
  }},
  "Genesis 1:5": {{
    "roots": [...],
    "formulas": [
      {{
        "hebrew": "ויהי ערב ויהי בקר יום אחד",
        "english": "And there was evening and there was morning, one day",
        "type": "creation",
        "function": "Marks the conclusion of each creation day",
        "confidence": 0.95
      }}
    ]
  }}
}}

IMPORTANT:
- Se concentrer sur les racines significatives (pas les particules)
- Identifier les formules connues uniquement
- Translitteration: utiliser la romanisation standard
- Repondre UNIQUEMENT en JSON"""

    def parse_response(self, response_text: str, verses_data: List[Dict]) -> Dict[str, Dict]:
        """Parse linguistic extraction response."""
        results = {v["ref"]: {"roots": [], "formulas": []} for v in verses_data}

        try:
            data = self.parse_json_response(response_text)

            for verse_ref, verse_data in data.items():
                if verse_ref not in results:
                    continue

                # Parse roots
                for root in verse_data.get("roots", []):
                    results[verse_ref]["roots"].append(
                        ExtractedRoot(
                            root_letters=root.get("root_letters", ""),
                            transliteration=root.get("transliteration", ""),
                            meaning=root.get("meaning", ""),
                            word=root.get("word", ""),
                            verb_form=root.get("verb_form"),
                            confidence=float(root.get("confidence", 0.8)),
                        )
                    )

                # Parse formulas
                for formula in verse_data.get("formulas", []):
                    results[verse_ref]["formulas"].append(
                        ExtractedFormula(
                            formula_hebrew=formula.get("hebrew", ""),
                            formula_english=formula.get("english", ""),
                            formula_type=formula.get("type", "other"),
                            function=formula.get("function"),
                            confidence=float(formula.get("confidence", 0.8)),
                        )
                    )

        except Exception as e:
            logger.warning(f"Failed to parse linguistic response: {e}")

        return results

    def save_extraction(self, verse: TorahVerse, items: Dict) -> int:
        """Save extracted linguistic data to database."""
        saved = 0

        # Save roots
        for root in items.get("roots", []):
            try:
                saved += self._save_root(verse, root)
            except Exception as e:
                logger.warning(f"Failed to save root: {e}")

        # Save formulas
        for formula in items.get("formulas", []):
            try:
                saved += self._save_formula(verse, formula)
            except Exception as e:
                logger.warning(f"Failed to save formula: {e}")

        return saved

    def _save_root(self, verse: TorahVerse, root: ExtractedRoot) -> int:
        """Save a Hebrew root and its word association."""
        if not root.root_letters:
            return 0

        # Get or create the Hebrew root
        root_id = self._get_or_create_root(root)
        if not root_id:
            return 0

        # Find the word in the verse
        word_id = self._find_word_id(verse, root.word)
        if not word_id:
            # Word not found in torah_words table, skip
            return 0

        # Check if word-root link already exists
        existing = (
            self.db.query(WordRoot)
            .filter(
                and_(
                    WordRoot.word_id == word_id,
                    WordRoot.root_id == root_id,
                )
            )
            .first()
        )

        if existing:
            return 0

        # Map verb form
        verb_form = None
        if root.verb_form:
            try:
                verb_form = VerbForm(root.verb_form.lower())
            except ValueError:
                pass

        word_root = WordRoot(
            word_id=word_id,
            root_id=root_id,
            verb_form=verb_form,
            word_meaning=root.meaning,
            confidence=root.confidence,
        )
        self.db.add(word_root)
        return 1

    def _get_or_create_root(self, root: ExtractedRoot) -> Optional[int]:
        """Get or create a Hebrew root."""
        if root.root_letters in self._root_cache:
            return self._root_cache[root.root_letters]

        # Check database
        hebrew_root = (
            self.db.query(HebrewRoot)
            .filter(HebrewRoot.root_letters == root.root_letters)
            .first()
        )

        if hebrew_root:
            self._root_cache[root.root_letters] = hebrew_root.id
            # Update occurrence count
            hebrew_root.occurrence_count += 1
            return hebrew_root.id

        # Create new root
        hebrew_root = HebrewRoot(
            root_letters=root.root_letters,
            root_transliteration=root.transliteration,
            basic_meaning=root.meaning,
            occurrence_count=1,
        )
        self.db.add(hebrew_root)
        self.db.flush()

        self._root_cache[root.root_letters] = hebrew_root.id
        return hebrew_root.id

    def _find_word_id(self, verse: TorahVerse, word_text: str) -> Optional[int]:
        """Find word ID in torah_words table."""
        if not word_text:
            return None

        # Check cache
        if verse.id in self._word_cache:
            if word_text in self._word_cache[verse.id]:
                return self._word_cache[verse.id][word_text]
        else:
            self._word_cache[verse.id] = {}

        # Query database
        word = (
            self.db.query(TorahWord)
            .filter(
                and_(
                    TorahWord.verse_id == verse.id,
                    TorahWord.word_original == word_text,
                )
            )
            .first()
        )

        if word:
            self._word_cache[verse.id][word_text] = word.id
            return word.id

        # Try normalized form
        word = (
            self.db.query(TorahWord)
            .filter(
                and_(
                    TorahWord.verse_id == verse.id,
                    TorahWord.word_normalized == word_text,
                )
            )
            .first()
        )

        if word:
            self._word_cache[verse.id][word_text] = word.id
            return word.id

        return None

    def _save_formula(self, verse: TorahVerse, formula: ExtractedFormula) -> int:
        """Save a formulaic expression and its occurrence."""
        if not formula.formula_hebrew:
            return 0

        # Get or create the formula
        formula_id = self._get_or_create_formula(formula)
        if not formula_id:
            return 0

        # Check if occurrence already exists
        existing = (
            self.db.query(FormulaOccurrence)
            .filter(
                and_(
                    FormulaOccurrence.formula_id == formula_id,
                    FormulaOccurrence.verse_id == verse.id,
                )
            )
            .first()
        )

        if existing:
            return 0

        occurrence = FormulaOccurrence(
            formula_id=formula_id,
            verse_id=verse.id,
            surface_form=formula.formula_hebrew,
        )
        self.db.add(occurrence)
        return 1

    def _get_or_create_formula(self, formula: ExtractedFormula) -> Optional[int]:
        """Get or create a formulaic expression."""
        # Check for existing formula
        existing = (
            self.db.query(FormulaicExpression)
            .filter(FormulaicExpression.formula_hebrew == formula.formula_hebrew)
            .first()
        )

        if existing:
            existing.occurrence_count += 1
            return existing.id

        # Map formula type
        try:
            formula_type = FormulaType(formula.formula_type.lower())
        except ValueError:
            formula_type = FormulaType.OTHER

        new_formula = FormulaicExpression(
            formula_hebrew=formula.formula_hebrew,
            formula_english=formula.formula_english,
            formula_type=formula_type,
            function=formula.function,
            occurrence_count=1,
        )
        self.db.add(new_formula)
        self.db.flush()

        return new_formula.id

    def get_extraction_status(self) -> Dict[str, Any]:
        """Get status of linguistic extraction."""
        base_status = super().get_extraction_status()

        roots_count = self.db.query(HebrewRoot).count()
        word_roots_count = self.db.query(WordRoot).count()
        formulas_count = self.db.query(FormulaicExpression).count()
        formula_occurrences_count = self.db.query(FormulaOccurrence).count()

        return {
            **base_status,
            "hebrew_roots": roots_count,
            "word_root_links": word_roots_count,
            "formulaic_expressions": formulas_count,
            "formula_occurrences": formula_occurrences_count,
        }


class LiteraryStructureExtractionService(BaseExtractionService):
    """Service for extracting literary structures (chiasmus, parallelism, etc.)."""

    EXTRACTION_NAME = "literary_structures"

    def build_prompt(self, verses_data: List[Dict]) -> str:
        """Build prompt for literary structure extraction.

        Note: This requires analyzing larger blocks of text, so it's typically
        called with chapter-sized batches.
        """
        verses_text = "\n".join(
            f"{v['ref']}: {v['text_english'][:150]}"
            for v in verses_data
        )

        return f"""Expert en rhetorique biblique. Tache: identifier les STRUCTURES LITTERAIRES.

PASSAGE A ANALYSER:
{verses_text}

===== TYPES DE STRUCTURES =====
- chiasmus: ABBA ou ABCBA pattern (structure en miroir)
- parallelism: AB / A'B' (idees paralleles)
- inclusio: meme element au debut et a la fin
- repetition: element repete intentionnellement
- sandwich: ABA pattern (interruption)
- concatenation: liens entre sections

===== FORMAT JSON =====
{{
  "structures": [
    {{
      "type": "chiasmus",
      "verse_start": "Genesis 1:1",
      "verse_end": "Genesis 2:4",
      "pattern": "ABCBA",
      "focal_point": "Genesis 1:27",
      "description": "La creation comme chiasme centre sur l'homme",
      "elements": [
        {{"label": "A", "verses": "1:1-2", "content": "Introduction cosmique"}},
        {{"label": "B", "verses": "1:3-13", "content": "Formation des espaces"}},
        {{"label": "C", "verses": "1:14-19", "content": "Luminaires"}},
        {{"label": "B'", "verses": "1:20-25", "content": "Remplissage des espaces"}},
        {{"label": "A'", "verses": "1:26-31", "content": "Conclusion: l'homme"}}
      ],
      "confidence": 0.85
    }}
  ]
}}

Si aucune structure identifiee: {{"structures": []}}"""

    def parse_response(self, response_text: str, verses_data: List[Dict]) -> Dict[str, List]:
        """Parse literary structure response."""
        results = {"structures": []}

        try:
            data = self.parse_json_response(response_text)
            results["structures"] = data.get("structures", [])
        except Exception as e:
            logger.warning(f"Failed to parse literary structure response: {e}")

        return results

    def save_extraction(self, verse: TorahVerse, items: Dict) -> int:
        """Save extracted literary structures."""
        saved = 0

        for struct in items.get("structures", []):
            try:
                # Map structure type
                try:
                    struct_type = LiteraryStructureType(struct.get("type", "other").lower())
                except ValueError:
                    struct_type = LiteraryStructureType.OTHER

                # Get verse IDs
                start_ref = struct.get("verse_start", verse.ref)
                end_ref = struct.get("verse_end", start_ref)
                focal_ref = struct.get("focal_point")

                start_verse = self.db.query(TorahVerse).filter(TorahVerse.ref == start_ref).first()
                end_verse = self.db.query(TorahVerse).filter(TorahVerse.ref == end_ref).first()
                focal_verse = None
                if focal_ref:
                    focal_verse = self.db.query(TorahVerse).filter(TorahVerse.ref == focal_ref).first()

                structure = LiteraryStructure(
                    verse_start_id=start_verse.id if start_verse else verse.id,
                    verse_end_id=end_verse.id if end_verse else verse.id,
                    verse_start_ref=start_ref,
                    verse_end_ref=end_ref,
                    structure_type=struct_type,
                    pattern_notation=struct.get("pattern"),
                    focal_point_verse_id=focal_verse.id if focal_verse else None,
                    focal_point_ref=focal_ref,
                    description=struct.get("description"),
                    structural_elements=struct.get("elements"),
                    confidence=float(struct.get("confidence", 0.7)),
                )
                self.db.add(structure)
                saved += 1

            except Exception as e:
                logger.warning(f"Failed to save literary structure: {e}")

        return saved
