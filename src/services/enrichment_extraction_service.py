"""Service for extracting enrichments: sentiment, symbols, cross-references."""
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.db.models.torah import TorahVerse
from src.db.models.names import TorahName
from src.db.models.enrichment import (
    VerseSentiment,
    CharacterEmotion,
    SymbolicNumber,
    SymbolicElement,
    RecurringMotif,
    MotifOccurrence,
    CrossReference,
    EmotionType,
    DivineSentiment,
    SymbolicElementType,
    CrossReferenceType,
)
from src.services.base_extraction_service import BaseExtractionService

logger = logging.getLogger(__name__)


@dataclass
class ExtractedSentiment:
    """Extracted sentiment for a verse."""
    primary_emotion: str
    secondary_emotion: Optional[str] = None
    sentiment_polarity: float = 0.0
    tension_level: float = 0.0
    divine_sentiment: Optional[str] = None
    confidence: float = 0.8


@dataclass
class ExtractedCharacterEmotion:
    """Extracted emotion for a character."""
    character: str
    emotion: str
    trigger: Optional[str] = None
    resulting_action: Optional[str] = None
    confidence: float = 0.8


@dataclass
class ExtractedSymbol:
    """Extracted symbolic element."""
    name: str
    element_type: str
    meaning: Optional[str] = None
    is_positive: Optional[bool] = None
    confidence: float = 0.8


@dataclass
class ExtractedNumber:
    """Extracted symbolic number."""
    value: int
    context: str
    meaning: Optional[str] = None
    is_symbolic: bool = False
    confidence: float = 0.8


class EnrichmentExtractionService(BaseExtractionService):
    """Service for extracting sentiment, symbols, and enrichments from Torah verses."""

    EXTRACTION_NAME = "enrichment"

    def __init__(self, db: Session, model: str = None, max_workers: int = 5):
        super().__init__(db, model, max_workers)
        self._name_cache: Dict[str, int] = {}
        self._motif_cache: Dict[str, int] = {}

    def build_prompt(self, verses_data: List[Dict]) -> str:
        """Build prompt for enrichment extraction."""
        verses_text = "\n".join(
            f"{i+1}. {v['ref']} | {v['text_english'][:180]}"
            for i, v in enumerate(verses_data)
        )

        return f"""Expert en analyse biblique. Tache: extraire SENTIMENTS, SYMBOLES et NOMBRES significatifs.

VERSETS A ANALYSER ({len(verses_data)} versets):
{verses_text}

===== SENTIMENT DU VERSET =====
Emotions: joy, fear, anger, sorrow, love, awe, gratitude, jealousy, shame, hope, despair, compassion, neutral
Polarite: -1.0 (tres negatif) a +1.0 (tres positif)
Tension: 0.0 (calme) a 1.0 (tres tendu)
Sentiment divin: pleased, displeased, angry, merciful, jealous, grieved, neutral

===== EMOTIONS DES PERSONNAGES =====
Pour chaque personnage avec emotion explicite:
- trigger: cause de l'emotion
- resulting_action: action resultante

===== ELEMENTS SYMBOLIQUES =====
Types: animal, plant, color, number, object, natural_element, body_part, direction, time, material

Exemples: serpent (ruse), arc-en-ciel (alliance), huile (onction), eau (purification), montagne (revelation)

===== NOMBRES SYMBOLIQUES =====
Nombres avec signification: 7 (perfection), 40 (epreuve), 12 (tribus), 3 (divin), 10 (completude)

===== FORMAT JSON =====
{{
  "Genesis 3:8": {{
    "sentiment": {{
      "primary_emotion": "fear",
      "secondary_emotion": "shame",
      "polarity": -0.6,
      "tension": 0.8,
      "divine_sentiment": "displeased",
      "confidence": 0.9
    }},
    "character_emotions": [
      {{
        "character": "Adam",
        "emotion": "fear",
        "trigger": "Hearing God's voice after sinning",
        "resulting_action": "Hiding among the trees",
        "confidence": 0.9
      }}
    ],
    "symbols": [
      {{
        "name": "tree",
        "type": "plant",
        "meaning": "knowledge, life, temptation",
        "is_positive": null,
        "confidence": 0.85
      }}
    ],
    "numbers": []
  }},
  "Genesis 7:4": {{
    "sentiment": {{
      "primary_emotion": "awe",
      "polarity": -0.4,
      "tension": 0.9,
      "divine_sentiment": "grieved",
      "confidence": 0.85
    }},
    "character_emotions": [],
    "symbols": [
      {{"name": "rain", "type": "natural_element", "meaning": "judgment, destruction", "is_positive": false}}
    ],
    "numbers": [
      {{"value": 40, "context": "days and nights of rain", "meaning": "period of testing/judgment", "is_symbolic": true}}
    ]
  }}
}}

IMPORTANT:
- Extraire UNIQUEMENT ce qui est explicite ou fortement implique
- Etre prudent avec l'interpretation symbolique
- Repondre UNIQUEMENT en JSON"""

    def parse_response(self, response_text: str, verses_data: List[Dict]) -> Dict[str, Dict]:
        """Parse enrichment extraction response."""
        results = {
            v["ref"]: {"sentiment": None, "character_emotions": [], "symbols": [], "numbers": []}
            for v in verses_data
        }

        try:
            data = self.parse_json_response(response_text)

            for verse_ref, verse_data in data.items():
                if verse_ref not in results:
                    continue

                # Parse sentiment
                sent = verse_data.get("sentiment")
                if sent:
                    results[verse_ref]["sentiment"] = ExtractedSentiment(
                        primary_emotion=sent.get("primary_emotion", "neutral"),
                        secondary_emotion=sent.get("secondary_emotion"),
                        sentiment_polarity=float(sent.get("polarity", 0.0)),
                        tension_level=float(sent.get("tension", 0.0)),
                        divine_sentiment=sent.get("divine_sentiment"),
                        confidence=float(sent.get("confidence", 0.8)),
                    )

                # Parse character emotions
                for ce in verse_data.get("character_emotions", []):
                    results[verse_ref]["character_emotions"].append(
                        ExtractedCharacterEmotion(
                            character=ce.get("character", ""),
                            emotion=ce.get("emotion", "neutral"),
                            trigger=ce.get("trigger"),
                            resulting_action=ce.get("resulting_action"),
                            confidence=float(ce.get("confidence", 0.8)),
                        )
                    )

                # Parse symbols
                for sym in verse_data.get("symbols", []):
                    results[verse_ref]["symbols"].append(
                        ExtractedSymbol(
                            name=sym.get("name", ""),
                            element_type=sym.get("type", "object"),
                            meaning=sym.get("meaning"),
                            is_positive=sym.get("is_positive"),
                            confidence=float(sym.get("confidence", 0.8)),
                        )
                    )

                # Parse numbers
                for num in verse_data.get("numbers", []):
                    results[verse_ref]["numbers"].append(
                        ExtractedNumber(
                            value=int(num.get("value", 0)),
                            context=num.get("context", ""),
                            meaning=num.get("meaning"),
                            is_symbolic=num.get("is_symbolic", False),
                            confidence=float(num.get("confidence", 0.8)),
                        )
                    )

        except Exception as e:
            logger.warning(f"Failed to parse enrichment response: {e}")

        return results

    def save_extraction(self, verse: TorahVerse, items: Dict) -> int:
        """Save extracted enrichment data to database."""
        saved = 0

        # Save sentiment
        if items.get("sentiment"):
            try:
                saved += self._save_sentiment(verse, items["sentiment"])
            except Exception as e:
                logger.warning(f"Failed to save sentiment: {e}")

        # Save character emotions
        for ce in items.get("character_emotions", []):
            try:
                saved += self._save_character_emotion(verse, ce)
            except Exception as e:
                logger.warning(f"Failed to save character emotion: {e}")

        # Save symbols
        for sym in items.get("symbols", []):
            try:
                saved += self._save_symbol(verse, sym)
            except Exception as e:
                logger.warning(f"Failed to save symbol: {e}")

        # Save numbers
        for num in items.get("numbers", []):
            try:
                saved += self._save_number(verse, num)
            except Exception as e:
                logger.warning(f"Failed to save number: {e}")

        return saved

    def _save_sentiment(self, verse: TorahVerse, sent: ExtractedSentiment) -> int:
        """Save verse sentiment."""
        # Check for existing
        existing = self.db.query(VerseSentiment).filter(VerseSentiment.verse_id == verse.id).first()
        if existing:
            return 0

        # Map emotion types
        try:
            primary = EmotionType(sent.primary_emotion.lower())
        except ValueError:
            primary = EmotionType.NEUTRAL

        secondary = None
        if sent.secondary_emotion:
            try:
                secondary = EmotionType(sent.secondary_emotion.lower())
            except ValueError:
                pass

        divine = None
        if sent.divine_sentiment:
            try:
                divine = DivineSentiment(sent.divine_sentiment.lower())
            except ValueError:
                pass

        sentiment = VerseSentiment(
            verse_id=verse.id,
            primary_emotion=primary,
            secondary_emotion=secondary,
            sentiment_polarity=sent.sentiment_polarity,
            tension_level=sent.tension_level,
            divine_sentiment=divine,
            confidence=sent.confidence,
        )
        self.db.add(sentiment)
        return 1

    def _save_character_emotion(self, verse: TorahVerse, ce: ExtractedCharacterEmotion) -> int:
        """Save character emotion."""
        character_id = self._get_name_id(ce.character)
        if not character_id:
            return 0

        # Map emotion type
        try:
            emotion = EmotionType(ce.emotion.lower())
        except ValueError:
            emotion = EmotionType.NEUTRAL

        char_emotion = CharacterEmotion(
            verse_id=verse.id,
            character_id=character_id,
            character_name=ce.character,
            emotion=emotion,
            trigger=ce.trigger,
            resulting_action=ce.resulting_action,
            confidence=ce.confidence,
        )
        self.db.add(char_emotion)
        return 1

    def _save_symbol(self, verse: TorahVerse, sym: ExtractedSymbol) -> int:
        """Save symbolic element."""
        if not sym.name:
            return 0

        # Map element type
        try:
            elem_type = SymbolicElementType(sym.element_type.lower())
        except ValueError:
            elem_type = SymbolicElementType.OBJECT

        symbol = SymbolicElement(
            verse_id=verse.id,
            element_name=sym.name,
            element_type=elem_type,
            symbolic_meaning=sym.meaning,
            is_positive=sym.is_positive if sym.is_positive is not None else None,
            is_negative=not sym.is_positive if sym.is_positive is not None else None,
            confidence=sym.confidence,
        )
        self.db.add(symbol)
        return 1

    def _save_number(self, verse: TorahVerse, num: ExtractedNumber) -> int:
        """Save symbolic number."""
        if num.value <= 0:
            return 0

        number = SymbolicNumber(
            verse_id=verse.id,
            number_value=num.value,
            context=num.context,
            symbolic_meaning=num.meaning,
            is_literal=not num.is_symbolic,
            is_symbolic=num.is_symbolic,
            confidence=num.confidence,
        )
        self.db.add(number)
        return 1

    def _get_name_id(self, name: str) -> Optional[int]:
        """Get name ID from cache or database."""
        if not name:
            return None

        if name in self._name_cache:
            return self._name_cache[name]

        torah_name = (
            self.db.query(TorahName)
            .filter(TorahName.name_canonical == name)
            .first()
        )

        if torah_name:
            self._name_cache[name] = torah_name.id
            return torah_name.id

        return None

    def get_extraction_status(self) -> Dict[str, Any]:
        """Get status of enrichment extraction."""
        base_status = super().get_extraction_status()

        sentiment_count = self.db.query(VerseSentiment).count()
        char_emotions_count = self.db.query(CharacterEmotion).count()
        symbols_count = self.db.query(SymbolicElement).count()
        numbers_count = self.db.query(SymbolicNumber).count()
        motifs_count = self.db.query(RecurringMotif).count()

        return {
            **base_status,
            "verse_sentiments": sentiment_count,
            "character_emotions": char_emotions_count,
            "symbolic_elements": symbols_count,
            "symbolic_numbers": numbers_count,
            "recurring_motifs": motifs_count,
        }


class CrossReferenceExtractionService(BaseExtractionService):
    """Service for extracting cross-references between verses."""

    EXTRACTION_NAME = "cross_references"

    def build_prompt(self, verses_data: List[Dict]) -> str:
        """Build prompt for cross-reference extraction."""
        verses_text = "\n".join(
            f"{v['ref']}: {v['text_english'][:150]}"
            for v in verses_data
        )

        return f"""Expert en intertextualite biblique. Tache: identifier les REFERENCES CROISEES dans la Torah.

VERSETS A ANALYSER:
{verses_text}

===== TYPES DE REFERENCES =====
- parallel: contenu similaire
- quotation: citation directe
- fulfillment: accomplissement d'une promesse
- thematic: theme partage
- verbal: vocabulaire partage
- contrast: contenu oppose
- typology: prefiguration
- allusion: reference indirecte

===== FORMAT JSON =====
{{
  "cross_references": [
    {{
      "source": "Genesis 3:15",
      "target": "Genesis 22:18",
      "type": "fulfillment",
      "shared_vocabulary": ["seed", "blessing"],
      "shared_themes": ["redemption", "promise"],
      "explanation": "The promise of blessing through Abraham's seed echoes the protoevangelium",
      "similarity_score": 0.85,
      "bidirectional": true
    }}
  ]
}}

IMPORTANT:
- Se limiter aux references INTERNES a la Torah (Genesis-Deuteronomy)
- Privilegier les connexions explicites et etablies
- Si aucune reference croisee claire: {{"cross_references": []}}"""

    def parse_response(self, response_text: str, verses_data: List[Dict]) -> Dict[str, List]:
        """Parse cross-reference response."""
        results = {"cross_references": []}

        try:
            data = self.parse_json_response(response_text)
            results["cross_references"] = data.get("cross_references", [])
        except Exception as e:
            logger.warning(f"Failed to parse cross-reference response: {e}")

        return results

    def save_extraction(self, verse: TorahVerse, items: Dict) -> int:
        """Save extracted cross-references."""
        saved = 0

        for xref in items.get("cross_references", []):
            try:
                # Get verse IDs
                source_ref = xref.get("source", verse.ref)
                target_ref = xref.get("target")

                if not target_ref:
                    continue

                source_verse = self.db.query(TorahVerse).filter(TorahVerse.ref == source_ref).first()
                target_verse = self.db.query(TorahVerse).filter(TorahVerse.ref == target_ref).first()

                if not source_verse or not target_verse:
                    continue

                # Check for existing
                existing = (
                    self.db.query(CrossReference)
                    .filter(
                        and_(
                            CrossReference.source_verse_id == source_verse.id,
                            CrossReference.target_verse_id == target_verse.id,
                        )
                    )
                    .first()
                )

                if existing:
                    continue

                # Map reference type
                try:
                    ref_type = CrossReferenceType(xref.get("type", "thematic").lower())
                except ValueError:
                    ref_type = CrossReferenceType.THEMATIC

                cross_ref = CrossReference(
                    source_verse_id=source_verse.id,
                    target_verse_id=target_verse.id,
                    source_ref=source_ref,
                    target_ref=target_ref,
                    reference_type=ref_type,
                    shared_vocabulary=xref.get("shared_vocabulary"),
                    shared_themes=xref.get("shared_themes"),
                    similarity_score=float(xref.get("similarity_score", 0.5)),
                    explanation=xref.get("explanation"),
                    is_bidirectional=xref.get("bidirectional", False),
                    confidence=float(xref.get("confidence", 0.7)),
                )
                self.db.add(cross_ref)
                saved += 1

            except Exception as e:
                logger.warning(f"Failed to save cross-reference: {e}")

        return saved
