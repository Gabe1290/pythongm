"""
Root-level pytest configuration.

This conftest.py exists to prevent pytest from trying to import
the root __init__.py which imports PySide6 and other heavy dependencies.
"""

# Tell pytest to ignore everything except the tests/ directory
collect_ignore_glob = [
    "__init__.py",
    "main.py",
    "setup.py",
    "*.pyc",
    "widgets/*.py",
    "utils/*.py",
    "exporters/*.py",
    "editors/*.py",
    "dialogs/*.py",
    "actions/*.py",
    "core/*.py",
]
