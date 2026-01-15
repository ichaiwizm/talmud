import json
import re
import subprocess
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict

from src.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class ExtractedName:
    """Name extracted by Claude."""

    name: str
    name_hebrew: Optional[str]
    name_type: str
    confidence: float
    surface_form: str
    surface_form_hebrew: Optional[str]
    notes: Optional[str] = None


@dataclass
class ExtractionResult:
    """Complete extraction result."""

    verse_ref: str
    names: List[ExtractedName]
    raw_response: str
    success: bool
    error: Optional[str] = None


class ClaudeClient:
    """Client for Claude Code CLI (headless mode)."""

    def __init__(self, model: str = None, timeout: int = None):
        self.model = model or settings.claude_model
        self.timeout = timeout or settings.claude_timeout

    def extract_names(
        self,
        verse_ref: str,
        text_hebrew: str,
        text_english: str,
        context_before: List[str],
        context_after: List[str],
    ) -> ExtractionResult:
        """Extract proper names from a verse via Claude CLI."""
        prompt = self._build_extraction_prompt(
            verse_ref, text_hebrew, text_english, context_before, context_after
        )

        try:
            result = subprocess.run(
                [
                    "claude",
                    "-p",
                    prompt,
                    "--model",
                    self.model,
                    "--tools",
                    "",
                    "--output-format",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                logger.error(f"Claude CLI error: {result.stderr}")
                return ExtractionResult(
                    verse_ref=verse_ref,
                    names=[],
                    raw_response=result.stderr,
                    success=False,
                    error=f"CLI error: {result.stderr}",
                )

            # Parse JSON response
            response_data = json.loads(result.stdout)

            # Extract result text from response
            response_text = response_data.get("result", "")
            if not response_text:
                # Alternative format
                content = response_data.get("content", [])
                if content and isinstance(content, list):
                    response_text = content[0].get("text", "")

            # Parse names from response
            names = self._parse_names_response(response_text)

            return ExtractionResult(
                verse_ref=verse_ref,
                names=names,
                raw_response=result.stdout,
                success=True,
            )

        except subprocess.TimeoutExpired:
            return ExtractionResult(
                verse_ref=verse_ref,
                names=[],
                raw_response="",
                success=False,
                error="Timeout",
            )
        except json.JSONDecodeError as e:
            return ExtractionResult(
                verse_ref=verse_ref,
                names=[],
                raw_response=result.stdout if "result" in dir() else "",
                success=False,
                error=f"JSON parse error: {e}",
            )
        except Exception as e:
            return ExtractionResult(
                verse_ref=verse_ref,
                names=[],
                raw_response="",
                success=False,
                error=str(e),
            )

    def _build_extraction_prompt(
        self,
        verse_ref: str,
        text_hebrew: str,
        text_english: str,
        context_before: List[str],
        context_after: List[str],
    ) -> str:
        """Build the extraction prompt."""
        context_before_text = (
            "\n".join(context_before) if context_before else "(debut du texte)"
        )
        context_after_text = (
            "\n".join(context_after) if context_after else "(fin du texte)"
        )

        return f"""Expert en textes bibliques hebraiques. Tache: extraire les noms propres du verset ci-dessous.

VERSET A ANALYSER:
- Reference: {verse_ref}
- Hebreu: {text_hebrew}
- Anglais: {text_english}

CONTEXTE (3 versets avant): {context_before_text}
CONTEXTE (3 versets apres): {context_after_text}

DEFINITION D'UN NOM PROPRE (a extraire):
Un nom propre designe une entite unique et specifique. Dans la Bible, cela inclut:
- Les individus nommes (etres humains avec un prenom)
- Les noms et titres de Dieu (quand ils designent la divinite)
- Les lieux geographiques nommes (villes, regions, pays, montagnes, fleuves)
- Les peuples et nations nommes (groupes ethniques specifiques)
- Les etres celestes nommes (anges avec un nom)

CE QUI N'EST PAS UN NOM PROPRE (a ignorer):
- Les noms communs designant des categories generales: homme, femme, roi, serviteur, fils, fille
- Les elements naturels generiques: terre, ciel, mer, jour, nuit, lumiere, tenebres, eaux
- Les concepts abstraits: bien, mal, vie, mort
- Les descriptions: l'abime, le firmament, la voute celeste

TYPES VALIDES: person, deity, place, people_group, angel

REPONSE EN JSON UNIQUEMENT:
{{"names": [{{"name": "NomCanonique", "name_hebrew": "HebreuSiPresent", "type": "TypeValide", "surface_form": "FormeDansTexte", "surface_form_hebrew": "FormeHebreue", "confidence": 0.9}}]}}

Si aucun nom propre dans ce verset: {{"names": []}}"""

    def _parse_names_response(self, response_text: str) -> List[ExtractedName]:
        """Parse Claude's JSON response."""
        try:
            # Look for JSON block in response
            json_match = re.search(
                r"```json\s*(.*?)\s*```", response_text, re.DOTALL
            )
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to parse directly
                json_str = response_text.strip()

            data = json.loads(json_str)
            names = []

            for item in data.get("names", []):
                names.append(
                    ExtractedName(
                        name=item.get("name", ""),
                        name_hebrew=item.get("name_hebrew"),
                        name_type=item.get("type", "unknown"),
                        confidence=float(item.get("confidence", 0.5)),
                        surface_form=item.get("surface_form", item.get("name", "")),
                        surface_form_hebrew=item.get("surface_form_hebrew"),
                        notes=item.get("notes"),
                    )
                )

            return names

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse names response: {e}")
            return []

    def extract_names_bulk(self, verses: List[Dict]) -> Dict[str, List[ExtractedName]]:
        """Extract names from multiple verses at once.

        Args:
            verses: List of dicts with keys: ref, text_hebrew, text_english

        Returns:
            Dict mapping verse_ref to list of ExtractedName
        """
        prompt = self._build_bulk_prompt(verses)

        try:
            result = subprocess.run(
                [
                    "claude",
                    "-p",
                    prompt,
                    "--model",
                    self.model,
                    "--tools",
                    "",
                    "--output-format",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                logger.error(f"Claude CLI error: {result.stderr}")
                return {v["ref"]: [] for v in verses}

            response_data = json.loads(result.stdout)
            response_text = response_data.get("result", "")
            if not response_text:
                content = response_data.get("content", [])
                if content and isinstance(content, list):
                    response_text = content[0].get("text", "")

            return self._parse_bulk_response(response_text, verses)

        except subprocess.TimeoutExpired:
            logger.error("Bulk extraction timeout")
            return {v["ref"]: [] for v in verses}
        except Exception as e:
            logger.error(f"Bulk extraction error: {e}")
            return {v["ref"]: [] for v in verses}

    def _build_bulk_prompt(self, verses: List[Dict]) -> str:
        """Build prompt for bulk extraction."""
        verses_text = "\n".join(
            f"{i+1}. {v['ref']} | {v['text_hebrew'][:100]} | {v['text_english'][:150]}"
            for i, v in enumerate(verses)
        )

        return f"""Expert en textes bibliques hebraiques. Tache: extraire les noms propres de CHAQUE verset ci-dessous.

VERSETS A ANALYSER ({len(verses)} versets):
{verses_text}

DEFINITION D'UN NOM PROPRE (a extraire):
Un nom propre designe une entite unique et specifique. Dans la Bible, cela inclut:
- Les individus nommes (etres humains avec un prenom)
- Les noms et titres de Dieu (quand ils designent la divinite)
- Les lieux geographiques nommes (villes, regions, pays, montagnes, fleuves)
- Les peuples et nations nommes (groupes ethniques specifiques)
- Les etres celestes nommes (anges avec un nom)

CE QUI N'EST PAS UN NOM PROPRE (a ignorer):
- Les noms communs: homme, femme, roi, serviteur, fils, fille
- Les elements naturels generiques: terre, ciel, mer, jour, nuit
- Les concepts abstraits: bien, mal, vie, mort

TYPES VALIDES: person, deity, place, people_group, angel

REPONSE JSON UNIQUEMENT (un objet par verset):
{{
  "Genesis 1:1": {{"names": [{{"name": "God", "name_hebrew": "אלהים", "type": "deity", "confidence": 0.95}}]}},
  "Genesis 1:2": {{"names": []}},
  ...
}}

IMPORTANT: Reponds UNIQUEMENT avec le JSON, sans explication."""

    def _parse_bulk_response(self, response_text: str, verses: List[Dict]) -> Dict[str, List[ExtractedName]]:
        """Parse bulk response into per-verse results."""
        results = {v["ref"]: [] for v in verses}

        try:
            # Look for JSON block in response
            json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_text.strip()

            data = json.loads(json_str)

            for verse_ref, verse_data in data.items():
                if verse_ref not in results:
                    continue

                names_list = verse_data.get("names", [])
                for item in names_list:
                    results[verse_ref].append(
                        ExtractedName(
                            name=item.get("name", ""),
                            name_hebrew=item.get("name_hebrew"),
                            name_type=item.get("type", "unknown"),
                            confidence=float(item.get("confidence", 0.5)),
                            surface_form=item.get("surface_form", item.get("name", "")),
                            surface_form_hebrew=item.get("surface_form_hebrew"),
                            notes=item.get("notes"),
                        )
                    )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse bulk response: {e}")

        return results
