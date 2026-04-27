from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from app.database import SessionLocal
from app.models.analytics import VisitLog

_logger = logging.getLogger(__name__)
_JSONL_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "visit_logs.jsonl"

# --- Async log queue & background worker ---
_LOG_QUEUE: asyncio.Queue | None = None
_QUEUE_MAXSIZE = 1000
_BATCH_SIZE = 50
_FLUSH_INTERVAL = 5.0  # seconds
_worker_task: asyncio.Task | None = None
_worker_started = False


def _get_queue() -> asyncio.Queue:
    """Return the module-level queue, creating it on first call."""
    global _LOG_QUEUE
    if _LOG_QUEUE is None:
        _LOG_QUEUE = asyncio.Queue(maxsize=_QUEUE_MAXSIZE)
    return _LOG_QUEUE


async def _flush_batch(batch: list[dict]) -> None:
    """Write a batch of log entries to DB and JSONL."""
    if not batch:
        return

    # --- DB write (one session for the whole batch) ---
    try:
        db = SessionLocal()
        try:
            for entry in batch:
                log = VisitLog(**entry)
                db.add(log)
            db.commit()
        except Exception:
            db.rollback()
            _logger.warning("visit_log batch DB write failed (%d entries)", len(batch))
        finally:
            db.close()
    except Exception:
        _logger.warning("visit_log batch DB session creation failed")

    # --- JSONL backup (append each entry) ---
    try:
        _JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_JSONL_PATH, "a", encoding="utf-8") as f:
            for entry in batch:
                backup_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **entry,
                }
                f.write(json.dumps(backup_data, ensure_ascii=False) + "\n")
    except Exception:
        _logger.warning("visit_log JSONL batch write failed (%d entries)", len(batch))


async def _log_worker() -> None:
    """Background coroutine that drains the log queue in batches."""
    queue = _get_queue()
    batch: list[dict] = []

    while True:
        try:
            # Wait for the first item with a flush-interval timeout
            try:
                entry = await asyncio.wait_for(queue.get(), timeout=_FLUSH_INTERVAL)
                batch.append(entry)
            except asyncio.TimeoutError:
                # Nothing arrived within the interval — flush partial batch and loop
                if batch:
                    await _flush_batch(batch)
                    batch = []
                continue
            except asyncio.CancelledError:
                # Shutting down — flush whatever remains and exit
                if batch:
                    await _flush_batch(batch)
                return

            # Drain up to _BATCH_SIZE - 1 more items without blocking
            while len(batch) < _BATCH_SIZE:
                try:
                    entry = queue.get_nowait()
                    batch.append(entry)
                except asyncio.QueueEmpty:
                    break

            # Flush when batch is full
            if len(batch) >= _BATCH_SIZE:
                await _flush_batch(batch)
                batch = []

        except asyncio.CancelledError:
            if batch:
                await _flush_batch(batch)
            return
        except Exception:
            _logger.warning("log_worker unexpected error", exc_info=True)
            if batch:
                await _flush_batch(batch)
                batch = []


def _ensure_worker() -> None:
    """Start the background worker task once (safe to call multiple times)."""
    global _worker_task, _worker_started
    if _worker_started:
        return
    _worker_started = True
    try:
        loop = asyncio.get_running_loop()
        _worker_task = loop.create_task(_log_worker(), name="analytics-log-worker")
    except RuntimeError:
        _worker_started = False  # no running loop; will retry on next request


async def shutdown_log_worker() -> None:
    """Cancel the background worker and flush remaining entries.

    Call this during application shutdown (e.g. in a FastAPI shutdown event).
    """
    global _worker_task, _worker_started
    if _worker_task is not None and not _worker_task.done():
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    _worker_task = None
    _worker_started = False


class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 只记录 /api/ 且不记录 /api/admin/
        path = request.url.path
        if not path.startswith("/api/") or path.startswith("/api/admin/"):
            return await call_next(request)

        # 先读取 body（在 call_next 之前）
        body_bytes = b""
        if request.method == "POST":
            try:
                body_bytes = await request.body()
            except Exception:
                pass

        response = await call_next(request)

        # Build log data (cheap, no I/O)
        try:
            log_data = {
                "endpoint": path,
                "method": request.method,
                "ip_address": request.client.host if request.client else "",
                "user_agent": request.headers.get("user-agent", ""),
            }

            # 解析缓存的 body
            if request.method == "POST" and body_bytes:
                try:
                    data = json.loads(body_bytes)
                    log_data["industry"] = data.get("industry", "")
                    log_data["region"] = data.get("province", "")
                    log_data["enterprise"] = data.get("name", data.get("enterprise", ""))
                    log_data["major"] = data.get("major", "")
                    log_data["hour"] = str(data.get("hour", ""))
                except Exception:
                    pass

            # Enqueue for background processing (non-blocking)
            _ensure_worker()
            try:
                _get_queue().put_nowait(log_data)
            except asyncio.QueueFull:
                _logger.warning("analytics log queue full — dropping entry for %s", path)
        except Exception:
            pass

        return response
