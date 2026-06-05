# =============================================================================
# logger.py  –  Application-level audit logger
# Logs every input change, navigation step, scoring event, recommendation, and
# physician action with ISO-8601 timestamps.
# =============================================================================

import logging
import logging.handlers
import os

from config.config import LOG_DATE_FORMAT, LOG_FILE_NAME


_logger: logging.Logger | None = None


def get_logger() -> logging.Logger:
    """Return (and lazily initialise) the application logger."""
    global _logger
    if _logger is None:
        _logger = _create_logger()
    return _logger


def _create_logger() -> logging.Logger:
    logger = logging.getLogger("CDSS_PE")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers when module is re-imported
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s  [%(levelname)-8s]  %(message)s",
        datefmt=LOG_DATE_FORMAT,
    )

    # ── File handler (rotating, max 5 MB × 3 backups) ──
    log_path = os.path.join(os.path.dirname(__file__), LOG_FILE_NAME)
    fh = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info("=" * 70)
    logger.info("CDS PE Logger initialised – session start")
    logger.info("=" * 70)
    return logger


# helper functions

def log_session_start(mrn: str, patient_name: str) -> None:
    log = get_logger()
    log.info(f"SESSION START | MRN={mrn} | Patient='{patient_name}'")


def log_navigation(from_step: int, to_step: int, direction: str) -> None:
    log = get_logger()
    log.info(f"NAVIGATION | {direction.upper()} | Step {from_step} → {to_step}")


def log_data_saved(mrn: str, step: int, field: str, value: object) -> None:
    log = get_logger()
    log.debug(f"DATA_SAVED | MRN={mrn} | Step={step} | {field}={value!r}")


def log_wells_score(mrn: str, score: float, risk: str) -> None:
    log = get_logger()
    log.info(
        f"WELLS_SCORE | MRN={mrn} | Score={score:.1f} | RiskLevel='{risk}'"
    )


def log_recommendation(mrn: str, rec_title: str, strength: str) -> None:
    log = get_logger()
    log.info(
        f"RECOMMENDATION | MRN={mrn} | Title='{rec_title}' | Strength='{strength}'"
    )


def log_physician_decision(
        mrn: str, decision: str, override_reason: str = "", comments: str = ""
) -> None:
    log = get_logger()
    log.info(
        f"PHYSICIAN_DECISION | MRN={mrn} | Decision='{decision}' "
        f"| OverrideReason='{override_reason}' | Comments='{comments[:80]}'"
    )


def log_missing_data(mrn: str, missing_fields: list[str]) -> None:
    log = get_logger()
    log.warning(
        f"MISSING_DATA | MRN={mrn} | Fields={missing_fields}"
    )


def log_db_event(event: str, detail: str = "") -> None:
    log = get_logger()
    log.info(f"DATABASE | {event}" + (f" | {detail}" if detail else ""))


def log_error(context: str, error: Exception) -> None:
    log = get_logger()
    log.error(f"ERROR | {context} | {type(error).__name__}: {error}")
