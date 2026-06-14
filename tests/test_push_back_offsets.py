"""Regression test for push_back_instance bbox/origin offsets (audit M50).

Overlap was detected in bbox-world coordinates (x - origin + bbox_left) but
push_back_instance resolved the separated position from raw instance coords
with bbox dimensions, so the landing was shifted by the sprite origin / bbox
offsets — leaving the bboxes still overlapping or knocking the instance off
the grid. push_back_instance now works entirely in bbox-world coords and
converts back to raw coords via the moving instance's offset.
"""

import pytest

pytest.importorskip("pygame")

from runtime.game_runner import GameRunner


class _Inst:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def _runner():
    return GameRunner.__new__(GameRunner)


def test_left_push_lands_flush_with_offset():
    runner = _runner()
    # Moving sprite: origin 0, bbox_left 4  -> off_x = -4; raw x=30 -> mbx=34.
    moving = _Inst(30, 0)
    mbx, mby, mbw, mbh = 34, 0, 24, 24
    sbx, sby, sbw, sbh = 44, 0, 24, 24  # static bbox

    runner.push_back_instance(moving, mbx, mby, mbw, mbh, sbx, sby, sbw, sbh)

    off_x = 30 - mbx  # -4
    new_mbx = moving.x - off_x
    # Moving bbox right edge must sit exactly on the static bbox left edge.
    assert new_mbx + mbw == sbx
    assert moving.x == 16


def test_top_push_lands_flush_with_offset():
    runner = _runner()
    moving = _Inst(0, 30)
    mbx, mby, mbw, mbh = 0, 34, 24, 24
    sbx, sby, sbw, sbh = 0, 44, 24, 24

    runner.push_back_instance(moving, mbx, mby, mbw, mbh, sbx, sby, sbw, sbh)

    off_y = 30 - mby
    new_mby = moving.y - off_y
    assert new_mby + mbh == sby


def test_zero_offset_matches_simple_separation():
    runner = _runner()
    # origin 0, bbox_left 0 -> bbox-world == raw coords.
    moving = _Inst(30, 0)
    # Horizontal overlap (12) is smaller than vertical (32), so it pushes left.
    runner.push_back_instance(moving, 30, 0, 32, 32, 50, 0, 32, 32)
    # Left push: moving right edge (x+32) flush to static left (50) -> x = 18.
    assert moving.x == 18
