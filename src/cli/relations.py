"""Relations CLI commands for co-occurrences and graphs."""
import json
import click

from src.cli.common import (
    with_db, output_result, handle_error, COLUMNS, name_row, print_table, print_json,
)
from src.services.relation_service import RelationService
from src.services.timeline_service import TimelineService


def _print_target_info(target: dict, label: str = "Co-occurrences with"):
    """Print target name header info."""
    click.echo(f"\n{label}: {target['name']} ({target['type']})")
    if target.get("hebrew"):
        click.echo(f"Hebrew: {target['hebrew']}")
    click.echo()


@click.command("co-occurrences")
@click.argument("name")
@click.option("--min-count", "-m", default=1, help="Minimum count")
@click.option("--limit", "-l", default=20, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def co_occurrences_cmd(db, name: str, min_count: int, limit: int, as_json: bool):
    """Find names appearing in the same verses as NAME."""
    result = RelationService(db).get_co_occurrences(name, min_count=min_count, limit=limit)

    if handle_error(result):
        return

    if as_json:
        print_json(result)
        return

    _print_target_info(result["target"])

    if not result["co_occurrences"]:
        click.echo("No co-occurrences found.")
        return

    output_result(result["co_occurrences"], False, {
        "title": "Names appearing together",
        "columns": [("Name", "left"), ("Hebrew", "left"), ("Type", "left"), ("Count", "right")],
        "row_mapper": lambda n: [n["name"], n.get("hebrew") or "-", n["type"], n["count"]],
        "show_index": True,
    })


@click.command("name-pairs")
@click.option("--type", "-t", "name_type", help="Filter by type")
@click.option("--limit", "-l", default=20, help="Max pairs")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def name_pairs_cmd(db, name_type: str, limit: int, as_json: bool):
    """Show most frequent name pairs appearing together."""
    results = RelationService(db).get_name_pairs(name_type=name_type, limit=limit)

    if not results:
        click.echo("No name pairs found.")
        return

    if as_json:
        print_json(results)
        return

    title = "Most Frequent Name Pairs" + (f" ({name_type})" if name_type else "")
    rows = [[p["name1"], p["name2"], p["count"]] for p in results]
    print_table(title, [("Name 1", "left"), ("Name 2", "left"), ("Together", "right")], rows, show_index=True)


@click.command("nearby-names")
@click.argument("name")
@click.option("--radius", "-r", default=3, help="Verses before/after")
@click.option("--limit", "-l", default=20, help="Max results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def nearby_names_cmd(db, name: str, radius: int, limit: int, as_json: bool):
    """Find names within N verses of NAME."""
    result = TimelineService(db).get_nearby_names(name, radius=radius, limit=limit)

    if handle_error(result):
        return

    if as_json:
        print_json(result)
        return

    _print_target_info(result["target"], f"Names near")
    click.echo(f"Radius: {result['radius']} verses\n")

    if not result["nearby_names"]:
        click.echo("No nearby names found.")
        return

    output_result(result["nearby_names"], False, {
        "title": "Nearby names",
        "columns": [("Name", "left"), ("Hebrew", "left"), ("Type", "left"), ("Count", "right")],
        "row_mapper": lambda n: [n["name"], n.get("hebrew") or "-", n["type"], n["count"]],
        "show_index": True,
    })


@click.command("timeline")
@click.argument("name")
@click.option("--limit", "-l", type=int, help="Max occurrences")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def timeline_cmd(db, name: str, limit: int, as_json: bool):
    """Show chronological timeline of NAME appearances."""
    result = TimelineService(db).get_timeline(name, limit=limit)

    if handle_error(result):
        return

    if as_json:
        print_json(result)
        return

    info = result["name"]
    click.echo(f"\nTimeline: {info['canonical']} ({info['type']})")
    if info.get("hebrew"):
        click.echo(f"Hebrew: {info['hebrew']}")
    click.echo(f"Total occurrences: {result['total_occurrences']}")

    if result["by_book"]:
        click.echo("\nBy book:")
        for book, count in result["by_book"].items():
            click.echo(f"  {book}: {count}")
    click.echo()

    if result["timeline"]:
        rows = [[t["ref"], t["surface_form"]] for t in result["timeline"]]
        print_table("Occurrences", [("Reference", "left"), ("Form", "left")], rows, show_index=True)


@click.command("relation-graph")
@click.option("--output", "-o", type=click.Path(), help="Output file")
@click.option("--min-weight", "-w", default=2, help="Minimum edge weight")
@click.option("--type", "-t", "name_type", help="Filter by type")
@with_db
def relation_graph_cmd(db, output: str, min_weight: int, name_type: str):
    """Export co-occurrence graph for visualization."""
    result = RelationService(db).export_graph(min_weight=min_weight, name_type=name_type)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        click.echo(f"Graph exported to {output}")
        click.echo(f"  Nodes: {result['meta']['node_count']}")
        click.echo(f"  Edges: {result['meta']['edge_count']}")
    else:
        print_json(result)


relation_commands = [co_occurrences_cmd, name_pairs_cmd, nearby_names_cmd, timeline_cmd, relation_graph_cmd]
