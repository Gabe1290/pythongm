"""File-exchange multiplayer -- the built-in connect/lobby screen (Phase 4).

extensions/multiplayer_files/connect_screen.py. Plain pygame surfaces +
synthetic events, no QApplication. SDL dummy driver so a display can be
created for the draw path. Mirrors
tests/test_multiplayer_lan_connect_screen.py's own harness for the
sibling extension's screen.
"""
import os
import sys
import tempfile
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

from extensions.multiplayer_files.connect_screen import FileConnectScreen  # noqa: E402


def _surface():
    return pygame.Surface((640, 480))


def _key(ch=None, key=None):
    return pygame.event.Event(pygame.KEYDOWN,
                              key=key if key is not None else ord(ch or "a"),
                              unicode=ch or "")


def _click(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)


class TestClientScreen:
    def test_typing_builds_the_manual_path(self):
        cs = FileConnectScreen("client", _surface())
        for ch in "/srv/share":
            cs.handle_event(_key(ch))
        assert cs.manual_path == "/srv/share"

    def test_a_keydown_with_no_unicode_attribute_does_not_crash(self):
        """A real bug this exact shape caught in the full suite: this
        screen reads the process-wide pygame.event.get() queue, not one
        scoped to itself, so a KEYDOWN posted elsewhere with no
        `unicode` kwarg (any code building
        pygame.event.Event(pygame.KEYDOWN, key=...) without it) must not
        crash the modal loop."""
        cs = FileConnectScreen("client", _surface())
        bare = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
        assert not hasattr(bare, "unicode")
        cs.handle_event(bare)          # must not raise
        assert cs.manual_path == ""    # no char appended either

    def test_free_form_characters_are_not_filtered(self):
        """Unlike the LAN screen's digit-only address field, a folder
        path is free-form -- letters, spaces, backslashes for a UNC
        path, drive-letter colons, all pass through."""
        cs = FileConnectScreen("client", _surface())
        for ch in r"C:\Shared Drive\tictactoe":
            cs.handle_event(_key(ch))
        assert cs.manual_path == r"C:\Shared Drive\tictactoe"

    def test_backspace(self):
        cs = FileConnectScreen("client", _surface(), manual_default="/tmp/x")
        cs.handle_event(_key(key=pygame.K_BACKSPACE))
        assert cs.manual_path == "/tmp/"

    def test_escape_cancels(self):
        cs = FileConnectScreen("client", _surface())
        assert cs.handle_event(_key(key=pygame.K_ESCAPE)) == "cancel"

    def test_empty_path_shows_an_error_not_a_connect(self):
        cs = FileConnectScreen("client", _surface(), manual_default="")
        assert cs.handle_event(_key(key=pygame.K_RETURN)) is None
        assert cs.status_kind == "error"

    def test_a_nonexistent_path_is_rejected_with_a_clear_error(self):
        cs = FileConnectScreen("client", _surface(),
                               manual_default="/no/such/folder/at/all")
        assert cs.handle_event(_key(key=pygame.K_RETURN)) is None
        assert cs.status_kind == "error"
        assert "existe" in cs.status.lower()

    def test_a_real_writable_folder_is_accepted(self, tmp_path):
        cs = FileConnectScreen("client", _surface(), manual_default=str(tmp_path))
        result = cs.handle_event(_key(key=pygame.K_RETURN))
        assert result == "folder:%s" % tmp_path
        assert cs.result == result

    def test_connect_button_click(self, tmp_path):
        cs = FileConnectScreen("client", _surface(), manual_default=str(tmp_path))
        cs.draw()
        btn = cs._buttons["connect"]
        assert cs.handle_event(_click(btn.rect.center)) == "folder:%s" % tmp_path

    def test_a_file_not_a_directory_is_rejected(self, tmp_path):
        f = tmp_path / "not_a_folder.txt"
        f.write_text("x")
        cs = FileConnectScreen("client", _surface(), manual_default=str(f))
        assert cs.handle_event(_key(key=pygame.K_RETURN)) is None
        assert cs.status_kind == "error"

    def test_draw_does_not_crash_and_paints(self, tmp_path):
        surf = _surface()
        cs = FileConnectScreen("client", surf, manual_default=str(tmp_path))
        cs.draw()
        assert surf.get_at((5, 5))[:3] != (0, 0, 0) or surf.get_at((320, 240))[:3] != (0, 0, 0)


class TestHostLobby:
    def test_roster_and_folder_are_rendered_and_ticked(self):
        ticks = []
        cs = FileConnectScreen(
            "host", _surface(), folder="/srv/share",
            roster_fn=lambda: [(0, "Prof"), (1, "Ada")],
            tick_fn=lambda: ticks.append(1))
        cs.draw()
        assert ticks                                # tick_fn called during draw
        assert cs._buttons.get("start") is not None
        assert cs.folder == "/srv/share"

    def test_start_button_click(self):
        cs = FileConnectScreen("host", _surface(), roster_fn=lambda: [(0, "Prof")])
        cs.draw()
        assert cs.handle_event(_click(cs._buttons["start"].rect.center)) == "start"

    def test_enter_starts(self):
        cs = FileConnectScreen("host", _surface())
        assert cs.handle_event(_key(key=pygame.K_RETURN)) == "start"

    def test_cancel_button_click(self):
        cs = FileConnectScreen("host", _surface(), roster_fn=lambda: [(0, "Prof")])
        cs.draw()
        assert cs.handle_event(_click(cs._buttons["cancel"].rect.center)) == "cancel"


class TestHeadlessFallback:
    def test_run_without_screen_connects_directly_with_the_given_path(self):
        cs = FileConnectScreen("client", None, manual_default="/srv/share")
        assert cs.run() == "folder:/srv/share"

    def test_run_without_screen_and_no_path_cancels(self):
        cs = FileConnectScreen("client", None)
        assert cs.run() == "cancel"

    def test_run_without_screen_host_starts(self):
        cs = FileConnectScreen("host", None)
        assert cs.run() == "start"

    def test_run_modal_loop_exits_on_quit(self):
        cs = FileConnectScreen("client", _surface(), manual_default="/srv/share")

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
