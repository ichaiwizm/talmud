"""Schemas for Torah names."""
from pydantic import BaseModel
from enum import Enum


class NameType(str, Enum):
    """Types of names in the Torah."""
    PERSON = "person"
    DEITY = "deity"
    PLACE = "place"
    PEOPLE_GROUP = "people_group"
    ANGEL = "angel"
    UNKNOWN = "unknown"


class NameSummary(BaseModel):
    """Summary of a name."""
    id: int
    name: str
    hebrew: str | None = None
    type: str
    occurrences: int
    first_mention: str | None = None

    model_config = {"from_attributes": True}


class VerseOccurrence(BaseModel):
    """A verse where a name occurs."""
    ref: str
    text: str
    hebrew: str
    surface_form: str


class NameDetail(BaseModel):
    """Detailed name information."""
    id: int
    name: str
    hebrew: str | None = None
    type: str
    first_mention: str | None = None
    description: str | None = None
    occurrences: int
    verses: list[VerseOccurrence]


class TimelineEntry(BaseModel):
    """Entry in a name's timeline."""
    ref: str
    book: str
    chapter: int
    verse: int
    surface_form: str


class NameTimeline(BaseModel):
    """Chronological timeline of a name."""
    name: str
    hebrew: str | None = None
    total_occurrences: int
    by_book: dict[str, int]
    timeline: list[TimelineEntry]


class CoOccurrence(BaseModel):
    """A name that co-occurs with another."""
    name: str
    hebrew: str | None = None
    type: str
    count: int


class CoOccurrenceResponse(BaseModel):
    """Response for co-occurrence query."""
    target_name: str
    co_occurrences: list[CoOccurrence]


class NamePair(BaseModel):
    """A pair of names that appear together."""
    name1: str
    name2: str
    count: int


class GraphNode(BaseModel):
    """Node in relationship graph."""
    id: str
    label: str
    hebrew: str | None = None
    type: str
    occurrences: int


class GraphEdge(BaseModel):
    """Edge in relationship graph."""
    source: str
    target: str
    weight: int


class GraphResponse(BaseModel):
    """Graph data for visualization."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]
