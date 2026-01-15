"""Search CLI commands."""
import click

from src.cli.common import (
    with_db, output_result, COLUMNS, name_row_with_first, truncate, print_table, print_json,
)
from src.services.search_service import SearchService


@click.command("search-name")
@click.argument("query")
@click.option("--exact", "-e", is_flag=True, help="Match exactly")
@click.option("--hebrew", "-h", is_flag=True, help="Also search Hebrew")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def search_name_cmd(db, query: str, exact: bool, hebrew: bool, as_json: bool):
    """Search for names matching QUERY."""
    results = SearchService(db).search_name(query, exact=exact, include_hebrew=hebrew)

    if not results:
        click.echo(f"No names found matching '{query}'.")
        return

    output_result(results, as_json, {
        "title": f"Names matching '{query}'",
        "columns": COLUMNS["name_with_first"],
        "row_mapper": name_row_with_first,
        "show_index": True,
    })


@click.command("find-verses")
@click.option("--name", "-n", required=True, help="Name to search for")
@click.option("--book", "-b", help="Filter by book")
@click.option("--limit", "-l", default=50, help="Max verses")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def find_verses_cmd(db, name: str, book: str, limit: int, as_json: bool):
    """Find all verses containing a name."""
    results = SearchService(db).find_verses_by_name(name, book_name=book, limit=limit)

    if not results:
        click.echo(f"No verses found containing '{name}'.")
        return

    if as_json:
        print_json(results)
        return

    title = f"Verses containing '{name}'" + (f" in {book}" if book else "")
    rows = [[v["ref"], v["surface_form"], truncate(v["text_english"])] for v in results]
    print_table(title, [("Reference", "left"), ("Form", "left"), ("Text", "left")], rows, show_index=True)

    if len(results) == limit:
        click.echo(f"\n(Showing first {limit} results. Use --limit to see more.)")


@click.command("search-verse")
@click.argument("query")
@click.option("--book", "-b", help="Filter by book")
@click.option("--hebrew", "-h", is_flag=True, help="Search Hebrew text")
@click.option("--limit", "-l", default=50, help="Max verses")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def search_verse_cmd(db, query: str, book: str, hebrew: bool, limit: int, as_json: bool):
    """Search for verses containing QUERY text."""
    results = SearchService(db).search_verses(query, book_name=book, search_hebrew=hebrew, limit=limit)

    if not results:
        click.echo(f"No verses found containing '{query}'.")
        return

    if as_json:
        print_json(results)
        return

    title = f"Verses containing '{query}'" + (f" in {book}" if book else "")
    text_field = "text_hebrew" if hebrew else "text_english"
    rows = [[v["ref"], truncate(v[text_field], 80)] for v in results]
    print_table(title, COLUMNS["verse_basic"], rows, show_index=True)

    if len(results) == limit:
        click.echo(f"\n(Showing first {limit} results. Use --limit to see more.)")


search_commands = [search_name_cmd, find_verses_cmd, search_verse_cmd]
