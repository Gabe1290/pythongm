"""End-to-end guard: the generated Kivy main.py (with the SoundLoader-backed
play_sound helper) must be valid Python.

The play_sound helper was added inside main.py's .format() template, where a
literal `{` must be written `{{`. A missed doubling would either raise
KeyError at format() time or emit broken source. This test exports a real
sample project and byte-compiles the generated main.py + object modules so any
brace-escaping regression fails loudly.
"""

import json
import py_compile
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import skip_without_pyside6

pytestmark = skip_without_pyside6

REPO_ROOT = Path(__file__).parent.parent
SAMPLE = REPO_ROOT / "samples" / "plateforme_1"


@pytest.mark.skipif(not (SAMPLE / "project.json").exists(),
                    reason="bundled sample not present in this checkout")
def test_exported_main_py_compiles_with_play_sound_helper(tmp_path):
    from export.Kivy.kivy_exporter import KivyExporter

    data = json.loads((SAMPLE / "project.json").read_text(encoding="utf-8"))
    out = tmp_path / "export"
    exporter = KivyExporter(data, SAMPLE, out)
    assert exporter.export() is True

    main_py = out / "game" / "main.py"
    assert main_py.exists()
    # Byte-compile: fails on any brace/format breakage in the template.
    py_compile.compile(str(main_py), doraise=True)

    text = main_py.read_text(encoding="utf-8")
    assert "def play_sound(path" in text
    assert "_sound_cache = {}" in text  # the doubled {{}} rendered to {}

    # Object modules (which may emit `from main import play_sound`) compile too.
    for obj in (out / "game" / "objects").glob("*.py"):
        py_compile.compile(str(obj), doraise=True)
