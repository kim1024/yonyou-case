import logging
import logging.handlers
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def setup_logging() -> None:
    """Configure application logging with file rotation and console output."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # app.log — all levels DEBUG and above, daily rotation, keep 30 days
    app_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(LOG_DIR / "app.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(formatter)
    app_handler.suffix = "%Y-%m-%d"

    # error.log — ERROR and above only, daily rotation, keep 30 days
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(LOG_DIR / "error.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.suffix = "%Y-%m-%d"

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)


def get_request_logger() -> logging.Logger:
    """Return the 'app.access' logger used by the request logging middleware."""
    logger = logging.getLogger("app.access")
    logger.setLevel(logging.DEBUG)
    return logger
