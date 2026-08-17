#!/usr/bin/env python3
"""Build a desktop export for real, launch it, and prove it renders.

This is the check that was missing. The desktop exporters used to bundle a
second engine, and nothing ever launched the artifact they produced -- so five
bugs (no tiles, jammed keyboard, no collision, a floating player, sub-images
stuck on frame 0) reached a user's manual pass with a green test suite behind
them. Every one of them was in an .exe nobody had run.

tools/smoke_run_samples.py already drives the samples' real game loop, but
in-process: it imports GameRunner and installs a tick hook. That is impossible
for a compiled binary, so this tool talks to a separate process instead,
through the engine's PYGM_MAX_FRAMES budget -- the exported game renders N real
frames, prints PYGM_FRAMES_COMPLETED=N, and exits 0.

"It was still running after 20 seconds" is NOT the same check: a game stuck on
a black screen before its first frame is also still running. This asserts
frames.

Usage:
    python tools/verify_desktop_export.py                  # maze_1
    python tools/verify_desktop_export.py maze_1 raycast_4 plateforme_2
    python tools/verify_desktop_export.py --all            # every sample
    python tools/verify_desktop_export.py --frames 300 maze_1
    python tools/verify_desktop_export.py --language fr maze_1

Needs PyInstaller, pygame and Pillow in this Python, builds only for the host
platform (PyInstaller cannot cross-compile), and takes a couple of minutes per
sample. Exits non-zero if any sample fails, so it can gate a release.
"""
import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SAMPLES_DIR = ROOT / "samples"
FRAME_MARKER = "PYGM_FRAMES_COMPLETED="


def exporter_for_host():
    """The exporter that targets this machine, or (None, why-not)."""
    system = platform.system()
    if system == "Windows":
        from export.exe.exe_exporter import ExeExporter
        return ExeExporter, "Windows .exe"
    if system == "Linux":
        from export.linux.linux_exporter import LinuxExporter
        return LinuxExporter, "Linux binary"
    if system == "Darwin":
        from export.macos.macos_exporter import MacOSExporter
        return MacOSExporter, "macOS .app"
    return None, "unsupported host platform: %s" % system


def built_executable(output_dir: Path):
    """Find what the build produced, whatever shape it took."""
    if platform.system() == "Darwin":
        for app in output_dir.glob("*.app"):
            binaries = sorted((app / "Contents" / "MacOS").glob("*"))
            if binaries:
                return binaries[0]
    candidates = []
    for path in output_dir.rglob("*"):
        if not path.is_file():
            continue
        if platform.system() == "Windows":
            if path.suffix.lower() == ".exe":
                candidates.append(path)
        elif os.access(path, os.X_OK) and path.suffix == "":
            candidates.append(path)
    # Prefer a top-level artifact over anything nested in a onedir payload.
    candidates.sort(key=lambda p: len(p.relative_to(output_dir).parts))
    return candidates[0] if candidates else None


def build(sample: str, output_dir: Path, language: str) -> str:
    """Build the sample. Returns "" on success, else the failure message."""
    exporter_class, label = exporter_for_host()
    if exporter_class is None:
        return label

    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])

    exporter = exporter_class()
    failures = []
    exporter.export_complete.connect(
        lambda ok, msg: None if ok else failures.append(msg))

    project = SAMPLES_DIR / sample / "project.json"
    if not project.exists():
        return "no such sample: %s" % sample

    print("  building %s (%s)..." % (sample, label), flush=True)
    started = time.time()
    ok = exporter.export_project(str(project), str(output_dir),
                                 {"language": language})
    print("  built in %.0fs" % (time.time() - started), flush=True)
    if not ok:
        return failures[-1] if failures else "export_project returned False"
    return ""


def launch(executable: Path, frames: int, timeout: int,
           screenshot: Path = None) -> str:
    """Run the built game for `frames` frames. Returns "" on success."""
    env = dict(os.environ,
               SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy",
               PYGM_MAX_FRAMES=str(frames))
    if screenshot:
        env["PYGM_SCREENSHOT"] = str(screenshot)
    # A crash inside a windowed build is silent, so the launcher writes it here.
    error_log = executable.parent / "game_error.log"
    if error_log.exists():
        error_log.unlink()

    print("  running %s for %d frames..." % (executable.name, frames),
          flush=True)
    try:
        result = subprocess.run([str(executable)], capture_output=True,
                                text=True, timeout=timeout, env=env,
                                cwd=str(executable.parent))
    except subprocess.TimeoutExpired:
        # Note for anyone extending this: killing a one-file PyInstaller
        # process is awkward, because the bootloader spawns a child that keeps
        # the pipes open. The frame budget is what avoids needing to.
        return ("did not finish %d frames within %ds -- it may be stuck before "
                "its first frame" % (frames, timeout))

    output = (result.stdout or "") + (result.stderr or "")

    if error_log.exists():
        return "wrote a crash log:\n%s" % error_log.read_text(
            encoding="utf-8", errors="replace")[:2000]
    if FRAME_MARKER not in output:
        tail = "\n".join(output.strip().splitlines()[-15:])
        return ("never reported completing its frames (exit %s). Output:\n%s"
                % (result.returncode, tail))

    reported = int(output.split(FRAME_MARKER)[1].split()[0])
    if reported < frames:
        return "rendered only %d of %d frames" % (reported, frames)
    if result.returncode != 0:
        return "rendered %d frames but exited %s" % (reported, result.returncode)

    print("  OK: rendered %d frames, exited cleanly" % reported, flush=True)
    return ""


def render_with_source_engine(sample: str, frames: int, timeout: int,
                              language: str, screenshot: Path) -> str:
    """Render the same frame with the engine the IDE runs, for comparison."""
    env = dict(os.environ,
               SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy",
               PYGM_MAX_FRAMES=str(frames), PYGM_SCREENSHOT=str(screenshot))
    project = SAMPLES_DIR / sample / "project.json"
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "runtime" / "run_game.py"),
             str(project), language],
            capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return "the source engine itself did not finish %d frames" % frames
    if not screenshot.exists():
        tail = "\n".join(((result.stdout or "") + (result.stderr or ""))
                         .strip().splitlines()[-10:])
        return "the source engine saved no frame:\n%s" % tail
    return ""


def compare_frames(exported: Path, reference: Path, tolerance: float) -> str:
    """Fraction of differing pixels between the two rendered frames.

    This is the strongest available answer to "is the export really the same
    engine": not an argument about shared code, a picture.

    Not exact, and not on by default, because a sample is only deterministic
    if it does not call random() -- several do, so an unconditional pixel
    check would flap. Treat a small difference as noise and a large one as a
    real divergence.
    """
    try:
        from PIL import Image
    except ImportError:
        return "Pillow is needed to compare frames"

    with Image.open(exported) as a, Image.open(reference) as b:
        first = a.convert("RGB")
        second = b.convert("RGB")
        if first.size != second.size:
            return ("the exported game rendered %sx%s but the IDE renders "
                    "%sx%s" % (first.size + second.size))
        pixels_a = first.load()
        pixels_b = second.load()
        width, height = first.size
        differing = sum(
            1
            for y in range(height)
            for x in range(width)
            if pixels_a[x, y] != pixels_b[x, y])

    fraction = differing / float(width * height)
    print("  frame differs from the IDE by %.2f%% of pixels" % (fraction * 100),
          flush=True)
    if fraction > tolerance:
        return ("the exported frame differs from the IDE's by %.1f%% of pixels "
                "(tolerance %.1f%%) -- the export is not rendering what the "
                "IDE renders" % (fraction * 100, tolerance * 100))
    return ""


def verify(sample: str, frames: int, timeout: int, language: str,
           keep: bool, compare: bool = False,
           tolerance: float = 0.02) -> str:
    output_dir = Path(tempfile.mkdtemp(prefix="pygm_verify_%s_" % sample))
    try:
        problem = build(sample, output_dir, language)
        if problem:
            return problem
        executable = built_executable(output_dir)
        if executable is None:
            return "the build produced no executable in %s" % output_dir

        exported_frame = output_dir / "exported_frame.png" if compare else None
        problem = launch(executable, frames, timeout, exported_frame)
        if problem or not compare:
            return problem

        if not exported_frame.exists():
            return "the exported game saved no frame to compare"
        reference = output_dir / "ide_frame.png"
        problem = render_with_source_engine(sample, frames, timeout, language,
                                            reference)
        if problem:
            return problem
        return compare_frames(exported_frame, reference, tolerance)
    finally:
        if keep:
            print("  build kept at %s" % output_dir, flush=True)
        else:
            shutil.rmtree(output_dir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samples", nargs="*", default=None,
                        help="sample names (default: maze_1)")
    parser.add_argument("--all", action="store_true",
                        help="every bundled sample -- minutes each, so slow")
    parser.add_argument("--frames", type=int, default=120,
                        help="frames the built game must render (default 120)")
    parser.add_argument("--timeout", type=int, default=180,
                        help="seconds to allow for those frames")
    parser.add_argument("--language", default="en",
                        help="export language, e.g. fr")
    parser.add_argument("--keep", action="store_true",
                        help="keep the built artifacts for inspection")
    parser.add_argument("--compare", action="store_true",
                        help="also compare the exported game's rendered frame "
                             "against the engine the IDE runs")
    parser.add_argument("--tolerance", type=float, default=0.02,
                        help="fraction of pixels allowed to differ with "
                             "--compare (default 0.02); samples that call "
                             "random() are not deterministic")
    args = parser.parse_args()

    if args.all:
        samples = sorted(p.parent.name
                         for p in SAMPLES_DIR.glob("*/project.json"))
    else:
        samples = args.samples or ["maze_1"]

    print("Host: %s   samples: %d   frames: %d"
          % (platform.system(), len(samples), args.frames))

    failures = {}
    for sample in samples:
        print("\n=== %s ===" % sample, flush=True)
        problem = verify(sample, args.frames, args.timeout, args.language,
                         args.keep, args.compare, args.tolerance)
        if problem:
            failures[sample] = problem
            print("  FAILED: %s" % problem, flush=True)

    print("\n" + "=" * 60)
    print("%d/%d verified" % (len(samples) - len(failures), len(samples)))
    for sample, problem in failures.items():
        print("  FAILED %s: %s" % (sample, problem.splitlines()[0]))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
