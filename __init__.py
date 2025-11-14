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

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "GameMaker-style IDE for Python game development"

# Import main application class for easy access
# Lazy import to avoid loading Qt during test collection
def __getattr__(name):
    if name == 'GameMakerIDE':
        from .main import GameMakerIDE
        return GameMakerIDE
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['GameMakerIDE']
