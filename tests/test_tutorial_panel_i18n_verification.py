"""Section L final verification (docs/I18N_CLEANUP_2026-08-06.md).

The registry's last open Section L checkbox calls for opening the Tutorial
panel in a running IDE with each localized language selected and confirming
every lesson appears and every page loads — a step this headless environment
can't perform by hand. This drives the real ``TutorialPanel`` widget through
the exact same code path a click-through would (``set_tutorials_path`` ->
``load_tutorial_list`` -> ``open_tutorial_by_data`` -> ``load_current_page``
for every page of every lesson), for every language that ships a
``Tutorials/<lang>/`` folder, and asserts the widget never falls into one of
its own error/placeholder branches ("Tutorial not found", "No content",
"Error loading page", "No tutorials available").
"""
import json
from pathlib import Path

import pytest

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

TUTORIALS_ROOT = Path(__file__).resolve().parent.parent / "Tutorials"

# Section L's scope: the six additive lesson-9 languages plus pt (built from
# scratch). fr predates this registry but is included for free since it also
# ships a Tutorials/fr/ folder and costs nothing extra to verify.
LOCALIZED_LANGUAGES = ["de", "es", "fr", "it", "pt", "ru", "sl", "uk"]

_ERROR_MARKERS = (
    "Tutorial not found",
    "No content",
    "Error loading page",
    "No tutorials available",
    "No tutorials folder found",
)


def _make_app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


@pytest.fixture
def language(request):
    """Force LanguageManager.get_current_language() to a fixed code, then restore.

    Also forces the edition to "development" (tutorial_folders=None, i.e. show
    all lessons) — the app's real DEFAULT_EDITION ("beginner") only surfaces
    lessons 1-4, and this verification is specifically about every lesson in
    every language, not the beginner-filtered subset.
    """
    from core.language_manager import get_language_manager
    from utils.config import Config

    manager = get_language_manager()
    original_lang = manager.current_language
    original_edition = Config.get("edition", None)

    manager.current_language = request.param
    Config.set("edition", "development")
    yield request.param
    manager.current_language = original_lang
    Config.set("edition", original_edition)


@pytest.mark.parametrize("language", LOCALIZED_LANGUAGES, indirect=True)
def test_localized_folder_is_selected(language):
    """localized_tutorials_path() resolves to Tutorials/<lang>, not the English root."""
    _make_app()
    from widgets.tutorial_panel import TutorialPanel

    panel = TutorialPanel()
    panel.set_tutorials_path(TUTORIALS_ROOT)

    assert panel.tutorials_path == TUTORIALS_ROOT / language


@pytest.mark.parametrize("language", LOCALIZED_LANGUAGES, indirect=True)
def test_tutorial_list_matches_index_json(language):
    """Every tutorial named in index.json appears in the loaded list widget."""
    _make_app()
    from widgets.tutorial_panel import TutorialPanel

    index_path = TUTORIALS_ROOT / language / "index.json"
    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)
    expected_titles = [t["title"] for t in index_data["tutorials"]]

    panel = TutorialPanel()
    panel.set_tutorials_path(TUTORIALS_ROOT)

    actual_titles = [panel.tutorial_list.item(i).text()
                      for i in range(panel.tutorial_list.count())]

    assert actual_titles == expected_titles
    for i in range(panel.tutorial_list.count()):
        item = panel.tutorial_list.item(i)
        data = item.data(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.UserRole)
        assert isinstance(data, dict) and "folder" in data


@pytest.mark.parametrize("language", LOCALIZED_LANGUAGES, indirect=True)
def test_every_lesson_every_page_loads(language):
    """Walk every lesson and every page via the widget's own open/navigate path."""
    _make_app()
    from widgets.tutorial_panel import TutorialPanel

    index_path = TUTORIALS_ROOT / language / "index.json"
    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    panel = TutorialPanel()
    panel.set_tutorials_path(TUTORIALS_ROOT)

    for tutorial in index_data["tutorials"]:
        panel.open_tutorial_by_data(tutorial)

        # open_tutorial_by_data must have switched to the content page, not
        # bailed into the list page (which it does on a hard failure).
        assert panel.stack.currentIndex() == 1
        assert len(panel.tutorial_pages) == len(tutorial["pages"]), (
            f"{language}/{tutorial['folder']}: expected "
            f"{len(tutorial['pages'])} pages, resolved {len(panel.tutorial_pages)}"
        )

        for page_index in range(len(panel.tutorial_pages)):
            panel.current_page_index = page_index
            panel.load_current_page()

            html = panel.content_browser.toHtml()
            plain = panel.content_browser.toPlainText()

            for marker in _ERROR_MARKERS:
                assert marker not in plain, (
                    f"{language}/{tutorial['folder']} page {page_index}: "
                    f"hit fallback branch {marker!r}"
                )
            # A real lesson page renders substantial prose, not a stub.
            assert len(plain.strip()) > 100, (
                f"{language}/{tutorial['folder']} page {page_index}: "
                f"suspiciously short rendered content ({len(plain.strip())} chars)"
            )
            assert html  # QTextBrowser always produces non-empty HTML once set


def test_ja_zh_fall_back_to_english_root_cleanly():
    """ja/zh have no Tutorials/<lang>/ folder yet (out of Section L's original
    scope) — the loader must fall back to the English root rather than error,
    and that fallback must itself be fully usable."""
    _make_app()
    from core.language_manager import get_language_manager
    from widgets.tutorial_panel import TutorialPanel

    manager = get_language_manager()
    original = manager.current_language
    try:
        for lang in ("ja", "zh"):
            assert not (TUTORIALS_ROOT / lang).exists()
            manager.current_language = lang

            panel = TutorialPanel()
            panel.set_tutorials_path(TUTORIALS_ROOT)

            assert panel.tutorials_path == TUTORIALS_ROOT
            assert panel.tutorial_list.count() > 0
            first_item = panel.tutorial_list.item(0)
            assert "No tutorials" not in first_item.text()
    finally:
        manager.current_language = original
