#!/usr/bin/env python3
# ==============================================================================
# LOGGING MODULE: core/logger.py
# Location: /project_root/core/logger.py
# ==============================================================================
"""
Centralized logging configuration for PyGameMaker.

This module provides a consistent logging interface across all PyGameMaker
components. It replaces scattered print() statements with proper logging
that can be configured at runtime.

Usage:
    from core.logger import get_logger
    logger = get_logger(__name__)

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

Configuration:
    Set environment variable PYGM_LOG_LEVEL to: DEBUG, INFO, WARNING, ERROR
    Default is WARNING for production use.
"""

import logging
import os
import sys
from typing import Optional

# Default log level - can be overridden by environment variable
DEFAULT_LOG_LEVEL = logging.WARNING

# Environment variable to control log level
LOG_LEVEL_ENV_VAR = "PYGM_LOG_LEVEL"

# Track if logging has been configured
_logging_configured = False

# Custom formatter with optional emoji support
class PyGMFormatter(logging.Formatter):
    """Custom formatter for PyGameMaker logs."""

    FORMATS = {
        logging.DEBUG: "%(name)s - DEBUG: %(message)s",
        logging.INFO: "%(name)s - %(message)s",
        logging.WARNING: "%(name)s - WARNING: %(message)s",
        logging.ERROR: "%(name)s - ERROR: %(message)s",
        logging.CRITICAL: "%(name)s - CRITICAL: %(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def configure_logging(level: Optional[int] = None, stream=None) -> None:
    """
    Configure the root logger for PyGameMaker.

    Args:
        level: Logging level (e.g., logging.DEBUG). If None, uses environment
               variable PYGM_LOG_LEVEL or defaults to WARNING.
        stream: Output stream (defaults to sys.stdout)
    """
    global _logging_configured

    if level is None:
        env_level = os.environ.get(LOG_LEVEL_ENV_VAR, "").upper()
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        level = level_map.get(env_level, DEFAULT_LOG_LEVEL)

    if stream is None:
        stream = sys.stdout

    # Configure the root logger for pygm namespace
    root_logger = logging.getLogger("pygm")
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Add console handler
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    handler.setFormatter(PyGMFormatter())
    root_logger.addHandler(handler)

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance configured for PyGameMaker

    Example:
        logger = get_logger(__name__)
        logger.debug("This is a debug message")
    """
    global _logging_configured

    if not _logging_configured:
        configure_logging()

    # Normalize the name to use pygm namespace
    if name.startswith("core.") or name.startswith("runtime.") or \
       name.startswith("export.") or name.startswith("editors.") or \
       name.startswith("widgets.") or name.startswith("events.") or \
       name.startswith("actions."):
        logger_name = f"pygm.{name}"
    elif name == "__main__":
        logger_name = "pygm.main"
    else:
        logger_name = f"pygm.{name}"

    return logging.getLogger(logger_name)


def set_log_level(level: int) -> None:
    """
    Change the log level at runtime.

    Args:
        level: New logging level (e.g., logging.DEBUG)
    """
    root_logger = logging.getLogger("pygm")
    root_logger.setLevel(level)
    for handler in root_logger.handlers:
        handler.setLevel(level)


def enable_debug() -> None:
    """Enable debug logging (convenience function)."""
    set_log_level(logging.DEBUG)


def disable_debug() -> None:
    """Disable debug logging, return to WARNING level."""
    set_log_level(logging.WARNING)
