"""Centralized logging configuration for MCP client."""

import logging
import sys
from typing import Optional

from rich.logging import RichHandler


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    include_timestamp: bool = True
) -> None:
    """Set up logging configuration for the MCP client.

    Args:
        level: Logging level (default: INFO).
        format_string: Custom format string for log messages.
        include_timestamp: Whether to include timestamp in log format.
    """
    # Use RichHandler for pretty, colorful logging
    rich_handler = RichHandler(
        rich_tracebacks=True,
        show_time=include_timestamp,
        show_path=False,
        log_time_format="[%X]",
    )

    if format_string is None:
        format_string = "%(message)s"

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[rich_handler]
    )

    # Set specific loggers to avoid noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__ of the module).

    Returns:
        Logger instance.
    """
    return logging.getLogger(name) 