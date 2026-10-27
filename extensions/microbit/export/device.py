#!/usr/bin/env python3
"""Copy a generated ``main.py`` onto a micro:bit already running
MicroPython (Stage X, unit X7's device-copy half).

Uses `microfs <https://github.com/ntoll/microfs>`_ (MIT, wraps
``pyserial``): confirmed by reading its installed source that
``microfs.put(filename, target=None, serial=None)`` auto-detects the
board over USB serial by VID:PID ``0D28:0204`` (the exact constant
Stage L's own sketch already names) and manages the whole serial
session itself when ``serial`` is left ``None`` -- no manual
``get_serial()``/open/close dance needed here. This module exists so
the UI layer (``export_microbit_code``) and tests don't import
``microfs`` directly.
"""
from core.logger import get_logger
from export.base_exporter import _missing_dependency_message

logger = get_logger(__name__)


class MicrobitNotFound(IOError):
    """No micro:bit found on any USB serial port. It must show up as a
    serial device, not just the MICROBIT mass-storage drive, for this to
    work -- a board that's brand new or still running the block-based
    MakeCode editor won't."""


def copy_main_py(main_py_path) -> None:
    """Copy ``main_py_path`` onto a connected micro:bit as ``main.py``.

    Raises ``RuntimeError`` (microfs/pyserial not installed, with the
    standard pip-install-no-admin-needed message) or ``MicrobitNotFound``
    (no board detected) with a message meant to be shown to the user
    directly. Any other ``IOError`` from microfs (a real write failure)
    is left to propagate as-is -- it already carries a device-reported
    reason.
    """
    try:
        import microfs
    except ImportError as exc:
        raise RuntimeError(_missing_dependency_message(
            "microfs", "microfs", "micro:bit MicroPython export",
            note="microfs talks to a micro:bit that's already running "
                 "MicroPython, over its USB serial connection (pyserial "
                 "installs automatically alongside it)."
        )) from exc

    try:
        microfs.put(str(main_py_path), target="main.py")
    except IOError as exc:
        if "micro:bit" in str(exc).lower():
            raise MicrobitNotFound(
                "No micro:bit found. Make sure it's plugged in via USB "
                "and is already running MicroPython -- if it's brand new "
                "or still running the block-based MakeCode editor, flash "
                "it once with MicroPython from python.microbit.org first."
            ) from exc
        raise
