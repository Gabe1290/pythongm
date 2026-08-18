"""The desktop exports must ship the REAL pygame engine and the REAL project.

Background (EYEBALL_FIXES_2026-08-16 issues 4-8). The desktop exporters used
to bundle the Kivy code generator, a second engine describing itself as "80%
GameMaker 7.0 compatible". One manual pass over the built .exe files found
five bugs at once -- no tiles, a keyboard that jammed at the first wall, no
wall collision, a player drifting upward, sub-images stuck on frame 0 -- none
of which reproduced in the IDE, because the IDE runs a different engine.

So the guarantee this rework buys is structural, and these tests pin the two
halves of it:

1. the bundled engine is `runtime/game_runner.py` -- the same module Test Game
   runs, not a generated reimplementation;
2. the bundled game is the author's project *verbatim*, so there is no
   transformation step in which the two can drift apart.

Anything asserting rendering behaviour belongs in the engine's own tests; the
point here is that the export cannot substitute a different engine or a
different project.

A real PyInstaller build takes minutes and cannot run in CI, so these tests
exercise everything up to invoking PyInstaller and assert on the staged tree
and the generated .spec. The build itself was verified by hand on 2026-08-17:
maze_1, plateforme_2 and raycast_4 each produced a single ~27 MB .exe that
launched, loaded all four plugins/extensions from inside the bundle, and ran.
"""
import ast
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pyside6  # noqa: E402

pytestmark = skip_without_pyside6


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


ALL_TARGETS = ("exe", "linux", "macos")


def _exporter(target):
    if target == "exe":
        from export.exe.exe_exporter import ExeExporter
        return ExeExporter()
    if target == "linux":
        from export.linux.linux_exporter import LinuxExporter
        return LinuxExporter()
    from export.macos.macos_exporter import MacOSExporter
    return MacOSExporter()


@pytest.fixture
def project(tmp_path):
    """A small project with the shapes that matter: a side file, a nested
    asset, and a soft-deleted asset in .trash."""
    root = tmp_path / "MyProject"
    (root / "sprites").mkdir(parents=True)
    (root / "objects").mkdir()
    (root / ".trash").mkdir()

    (root / "project.json").write_text(json.dumps({
        "name": "Mon Jeu",
        "assets": {"objects": {"obj_p": {"name": "obj_p"}}, "rooms": {}},
    }), encoding="utf-8")
    (root / "objects" / "obj_p.json").write_text(json.dumps({
        "name": "obj_p", "events": {"create": [{"action": "set_score"}]},
    }), encoding="utf-8")
    (root / "sprites" / "spr_p.png").write_bytes(b"\x89PNG\r\n")
    (root / ".trash" / "deleted.png").write_bytes(b"\x89PNG deleted")
    return root


def _runner_assignments(source):
    """{attribute: source of the assigned expression} for `runner.X = ...`.

    Parsed rather than grepped on purpose: a first draft of these tests
    asserted `"runner.language = LANGUAGE" in source`, which a mutation that
    commented the line out still satisfied -- the text was right there in the
    comment. Only the AST can tell an assignment from a mention of one.
    """
    found = {}
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "runner"):
                found[target.attr] = ast.unparse(node.value)
    return found


def _constant(source, name):
    """The value of a module-level `NAME = <literal>` in the launcher."""
    for node in ast.walk(ast.parse(source)):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == name):
            return ast.literal_eval(node.value)
    raise AssertionError("launcher has no %s constant" % name)


def _stage(target, project, tmp_path, settings=None):
    exporter = _exporter(target)
    exporter.project_path = project
    exporter.output_path = tmp_path / "out"
    exporter.export_settings = settings or {}
    exporter.project_data = json.loads(
        (project / "project.json").read_text(encoding="utf-8"))
    build_dir = tmp_path / ("build_" + target)
    build_dir.mkdir()
    exporter._stage_game(build_dir)
    return exporter, build_dir


# --- 1. the engine ---------------------------------------------------------

@pytest.mark.parametrize("target", ALL_TARGETS)
def test_launcher_runs_the_real_pygame_engine(qapp, target, project, tmp_path):
    exporter, build_dir = _stage(target, project, tmp_path)
    launcher = exporter._write_launcher(build_dir)
    source = launcher.read_text(encoding="utf-8")

    assert "from runtime.game_runner import GameRunner" in source, (
        "the desktop export must run the engine Test Game runs")
    assert "GameRunner(" in source
    # The old pipeline's tell. If this ever comes back, the export has been
    # pointed at a generated engine again.
    assert "from main import GameApp" not in source
    assert "kivy" not in source.lower()
    ast.parse(source)


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_launcher_passes_the_export_language_to_the_runtime(qapp, target, project, tmp_path):
    """Authored <param>_translations are resolved by the runtime, which reads
    GameRunner.language. Miss this and a French teacher's exported game shows
    English messages -- silently, since the dicts are still in the JSON."""
    exporter, build_dir = _stage(target, project, tmp_path, {"language": "fr"})
    source = exporter._write_launcher(build_dir).read_text(encoding="utf-8")
    assert _constant(source, "LANGUAGE") == "fr"
    assert _runner_assignments(source).get("language") == "LANGUAGE", (
        "the launcher must actually assign the export language to the runner")


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_launcher_keeps_high_scores_outside_the_bundle(qapp, target, project, tmp_path):
    """GameRunner puts highscores.json in the project folder, which inside a
    bundle is a temp directory deleted on exit -- so every high score would be
    lost on quit, silently."""
    exporter, build_dir = _stage(target, project, tmp_path)
    source = exporter._write_launcher(build_dir).read_text(encoding="utf-8")
    assigned = _runner_assignments(source).get("highscore_file")
    assert assigned, "the launcher must redirect the high-score file"
    assert "writable_dir()" in assigned, (
        "it must point outside the bundle, which is a temp dir: %r" % assigned)


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_plugins_and_extensions_ship_as_data(qapp, target, project, tmp_path):
    """They are loaded with spec_from_file_location, so they must be real .py
    files in the bundle. If they are missing the loader reports "Loaded 0
    plugin(s)" and carries on -- a 2.5D game then draws as a flat 2D room."""
    exporter, build_dir = _stage(target, project, tmp_path)
    datas = exporter._spec_datas(build_dir)
    destinations = {dest.replace("\\", "/") for _src, dest in datas}
    sources = {Path(src).name for src, _dest in datas}

    assert any(d == "plugins" or d.startswith("plugins/") for d in destinations)
    assert any(d == "extensions" or d.startswith("extensions/")
               for d in destinations)
    # Named specifically: audio actions are plugin-owned, and the raycast
    # renderer is a folder extension.
    assert "audio_actions.py" in sources
    assert "renderer.py" in sources, "the raycast extension must be bundled"


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_spec_does_not_exclude_pillow(qapp, target, project, tmp_path):
    """runtime/game_runner.py imports PIL at module level. Excluding it builds
    cleanly and then dies with ModuleNotFoundError on first launch -- which is
    exactly what happened during the freeze spike."""
    exporter, build_dir = _stage(target, project, tmp_path)
    spec = exporter._write_spec(build_dir, build_dir / "game_launcher.py")
    source = spec.read_text(encoding="utf-8")

    tree = ast.parse(source)
    excludes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "excludes":
            excludes = [el.value for el in node.value.elts]
    assert excludes, "spec should declare excludes"
    assert not any(e.upper().startswith("PIL") for e in excludes)
    assert not any(e == "pygame" for e in excludes)
    # Qt has no business in a game bundle; it would roughly triple the size.
    assert "PySide6" in excludes


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_pygame_is_required_and_kivy_is_not(qapp, target):
    exporter = _exporter(target)
    assert hasattr(exporter, "_check_pygame")
    messages = []
    exporter.export_complete.connect(lambda ok, msg: messages.append(msg))
    exporter._check_pygame = lambda: False
    exporter._check_pyinstaller = lambda: True
    assert exporter._require_pygame_dependencies() is False
    assert "pygame" in messages[-1]
    assert "Kivy" not in messages[-1]


# --- 2. the project --------------------------------------------------------

@pytest.mark.parametrize("target", ALL_TARGETS)
def test_the_project_is_copied_verbatim(qapp, target, project, tmp_path):
    """No regeneration, no rewriting: byte-for-byte the files the engine was
    tested against. This is the invariant the whole rework rests on."""
    exporter, build_dir = _stage(target, project, tmp_path)
    game_dir = build_dir / "game"

    for relative in ("project.json", "objects/obj_p.json", "sprites/spr_p.png"):
        source = project / relative
        copied = game_dir / relative
        assert copied.exists(), "%s was not bundled" % relative
        assert copied.read_bytes() == source.read_bytes(), (
            "%s was modified on the way into the bundle" % relative)


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_side_files_are_kept_rather_than_flattened(qapp, target, project, tmp_path):
    """GameRunner re-merges objects/*.json over the embedded copy, so the side
    files must travel with the project. Baking a merged project.json instead
    would be silently overwritten by the un-baked side files."""
    exporter, build_dir = _stage(target, project, tmp_path)
    assert (build_dir / "game" / "objects" / "obj_p.json").exists()


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_soft_deleted_assets_are_not_shipped(qapp, target, project, tmp_path):
    """.trash holds assets the author deleted (utils/asset_trash.py). Shipping
    them would undo the deletion -- the same leak already fixed for zip
    export in utils/project_compression.py."""
    exporter, build_dir = _stage(target, project, tmp_path)
    assert not (build_dir / "game" / ".trash").exists()

    datas = exporter._spec_datas(build_dir)
    assert not any("deleted.png" in src for src, _ in datas)


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_the_whole_game_tree_reaches_the_spec(qapp, target, project, tmp_path):
    """Staging the files is not enough -- anything absent from the spec's
    datas is absent from the bundle."""
    exporter, build_dir = _stage(target, project, tmp_path)
    datas = exporter._spec_datas(build_dir)
    bundled = {Path(src).name for src, dest in datas
               if str(dest).replace("\\", "/").startswith("game")}
    assert {"project.json", "obj_p.json", "spr_p.png"} <= bundled


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_staging_refuses_a_directory_with_no_project(qapp, target, tmp_path):
    """Fail loudly at export time rather than shipping an .exe that reports
    "Game data is missing from this build" to the player."""
    empty = tmp_path / "empty"
    empty.mkdir()
    exporter = _exporter(target)
    exporter.project_path = empty
    exporter.export_settings = {}
    with pytest.raises(FileNotFoundError):
        exporter._stage_game(tmp_path / "b")


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_build_directory_is_outside_the_project(qapp, target, project, tmp_path):
    """The project tree is copied wholesale into the build directory, so a
    build directory inside the project would recurse into itself."""
    exporter = _exporter(target)
    exporter.project_path = project
    build_dir = exporter._create_build_directory()
    try:
        assert project.resolve() not in build_dir.resolve().parents
    finally:
        import shutil
        shutil.rmtree(build_dir, ignore_errors=True)


# --- 3. the generated spec is valid --------------------------------------

@pytest.mark.parametrize("target", ALL_TARGETS)
def test_generated_spec_parses(qapp, target, project, tmp_path):
    """PyInstaller exec()s the spec, so a syntax error fails the export. The
    project name here is French and contains a space."""
    exporter, build_dir = _stage(target, project, tmp_path,
                                 {"icon_path": r"C:\Users\a\icon.ico"})
    source = exporter._write_spec(
        build_dir, build_dir / "game_launcher.py").read_text(encoding="utf-8")
    ast.parse(source)


def test_macos_spec_builds_an_app_bundle(qapp, project, tmp_path):
    """A .app is a directory, so macOS needs onedir + BUNDLE where the other
    two targets get a single file."""
    exporter, build_dir = _stage("macos", project, tmp_path)
    source = exporter._write_spec(
        build_dir, build_dir / "game_launcher.py").read_text(encoding="utf-8")
    assert "COLLECT(" in source
    assert "BUNDLE(" in source
    assert ".app'" in source
    assert "exclude_binaries=True" in source
    ast.parse(source)


@pytest.mark.parametrize("target", ("exe", "linux"))
def test_windows_and_linux_produce_one_file(qapp, target, project, tmp_path):
    """One artifact, because the realistic delivery path is a student handing
    a classmate a file."""
    exporter, build_dir = _stage(target, project, tmp_path)
    source = exporter._write_spec(
        build_dir, build_dir / "game_launcher.py").read_text(encoding="utf-8")
    assert "COLLECT(" not in source
    assert "exclude_binaries" not in source


def test_exe_spec_carries_the_dpi_manifest(qapp, project, tmp_path):
    """Without it Windows upscales the game window on a high-DPI display."""
    exporter, build_dir = _stage("exe", project, tmp_path)
    spec = exporter._write_spec(build_dir, build_dir / "game_launcher.py")
    assert "manifest='game.manifest'" in spec.read_text(encoding="utf-8")
    manifest = build_dir / "game.manifest"
    assert manifest.exists(), "the spec references a manifest that must exist"
    assert "dpiAware" in manifest.read_text(encoding="utf-8")


def test_hosts_cannot_cross_compile(qapp):
    """PyInstaller builds for the host only, so each target refuses elsewhere
    with an explanation rather than emitting a binary for the wrong OS."""
    import platform

    expectations = {"exe": "Windows", "linux": "Linux", "macos": "Darwin"}
    for target, required in expectations.items():
        exporter = _exporter(target)
        assert exporter.required_host_platform == required
        if platform.system() != required:
            refusal = exporter._host_platform_refusal()
            assert refusal and required in refusal
            assert "HTML5" in refusal, (
                "the refusal should point at the export that always works")
