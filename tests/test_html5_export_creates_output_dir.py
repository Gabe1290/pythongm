"""HTML5 export into a folder that doesn't exist yet.

Every write in HTML5Exporter.export assumed output_path already existed, so
exporting to a new folder failed with "No such file or directory" (found
while investigating the 2026-10-07 classroom USB-stick report). The exporter
now creates the destination itself.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_export_creates_missing_nested_output_dir(tmp_path):
    from export.HTML5.html5_exporter import HTML5Exporter

    out = tmp_path / "new_folder" / "nested"
    assert not out.exists()

    exporter = HTML5Exporter()
    assert exporter.export(REPO / "samples" / "maze_1", out) is True, \
        exporter.last_error_message
    assert list(out.glob("*.html")), "no .html file written"


def test_export_into_existing_dir_still_works(tmp_path):
    from export.HTML5.html5_exporter import HTML5Exporter

    exporter = HTML5Exporter()
    assert exporter.export(REPO / "samples" / "maze_1", tmp_path) is True, \
        exporter.last_error_message
    assert list(tmp_path.glob("*.html"))
