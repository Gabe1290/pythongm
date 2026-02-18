#!/usr/bin/env python3
"""
macOS Application Export System for PyGameMaker IDE
Exports games to standalone macOS .app bundles using PyInstaller
"""

from .macos_exporter import MacOSExporter

__all__ = ['MacOSExporter']
__version__ = "1.0.0"
