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
``find_orphaned_physical_files``.

Tier 3: trash the files Tier 2 finds — see ``trash_orphaned_file`` and
friends. Deliberately its OWN manifest/``.trash_orphaned_files/`` store,
NOT ``utils/asset_trash.py``'s ``.trash/`` mechanism, even though the
move-instead-of-unlink idea is the same: an orphaned file has no
project.json entry at all, but ``core/asset_manager.py``'s
``AssetManager.restore_from_trash`` unconditionally re-inserts a restored
entry into ``assets_cache[asset_type][asset_name]`` — reusing that path
for a bare file would plant a fake asset entry (just a raw ``file_path``,
none of the real shape a sprite/sound/background asset needs) into the
live project the next time anything saves. Sharing the manifest would
also surface these entries in the general "Restore Deleted Assets"
dialog, whose Restore button goes through that exact method. A second,
smaller, asset-model-free store avoids both problems entirely.
"""
import json
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logger import get_logger
logger = get_logger(__name__)

ORPHAN_TRASH_DIR_NAME = ".trash_orphaned_files"
_ORPHAN_MANIFEST_NAME = "manifest.json"

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


def _orphan_trash_root(project_dir: Path) -> Path:
    return Path(project_dir) / ORPHAN_TRASH_DIR_NAME


def _orphan_manifest_path(project_dir: Path) -> Path:
    return _orphan_trash_root(project_dir) / _ORPHAN_MANIFEST_NAME


def _load_orphan_manifest(project_dir: Path) -> List[Dict[str, Any]]:
    path = _orphan_manifest_path(project_dir)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, ValueError) as e:
        logger.warning(f"Could not read orphan-trash manifest {path}: {e}")
        return []


def _save_orphan_manifest(project_dir: Path, entries: List[Dict[str, Any]]) -> None:
    root = _orphan_trash_root(project_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = _orphan_manifest_path(project_dir)
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def trash_orphaned_file(project_dir: Path, relative_path: str) -> Optional[str]:
    """Move an orphaned physical file (as found by
    ``find_orphaned_physical_files``) into ``.trash_orphaned_files/``
    instead of deleting it outright, and record enough to restore it.

    ``relative_path`` is project-relative (posix-style), e.g.
    ``"sprites/spr_leftover.png"``. Returns the trash entry id, or None if
    the source file doesn't exist (nothing to trash — a caller re-scanning
    stale results shouldn't crash on it).
    """
    project_dir = Path(project_dir)
    src = project_dir / relative_path
    if not src.exists():
        return None

    entry_id = f"{Path(relative_path).stem}__{uuid.uuid4().hex[:12]}"
    entry_dir = _orphan_trash_root(project_dir) / entry_id
    entry_dir.mkdir(parents=True, exist_ok=True)
    dest = entry_dir / Path(relative_path).name
    shutil.move(str(src), str(dest))

    manifest = _load_orphan_manifest(project_dir)
    manifest.append({
        "id": entry_id,
        "relative_path": relative_path,
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    })
    _save_orphan_manifest(project_dir, manifest)
    logger.debug(f"Trashed orphaned file {relative_path} as {entry_id}")
    return entry_id


def list_orphan_trash(project_dir: Path) -> List[Dict[str, Any]]:
    """Every trashed orphaned file, newest first."""
    entries = _load_orphan_manifest(project_dir)
    return sorted(entries, key=lambda e: e.get("deleted_at", ""), reverse=True)


def restore_orphaned_file(project_dir: Path, trash_id: str) -> Optional[str]:
    """Move a trashed orphaned file back to its original relative path.

    Refuses (returns None) if a file already exists at the destination —
    something new was created at that path since the trash — rather than
    overwriting it; the trash entry is left in place so nothing is lost.
    Returns the restored relative path on success.
    """
    project_dir = Path(project_dir)
    manifest = _load_orphan_manifest(project_dir)
    entry = next((e for e in manifest if e.get("id") == trash_id), None)
    if entry is None:
        logger.warning(f"restore_orphaned_file: no trash entry {trash_id!r}")
        return None

    rel = entry["relative_path"]
    dest = project_dir / rel
    if dest.exists():
        logger.warning(
            f"restore_orphaned_file: refusing to overwrite existing file at "
            f"{dest} (trash entry {trash_id!r})")
        return None

    entry_dir = _orphan_trash_root(project_dir) / trash_id
    src = entry_dir / Path(rel).name
    if not src.exists():
        logger.warning(f"restore_orphaned_file: trashed file missing for {trash_id!r}")
        return None

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    shutil.rmtree(entry_dir, ignore_errors=True)

    manifest = [e for e in manifest if e.get("id") != trash_id]
    _save_orphan_manifest(project_dir, manifest)
    logger.debug(f"Restored orphaned file {rel} from {trash_id}")
    return rel


def empty_orphan_trash(project_dir: Path, trash_id: Optional[str] = None) -> int:
    """Permanently delete one orphan-trash entry (``trash_id`` given) or
    all of them (``trash_id=None``). Returns the number of entries removed."""
    project_dir = Path(project_dir)
    manifest = _load_orphan_manifest(project_dir)

    if trash_id is None:
        count = len(manifest)
        shutil.rmtree(_orphan_trash_root(project_dir), ignore_errors=True)
        return count

    entry = next((e for e in manifest if e.get("id") == trash_id), None)
    if entry is None:
        return 0
    shutil.rmtree(_orphan_trash_root(project_dir) / trash_id, ignore_errors=True)
    manifest = [e for e in manifest if e.get("id") != trash_id]
    _save_orphan_manifest(project_dir, manifest)
    return 1
