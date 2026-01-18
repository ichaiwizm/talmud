"""Service for extracting narrative structure: units, genealogy, themes, topics."""
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.db.models.torah import TorahVerse
from src.db.models.names import TorahName
from src.db.models.narrative import (
    NarrativeUnit,
    Genealogy,
    Marriage,
    VerseTopic,
    VerseTheme,
    NarrativeUnitType,
)
from src.services.base_extraction_service import BaseExtractionService

logger = logging.getLogger(__name__)


@dataclass
class ExtractedGenealogy:
    """Extracted genealogical data."""
    person: str
    father: Optional[str]
    mother: Optional[str]
    birth_order: Optional[int]
    lifespan: Optional[int]
    age_at_first_child: Optional[int]
    confidence: float = 0.8


@dataclass
class ExtractedMarriage:
    """Extracted marriage data."""
    husband: str
    wife: str
    marriage_order: int = 1
    is_primary: bool = True
    is_concubine: bool = False
    confidence: float = 0.8


@dataclass
class ExtractedTopic:
    """Extracted topic for a verse."""
    topic: str
    relevance_score: float = 0.8


@dataclass
class ExtractedTheme:
    """Extracted theme for a verse."""
    theme: str
    relevance_score: float = 0.8


class NarrativeExtractionService(BaseExtractionService):
    """Service for extracting narrative structure from Torah verses."""

    EXTRACTION_NAME = "narrative"

    def __init__(self, db: Session, model: str = None, max_workers: int = 5):
        super().__init__(db, model, max_workers)
        self._name_cache: Dict[str, int] = {}

    def build_prompt(self, verses_data: List[Dict]) -> str:
        """Build prompt for narrative extraction."""
        verses_text = "\n".join(
            f"{i+1}. {v['ref']} | {v['text_english'][:180]}"
            for i, v in enumerate(verses_data)
        )

        return f"""Expert en textes bibliques. Tache: extraire la STRUCTURE NARRATIVE (genealogie, mariages, themes, topics).

VERSETS A ANALYSER ({len(verses_data)} versets):
{verses_text}

===== GENEALOGIE =====
Extraire les relations pere-fils, mere-enfant, durees de vie:
- person: nom de la personne
- father: nom du pere
- mother: nom de la mere (si mentionne)
- birth_order: rang de naissance (1=premier-ne)
- lifespan: annees de vie
- age_at_first_child: age quand premier enfant

===== MARIAGES =====
- husband: nom du mari
- wife: nom de l'epouse
- marriage_order: 1ere, 2e femme, etc.
- is_concubine: true si concubine

===== TOPICS (sujets) =====
Sujets concrets traites: covenant, creation, law, journey, sacrifice, genealogy,
blessing, curse, birth, death, marriage, conflict, reconciliation, promise,
dream, vision, building, agriculture, famine, exile, return

===== THEMES (themes abstraits) =====
Themes theologiques/moraux: faith, obedience, redemption, justice, mercy,
grace, providence, covenant_faithfulness, sin, repentance, election,
promise_fulfillment, divine_guidance, human_failure, restoration

===== FORMAT JSON =====
{{
  "Genesis 5:3": {{
    "genealogy": [
      {{
        "person": "Seth",
        "father": "Adam",
        "mother": "Eve",
        "birth_order": 3,
        "lifespan": null,
        "confidence": 0.9
      }}
    ],
    "marriages": [],
    "topics": ["genealogy", "birth"],
    "themes": ["providence", "continuation"]
  }},
  "Genesis 5:5": {{
    "genealogy": [
      {{
        "person": "Adam",
        "lifespan": 930,
        "confidence": 0.95
      }}
    ],
    "marriages": [],
    "topics": ["death", "genealogy"],
    "themes": ["mortality", "sin_consequence"]
  }}
}}

IMPORTANT:
- Extraire UNIQUEMENT ce qui est explicite
- Utiliser les noms canoniques
- Topics et themes: 2-4 par verset maximum
- Si rien a extraire: tableaux vides"""

    def parse_response(self, response_text: str, verses_data: List[Dict]) -> Dict[str, Dict]:
        """Parse narrative extraction response."""
        results = {v["ref"]: {"genealogy": [], "marriages": [], "topics": [], "themes": []} for v in verses_data}

        try:
            data = self.parse_json_response(response_text)

            for verse_ref, verse_data in data.items():
                if verse_ref not in results:
                    continue

                # Parse genealogy
                for gen in verse_data.get("genealogy", []):
                    results[verse_ref]["genealogy"].append(
                        ExtractedGenealogy(
                            person=gen.get("person", ""),
                            father=gen.get("father"),
                            mother=gen.get("mother"),
                            birth_order=gen.get("birth_order"),
                            lifespan=gen.get("lifespan"),
                            age_at_first_child=gen.get("age_at_first_child"),
                            confidence=float(gen.get("confidence", 0.8)),
                        )
                    )

                # Parse marriages
                for mar in verse_data.get("marriages", []):
                    results[verse_ref]["marriages"].append(
                        ExtractedMarriage(
                            husband=mar.get("husband", ""),
                            wife=mar.get("wife", ""),
                            marriage_order=mar.get("marriage_order", 1),
                            is_primary=mar.get("is_primary", True),
                            is_concubine=mar.get("is_concubine", False),
                            confidence=float(mar.get("confidence", 0.8)),
                        )
                    )

                # Parse topics
                for topic in verse_data.get("topics", []):
                    if isinstance(topic, str):
                        results[verse_ref]["topics"].append(
                            ExtractedTopic(topic=topic, relevance_score=0.8)
                        )
                    elif isinstance(topic, dict):
                        results[verse_ref]["topics"].append(
                            ExtractedTopic(
                                topic=topic.get("name", topic.get("topic", "")),
                                relevance_score=float(topic.get("relevance", 0.8)),
                            )
                        )

                # Parse themes
                for theme in verse_data.get("themes", []):
                    if isinstance(theme, str):
                        results[verse_ref]["themes"].append(
                            ExtractedTheme(theme=theme, relevance_score=0.8)
                        )
                    elif isinstance(theme, dict):
                        results[verse_ref]["themes"].append(
                            ExtractedTheme(
                                theme=theme.get("name", theme.get("theme", "")),
                                relevance_score=float(theme.get("relevance", 0.8)),
                            )
                        )

        except Exception as e:
            logger.warning(f"Failed to parse narrative response: {e}")

        return results

    def save_extraction(self, verse: TorahVerse, items: Dict) -> int:
        """Save extracted narrative data to database."""
        saved = 0

        # Save genealogy
        for gen in items.get("genealogy", []):
            try:
                saved += self._save_genealogy(verse, gen)
            except Exception as e:
                logger.warning(f"Failed to save genealogy: {e}")

        # Save marriages
        for mar in items.get("marriages", []):
            try:
                saved += self._save_marriage(verse, mar)
            except Exception as e:
                logger.warning(f"Failed to save marriage: {e}")

        # Save topics
        for topic in items.get("topics", []):
            try:
                saved += self._save_topic(verse, topic)
            except Exception as e:
                logger.warning(f"Failed to save topic: {e}")

        # Save themes
        for theme in items.get("themes", []):
            try:
                saved += self._save_theme(verse, theme)
            except Exception as e:
                logger.warning(f"Failed to save theme: {e}")

        return saved

    def _save_genealogy(self, verse: TorahVerse, gen: ExtractedGenealogy) -> int:
        """Save genealogical data."""
        person_id = self._get_name_id(gen.person)
        if not person_id:
            return 0

        # Check if genealogy already exists for this person
        existing = self.db.query(Genealogy).filter(Genealogy.person_id == person_id).first()
        if existing:
            # Update existing record if we have new info
            if gen.father and not existing.father_id:
                existing.father_id = self._get_name_id(gen.father)
                existing.father_name = gen.father
            if gen.mother and not existing.mother_id:
                existing.mother_id = self._get_name_id(gen.mother)
                existing.mother_name = gen.mother
            if gen.lifespan and not existing.lifespan_years:
                existing.lifespan_years = gen.lifespan
            if gen.birth_order and not existing.birth_order:
                existing.birth_order = gen.birth_order
            if gen.age_at_first_child and not existing.age_at_first_child:
                existing.age_at_first_child = gen.age_at_first_child
            return 0  # Updated, not new

        genealogy = Genealogy(
            person_id=person_id,
            father_id=self._get_name_id(gen.father) if gen.father else None,
            mother_id=self._get_name_id(gen.mother) if gen.mother else None,
            father_name=gen.father,
            mother_name=gen.mother,
            birth_order=gen.birth_order,
            lifespan_years=gen.lifespan,
            age_at_first_child=gen.age_at_first_child,
            birth_verse_id=verse.id,
            confidence=gen.confidence,
        )
        self.db.add(genealogy)
        return 1

    def _save_marriage(self, verse: TorahVerse, mar: ExtractedMarriage) -> int:
        """Save marriage data."""
        husband_id = self._get_name_id(mar.husband)
        wife_id = self._get_name_id(mar.wife)

        if not husband_id or not wife_id:
            return 0

        # Check for existing marriage
        existing = (
            self.db.query(Marriage)
            .filter(
                and_(
                    Marriage.husband_id == husband_id,
                    Marriage.wife_id == wife_id,
                )
            )
            .first()
        )

        if existing:
            return 0

        marriage = Marriage(
            husband_id=husband_id,
            wife_id=wife_id,
            husband_name=mar.husband,
            wife_name=mar.wife,
            marriage_order=mar.marriage_order,
            is_primary=mar.is_primary,
            is_concubine=mar.is_concubine,
            verse_id=verse.id,
            verse_ref=verse.ref,
            confidence=mar.confidence,
        )
        self.db.add(marriage)
        return 1

    def _save_topic(self, verse: TorahVerse, topic: ExtractedTopic) -> int:
        """Save verse topic."""
        # Check for existing
        existing = (
            self.db.query(VerseTopic)
            .filter(
                and_(
                    VerseTopic.verse_id == verse.id,
                    VerseTopic.topic == topic.topic,
                )
            )
            .first()
        )

        if existing:
            return 0

        verse_topic = VerseTopic(
            verse_id=verse.id,
            topic=topic.topic,
            relevance_score=topic.relevance_score,
            confidence=topic.relevance_score,
        )
        self.db.add(verse_topic)
        return 1

    def _save_theme(self, verse: TorahVerse, theme: ExtractedTheme) -> int:
        """Save verse theme."""
        # Check for existing
        existing = (
            self.db.query(VerseTheme)
            .filter(
                and_(
                    VerseTheme.verse_id == verse.id,
                    VerseTheme.theme == theme.theme,
                )
            )
            .first()
        )

        if existing:
            return 0

        verse_theme = VerseTheme(
            verse_id=verse.id,
            theme=theme.theme,
            relevance_score=theme.relevance_score,
            confidence=theme.relevance_score,
        )
        self.db.add(verse_theme)
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
        """Get status of narrative extraction."""
        base_status = super().get_extraction_status()

        genealogy_count = self.db.query(Genealogy).count()
        marriage_count = self.db.query(Marriage).count()
        topics_count = self.db.query(VerseTopic).count()
        themes_count = self.db.query(VerseTheme).count()

        return {
            **base_status,
            "genealogy_entries": genealogy_count,
            "marriages": marriage_count,
            "verse_topics": topics_count,
            "verse_themes": themes_count,
        }
