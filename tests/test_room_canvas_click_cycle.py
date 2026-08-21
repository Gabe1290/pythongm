#!/usr/bin/env python3
"""Room editor: clicking a spot with several stacked instances (e.g.
several objects all placed at the same x/y -- the promo game's hub
screen does this deliberately, since a room instance has no per-instance
custom-variable slot to distinguish otherwise-identical placements) used
to always re-select the topmost one, forever. A repeated click at the
same spot, with the previous pick still the sole selection, now advances
to the next instance underneath (find_instances_at / last_click_pile in
editors/room_editor/room_canvas.py), matching the common "click again to
cycle" convention other editors use for overlapping objects.

Real offscreen QApplication (no pytest-qt), matching this repo's
established convention for room_canvas tests.
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPoint, QEvent, Qt
from PySide6.QtGui import QMouseEvent

from editors.room_editor.room_canvas import RoomCanvas
from editors.room_editor.object_instance import ObjectInstance


def _app():
    return QApplication.instance() or QApplication([])


def _make_instance(name, x, y, w=32, h=32):
    inst = ObjectInstance(name, x, y)
    inst._sprite_width = w
    inst._sprite_height = h
    inst._origin_x = 0
    inst._origin_y = 0
    return inst


def _click(canvas, x, y):
    pos = QPoint(x, y)
    press = QMouseEvent(
        QEvent.MouseButtonPress, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    release = QMouseEvent(
        QEvent.MouseButtonRelease, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    canvas.mousePressEvent(press)
    canvas.mouseReleaseEvent(release)


def test_find_instances_at_is_topmost_first():
    """Draw order is list order (later = on top); the pile must be
    reported in that same topmost-first order."""
    _app()
    canvas = RoomCanvas()
    a = _make_instance("obj_a", 0, 0)
    b = _make_instance("obj_b", 0, 0)
    c = _make_instance("obj_c", 0, 0)
    canvas.instances = [a, b, c]  # c drawn last -> topmost
    pile = canvas.find_instances_at(QPoint(10, 10))
    assert pile == [c, b, a]


def test_find_instance_at_still_returns_only_the_topmost():
    """Backward compatibility: erase/paint callers use find_instance_at
    and must keep seeing only the single topmost instance."""
    _app()
    canvas = RoomCanvas()
    a = _make_instance("obj_a", 0, 0)
    b = _make_instance("obj_b", 0, 0)
    canvas.instances = [a, b]
    assert canvas.find_instance_at(QPoint(5, 5)) is b


def test_repeated_click_on_a_pile_cycles_through_it():
    _app()
    canvas = RoomCanvas()
    a = _make_instance("obj_a", 0, 0)
    b = _make_instance("obj_b", 0, 0)
    c = _make_instance("obj_c", 0, 0)
    canvas.instances = [a, b, c]

    _click(canvas, 10, 10)
    assert canvas.selected_instances == [c]

    _click(canvas, 10, 10)
    assert canvas.selected_instances == [b]

    _click(canvas, 10, 10)
    assert canvas.selected_instances == [a]

    # Wraps back around to the top of the pile.
    _click(canvas, 10, 10)
    assert canvas.selected_instances == [c]


def test_single_instance_click_is_unaffected():
    """No pile (len 1) -- every click just re-selects the same instance,
    exactly like before this feature existed."""
    _app()
    canvas = RoomCanvas()
    only = _make_instance("obj_only", 0, 0)
    canvas.instances = [only]

    _click(canvas, 5, 5)
    assert canvas.selected_instances == [only]
    _click(canvas, 5, 5)
    assert canvas.selected_instances == [only]


def test_clicking_a_different_pile_resets_cycling():
    _app()
    canvas = RoomCanvas()
    a = _make_instance("obj_a", 0, 0)
    b = _make_instance("obj_b", 0, 0)
    elsewhere = _make_instance("obj_elsewhere", 200, 200)
    canvas.instances = [a, b, elsewhere]

    _click(canvas, 10, 10)
    assert canvas.selected_instances == [b]

    # Click a totally different instance...
    _click(canvas, 210, 210)
    assert canvas.selected_instances == [elsewhere]

    # ...then back on the original pile: starts over at the top, not
    # wherever cycling had previously left off.
    _click(canvas, 10, 10)
    assert canvas.selected_instances == [b]


def test_manually_reselecting_the_top_of_a_pile_does_not_desync_cycling():
    """If something else (e.g. an outliner click, or re-clicking after
    a shift-click) puts the topmost instance back as the sole selection,
    the next plain click still advances from there rather than jumping
    to some stale index."""
    _app()
    canvas = RoomCanvas()
    a = _make_instance("obj_a", 0, 0)
    b = _make_instance("obj_b", 0, 0)
    c = _make_instance("obj_c", 0, 0)
    canvas.instances = [a, b, c]

    _click(canvas, 10, 10)  # -> c
    _click(canvas, 10, 10)  # -> b
    assert canvas.selected_instances == [b]

    # Something re-selects the topmost instance directly (not via a click).
    canvas.selected_instances = [c]

    _click(canvas, 10, 10)
    assert canvas.selected_instances == [b]


def test_shift_click_does_not_participate_in_cycling():
    _app()
    canvas = RoomCanvas()
    a = _make_instance("obj_a", 0, 0)
    b = _make_instance("obj_b", 0, 0)
    canvas.instances = [a, b]

    pos = QPoint(10, 10)
    shift_press = QMouseEvent(
        QEvent.MouseButtonPress, pos, Qt.LeftButton, Qt.LeftButton, Qt.ShiftModifier)
    canvas.mousePressEvent(shift_press)
    assert canvas.selected_instances == [b]  # topmost, toggled into the multi-selection

    # A later plain click on the same spot must not think it's mid-cycle
    # from the shift-click (which never set last_click_pile).
    _click(canvas, 10, 10)
    assert canvas.selected_instances == [b]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
