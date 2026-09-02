"""LAN multiplayer v2 -- the built-in connect / lobby screen (Phase 6.2).

extensions/multiplayer_lan/connect_screen.py. Plain pygame surfaces +
synthetic events, no QApplication. SDL dummy driver so a display can be
created for the draw path.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((640, 480))

from extensions.multiplayer_lan.connect_screen import (  # noqa: E402
    ConnectScreen, _split_addr, local_ip,
)


def _surface():
    return pygame.Surface((640, 480))


def _key(ch=None, key=None):
    return pygame.event.Event(pygame.KEYDOWN,
                              key=key if key is not None else ord(ch),
                              unicode=ch or "")


def _click(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)


class _FakeListener:
    def __init__(self, servers):
        self._servers = servers

    def servers(self):
        return list(self._servers)


class TestHelpers:
    def test_split_addr_plain(self):
        assert _split_addr("192.168.1.5", 45782) == ("192.168.1.5", 45782)

    def test_split_addr_with_port(self):
        assert _split_addr("192.168.1.5:50000") == ("192.168.1.5", 50000)

    def test_split_addr_bad_port_falls_back(self):
        assert _split_addr("10.0.0.1:abc", 45782) == ("10.0.0.1", 45782)

    def test_split_addr_blank(self):
        assert _split_addr("", 45782) == ("127.0.0.1", 45782)

    def test_local_ip_returns_something(self):
        ip = local_ip()
        assert isinstance(ip, str) and ip.count(".") == 3


class TestClientScreen:
    def test_typing_builds_the_manual_address(self):
        cs = ConnectScreen("client", _surface(), default_port=45782)
        for ch in "10.0.0.9":
            cs.handle_event(_key(ch))
        assert cs.manual_ip == "10.0.0.9"

    def test_letters_are_ignored_in_the_address_field(self):
        cs = ConnectScreen("client", _surface())
        for ch in "1a2b.3":
            cs.handle_event(_key(ch))
        assert cs.manual_ip == "12.3"

    def test_backspace(self):
        cs = ConnectScreen("client", _surface(), manual_default="1.2.3.4")
        cs.handle_event(_key(key=pygame.K_BACKSPACE))
        assert cs.manual_ip == "1.2.3."

    def test_enter_connects_to_the_manual_address(self):
        cs = ConnectScreen("client", _surface(), manual_default="10.0.0.5",
                           default_port=45782)
        result = cs.handle_event(_key(key=pygame.K_RETURN))
        assert result == "connect:10.0.0.5:45782"
        assert cs.result == "connect:10.0.0.5:45782"

    def test_escape_cancels(self):
        cs = ConnectScreen("client", _surface())
        assert cs.handle_event(_key(key=pygame.K_ESCAPE)) == "cancel"

    def test_empty_address_shows_an_error_not_a_connect(self):
        cs = ConnectScreen("client", _surface(), manual_default="")
        assert cs.handle_event(_key(key=pygame.K_RETURN)) is None
        assert cs.status_kind == "error"

    def test_selecting_and_connecting_to_a_discovered_server(self):
        listener = _FakeListener([
            {"ip": "10.0.0.2", "port": 45782, "name": "Quiz", "players": 2, "max": 8}])
        cs = ConnectScreen("client", _surface(), discovery_listener=listener)
        cs.draw()                                    # lays out the server rows
        assert len(cs._server_rects) == 1
        row = cs._server_rects[0]
        cs.handle_event(_click(row.center))          # first click selects
        assert cs.selected == 0
        result = cs.handle_event(_click(row.center))  # second click connects
        assert result == "connect:10.0.0.2:45782"

    def test_connect_button_click(self):
        cs = ConnectScreen("client", _surface(), manual_default="10.0.0.7",
                           default_port=45782)
        cs.draw()
        btn = cs._buttons["connect"]
        assert cs.handle_event(_click(btn.rect.center)) == "connect:10.0.0.7:45782"

    def test_draw_does_not_crash_and_paints(self):
        surf = _surface()
        cs = ConnectScreen("client", surf, manual_default="1.2.3.4")
        cs.draw()
        # something other than pure black got painted
        assert surf.get_at((5, 5))[:3] != (0, 0, 0) or surf.get_at((320, 240))[:3] != (0, 0, 0)


class TestHostLobby:
    def test_roster_is_rendered_and_ticked(self):
        ticks = []
        cs = ConnectScreen("host", _surface(),
                           roster_fn=lambda: [(0, "Prof"), (1, "Ada"), (2, "Bo")],
                           tick_fn=lambda: ticks.append(1))
        cs.draw()
        assert ticks                                # tick_fn called during draw
        assert cs._buttons.get("start") is not None

    def test_start_button_click(self):
        cs = ConnectScreen("host", _surface(), roster_fn=lambda: [(0, "Prof")])
        cs.draw()
        assert cs.handle_event(_click(cs._buttons["start"].rect.center)) == "start"

    def test_enter_starts(self):
        cs = ConnectScreen("host", _surface())
        assert cs.handle_event(_key(key=pygame.K_RETURN)) == "start"


class TestHeadlessFallback:
    def test_run_without_screen_connects_directly(self):
        cs = ConnectScreen("client", None, manual_default="10.1.1.1", default_port=45782)
        assert cs.run() == "connect:10.1.1.1:45782"

    def test_run_without_screen_host_starts(self):
        cs = ConnectScreen("host", None)
        assert cs.run() == "start"

    def test_run_modal_loop_exits_on_quit(self):
        cs = ConnectScreen("client", _surface(), manual_default="1.2.3.4")

        class _Clock:
            def __init__(self):
                self.n = 0

            def tick(self, fps=0):
                self.n += 1
                if self.n == 1:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif self.n > 5:
                    raise AssertionError("modal loop did not exit")

        assert cs.run(_Clock()) == "cancel"
