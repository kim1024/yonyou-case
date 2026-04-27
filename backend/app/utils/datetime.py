import logging
from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.config import settings

_logger = logging.getLogger(__name__)


def _resolve_server_timezone():
    tz_name = settings.get("server", {}).get("timezone")
    if tz_name:
        try:
            return ZoneInfo(tz_name), tz_name
        except ZoneInfoNotFoundError:
            _logger.warning("Invalid server.timezone %r, fallback to system local timezone", tz_name)

    local_tz = datetime.now().astimezone().tzinfo or timezone.utc
    return local_tz, getattr(local_tz, "key", str(local_tz))


SERVER_TIMEZONE, SERVER_TIMEZONE_NAME = _resolve_server_timezone()


def ensure_utc(dt: datetime | None) -> datetime | None:
    """Normalize a datetime to UTC-aware."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def utc_isoformat(dt: datetime | None) -> str | None:
    """Serialize datetime for API output in server timezone.

    Naive datetimes from DB are treated as UTC.
    """
    utc_dt = ensure_utc(dt)
    if utc_dt is None:
        return None
    return utc_dt.astimezone(SERVER_TIMEZONE).isoformat()


def parse_date_from_server_tz(value: str) -> datetime:
    """Parse date/datetime string as server timezone, then convert to UTC-aware."""
    raw = (value or "").strip()
    if not raw:
        raise ValueError("empty date")

    if "T" in raw or " " in raw:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=SERVER_TIMEZONE)
        else:
            dt = dt.astimezone(SERVER_TIMEZONE)
    else:
        d = date.fromisoformat(raw)
        dt = datetime.combine(d, time.min, tzinfo=SERVER_TIMEZONE)

    return dt.astimezone(timezone.utc)


def day_range_utc_by_server_tz(day_value: str) -> tuple[datetime, datetime]:
    """Get [start, end) UTC range for one day in server timezone."""
    start_utc = parse_date_from_server_tz(day_value)
    start_local = start_utc.astimezone(SERVER_TIMEZONE).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def server_today_start_utc(now_utc: datetime | None = None) -> datetime:
    """Today's midnight in server timezone, represented in UTC."""
    utc_now = now_utc or datetime.now(timezone.utc)
    local_now = utc_now.astimezone(SERVER_TIMEZONE)
    local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    return local_start.astimezone(timezone.utc)
