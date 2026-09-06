#!/usr/bin/env python3
"""Colour parsing shared by the action executor and its mixins.

``_hex_to_rgb`` lived at module level in ``runtime/action_executor.py`` and is
used from two different action clusters (the high-score screen and
``set_draw_color``), so splitting those into sibling mixin modules
(``docs/POST_1_0_REFACTOR.md`` File 4) needed a home that neither imports from
the other -- importing it back out of ``action_executor`` would be circular.

The name is deliberately unchanged, underscore and all: keeping it identical
means every call site's bytecode is untouched, so the extraction proof can
still assert byte-for-byte body equality against pre-refactor HEAD.
"""

from typing import Tuple


def _hex_to_rgb(hex_str: str, default: Tuple[int, int, int] = (0, 0, 0)) -> Tuple[int, int, int]:
    """Parse ``#RRGGBB`` (or ``RRGGBB``) to an ``(r, g, b)`` 0-255 tuple.

    Returns ``default`` on empty input or any parse failure.
    """
    if not hex_str:
        return default
    try:
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError, TypeError):
        return default
