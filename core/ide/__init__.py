#!/usr/bin/env python3
"""IDE main-window mixin package.

``core/ide_window.py`` (``PyGameMakerIDE(QMainWindow)``) is being split into
category mixins under this package — see ``docs/POST_1_0_REFACTOR.md`` File 2.
Each ``_<name>.py`` here defines a ``*Mixin`` that ``PyGameMakerIDE`` composes
in; the methods move verbatim, so ``self`` / ``self.tr()`` and every
signal/slot wiring keep resolving on the concrete window via MRO.

``core/ide_window.py`` itself stays put (it is the plan's "window.py" shell)
rather than becoming a re-export shim: ~30 ``mock.patch("core.ide_window.
<NAME>")`` sites across the test suite would otherwise all need repointing
for no functional gain. Each cluster commit repoints only the patch sites
for the methods it moves.

This ``__init__`` deliberately imports nothing — ``core.ide_window`` imports
``core.ide._<name>`` at class-definition time, so a re-export here would be a
circular import.
"""
