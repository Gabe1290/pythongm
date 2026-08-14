#!/usr/bin/env python3
"""
Offline Pyodide bundle for HTML5 export.

engine.js's PythonBridge normally loads Pyodide from the jsDelivr CDN at
PLAY time — fine for a browser with internet, but a dealbreaker on a
locked-down school network (TODO.md's "Pyodide loads from the jsDelivr
CDN — a Python-using game needs internet on first open").

This downloads (once, then caches) the small set of core Pyodide files a
plain execute_code game actually needs — no numpy/pillow/etc., just the
interpreter + standard library — so HTML5Exporter can embed them directly
into the exported .html as base64, keeping the export a genuinely
self-contained single file with zero runtime network dependency, matching
game_data/sprites_data/sounds_data's existing embedding pattern.

Cache lives outside the repo (~/.pygamemaker/pyodide_cache/<version>/) —
these are multi-MB third-party binaries, not something to vendor into the
git history the way resources/vendor/pako.min.js's ~47 KB was.
"""
import urllib.request
import urllib.error
from pathlib import Path
from typing import Callable, Dict, Optional

from core.logger import get_logger
logger = get_logger(__name__)

# Must match engine.js's PYODIDE_URL version pin (v0.26.4) — the CDN and
# offline paths need to agree, or PY_BOOTSTRAP could run against a
# different pyodide/CPython version than intended.
PYODIDE_VERSION = "0.26.4"
_BASE_URL = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/"

# The full Pyodide distribution also ships every optional scientific
# package (numpy, pandas, ...); PY_BOOTSTRAP only ever imports json/math/
# random (all core stdlib), so only these five are needed:
#   - pyodide.js / pyodide.asm.js: the loader + emscripten glue, executed
#     inline as a <script> instead of fetched, so loadPyodide() never
#     issues a network request for them (see engine.js's embedded-bundle
#     branch).
#   - pyodide.asm.wasm: the interpreter itself. Not directly settable via
#     loadPyodide() options — engine.js intercepts window.fetch for this
#     one file specifically.
#   - pyodide-lock.json / python_stdlib.zip: passed as data: URIs via
#     loadPyodide()'s own lockFileURL/stdLibURL options — no interception
#     needed, fetch() natively supports data: URIs.
CORE_FILES = (
    "pyodide.js",
    "pyodide.asm.js",
    "pyodide.asm.wasm",
    "pyodide-lock.json",
    "python_stdlib.zip",
)

# MIME types for embedding as data: URIs / Response objects in engine.js.
MIME_TYPES = {
    "pyodide.js": "text/javascript",
    "pyodide.asm.js": "text/javascript",
    "pyodide.asm.wasm": "application/wasm",
    "pyodide-lock.json": "application/json",
    "python_stdlib.zip": "application/zip",
}


def _cache_dir() -> Path:
    return Path.home() / ".pygamemaker" / "pyodide_cache" / PYODIDE_VERSION


def _default_downloader(url: str, timeout: int = 120) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def ensure_pyodide_files(
    progress_callback: Optional[Callable[[float, str], None]] = None,
    downloader: Optional[Callable[[str], bytes]] = None,
    cache_dir: Optional[Path] = None,
) -> Dict[str, bytes]:
    """Return {filename: bytes} for every file in CORE_FILES, downloading
    (into cache_dir, default ~/.pygamemaker/pyodide_cache/<version>/) any
    that aren't already cached.

    downloader defaults to a real HTTP GET (urllib) — injectable so tests
    never need real network access or a real 13 MB payload.

    Raises RuntimeError with an actionable message (matching this
    codebase's _missing_dependency_message convention) if a download
    fails — this needs network access ONCE, at export time, not at every
    play session (the whole point of the feature).
    """
    cache_dir = Path(cache_dir) if cache_dir is not None else _cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    get = downloader or _default_downloader

    result: Dict[str, bytes] = {}
    total = len(CORE_FILES)
    for i, filename in enumerate(CORE_FILES):
        cached_path = cache_dir / filename
        if progress_callback:
            progress_callback(i / total, f"Preparing offline Python runtime: {filename}...")
        if cached_path.exists():
            result[filename] = cached_path.read_bytes()
            continue
        try:
            data = get(_BASE_URL + filename)
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            raise RuntimeError(
                f"Could not download the offline Python runtime file "
                f"'{filename}' from {_BASE_URL}{filename}.\n\n"
                f"{e}\n\n"
                "The offline-bundle option needs internet access once, at "
                "export time, to download and cache Pyodide "
                f"(cached afterwards in {cache_dir}). "
                "Uncheck it to export with the normal CDN-loaded Python "
                "runtime instead (still works fine with internet at play "
                "time), or check your connection and try again."
            ) from e
        cached_path.write_bytes(data)
        result[filename] = data

    if progress_callback:
        progress_callback(1.0, "Offline Python runtime ready.")
    return result


def is_cached(cache_dir: Optional[Path] = None) -> bool:
    """True if every core file is already cached (no download needed)."""
    cache_dir = Path(cache_dir) if cache_dir is not None else _cache_dir()
    return all((cache_dir / f).exists() for f in CORE_FILES)
