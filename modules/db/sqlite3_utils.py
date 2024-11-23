import sqlite3
from datetime import UTC, datetime

__all__ = ["sqlite3"]


# Custom adapter: Converts Python datetime object to SQLite-compatible string
def datetime_adapter(value):
    return value.isoformat()


# Custom converter: Converts SQLite DATETIME string to Python datetime object
def datetime_converter(value):
    return datetime.fromisoformat(value.decode()).replace(tzinfo=UTC)


# Register the adapter and converter
sqlite3.register_adapter(datetime, datetime_adapter)
sqlite3.register_converter("DATETIME", datetime_converter)
