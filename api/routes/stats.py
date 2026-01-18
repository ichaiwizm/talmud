"""Stats routes."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter, TorahName
from src.db.models.theological import DivineNameOccurrence, Mitzvah, Covenant, BlessingCurse
from src.db.models.enrichment import VerseSentiment, CharacterEmotion, CrossReference

router = APIRouter()


@router.get("")
def get_stats(db: Session = Depends(get_db)):
    """Get overall database statistics."""
    return {
        "verses": db.query(TorahVerse).count(),
        "books": db.query(TorahBook).count(),
        "names": db.query(TorahName).count(),
        "divine_names": db.query(DivineNameOccurrence).count(),
        "mitzvot": db.query(Mitzvah).count(),
        "covenants": db.query(Covenant).count(),
        "blessings_curses": db.query(BlessingCurse).count(),
        "verse_sentiments": db.query(VerseSentiment).count(),
        "character_emotions": db.query(CharacterEmotion).count(),
        "cross_references": db.query(CrossReference).count(),
    }


@router.get("/interfaces")
def get_interfaces():
    """Get available visualization interfaces."""
    return [
        {
            "id": "divine-observatory",
            "name": "Divine Name Observatory",
            "description": "Analyse l'usage des noms divins",
            "icon": "star",
            "color": "#D4AF37",
            "ready": True,
        },
        {
            "id": "constellation",
            "name": "Torah Constellation",
            "description": "Versets comme étoiles dans un cosmos",
            "icon": "sparkles",
            "color": "#6366F1",
            "ready": True,
        },
        {
            "id": "living-scroll",
            "name": "Living Scroll",
            "description": "Texte qui respire et s'anime",
            "icon": "scroll",
            "color": "#8B5CF6",
            "ready": True,
        },
        {
            "id": "emotional-topology",
            "name": "Emotional Topology",
            "description": "Terrain 3D des émotions",
            "icon": "mountain",
            "color": "#10B981",
            "ready": False,
        },
        {
            "id": "voice-chamber",
            "name": "Voice Chamber",
            "description": "Théâtre des dialogues",
            "icon": "message-circle",
            "color": "#F59E0B",
            "ready": True,
        },
        {
            "id": "journey-atlas",
            "name": "Journey Atlas",
            "description": "Carte des voyages patriarcaux",
            "icon": "map",
            "color": "#3B82F6",
            "ready": False,
        },
        {
            "id": "shoresh-navigator",
            "name": "Shoresh Navigator",
            "description": "Exploration des racines hébraïques",
            "icon": "git-branch",
            "color": "#EC4899",
            "ready": False,
        },
        {
            "id": "pattern-forge",
            "name": "Pattern Forge",
            "description": "Structures littéraires",
            "icon": "layers",
            "color": "#8B5CF6",
            "ready": False,
        },
        {
            "id": "covenant-architect",
            "name": "Covenant Architect",
            "description": "Architecture des alliances",
            "icon": "building",
            "color": "#0EA5E9",
            "ready": False,
        },
        {
            "id": "gematria-lab",
            "name": "GematriaLab",
            "description": "L'atelier de numérologie sacrée",
            "icon": "calculator",
            "color": "#D4A853",
            "ready": True,
        },
        {
            "id": "blessing-flow",
            "name": "Blessing Flow",
            "description": "Flux des bénédictions",
            "icon": "workflow",
            "color": "#F97316",
            "ready": False,
        },
        {
            "id": "emotion-timeline",
            "name": "Emotion Timeline",
            "description": "Arcs émotionnels",
            "icon": "activity",
            "color": "#EF4444",
            "ready": False,
        },
    ]
