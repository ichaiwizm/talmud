"""Covenant Architect API routes - Biblical covenants architecture."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter, TorahName
from src.db.models.theological import (
    Covenant,
    CovenantElement,
    CovenantType,
    BlessingCurse,
    BlessingCurseType,
    BlessingCurseCategory,
)

router = APIRouter()

# Covenant info and colors
COVENANT_INFO = {
    "noahic": {
        "name": "Noahic Covenant",
        "name_hebrew": "ברית נח",
        "party": "Noah / All Humanity",
        "sign": "Rainbow (קשת)",
        "color": "#60a5fa",
        "icon": "rainbow",
    },
    "abrahamic": {
        "name": "Abrahamic Covenant",
        "name_hebrew": "ברית אברהם",
        "party": "Abraham / His Seed",
        "sign": "Circumcision (מילה)",
        "color": "#d4a853",
        "icon": "star",
    },
    "sinaitic": {
        "name": "Sinaitic Covenant",
        "name_hebrew": "ברית סיני",
        "party": "Israel",
        "sign": "Shabbat (שבת)",
        "color": "#8b5cf6",
        "icon": "scroll",
    },
    "priestly": {
        "name": "Priestly Covenant",
        "name_hebrew": "ברית כהונה",
        "party": "Aaron / Priests",
        "sign": "Salt / Eternal Priesthood",
        "color": "#f59e0b",
        "icon": "crown",
    },
    "land": {
        "name": "Land Covenant",
        "name_hebrew": "ברית הארץ",
        "party": "Israel",
        "sign": "The Land Itself",
        "color": "#22c55e",
        "icon": "map",
    },
}

# Covenant element type info
ELEMENT_TYPE_INFO = {
    "promise": {
        "name": "Promise",
        "name_hebrew": "הבטחה",
        "description": "Divine promise or commitment",
        "color": "#22c55e",
        "icon": "gift",
    },
    "obligation": {
        "name": "Obligation",
        "name_hebrew": "חובה",
        "description": "Human obligation or requirement",
        "color": "#f59e0b",
        "icon": "scroll",
    },
    "sign": {
        "name": "Sign",
        "name_hebrew": "אות",
        "description": "Visible covenant sign",
        "color": "#8b5cf6",
        "icon": "badge",
    },
    "ceremony": {
        "name": "Ceremony",
        "name_hebrew": "טקס",
        "description": "Ritual or ceremony",
        "color": "#ec4899",
        "icon": "flame",
    },
    "condition": {
        "name": "Condition",
        "name_hebrew": "תנאי",
        "description": "Conditional requirement",
        "color": "#ef4444",
        "icon": "alert",
    },
    "blessing": {
        "name": "Blessing",
        "name_hebrew": "ברכה",
        "description": "Promised blessing",
        "color": "#14b8a6",
        "icon": "sparkles",
    },
    "curse": {
        "name": "Curse",
        "name_hebrew": "קללה",
        "description": "Warning or curse for violation",
        "color": "#64748b",
        "icon": "warning",
    },
}

# Blessing/curse category info
BLESSING_CATEGORY_INFO = {
    "patriarchal": {
        "name": "Patriarchal",
        "description": "Blessings from the patriarchs",
        "color": "#d4a853",
    },
    "priestly": {
        "name": "Priestly",
        "description": "Priestly blessings",
        "color": "#f59e0b",
    },
    "mosaic": {
        "name": "Mosaic",
        "description": "Blessings from Moses",
        "color": "#8b5cf6",
    },
    "covenantal": {
        "name": "Covenantal",
        "description": "Covenant blessings/curses",
        "color": "#22c55e",
    },
    "deathbed": {
        "name": "Deathbed",
        "description": "Final blessings before death",
        "color": "#64748b",
    },
    "prophetic": {
        "name": "Prophetic",
        "description": "Prophetic pronouncements",
        "color": "#3b82f6",
    },
}


@router.get("/covenants")
def get_covenants(
    covenant_type: Optional[str] = Query(None, description="Filter by type"),
    party: Optional[str] = Query(None, description="Filter by human party"),
    db: Session = Depends(get_db),
):
    """Get all covenants."""
    query = db.query(Covenant)

    if covenant_type:
        try:
            ct = CovenantType(covenant_type)
            query = query.filter(Covenant.covenant_type == ct)
        except ValueError:
            pass

    if party:
        query = query.filter(Covenant.party_human.ilike(f"%{party}%"))

    covenants = query.order_by(Covenant.verse_start_id).all()

    return [
        {
            "id": c.id,
            "name": c.covenant_name,
            "name_hebrew": c.covenant_name_hebrew,
            "party_divine": c.party_divine,
            "party_human": c.party_human,
            "sign": c.covenant_sign,
            "type": c.covenant_type.value,
            "is_conditional": c.covenant_type == CovenantType.CONDITIONAL,
            "summary": c.summary,
            "confidence": c.confidence,
            "element_count": len(c.elements) if c.elements else 0,
        }
        for c in covenants
    ]


@router.get("/covenant/{covenant_id}")
def get_covenant_details(
    covenant_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed covenant information with elements and verses."""
    covenant = db.query(Covenant).filter(Covenant.id == covenant_id).first()
    if not covenant:
        return {"error": "Covenant not found"}

    # Get verses in range
    verses = []
    if covenant.verse_start_id:
        end_id = covenant.verse_end_id or covenant.verse_start_id
        verse_objs = (
            db.query(TorahVerse)
            .filter(
                TorahVerse.id >= covenant.verse_start_id,
                TorahVerse.id <= end_id,
            )
            .order_by(TorahVerse.id)
            .all()
        )
        verses = [
            {
                "id": v.id,
                "ref": v.ref,
                "hebrew": v.text_hebrew,
                "english": v.text_english,
            }
            for v in verse_objs
        ]

    # Get elements grouped by type
    elements_by_type = {}
    for el in covenant.elements or []:
        el_type = el.element_type
        if el_type not in elements_by_type:
            elements_by_type[el_type] = {
                "type": el_type,
                "type_info": ELEMENT_TYPE_INFO.get(el_type, ELEMENT_TYPE_INFO["promise"]),
                "elements": [],
            }

        # Get verse for this element
        verse = db.query(TorahVerse).filter(TorahVerse.id == el.verse_id).first()
        elements_by_type[el_type]["elements"].append({
            "id": el.id,
            "content": el.element_content,
            "content_hebrew": el.element_content_hebrew,
            "verse_ref": verse.ref if verse else None,
        })

    # Get human party info
    party_info = None
    if covenant.party_human_id:
        person = db.query(TorahName).filter(TorahName.id == covenant.party_human_id).first()
        if person:
            party_info = {
                "id": person.id,
                "name": person.name,
                "name_hebrew": person.name_hebrew,
            }

    return {
        "id": covenant.id,
        "name": covenant.covenant_name,
        "name_hebrew": covenant.covenant_name_hebrew,
        "party_divine": covenant.party_divine,
        "party_human": covenant.party_human,
        "party_info": party_info,
        "sign": covenant.covenant_sign,
        "type": covenant.covenant_type.value,
        "is_conditional": covenant.covenant_type == CovenantType.CONDITIONAL,
        "summary": covenant.summary,
        "elements_by_type": list(elements_by_type.values()),
        "verses": verses,
    }


@router.get("/elements")
def get_covenant_elements(
    element_type: Optional[str] = Query(None, description="Filter by element type"),
    covenant_id: Optional[int] = Query(None, description="Filter by covenant"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Get covenant elements."""
    query = db.query(CovenantElement)

    if element_type:
        query = query.filter(CovenantElement.element_type == element_type)

    if covenant_id:
        query = query.filter(CovenantElement.covenant_id == covenant_id)

    total = query.count()
    elements = query.limit(limit).all()

    return {
        "total": total,
        "elements": [
            {
                "id": el.id,
                "covenant_id": el.covenant_id,
                "type": el.element_type,
                "type_info": ELEMENT_TYPE_INFO.get(el.element_type, ELEMENT_TYPE_INFO["promise"]),
                "content": el.element_content,
                "content_hebrew": el.element_content_hebrew,
            }
            for el in elements
        ],
    }


@router.get("/element-types")
def get_element_types(db: Session = Depends(get_db)):
    """Get element type distribution."""
    results = (
        db.query(
            CovenantElement.element_type,
            func.count(CovenantElement.id).label("count"),
        )
        .group_by(CovenantElement.element_type)
        .order_by(desc("count"))
        .all()
    )

    return [
        {
            "type": et,
            "count": count,
            "info": ELEMENT_TYPE_INFO.get(et, ELEMENT_TYPE_INFO["promise"]),
        }
        for et, count in results
    ]


@router.get("/blessings")
def get_blessings_curses(
    blessing_type: Optional[str] = Query(None, description="Filter: blessing or curse"),
    category: Optional[str] = Query(None, description="Filter by category"),
    giver: Optional[str] = Query(None, description="Filter by giver name"),
    recipient: Optional[str] = Query(None, description="Filter by recipient name"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """Get blessings and curses."""
    query = db.query(BlessingCurse, TorahVerse).join(
        TorahVerse, BlessingCurse.verse_id == TorahVerse.id
    )

    if blessing_type:
        try:
            bt = BlessingCurseType(blessing_type)
            query = query.filter(BlessingCurse.blessing_type == bt)
        except ValueError:
            pass

    if category:
        try:
            cat = BlessingCurseCategory(category)
            query = query.filter(BlessingCurse.category == cat)
        except ValueError:
            pass

    if giver:
        query = query.filter(BlessingCurse.giver_name.ilike(f"%{giver}%"))

    if recipient:
        query = query.filter(BlessingCurse.recipient_name.ilike(f"%{recipient}%"))

    total = query.count()
    results = query.order_by(TorahVerse.id).offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": bc.id,
                "type": bc.blessing_type.value,
                "is_blessing": bc.blessing_type == BlessingCurseType.BLESSING,
                "category": bc.category.value if bc.category else None,
                "category_info": BLESSING_CATEGORY_INFO.get(bc.category.value if bc.category else "", {}),
                "giver": bc.giver_name,
                "recipient": bc.recipient_name,
                "content": bc.content,
                "content_hebrew": bc.content_hebrew,
                "is_conditional": bc.is_conditional,
                "condition": bc.condition_text,
                "is_divine": bc.is_divine,
                "is_prophetic": bc.is_prophetic,
                "verse_ref": verse.ref,
                "verse_hebrew": verse.text_hebrew,
                "verse_english": verse.text_english,
            }
            for bc, verse in results
        ],
    }


@router.get("/blessing-categories")
def get_blessing_categories(db: Session = Depends(get_db)):
    """Get blessing/curse category distribution."""
    results = (
        db.query(
            BlessingCurse.category,
            BlessingCurse.blessing_type,
            func.count(BlessingCurse.id).label("count"),
        )
        .filter(BlessingCurse.category.isnot(None))
        .group_by(BlessingCurse.category, BlessingCurse.blessing_type)
        .order_by(desc("count"))
        .all()
    )

    return [
        {
            "category": cat.value if cat else "unknown",
            "type": bt.value if bt else "unknown",
            "is_blessing": bt == BlessingCurseType.BLESSING if bt else True,
            "count": count,
            "info": BLESSING_CATEGORY_INFO.get(cat.value if cat else "", {}),
        }
        for cat, bt, count in results
    ]


@router.get("/timeline")
def get_covenant_timeline(db: Session = Depends(get_db)):
    """Get covenants in chronological order for timeline view."""
    covenants = (
        db.query(Covenant, TorahVerse)
        .join(TorahVerse, Covenant.verse_start_id == TorahVerse.id)
        .order_by(TorahVerse.id)
        .all()
    )

    return [
        {
            "id": c.id,
            "name": c.covenant_name,
            "name_hebrew": c.covenant_name_hebrew,
            "party_human": c.party_human,
            "sign": c.covenant_sign,
            "type": c.covenant_type.value,
            "is_conditional": c.covenant_type == CovenantType.CONDITIONAL,
            "verse_ref": verse.ref,
            "summary": c.summary,
            "element_count": len(c.elements) if c.elements else 0,
        }
        for c, verse in covenants
    ]


@router.get("/compare")
def compare_covenants(
    covenant_ids: str = Query(..., description="Comma-separated covenant IDs"),
    db: Session = Depends(get_db),
):
    """Compare multiple covenants side by side."""
    ids = [int(x.strip()) for x in covenant_ids.split(",") if x.strip().isdigit()]

    covenants = db.query(Covenant).filter(Covenant.id.in_(ids)).all()

    comparison = []
    for c in covenants:
        # Get elements by type
        elements_by_type = {}
        for el in c.elements or []:
            if el.element_type not in elements_by_type:
                elements_by_type[el.element_type] = []
            elements_by_type[el.element_type].append({
                "content": el.element_content,
                "content_hebrew": el.element_content_hebrew,
            })

        comparison.append({
            "id": c.id,
            "name": c.covenant_name,
            "name_hebrew": c.covenant_name_hebrew,
            "party_human": c.party_human,
            "sign": c.covenant_sign,
            "type": c.covenant_type.value,
            "is_conditional": c.covenant_type == CovenantType.CONDITIONAL,
            "summary": c.summary,
            "elements_by_type": elements_by_type,
        })

    return comparison


@router.get("/stats")
def get_covenant_stats(db: Session = Depends(get_db)):
    """Get overall covenant statistics."""
    covenant_count = db.query(Covenant).count()
    element_count = db.query(CovenantElement).count()
    blessing_count = db.query(BlessingCurse).filter(
        BlessingCurse.blessing_type == BlessingCurseType.BLESSING
    ).count()
    curse_count = db.query(BlessingCurse).filter(
        BlessingCurse.blessing_type == BlessingCurseType.CURSE
    ).count()

    # Covenant type distribution
    type_dist = (
        db.query(Covenant.covenant_type, func.count(Covenant.id))
        .group_by(Covenant.covenant_type)
        .all()
    )

    return {
        "total_covenants": covenant_count,
        "total_elements": element_count,
        "total_blessings": blessing_count,
        "total_curses": curse_count,
        "type_distribution": {
            ct.value if ct else "unknown": count
            for ct, count in type_dist
        },
    }


@router.get("/structure/{covenant_id}")
def get_covenant_structure(
    covenant_id: int,
    db: Session = Depends(get_db),
):
    """Get covenant structure for visualization."""
    covenant = db.query(Covenant).filter(Covenant.id == covenant_id).first()
    if not covenant:
        return {"error": "Covenant not found"}

    # Build structure for visualization
    nodes = [
        {
            "id": "covenant",
            "type": "covenant",
            "label": covenant.covenant_name,
            "color": "#d4a853",
        },
        {
            "id": "divine",
            "type": "party",
            "label": covenant.party_divine,
            "color": "#8b5cf6",
        },
        {
            "id": "human",
            "type": "party",
            "label": covenant.party_human or "Unknown",
            "color": "#22c55e",
        },
    ]

    edges = [
        {"source": "divine", "target": "covenant", "label": "Initiates"},
        {"source": "human", "target": "covenant", "label": "Receives"},
    ]

    # Add sign if exists
    if covenant.covenant_sign:
        nodes.append({
            "id": "sign",
            "type": "sign",
            "label": covenant.covenant_sign,
            "color": "#f59e0b",
        })
        edges.append({"source": "covenant", "target": "sign", "label": "Sign"})

    # Add elements
    for el in covenant.elements or []:
        el_id = f"element_{el.id}"
        info = ELEMENT_TYPE_INFO.get(el.element_type, ELEMENT_TYPE_INFO["promise"])
        nodes.append({
            "id": el_id,
            "type": el.element_type,
            "label": el.element_content[:50] + "..." if len(el.element_content) > 50 else el.element_content,
            "color": info["color"],
        })
        edges.append({"source": "covenant", "target": el_id, "label": info["name"]})

    return {
        "covenant": {
            "id": covenant.id,
            "name": covenant.covenant_name,
            "name_hebrew": covenant.covenant_name_hebrew,
        },
        "nodes": nodes,
        "edges": edges,
    }
