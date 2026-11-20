"""LAN multiplayer on a phone: discovery. A hosting phone broadcasts the desktop's own UDP beacon, and
``join_game`` with host ``auto`` listens for one and joins the first host with a free slot (no picker screen).

Driven against REAL desktop peers (``NetworkSession``, ``DiscoveryBeacon``, ``DiscoveryListener``) over 127.0.0.1 on a
spare UDP port, with the real ``mp_lan`` package from a real export.
"""
import socket
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import skip_without_pyside6  # noqa: E402
from extensions.multiplayer_lan.discovery import DiscoveryBeacon, DiscoveryListener  # noqa: E402
from extensions.multiplayer_lan.session import NetworkSession  # noqa: E402
from test_kivy_multiplayer_client import export_dir, glue, _Scene  # noqa: E402,F401  (fixtures)

pytestmark = skip_without_pyside6


def _udp_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _wait(fn, timeout=6.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = fn()
        if value:
            return value
        time.sleep(0.02)
    return None


def test_the_export_ships_the_discovery_module(export_dir):
    assert (export_dir / "mp_lan" / "discovery.py").is_file()


def test_a_hosting_phone_is_seen_by_a_real_listener(glue):
    g, app = glue
    port = _udp_port()
    g._beacon_target = ("127.0.0.1", port)
    listener = DiscoveryListener(port=port)
    listener.start()
    try:
        g.host(0, "Prof", 4, False, "Maze Duel")
        assert g._beacon is not None
        found = _wait(listener.servers)
        assert found and found[0]["name"] == "Maze Duel"
        assert found[0]["port"] == g._session.bound_port and found[0]["max"] == 4
        g.leave()
        assert g._beacon is None
    finally:
        listener.stop()
        g.leave()


def test_join_auto_finds_a_real_host_and_joins_it(glue):
    g, app = glue
    port = _udp_port()
    g._discovery_port = port
    host = NetworkSession(mode="host", port=0, player_name="Prof")
    host.start()
    beacon = DiscoveryBeacon("Their game", host.bound_port, 1, 8, target=("127.0.0.1", port), interval=0.1)
    beacon.start()
    scene = _Scene()
    try:
        g.join("auto", 45782, "Ada")
        assert g._auto is not None and not g.active()
        assert _wait(lambda: (host.pump_before_step(), g.update(scene), host.pump_after_update(),
                              g.active() and g._session.player_id >= 0)[-1])
        assert host.player_count == 2
        assert g._auto is None
    finally:
        beacon.stop()
        g.leave()
        host.close()


def test_join_auto_skips_a_full_host_and_gives_up_with_one_warning(glue):
    g, app = glue
    port = _udp_port()
    g._discovery_port = port
    g.AUTO_TIMEOUT = 0.3
    beacon = DiscoveryBeacon("Full", 45999, 4, 4, target=("127.0.0.1", port), interval=0.05)
    beacon.start()
    scene = _Scene()
    try:
        g.join("auto", 45782, "Ada")
        assert _wait(lambda: (g.update(scene), g._auto is None)[-1])
        assert not g.active()
        assert "join_game(host='auto')/none" in g._warned
    finally:
        beacon.stop()
        g.leave()


def test_leave_cancels_a_pending_auto_join(glue):
    g, app = glue
    g._discovery_port = _udp_port()
    g.join("auto", 45782, "Ada")
    assert g._auto is not None
    g.leave()
    assert g._auto is None
