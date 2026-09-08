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

# Known-good SHA-256 per file at PYODIDE_VERSION (L11,
# docs/FULL_AUDIT_2026-09-07.md) -- pinned so a compromised CDN response,
# or a tampered/corrupted cache file, can't silently ship arbitrary JS/wasm
# inside every offline export. Computed from a fresh download of the real
# jsDelivr files and cross-checked with an independent sha256sum run; must
# be updated alongside PYODIDE_VERSION whenever that version bumps.
EXPECTED_SHA256 = {
    "pyodide.js": "c0069107621d5b942a659e737a12e774cc0451feaa2256f475d72e071d844ec7",
    "pyodide.asm.js": "919560652ed3dad3707cb3a394785da1e046fb13dc0defa162058ff230cb7eed",
    "pyodide.asm.wasm": "b7e66a19427a55010ac3367c1b6c64b893f9826f783412945fdf0c3337f3bc94",
    "pyodide-lock.json": "cd50b49de944c579045e122fe8628b31f9ce446379f032f36c05e273d38766e0",
    "python_stdlib.zip": "72894522b791858b9d613ac786b951d8b5094035dcf376313ea24a466810f336",
}

# Generous upper bound per file -- real sizes top out around 10 MB
# (pyodide.asm.wasm). Exists to bound memory during download (streamed in
# chunks, checked as it arrives), not as a tight budget; the hash check
# above is the real integrity guard.
_MAX_FILE_BYTES = 64 * 1024 * 1024  # 64 MB


def _cache_dir() -> Path:
    return Path.home() / ".pygamemaker" / "pyodide_cache" / PYODIDE_VERSION


def _default_downloader(url: str, timeout: int = 120) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        chunks = []
        total = 0
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            total += len(chunk)
            if total > _MAX_FILE_BYTES:
                raise ValueError(
                    f"Response from {url} exceeded the {_MAX_FILE_BYTES}-byte "
                    "cap for a single Pyodide core file; aborting download.")
            chunks.append(chunk)
        return b"".join(chunks)


def _verify_hash(filename: str, data: bytes, expected_sha256: Dict[str, str]) -> None:
    """Raise RuntimeError if data doesn't match expected_sha256[filename].
    A no-op for a filename with no recorded pin (defensive; every name in
    CORE_FILES has one in the real EXPECTED_SHA256 table)."""
    expected = expected_sha256.get(filename)
    if expected is None:
        return
    import hashlib
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise RuntimeError(
            f"The offline Python runtime file '{filename}' does not match "
            f"its expected SHA-256 (got {actual}, expected {expected}).\n\n"
            "This can mean a corrupted download, a tampered cache file, or "
            "a compromised CDN response -- refusing to embed it into the "
            "export. Delete the cached copy "
            f"({_cache_dir() / filename}) and try again, or check your "
            "connection."
        )


def ensure_pyodide_files(
    progress_callback: Optional[Callable[[float, str], None]] = None,
    downloader: Optional[Callable[[str], bytes]] = None,
    cache_dir: Optional[Path] = None,
    expected_sha256: Optional[Dict[str, str]] = None,
) -> Dict[str, bytes]:
    """Return {filename: bytes} for every file in CORE_FILES, downloading
    (into cache_dir, default ~/.pygamemaker/pyodide_cache/<version>/) any
    that aren't already cached.

    downloader defaults to a real HTTP GET (urllib) — injectable so tests
    never need real network access or a real 13 MB payload.

    expected_sha256 defaults to the real EXPECTED_SHA256 pin table (L11,
    docs/FULL_AUDIT_2026-09-07.md) -- every file, whether freshly
    downloaded or read back from cache, must match its pinned hash or
    this raises rather than embedding it. Also injectable, purely so
    tests can exercise the real verification code path against their own
    fake file content instead of either fighting the real CDN's hashes or
    disabling the check outright.

    Raises RuntimeError with an actionable message (matching this
    codebase's _missing_dependency_message convention) if a download
    fails — this needs network access ONCE, at export time, not at every
    play session (the whole point of the feature).
    """
    cache_dir = Path(cache_dir) if cache_dir is not None else _cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    get = downloader or _default_downloader
    hashes = expected_sha256 if expected_sha256 is not None else EXPECTED_SHA256

    result: Dict[str, bytes] = {}
    total = len(CORE_FILES)
    for i, filename in enumerate(CORE_FILES):
        cached_path = cache_dir / filename
        if progress_callback:
            progress_callback(i / total, f"Preparing offline Python runtime: {filename}...")
        if cached_path.exists():
            data = cached_path.read_bytes()
            _verify_hash(filename, data, hashes)
            result[filename] = data
            continue
        try:
            data = get(_BASE_URL + filename)
        except (urllib.error.URLError, OSError, TimeoutError, ValueError) as e:
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
        _verify_hash(filename, data, hashes)
        cached_path.write_bytes(data)
        result[filename] = data

    if progress_callback:
        progress_callback(1.0, "Offline Python runtime ready.")
    return result


def is_cached(cache_dir: Optional[Path] = None) -> bool:
    """True if every core file is already cached (no download needed)."""
    cache_dir = Path(cache_dir) if cache_dir is not None else _cache_dir()
    return all((cache_dir / f).exists() for f in CORE_FILES)
