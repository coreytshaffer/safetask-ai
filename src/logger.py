import logging
import sys
from pathlib import Path


def setup_logger(name: str = "fieldaware") -> logging.Logger:
    """Configures and returns the centralized logger for the FieldAware application."""
    logger = logging.getLogger(name)

    # Only configure if no handlers are present to avoid duplication
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Formatters
        console_formatter = logging.Formatter("%(levelname)s - %(name)s: %(message)s")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console Handler (INFO level)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(console_formatter)

        # File Handler (DEBUG level)
        # Ensure log directory exists
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "fieldaware.log"

        fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(file_formatter)

        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger


# Global logger instance
logger = setup_logger()
