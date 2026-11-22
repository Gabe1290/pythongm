"""The exported Aseba program's header names both ways to run it (2026-11-22).

It used to say only "Upload this code ... using Aseba Studio", but the same
source is what File -> Send to Thymio robot... compiles on the robot with no
Aseba Studio at all. The header now names both paths, and the menu label it
quotes must stay the real one.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extensions.thymio.export.aseba_exporter import AsebaExporter  # noqa: E402


def _header():
    return AsebaExporter()._generate_header("thymio_bot", {"name": "Demo"})


def test_the_header_names_send_to_thymio_and_aseba_studio():
    h = _header()
    assert "File -> Send to Thymio robot..." in h
    assert "no Aseba Studio needed" in h
    assert 'open the exported .aesl file, click "Load", then "Run".' in h
    assert "Upload this code to your Thymio robot using Aseba Studio" not in h


def test_every_header_line_is_an_aseba_comment():
    """The header is compiled on the robot by Send to Thymio: every line must
    be a comment or the program fails to compile."""
    for line in _header().splitlines():
        assert line.startswith("#"), line


def test_the_quoted_menu_label_is_the_real_one():
    menu = (ROOT / "extensions" / "thymio" / "__init__.py").read_text(encoding="utf-8")
    label = re.search(r'ide\.tr\("(Send to &Thymio robot\.\.\.)"\)', menu).group(1)
    assert label.replace("&", "") in _header()


def test_the_exported_readme_mentions_send_to_thymio(tmp_path):
    readme = tmp_path / "README.md"
    AsebaExporter()._generate_readme(readme, {"name": "Demo"}, {"thymio_bot": {}})
    text = readme.read_text(encoding="utf-8")
    assert "File → Send to Thymio robot..." in text and "with no Aseba Studio" in text
    assert "click File → Open" in text          # the Aseba Studio steps stay
