"""Service for extracting relationships, events, and direct speech from Torah verses."""
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.db.models.torah import TorahVerse
from src.db.models.names import TorahName
from src.db.models.relationships import (
    EntityRelationship,
    Event,
    EventParticipant,
    DirectSpeech,
    RelationshipType,
    RelationshipCategory,
    EventType,
    ParticipantRole,
    SpeechType,
)
from src.services.base_extraction_service import BaseExtractionService

logger = logging.getLogger(__name__)


@dataclass
class ExtractedRelationship:
    """Extracted relationship between entities."""
    source_name: str
    target_name: str
    relationship_type: str
    category: str
    confidence: float
    notes: Optional[str] = None


@dataclass
class ExtractedEvent:
    """Extracted event from the narrative."""
    event_type: str
    description: str
    participants: List[Dict[str, str]]  # [{name, role}]
    location: Optional[str] = None
    is_miraculous: bool = False
    divine_involvement: Optional[str] = None
    confidence: float = 0.8


@dataclass
class ExtractedSpeech:
    """Extracted direct speech."""
    speaker: str
    addressee: Optional[str]
    speech_type: str
    speech_text: str
    is_divine: bool = False
    confidence: float = 0.8


class RelationshipExtractionService(BaseExtractionService):
    """Service for extracting entity relationships from Torah verses."""

    EXTRACTION_NAME = "relationships"

    def __init__(self, db: Session, model: str = None, max_workers: int = 5):
        super().__init__(db, model, max_workers)
        self._name_cache: Dict[str, int] = {}

    def build_prompt(self, verses_data: List[Dict]) -> str:
        """Build prompt for relationship extraction."""
        verses_text = "\n".join(
            f"{i+1}. {v['ref']} | {v['text_hebrew'][:80]} | {v['text_english'][:150]}"
            for i, v in enumerate(verses_data)
        )

        return f"""Expert en textes bibliques hebraiques. Tache: extraire les RELATIONS, EVENEMENTS et DISCOURS DIRECTS.

VERSETS A ANALYSER ({len(verses_data)} versets):
{verses_text}

===== EXTRACTION DES RELATIONS =====
Types de relations a extraire:
FAMILLE: parent_of, child_of, spouse_of, sibling_of, ancestor_of, descendant_of
POLITIQUE: rules_over, serves, ally_of, enemy_of, successor_of
SPIRITUEL: blesses, curses, speaks_to, appears_to, worships, covenants_with
SPATIAL: lives_in, travels_to, born_in, dies_in, buried_in, flees_to

===== EXTRACTION DES EVENEMENTS =====
Types d'evenements:
birth, death, marriage, covenant, battle, miracle, theophany, journey,
construction, sacrifice, blessing, curse, prophecy, law_giving, creation,
destruction, naming, circumcision

Roles des participants: agent, patient, beneficiary, witness, instrument, location

===== EXTRACTION DES DISCOURS DIRECTS =====
Types de discours:
command, question, blessing, curse, prophecy, prayer, promise, warning, narrative, dialogue

===== FORMAT DE REPONSE JSON =====
{{
  "Genesis 1:1": {{
    "relationships": [
      {{"source": "God", "target": "heaven", "type": "creation", "category": "spiritual", "confidence": 0.95}}
    ],
    "events": [
      {{
        "type": "creation",
        "description": "God creates heaven and earth",
        "participants": [{{"name": "God", "role": "agent"}}, {{"name": "heaven", "role": "patient"}}],
        "is_miraculous": true,
        "divine_involvement": "direct"
      }}
    ],
    "speech": []
  }},
  "Genesis 1:3": {{
    "relationships": [],
    "events": [],
    "speech": [
      {{
        "speaker": "God",
        "addressee": null,
        "type": "command",
        "text": "Let there be light",
        "is_divine": true,
        "confidence": 0.95
      }}
    ]
  }}
}}

IMPORTANT:
- Extraire UNIQUEMENT ce qui est explicite ou clairement implique dans le texte
- Utiliser les noms canoniques (ex: "God" pas "the LORD")
- Si rien a extraire pour un verset, utiliser des tableaux vides
- Repondre UNIQUEMENT avec le JSON, sans explication"""

    def parse_response(self, response_text: str, verses_data: List[Dict]) -> Dict[str, Dict]:
        """Parse Claude's response into structured data."""
        results = {v["ref"]: {"relationships": [], "events": [], "speech": []} for v in verses_data}

        try:
            data = self.parse_json_response(response_text)

            for verse_ref, verse_data in data.items():
                if verse_ref not in results:
                    continue

                # Parse relationships
                for rel in verse_data.get("relationships", []):
                    results[verse_ref]["relationships"].append(
                        ExtractedRelationship(
                            source_name=rel.get("source", ""),
                            target_name=rel.get("target", ""),
                            relationship_type=rel.get("type", ""),
                            category=rel.get("category", ""),
                            confidence=float(rel.get("confidence", 0.5)),
                            notes=rel.get("notes"),
                        )
                    )

                # Parse events
                for evt in verse_data.get("events", []):
                    results[verse_ref]["events"].append(
                        ExtractedEvent(
                            event_type=evt.get("type", ""),
                            description=evt.get("description", ""),
                            participants=evt.get("participants", []),
                            location=evt.get("location"),
                            is_miraculous=evt.get("is_miraculous", False),
                            divine_involvement=evt.get("divine_involvement"),
                            confidence=float(evt.get("confidence", 0.5)),
                        )
                    )

                # Parse speech
                for spch in verse_data.get("speech", []):
                    results[verse_ref]["speech"].append(
                        ExtractedSpeech(
                            speaker=spch.get("speaker", ""),
                            addressee=spch.get("addressee"),
                            speech_type=spch.get("type", "dialogue"),
                            speech_text=spch.get("text", ""),
                            is_divine=spch.get("is_divine", False),
                            confidence=float(spch.get("confidence", 0.5)),
                        )
                    )

        except Exception as e:
            logger.warning(f"Failed to parse relationship response: {e}")

        return results

    def save_extraction(self, verse: TorahVerse, items: Dict) -> int:
        """Save extracted relationships, events, and speech to database."""
        saved = 0

        # Save relationships
        for rel in items.get("relationships", []):
            try:
                saved += self._save_relationship(verse, rel)
            except Exception as e:
                logger.warning(f"Failed to save relationship: {e}")

        # Save events
        for evt in items.get("events", []):
            try:
                saved += self._save_event(verse, evt)
            except Exception as e:
                logger.warning(f"Failed to save event: {e}")

        # Save speech
        for spch in items.get("speech", []):
            try:
                saved += self._save_speech(verse, spch)
            except Exception as e:
                logger.warning(f"Failed to save speech: {e}")

        return saved

    def _save_relationship(self, verse: TorahVerse, rel: ExtractedRelationship) -> int:
        """Save a single relationship."""
        source_id = self._get_or_create_name_id(rel.source_name)
        target_id = self._get_or_create_name_id(rel.target_name)

        if not source_id or not target_id:
            return 0

        # Map relationship type
        try:
            rel_type = RelationshipType(rel.relationship_type)
        except ValueError:
            rel_type = RelationshipType.SPEAKS_TO  # Default

        # Map category
        try:
            rel_cat = RelationshipCategory(rel.category)
        except ValueError:
            rel_cat = RelationshipCategory.SPIRITUAL  # Default

        # Check for existing relationship
        existing = (
            self.db.query(EntityRelationship)
            .filter(
                and_(
                    EntityRelationship.source_entity_id == source_id,
                    EntityRelationship.target_entity_id == target_id,
                    EntityRelationship.relationship_type == rel_type,
                    EntityRelationship.verse_id == verse.id,
                )
            )
            .first()
        )

        if existing:
            return 0

        entity_rel = EntityRelationship(
            source_entity_id=source_id,
            target_entity_id=target_id,
            relationship_type=rel_type,
            relationship_category=rel_cat,
            verse_id=verse.id,
            confidence=rel.confidence,
            notes=rel.notes,
            extraction_source="claude",
        )
        self.db.add(entity_rel)
        return 1

    def _save_event(self, verse: TorahVerse, evt: ExtractedEvent) -> int:
        """Save an event and its participants."""
        # Map event type
        try:
            event_type = EventType(evt.event_type)
        except ValueError:
            event_type = EventType.CREATION  # Default

        location_id = None
        if evt.location:
            location_id = self._get_or_create_name_id(evt.location)

        event = Event(
            event_type=event_type,
            description=evt.description,
            verse_start_id=verse.id,
            location_id=location_id,
            is_miraculous=evt.is_miraculous,
            divine_involvement=evt.divine_involvement,
            confidence=evt.confidence,
            extraction_source="claude",
        )
        self.db.add(event)
        self.db.flush()  # Get event ID

        # Save participants
        for p in evt.participants:
            entity_id = self._get_or_create_name_id(p.get("name", ""))
            if not entity_id:
                continue

            try:
                role = ParticipantRole(p.get("role", "agent"))
            except ValueError:
                role = ParticipantRole.AGENT

            participant = EventParticipant(
                event_id=event.id,
                entity_id=entity_id,
                role=role,
            )
            self.db.add(participant)

        return 1

    def _save_speech(self, verse: TorahVerse, spch: ExtractedSpeech) -> int:
        """Save direct speech."""
        speaker_id = self._get_or_create_name_id(spch.speaker)
        addressee_id = None
        if spch.addressee:
            addressee_id = self._get_or_create_name_id(spch.addressee)

        # Map speech type
        try:
            speech_type = SpeechType(spch.speech_type)
        except ValueError:
            speech_type = SpeechType.DIALOGUE

        speech = DirectSpeech(
            verse_id=verse.id,
            speaker_id=speaker_id,
            addressee_id=addressee_id,
            speech_type=speech_type,
            speech_text=spch.speech_text,
            is_divine_speech=spch.is_divine,
            confidence=spch.confidence,
            extraction_source="claude",
        )
        self.db.add(speech)
        return 1

    def _get_or_create_name_id(self, name: str) -> Optional[int]:
        """Get name ID from cache or database, creating if necessary."""
        if not name:
            return None

        # Check cache first
        if name in self._name_cache:
            return self._name_cache[name]

        # Query database
        torah_name = (
            self.db.query(TorahName)
            .filter(TorahName.name_canonical == name)
            .first()
        )

        if torah_name:
            self._name_cache[name] = torah_name.id
            return torah_name.id

        # Name not found - don't create new names in relationship extraction
        # Just return None to skip this relationship
        return None

    def get_extraction_status(self) -> Dict[str, Any]:
        """Get status of relationship extraction."""
        base_status = super().get_extraction_status()

        relationships_count = self.db.query(EntityRelationship).count()
        events_count = self.db.query(Event).count()
        speech_count = self.db.query(DirectSpeech).count()

        return {
            **base_status,
            "relationships_extracted": relationships_count,
            "events_extracted": events_count,
            "speech_extracted": speech_count,
        }
