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
"""
import time
from pathlib import Path
from typing import List

from core.logger import get_logger
logger = get_logger(__name__)

# A save's .tmp sibling lives only for the duration of a single synchronous
# write (milliseconds); this floor just guards against a sweep racing a
# write that happens to be in flight at the exact moment it runs.
DEFAULT_MIN_AGE_SECONDS = 60


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
