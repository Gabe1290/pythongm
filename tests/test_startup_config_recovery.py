"""Regression tests: a damaged ~/.pygamemaker/config.json no longer stops the IDE.

Classroom incident 2026-11-18 (Debian 12, release build): after some language
switching and restarts the IDE closed at once on every launch -- through
logout, reboot and a fresh download -- until the student's account was
deleted. Starting the real IDE against damaged configs showed that a
wrong-typed entry (font, appearance, editor, recent_projects ...) made
startup raise, and main() just printed to a console nobody sees and exited.

main.py now moves the damaged file aside (config.json.broken-<timestamp>),
logs the traceback to ~/.pygamemaker/startup_error.log and starts again with
defaults; if that fails too it shows a dialog instead of vanishing.

The subprocess tests run the REAL main.py (offscreen, isolated HOME) through
a tiny driver that quits once the main window is shown.
"""

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO = Path(__file__).resolve().parent.parent

DRIVER = textwrap.dedent("""
    import os, runpy, sys
    sys.path.insert(0, os.getcwd())
    sys.argv = [sys.argv[0]]
    mod = runpy.run_path("main.py", run_name="pygm_main")
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QMessageBox
    QMessageBox.critical = staticmethod(
        lambda *a, **k: print("FATAL_DIALOG:", a[2].replace(chr(10), " | "), flush=True))
    ide_cls = mod["PyGameMakerIDE"]
    if os.environ.get("BREAK_IDE") == "1":
        def boom(self, *a, **k):
            raise RuntimeError("ide construction always fails")
        ide_cls.__init__ = boom
    orig_show = ide_cls.show
    def show(self):
        orig_show(self)
        print("IDE_SHOWN", flush=True)
        QTimer.singleShot(200, QApplication.instance().quit)
    ide_cls.show = show
    mod["main"]()
""")


def _run_ide(home, extra_env=None, timeout=120):
    env = dict(os.environ)
    env.update({
        "HOME": str(home), "USERPROFILE": str(home),
        "QT_QPA_PLATFORM": "offscreen",
        "PYGM_ALLOW_MULTIPLE_INSTANCES": "1",
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_DATA_HOME": str(home / ".local" / "share"),
        "XDG_CACHE_HOME": str(home / ".cache"),
        "PYTHONIOENCODING": "utf-8",
    })
    env.update(extra_env or {})
    proc = subprocess.run([sys.executable, "-c", DRIVER], cwd=REPO, env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)
    return proc.returncode, proc.stdout + proc.stderr


def _write_config(home, data):
    cfg_dir = home / ".pygamemaker"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "config.json").write_text(json.dumps(data), encoding="utf-8")


class TestRealStartup:

    @pytest.mark.parametrize("bad", [
        {"language": "fr", "font": None},
        {"language": "pt", "recent_projects": [123, None]},
        {"language": "fr", "editor": None},
        {"appearance": {"theme": "default", "ui_scale": "1,5"}},
    ], ids=["font-null", "recent-int", "editor-null", "scale-str"])
    def test_damaged_config_is_set_aside_and_the_ide_starts(self, tmp_path, bad):
        _write_config(tmp_path, bad)
        rc, out = _run_ide(tmp_path)
        assert "IDE_SHOWN" in out, out[-3000:]
        assert rc == 0, out[-3000:]
        cfg_dir = tmp_path / ".pygamemaker"
        broken = list(cfg_dir.glob("config.json.broken-*"))
        assert len(broken) == 1, list(cfg_dir.iterdir())
        assert json.loads(broken[0].read_text(encoding="utf-8")) == bad
        assert "Traceback" in (cfg_dir / "startup_error.log").read_text(encoding="utf-8")

    def test_a_good_config_is_left_alone(self, tmp_path):
        _write_config(tmp_path, {"language": "fr"})
        rc, out = _run_ide(tmp_path)
        assert "IDE_SHOWN" in out and rc == 0, out[-3000:]
        cfg_dir = tmp_path / ".pygamemaker"
        assert not list(cfg_dir.glob("config.json.broken-*"))
        assert not (cfg_dir / "startup_error.log").exists()
        assert json.loads((cfg_dir / "config.json").read_text())["language"] == "fr"

    def test_a_file_named_like_the_projects_folder_is_not_fatal(self, tmp_path):
        _write_config(tmp_path, {"language": "fr"})
        (tmp_path / "PyGameMaker Projects").write_text("not a folder")
        rc, out = _run_ide(tmp_path)
        assert "IDE_SHOWN" in out and rc == 0, out[-3000:]

    def test_failure_with_defaults_too_shows_a_dialog_instead_of_vanishing(self, tmp_path):
        _write_config(tmp_path, {"language": "fr"})
        rc, out = _run_ide(tmp_path, {"BREAK_IDE": "1"})
        assert rc == 1, out[-3000:]
        assert "IDE_SHOWN" not in out
        dialog = [l for l in out.splitlines() if l.startswith("FATAL_DIALOG:")]
        assert dialog, out[-3000:]
        assert "n'a pas pu démarrer" in dialog[0]
        assert "ide construction always fails" in dialog[0]
        log = (tmp_path / ".pygamemaker" / "startup_error.log").read_text(encoding="utf-8")
        assert log.count("Traceback") == 2  # first try + retry with defaults


class TestQuarantineConfigFile:

    @pytest.fixture
    def config_cls(self, tmp_path, monkeypatch):
        from utils.config import Config
        monkeypatch.setattr(Config, "_config_file", tmp_path / ".pygamemaker" / "config.json")
        monkeypatch.setattr(Config, "_config_data", {})
        return Config

    def test_moves_the_file_and_falls_back_to_defaults(self, config_cls):
        config_cls._config_file.parent.mkdir()
        config_cls._config_file.write_text('{"language": "pt", "font": null}')
        config_cls.load()
        assert config_cls.get("language") == "pt"
        moved = config_cls.quarantine_config_file()
        assert moved is not None and moved.exists()
        assert moved.name.startswith("config.json.broken-")
        assert not config_cls._config_file.exists()
        assert config_cls.get("language", "en") == "en"

    def test_returns_none_when_there_is_no_file(self, config_cls):
        assert config_cls.quarantine_config_file() is None
