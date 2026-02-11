#!/usr/bin/env python3
"""
GMK file importer for PyGameMaker (pygm2).

Supports GameMaker 8.0/8.1 .gmk files (binary format versions 800/810).

Usage:
    from importers import import_gmk

    success = import_gmk("path/to/game.gmk", "path/to/output_project")
"""

from importers.gmk_importer import import_gmk, GmkImportError

__all__ = ['import_gmk', 'GmkImportError']
