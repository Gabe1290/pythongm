"""Regression test: the ThymioPlaygroundWindow f-string-in-tr() dead
translation bug.

widgets/thymio_playground.py used `self.tr(f"Zoom: {int(...)}%")` style
calls in 7 messages (8 call sites) — an f-string is fully interpolated
BEFORE being passed to tr(), so Qt's translate() only ever saw the
already-substituted runtime string (e.g. "Zoom: 150%"), never the literal
template text every language's .ts had translated. Those 7 translations
were real and complete but could never reach the running app in ANY
language — the same failure MODE as the self.ide dead-context bug
(tests/test_self_ide_context_fix.py), caused by broken source code
instead of a wrong translation-context name. One message (the second
pan_label update, in _update_status_panel) had no tr() call at all.

Two more wrinkles specific to this bug, both fixed here:
- The split pygm2_<lang>_misc.ts copies (the files ACTUALLY shipped for
  de/it/ru/sl/uk) had these 7 messages marked type="vanished" with no
  <location> — lrelease excludes vanished entries from the compiled
  .qm entirely, so they were doubly dead there. es/fr (monolithic-
  shipping) didn't have this second problem.
- Two of the seven messages interpolate an English state word
  ("on"/"off"/"paused"/"running") that was never itself wrapped in
  tr() — fixed by translating the word at its point of construction
  instead of just the surrounding template.

Fixed in widgets/thymio_playground.py to use
self.tr("Zoom: {0}%").format(...) placeholder-style calls, and every
already-shipped language's real translation was re-filed under the new
placeholder source text (un-vanished + given real <location> tags where
needed).

Uses a hand-rolled offscreen QApplication (no qapp fixture) per this
repo's audit-regression convention.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANS_DIR = REPO_ROOT / "translations"
SOURCE_FILE = REPO_ROOT / "widgets" / "thymio_playground.py"

SHIPPED_QM = {
    "de": TRANS_DIR / "pygm2_de_misc.qm",
    "it": TRANS_DIR / "pygm2_it_misc.qm",
    "ru": TRANS_DIR / "pygm2_ru_misc.qm",
    "sl": TRANS_DIR / "pygm2_sl_misc.qm",
    "uk": TRANS_DIR / "pygm2_uk_misc.qm",
    "es": TRANS_DIR / "pygm2_es.qm",
    "fr": TRANS_DIR / "pygm2_fr.qm",
}


def test_source_has_no_fstring_tr_calls():
    content = SOURCE_FILE.read_text(encoding="utf-8")
    assert 'self.tr(f"' not in content, (
        "widgets/thymio_playground.py still calls self.tr() with an "
        "f-string — the interpolated value would bypass translation "
        "entirely (fix regressed)"
    )


def test_runtime_zoom_and_pan_labels_translate():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTranslator

    app = QApplication.instance() or QApplication([])
    from widgets.thymio_playground import ThymioPlaygroundWindow

    for lang, qm_path in SHIPPED_QM.items():
        if not qm_path.exists():
            continue
        translator = QTranslator()
        assert translator.load(str(qm_path)), f"{qm_path.name} failed to load"
        app.installTranslator(translator)
        try:
            window = ThymioPlaygroundWindow()
            window.zoom_level = 1.5
            window.camera_x = 10
            window.camera_y = -5
            window._update_zoom_label()
            zoom_text = window.zoom_label.text()
            pan_text = window.pan_label.text()
            assert "150" in zoom_text, f"{lang}: zoom label missing value: {zoom_text!r}"
            assert "10" in pan_text and "-5" in pan_text, (
                f"{lang}: pan label missing values: {pan_text!r}"
            )
            # The literal Python-expression text must never leak through.
            assert "int(self.zoom_level" not in zoom_text
            assert "int(self.camera_x)" not in pan_text
        finally:
            app.removeTranslator(translator)
            window.close()


def test_runtime_sensor_state_word_is_translated():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTranslator

    app = QApplication.instance() or QApplication([])
    from widgets.thymio_playground import ThymioPlaygroundWindow

    translator = QTranslator()
    de_qm = SHIPPED_QM["de"]
    if not de_qm.exists():
        return
    assert translator.load(str(de_qm))
    app.installTranslator(translator)
    try:
        window = ThymioPlaygroundWindow()
        window.renderer.toggle_sensors()  # turns sensors ON
        window.toggle_sensors()  # toggles again -> reports current state
        message = window.statusbar.currentMessage()
        assert "{state}" not in message
        assert "{0}" not in message
        # German "on"/"off" words, not the raw English "on"/"off".
        assert message in (
            "Sensorvisualisierung: ein",
            "Sensorvisualisierung: aus",
        ), message
    finally:
        app.removeTranslator(translator)
        window.close()
