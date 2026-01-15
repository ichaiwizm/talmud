"""Statistics CLI commands."""
import click

from src.cli.common import (
    with_db, output_result, handle_error,
    COLUMNS, name_row, print_table, print_json,
)
from src.services.stats_service import StatsService
from src.services.search_service import SearchService
from src.utils.table_formatter import print_stats_panel, print_name_detail


@click.command("stats")
@click.option("--book", "-b", help="Filter by book name")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def stats_cmd(db, book: str, as_json: bool):
    """Show detailed statistics about the Torah database."""
    result = StatsService(db).get_global_stats(book)

    if handle_error(result):
        return

    if as_json:
        print_json(result)
        return

    print_stats_panel("Torah Statistics", {
        "Book": result["book"],
        "Chapters": result["chapters"],
        "Verses": f"{result['verses']} ({result['progress_percent']}% processed)",
        "Unique Names": result["unique_names"],
        "Total Occurrences": result["total_occurrences"],
    })

    if result["type_distribution"]:
        total = sum(result["type_distribution"].values())
        rows = [
            [t.upper(), count, f"{count/total*100:.1f}%"]
            for t, count in sorted(result["type_distribution"].items(), key=lambda x: x[1], reverse=True)
        ]
        print_table("Name Types Distribution",
            [("Type", "left"), ("Count", "right"), ("Percentage", "right")], rows)


@click.command("top-names")
@click.option("--limit", "-l", default=20, help="Number of names to show")
@click.option("--type", "-t", "name_type", help="Filter by type")
@click.option("--book", "-b", help="Filter by book name")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def top_names_cmd(db, limit: int, name_type: str, book: str, as_json: bool):
    """Show top names by occurrence count."""
    results = StatsService(db).get_top_names(limit=limit, name_type=name_type, book_name=book)

    if not results:
        click.echo("No names found.")
        return

    title = "Top Names" + (f" ({name_type})" if name_type else "") + (f" in {book}" if book else "")
    output_result(results, as_json, {
        "title": title,
        "columns": COLUMNS["name_basic"],
        "row_mapper": name_row,
        "show_index": True,
    })


@click.command("list-names")
@click.option("--type", "-t", "name_type", help="Filter by type")
@click.option("--book", "-b", help="Filter by book name")
@click.option("--sort", "-s", type=click.Choice(["frequency", "alpha"]), default="frequency")
@click.option("--limit", "-l", default=100, help="Maximum names")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def list_names_cmd(db, name_type: str, book: str, sort: str, limit: int, as_json: bool):
    """List names with optional filtering."""
    results = StatsService(db).list_names(name_type=name_type, book_name=book, sort_by=sort, limit=limit)

    if not results:
        click.echo("No names found.")
        return

    title = "Names" + (f" (type: {name_type})" if name_type else "") + (f" in {book}" if book else "")
    output_result(results, as_json, {
        "title": title,
        "columns": COLUMNS["name_basic"],
        "row_mapper": name_row,
        "show_index": True,
    })


@click.command("show-name")
@click.argument("name")
@click.option("--verses", "-v", is_flag=True, help="Show verses")
@click.option("--limit", "-l", default=10, help="Max verses")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def show_name_cmd(db, name: str, verses: bool, limit: int, as_json: bool):
    """Show detailed information about a name."""
    from src.utils.table_formatter import print_error

    result = SearchService(db).get_name_detail(name)

    if not result:
        print_error(f"Name '{name}' not found.")
        return

    if as_json:
        if not verses:
            result["verses"] = result["verses"][:limit]
        print_json(result)
        return

    verse_data = result["verses"][:limit] if verses else None
    print_name_detail(
        name=result["name"],
        hebrew=result["hebrew"],
        name_type=result["type"],
        occurrences=result["occurrences"],
        first_mention=result["first_mention"],
        verses=verse_data,
    )
    if verses and len(result["verses"]) > limit:
        click.echo(f"\n... and {len(result['verses']) - limit} more verses")


stats_commands = [stats_cmd, top_names_cmd, list_names_cmd, show_name_cmd]
