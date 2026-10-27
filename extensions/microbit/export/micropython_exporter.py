#!/usr/bin/env python3
"""MicroPython exporter for micro:bit objects (Stage X, unit X1: skeleton).

docs/MICROBIT_STAGE_X_PLAN.md is the map. In the shape of
``extensions/thymio/export/aseba_exporter.py`` -- object discovery, the
objects/<name>.json merge, and the per-object output all mirror it -- but
the output unit is a standalone ``main.py`` per micro:bit object (one real
board = one flat script, no event-handler indirection), not one shared
runtime. Action/condition translators are added unit by unit (X2-X4);
until then every action an object uses is reported as unsupported, which
is the correct, honest state for this stage -- not a bug.
"""
import json
from datetime import datetime
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)


class MicropythonExporter:
    """Export a project's micro:bit objects to standalone ``main.py`` files,
    one per object under ``<output>/<object_name>/main.py`` -- a real board
    only auto-runs a file with that exact name, so two boards' programs
    can't share one flat output directory."""

    def __init__(self):
        self.unsupported = set()
        self.indent_level = 0
        self.current_object = None

    def export(self, project_path, output_path=None) -> bool:
        project_path = Path(project_path)
        if not project_path.exists():
            logger.error(f"Project not found: {project_path}")
            return False

        with open(project_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        # project.json's embedded object bodies can be stale -- the modular
        # project format keeps the authoritative copy in objects/<name>.json.
        # Same reason the Aseba/HTML5 exporters merge it first.
        self._load_object_files(project_path.parent, project_data)

        if output_path is None:
            output_path = project_path.parent / "microbit_export"
        else:
            output_path = Path(output_path)
        output_path.mkdir(exist_ok=True)

        microbit_objects = self._find_microbit_objects(project_data)
        if not microbit_objects:
            logger.warning("No micro:bit objects found in project")
            return False

        logger.info(f"Exporting {len(microbit_objects)} micro:bit object(s) to MicroPython...")

        for obj_name, obj_data in microbit_objects.items():
            self.unsupported = set()
            self.indent_level = 0
            self.current_object = obj_name

            code = self.generate_main(obj_name, obj_data, project_data)

            obj_dir = output_path / obj_name
            obj_dir.mkdir(exist_ok=True)
            main_file = obj_dir / "main.py"
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(code)
            logger.info(f"   Exported {obj_name} -> {main_file}")

        return True

    def _load_object_files(self, project_dir, project_data) -> None:
        """Merge objects/<name>.json side files into project_data (file
        wins), matching the project loader's precedence -- same helper the
        Aseba and HTML5 exporters already use for the same reason."""
        from utils.project_file_merge import merge_object_file

        objects_data = project_data.get('assets', {}).get('objects', {})
        objects_dir = project_dir / "objects"
        if not objects_dir.exists():
            return

        for object_name, object_data in list(objects_data.items()):
            if isinstance(object_data, str):
                object_data = {"name": object_name, "asset_type": "object"}
                objects_data[object_name] = object_data
            object_file = objects_dir / f"{object_name}.json"
            if object_file.exists():
                try:
                    with open(object_file, 'r', encoding='utf-8') as f:
                        file_object_data = json.load(f)
                    merge_object_file(object_data, file_object_data)
                except Exception as e:
                    logger.warning(f"Failed to load object file {object_file}: {e}")

    def _find_microbit_objects(self, project_data) -> dict:
        """Same identification rule as the simulator's own
        ``on_instance_created``: name starts with ``microbit`` (case-
        insensitive) or the object sets ``is_microbit``."""
        objects = project_data.get('assets', {}).get('objects', {})
        return {
            name: data for name, data in objects.items()
            if isinstance(data, dict) and (
                name.lower().startswith('microbit') or data.get('is_microbit', False)
            )
        }

    def generate_main(self, obj_name, obj_data, project_data) -> str:
        """The full ``main.py`` source for one micro:bit object: header,
        import, one-time setup from the Create event, then a single
        ``while True:`` loop whose body is the Step event (event polling
        joins the loop body starting in X5)."""
        lines = [self._generate_header(obj_name, project_data), "",
                  "from microbit import *", ""]

        setup_section = self._generate_setup(obj_data)
        if setup_section:
            lines.append(setup_section)
            lines.append("")

        lines.append("while True:")
        self.indent_level = 1
        body = self._generate_loop_body(obj_data)
        lines.append(body if body else "    pass")
        self.indent_level = 0

        if self.unsupported:
            lines.append("")
            lines.append("# Not exported in this version (unsupported action type(s)): "
                         + ", ".join(sorted(self.unsupported)))

        return '\n'.join(lines) + '\n'

    def _generate_header(self, obj_name, project_data) -> str:
        project_name = project_data.get('name', 'Untitled')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        return (
            f"# MicroPython for {obj_name}\n"
            f"# Generated by PyGameMaker\n"
            f"# Project: {project_name}\n"
            f"# Generated: {timestamp}\n"
            f"#\n"
            f"# Your micro:bit must already be running MicroPython. Copy this\n"
            f"# file onto it named exactly \"main.py\" -- the board runs it\n"
            f"# automatically on startup."
        )

    def _generate_setup(self, obj_data) -> str:
        events = obj_data.get('events', {})
        actions = events.get('create', {}).get('actions', [])
        lines = [code for code in (self._translate_action(a) for a in actions) if code]
        if not lines:
            return ""
        return '\n'.join(["# -- setup (from the Create event) --"] + lines)

    def _generate_loop_body(self, obj_data) -> str:
        events = obj_data.get('events', {})
        actions = events.get('step', {}).get('actions', [])
        lines = [code for code in (self._translate_action(a) for a in actions) if code]
        if not lines:
            return ""
        indent = '    ' * self.indent_level
        return '\n'.join(indent + line for line in lines)

    def _translate_action(self, action):
        """One action -> one (or more) lines of MicroPython, or ``None`` if
        this action type isn't exported yet -- tracked in ``unsupported``
        rather than silently dropped (the Kivy warning precedent)."""
        action_type = action.get('action', '')
        translator = self._get_action_translator(action_type)
        if translator is None:
            self.unsupported.add(action_type)
            return None
        return translator(action.get('parameters', {}))

    def _get_action_translator(self, action_type):
        """Populated unit by unit (X2: display/sound, X3: radio/sensors,
        X4: conditions + the generic variable/block subset). Empty here --
        X1 is the skeleton that proves discovery, merging and file layout
        before any translation exists."""
        translators = {}
        return translators.get(action_type)


def export(project_path, output_path=None) -> bool:
    """Module-level convenience wrapper, matching the Aseba exporter's shape."""
    return MicropythonExporter().export(project_path, output_path)
