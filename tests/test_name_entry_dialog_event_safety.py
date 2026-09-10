"""GameRunner._show_name_entry_dialog must tolerate a KEYDOWN with no
`unicode` attribute.

Same bug class just found and fixed in extensions/multiplayer_lan and
extensions/multiplayer_files's own connect_screen.py: this dialog reads
pygame.event.get() -- the process-wide queue, not one scoped to itself
-- so a KEYDOWN built without a unicode kwarg (ordinary when other code
only cares about the key, e.g. pygame.event.Event(pygame.KEYDOWN, key=
pygame.K_a)) must not crash it with an AttributeError.

pygame.event.get() is monkeypatched directly rather than posted through
the real SDL queue: _show_name_entry_dialog calls pygame.event.clear()
at its very start, which would drain a pre-posted event before the
modal loop ever saw it, and reproducing the actual crash means the event
has to arrive from a pygame.event.get() call made *inside* the loop.
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

from runtime.game_runner import GameRunner  # noqa: E402


def _runner():
    r = GameRunner(None)
    r.screen = pygame.display.get_surface()
    return r


def _feed(monkeypatch, batches):
    """Make pygame.event.get() return each list in `batches` in turn,
    then an empty list forever -- deterministic, no real SDL queue
    involved."""
    remaining = list(batches)

    def fake_get(*a, **k):
        return remaining.pop(0) if remaining else []

    monkeypatch.setattr(pygame.event, "get", fake_get)


class TestNameEntryDialogEventSafety:
    def test_a_keydown_with_no_unicode_does_not_crash(self, monkeypatch):
        runner = _runner()
        _feed(monkeypatch, [
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
        ])
        assert runner._show_name_entry_dialog() == ""  # must not raise

    def test_typing_still_works(self, monkeypatch):
        runner = _runner()

        def key(k, ch):
            return pygame.event.Event(pygame.KEYDOWN, key=k, unicode=ch)

        _feed(monkeypatch, [
            [key(pygame.K_a, "a")],
            [key(pygame.K_b, "b")],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)],
        ])
        assert runner._show_name_entry_dialog() == "ab"

    def test_backspace_still_works(self, monkeypatch):
        runner = _runner()

        def key(k, ch):
            return pygame.event.Event(pygame.KEYDOWN, key=k, unicode=ch)

        _feed(monkeypatch, [
            [key(pygame.K_a, "a")],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
        ])
        assert runner._show_name_entry_dialog() == ""
