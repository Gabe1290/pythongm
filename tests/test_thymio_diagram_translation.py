"""The Thymio tab's robot diagram (its FRONT / GND labels and hover tooltips) is translated, and fiche 1's
screenshot of the tab exists. The labels used to be hard-coded English in every language."""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest

pytest.importorskip("PySide6")

FRENCH = {
    "FRONT": "AVANT",
    "GND": "SOL",
    "Forward Button": "Bouton avant",
    "Proximity Sensor 2 (Front Center)": "Capteur de proximité 2 (avant centre)",
    "Circle LED 0 (Front)": "LED du cercle 0 (avant)",
}


def test_every_tooltip_and_label_has_a_french_translation():
    from PySide6.QtCore import QCoreApplication, QTranslator
    from PySide6.QtWidgets import QApplication
    from extensions.thymio.diagram_widget import ThymioDiagramWidget

    app = QApplication.instance() or QApplication([])
    translator = QTranslator()
    assert translator.load(str(REPO_ROOT / "translations" / "pygm2_fr.qm"))
    app.installTranslator(translator)
    try:
        for source, expected in FRENCH.items():
            assert QCoreApplication.translate("ThymioDiagramWidget", source) == expected
        for text in ThymioDiagramWidget.REGION_DESCRIPTIONS.values():
            assert QCoreApplication.translate("ThymioDiagramWidget", text) != text, text
    finally:
        app.removeTranslator(translator)


def test_the_source_translates_where_it_draws_and_shows_tooltips():
    src = (REPO_ROOT / "extensions" / "thymio" / "diagram_widget.py").read_text(encoding="utf-8")
    assert 'translate("ThymioDiagramWidget", "FRONT")' in src
    assert src.count('translate("ThymioDiagramWidget", "GND")') == 2
    assert 'self.REGION_DESCRIPTIONS.get(new_hover, new_hover)' in src
    assert re.search(r'translate\(\s*"ThymioDiagramWidget",\s*self\.REGION_DESCRIPTIONS', src)


def test_fiche_1_shows_the_thymio_tab_screenshot():
    md = REPO_ROOT / "docs" / "thymio_fiches" / "fiche_1.fr.md"
    match = re.search(r"!\[[^\]]*\]\(([^)]+\.png)\)", md.read_text(encoding="utf-8"))
    assert match, "fiche 1 has no screenshot"
    image = md.parent / match.group(1)
    assert image.is_file() and image.stat().st_size > 10_000
