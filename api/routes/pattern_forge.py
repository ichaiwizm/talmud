"""Pattern Forge API routes - Literary structures and patterns."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter
from src.db.models.linguistic import (
    LiteraryStructure,
    LiteraryStructureType,
    FormulaicExpression,
    FormulaOccurrence,
    FormulaType,
)
from src.db.models.enrichment import (
    CrossReference,
    CrossReferenceType,
    RecurringMotif,
    MotifOccurrence,
)

router = APIRouter()

# Structure type colors and icons
STRUCTURE_TYPE_INFO = {
    "chiasmus": {
        "name": "Chiasmus",
        "description": "ABBA mirror pattern",
        "example": "A-B-B'-A'",
        "color": "#06b6d4",
        "icon": "mirror",
    },
    "parallelism": {
        "name": "Parallelism",
        "description": "Parallel matching elements",
        "example": "AB / A'B'",
        "color": "#8b5cf6",
        "icon": "columns",
    },
    "inclusio": {
        "name": "Inclusio",
        "description": "Bookend framing structure",
        "example": "A...A'",
        "color": "#22c55e",
        "icon": "brackets",
    },
    "acrostic": {
        "name": "Acrostic",
        "description": "Alphabetic pattern",
        "example": "א-ב-ג-ד...",
        "color": "#f59e0b",
        "icon": "list-ordered",
    },
    "repetition": {
        "name": "Repetition",
        "description": "Repeated elements",
        "example": "A-A-A",
        "color": "#ef4444",
        "icon": "repeat",
    },
    "sandwich": {
        "name": "Sandwich",
        "description": "ABA intercalation",
        "example": "A-B-A",
        "color": "#ec4899",
        "icon": "layers",
    },
    "staircase": {
        "name": "Staircase",
        "description": "Progressive parallel structure",
        "example": "ABC / A'B'C'",
        "color": "#14b8a6",
        "icon": "stairs",
    },
    "envelope": {
        "name": "Envelope",
        "description": "Wrapping structure",
        "example": "A-B-C-B'-A'",
        "color": "#6366f1",
        "icon": "mail",
    },
    "concatenation": {
        "name": "Concatenation",
        "description": "Chain-linked sections",
        "example": "AB-BC-CD",
        "color": "#f97316",
        "icon": "link",
    },
    "other": {
        "name": "Other",
        "description": "Other patterns",
        "example": "",
        "color": "#94a3b8",
        "icon": "shapes",
    },
}

# Formula type info
FORMULA_TYPE_INFO = {
    "toledot": {
        "name": "Toledot",
        "description": "Genealogical formula",
        "example": "אֵלֶּה תוֹלְדֹת",
        "color": "#d4a853",
    },
    "wayyomer": {
        "name": "Wayyomer",
        "description": "Speech introduction",
        "example": "וַיֹּאמֶר",
        "color": "#3b82f6",
    },
    "blessing": {
        "name": "Blessing",
        "description": "Blessing formula",
        "example": "בָּרוּךְ",
        "color": "#22c55e",
    },
    "covenant": {
        "name": "Covenant",
        "description": "Covenant formula",
        "example": "וַהֲקִמֹתִי אֶת־בְּרִיתִי",
        "color": "#8b5cf6",
    },
    "creation": {
        "name": "Creation",
        "description": "Creation day formula",
        "example": "וַיְהִי־עֶרֶב וַיְהִי־בֹקֶר",
        "color": "#06b6d4",
    },
    "genealogy": {
        "name": "Genealogy",
        "description": "Genealogical listing",
        "example": "וַיְחִי... וַיּוֹלֶד",
        "color": "#f59e0b",
    },
    "narrative_transition": {
        "name": "Transition",
        "description": "Narrative transition",
        "example": "וַיְהִי אַחַר הַדְּבָרִים",
        "color": "#64748b",
    },
    "legal": {
        "name": "Legal",
        "description": "Legal formula",
        "example": "כִּי... / אִם...",
        "color": "#ef4444",
    },
    "summary": {
        "name": "Summary",
        "description": "Summary formula",
        "example": "אֵלֶּה...",
        "color": "#94a3b8",
    },
    "other": {
        "name": "Other",
        "description": "Other formulas",
        "example": "",
        "color": "#71717a",
    },
}

# Cross-reference type info
CROSSREF_TYPE_INFO = {
    "parallel": {
        "name": "Parallel",
        "description": "Similar content",
        "color": "#8b5cf6",
    },
    "quotation": {
        "name": "Quotation",
        "description": "Direct quote",
        "color": "#22c55e",
    },
    "fulfillment": {
        "name": "Fulfillment",
        "description": "Promise fulfilled",
        "color": "#d4a853",
    },
    "thematic": {
        "name": "Thematic",
        "description": "Shared theme",
        "color": "#3b82f6",
    },
    "verbal": {
        "name": "Verbal",
        "description": "Shared vocabulary",
        "color": "#06b6d4",
    },
    "contrast": {
        "name": "Contrast",
        "description": "Opposite content",
        "color": "#ef4444",
    },
    "typology": {
        "name": "Typology",
        "description": "Foreshadowing",
        "color": "#f59e0b",
    },
    "allusion": {
        "name": "Allusion",
        "description": "Indirect reference",
        "color": "#ec4899",
    },
}


@router.get("/structures")
def get_structures(
    structure_type: Optional[str] = Query(None, description="Filter by structure type"),
    book: Optional[str] = Query(None, description="Filter by book"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """Get literary structures."""
    query = db.query(LiteraryStructure)

    if structure_type:
        try:
            st = LiteraryStructureType(structure_type)
            query = query.filter(LiteraryStructure.structure_type == st)
        except ValueError:
            pass

    if book:
        # Filter by book using verse start
        query = (
            query.join(TorahVerse, LiteraryStructure.verse_start_id == TorahVerse.id)
            .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
            .join(TorahBook, TorahChapter.book_id == TorahBook.id)
            .filter(TorahBook.name == book)
        )

    total = query.count()
    structures = query.order_by(LiteraryStructure.verse_start_id).offset(offset).limit(limit).all()

    return {
        "total": total,
        "structures": [
            {
                "id": s.id,
                "type": s.structure_type.value,
                "type_info": STRUCTURE_TYPE_INFO.get(s.structure_type.value, STRUCTURE_TYPE_INFO["other"]),
                "pattern": s.pattern_notation,
                "start_ref": s.verse_start_ref,
                "end_ref": s.verse_end_ref,
                "focal_ref": s.focal_point_ref,
                "description": s.description,
                "elements": s.structural_elements,
                "confidence": s.confidence,
            }
            for s in structures
        ],
    }


@router.get("/structure/{structure_id}")
def get_structure_details(
    structure_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed information about a specific structure."""
    structure = db.query(LiteraryStructure).filter(LiteraryStructure.id == structure_id).first()
    if not structure:
        return {"error": "Structure not found"}

    # Get verses in range
    verses = (
        db.query(TorahVerse)
        .filter(
            TorahVerse.id >= structure.verse_start_id,
            TorahVerse.id <= structure.verse_end_id,
        )
        .order_by(TorahVerse.id)
        .all()
    )

    # Get focal verse if exists
    focal_verse = None
    if structure.focal_point_verse_id:
        fv = db.query(TorahVerse).filter(TorahVerse.id == structure.focal_point_verse_id).first()
        if fv:
            focal_verse = {
                "ref": fv.ref,
                "hebrew": fv.text_hebrew,
                "english": fv.text_english,
            }

    return {
        "id": structure.id,
        "type": structure.structure_type.value,
        "type_info": STRUCTURE_TYPE_INFO.get(structure.structure_type.value, STRUCTURE_TYPE_INFO["other"]),
        "pattern": structure.pattern_notation,
        "start_ref": structure.verse_start_ref,
        "end_ref": structure.verse_end_ref,
        "description": structure.description,
        "elements": structure.structural_elements,
        "notes": structure.notes,
        "scholarly_reference": structure.scholarly_reference,
        "confidence": structure.confidence,
        "focal_verse": focal_verse,
        "verses": [
            {
                "id": v.id,
                "ref": v.ref,
                "hebrew": v.text_hebrew,
                "english": v.text_english,
            }
            for v in verses
        ],
    }


@router.get("/structure-types")
def get_structure_types(db: Session = Depends(get_db)):
    """Get structure type distribution."""
    results = (
        db.query(
            LiteraryStructure.structure_type,
            func.count(LiteraryStructure.id).label("count"),
        )
        .group_by(LiteraryStructure.structure_type)
        .order_by(desc("count"))
        .all()
    )

    return [
        {
            "type": st.value if st else "other",
            "count": count,
            "info": STRUCTURE_TYPE_INFO.get(st.value if st else "other", STRUCTURE_TYPE_INFO["other"]),
        }
        for st, count in results
    ]


@router.get("/formulas")
def get_formulas(
    formula_type: Optional[str] = Query(None, description="Filter by formula type"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """Get formulaic expressions."""
    query = db.query(FormulaicExpression)

    if formula_type:
        try:
            ft = FormulaType(formula_type)
            query = query.filter(FormulaicExpression.formula_type == ft)
        except ValueError:
            pass

    total = query.count()
    formulas = query.order_by(desc(FormulaicExpression.occurrence_count)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "formulas": [
            {
                "id": f.id,
                "hebrew": f.formula_hebrew,
                "english": f.formula_english,
                "transliteration": f.formula_transliteration,
                "type": f.formula_type.value,
                "type_info": FORMULA_TYPE_INFO.get(f.formula_type.value, FORMULA_TYPE_INFO["other"]),
                "function": f.function,
                "occurrence_count": f.occurrence_count,
            }
            for f in formulas
        ],
    }


@router.get("/formula/{formula_id}")
def get_formula_details(
    formula_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Get detailed information about a formula and its occurrences."""
    formula = db.query(FormulaicExpression).filter(FormulaicExpression.id == formula_id).first()
    if not formula:
        return {"error": "Formula not found"}

    # Get occurrences with verse context
    occurrences = (
        db.query(FormulaOccurrence, TorahVerse)
        .join(TorahVerse, FormulaOccurrence.verse_id == TorahVerse.id)
        .filter(FormulaOccurrence.formula_id == formula_id)
        .order_by(TorahVerse.id)
        .limit(limit)
        .all()
    )

    return {
        "id": formula.id,
        "hebrew": formula.formula_hebrew,
        "english": formula.formula_english,
        "transliteration": formula.formula_transliteration,
        "type": formula.formula_type.value,
        "type_info": FORMULA_TYPE_INFO.get(formula.formula_type.value, FORMULA_TYPE_INFO["other"]),
        "function": formula.function,
        "occurrence_count": formula.occurrence_count,
        "pattern_regex": formula.pattern_regex,
        "notes": formula.notes,
        "occurrences": [
            {
                "id": occ.id,
                "verse_ref": verse.ref,
                "verse_hebrew": verse.text_hebrew,
                "verse_english": verse.text_english,
                "surface_form": occ.surface_form,
                "position": occ.position_in_verse,
                "variation_notes": occ.variation_notes,
            }
            for occ, verse in occurrences
        ],
    }


@router.get("/formula-types")
def get_formula_types(db: Session = Depends(get_db)):
    """Get formula type distribution."""
    results = (
        db.query(
            FormulaicExpression.formula_type,
            func.count(FormulaicExpression.id).label("count"),
            func.sum(FormulaicExpression.occurrence_count).label("total_occurrences"),
        )
        .group_by(FormulaicExpression.formula_type)
        .order_by(desc("count"))
        .all()
    )

    return [
        {
            "type": ft.value if ft else "other",
            "count": count,
            "total_occurrences": total or 0,
            "info": FORMULA_TYPE_INFO.get(ft.value if ft else "other", FORMULA_TYPE_INFO["other"]),
        }
        for ft, count, total in results
    ]


@router.get("/cross-references")
def get_cross_references(
    ref_type: Optional[str] = Query(None, description="Filter by reference type"),
    source_book: Optional[str] = Query(None, description="Filter by source book"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """Get cross-references between verses."""
    query = db.query(CrossReference)

    if ref_type:
        try:
            rt = CrossReferenceType(ref_type)
            query = query.filter(CrossReference.reference_type == rt)
        except ValueError:
            pass

    if source_book:
        query = (
            query.join(TorahVerse, CrossReference.source_verse_id == TorahVerse.id)
            .join(TorahChapter, TorahVerse.chapter_id == TorahChapter.id)
            .join(TorahBook, TorahChapter.book_id == TorahBook.id)
            .filter(TorahBook.name == source_book)
        )

    total = query.count()
    refs = query.order_by(CrossReference.source_verse_id).offset(offset).limit(limit).all()

    return {
        "total": total,
        "references": [
            {
                "id": r.id,
                "source_ref": r.source_ref,
                "target_ref": r.target_ref,
                "type": r.reference_type.value,
                "type_info": CROSSREF_TYPE_INFO.get(r.reference_type.value, CROSSREF_TYPE_INFO["parallel"]),
                "similarity_score": r.similarity_score,
                "shared_vocabulary": r.shared_vocabulary,
                "shared_themes": r.shared_themes,
                "is_bidirectional": r.is_bidirectional,
            }
            for r in refs
        ],
    }


@router.get("/cross-reference/{ref_id}")
def get_cross_reference_details(
    ref_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed cross-reference with verse texts."""
    ref = db.query(CrossReference).filter(CrossReference.id == ref_id).first()
    if not ref:
        return {"error": "Cross-reference not found"}

    source_verse = db.query(TorahVerse).filter(TorahVerse.id == ref.source_verse_id).first()
    target_verse = db.query(TorahVerse).filter(TorahVerse.id == ref.target_verse_id).first()

    return {
        "id": ref.id,
        "type": ref.reference_type.value,
        "type_info": CROSSREF_TYPE_INFO.get(ref.reference_type.value, CROSSREF_TYPE_INFO["parallel"]),
        "source": {
            "ref": ref.source_ref,
            "hebrew": source_verse.text_hebrew if source_verse else None,
            "english": source_verse.text_english if source_verse else None,
        },
        "target": {
            "ref": ref.target_ref,
            "hebrew": target_verse.text_hebrew if target_verse else None,
            "english": target_verse.text_english if target_verse else None,
        },
        "similarity_score": ref.similarity_score,
        "shared_vocabulary": ref.shared_vocabulary,
        "shared_themes": ref.shared_themes,
        "explanation": ref.explanation,
        "is_bidirectional": ref.is_bidirectional,
        "confidence": ref.confidence,
    }


@router.get("/crossref-types")
def get_crossref_types(db: Session = Depends(get_db)):
    """Get cross-reference type distribution."""
    results = (
        db.query(
            CrossReference.reference_type,
            func.count(CrossReference.id).label("count"),
        )
        .group_by(CrossReference.reference_type)
        .order_by(desc("count"))
        .all()
    )

    return [
        {
            "type": rt.value if rt else "parallel",
            "count": count,
            "info": CROSSREF_TYPE_INFO.get(rt.value if rt else "parallel", CROSSREF_TYPE_INFO["parallel"]),
        }
        for rt, count in results
    ]


@router.get("/motifs")
def get_motifs(
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """Get recurring motifs."""
    query = db.query(RecurringMotif)

    total = query.count()
    motifs = query.order_by(desc(RecurringMotif.occurrence_count)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "motifs": [
            {
                "id": m.id,
                "name": m.motif_name,
                "name_hebrew": m.motif_name_hebrew,
                "description": m.description,
                "thematic_significance": m.thematic_significance,
                "occurrence_count": m.occurrence_count,
                "first_occurrence": m.first_occurrence_ref,
                "related_motifs": m.related_motifs,
                "examples": m.examples,
            }
            for m in motifs
        ],
    }


@router.get("/motif/{motif_id}")
def get_motif_details(
    motif_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Get detailed motif information with occurrences."""
    motif = db.query(RecurringMotif).filter(RecurringMotif.id == motif_id).first()
    if not motif:
        return {"error": "Motif not found"}

    # Get occurrences with verse context
    occurrences = (
        db.query(MotifOccurrence, TorahVerse)
        .join(TorahVerse, MotifOccurrence.verse_id == TorahVerse.id)
        .filter(MotifOccurrence.motif_id == motif_id)
        .order_by(TorahVerse.id)
        .limit(limit)
        .all()
    )

    # Get related motifs
    related = []
    if motif.related_motifs:
        related_ids = motif.related_motifs if isinstance(motif.related_motifs, list) else []
        for rel_id in related_ids[:5]:
            rel_motif = db.query(RecurringMotif).filter(RecurringMotif.id == rel_id).first()
            if rel_motif:
                related.append({
                    "id": rel_motif.id,
                    "name": rel_motif.motif_name,
                    "occurrence_count": rel_motif.occurrence_count,
                })

    return {
        "id": motif.id,
        "name": motif.motif_name,
        "name_hebrew": motif.motif_name_hebrew,
        "description": motif.description,
        "thematic_significance": motif.thematic_significance,
        "occurrence_count": motif.occurrence_count,
        "first_occurrence": motif.first_occurrence_ref,
        "related_motifs": related,
        "occurrences": [
            {
                "id": occ.id,
                "verse_ref": verse.ref,
                "verse_hebrew": verse.text_hebrew,
                "verse_english": verse.text_english,
                "context": occ.context,
                "significance": occ.significance,
                "variation_notes": occ.variation_notes,
            }
            for occ, verse in occurrences
        ],
    }


@router.get("/stats")
def get_pattern_stats(db: Session = Depends(get_db)):
    """Get overall pattern statistics."""
    structure_count = db.query(LiteraryStructure).count()
    formula_count = db.query(FormulaicExpression).count()
    formula_occurrence_count = db.query(FormulaOccurrence).count()
    crossref_count = db.query(CrossReference).count()
    motif_count = db.query(RecurringMotif).count()
    motif_occurrence_count = db.query(MotifOccurrence).count()

    # Most common structure type
    top_structure = (
        db.query(LiteraryStructure.structure_type, func.count(LiteraryStructure.id).label("count"))
        .group_by(LiteraryStructure.structure_type)
        .order_by(desc("count"))
        .first()
    )

    # Most common formula type
    top_formula = (
        db.query(FormulaicExpression.formula_type, func.count(FormulaicExpression.id).label("count"))
        .group_by(FormulaicExpression.formula_type)
        .order_by(desc("count"))
        .first()
    )

    return {
        "total_structures": structure_count,
        "total_formulas": formula_count,
        "total_formula_occurrences": formula_occurrence_count,
        "total_cross_references": crossref_count,
        "total_motifs": motif_count,
        "total_motif_occurrences": motif_occurrence_count,
        "top_structure_type": {
            "type": top_structure[0].value if top_structure else None,
            "count": top_structure[1] if top_structure else 0,
        } if top_structure else None,
        "top_formula_type": {
            "type": top_formula[0].value if top_formula else None,
            "count": top_formula[1] if top_formula else 0,
        } if top_formula else None,
    }


@router.get("/network")
def get_pattern_network(
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """Get cross-reference network for visualization."""
    refs = (
        db.query(CrossReference)
        .filter(CrossReference.similarity_score.isnot(None))
        .order_by(desc(CrossReference.similarity_score))
        .limit(limit)
        .all()
    )

    # Build nodes and edges
    nodes = {}
    edges = []

    for r in refs:
        # Source node
        if r.source_ref and r.source_ref not in nodes:
            nodes[r.source_ref] = {
                "id": r.source_ref,
                "ref": r.source_ref,
            }
        # Target node
        if r.target_ref and r.target_ref not in nodes:
            nodes[r.target_ref] = {
                "id": r.target_ref,
                "ref": r.target_ref,
            }
        # Edge
        if r.source_ref and r.target_ref:
            edges.append({
                "source": r.source_ref,
                "target": r.target_ref,
                "type": r.reference_type.value,
                "color": CROSSREF_TYPE_INFO.get(r.reference_type.value, {}).get("color", "#94a3b8"),
                "strength": r.similarity_score or 0.5,
            })

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
    }
