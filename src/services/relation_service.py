"""Relation service for name co-occurrences."""
from collections import defaultdict
from sqlalchemy import func, desc
from sqlalchemy.orm import Session, joinedload

from src.db.models.names import TorahName, TorahNameOccurrence


class RelationService:
    """Service for co-occurrence analysis."""

    def __init__(self, db: Session):
        self.db = db

    def _find_name(self, name_query: str) -> TorahName | None:
        return self.db.query(TorahName).filter(TorahName.name_canonical.ilike(f"%{name_query}%")).first()

    def _name_to_dict(self, name: TorahName) -> dict:
        return {"name": name.name_canonical, "hebrew": name.name_hebrew, "type": name.name_type.value}

    def get_co_occurrences(self, name_query: str, min_count: int = 1, limit: int = 20) -> dict:
        """Get names that appear in the same verses as the given name."""
        target = self._find_name(name_query)
        if not target:
            return {"error": f"Name '{name_query}' not found"}

        target_verse_ids = (
            self.db.query(TorahNameOccurrence.verse_id)
            .filter(TorahNameOccurrence.name_id == target.id)
            .scalar_subquery()
        )

        results = (
            self.db.query(TorahName, func.count(TorahNameOccurrence.id).label("count"))
            .join(TorahNameOccurrence)
            .filter(TorahNameOccurrence.verse_id.in_(target_verse_ids))
            .filter(TorahName.id != target.id)
            .group_by(TorahName.id)
            .having(func.count(TorahNameOccurrence.id) >= min_count)
            .order_by(desc("count")).limit(limit).all()
        )

        return {
            "target": self._name_to_dict(target),
            "co_occurrences": [{**self._name_to_dict(n), "count": c} for n, c in results],
        }

    def get_name_pairs(self, name_type: str | None = None, limit: int = 20) -> list[dict]:
        """Get most frequent pairs of names appearing together."""
        query = self.db.query(TorahNameOccurrence).options(joinedload(TorahNameOccurrence.name))
        if name_type:
            query = query.join(TorahName).filter(TorahName.name_type == name_type)

        # Group by verse
        verse_names: dict[int, list] = defaultdict(list)
        for occ in query.all():
            verse_names[occ.verse_id].append(occ.name)

        # Count pairs
        pair_counts: dict[tuple, int] = defaultdict(int)
        for names in verse_names.values():
            if len(names) < 2:
                continue
            unique = list({n.id: n for n in names}.values())
            for i, n1 in enumerate(unique):
                for n2 in unique[i + 1:]:
                    key = (n1.name_canonical, n2.name_canonical) if n1.id < n2.id else (n2.name_canonical, n1.name_canonical)
                    pair_counts[key] += 1

        sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"name1": k[0], "name2": k[1], "count": c} for k, c in sorted_pairs]

    def export_graph(self, min_weight: int = 2, name_type: str | None = None) -> dict:
        """Export co-occurrence data as graph structure."""
        pairs = self.get_name_pairs(name_type=name_type, limit=1000)
        nodes, edges = {}, []

        for pair in pairs:
            if pair["count"] < min_weight:
                continue
            for name in [pair["name1"], pair["name2"]]:
                if name not in nodes:
                    obj = self.db.query(TorahName).filter(TorahName.name_canonical == name).first()
                    if obj:
                        nodes[name] = {"id": name, "label": name, "hebrew": obj.name_hebrew, "type": obj.name_type.value}
            edges.append({"source": pair["name1"], "target": pair["name2"], "weight": pair["count"]})

        return {"nodes": list(nodes.values()), "edges": edges,
                "meta": {"min_weight": min_weight, "node_count": len(nodes), "edge_count": len(edges)}}
