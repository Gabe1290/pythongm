"""widgets/qt_helpers.py -- small generic Qt helpers.

Pure logic, no live QApplication needed: as_hashable_tuple normalises an
already-retrieved item.data(...) value, it never touches a Qt widget itself.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from widgets.qt_helpers import as_hashable_tuple


def test_normalises_a_list_back_into_a_tuple():
    """The exact PySide6 6.10 hazard this exists for: setData stores a
    tuple, Qt hands a list back on read."""
    assert as_hashable_tuple(["sprites", "spr_player"]) == ("sprites", "spr_player")


def test_leaves_a_real_tuple_alone():
    assert as_hashable_tuple(("sprites", "spr_player")) == ("sprites", "spr_player")


def test_result_is_hashable():
    """The whole point: a caller putting this in a set/dict key must not hit
    TypeError: unhashable type: 'list' on either PySide6 version."""
    hash(as_hashable_tuple(["sprites", "spr_player"]))


def test_non_tuple_shaped_data_is_none():
    assert as_hashable_tuple(None) is None
    assert as_hashable_tuple("just a string") is None
    assert as_hashable_tuple(42) is None
