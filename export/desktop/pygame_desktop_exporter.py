#!/usr/bin/env python3
"""Freeze the REAL pygame engine for desktop export.

Why this exists
---------------
The desktop exporters used to bundle a *reimplementation* of the engine: the
Kivy code generator, self-described as "80% GameMaker 7.0 compatible". So an
exported .exe was not the game the author had just tested with Test Game, and
the missing 20% showed up as five separate user-reported bugs in one pass
(EYEBALL_FIXES_2026-08-16 issues 4-8): no tiles, keyboard input that jammed
after the first wall, no wall collision, a player that floated upward, bonus
objects all stuck on sub-image 0.

Fixing five symptoms in a second engine treats the symptoms. This module
removes the cause: the desktop export now freezes `runtime/game_runner.py` --
the same engine, running the same project files, that Test Game runs. Kivy
stays where it is the only option: Android/iOS.

Design decisions worth keeping
------------------------------
**The project is copied verbatim.** Not regenerated, not transformed. The
whole bug class above came from the exported game differing from the tested
one, so the bundled `game/` directory is a plain copy of the author's project
folder -- same project.json, same rooms/objects/sprites side files, same
assets. The engine then reads it exactly as it does from disk.

That is also why authored `<param>_translations` are handled by passing the
export language to the runtime (`GameRunner.language`, which
`ActionExecutor.localize_param` reads) rather than by baking them into the
copied JSON the way the HTML5 and Kivy exporters must. Those two have no
choice -- their engines are generated. This one does, and the less the
exporter rewrites, the fewer ways it can diverge. Note the ordering hazard
that rules out baking here: `GameRunner` re-merges `objects/*.json` over the
embedded data, so a baked project.json would be silently overwritten by the
un-baked side files.

**Pillow is a hard requirement.** `runtime/game_runner.py` imports PIL at
module level, so a bundle built without it builds cleanly and then dies with
ModuleNotFoundError on first launch. Kivy is *not* required any more.

**Plugins and folder extensions ship as data, not as frozen modules.** They
are loaded with `spec_from_file_location`, so they must exist as real .py
files inside the bundle; `events.plugin_loader.get_app_root()` finds them at
`sys._MEIPASS`. Getting this wrong is silent -- the loader reports
"Loaded 0 plugin(s)" and a 2.5D game draws as a flat 2D room.

**Exporting requires the IDE to run from source.** PyInstaller analyses the
engine's imports from `pathex`, and it cannot run inside a frozen app anyway
(the standing decision in CLAUDE.md's export-dependency note).
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.logger import get_logger
from export.base_exporter import BaseKivyExporter, _missing_dependency_message

logger = get_logger(__name__)

# Repo root: export/desktop/pygame_desktop_exporter.py -> up 2.
ENGINE_ROOT = Path(__file__).resolve().parents[2]

# Directories that must ship as DATA because they are imported by path at
# runtime rather than by name at build time (see the module docstring).
ENGINE_DATA_DIRS: Tuple[str, ...] = ("plugins", "extensions")

# Modules the static analyser cannot see: reached only through
# spec_from_file_location, from inside plugins/ and extensions/.
ENGINE_HIDDEN_IMPORTS: Tuple[str, ...] = (
    "events.action_types",
    "events.event_types",
    "events.plugin_loader",
    "runtime.action_executor",
    "runtime.extension_hooks",
    "runtime.game_runner",
    "config.blockly_translations",  # get_runtime_translation, for dialogs
)

# The IDE's toolkit has no business in a game bundle, and dragging Qt in would
# roughly triple the download. numpy/matplotlib are unused by the engine
# (verified: no numpy or pygame.surfarray anywhere under runtime/, extensions/
# or plugins/). Kivy is deliberately gone -- that was the old runtime.
ENGINE_EXCLUDES: Tuple[str, ...] = (
    "PySide6", "shiboken6", "PyQt5", "PyQt6",
    "kivy", "tkinter", "matplotlib", "numpy",
)

# Never copy these out of the author's project folder.
#   .trash      soft-deleted assets (utils/asset_trash.py). Shipping them
#               would undo the deletion the author asked for -- the same leak
#               already fixed in utils/project_compression.py.
#   build_temp* leftovers from an earlier export, potentially huge.
SKIPPED_PROJECT_DIRS = frozenset({
    ".trash", ".git", "__pycache__", "build", "dist",
})
SKIPPED_PROJECT_PREFIXES = ("build_temp",)


def sanitize_app_name(raw: str, fallback: str = "Game") -> str:
    """Reduce a project name to a filename-safe token.

    The name is interpolated into single-quoted Python literals in the
    generated .spec, which PyInstaller exec()s, so an apostrophe -- ubiquitous
    in French titles like "L'aventure" -- would produce a SyntaxError and fail
    the whole export. Carried over from the Kivy-era exporters, where this was
    a real reported bug.
    """
    return re.sub(r"[^A-Za-z0-9_]", "_", str(raw)) or fallback


def _literal(path) -> str:
    """A path as a safe Python literal for the generated .spec.

    Forward slashes because a Windows ``C:\\Users\\...`` embeds invalid escapes
    (``\\U``), and repr() because an asset called ``épée d'or.png`` would
    otherwise close the string early.
    """
    return repr(str(path).replace("\\", "/"))


class BasePygameDesktopExporter(BaseKivyExporter):
    """Shared pipeline for the three desktop targets.

    Subclasses supply naming and packaging details only; the build itself is
    identical, which is the point -- the three targets diverging is how the
    Kivy exporters drifted apart in the first place.
    """

    # --- subclass configuration ------------------------------------------
    platform_label = "desktop exporter"
    build_tag = "desktop"
    #: Appended to the app name for the built artifact ('.exe' on Windows).
    executable_suffix = ""
    #: Set to a platform name to refuse to build anywhere else, since
    #: PyInstaller cannot cross-compile.
    required_host_platform: Optional[str] = None
    required_host_hint = ""
    #: "onefile" produces a single artifact a student can hand to a classmate
    #: on a USB stick, which is why Windows and Linux use it. macOS needs
    #: "onedir", because a .app *is* a directory and BUNDLE() wraps COLLECT().
    bundle_style = "onefile"

    # --- template method -------------------------------------------------
    def export_project(self, project_path: str, output_path: str,
                       settings: Dict) -> bool:
        build_dir = None
        try:
            refusal = self._host_platform_refusal()
            if refusal:
                self.export_complete.emit(False, refusal)
                return False

            self._load_project(project_path, output_path, settings)

            self.progress_update.emit(5, "Checking dependencies...")
            if not self._require_pygame_dependencies():
                return False

            self.progress_update.emit(10, "Creating build directory...")
            build_dir = self._create_build_directory()

            self.progress_update.emit(20, "Copying game files...")
            self._stage_game(build_dir)

            self.progress_update.emit(35, "Creating launcher...")
            launcher = self._write_launcher(build_dir)

            self.progress_update.emit(45, "Creating PyInstaller spec...")
            spec_file = self._write_spec(build_dir, launcher)

            self.progress_update.emit(55,
                                      "Building executable (this may take a while)...")
            if not self._run_pyinstaller(spec_file):
                self.export_complete.emit(
                    False,
                    "PyInstaller build failed.\n\n"
                    "The build log is above in the console. The build "
                    f"directory was kept for inspection:\n{build_dir}")
                return False

            self.progress_update.emit(90, "Copying to output directory...")
            if not self._copy_to_output(build_dir):
                # dist/ holds the only copy -- never clean up after a failed
                # copy, and never report success with an empty output folder.
                self.export_complete.emit(
                    False,
                    "Export built but could not be copied to:\n"
                    f"{self.output_path}\n\n"
                    f"The build is available at:\n{build_dir / 'dist'}")
                return False

            self.progress_update.emit(92, "Signing build...")
            sign_error = self._sign_build(build_dir)
            if sign_error:
                # Signing was explicitly requested (see _sign_build's own
                # no-op-when-unconfigured contract) -- a failure here must
                # fail the export rather than silently ship an unsigned
                # build the author believes is signed.
                self.export_complete.emit(
                    False,
                    "The build itself succeeded, but code signing failed:\n\n"
                    f"{sign_error}\n\n"
                    f"The unsigned build is available at:\n{self.output_path}")
                return False

            if not settings.get("include_debug", False):
                self.progress_update.emit(95, "Cleaning up temporary files...")
                self._cleanup(build_dir)

            self.progress_update.emit(100, "Export complete!")
            self.export_complete.emit(
                True, f"Game exported successfully to:\n{self.output_path}")
            return True

        except Exception as exc:  # noqa: BLE001 - reported to the user
            logger.error("Desktop export failed: %s", exc)
            import traceback
            traceback.print_exc()
            self.export_complete.emit(False, f"Export failed: {exc}")
            return False

    # --- steps -----------------------------------------------------------
    def _host_platform_refusal(self) -> Optional[str]:
        """PyInstaller builds for the host only; refuse early and explain."""
        import platform

        if not self.required_host_platform:
            return None
        if platform.system() == self.required_host_platform:
            return None
        return (
            f"{self.platform_label} must be run on "
            f"{self.required_host_platform}.\n\n"
            "PyInstaller creates binaries for the platform it runs on, so a "
            f"binary built on {platform.system()} will not run on "
            f"{self.required_host_platform}.\n\n"
            f"{self.required_host_hint}"
            "Or use the Web (HTML5) export, which runs everywhere and needs "
            "nothing installed."
        )

    def _require_pygame_dependencies(self) -> bool:
        """PyInstaller + pygame + Pillow, in the Python running the IDE.

        Deliberately NOT `_require_kivy_dependencies`: this pipeline does not
        use Kivy at all, and demanding it would block an export that would
        have worked.
        """
        if not self._check_pyinstaller():
            self.export_complete.emit(False, _missing_dependency_message(
                "PyInstaller", "pyinstaller", self.platform_label))
            return False

        if not self._check_pygame():
            self.export_complete.emit(False, _missing_dependency_message(
                "pygame", "pygame", self.platform_label,
                note="pygame is the game engine itself."))
            return False

        if not self._check_pillow():
            self.export_complete.emit(False, _missing_dependency_message(
                "Pillow (PIL)", "pillow", self.platform_label,
                note="Pillow handles the game's image assets."))
            return False

        return True

    def _check_pygame(self) -> bool:
        try:
            import pygame  # noqa: F401
            return True
        except ImportError:
            return False

    def _create_build_directory(self) -> Path:
        """A scratch directory OUTSIDE the project folder.

        Outside matters: the project tree is copied wholesale into the build
        directory, so a build directory inside the project would recurse into
        itself. It also keeps the author's project folder clean and dodges the
        Dropbox/antivirus file locks the old in-project build directory needed
        retry loops for.
        """
        build_dir = Path(tempfile.mkdtemp(
            prefix=f"pygm_export_{self.build_tag}_"))
        logger.debug("Build directory: %s", build_dir)
        return build_dir

    def _stage_game(self, build_dir: Path) -> Path:
        """Copy the author's project verbatim into build_dir/game."""
        source = (self.project_path if self.project_path.is_dir()
                  else self.project_path.parent)
        game_dir = build_dir / "game"

        def ignore(directory, names):
            skipped = []
            for name in names:
                if name in SKIPPED_PROJECT_DIRS:
                    skipped.append(name)
                elif name.startswith(SKIPPED_PROJECT_PREFIXES):
                    skipped.append(name)
                elif name.endswith(".pyc"):
                    skipped.append(name)
            return skipped

        shutil.copytree(source, game_dir, ignore=ignore, dirs_exist_ok=True)

        if not (game_dir / "project.json").exists():
            raise FileNotFoundError(
                f"No project.json in {source} -- nothing to export")
        return game_dir

    def _write_launcher(self, build_dir: Path) -> Path:
        """Generate the entry point that starts the frozen engine."""
        launcher = build_dir / "game_launcher.py"
        language = (self.export_settings or {}).get("language", "en") or "en"
        title = self.project_data.get("name", "Game")

        launcher.write_text(LAUNCHER_TEMPLATE.format(
            title=repr(str(title)),
            language=repr(str(language)),
        ), encoding="utf-8")
        return launcher

    # --- spec ------------------------------------------------------------
    def app_name(self) -> str:
        return sanitize_app_name(self.project_data.get("name", "Game"))

    def _spec_datas(self, build_dir: Path) -> List[Tuple[str, str]]:
        """(source, destination-inside-bundle) pairs.

        The whole game directory plus the engine's path-loaded plugins and
        extensions. Paths are absolute so the spec does not depend on
        PyInstaller's working directory.
        """
        datas: List[Tuple[str, str]] = []

        game_dir = build_dir / "game"
        for root, dirs, files in os.walk(game_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in files:
                if name.endswith(".pyc"):
                    continue
                src = Path(root) / name
                dest = Path("game") / src.relative_to(game_dir).parent
                datas.append((str(src), str(dest)))

        for folder in ENGINE_DATA_DIRS:
            source = ENGINE_ROOT / folder
            if not source.is_dir():
                logger.warning("Engine data directory missing: %s", source)
                continue
            for path in sorted(source.rglob("*")):
                if not path.is_file() or path.suffix == ".pyc":
                    continue
                if "__pycache__" in path.parts:
                    continue
                dest = Path(folder) / path.relative_to(source).parent
                datas.append((str(path), str(dest)))

        return datas

    def _spec_exe_options(self) -> str:
        """Extra keyword lines for the EXE() call. Overridden per platform."""
        return ""

    def _spec_trailer(self, app_name: str) -> str:
        """Anything after EXE() -- macOS adds a BUNDLE()."""
        return ""

    def _spec_template(self) -> str:
        if self.bundle_style == "onedir":
            return SPEC_TEMPLATE_ONEDIR
        return SPEC_TEMPLATE_ONEFILE

    def _write_spec(self, build_dir: Path, launcher: Path) -> Path:
        spec_file = build_dir / "game.spec"
        app_name = self.app_name()
        settings = self.export_settings or {}

        datas_str = ",\n        ".join(
            f"({_literal(src)}, {_literal(dest)})"
            for src, dest in self._spec_datas(build_dir))
        hidden_str = ",\n        ".join(
            repr(name) for name in ENGINE_HIDDEN_IMPORTS)
        excludes_str = ",\n        ".join(
            repr(name) for name in ENGINE_EXCLUDES)

        # A game window has no console: a stray print must not open one. With
        # debug on, keep the console so a crash is visible while building.
        debug = bool(settings.get("include_debug", False))

        spec_file.write_text(self._spec_template().format(
            app_name=app_name,
            launcher=_literal(launcher.name),
            engine_root=_literal(ENGINE_ROOT),
            datas=datas_str,
            hiddenimports=hidden_str,
            excludes=excludes_str,
            exe_name=repr(app_name + self.executable_suffix),
            debug=debug,
            console=debug,
            upx=bool(settings.get("optimize", False)),
            extra_options=self._spec_exe_options(),
            trailer=self._spec_trailer(app_name),
        ), encoding="utf-8")
        return spec_file

    # --- build -----------------------------------------------------------
    def _run_pyinstaller(self, spec_file: Path) -> bool:
        process = None
        try:
            logger.info("Running PyInstaller (a few minutes)...")
            process = subprocess.Popen(
                [sys.executable, "-m", "PyInstaller", "--clean",
                 "--noconfirm", str(spec_file)],
                cwd=str(spec_file.parent),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1)
            for line in process.stdout:
                logger.debug(line.rstrip())
            process.wait(timeout=900)
            if process.returncode != 0:
                logger.error("PyInstaller failed (exit %s)", process.returncode)
                return False
            logger.info("PyInstaller build completed")
            return True
        except subprocess.TimeoutExpired:
            logger.error("PyInstaller timed out after 15 minutes")
            if process:
                process.kill()
            return False
        except Exception as exc:  # noqa: BLE001
            logger.error("Error running PyInstaller: %s", exc)
            import traceback
            traceback.print_exc()
            return False

    def _copy_to_output(self, build_dir: Path) -> bool:
        """Copy dist/ to the chosen output directory.

        Returns False if anything ultimately failed after retries; the caller
        must then keep the build directory, since dist/ holds the only copy.
        """
        dist_dir = build_dir / "dist"
        self.output_path.mkdir(parents=True, exist_ok=True)

        if not dist_dir.exists():
            logger.error("PyInstaller produced no dist/ directory")
            return False

        all_copied = True
        for item in dist_dir.iterdir():
            for attempt in range(5):
                try:
                    if item.is_dir():
                        shutil.copytree(item, self.output_path / item.name,
                                        dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, self.output_path / item.name)
                    break
                except PermissionError as exc:
                    if attempt < 4:
                        time.sleep(1)
                    else:
                        logger.warning("Could not copy %s: %s", item.name, exc)
                        logger.info("Build kept at: %s", dist_dir / item.name)
                        all_copied = False
        return all_copied

    def _cleanup(self, build_dir: Path) -> None:
        try:
            shutil.rmtree(build_dir)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not clean up %s: %s", build_dir, exc)

    # --- signing -----------------------------------------------------------
    def _sign_build(self, build_dir: Path) -> Optional[str]:
        """Post-build code signing hook (docs/EXPORT_POLISH_PLAN.md item 2b).

        No-op by default -- every export stays unsigned exactly as before
        unless a subclass overrides this AND the relevant export settings
        are actually provided. Returns None on success (including "not
        configured, nothing to do"), or a human-readable error message on
        failure. Neither Linux binary carries this concept (ELF has no
        signing metadata), so LinuxExporter never overrides this.
        """
        return None


# The launcher is what actually runs inside the bundle. Kept small on purpose:
# everything it needs already exists in the engine.
LAUNCHER_TEMPLATE = '''#!/usr/bin/env python3
"""Entry point for a frozen PyGameMaker game. Generated -- do not edit.

Runs the real pygame engine (runtime/game_runner.py) against the project
copied into the bundle, so this is the same engine, and the same project
files, that Test Game runs in the IDE.
"""
import sys
from pathlib import Path

GAME_TITLE = {title}
LANGUAGE = {language}


def bundle_root():
    """Where the bundled data landed."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def writable_dir():
    """A directory that survives the run.

    In a one-file bundle the bundle root is a temp directory deleted on exit,
    so anything the game saves there is lost. Next to the executable is where
    a player would look for it.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def report(message):
    """A frozen game has no console, so a crash must leave a trace."""
    log = writable_dir() / "game_error.log"
    try:
        log.write_text(message, encoding="utf-8")
    except OSError:
        pass
    print(message)


def main():
    project = bundle_root() / "game" / "project.json"
    if not project.exists():
        report("Game data is missing from this build: %s" % project)
        sys.exit(1)

    try:
        from runtime.game_runner import GameRunner

        runner = GameRunner(str(project))
        # Authored <param>_translations are resolved at runtime by
        # ActionExecutor.localize_param, which reads this.
        runner.language = LANGUAGE
        # High scores default to the project folder, which is inside the
        # bundle -- and therefore a temp directory that is deleted on exit.
        # Keep them next to the executable so they persist.
        runner.highscore_file = writable_dir() / "highscores.json"
        runner.run()
    except Exception:
        import traceback
        report("%s failed to start:\\n\\n%s" % (GAME_TITLE,
                                               traceback.format_exc()))
        sys.exit(1)


if __name__ == "__main__":
    main()
'''


SPEC_ANALYSIS = '''# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for {app_name} -- generated by PyGameMaker.
# Freezes the real pygame engine; see export/desktop/pygame_desktop_exporter.py.

a = Analysis(
    [{launcher}],
    # The engine is pulled in by import analysis from the launcher.
    pathex=[{engine_root}],
    binaries=[],
    datas=[
        {datas}
    ],
    hiddenimports=[
        {hiddenimports}
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        {excludes}
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)
'''

# One artifact. a.binaries/a.datas go INTO the EXE, and PyInstaller's
# bootloader unpacks them to a temp directory at launch (which is why the
# launcher keeps highscores.json next to the executable instead).
SPEC_TEMPLATE_ONEFILE = SPEC_ANALYSIS + '''
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name={exe_name},
    debug={debug},
    bootloader_ignore_signals=False,
    strip=False,
    upx={upx},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {extra_options}
)
{trailer}'''

# A directory: EXE holds only the bootloader (exclude_binaries=True) and
# COLLECT gathers the rest beside it. Required on macOS, where a .app IS a
# directory and BUNDLE() wraps the COLLECT.
SPEC_TEMPLATE_ONEDIR = SPEC_ANALYSIS + '''
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name={exe_name},
    debug={debug},
    bootloader_ignore_signals=False,
    strip=False,
    upx={upx},
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {extra_options}
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx={upx},
    upx_exclude=[],
    name={app_name!r},
)
{trailer}'''
