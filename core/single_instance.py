"""Single-instance guard for the PyGameMaker IDE.

Real classroom incident (2026-09-23): a student ended up with 10+ IDE
processes running simultaneously (each relaunch after closing a Test Game
window, unable to find the existing — minimized — IDE window, started a
new one instead). All ten had the same project folder open. PyGameMaker's
folder save format writes each asset as its own file
(``rooms/*.json``, ``objects/*.json``, ``sprites/*.json`` ...), so nothing
detects or prevents two *processes* saving to the same folder at once —
each instance's independent saves (Test Game alone calls ``save_project()``)
silently accumulate into the folder rather than overwriting each other,
since a save only rewrites files for assets *that instance* knows about.
Test Game then loads whatever is currently on disk: a project that is the
union of everything every one of those ten students' clicks ever wrote,
not any single student's actual project. Limiting the app to one process
per machine removes the accumulation at the source, rather than trying to
detect or repair a project folder after the fact.

Mechanism: the standard Qt single-application-instance recipe, built on
``QLocalServer``/``QLocalSocket`` (a named local socket — a Unix domain
socket on Linux/macOS, a named pipe on Windows). The first process to run
becomes the primary and listens; every later launch attempt connects,
then exits immediately without ever constructing an IDE window or
touching a project. No payload is sent — the connection itself is the
whole message, deliberately, since an async readyRead-driven read here
segfaulted under PySide6 (a stray reference to a QLocalSocket the caller
had already let go of, likely). The primary's ``raise_requested`` signal
fires on each such connection so the caller (main.py) can bring the
existing window to front via ``PyGameMakerIDE.bring_to_front()``
(``core/ide/_test_game.py``) — best-effort, subject to the same
focus-stealing-prevention caveats as that method already documents, but
even in the worst case (the compositor refuses to raise it) the real fix
here is that a SECOND process never gets to open the project at all.
"""

import os

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from core.logger import get_logger

logger = get_logger(__name__)

SERVER_NAME = "PyGameMakerIDE-single-instance"
_CONNECT_TIMEOUT_MS = 500


def multiple_instances_allowed() -> bool:
    """True when the user has opted out of the one-IDE-per-machine guard.

    Two opt-outs, either is enough: the ``PYGM_ALLOW_MULTIPLE_INSTANCES=1``
    environment variable (developers, wrapper scripts) or the Preferences ->
    Advanced checkbox, stored as ``advanced.allow_multiple_instances``.
    Read once at startup, so a change takes effect on the next launch.
    """
    if os.environ.get('PYGM_ALLOW_MULTIPLE_INSTANCES') == '1':
        return True
    from utils.config import Config
    return bool(Config.get_advanced_config()['allow_multiple_instances'])


class SingleInstanceGuard(QObject):
    """Construct once, early, right after the QApplication exists.

    ``self.is_primary`` is True if this process should proceed normally
    (and, if a QLocalServer was successfully started, connect
    ``raise_requested`` to something that brings the main window forward).
    It is False if another instance is already running — the caller should
    exit immediately without doing anything else (no project load, no
    plugin load, no window).
    """

    raise_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._server = None
        self.is_primary = self._acquire()

    def _acquire(self) -> bool:
        # Is another instance already listening? The connection itself is
        # the whole signal -- no payload needed, which keeps both ends
        # synchronous, no signal/slot handoff required to notice a launch
        # attempt (a readyRead-driven async read here was the first draft;
        # it segfaulted under PySide6 -- see _on_new_connection).
        probe = QLocalSocket(self)
        probe.connectToServer(SERVER_NAME)
        connected = probe.waitForConnected(_CONNECT_TIMEOUT_MS)
        probe.close()
        probe.deleteLater()
        if connected:
            return False

        # Nobody answered -- become the primary. removeServer() clears a
        # stale socket file a crashed/kill-9'd prior instance can leave
        # behind, which otherwise makes listen() fail with
        # AddressInUseError even though (as just proven above) nothing is
        # actually listening on it.
        QLocalServer.removeServer(SERVER_NAME)
        server = QLocalServer(self)
        if not server.listen(SERVER_NAME):
            # Could not become the primary either (permissions, an odd
            # platform quirk). Fail OPEN -- never block a student from
            # launching the IDE at all just because this guard couldn't
            # set itself up; worst case we're back to the pre-guard
            # behaviour for this one launch.
            logger.warning(
                "Single-instance guard: could not listen (%s); "
                "continuing without it.", server.errorString()
            )
            return True

        server.newConnection.connect(self._on_new_connection)
        self._server = server
        return True

    def _on_new_connection(self):
        # Drain every pending connection (a burst of near-simultaneous
        # launch attempts can queue more than one before this slot runs),
        # closing each immediately -- no data is ever sent or read, the
        # connection itself is the whole message, so there is nothing left
        # asynchronous that could fire on a socket this method has already
        # let go of.
        while self._server.hasPendingConnections():
            conn = self._server.nextPendingConnection()
            if conn is None:
                break
            conn.close()
            conn.deleteLater()
            self.raise_requested.emit()

    def close(self):
        """Release the server name so the next launch can become primary
        cleanly. Safe to call more than once / when never primary."""
        if self._server is not None:
            self._server.close()
            self._server = None
            QLocalServer.removeServer(SERVER_NAME)
