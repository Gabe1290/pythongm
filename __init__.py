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
"""

__version__ = "0.10.0-alpha"
__author__ = "Gabriel Thullen"
__description__ = "GameMaker-style IDE for Python game development"

# Import main application class for easy access
from .main import GameMakerIDE

__all__ = ['GameMakerIDE']
