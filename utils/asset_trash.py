"""Soft-delete trash for project assets.

Design decision (2026-08-09, see docs/ASSET_MANAGER_PLAN.md /
docs/CLEAN_PROJECT_PLAN.md — "the bulk-delete-undo design question"):
deliberately NOT a QUndoCommand-based undo/redo. The existing QUndoStack
usage elsewhere in this codebase (editors/room_undo_commands.py,
editors/playground_editor/playground_undo_commands.py, the sprite editor)
is scoped to live, in-memory canvas edits with no file I/O — undo/redo
of a room instance move, say, never touches disk. Asset deletion is a
different problem: it removes a project.json entry, deletes a physical
file, a thumbnail, a side file (<type>/<name>.json for rooms/objects/
playgrounds), and clears cross-references in OTHER assets (sprite ->
object). An in-memory undo stack also can't outlive what it needs to
protect against here — it's cleared on project switch or app restart,
exactly when "I didn't mean to delete that" is most likely to be
noticed.

Instead: move a deleted asset's files into <project>/.trash/ rather than
unlinking them, with a manifest (.trash/manifest.json) recording enough
to restore it. This is the one mechanism Asset Manager Tier 3 (bulk
delete, docs/ASSET_MANAGER_PLAN.md) and Clean Project (deleting unused/
orphaned assets, docs/CLEAN_PROJECT_PLAN.md) both need — implemented
once here, called by single-asset delete today and by both of those
whenever they're picked up, rather than three separate half-answers to
"what if that was a mistake."

Pure file/manifest logic, no Qt dependency, so it's usable from
core/asset_manager.py (the real, live-app delete path),
widgets/asset_tree/asset_operations.py's legacy fallback, and a future
bulk-delete/Clean-Project caller alike.
"""
import json
import shutil
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logger import get_logger
logger = get_logger(__name__)

TRASH_DIR_NAME = ".trash"
MANIFEST_NAME = "manifest.json"


def _trash_root(project_dir: Path) -> Path:
    return Path(project_dir) / TRASH_DIR_NAME


def _manifest_path(project_dir: Path) -> Path:
    return _trash_root(project_dir) / MANIFEST_NAME


def _load_manifest(project_dir: Path) -> List[Dict[str, Any]]:
    path = _manifest_path(project_dir)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, ValueError) as e:
        logger.warning(f"Could not read trash manifest {path}: {e}")
        return []


def _save_manifest(project_dir: Path, entries: List[Dict[str, Any]]) -> None:
    root = _trash_root(project_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = _manifest_path(project_dir)
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def trash_asset(project_dir: Path, asset_type: str, asset_name: str,
                 asset_data: Dict[str, Any],
                 side_file_rel: Optional[str] = None,
                 cleared_references: Optional[List[Dict[str, str]]] = None) -> str:
    """Move an asset's files into .trash/ and record a manifest entry.

    asset_data is the FULL project.json entry for this asset (recorded
    verbatim so restore_asset can hand it straight back). side_file_rel is
    the project-relative path to a <type>/<name>.json side file (rooms/
    objects/playgrounds), if one exists — this module doesn't know that
    convention itself, so the caller (which already does) passes it in.
    cleared_references is purely informational (e.g. "clearing this
    sprite blanked obj_player's sprite field") — restore does not
    auto-relink them, only lists them so a human can decide.

    Returns the trash entry id. Never raises for a missing file (some
    assets have no physical file at all, e.g. a room/object referenced
    only via its project.json entry + side file) — only for a real I/O
    error moving a file that DOES exist.
    """
    project_dir = Path(project_dir)
    entry_id = f"{asset_name}__{uuid.uuid4().hex[:12]}"
    entry_dir = _trash_root(project_dir) / asset_type / entry_id
    entry_dir.mkdir(parents=True, exist_ok=True)

    files: Dict[str, str] = {}

    def _move_if_exists(rel_path: Optional[str], key: str):
        if not rel_path:
            return
        src = project_dir / rel_path
        if not src.exists():
            return
        dest = entry_dir / Path(rel_path).name
        shutil.move(str(src), str(dest))
        files[key] = rel_path  # original relative path, for restore

    _move_if_exists(asset_data.get("file_path") or asset_data.get("project_path"), "main")
    _move_if_exists(asset_data.get("thumbnail"), "thumbnail")
    _move_if_exists(side_file_rel, "side_file")

    manifest = _load_manifest(project_dir)
    manifest.append({
        "id": entry_id,
        "asset_type": asset_type,
        "asset_name": asset_name,
        "deleted_at": datetime.now(timezone.utc).isoformat(),
        "asset_data": deepcopy(asset_data),
        "files": files,
        "cleared_references": cleared_references or [],
    })
    _save_manifest(project_dir, manifest)
    logger.debug(f"Trashed {asset_type}/{asset_name} as {entry_id}")
    return entry_id


def list_trash(project_dir: Path) -> List[Dict[str, Any]]:
    """Every trashed asset, newest first."""
    entries = _load_manifest(project_dir)
    return sorted(entries, key=lambda e: e.get("deleted_at", ""), reverse=True)


def restore_asset(project_dir: Path, trash_id: str) -> Optional[Dict[str, Any]]:
    """Move a trashed asset's files back and return its asset_data for the
    caller to re-insert into project_data["assets"][asset_type][asset_name].

    Refuses (returns None) if a file already exists at any destination the
    restore would write to — a same-named asset was created after the
    delete — rather than silently overwriting it. The trash entry is left
    in place in that case so nothing is lost; the caller should tell the
    user to rename or remove the conflicting asset first.
    """
    project_dir = Path(project_dir)
    manifest = _load_manifest(project_dir)
    entry = next((e for e in manifest if e.get("id") == trash_id), None)
    if entry is None:
        logger.warning(f"restore_asset: no trash entry {trash_id!r}")
        return None

    entry_dir = _trash_root(project_dir) / entry["asset_type"] / trash_id
    files = entry.get("files", {})

    # Verify no destination collision before moving anything (all-or-nothing).
    for key, rel_path in files.items():
        dest = project_dir / rel_path
        if dest.exists():
            logger.warning(
                f"restore_asset: refusing to overwrite existing file at "
                f"{dest} (trash entry {trash_id!r}, file kind {key!r})")
            return None

    for key, rel_path in files.items():
        src = entry_dir / Path(rel_path).name
        if not src.exists():
            continue
        dest = project_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))

    # Remove the (now-empty, or at least fully-consumed) trash entry dir
    # and its manifest record — a restored asset is no longer "in trash".
    shutil.rmtree(entry_dir, ignore_errors=True)
    manifest = [e for e in manifest if e.get("id") != trash_id]
    _save_manifest(project_dir, manifest)

    logger.debug(f"Restored {entry['asset_type']}/{entry['asset_name']} from {trash_id}")
    return deepcopy(entry["asset_data"])


def empty_trash(project_dir: Path, trash_id: Optional[str] = None) -> int:
    """Permanently delete one trash entry (trash_id given) or all of them
    (trash_id=None). Returns the number of entries removed."""
    project_dir = Path(project_dir)
    manifest = _load_manifest(project_dir)

    if trash_id is None:
        to_remove = manifest
        remaining: List[Dict[str, Any]] = []
    else:
        to_remove = [e for e in manifest if e.get("id") == trash_id]
        remaining = [e for e in manifest if e.get("id") != trash_id]

    for entry in to_remove:
        entry_dir = _trash_root(project_dir) / entry["asset_type"] / entry["id"]
        shutil.rmtree(entry_dir, ignore_errors=True)

    _save_manifest(project_dir, remaining)
    logger.debug(f"Emptied {len(to_remove)} trash entr{'y' if len(to_remove) == 1 else 'ies'}")
    return len(to_remove)
