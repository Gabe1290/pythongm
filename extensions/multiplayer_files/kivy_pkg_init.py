# The shared-folder multiplayer package shipped into a Kivy export (see export_kivy.py).
#
# The session modules do `from core.logger import get_logger` (the IDE's logger). An exported
# game has no `core` package, so stand a minimal stand-in in front of the import -- only when
# the real one is not importable (the IDE, tests). Same shim as the LAN extension's.
import logging as _logging
import sys as _sys
import types as _types

try:
    import core.logger  # noqa: F401
except ImportError:
    _core = _sys.modules.get("core") or _types.ModuleType("core")
    _logger = _sys.modules.get("core.logger") or _types.ModuleType("core.logger")
    _logger.get_logger = _logging.getLogger
    _core.logger = _logger
    _sys.modules["core"] = _core
    _sys.modules["core.logger"] = _logger
