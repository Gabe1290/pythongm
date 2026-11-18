"""Regression tests for the 2026-11-18 classroom incident (Debian 12).

After a few restarts of the IDE (switching the language to Portuguese, then
back to French), the IDE "closed straight away" on every launch. Three
defects in the single-instance machinery made that possible:

1. The lock name was the same for every account: Qt put it at
   ``/tmp/PyGameMakerIDE-single-instance``, so ONE live IDE anywhere on the
   computer (another user's session, a hung leftover) turned every other
   launch away silently. Now it is per user and, on Linux, in the user's
   private ``$XDG_RUNTIME_DIR``.
2. The IDE could not be stopped with SIGTERM: ``pygame.mixer.init()`` let SDL
   install a handler that turns SIGTERM into an SDL_QUIT event the Qt IDE
   never reads, so a stuck IDE kept the lock. main.py now sets
   ``SDL_NO_SIGNAL_HANDLERS=1`` (and Test Game children get it removed).
3. ``bring_to_front`` (what the running IDE does when a second launch knocks)
   never showed a hidden main window, so the knock produced no window at all.
"""

import ast
import os
import subprocess
import sys
import textwrap
import time
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO = Path(__file__).parent.parent


@pytest.fixture
def offscreen_app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


@pytest.fixture
def guard_module(monkeypatch):
    import core.single_instance as single_instance
    monkeypatch.setattr(single_instance, "SERVER_NAME",
                        f"pygm2-t-{uuid.uuid4().hex[:12]}")
    return single_instance


def _as_user(monkeypatch, name):
    import getpass
    monkeypatch.setattr(getpass, "getuser", lambda: name)


class TestServerName:

    def test_name_contains_the_user(self, guard_module, monkeypatch):
        monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
        _as_user(monkeypatch, "alice")
        assert guard_module.server_name() == f"{guard_module.SERVER_NAME}-alice"

    def test_two_users_get_different_names(self, guard_module, monkeypatch):
        _as_user(monkeypatch, "alice")
        a = guard_module.server_name()
        _as_user(monkeypatch, "bob")
        assert guard_module.server_name() != a

    def test_unsafe_characters_are_replaced(self, guard_module, monkeypatch):
        monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
        _as_user(monkeypatch, "DOMAIN\\élève 1/x")
        name = guard_module.server_name()
        tag = name[len(guard_module.SERVER_NAME) + 1:]
        assert all(c.isascii() and (c.isalnum() or c in "_.-") for c in tag), tag

    @pytest.mark.skipif(sys.platform == "win32", reason="no XDG_RUNTIME_DIR")
    def test_uses_the_private_runtime_dir(self, guard_module, monkeypatch, tmp_path):
        monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
        _as_user(monkeypatch, "alice")
        assert guard_module.server_name() == str(
            tmp_path / f"{guard_module.SERVER_NAME}-alice")

    @pytest.mark.skipif(sys.platform == "win32", reason="no XDG_RUNTIME_DIR")
    def test_too_long_runtime_path_falls_back_to_a_plain_name(
            self, guard_module, monkeypatch, tmp_path):
        deep = tmp_path / ("d" * 120)
        deep.mkdir()
        monkeypatch.setenv("XDG_RUNTIME_DIR", str(deep))
        _as_user(monkeypatch, "alice")
        assert guard_module.server_name() == f"{guard_module.SERVER_NAME}-alice"


class TestGuardIsPerUser:

    def test_another_users_ide_does_not_block_this_user(
            self, offscreen_app, guard_module, monkeypatch):
        _as_user(monkeypatch, "alice")
        alice = guard_module.SingleInstanceGuard()
        try:
            assert alice.is_primary
            _as_user(monkeypatch, "bob")
            bob = guard_module.SingleInstanceGuard()
            try:
                assert bob.is_primary, "bob was turned away by alice's IDE"
            finally:
                bob.close()
        finally:
            alice.close()

    def test_same_user_is_still_turned_away(
            self, offscreen_app, guard_module, monkeypatch):
        _as_user(monkeypatch, "alice")
        first = guard_module.SingleInstanceGuard()
        try:
            second = guard_module.SingleInstanceGuard()
            try:
                assert second.is_primary is False
            finally:
                second.close()
        finally:
            first.close()

    @pytest.mark.skipif(sys.platform == "win32", reason="no XDG_RUNTIME_DIR")
    def test_socket_is_created_in_the_runtime_dir_and_removed_on_close(
            self, offscreen_app, guard_module, monkeypatch, tmp_path):
        monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
        _as_user(monkeypatch, "alice")
        guard = guard_module.SingleInstanceGuard()
        sock = tmp_path / f"{guard_module.SERVER_NAME}-alice"
        try:
            assert guard.is_primary
            assert sock.exists()
        finally:
            guard.close()
        assert not sock.exists()


def _module_assign_value(path, env_key):
    """The literal main.py passes to os.environ.setdefault(env_key, ...)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:  # module level only -- before any Qt/pygame use
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and getattr(node.value.func, "attr", "") == "setdefault"
                and node.value.args
                and isinstance(node.value.args[0], ast.Constant)
                and node.value.args[0].value == env_key):
            return node.value.args[1].value
    return None


class TestSigterm:

    def test_main_disables_sdl_signal_handlers_at_module_level(self):
        assert _module_assign_value(REPO / "main.py", "SDL_NO_SIGNAL_HANDLERS") == "1"

    def test_test_game_child_gets_the_variable_removed(self):
        src = (REPO / "core" / "ide" / "_test_game.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        pops = [n for n in ast.walk(tree)
                if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "pop"
                and getattr(n.func.value, "id", "") == "env"
                and n.args and isinstance(n.args[0], ast.Constant)
                and n.args[0].value == "SDL_NO_SIGNAL_HANDLERS"]
        assert pops, "Test Game's child env must drop SDL_NO_SIGNAL_HANDLERS"

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX signals")
    @pytest.mark.parametrize("hint, survives", [(None, True), ("1", False)])
    def test_sigterm_after_mixer_init(self, hint, survives, tmp_path):
        """With SDL's handler, SIGTERM is swallowed; with the hint it kills."""
        pytest.importorskip("pygame")
        script = tmp_path / "child.py"
        script.write_text(textwrap.dedent("""
            import os, time
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
            import pygame
            pygame.mixer.init()
            print('ready', flush=True)
            time.sleep(30)
        """))
        env = dict(os.environ)
        env.pop("SDL_NO_SIGNAL_HANDLERS", None)
        env["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        if hint:
            env["SDL_NO_SIGNAL_HANDLERS"] = hint
        proc = subprocess.Popen([sys.executable, str(script)], env=env,
                                stdout=subprocess.PIPE, text=True)
        try:
            assert proc.stdout.readline().strip() == "ready"
            proc.terminate()
            time.sleep(1.0)
            assert (proc.poll() is None) is survives
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait(5)


class TestBringToFrontShowsHiddenWindow:

    def test_hidden_main_window_is_shown(self, offscreen_app):
        from PySide6.QtWidgets import QMainWindow
        from core.ide._test_game import TestGameMixin

        class Win(QMainWindow):
            bring_to_front = TestGameMixin.bring_to_front

        win = Win()
        try:
            win.show()
            win.hide()
            assert not win.isVisible()
            win.bring_to_front()
            assert win.isVisible()
        finally:
            win.close()
            win.deleteLater()
