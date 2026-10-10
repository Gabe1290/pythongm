"""Regression tests for editors/object_editor/blockly_widget.py's two
QtWebEngine-packaging helpers, added after a real classroom report
(2026-10-10): clicking the Blockly tab crashed the whole compiled Linux
build, not just that tab. A QtWebEngineProcess that fails to start because
a system shared library is missing can abort the whole host process in some
Qt/Chromium version combinations -- a Python try/except cannot catch that,
so qtwebengine_missing_libraries() checks with `ldd` (safe, read-only)
*before* ever constructing a QWebEngineView, and
create_visual_programming_tab() (object_editor_main.py) turns a detected gap
into this tab's existing fallback label instead of attempting construction.

blockly_message_file() is tested too: it had the same "Path(__file__) is not
a reliable filesystem path inside a PyInstaller onefile's PYZ archive" bug
_load_blockly_html() already handles correctly, found while investigating
this crash (not confirmed as the crash's own cause, but a real latent bug
regardless -- see its own docstring for the fail-safe consequence if wrong).
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6


def _blockly_widget():
    import editors.object_editor.blockly_widget as m
    return m


class TestBlocklyMessageFile:

    def test_source_mode_finds_a_real_language_file(self):
        m = _blockly_widget()
        path = m.blockly_message_file("fr")
        assert path is not None
        assert path.name == "fr.js"
        assert path.is_file()

    def test_english_resolves_to_msg_en_js(self):
        m = _blockly_widget()
        path = m.blockly_message_file("en")
        assert path is not None
        assert path.name == "msg_en.js"

    def test_unknown_language_returns_none(self):
        m = _blockly_widget()
        assert m.blockly_message_file("xx") is None

    def test_frozen_mode_resolves_under_sys_meipass(self, monkeypatch, tmp_path):
        """The bug this guards: blockly_message_file() used
        Path(__file__).resolve().parent unconditionally, which is not a
        real filesystem path for a module bundled into a PyInstaller
        onefile's PYZ archive -- it must check sys.frozen / sys._MEIPASS
        the same way _load_blockly_html() already does."""
        m = _blockly_widget()
        fake_meipass = tmp_path / "meipass"
        fr_file = fake_meipass / "editors" / "object_editor" / "blockly" / "lib" / "msg" / "fr.js"
        fr_file.parent.mkdir(parents=True)
        fr_file.write_text("// fake blockly fr messages", encoding="utf-8")

        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(fake_meipass), raising=False)
        try:
            path = m.blockly_message_file("fr")
            assert path == fr_file
        finally:
            monkeypatch.delattr(sys, "frozen", raising=False)
            monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    def test_frozen_mode_with_no_matching_file_returns_none_not_a_crash(self, monkeypatch, tmp_path):
        m = _blockly_widget()
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
        try:
            assert m.blockly_message_file("fr") is None
        finally:
            monkeypatch.delattr(sys, "frozen", raising=False)
            monkeypatch.delattr(sys, "_MEIPASS", raising=False)


class TestQtWebEngineMissingLibraries:

    def test_returns_none_when_ldd_is_unavailable(self):
        m = _blockly_widget()
        with patch("shutil.which", return_value=None):
            assert m.qtwebengine_missing_libraries() is None

    def test_returns_none_on_windows_or_macos(self):
        m = _blockly_widget()
        with patch.object(sys, "platform", "win32"):
            assert m.qtwebengine_missing_libraries() is None
        with patch.object(sys, "platform", "darwin"):
            assert m.qtwebengine_missing_libraries() is None

    def test_returns_none_when_the_library_cannot_be_located(self, tmp_path):
        m = _blockly_widget()
        fake_pyside6 = tmp_path / "PySide6" / "__init__.py"
        fake_pyside6.parent.mkdir(parents=True)
        fake_pyside6.write_text("", encoding="utf-8")
        with patch("shutil.which", return_value="/usr/bin/ldd"), \
             patch("PySide6.__file__", str(fake_pyside6)):
            # no Qt/lib/libQt6WebEngineCore.so* under this fake tree
            assert m.qtwebengine_missing_libraries() is None

    def test_parses_not_found_lines_from_ldd_output(self, tmp_path):
        """The actual detection logic: given real ldd-shaped output naming
        missing libraries, the function must extract exactly those names."""
        m = _blockly_widget()
        fake_lib_dir = tmp_path / "PySide6" / "Qt" / "lib"
        fake_lib_dir.mkdir(parents=True)
        fake_lib = fake_lib_dir / "libQt6WebEngineCore.so.6"
        fake_lib.write_bytes(b"")
        fake_pyside6_init = tmp_path / "PySide6" / "__init__.py"
        fake_pyside6_init.write_text("", encoding="utf-8")

        ldd_output = (
            "\tlinux-vdso.so.1 (0x00007fff)\n"
            "\tlibnss3.so => not found\n"
            "\tlibgbm.so.1 => not found\n"
            "\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f00)\n"
        )
        fake_result = MagicMock(stdout=ldd_output)
        with patch("shutil.which", return_value="/usr/bin/ldd"), \
             patch("PySide6.__file__", str(fake_pyside6_init)), \
             patch("subprocess.run", return_value=fake_result) as run:
            missing = m.qtwebengine_missing_libraries()

        assert missing == ["libgbm.so.1", "libnss3.so"]
        run.assert_called_once()
        assert run.call_args[0][0] == ["ldd", str(fake_lib)]

    def test_returns_none_when_nothing_is_missing(self, tmp_path):
        m = _blockly_widget()
        fake_lib_dir = tmp_path / "PySide6" / "Qt" / "lib"
        fake_lib_dir.mkdir(parents=True)
        (fake_lib_dir / "libQt6WebEngineCore.so.6").write_bytes(b"")
        fake_pyside6_init = tmp_path / "PySide6" / "__init__.py"
        fake_pyside6_init.write_text("", encoding="utf-8")

        fake_result = MagicMock(stdout="\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f00)\n")
        with patch("shutil.which", return_value="/usr/bin/ldd"), \
             patch("PySide6.__file__", str(fake_pyside6_init)), \
             patch("subprocess.run", return_value=fake_result):
            assert m.qtwebengine_missing_libraries() is None

    def test_frozen_mode_looks_under_sys_meipass(self, monkeypatch, tmp_path):
        m = _blockly_widget()
        fake_lib_dir = tmp_path / "PySide6" / "Qt" / "lib"
        fake_lib_dir.mkdir(parents=True)
        fake_lib = fake_lib_dir / "libQt6WebEngineCore.so.6"
        fake_lib.write_bytes(b"")

        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
        fake_result = MagicMock(stdout="")
        try:
            with patch("shutil.which", return_value="/usr/bin/ldd"), \
                 patch("subprocess.run", return_value=fake_result) as run:
                m.qtwebengine_missing_libraries()
            assert run.call_args[0][0] == ["ldd", str(fake_lib)]
        finally:
            monkeypatch.delattr(sys, "frozen", raising=False)
            monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    def test_survives_a_hanging_or_erroring_ldd(self, tmp_path):
        """ldd itself is a well-behaved system tool, but this must still
        degrade to "no diagnostic" rather than raise, since it runs ahead
        of ordinary tab creation and must never be the thing that breaks
        opening an object editor."""
        import subprocess
        m = _blockly_widget()
        fake_lib_dir = tmp_path / "PySide6" / "Qt" / "lib"
        fake_lib_dir.mkdir(parents=True)
        (fake_lib_dir / "libQt6WebEngineCore.so.6").write_bytes(b"")
        fake_pyside6_init = tmp_path / "PySide6" / "__init__.py"
        fake_pyside6_init.write_text("", encoding="utf-8")

        with patch("shutil.which", return_value="/usr/bin/ldd"), \
             patch("PySide6.__file__", str(fake_pyside6_init)), \
             patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ldd", 5)):
            assert m.qtwebengine_missing_libraries() is None

    def test_this_machine_reports_no_missing_libraries(self):
        """A real, unmocked run against this dev box's actual PySide6
        install -- confirmed by hand (ldd) while investigating the crash
        report that nothing is missing here, so this pins that baseline."""
        m = _blockly_widget()
        assert m.qtwebengine_missing_libraries() is None


class TestCreateVisualProgrammingTabFallback:
    """object_editor_main.py's create_visual_programming_tab -- a detected
    missing-library gap must become the tab's ordinary fallback label, not
    an attempt to construct a QWebEngineView."""

    @pytest.fixture(autouse=True)
    def _qapp(self):
        # QWidget construction (the fallback QLabel, or a real
        # BlocklyVisualProgrammingTab) aborts hard without a live
        # QApplication -- this class is the only one in this file that
        # builds real widgets, so it needs its own instance explicitly.
        from PySide6.QtWidgets import QApplication
        QApplication.instance() or QApplication([])
        yield

    def test_missing_libraries_produce_the_fallback_label_not_a_blockly_tab(self):
        """A bare MagicMock() as `self` is deliberately NOT used here: PySide6's
        Signal.connect() expects a real Python callable, and handing it a
        MagicMock instead crashed the *test* hard (a native abort, not a
        catchable exception) the first time this was written -- a test
        artifact, not a real repro of the reported bug, but worth the plain
        functions below instead of chasing that down."""
        from types import SimpleNamespace
        from editors.object_editor.object_editor_main import ObjectEditor
        from PySide6.QtWidgets import QLabel

        stub = SimpleNamespace(
            tr=lambda s: s,
            blockly_tab="sentinel",
            on_blockly_events_modified=lambda *a, **k: None,
            on_blockly_config_changed=lambda *a, **k: None,
        )

        with patch("editors.object_editor.blockly_widget.qtwebengine_missing_libraries",
                   return_value=["libnss3.so"]):
            result = ObjectEditor.create_visual_programming_tab(stub)

        assert isinstance(result, QLabel)
        assert "libnss3.so" in result.text()
        assert stub.blockly_tab is None  # cleared by the except branch

    def test_no_missing_libraries_constructs_a_real_blockly_tab(self):
        """The inverse case: when the check reports nothing missing, a real
        BlocklyVisualProgrammingTab is still constructed (the guard doesn't
        accidentally block the normal, working path)."""
        from types import SimpleNamespace
        from editors.object_editor.object_editor_main import ObjectEditor
        from editors.object_editor.blockly_widget import BlocklyVisualProgrammingTab

        stub = SimpleNamespace(
            tr=lambda s: s,
            blockly_tab=None,
            on_blockly_events_modified=lambda *a, **k: None,
            on_blockly_config_changed=lambda *a, **k: None,
        )

        with patch("editors.object_editor.blockly_widget.qtwebengine_missing_libraries",
                   return_value=None):
            result = ObjectEditor.create_visual_programming_tab(stub)

        assert isinstance(result, BlocklyVisualProgrammingTab)
        assert stub.blockly_tab is result
