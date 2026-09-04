"""Regression: SamplesMixin._samples_dir must resolve to the repo-root
samples/ folder, not core/samples.

When the method moved from core/ide_window.py (1 dir deep) to
core/ide/_samples.py (2 dirs deep) in the File-2 refactor, its
``Path(__file__).resolve().parent.parent`` climbed one level too few and
pointed at core/samples/ (nonexistent). No existing test asserted the
path, so the full suite stayed green while sample-opening was broken for a
real IDE run. Fixed to ``.parents[2]``.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.ide._samples import SamplesMixin


class _Host(SamplesMixin):
    pass


def test_samples_dir_points_at_repo_root_samples():
    d = _Host()._samples_dir()
    repo_root = Path(__file__).resolve().parent.parent
    assert d == (repo_root / "samples").resolve()
    assert d.is_dir()
    # a bundled sample every checkout has
    assert (d / "maze_1").is_dir()


def test_is_samples_path_recognises_a_bundled_sample():
    host = _Host()
    d = host._samples_dir()
    assert host._is_samples_path(d / "maze_1") is True
    assert host._is_samples_path(Path("/tmp/not-a-sample")) is False
