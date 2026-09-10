#!/usr/bin/env python3
"""Shared-folder file I/O for the file-exchange multiplayer extension.

The transport layer, in the same sense extensions/multiplayer_lan/
network.py is a transport layer for sockets -- session.py's FileSession
calls these, never touches Path/json/os.replace directly. Every write is
atomic (write to a sibling ``.tmp``, ``os.replace`` into place) and every
operation is exception-safe: a locked/missing/unreadable file degrades to
None/False rather than raising, so a transient shared-drive hiccup never
crashes a frame -- FileSession's own "never raises" contract depends on
that.

Ported from core/project_manager.py's ``_atomic_write_json`` PATTERN, not
the function itself (that one is Qt/project-specific) -- see the plan
doc's "Reused pieces" section. Same reasoning applies here: Dropbox/
OneDrive/iCloud/a school SMB share's own indexing or AV scan can hold a
transient lock on a file, raising ``PermissionError`` on the rename;
retrying the rename a few times recovers from that without the caller
ever seeing an exception.
"""

import json
import os
import time
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)

_RETRY_DELAYS = (0.0, 0.05, 0.1, 0.2)


def atomic_write_json(path: Path, data) -> bool:
    """Write ``data`` to ``path`` as JSON atomically. Returns True on
    success, False on any failure. Never raises."""
    tmp_path = path.with_name(path.name + ".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
    except OSError as exc:
        logger.debug("multiplayer_files: write %s failed: %s", path, exc)
        _try_unlink(tmp_path)
        return False

    last_err = None
    for delay in _RETRY_DELAYS:
        if delay:
            time.sleep(delay)
        try:
            os.replace(tmp_path, path)
            return True
        except OSError as exc:
            last_err = exc
    logger.debug("multiplayer_files: replace %s failed after retries: %s",
                 path, last_err)
    _try_unlink(tmp_path)
    return False


def read_json(path: Path):
    """The parsed JSON at ``path``, or None if it doesn't exist, can't be
    read, or isn't valid JSON (including a file another writer has only
    partially written so far -- the caller just tries again next poll).
    Never raises."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def list_files(folder: Path, prefix: str):
    """Filenames directly in ``folder`` starting with ``prefix``, or None
    if the folder itself can't be listed (missing, permission denied, a
    disconnected drive). An empty list means the folder IS reachable and
    simply has no such files yet -- callers rely on that distinction to
    tell "nothing to do" from "the shared drive is gone". Never raises."""
    try:
        return [p.name for p in folder.iterdir()
                if p.is_file() and p.name.startswith(prefix)]
    except OSError:
        return None


def ensure_folder(folder: Path) -> bool:
    """Create ``folder`` (and its parents) if it doesn't already exist.
    Returns True if the folder exists (or now does), False on any
    failure. Never raises."""
    try:
        folder.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as exc:
        logger.debug("multiplayer_files: could not create %s: %s", folder, exc)
        return False


def _try_unlink(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
