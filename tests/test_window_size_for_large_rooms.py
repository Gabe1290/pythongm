"""A room bigger than the window must not be shown all at once.

`GameRunner` sized the window to the room unconditionally, so views_1 --
whose whole subject is a 2400x800 room seen through an 800x600 camera --
rendered the entire room in one window. The scrolling camera it exists to
demonstrate had nothing to do, which is why the sample read as "what is this
supposed to do?".

`_window_size_for` clamps to the project's declared window size, per axis and
only downwards. The blast radius matters as much as the fix: rooms smaller
than or equal to the declared size must behave exactly as before, or
raycast_* (640x480 declared, 480x480 rooms) and maze_2/maze_3 (rooms of
differing heights) would all change size. The last test pins that.
"""
import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame  # noqa: E402

pytestmark = skip_without_pygame

from runtime.game_runner import GameRunner  # noqa: E402


class _Room:
    def __init__(self, width, height):
        self.width = width
        self.height = height


def _runner(settings):
    r = GameRunner.__new__(GameRunner)          # no display, no project load
    r.project_data = {"settings": settings}
    return r


class TestWindowSizeRule:
    def test_a_room_smaller_than_the_window_keeps_its_own_size(self):
        """The previous behaviour, and what every sample but views_* relies
        on -- raycast_* declares 640x480 with 480x480 rooms."""
        r = _runner({"window_width": 640, "window_height": 480})
        assert r._window_size_for(_Room(480, 480)) == (480, 480)

    def test_a_room_equal_to_the_window_is_unchanged(self):
        r = _runner({"window_width": 640, "window_height": 480})
        assert r._window_size_for(_Room(640, 480)) == (640, 480)

    def test_a_room_larger_than_the_window_is_clamped(self):
        r = _runner({"window_width": 800, "window_height": 600})
        assert r._window_size_for(_Room(2400, 800)) == (800, 600)

    def test_clamping_is_per_axis(self):
        """A room wider but not taller than the window clamps only width."""
        r = _runner({"window_width": 800, "window_height": 600})
        assert r._window_size_for(_Room(2400, 480)) == (800, 480)
        assert r._window_size_for(_Room(640, 900)) == (640, 600)

    @pytest.mark.parametrize("settings", [
        {},                                             # nothing declared
        {"window_width": 0, "window_height": 0},        # zero
        {"window_width": None, "window_height": None},  # explicit null
        {"window_width": "wide", "window_height": "tall"},   # rubbish
    ])
    def test_a_missing_or_unusable_setting_falls_back_to_the_room(self, settings):
        r = _runner(settings)
        assert r._window_size_for(_Room(2400, 800)) == (2400, 800)

    def test_it_survives_project_data_being_absent(self):
        r = GameRunner.__new__(GameRunner)
        r.project_data = None
        assert r._window_size_for(_Room(1200, 900)) == (1200, 900)


class TestTheSamplesAreUnaffectedExceptViews:
    """Pins the blast radius: exactly the views_* samples change size."""

    @staticmethod
    def _sizes(sample):
        path = REPO_ROOT / "samples" / sample
        settings = json.loads(
            (path / "project.json").read_text(encoding="utf-8")).get("settings", {})
        r = _runner(settings)
        out = []
        for room_file in sorted((path / "rooms").glob("*.json")):
            room = json.loads(room_file.read_text(encoding="utf-8"))
            got = r._window_size_for(_Room(room["width"], room["height"]))
            out.append((room_file.stem, (room["width"], room["height"]), got))
        return out

    @pytest.mark.parametrize("sample", sorted(
        p.parent.name for p in (REPO_ROOT / "samples").glob("*/project.json")
        if not p.parent.name.startswith("views_")))
    def test_every_other_sample_still_uses_its_room_size(self, sample):
        for name, room, window in self._sizes(sample):
            assert window == room, (
                "%s/%s would change from %s to %s" % (sample, name, room, window))

    @pytest.mark.parametrize("sample", ["views_1", "views_2"])
    def test_the_views_samples_are_clamped_to_their_declared_window(self, sample):
        for name, room, window in self._sizes(sample):
            assert room[0] > window[0], "%s/%s is not wider than the window" % (
                sample, name)
            assert window == (800, 600)
