#!/usr/bin/env python3
"""Small, generic Qt helpers shared across widgets.

Kept separate from any one dialog/widget module: the hazards these guard
against (Qt/PySide6 version-dependent round-trip behaviour, mostly) are
properties of Qt itself, not of whichever widget happened to hit them first.
"""


def as_hashable_tuple(data):
    """Normalise Qt item data that should be a tuple back into a real one,
    or None if it isn't tuple-shaped data at all.

    Takes the already-retrieved value (``item.data(...)``), not the item
    itself: ``QTreeWidgetItem.data(column, role)`` and
    ``QListWidgetItem.data(role)`` take different arguments, so there is no
    one call this helper could make on the caller's behalf -- only the
    normalisation is generic.

    Why this exists: ``setData`` stores a Python tuple, but Qt round-trips
    it through ``QVariant``, and PySide6 6.10 hands back a **list** where 6.9
    handed back the tuple it was given. A caller that only unpacks the value
    doesn't notice; a caller that hashes it -- putting it in a set, keying a
    dict -- gets ``TypeError: unhashable type: 'list'`` on one PySide6 and
    works fine on the other. Normalising on read makes the contract
    version-independent instead of leaving a trap for the next caller to
    rediscover.

    Found and fixed once already for ``widgets.asset_tree.asset_dialogs.
    UnusedAssetsDialog.item_key`` (which now delegates here); extracted so
    the next Qt widget that stores a tuple via ``setData(role, (a, b))`` can
    call this instead of re-deriving the fix.
    """
    return tuple(data) if isinstance(data, (list, tuple)) else None
