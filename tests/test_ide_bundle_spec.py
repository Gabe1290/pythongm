"""Guards for PyGameMaker.spec -- the PyInstaller spec that produces the
downloadable IDE builds (GitHub Releases, .github/workflows/build.yml).

The regression this exists for: `plugins/` and `extensions/` are loaded
OFF DISK at runtime by events/plugin_loader.get_app_root() (which points
at sys._MEIPASS when frozen). If the spec's Tree list stops bundling
them, the packaged app silently loads zero plugins/extensions -- every
Network / audio / 2.5D-renderer action just does nothing, with no error.
`samples/` had the same omission once (commit d0de97ab).
"""
import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC = REPO_ROOT / "PyGameMaker.spec"


def _bundled_dirs():
    """The (source_dir) entries from the spec's `for _dir, _prefix in [...]`
    Tree loop, pulled out via AST so a commented-out line can't satisfy the
    check."""
    tree = ast.parse(SPEC.read_text(encoding="utf-8"), str(SPEC))
    dirs = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.For):
            continue
        it = node.iter
        if not isinstance(it, ast.List):
            continue
        for elt in it.elts:
            if (isinstance(elt, ast.Tuple) and elt.elts
                    and isinstance(elt.elts[0], ast.Constant)
                    and isinstance(elt.elts[0].value, str)):
                dirs.append(elt.elts[0].value)
    return dirs


def test_spec_is_valid_python():
    ast.parse(SPEC.read_text(encoding="utf-8"), str(SPEC))


def test_bundles_the_runtime_loaded_dirs():
    dirs = _bundled_dirs()
    for required in ("extensions", "plugins", "samples", "Tutorials", "templates"):
        assert required in dirs, (
            f"PyGameMaker.spec no longer bundles {required!r} -- the frozen "
            f"build will be missing it (loaded: {dirs})")
        assert (REPO_ROOT / required).is_dir(), (
            f"spec bundles {required!r} but it's not a real dir")


def test_extensions_dir_actually_has_the_folder_extensions():
    # Sanity: the thing we're bundling is the real extension set, so the
    # frozen loader has something to find.
    ext = REPO_ROOT / "extensions"
    folders = {p.name for p in ext.iterdir()
               if p.is_dir() and (p / "extension.json").exists()}
    assert {"multiplayer_lan", "raycast_2_5d", "block_world"} <= folders
