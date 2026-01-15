"""Gematria administration CLI commands."""

import click

from src.cli.common import with_db
from src.utils.table_formatter import print_table, print_json, print_stats_panel
from src.services.gematria import (
    populate_all_words,
    get_population_status,
    get_gematria_stats,
)


@click.command("populate-words")
@click.option("--limit", "-l", type=int, help="Maximum verses to process")
@click.option("--book", "-b", help="Process only this book")
@with_db
def populate_words_cmd(db, limit: int, book: str):
    """Populate the torah_words table with gematria values."""
    click.echo("Populating words table...")

    result = populate_all_words(db, limit=limit, book_name=book)

    click.echo(f"Verses processed: {result['verses_processed']}")
    click.echo(f"Words added: {result['words_added']}")


@click.command("gematria-status")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def gematria_status_cmd(db, as_json: bool):
    """Show gematria word population status."""
    status = get_population_status(db)

    if as_json:
        print_json(status)
        return

    print_stats_panel("Gematria Population Status", {
        "Total Verses": status["total_verses"],
        "Verses Populated": f"{status['verses_populated']} ({status['progress_percent']}%)",
        "Pending": status["pending"],
        "Total Words": status["total_words"],
    })


@click.command("gematria-stats")
@click.option("--book", "-b", help="Filter by book name")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@with_db
def gematria_stats_cmd(db, book: str, as_json: bool):
    """Show gematria statistics."""
    stats = get_gematria_stats(db, book_name=book)

    if as_json:
        print_json(stats)
        return

    print_stats_panel("Gematria Statistics", {
        "Book": stats["book"],
        "Total Words": stats["total_words"],
        "Verses Populated": f"{stats['verses_populated']}/{stats['total_verses']} "
                           f"({stats['population_percent']}%)",
    })

    if stats["top_gematria_values"]:
        click.echo()
        rows = [[v["value"], v["count"]] for v in stats["top_gematria_values"]]
        print_table(
            "Most Common Gematria Values (Standard)",
            [("Value", "right"), ("Count", "right")],
            rows,
            show_index=True,
        )


# Export commands
admin_commands = [populate_words_cmd, gematria_status_cmd, gematria_stats_cmd]
