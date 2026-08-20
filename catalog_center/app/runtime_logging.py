from __future__ import annotations

import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path


SECRET_PATTERNS = (
    re.compile(
        r"(?i)(password|token|access[_ -]?token|refresh[_ -]?token|authorization|api[_ -]?key|secret|management[_ -]?key|admin[_ -]?key)"
        r"(\s*[:=]\s*)([^\s,;]+)"
    ),
    re.compile(r"(?i)(bearer\s+)([a-z0-9._~+/=-]+)"),
)


def redact(value: object) -> str:
    text = str(value)
    for pattern in SECRET_PATTERNS:
        if pattern.groups == 3:
            text = pattern.sub(r"\1\2***", text)
        else:
            text = pattern.sub(r"\1***", text)
    return text


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return redact(super().format(record))


def configure_logging(data_root: Path, debug: bool = False) -> tuple[logging.Logger, Path]:
    log_dir = data_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "catalog-intelligence.log"
    logger = logging.getLogger("3dprinthub.catalog")
    logger.disabled = False
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
        handler.setFormatter(RedactingFormatter("%(asctime)s %(levelname)s %(threadName)s %(message)s"))
        logger.addHandler(handler)
        if debug:
            console = logging.StreamHandler()
            console.setFormatter(RedactingFormatter("%(asctime)s %(levelname)s %(message)s"))
            logger.addHandler(console)
    return logger, log_path


def close_logging(logger: logging.Logger) -> None:
    """Flush, detach, and close handlers so Windows releases the log file."""
    handlers = list(logger.handlers)
    for handler in handlers:
        logger.removeHandler(handler)
    for handler in handlers:
        try:
            handler.flush()
        finally:
            handler.close()
