from datetime import datetime, timezone


def utc_isoformat(dt: datetime | None) -> str | None:
    """Serialize a datetime as UTC ISO 8601 string with +00:00 suffix.

    Naive datetimes from the database are assumed to be UTC (PostgreSQL NOW() returns UTC).
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()
