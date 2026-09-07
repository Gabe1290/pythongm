#!/usr/bin/env python3
"""Build the artefacts the hand-verification pass needs, into one folder.

`docs/PLATFORM_DISPLAY_CHECKLIST.md` and `docs/NOW_PLAN_2026-09-06.md`'s Track B
ask a human to do things a script cannot: decide whether a `.exe` trips an
antivirus scanner, whether holding a key down *feels* right, whether a page
renders correctly in a real browser. None of that is automatable -- but the
building is, and it is the part that takes the time and knows the details
(which exporter class per host, which samples are worth the minutes, that a
Pyodide-bundled export needs network access at build time).

So this produces a folder of things to double-click, plus a README naming what
to look at in each, and leaves the looking to a person.

Usage:
    py -3.12 tools/build_qa_bundle.py                 # default set
    py -3.12 tools/build_qa_bundle.py --out D:\\qa
    py -3.12 tools/build_qa_bundle.py --exe maze_1 --html5 raycast_1 block_world_1
    py -3.12 tools/build_qa_bundle.py --skip-exe      # HTML5 only, ~seconds
"""
import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
SAMPLES_DIR = REPO_ROOT / "samples"

# A `.exe` takes minutes each, so the default is two: one that is simply
# playable, and one whose feel is the point (a platformer is where a sticky
# key or a dropped input shows up first).
DEFAULT_EXE = ["maze_1", "plateforme_3"]

# HTML5 is seconds each, so this is chosen for COVERAGE of the things most
# likely to be wrong in a browser rather than for speed.
DEFAULT_HTML5 = [
    ("maze_1", "the baseline -- if this is wrong, everything is"),
    ("plateforme_3", "gravity, collisions and draw depth"),
    ("raycast_1", "the 2.5D renderer, floor casting included"),
    ("block_world_1", "voxel view + distance fog, never yet seen in a browser"),
    ("block_world_2", "open terrain: the fog band at the render distance"),
    ("match3_1", "mouse input and a grid of sprites"),
    ("sky_strike_1", "sprites, sound and a scrolling background"),
]

# Pyodide (the embedded Python runtime) is only pulled in for a project that
# actually RUNS Python -- an execute_code/execute_script action somewhere. Ask
# for it on a project that does not and you silently get an ordinary export;
# match3_1 really does use it. (block_world_2 and match3_2/3 also qualify.)
PYODIDE_SAMPLE = "match3_1"


def _qt_app():
    """The exporters are QObjects and emit progress signals."""
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def _exporter_for_host():
    if sys.platform.startswith("win"):
        from export.exe.exe_exporter import ExeExporter
        return ExeExporter, "Windows .exe"
    if sys.platform.startswith("linux"):
        from export.linux.linux_exporter import LinuxExporter
        return LinuxExporter, "Linux binary"
    if sys.platform == "darwin":
        from export.macos.macos_exporter import MacOSExporter
        return MacOSExporter, "macOS .app"
    return None, "no desktop exporter for %s" % sys.platform


def build_exe(sample, out_dir, language="en"):
    exporter_class, label = _exporter_for_host()
    if exporter_class is None:
        return label

    _qt_app()
    exporter = exporter_class()
    failures = []
    exporter.export_complete.connect(
        lambda ok, msg: None if ok else failures.append(msg))

    project = SAMPLES_DIR / sample / "project.json"
    if not project.exists():
        return "no such sample: %s" % sample

    target = out_dir / sample
    target.mkdir(parents=True, exist_ok=True)
    started = time.time()
    print("  building %s (%s) -- minutes, not seconds..." % (sample, label),
          flush=True)
    ok = exporter.export_project(str(project), str(target),
                                 {"language": language})
    if not ok:
        return failures[-1] if failures else "export_project returned False"
    print("  built in %.0fs" % (time.time() - started), flush=True)
    return ""


def build_html5(sample, out_dir, offline_pyodide=False, language="en"):
    from export.HTML5.html5_exporter import HTML5Exporter

    project_dir = SAMPLES_DIR / sample
    if not (project_dir / "project.json").exists():
        return "no such sample: %s" % sample

    target = out_dir / (sample + ("_pyodide" if offline_pyodide else ""))
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    exporter = HTML5Exporter()
    settings = {"language": language}
    if offline_pyodide:
        settings["offline_pyodide"] = True
    ok = exporter.export(project_dir, target, settings)
    if not ok:
        return exporter.last_error_message or "export returned False"
    return ""


README = """# Hand-verification bundle

Built by `tools/build_qa_bundle.py` on {when}. Nothing here needs a build step
or a terminal -- it is all double-click-and-look.

This covers Track B of `docs/NOW_PLAN_2026-09-06.md` (B1, B3, B4). Tick what you
cover in `docs/PLATFORM_DISPLAY_CHECKLIST.md` afterwards, so the next pass
starts from a real baseline.

## exe/ -- the desktop builds  (B1, B4)

{exe_list}
**B1, antivirus (~10 min, release-gating).** Upload one `.exe` to
virustotal.com, or just run your own scanner over the folder. An unsigned
PyInstaller binary is a classic false positive, and a teacher who hits one
concludes the software is malware. What matters is whether it trips anything,
and which engine.

**B4, play it (~10 min).** The automated verifier already proves an export
renders frames pixel-identical to the IDE. It cannot tell you whether holding a
key down feels right. Play for a minute: does movement start and stop cleanly,
does the platformer jump when you expect, does anything stutter?

## html5/ -- the browser builds  (B3)

{html5_list}
Open each `.html`. Worth doing **twice**: straight from the file (a
`file://` URL) and from a served folder, because browsers apply different
security rules to the two and only the second is how a student would really
publish. To serve one:

    cd html5/maze_1 && py -3.12 -m http.server 8000

then visit http://localhost:8000/maze_1.html .

Try **Firefox and a Chromium browser** (Chrome or Edge) -- their canvas and
audio behaviour differ. What to look for: the game starts at all, sprites and
text are in the right places, sound plays, input responds, and nothing floods
the browser console with errors (F12).

{pyodide_note}
## Worth a specially close look this time

`block_world_1` and `block_world_2` gained distance fog on 2026-09-07, and the
HTML5 port of it has been verified only by parity numbers -- **nobody has
watched it render in a browser**. The far edge of the world should fade into
the sky. If it instead ends on a hard line with a dark brown band, the port is
wrong in a way no test here catches.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None,
                        help="output folder (default: qa_bundle/ beside the repo)")
    parser.add_argument("--exe", nargs="*", default=None,
                        help="samples to build as native executables")
    parser.add_argument("--html5", nargs="*", default=None,
                        help="samples to build for the browser")
    parser.add_argument("--skip-exe", action="store_true",
                        help="HTML5 only -- seconds instead of minutes")
    parser.add_argument("--skip-pyodide", action="store_true",
                        help="skip the embedded-runtime build (it downloads)")
    parser.add_argument("--language", default="en")
    args = parser.parse_args()

    out_dir = Path(args.out) if args.out else REPO_ROOT.parent / "qa_bundle"
    out_dir.mkdir(parents=True, exist_ok=True)
    print("Output: %s\n" % out_dir)

    exe_samples = [] if args.skip_exe else (args.exe if args.exe is not None
                                            else DEFAULT_EXE)
    html5_samples = ([(s, "") for s in args.html5] if args.html5 is not None
                     else DEFAULT_HTML5)

    problems = {}

    html5_lines = []
    if html5_samples:
        print("HTML5 exports:")
        (out_dir / "html5").mkdir(exist_ok=True)
        for sample, why in html5_samples:
            problem = build_html5(sample, out_dir / "html5",
                                 language=args.language)
            state = "ok" if not problem else "FAILED: %s" % problem
            print("  %-16s %s" % (sample, state), flush=True)
            if problem:
                problems["html5/" + sample] = problem
            else:
                page = next((f.name for f in (out_dir / "html5" / sample).glob("*.html")),
                            sample + ".html")
                html5_lines.append("- `%s/%s`%s"
                                   % (sample, page,
                                      " -- " + why if why else ""))

        if not args.skip_pyodide:
            print("  %-16s (embedded Python runtime -- downloads)"
                  % PYODIDE_SAMPLE, flush=True)
            problem = build_html5(PYODIDE_SAMPLE, out_dir / "html5",
                                 offline_pyodide=True, language=args.language)
            if problem:
                problems["html5/%s_pyodide" % PYODIDE_SAMPLE] = problem
                print("      FAILED: %s" % problem)
            else:
                folder = out_dir / "html5" / (PYODIDE_SAMPLE + "_pyodide")
                page = next((f.name for f in folder.glob("*.html")),
                            PYODIDE_SAMPLE + ".html")
                size = sum(f.stat().st_size for f in folder.rglob("*")
                           if f.is_file()) / 1048576
                html5_lines.append(
                    "- `%s_pyodide/%s` -- the same game carrying its own Python"
                    " runtime (%.0f MB), so it needs no network at all. If this"
                    " one is the same size as the plain build above, the runtime"
                    " was NOT embedded."
                    % (PYODIDE_SAMPLE, page, size))

    exe_lines = []
    if exe_samples:
        print("\nDesktop builds:")
        (out_dir / "exe").mkdir(exist_ok=True)
        for sample in exe_samples:
            problem = build_exe(sample, out_dir / "exe", args.language)
            if problem:
                problems["exe/" + sample] = problem
                print("  %-16s FAILED: %s" % (sample, problem), flush=True)
            else:
                exe_lines.append("- `%s/`" % sample)

    pyodide_note = ""
    if any(k.endswith("_pyodide") for k in problems):
        pyodide_note = (
            "*The embedded-runtime build failed this run -- it needs network "
            "access at build time. Re-run with network, or `--skip-pyodide`.*\n\n")

    (out_dir / "README.md").write_text(README.format(
        when=time.strftime("%Y-%m-%d %H:%M"),
        exe_list=("\n".join(exe_lines) + "\n\n") if exe_lines
                 else "*(none built this run)*\n\n",
        html5_list=("\n".join(html5_lines) + "\n\n") if html5_lines
                   else "*(none built this run)*\n\n",
        pyodide_note=pyodide_note,
    ), encoding="utf-8")

    print("\n%d built, %d failed. README.md written to %s"
          % (len(exe_lines) + len(html5_lines), len(problems), out_dir))
    for name, problem in problems.items():
        print("  FAILED %s: %s" % (name, problem))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
