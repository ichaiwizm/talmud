"""Table formatting utilities using Rich."""
import json
from typing import Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_table(
    title: str,
    columns: list[tuple[str, str]],  # (name, justify)
    rows: list[list[Any]],
    show_index: bool = False,
) -> None:
    """Print a formatted table.

    Args:
        title: Table title
        columns: List of (column_name, justify) tuples
        rows: List of row data
        show_index: Whether to show row numbers
    """
    table = Table(title=title, show_header=True, header_style="bold cyan")

    if show_index:
        table.add_column("#", justify="right", style="dim")

    for name, justify in columns:
        table.add_column(name, justify=justify)

    for i, row in enumerate(rows, 1):
        str_row = [str(cell) for cell in row]
        if show_index:
            table.add_row(str(i), *str_row)
        else:
            table.add_row(*str_row)

    console.print(table)


def print_stats_panel(title: str, stats: dict[str, Any]) -> None:
    """Print statistics in a panel format.

    Args:
        title: Panel title
        stats: Dictionary of stat_name -> value
    """
    lines = []
    for key, value in stats.items():
        if isinstance(value, dict):
            lines.append(f"[bold]{key}:[/bold]")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        else:
            lines.append(f"[bold]{key}:[/bold] {value}")

    panel = Panel("\n".join(lines), title=title, border_style="cyan")
    console.print(panel)


def print_name_detail(
    name: str,
    hebrew: str | None,
    name_type: str,
    occurrences: int,
    first_mention: str | None,
    verses: list[dict] | None = None,
) -> None:
    """Print detailed information about a name.

    Args:
        name: Canonical name
        hebrew: Hebrew form
        name_type: Type of name
        occurrences: Number of occurrences
        first_mention: First verse reference
        verses: Optional list of verse occurrences
    """
    text = Text()
    text.append(f"{name}", style="bold green")
    if hebrew:
        text.append(f" ({hebrew})", style="yellow")
    text.append(f"\n")
    text.append(f"Type: ", style="bold")
    text.append(f"{name_type}\n", style="magenta")
    text.append(f"Occurrences: ", style="bold")
    text.append(f"{occurrences}\n", style="cyan")
    if first_mention:
        text.append(f"First mention: ", style="bold")
        text.append(f"{first_mention}\n", style="dim")

    panel = Panel(text, border_style="green")
    console.print(panel)

    if verses:
        print_table(
            f"Verses containing {name}",
            [("Reference", "left"), ("Text (excerpt)", "left")],
            [[v["ref"], v["text"][:80] + "..." if len(v["text"]) > 80 else v["text"]] for v in verses],
            show_index=True,
        )


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    console.print_json(json.dumps(data, ensure_ascii=False, indent=2))


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]Success:[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")
