"""Shoresh Navigator API routes - Hebrew root exploration."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter
from src.db.models.gematria import TorahWord
from src.db.models.linguistic import HebrewRoot, WordRoot, VerbForm

router = APIRouter()

# Semantic field colors for visualization
SEMANTIC_FIELD_COLORS = {
    "creation": "#22c55e",
    "speech": "#3b82f6",
    "movement": "#f59e0b",
    "life": "#10b981",
    "death": "#6b7280",
    "holiness": "#8b5cf6",
    "covenant": "#d4a853",
    "blessing": "#14b8a6",
    "sin": "#ef4444",
    "judgment": "#7c3aed",
    "love": "#ec4899",
    "knowledge": "#06b6d4",
    "power": "#f97316",
    "worship": "#a855f7",
    "nature": "#84cc16",
    "family": "#fb7185",
    "general": "#94a3b8",
}

# Verb form (binyan) descriptions
BINYAN_INFO = {
    "qal": {"name": "Qal (פָּעַל)", "description": "Simple active", "color": "#22c55e"},
    "niphal": {"name": "Niphal (נִפְעַל)", "description": "Simple passive/reflexive", "color": "#3b82f6"},
    "piel": {"name": "Piel (פִּעֵל)", "description": "Intensive active", "color": "#f59e0b"},
    "pual": {"name": "Pual (פֻּעַל)", "description": "Intensive passive", "color": "#8b5cf6"},
    "hiphil": {"name": "Hiphil (הִפְעִיל)", "description": "Causative active", "color": "#ef4444"},
    "hophal": {"name": "Hophal (הָפְעַל)", "description": "Causative passive", "color": "#ec4899"},
    "hitpael": {"name": "Hitpael (הִתְפַּעֵל)", "description": "Reflexive/reciprocal", "color": "#14b8a6"},
    "other": {"name": "Other", "description": "Other forms", "color": "#94a3b8"},
}


@router.get("/roots")
def get_roots(
    search: Optional[str] = Query(None, description="Search by root letters or meaning"),
    semantic_field: Optional[str] = Query(None, description="Filter by semantic field"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """Get list of Hebrew roots with occurrence counts."""
    query = db.query(HebrewRoot)

    if search:
        query = query.filter(
            HebrewRoot.root_letters.ilike(f"%{search}%")
            | HebrewRoot.root_transliteration.ilike(f"%{search}%")
            | HebrewRoot.basic_meaning.ilike(f"%{search}%")
        )

    if semantic_field:
        query = query.filter(HebrewRoot.semantic_field == semantic_field)

    total = query.count()
    roots = query.order_by(desc(HebrewRoot.occurrence_count)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "roots": [
            {
                "id": r.id,
                "letters": r.root_letters,
                "transliteration": r.root_transliteration,
                "meaning": r.basic_meaning,
                "meaning_hebrew": r.basic_meaning_hebrew,
                "occurrence_count": r.occurrence_count,
                "semantic_field": r.semantic_field,
                "color": SEMANTIC_FIELD_COLORS.get(r.semantic_field or "general", "#94a3b8"),
                "related_roots": r.related_roots,
            }
            for r in roots
        ],
    }


@router.get("/root/{root_id}")
def get_root_details(
    root_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed information about a specific root."""
    root = db.query(HebrewRoot).filter(HebrewRoot.id == root_id).first()
    if not root:
        return {"error": "Root not found"}

    # Get word derivations with verse context
    word_roots = (
        db.query(WordRoot, TorahWord, TorahVerse)
        .join(TorahWord, WordRoot.word_id == TorahWord.id)
        .join(TorahVerse, TorahWord.verse_id == TorahVerse.id)
        .filter(WordRoot.root_id == root_id)
        .limit(100)
        .all()
    )

    # Group by verb form
    by_form = {}
    for wr, word, verse in word_roots:
        form = wr.verb_form.value if wr.verb_form else "other"
        if form not in by_form:
            by_form[form] = []
        by_form[form].append({
            "word": word.word_original,
            "word_normalized": word.word_normalized,
            "verse_ref": verse.ref,
            "meaning": wr.word_meaning,
            "gematria": word.gematria_standard,
        })

    # Get unique words
    unique_words = {}
    for wr, word, verse in word_roots:
        if word.word_normalized not in unique_words:
            unique_words[word.word_normalized] = {
                "word": word.word_original,
                "word_normalized": word.word_normalized,
                "count": 0,
                "meaning": wr.word_meaning,
            }
        unique_words[word.word_normalized]["count"] += 1

    # Get related roots details
    related = []
    if root.related_roots:
        related_ids = root.related_roots if isinstance(root.related_roots, list) else []
        for rel_id in related_ids[:5]:
            rel_root = db.query(HebrewRoot).filter(HebrewRoot.id == rel_id).first()
            if rel_root:
                related.append({
                    "id": rel_root.id,
                    "letters": rel_root.root_letters,
                    "meaning": rel_root.basic_meaning,
                })

    return {
        "id": root.id,
        "letters": root.root_letters,
        "transliteration": root.root_transliteration,
        "meaning": root.basic_meaning,
        "meaning_hebrew": root.basic_meaning_hebrew,
        "occurrence_count": root.occurrence_count,
        "semantic_field": root.semantic_field,
        "color": SEMANTIC_FIELD_COLORS.get(root.semantic_field or "general", "#94a3b8"),
        "notes": root.notes,
        "related_roots": related,
        "by_verb_form": {
            form: {
                "count": len(words),
                "info": BINYAN_INFO.get(form, BINYAN_INFO["other"]),
                "examples": words[:5],
            }
            for form, words in by_form.items()
        },
        "unique_words": sorted(
            unique_words.values(),
            key=lambda x: x["count"],
            reverse=True
        )[:20],
    }


@router.get("/words/{root_id}")
def get_root_words(
    root_id: int,
    verb_form: Optional[str] = Query(None, description="Filter by verb form"),
    book: Optional[str] = Query(None, description="Filter by book"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Get words derived from a specific root with verse context."""
    query = (
        db.query(WordRoot, TorahWord, TorahVerse, TorahChapter, TorahBook)
        .join(TorahWord, WordRoot.word_id == TorahWord.id)
        .join(TorahVerse, TorahWord.verse_id == TorahVerse.id)
        .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
        .join(TorahBook, TorahChapter.book_id == TorahBook.id)
        .filter(WordRoot.root_id == root_id)
    )

    if verb_form:
        try:
            vf = VerbForm(verb_form)
            query = query.filter(WordRoot.verb_form == vf)
        except ValueError:
            pass

    if book:
        query = query.filter(TorahBook.name == book)

    results = query.order_by(TorahVerse.id).limit(limit).all()

    return [
        {
            "word": word.word_original,
            "word_normalized": word.word_normalized,
            "verb_form": wr.verb_form.value if wr.verb_form else None,
            "meaning": wr.word_meaning,
            "verse_ref": verse.ref,
            "book": book_obj.name,
            "text_hebrew": verse.text_hebrew,
            "text_english": verse.text_english,
            "gematria": word.gematria_standard,
        }
        for wr, word, verse, chapter, book_obj in results
    ]


@router.get("/semantic-fields")
def get_semantic_fields(db: Session = Depends(get_db)):
    """Get list of semantic fields with root counts."""
    results = (
        db.query(
            HebrewRoot.semantic_field,
            func.count(HebrewRoot.id).label("count"),
            func.sum(HebrewRoot.occurrence_count).label("total_occurrences"),
        )
        .filter(HebrewRoot.semantic_field.isnot(None))
        .group_by(HebrewRoot.semantic_field)
        .order_by(desc("count"))
        .all()
    )

    return [
        {
            "field": field or "general",
            "root_count": count,
            "total_occurrences": total or 0,
            "color": SEMANTIC_FIELD_COLORS.get(field or "general", "#94a3b8"),
        }
        for field, count, total in results
    ]


@router.get("/verb-forms")
def get_verb_forms(db: Session = Depends(get_db)):
    """Get verb form distribution across all roots."""
    results = (
        db.query(
            WordRoot.verb_form,
            func.count(WordRoot.id).label("count"),
        )
        .filter(WordRoot.verb_form.isnot(None))
        .group_by(WordRoot.verb_form)
        .order_by(desc("count"))
        .all()
    )

    return [
        {
            "form": form.value if form else "other",
            "count": count,
            "info": BINYAN_INFO.get(form.value if form else "other", BINYAN_INFO["other"]),
        }
        for form, count in results
    ]


@router.get("/search")
def search_roots(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
):
    """Search roots by letters, transliteration, or meaning."""
    roots = (
        db.query(HebrewRoot)
        .filter(
            HebrewRoot.root_letters.ilike(f"%{q}%")
            | HebrewRoot.root_transliteration.ilike(f"%{q}%")
            | HebrewRoot.basic_meaning.ilike(f"%{q}%")
        )
        .order_by(desc(HebrewRoot.occurrence_count))
        .limit(20)
        .all()
    )

    return [
        {
            "id": r.id,
            "letters": r.root_letters,
            "transliteration": r.root_transliteration,
            "meaning": r.basic_meaning,
            "occurrence_count": r.occurrence_count,
            "semantic_field": r.semantic_field,
            "color": SEMANTIC_FIELD_COLORS.get(r.semantic_field or "general", "#94a3b8"),
        }
        for r in roots
    ]


@router.get("/tree/{root_id}")
def get_root_tree(
    root_id: int,
    db: Session = Depends(get_db),
):
    """Get root and its related roots in a tree structure."""
    root = db.query(HebrewRoot).filter(HebrewRoot.id == root_id).first()
    if not root:
        return {"error": "Root not found"}

    # Build tree structure
    tree = {
        "id": root.id,
        "letters": root.root_letters,
        "transliteration": root.root_transliteration,
        "meaning": root.basic_meaning,
        "occurrence_count": root.occurrence_count,
        "semantic_field": root.semantic_field,
        "color": SEMANTIC_FIELD_COLORS.get(root.semantic_field or "general", "#94a3b8"),
        "children": [],
    }

    # Get related roots
    if root.related_roots:
        related_ids = root.related_roots if isinstance(root.related_roots, list) else []
        for rel_id in related_ids[:10]:
            rel_root = db.query(HebrewRoot).filter(HebrewRoot.id == rel_id).first()
            if rel_root:
                tree["children"].append({
                    "id": rel_root.id,
                    "letters": rel_root.root_letters,
                    "transliteration": rel_root.root_transliteration,
                    "meaning": rel_root.basic_meaning,
                    "occurrence_count": rel_root.occurrence_count,
                    "semantic_field": rel_root.semantic_field,
                    "color": SEMANTIC_FIELD_COLORS.get(rel_root.semantic_field or "general", "#94a3b8"),
                })

    return tree


@router.get("/stats")
def get_shoresh_stats(db: Session = Depends(get_db)):
    """Get overall shoresh statistics."""
    root_count = db.query(HebrewRoot).count()
    word_root_count = db.query(WordRoot).count()

    # Most common roots
    top_roots = (
        db.query(HebrewRoot)
        .order_by(desc(HebrewRoot.occurrence_count))
        .limit(5)
        .all()
    )

    # Semantic field count
    field_count = (
        db.query(HebrewRoot.semantic_field)
        .filter(HebrewRoot.semantic_field.isnot(None))
        .distinct()
        .count()
    )

    return {
        "total_roots": root_count,
        "total_word_mappings": word_root_count,
        "semantic_field_count": field_count,
        "top_roots": [
            {
                "letters": r.root_letters,
                "meaning": r.basic_meaning,
                "count": r.occurrence_count,
            }
            for r in top_roots
        ],
    }


@router.get("/binyanim")
def get_binyanim():
    """Get information about Hebrew verb forms (binyanim)."""
    return [
        {"form": form, **info}
        for form, info in BINYAN_INFO.items()
    ]
