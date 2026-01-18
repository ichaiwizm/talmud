"""Journey Atlas API routes - Biblical journeys and locations."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import TorahVerse, TorahBook, TorahChapter
from src.db.models.names import TorahName, NameType, TorahNameOccurrence
from src.db.models.relationships import (
    EntityRelationship,
    RelationshipType,
    RelationshipCategory,
    Event,
    EventType,
    EventParticipant,
    ParticipantRole,
)

router = APIRouter()

# Predefined biblical location coordinates (approximate, for visualization)
# Format: {name: {x: 0-100, y: 0-100, region: str}}
LOCATION_COORDINATES = {
    # Mesopotamia
    "Ur": {"x": 85, "y": 45, "region": "Mesopotamia"},
    "Ur of the Chaldees": {"x": 85, "y": 45, "region": "Mesopotamia"},
    "Haran": {"x": 70, "y": 25, "region": "Mesopotamia"},
    "Babylon": {"x": 80, "y": 40, "region": "Mesopotamia"},
    "Babel": {"x": 80, "y": 40, "region": "Mesopotamia"},

    # Canaan / Israel
    "Canaan": {"x": 45, "y": 45, "region": "Canaan"},
    "Shechem": {"x": 45, "y": 42, "region": "Canaan"},
    "Bethel": {"x": 44, "y": 47, "region": "Canaan"},
    "Ai": {"x": 45, "y": 47, "region": "Canaan"},
    "Hebron": {"x": 43, "y": 55, "region": "Canaan"},
    "Mamre": {"x": 43, "y": 54, "region": "Canaan"},
    "Beer-sheba": {"x": 40, "y": 60, "region": "Canaan"},
    "Beersheba": {"x": 40, "y": 60, "region": "Canaan"},
    "Jerusalem": {"x": 44, "y": 50, "region": "Canaan"},
    "Salem": {"x": 44, "y": 50, "region": "Canaan"},
    "Moriah": {"x": 44, "y": 50, "region": "Canaan"},
    "Jericho": {"x": 47, "y": 48, "region": "Canaan"},
    "Jordan": {"x": 48, "y": 45, "region": "Canaan"},
    "Dead Sea": {"x": 47, "y": 55, "region": "Canaan"},
    "Sodom": {"x": 48, "y": 58, "region": "Canaan"},
    "Gomorrah": {"x": 49, "y": 59, "region": "Canaan"},
    "Negev": {"x": 38, "y": 65, "region": "Canaan"},
    "Luz": {"x": 44, "y": 47, "region": "Canaan"},
    "Peniel": {"x": 50, "y": 42, "region": "Canaan"},
    "Penuel": {"x": 50, "y": 42, "region": "Canaan"},
    "Gilead": {"x": 52, "y": 40, "region": "Canaan"},
    "Dothan": {"x": 45, "y": 38, "region": "Canaan"},

    # Egypt
    "Egypt": {"x": 30, "y": 70, "region": "Egypt"},
    "Goshen": {"x": 35, "y": 65, "region": "Egypt"},
    "Pithom": {"x": 33, "y": 63, "region": "Egypt"},
    "Rameses": {"x": 34, "y": 62, "region": "Egypt"},
    "On": {"x": 32, "y": 68, "region": "Egypt"},
    "Memphis": {"x": 30, "y": 70, "region": "Egypt"},
    "Nile": {"x": 28, "y": 72, "region": "Egypt"},

    # Sinai / Wilderness
    "Sinai": {"x": 40, "y": 80, "region": "Sinai"},
    "Mount Sinai": {"x": 40, "y": 82, "region": "Sinai"},
    "Horeb": {"x": 40, "y": 82, "region": "Sinai"},
    "Red Sea": {"x": 38, "y": 75, "region": "Sinai"},
    "Wilderness of Sin": {"x": 38, "y": 78, "region": "Sinai"},
    "Kadesh": {"x": 38, "y": 68, "region": "Sinai"},
    "Kadesh-barnea": {"x": 38, "y": 68, "region": "Sinai"},
    "Paran": {"x": 42, "y": 72, "region": "Sinai"},
    "Elim": {"x": 36, "y": 76, "region": "Sinai"},
    "Marah": {"x": 35, "y": 74, "region": "Sinai"},
    "Rephidim": {"x": 39, "y": 80, "region": "Sinai"},

    # Trans-Jordan
    "Moab": {"x": 50, "y": 58, "region": "Trans-Jordan"},
    "Edom": {"x": 48, "y": 65, "region": "Trans-Jordan"},
    "Seir": {"x": 48, "y": 65, "region": "Trans-Jordan"},
    "Ammon": {"x": 52, "y": 50, "region": "Trans-Jordan"},
    "Bashan": {"x": 52, "y": 35, "region": "Trans-Jordan"},
    "Mount Nebo": {"x": 50, "y": 52, "region": "Trans-Jordan"},

    # Other
    "Paddan-aram": {"x": 72, "y": 28, "region": "Mesopotamia"},
    "Laban": {"x": 72, "y": 28, "region": "Mesopotamia"},
    "Midian": {"x": 45, "y": 85, "region": "Arabia"},
}

# Major biblical figures and their journey colors
JOURNEY_FIGURES = {
    "Abraham": {"color": "#d4a853", "order": 1},
    "Isaac": {"color": "#b87333", "order": 2},
    "Jacob": {"color": "#4a90d9", "order": 3},
    "Joseph": {"color": "#22c55e", "order": 4},
    "Moses": {"color": "#ef4444", "order": 5},
    "Israel": {"color": "#8b5cf6", "order": 6},
}


@router.get("/locations")
def get_locations(
    region: Optional[str] = Query(None, description="Filter by region"),
    db: Session = Depends(get_db),
):
    """Get all biblical locations with coordinates and verse counts."""
    # Get places from database
    places = (
        db.query(TorahName)
        .filter(TorahName.name_type == NameType.PLACE)
        .all()
    )

    locations = []
    for place in places:
        # Get coordinates if we have them
        coords = LOCATION_COORDINATES.get(place.name_canonical)
        if not coords and place.name_hebrew:
            coords = LOCATION_COORDINATES.get(place.name_hebrew)

        # Count occurrences
        occurrence_count = (
            db.query(TorahNameOccurrence)
            .filter(TorahNameOccurrence.name_id == place.id)
            .count()
        )

        location_data = {
            "id": place.id,
            "name": place.name_canonical,
            "name_hebrew": place.name_hebrew,
            "description": place.description,
            "first_mention": place.first_mention_ref,
            "occurrence_count": occurrence_count,
            "x": coords["x"] if coords else None,
            "y": coords["y"] if coords else None,
            "region": coords["region"] if coords else "Unknown",
            "has_coordinates": coords is not None,
        }

        if region and coords and coords["region"] != region:
            continue

        locations.append(location_data)

    # Sort by occurrence count
    locations.sort(key=lambda x: x["occurrence_count"], reverse=True)

    return locations


@router.get("/journeys")
def get_journeys(
    figure: Optional[str] = Query(None, description="Filter by figure name"),
    db: Session = Depends(get_db),
):
    """Get journey data for major biblical figures."""
    journeys = []

    # Get spatial relationships (TRAVELS_TO, FLEES_TO, etc.)
    spatial_types = [
        RelationshipType.TRAVELS_TO,
        RelationshipType.FLEES_TO,
        RelationshipType.LIVES_IN,
    ]

    for fig_name, fig_data in JOURNEY_FIGURES.items():
        if figure and fig_name.lower() != figure.lower():
            continue

        # Find the person entity
        person = (
            db.query(TorahName)
            .filter(
                TorahName.name_canonical == fig_name,
                TorahName.name_type == NameType.PERSON,
            )
            .first()
        )

        if not person:
            continue

        # Get their spatial relationships
        relationships = (
            db.query(EntityRelationship, TorahName, TorahVerse)
            .join(TorahName, EntityRelationship.target_entity_id == TorahName.id)
            .outerjoin(TorahVerse, EntityRelationship.verse_id == TorahVerse.id)
            .filter(
                EntityRelationship.source_entity_id == person.id,
                EntityRelationship.relationship_type.in_(spatial_types),
            )
            .order_by(TorahVerse.id)
            .all()
        )

        journey_points = []
        for rel, target, verse in relationships:
            coords = LOCATION_COORDINATES.get(target.name_canonical)

            journey_points.append({
                "location_id": target.id,
                "location_name": target.name_canonical,
                "location_hebrew": target.name_hebrew,
                "relationship": rel.relationship_type.value,
                "verse_ref": verse.ref if verse else None,
                "verse_id": verse.id if verse else None,
                "x": coords["x"] if coords else None,
                "y": coords["y"] if coords else None,
                "has_coordinates": coords is not None,
            })

        if journey_points:
            journeys.append({
                "figure": fig_name,
                "figure_id": person.id,
                "color": fig_data["color"],
                "order": fig_data["order"],
                "point_count": len(journey_points),
                "points": journey_points,
            })

    return journeys


@router.get("/events")
def get_location_events(
    location: Optional[str] = Query(None, description="Filter by location name"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
):
    """Get events that occurred at specific locations."""
    query = (
        db.query(Event, TorahName, TorahVerse)
        .outerjoin(TorahName, Event.location_id == TorahName.id)
        .join(TorahVerse, Event.verse_start_id == TorahVerse.id)
    )

    if location:
        query = query.filter(TorahName.name_canonical.ilike(f"%{location}%"))

    if event_type:
        try:
            et = EventType(event_type)
            query = query.filter(Event.event_type == et)
        except ValueError:
            pass

    results = query.order_by(TorahVerse.id).limit(limit).all()

    events = []
    for event, loc, verse in results:
        coords = None
        if loc:
            coords = LOCATION_COORDINATES.get(loc.name_canonical)

        events.append({
            "id": event.id,
            "event_type": event.event_type.value,
            "description": event.description,
            "location": loc.name_canonical if loc else None,
            "location_hebrew": loc.name_hebrew if loc else None,
            "verse_ref": verse.ref,
            "text_preview": verse.text_hebrew[:50] if verse.text_hebrew else None,
            "is_miraculous": event.is_miraculous,
            "divine_involvement": event.divine_involvement,
            "x": coords["x"] if coords else None,
            "y": coords["y"] if coords else None,
        })

    return events


@router.get("/location/{location_id}")
def get_location_details(
    location_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed information about a specific location."""
    location = db.query(TorahName).filter(TorahName.id == location_id).first()
    if not location:
        return {"error": "Location not found"}

    coords = LOCATION_COORDINATES.get(location.name_canonical)

    # Get all verse occurrences
    occurrences = (
        db.query(TorahNameOccurrence, TorahVerse)
        .join(TorahVerse, TorahNameOccurrence.verse_id == TorahVerse.id)
        .filter(TorahNameOccurrence.name_id == location_id)
        .order_by(TorahVerse.id)
        .limit(50)
        .all()
    )

    # Get people who visited/lived here
    visitors = (
        db.query(TorahName, EntityRelationship)
        .join(EntityRelationship, EntityRelationship.source_entity_id == TorahName.id)
        .filter(
            EntityRelationship.target_entity_id == location_id,
            EntityRelationship.relationship_category == RelationshipCategory.SPATIAL,
        )
        .all()
    )

    # Get events at this location
    events = (
        db.query(Event)
        .filter(Event.location_id == location_id)
        .limit(20)
        .all()
    )

    return {
        "id": location.id,
        "name": location.name_canonical,
        "name_hebrew": location.name_hebrew,
        "description": location.description,
        "first_mention": location.first_mention_ref,
        "x": coords["x"] if coords else None,
        "y": coords["y"] if coords else None,
        "region": coords["region"] if coords else "Unknown",
        "occurrence_count": len(occurrences),
        "occurrences": [
            {
                "verse_ref": verse.ref,
                "text_hebrew": verse.text_hebrew,
                "text_english": verse.text_english,
            }
            for occ, verse in occurrences[:10]
        ],
        "visitors": [
            {
                "name": person.name_canonical,
                "relationship": rel.relationship_type.value,
            }
            for person, rel in visitors
        ],
        "events": [
            {
                "type": e.event_type.value,
                "description": e.description,
                "is_miraculous": e.is_miraculous,
            }
            for e in events
        ],
    }


@router.get("/figures")
def get_journey_figures():
    """Get list of major figures with journey data."""
    return [
        {"name": name, "color": data["color"], "order": data["order"]}
        for name, data in sorted(JOURNEY_FIGURES.items(), key=lambda x: x[1]["order"])
    ]


@router.get("/regions")
def get_regions():
    """Get list of biblical regions."""
    regions = set()
    for loc in LOCATION_COORDINATES.values():
        regions.add(loc["region"])
    return sorted(list(regions))


@router.get("/stats")
def get_journey_stats(db: Session = Depends(get_db)):
    """Get journey atlas statistics."""
    place_count = (
        db.query(TorahName)
        .filter(TorahName.name_type == NameType.PLACE)
        .count()
    )

    spatial_rel_count = (
        db.query(EntityRelationship)
        .filter(EntityRelationship.relationship_category == RelationshipCategory.SPATIAL)
        .count()
    )

    journey_event_count = (
        db.query(Event)
        .filter(Event.event_type == EventType.JOURNEY)
        .count()
    )

    located_events = (
        db.query(Event)
        .filter(Event.location_id.isnot(None))
        .count()
    )

    return {
        "total_locations": place_count,
        "locations_with_coords": len(LOCATION_COORDINATES),
        "spatial_relationships": spatial_rel_count,
        "journey_events": journey_event_count,
        "located_events": located_events,
        "tracked_figures": len(JOURNEY_FIGURES),
    }


@router.get("/event-types")
def get_event_types():
    """Get available event types."""
    return [{"type": e.value} for e in EventType]
