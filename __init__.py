# ==============================================================================
# MAIN PROJECT ROOT: __init__.py
# Location: /project_root/__init__.py
# ==============================================================================
"""
PyGameMaker IDE - Main Package
A GameMaker-style visual game development environment

This package contains:
- Core application logic
- Asset management system
- Visual programming interface
- Project management tools
- Thymio educational robot support
"""

import importlib
import os
import sys

__version__ = "1.0.0"
__author__ = "Gabriel Thullen"
__description__ = "GameMaker-style IDE for creating 2D games in Python"

# The application class is PyGameMakerIDE; GameMakerIDE is a backward-compatible
# alias for the previously-documented (and previously-broken) name.
__all__ = ['PyGameMakerIDE', 'GameMakerIDE']

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))


def __getattr__(name):
    """Lazily expose the main application class (PEP 562).

    PyGameMaker is normally launched as a script (``python main.py``) with the
    project root on ``sys.path``; its modules use top-level absolute imports
    (``from core ... import``). Importing this package from elsewhere therefore
    requires the project root on ``sys.path`` *before* ``main`` is imported.
    Doing it lazily here keeps ``import pygm2`` cheap and side-effect-free
    (no PySide6/Qt load) until the class is actually requested.
    """
    if name in ("PyGameMakerIDE", "GameMakerIDE"):
        if _PKG_DIR not in sys.path:
            sys.path.insert(0, _PKG_DIR)
        return importlib.import_module("main").PyGameMakerIDE
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
