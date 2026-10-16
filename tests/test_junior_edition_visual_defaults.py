"""docs/KID_UI_SIMPLIFICATION_PLAN.md Phase 2.5: visual restyling for the
"junior" edition -- a high-contrast color theme, a bigger default UI font
size, and bigger main-toolbar icons for easier click targets.

The theme/font-size defaults must apply only when the user has never
explicitly customized the matching setting via Preferences (checked
against the raw saved config, see config.editions.
resolve_startup_visual_overrides) -- picking the "Junior" edition should
never silently override a teacher's own theme/font choice on a shared
machine. The toolbar icon size has no such saved-preference knob to
check against, so it always applies for the tier.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


class TestResolveStartupVisualOverrides:
    def test_junior_with_nothing_customized_gets_the_junior_defaults(self):
        from config.editions import resolve_startup_visual_overrides
        result = resolve_startup_visual_overrides({"edition": "junior"})
        assert result == {"theme": "junior", "font_size": 13}

    def test_junior_with_an_explicit_theme_and_font_size_keeps_them(self):
        from config.editions import resolve_startup_visual_overrides
        result = resolve_startup_visual_overrides({
            "edition": "junior",
            "appearance": {"theme": "dark"},
            "font": {"size": 11},
        })
        assert result == {"theme": None, "font_size": None}

    def test_junior_with_only_the_theme_customized_still_overrides_font_size(self):
        from config.editions import resolve_startup_visual_overrides
        result = resolve_startup_visual_overrides({
            "edition": "junior",
            "appearance": {"theme": "dark"},
        })
        assert result == {"theme": None, "font_size": 13}

    @pytest.mark.parametrize("edition_key", ["beginner", "advanced", "development"])
    def test_other_editions_never_override_anything(self, edition_key):
        from config.editions import resolve_startup_visual_overrides
        result = resolve_startup_visual_overrides({"edition": edition_key})
        assert result == {"theme": None, "font_size": None}

    def test_unset_edition_key_falls_back_to_the_default_edition(self):
        from config.editions import resolve_startup_visual_overrides
        from config.editions import DEFAULT_EDITION
        assert DEFAULT_EDITION != "junior"
        result = resolve_startup_visual_overrides({})
        assert result == {"theme": None, "font_size": None}


@pytest.fixture(scope="module")
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_junior_theme_applies_a_real_distinct_palette(_qapp):
    """A real round trip through ThemeManager, not just the JSON file --
    confirms the "junior" entry is wired up the same way dark/light are."""
    from utils.theme_manager import ThemeManager
    from PySide6.QtGui import QPalette

    ThemeManager.apply_theme("light")
    light_window = _qapp.palette().color(QPalette.Window).name()

    ThemeManager.apply_theme("junior")
    junior_window = _qapp.palette().color(QPalette.Window).name()
    junior_highlight = _qapp.palette().color(QPalette.Highlight).name()

    assert junior_window != light_window, "junior theme didn't actually change the palette"
    assert junior_window == "#fffdf4"
    assert junior_highlight == "#ffca28"


@pytest.fixture
def _edition(request):
    from utils.config import Config
    original = Config.get("edition", None)
    Config.set("edition", request.param)
    yield request.param
    Config.set("edition", original)


def _main_toolbar(ide):
    from PySide6.QtWidgets import QToolBar
    return ide.findChild(QToolBar, "MainToolbar")


@pytest.mark.parametrize("_edition", ["junior"], indirect=True)
def test_junior_edition_gets_bigger_toolbar_icons(_qapp, _edition):
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    toolbar = _main_toolbar(ide)
    assert toolbar is not None
    assert toolbar.iconSize().width() == 32
    assert toolbar.iconSize().height() == 32


@pytest.mark.parametrize("_edition", ["beginner", "advanced", "development"], indirect=True)
def test_other_editions_keep_the_default_toolbar_icon_size(_qapp, _edition):
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    toolbar = _main_toolbar(ide)
    assert toolbar is not None
    assert toolbar.iconSize().width() == 16
    assert toolbar.iconSize().height() == 16
