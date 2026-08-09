"""Clean Project (docs/CLEAN_PROJECT_PLAN.md / DEFERRED_ITEMS_PLAN.md item 11).

Tier 1: sweep orphaned ``*.tmp`` atomic-write siblings. core/project_manager.py's
``_atomic_write_json`` writes every JSON file (project.json, rooms/*.json,
objects/*.json, playgrounds/*.json) to a sibling ``<path>.tmp`` first, then
``os.replace``s it into place — a crash or power loss mid-write can
theoretically orphan the ``.tmp`` copy. Unlike an asset delete, a ``.tmp``
file was never routed through the asset system and is never the
authoritative copy of anything, so permanent removal (not the Trash) is
correct here — see utils/asset_trash.py's module docstring for the
contrasting case.

Tier 2: detect physical asset files on disk with no project.json entry
pointing at them ("shrink project size") — see
``find_orphaned_physical_files``. Detection only; deletion (Tier 3) isn't
built yet and, when it is, should route through the Trash like everything
else in item 10.5, unlike Tier 1's permanent removal.
"""
import time
from pathlib import Path
from typing import Any, Dict, List

from core.logger import get_logger
logger = get_logger(__name__)

# A save's .tmp sibling lives only for the duration of a single synchronous
# write (milliseconds); this floor just guards against a sweep racing a
# write that happens to be in flight at the exact moment it runs.
DEFAULT_MIN_AGE_SECONDS = 60

# Physical-file asset categories, mirroring core/asset_manager.py's
# SUPPORTED_FORMATS. Kept as a local copy rather than importing AssetManager
# — that class pulls in PySide6/pygame/PIL, which this module deliberately
# stays free of (pure filesystem logic, usable from a CLI or a test with no
# Qt app). "thumbnails" isn't a real asset category (nothing in project.json
# is typed "thumbnails"), but it's a real directory whose files are
# referenced by sprites'/backgrounds' own "thumbnail" field, so it gets the
# same orphan-detection treatment.
_PHYSICAL_ASSET_EXTENSIONS: Dict[str, set] = {
    "sprites": {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tga", ".webp"},
    "sounds": {".wav", ".mp3", ".ogg", ".m4a", ".aac", ".flac"},
    "backgrounds": {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tga", ".webp"},
    "fonts": {".ttf", ".otf", ".woff", ".woff2"},
    "thumbnails": {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tga", ".webp"},
}


def find_orphan_tmp_files(project_dir: Path, min_age_seconds: int = DEFAULT_MIN_AGE_SECONDS) -> List[Path]:
    """Every ``*.tmp`` file under ``project_dir`` older than ``min_age_seconds``.

    Read-only — callers that want to act on the result call
    ``sweep_orphan_tmp_files`` (or delete the returned paths themselves).
    """
    project_dir = Path(project_dir)
    found: List[Path] = []
    now = time.time()
    try:
        for entry in project_dir.rglob('*.tmp'):
            try:
                if not entry.is_file():
                    continue
                if now - entry.stat().st_mtime < min_age_seconds:
                    continue
                found.append(entry)
            except OSError:
                continue
    except OSError as e:
        logger.debug(f"Orphan-tmp scan skipped for {project_dir}: {e}")
    return found


def sweep_orphan_tmp_files(project_dir: Path, min_age_seconds: int = DEFAULT_MIN_AGE_SECONDS) -> List[Path]:
    """Delete every orphaned ``*.tmp`` file found by ``find_orphan_tmp_files``.

    Returns the list of paths actually removed (a path that fails to
    delete, e.g. a permissions error, is skipped rather than raising, so
    one bad entry can't abort the whole sweep).
    """
    removed: List[Path] = []
    for entry in find_orphan_tmp_files(project_dir, min_age_seconds):
        try:
            entry.unlink()
            removed.append(entry)
            logger.debug(f"Swept orphan tmp file: {entry}")
        except OSError as e:
            logger.debug(f"Could not remove orphan tmp file {entry}: {e}")
    return removed


def find_orphaned_physical_files(project_dir: Path, project_data: Dict[str, Any]) -> Dict[str, List[Path]]:
    """Tier 2: physical files under sprites/sounds/backgrounds/fonts/
    thumbnails that no project.json asset entry's ``file_path``/
    ``thumbnail`` references — the "shrink project size" case, genuinely
    different from ``utils/asset_usage.find_unused_assets`` (which only
    ever looks at project.json *entries*, never the filesystem — an entry
    can be "used" by a room while its own file went missing, and a file
    can sit on disk with no entry pointing at it at all, e.g. left behind
    by a manual `project.json` edit or a delete that predates the Trash
    mechanism).

    Read-only, grouped by directory. Deliberately restricted to known
    asset extensions per category (not every file under, say, sprites/) so
    a README or other file a user intentionally dropped there isn't
    reported as if it were asset debris.
    """
    project_dir = Path(project_dir)
    assets = (project_data or {}).get("assets") or {}

    referenced: set = set()
    for category in ("sprites", "sounds", "backgrounds", "fonts"):
        entries = assets.get(category) or {}
        if not isinstance(entries, dict):
            continue
        for asset_data in entries.values():
            if not isinstance(asset_data, dict):
                continue
            for key in ("file_path", "thumbnail"):
                rel = asset_data.get(key)
                if rel:
                    try:
                        referenced.add((project_dir / rel).resolve())
                    except OSError:
                        continue

    orphaned: Dict[str, List[Path]] = {}
    for category, extensions in _PHYSICAL_ASSET_EXTENSIONS.items():
        category_dir = project_dir / category
        if not category_dir.is_dir():
            continue
        found = []
        try:
            for entry in sorted(category_dir.iterdir()):
                if not entry.is_file() or entry.suffix.lower() not in extensions:
                    continue
                if entry.resolve() not in referenced:
                    found.append(entry)
        except OSError as e:
            logger.debug(f"Orphaned-file scan skipped for {category_dir}: {e}")
            continue
        if found:
            orphaned[category] = found
    return orphaned
