#!/usr/bin/env python3
"""Talk to a real Thymio II without Aseba Studio (Qt-free).

The Thymio Suite runs a background service, the **Thymio Device Manager** (TDM), that owns the USB / wireless
connection to every robot and speaks a small TCP protocol (default port 8596). Aseba Studio is only one client of
it; the ``tdmclient`` package (Mobsya, BSD-3) is another, and is what this module uses to

* find out whether the TDM is running, and start it if the Thymio software is installed (:func:`ensure_device_manager`);
* list the robots it sees (:func:`list_robots`: name, id, status);
* send a plain-text Aseba program to one of them, compile it there and run it (:func:`send_program`).

Nothing here needs a robot to be *imported*: ``tdmclient`` is imported lazily and every public call reports a missing
package as a :class:`ThymioLinkError`, so the IDE can say how to install it. The ``client_factory`` arguments exist so
the tests can drive the whole flow with a fake client; the real thing (a physical robot) can only be checked by hand.
"""
import os
import platform
import shutil
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from core.logger import get_logger

logger = get_logger(__name__)

TDM_HOST = "localhost"
TDM_PORT = 8596

# tdmclient's node status numbers (tdmclient.thymio.ThymioFB.NODE_STATUS_*)
STATUS_NAMES = {0: "unknown", 1: "connected", 2: "available", 3: "busy", 4: "ready", 5: "disconnected"}
STATUS_AVAILABLE, STATUS_BUSY, STATUS_READY = 2, 3, 4
INSTALL_HINT = "pip install --user tdmclient"


class ThymioLinkError(Exception):
    """The robot link cannot be used; ``str(error)`` says why and what to do."""


@dataclass
class Robot:
    """A robot the device manager reported."""
    id: str
    name: str
    status: int

    @property
    def status_name(self) -> str:
        return STATUS_NAMES.get(self.status, str(self.status))

    @property
    def usable(self) -> bool:
        """Can a program be sent right now? (a ``busy`` robot is held by another program)"""
        return self.status in (STATUS_AVAILABLE, STATUS_READY)


@dataclass
class SendResult:
    ok: bool
    stage: str          # "done", "lock", "compile" or "run"
    message: str = ""   # the robot's own error text when it refused the program
    robot: str = ""


def tdmclient_installed() -> bool:
    try:
        import tdmclient  # noqa: F401
        return True
    except ImportError:
        return False


def _client_class():
    try:
        from tdmclient import ClientAsync
    except ImportError as exc:
        raise ThymioLinkError(f"The 'tdmclient' package is not installed. Install it with: {INSTALL_HINT}") from exc
    return ClientAsync


# --- the device manager ------------------------------------------------------------------------------

def device_manager_running(host: str = TDM_HOST, port: int = TDM_PORT, timeout: float = 0.5) -> bool:
    """Is something listening where the TDM listens?"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def find_device_manager_executable() -> Optional[Path]:
    """The installed ``thymio-device-manager`` program, or None."""
    on_path = shutil.which("thymio-device-manager")
    if on_path:
        return Path(on_path)
    system = platform.system()
    candidates = []
    if system == "Windows":
        for root in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"), r"C:\Program Files"):
            if root:
                candidates.append(Path(root) / "Thymio" / "bin" / "thymio-device-manager.exe")
    elif system == "Darwin":
        candidates += [Path("/Applications/Thymio Suite.app/Contents/MacOS/thymio-device-manager"),
                       Path("/Applications/Thymio Suite/thymio-device-manager")]
    else:
        candidates += [Path("/usr/bin/thymio-device-manager"), Path("/opt/Thymio/bin/thymio-device-manager"),
                       Path("/opt/thymio-suite/thymio-device-manager")]
    return next((c for c in candidates if c.is_file()), None)


def ensure_device_manager(wait: float = 10.0, host: str = TDM_HOST, port: int = TDM_PORT,
                          launch: Optional[Callable[[Path], object]] = None,
                          running: Optional[Callable[[], bool]] = None) -> bool:
    """True once the TDM is reachable. Starts it (detached, so it outlives the IDE's call) when it is not running
    and the Thymio software is installed; False when it cannot be reached."""
    is_up = running or (lambda: device_manager_running(host, port))
    if is_up():
        return True
    exe = find_device_manager_executable()
    if exe is None:
        return False
    logger.info(f"Starting the Thymio device manager: {exe}")
    try:
        (launch or _launch_detached)(exe)
    except OSError as exc:
        logger.warning(f"Could not start {exe}: {exc}")
        return False
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        if is_up():
            return True
        time.sleep(0.3)
    return is_up()


def _launch_detached(exe: Path) -> None:
    kwargs = {"cwd": str(exe.parent), "stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL,
              "stderr": subprocess.DEVNULL}
    if platform.system() == "Windows":
        kwargs["creationflags"] = 0x00000008 | 0x00000200          # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen([str(exe)], **kwargs)


# --- robots ---------------------------------------------------------------------------------------------

def _close_client(client) -> None:
    """Disconnect from the TDM and make sure its reader thread ends.

    ``tdmclient`` reads the socket in a non-daemon thread blocked in ``recv()``; ``disconnect()`` only asks it to
    stop, and it would not notice until the next packet -- long enough to make the Python process (the IDE, on quit)
    hang. A short socket timeout makes the blocked read return; the library already treats a timeout as "look at the
    running flag again", so the thread ends cleanly (shutting the socket down instead makes it print a traceback)."""
    tdm = getattr(client, "tdm", None)
    sock = getattr(getattr(tdm, "io", None), "socket", None)
    try:
        client.disconnect()
    except Exception as exc:                       # never let cleanup hide the real result
        logger.debug(f"Thymio client disconnect failed: {exc}")
    if sock is not None:
        try:
            sock.settimeout(0.2)
        except OSError:
            pass


def _robots_of(client) -> List[Robot]:
    found = []
    for node in list(getattr(client, "nodes", None) or []):
        props = getattr(node, "props", None) or {}
        found.append(Robot(id=str(getattr(node, "id_str", "") or ""),
                           name=str(props.get("name") or "Thymio"),
                           status=int(getattr(node, "status", 0) or 0)))
    return found


def list_robots(timeout: float = 3.0, client_factory=None, host: str = TDM_HOST, port: int = TDM_PORT) -> List[Robot]:
    """The robots the device manager currently sees. Raises :class:`ThymioLinkError` if it cannot be reached."""
    factory = client_factory or _client_class()
    try:
        client = factory(tdm_addr=host, tdm_port=port) if client_factory is None else factory()
    except OSError as exc:
        raise ThymioLinkError(f"Could not reach the Thymio device manager ({exc}).") from exc
    try:
        deadline = time.monotonic() + timeout
        robots: List[Robot] = []
        while time.monotonic() < deadline:
            client.process_waiting_messages()
            robots = _robots_of(client)
            if robots and any(r.status != 1 for r in robots):          # statuses settle just after the first report
                break
            time.sleep(0.1)
        return robots
    finally:
        _close_client(client)


def send_program(source: str, node_id: Optional[str] = None, run: bool = True, client_factory=None,
                 host: str = TDM_HOST, port: int = TDM_PORT) -> SendResult:
    """Compile ``source`` (plain Aseba text) on a robot and, unless ``run`` is False, start it.

    ``node_id`` picks a robot (default: the first one). Returns a :class:`SendResult`; a refusal by the robot (a
    compile error, a busy robot) is a result, not an exception. Raises :class:`ThymioLinkError` only when the
    device manager itself cannot be used."""
    factory = client_factory or _client_class()
    try:
        client = factory(tdm_addr=host, tdm_port=port) if client_factory is None else factory()
    except OSError as exc:
        raise ThymioLinkError(f"Could not reach the Thymio device manager ({exc}).") from exc
    outcome = {}

    async def program():
        try:
            from tdmclient import NodeLockError
        except ImportError:                                            # a fake client in a test
            class NodeLockError(Exception):
                pass
        kwargs = {"node_id": node_id} if node_id else {}
        try:
            with await client.lock(**kwargs) as node:
                outcome["robot"] = str(getattr(node, "props", {}).get("name") or "Thymio") \
                    if isinstance(getattr(node, "props", None), dict) else "Thymio"
                error = await node.compile(source)
                if error is not None:
                    outcome["result"] = SendResult(False, "compile", str(error.get("error_msg", error)), outcome["robot"])
                    return
                if run:
                    error = await node.run()
                    if error is not None:
                        outcome["result"] = SendResult(False, "run", f"error {error.get('error_code', error)}", outcome["robot"])
                        return
                outcome["result"] = SendResult(True, "done", "", outcome["robot"])
        except NodeLockError as exc:
            outcome["result"] = SendResult(False, "lock", str(exc), outcome.get("robot", ""))

    try:
        client.run_async_program(program)
    except OSError as exc:
        raise ThymioLinkError(f"Lost the Thymio device manager ({exc}).") from exc
    finally:
        _close_client(client)
    return outcome.get("result") or SendResult(False, "lock", "no answer from the robot")
