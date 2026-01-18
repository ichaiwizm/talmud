"""Service for extracting theological content: divine names, mitzvot, covenants, blessings."""
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.db.models.torah import TorahVerse
from src.db.models.names import TorahName
from src.db.models.theological import (
    DivineNameOccurrence,
    Mitzvah,
    Covenant,
    CovenantElement,
    BlessingCurse,
    DivineNameType,
    ContextType,
    MitzvahType,
    MitzvahCategory,
    MitzvahDomain,
    CovenantType,
    BlessingCurseType,
    BlessingCurseCategory,
)
from src.services.base_extraction_service import BaseExtractionService

logger = logging.getLogger(__name__)


@dataclass
class ExtractedDivineName:
    """Extracted divine name occurrence."""
    divine_name: str
    divine_name_hebrew: Optional[str]
    context_type: Optional[str]
    speaker_type: Optional[str]
    theological_note: Optional[str]
    confidence: float = 0.9


@dataclass
class ExtractedMitzvah:
    """Extracted commandment."""
    command_text: str
    command_hebrew: Optional[str]
    mitzvah_type: str  # positive or negative
    category: Optional[str]
    domain: Optional[str]
    applies_to: Optional[str]
    rationale: Optional[str]
    confidence: float = 0.8


@dataclass
class ExtractedBlessing:
    """Extracted blessing or curse."""
    blessing_type: str  # blessing or curse
    giver: Optional[str]
    recipient: Optional[str]
    content: str
    is_conditional: bool
    condition_text: Optional[str]
    category: Optional[str]
    is_divine: bool = False
    confidence: float = 0.8


class TheologicalExtractionService(BaseExtractionService):
    """Service for extracting theological content from Torah verses."""

    EXTRACTION_NAME = "theological"

    def __init__(self, db: Session, model: str = None, max_workers: int = 5):
        super().__init__(db, model, max_workers)
        self._name_cache: Dict[str, int] = {}

    def build_prompt(self, verses_data: List[Dict]) -> str:
        """Build prompt for theological extraction."""
        verses_text = "\n".join(
            f"{i+1}. {v['ref']} | {v['text_hebrew'][:80]} | {v['text_english'][:150]}"
            for i, v in enumerate(verses_data)
        )

        return f"""Expert en textes bibliques hebraiques et theologie. Tache: extraire le CONTENU THEOLOGIQUE.

VERSETS A ANALYSER ({len(verses_data)} versets):
{verses_text}

===== NOMS DIVINS =====
Identifier chaque occurrence d'un nom de Dieu:
- yhwh: יהוה (tetragramme)
- elohim: אלהים (Dieu puissant)
- el_shaddai: אל שדי (Tout-Puissant)
- el_elyon: אל עליון (Tres-Haut)
- adonai: אדני (Seigneur)
- el: אל
- ehyeh: אהיה

Contexte d'usage: creation, covenant, judgment, mercy, revelation, blessing, command, narrative

===== MITZVOT (COMMANDEMENTS) =====
Extraire les commandements explicites:
- Type: aseh (positif - faire) ou lo_taaseh (negatif - ne pas faire)
- Categorie: mishpatim (lois rationnelles), chukim (statuts), edot (temoignages)
- Domaine: shabbat, kashrut, purity, civil, criminal, temple, prayer, family, agriculture, ethics, idolatry, festivals

===== BENEDICTIONS ET MALEDICTIONS =====
Types: blessing, curse
Categories: patriarchal, priestly, mosaic, covenantal, deathbed, prophetic

===== FORMAT DE REPONSE JSON =====
{{
  "Genesis 1:1": {{
    "divine_names": [
      {{
        "name": "elohim",
        "hebrew": "אלהים",
        "context": "creation",
        "speaker": "narrator",
        "note": "Premier usage du nom Elohim dans la Torah",
        "confidence": 0.95
      }}
    ],
    "mitzvot": [],
    "blessings_curses": []
  }},
  "Genesis 2:3": {{
    "divine_names": [
      {{"name": "elohim", "hebrew": "אלהים", "context": "blessing", "speaker": "narrator", "confidence": 0.95}}
    ],
    "mitzvot": [
      {{
        "text": "Sanctify the Sabbath day",
        "text_hebrew": "ויברך אלהים את יום השביעי ויקדש אתו",
        "type": "aseh",
        "category": "edot",
        "domain": "shabbat",
        "applies_to": "all_israel",
        "rationale": "God rested on the seventh day",
        "confidence": 0.85
      }}
    ],
    "blessings_curses": [
      {{
        "type": "blessing",
        "giver": "God",
        "recipient": "Sabbath",
        "content": "God blessed the seventh day and sanctified it",
        "is_conditional": false,
        "category": "covenantal",
        "is_divine": true,
        "confidence": 0.9
      }}
    ]
  }}
}}

IMPORTANT:
- Extraire UNIQUEMENT ce qui est explicite dans le texte
- Pour les mitzvot, se concentrer sur les commandements clairs
- Distinguer benedictions divines des humaines
- Repondre UNIQUEMENT avec le JSON, sans explication"""

    def parse_response(self, response_text: str, verses_data: List[Dict]) -> Dict[str, Dict]:
        """Parse Claude's response into structured data."""
        results = {v["ref"]: {"divine_names": [], "mitzvot": [], "blessings_curses": []} for v in verses_data}

        try:
            data = self.parse_json_response(response_text)

            for verse_ref, verse_data in data.items():
                if verse_ref not in results:
                    continue

                # Parse divine names
                for dn in verse_data.get("divine_names", []):
                    results[verse_ref]["divine_names"].append(
                        ExtractedDivineName(
                            divine_name=dn.get("name", ""),
                            divine_name_hebrew=dn.get("hebrew"),
                            context_type=dn.get("context"),
                            speaker_type=dn.get("speaker"),
                            theological_note=dn.get("note"),
                            confidence=float(dn.get("confidence", 0.8)),
                        )
                    )

                # Parse mitzvot
                for mtz in verse_data.get("mitzvot", []):
                    results[verse_ref]["mitzvot"].append(
                        ExtractedMitzvah(
                            command_text=mtz.get("text", ""),
                            command_hebrew=mtz.get("text_hebrew"),
                            mitzvah_type=mtz.get("type", "aseh"),
                            category=mtz.get("category"),
                            domain=mtz.get("domain"),
                            applies_to=mtz.get("applies_to"),
                            rationale=mtz.get("rationale"),
                            confidence=float(mtz.get("confidence", 0.8)),
                        )
                    )

                # Parse blessings/curses
                for bc in verse_data.get("blessings_curses", []):
                    results[verse_ref]["blessings_curses"].append(
                        ExtractedBlessing(
                            blessing_type=bc.get("type", "blessing"),
                            giver=bc.get("giver"),
                            recipient=bc.get("recipient"),
                            content=bc.get("content", ""),
                            is_conditional=bc.get("is_conditional", False),
                            condition_text=bc.get("condition"),
                            category=bc.get("category"),
                            is_divine=bc.get("is_divine", False),
                            confidence=float(bc.get("confidence", 0.8)),
                        )
                    )

        except Exception as e:
            logger.warning(f"Failed to parse theological response: {e}")

        return results

    def save_extraction(self, verse: TorahVerse, items: Dict) -> int:
        """Save extracted theological content to database."""
        saved = 0

        # Save divine names
        for dn in items.get("divine_names", []):
            try:
                saved += self._save_divine_name(verse, dn)
            except Exception as e:
                logger.warning(f"Failed to save divine name: {e}")

        # Save mitzvot
        for mtz in items.get("mitzvot", []):
            try:
                saved += self._save_mitzvah(verse, mtz)
            except Exception as e:
                logger.warning(f"Failed to save mitzvah: {e}")

        # Save blessings/curses
        for bc in items.get("blessings_curses", []):
            try:
                saved += self._save_blessing_curse(verse, bc)
            except Exception as e:
                logger.warning(f"Failed to save blessing/curse: {e}")

        return saved

    def _save_divine_name(self, verse: TorahVerse, dn: ExtractedDivineName) -> int:
        """Save a divine name occurrence."""
        # Map divine name type
        try:
            name_type = DivineNameType(dn.divine_name)
        except ValueError:
            name_type = DivineNameType.OTHER

        # Map context type
        context = None
        if dn.context_type:
            try:
                context = ContextType(dn.context_type)
            except ValueError:
                pass

        divine_name = DivineNameOccurrence(
            verse_id=verse.id,
            divine_name=name_type,
            divine_name_hebrew=dn.divine_name_hebrew,
            context_type=context,
            speaker_type=dn.speaker_type,
            theological_note=dn.theological_note,
            confidence=dn.confidence,
        )
        self.db.add(divine_name)
        return 1

    def _save_mitzvah(self, verse: TorahVerse, mtz: ExtractedMitzvah) -> int:
        """Save a mitzvah."""
        # Map mitzvah type
        try:
            mtz_type = MitzvahType(mtz.mitzvah_type)
        except ValueError:
            mtz_type = MitzvahType.POSITIVE

        # Map category
        category = None
        if mtz.category:
            try:
                category = MitzvahCategory(mtz.category)
            except ValueError:
                pass

        # Map domain
        domain = None
        if mtz.domain:
            try:
                domain = MitzvahDomain(mtz.domain)
            except ValueError:
                pass

        mitzvah = Mitzvah(
            verse_id=verse.id,
            command_text=mtz.command_text,
            command_text_hebrew=mtz.command_hebrew,
            mitzvah_type=mtz_type,
            category=category,
            domain=domain,
            applies_to=mtz.applies_to,
            rationale=mtz.rationale,
            confidence=mtz.confidence,
            extraction_source="claude",
        )
        self.db.add(mitzvah)
        return 1

    def _save_blessing_curse(self, verse: TorahVerse, bc: ExtractedBlessing) -> int:
        """Save a blessing or curse."""
        # Map type
        try:
            bc_type = BlessingCurseType(bc.blessing_type)
        except ValueError:
            bc_type = BlessingCurseType.BLESSING

        # Map category
        category = None
        if bc.category:
            try:
                category = BlessingCurseCategory(bc.category)
            except ValueError:
                pass

        # Get giver/recipient IDs
        giver_id = self._get_name_id(bc.giver) if bc.giver else None
        recipient_id = self._get_name_id(bc.recipient) if bc.recipient else None

        blessing = BlessingCurse(
            verse_id=verse.id,
            blessing_type=bc_type,
            category=category,
            giver_id=giver_id,
            giver_name=bc.giver,
            recipient_id=recipient_id,
            recipient_name=bc.recipient,
            content=bc.content,
            is_conditional=bc.is_conditional,
            condition_text=bc.condition_text,
            is_divine=bc.is_divine,
            confidence=bc.confidence,
        )
        self.db.add(blessing)
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
        """Get status of theological extraction."""
        base_status = super().get_extraction_status()

        divine_names_count = self.db.query(DivineNameOccurrence).count()
        mitzvot_count = self.db.query(Mitzvah).count()
        blessings_count = self.db.query(BlessingCurse).count()
        covenants_count = self.db.query(Covenant).count()

        return {
            **base_status,
            "divine_names_extracted": divine_names_count,
            "mitzvot_extracted": mitzvot_count,
            "blessings_curses_extracted": blessings_count,
            "covenants_extracted": covenants_count,
        }


class CovenantExtractionService(BaseExtractionService):
    """Specialized service for extracting covenants (requires broader context)."""

    EXTRACTION_NAME = "covenants"

    def build_prompt(self, verses_data: List[Dict]) -> str:
        """Build prompt for covenant extraction."""
        verses_text = "\n".join(
            f"{i+1}. {v['ref']} | {v['text_english'][:200]}"
            for i, v in enumerate(verses_data)
        )

        return f"""Expert en theologie biblique. Tache: identifier les ALLIANCES (BRIT) dans ce passage.

PASSAGE A ANALYSER:
{verses_text}

===== ALLIANCES A IDENTIFIER =====
- Alliance avec Noe (arc-en-ciel)
- Alliance avec Abraham (circoncision)
- Alliance du Sinai (shabbat, Torah)
- Alliance sacerdotale

===== ELEMENTS D'UNE ALLIANCE =====
- promise: promesse divine
- obligation: obligation humaine
- sign: signe de l'alliance
- ceremony: ceremonie d'etablissement

===== FORMAT JSON =====
{{
  "covenants": [
    {{
      "name": "Covenant with Abraham",
      "party_human": "Abraham",
      "type": "unconditional",
      "sign": "circumcision",
      "verse_start": "Genesis 17:1",
      "verse_end": "Genesis 17:14",
      "summary": "God promises land and descendants",
      "elements": [
        {{"type": "promise", "verse": "Genesis 17:2", "content": "I will multiply you"}},
        {{"type": "obligation", "verse": "Genesis 17:10", "content": "Every male shall be circumcised"}},
        {{"type": "sign", "verse": "Genesis 17:11", "content": "Circumcision as sign of covenant"}}
      ]
    }}
  ]
}}

Si aucune alliance dans ce passage: {{"covenants": []}}"""

    def parse_response(self, response_text: str, verses_data: List[Dict]) -> Dict[str, List]:
        """Parse covenant extraction response."""
        # Covenants span multiple verses, so we return them differently
        results = {"covenants": []}

        try:
            data = self.parse_json_response(response_text)
            results["covenants"] = data.get("covenants", [])
        except Exception as e:
            logger.warning(f"Failed to parse covenant response: {e}")

        return results

    def save_extraction(self, verse: TorahVerse, items: Dict) -> int:
        """Save extracted covenants."""
        saved = 0

        for cov_data in items.get("covenants", []):
            try:
                # Map covenant type
                try:
                    cov_type = CovenantType(cov_data.get("type", "unconditional"))
                except ValueError:
                    cov_type = CovenantType.UNCONDITIONAL

                # Get verse IDs
                start_ref = cov_data.get("verse_start", verse.ref)
                start_verse = self.db.query(TorahVerse).filter(TorahVerse.ref == start_ref).first()
                end_ref = cov_data.get("verse_end", start_ref)
                end_verse = self.db.query(TorahVerse).filter(TorahVerse.ref == end_ref).first()

                # Get party human ID
                party_human = cov_data.get("party_human")
                party_id = None
                if party_human:
                    torah_name = self.db.query(TorahName).filter(TorahName.name_canonical == party_human).first()
                    if torah_name:
                        party_id = torah_name.id

                covenant = Covenant(
                    covenant_name=cov_data.get("name", "Unknown Covenant"),
                    party_human=party_human,
                    party_human_id=party_id,
                    covenant_sign=cov_data.get("sign"),
                    covenant_type=cov_type,
                    verse_start_id=start_verse.id if start_verse else verse.id,
                    verse_end_id=end_verse.id if end_verse else None,
                    summary=cov_data.get("summary"),
                )
                self.db.add(covenant)
                self.db.flush()

                # Save covenant elements
                for elem in cov_data.get("elements", []):
                    elem_verse_ref = elem.get("verse", verse.ref)
                    elem_verse = self.db.query(TorahVerse).filter(TorahVerse.ref == elem_verse_ref).first()

                    element = CovenantElement(
                        covenant_id=covenant.id,
                        verse_id=elem_verse.id if elem_verse else verse.id,
                        element_type=elem.get("type", "promise"),
                        element_content=elem.get("content", ""),
                    )
                    self.db.add(element)

                saved += 1

            except Exception as e:
                logger.warning(f"Failed to save covenant: {e}")

        return saved
