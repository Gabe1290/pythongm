#!/usr/bin/env python3
"""
Main orchestrator for GMK file import.

Ties together the parser (gmk_parser) and converter (gmk_converter)
to import a GameMaker 8.0/8.1 .gmk file into a pygm2 project.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from importers.gmk_parser import GmkParser, GmkParseError
from importers.gmk_converter import GmkConverter

logger = logging.getLogger(__name__)


class GmkImportError(Exception):
    """Error during GMK file import."""
    pass


class GmkImportResult:
    """Detailed result of a GMK import operation."""

    def __init__(self):
        self.success: bool = False
        self.project_path: Optional[Path] = None
        self.warnings: list = []
        self.stats: dict = {}

    def __repr__(self):
        return (f"GmkImportResult(success={self.success}, "
                f"path={self.project_path}, "
                f"warnings={len(self.warnings)}, "
                f"stats={self.stats})")


def import_gmk(gmk_path: str, output_dir: str) -> bool:
    """
    Import a GameMaker 8.0/8.1 .gmk file and create a pygm2 project.

    Args:
        gmk_path: Path to the .gmk file
        output_dir: Directory where the pygm2 project will be created.
                    The directory will be created if it doesn't exist.

    Returns:
        True if import was successful

    Raises:
        GmkImportError: If the file cannot be parsed or converted
    """
    result = import_gmk_detailed(gmk_path, output_dir)
    if not result.success:
        raise GmkImportError("Import failed (see log for details)")
    return True


def import_gmk_detailed(gmk_path: str, output_dir: str) -> GmkImportResult:
    """
    Import a .gmk file with detailed result information.

    Same as import_gmk() but returns a GmkImportResult with statistics
    and warnings instead of raising on failure.
    """
    result = GmkImportResult()
    gmk_path = Path(gmk_path)
    output_dir = Path(output_dir)

    # Validate input
    if not gmk_path.exists():
        result.warnings.append(f"GMK file not found: {gmk_path}")
        logger.error(result.warnings[-1])
        return result

    if not gmk_path.suffix.lower() == ".gmk":
        result.warnings.append(f"Not a .gmk file: {gmk_path}")
        logger.error(result.warnings[-1])
        return result

    try:
        # Step 1: Parse the GMK binary file
        logger.info(f"Parsing GMK file: {gmk_path}")
        parser = GmkParser()
        gmk_project = parser.parse(str(gmk_path))
        result.warnings.extend(parser.warnings)

        # Step 2: Convert to pygm2 format and write files
        logger.info(f"Converting to pygm2 project: {output_dir}")
        converter = GmkConverter(gmk_project, output_dir)
        project_data = converter.convert()
        result.warnings.extend(converter.warnings)

        # Step 3: Write project.json
        project_file = output_dir / "project.json"
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)

        # Collect statistics
        assets = project_data.get("assets", {})
        for asset_type, asset_dict in assets.items():
            result.stats[asset_type] = len(asset_dict)

        result.success = True
        result.project_path = output_dir

        # Log and print summary
        summary_parts = [f"{k}: {v}" for k, v in result.stats.items() if v > 0]
        summary = f"Import complete: {', '.join(summary_parts)}"
        logger.info(summary)
        print(summary)
        if result.warnings:
            for w in result.warnings:
                print(f"  Warning: {w}")

    except GmkParseError as e:
        msg = f"Failed to parse GMK file: {e}"
        result.warnings.append(msg)
        logger.error(msg)
        print(msg)

    except Exception as e:
        msg = f"Import failed: {e}"
        result.warnings.append(msg)
        logger.error(msg, exc_info=True)
        print(msg)

    return result
