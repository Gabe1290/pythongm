#!/usr/bin/env python3
# ==============================================================================
# CORE PACKAGE: core/__init__.py
# Location: /project_root/core/__init__.py
# ==============================================================================
"""
Location: core/__init__.py

Core functionality and business logic:
- Project management
- File I/O operations
- Configuration management
- Visual programming logic
"""

from .logger import get_logger, configure_logging, enable_debug, disable_debug

__version__ = "1.0.0-rc.10"

try:
    from .ide_window import PyGameMakerIDE
except ImportError:
    PyGameMakerIDE = None  # type: ignore

__all__ = [
    'PyGameMakerIDE',
    'get_logger',
    'configure_logging',
    'enable_debug',
    'disable_debug',
]
