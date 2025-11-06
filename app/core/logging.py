import logging
import sys
from typing import Any, Dict, Optional

def configure_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
) -> None:
    """Configure logging for the application.

    Args:
        level: The minimum logging level to capture
        format_string: Custom format string for log messages
    """
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

# Configure logging when this module is imported
configure_logging()