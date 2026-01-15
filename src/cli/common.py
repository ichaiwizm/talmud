"""Common CLI utilities to avoid repetition."""
import functools
import click
from contextlib import contextmanager

from src.db.base import SessionLocal
from src.utils.table_formatter import print_table, print_json, print_error


@contextmanager
def db_session():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def with_db(f):
    """Decorator that injects a database session as first argument."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with db_session() as db:
            return f(db, *args, **kwargs)
    return wrapper


def output_result(data, as_json: bool, table_config: dict | None = None):
    """Output data as JSON or table.

    Args:
        data: Data to output (list of dicts for table, any for JSON)
        as_json: If True, output JSON
        table_config: Dict with 'title', 'columns', 'row_mapper', 'show_index'
    """
    if as_json:
        print_json(data)
        return

    if not table_config or not data:
        return

    rows = [table_config["row_mapper"](item) for item in data]
    print_table(
        table_config.get("title", "Results"),
        table_config["columns"],
        rows,
        show_index=table_config.get("show_index", False),
    )


def handle_error(result: dict) -> bool:
    """Check for error in result dict and print if found.

    Returns True if error was found.
    """
    if "error" in result:
        print_error(result["error"])
        return True
    return False


# Common column definitions
COLUMNS = {
    "name_basic": [
        ("Name", "left"),
        ("Hebrew", "left"),
        ("Type", "left"),
        ("Occurrences", "right"),
    ],
    "name_with_first": [
        ("Name", "left"),
        ("Hebrew", "left"),
        ("Type", "left"),
        ("Occurrences", "right"),
        ("First Mention", "left"),
    ],
    "verse_basic": [
        ("Reference", "left"),
        ("Text", "left"),
    ],
}


def name_row(n: dict) -> list:
    """Map name dict to table row."""
    return [n["name"], n.get("hebrew") or "-", n["type"], n["occurrences"]]


def name_row_with_first(n: dict) -> list:
    """Map name dict to table row with first mention."""
    return [n["name"], n.get("hebrew") or "-", n["type"], n["occurrences"], n.get("first_mention") or "-"]


def truncate(text: str, length: int = 60) -> str:
    """Truncate text with ellipsis."""
    return text[:length] + "..." if len(text) > length else text
