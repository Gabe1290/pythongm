"""
Export module for PyGameMaker IDE
Handles exporting games to various platforms
"""

# Only import what actually exists
# Add imports here as you create new exporters

__all__ = []

# Conditionally import exporters only if they exist
try:
    from .exe.exe_exporter import ExeExporter
    __all__.append('ExeExporter')
except ImportError:
    pass

# Future exporters can be added like this:
# try:
#     from .kivy.kivy_exporter import KivyExporter
#     __all__.append('KivyExporter')
# except ImportError:
#     pass