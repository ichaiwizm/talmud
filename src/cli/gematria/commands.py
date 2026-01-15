"""Gematria calculation and search CLI commands."""

import click

from src.cli.common import with_db, truncate
from src.utils.table_formatter import print_table, print_json, print_stats_panel
from src.utils.hebrew import calculate_all, GematriaMethod
from src.services.gematria import (
    search_words_by_gematria,
    search_verses_by_gematria,
    find_gematria_matches,
)


@click.command("gematria")
@click.argument("text")
@click.option(
    "--method", "-m",
    type=click.Choice(["standard", "katan", "ordinal", "atbash"]),
    default="standard",
    help="Gematria calculation method",
)
@click.option("--all-methods", "-a", is_flag=True, help="Show all methods")
def gematria_cmd(text: str, method: str, all_methods: bool):
    """Calculate gematria value for Hebrew TEXT."""
    results = calculate_all(text)

    if all_methods:
        print_stats_panel(f"Gematria: {text}", {
            "Standard (Mispar Gadol)": results["standard"],
            "Katan (petit)": results["katan"],
            "Ordinal (1-22)": results["ordinal"],
            "Atbash": results["atbash"],
        })
    else:
        value = results[method]
        click.echo(f"{text} = {value} ({method})")


@click.command("gematria-search")
@click.argument("value", type=int)
@click.option(
    "--method", "-m",
    type=click.Choice(["standard", "katan", "ordinal", "atbash"]),
    default="standard",
    help="Gematria method",
)
@click.option(
    "--type", "-t", "search_type",
    type=click.Choice(["words", "verses"]),
    default="words",
    help="Search for words or verses",
)
@click.option("--book", "-b", help="Filter by book name")
@click.option("--limit", "-l", default=50, help="Maximum results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def gematria_search_cmd(
    db, value: int, method: str, search_type: str,
    book: str, limit: int, as_json: bool
):
    """Search for words/verses with gematria VALUE."""
    if search_type == "words":
        results = search_words_by_gematria(db, value, method, book, limit)

        if as_json:
            print_json(results)
            return

        if not results:
            click.echo(f"No words found with {method} gematria = {value}")
            return

        title = f"Words with {method} gematria = {value}"
        if book:
            title += f" in {book}"

        rows = [
            [r["word"], r["verse_ref"], truncate(r["verse_text_english"], 50)]
            for r in results
        ]
        print_table(title, [
            ("Word", "left"),
            ("Verse", "left"),
            ("Text", "left"),
        ], rows, show_index=True)

    else:
        results = search_verses_by_gematria(db, value, method, book, limit)

        if as_json:
            print_json(results)
            return

        if not results:
            click.echo(f"No verses found with total {method} gematria = {value}")
            return

        title = f"Verses with total {method} gematria = {value}"
        rows = [
            [r["ref"], r["word_count"], truncate(r["text_english"], 50)]
            for r in results
        ]
        print_table(title, [
            ("Reference", "left"),
            ("Words", "right"),
            ("Text", "left"),
        ], rows, show_index=True)

    if len(results) == limit:
        click.echo(f"\n(Showing first {limit} results. Use --limit for more.)")


@click.command("gematria-match")
@click.argument("text")
@click.option(
    "--method", "-m",
    type=click.Choice(["standard", "katan", "ordinal", "atbash"]),
    default="standard",
    help="Gematria method",
)
@click.option(
    "--type", "-t", "search_type",
    type=click.Choice(["words", "verses"]),
    default="words",
    help="Search for matching words or verses",
)
@click.option("--book", "-b", help="Filter by book name")
@click.option("--limit", "-l", default=30, help="Maximum results")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def gematria_match_cmd(
    db, text: str, method: str, search_type: str,
    book: str, limit: int, as_json: bool
):
    """Find words/verses matching the gematria of Hebrew TEXT."""
    result = find_gematria_matches(db, text, method, search_type, book, limit)

    if as_json:
        print_json(result)
        return

    click.echo(f"\n'{text}' has {method} gematria = {result['calculated_value']}")
    click.echo(f"Found {result['match_count']} matching {search_type}:\n")

    matches = result["matches"]
    if search_type == "words":
        rows = [
            [m["word"], m["verse_ref"], truncate(m["verse_text_english"], 50)]
            for m in matches
        ]
        print_table(f"Matches for '{text}'", [
            ("Word", "left"),
            ("Verse", "left"),
            ("Text", "left"),
        ], rows, show_index=True)
    else:
        rows = [
            [m["ref"], m["word_count"], truncate(m["text_english"], 50)]
            for m in matches
        ]
        print_table("Matching Verses", [
            ("Reference", "left"),
            ("Words", "right"),
            ("Text", "left"),
        ], rows, show_index=True)


# Export commands
user_commands = [gematria_cmd, gematria_search_cmd, gematria_match_cmd]
