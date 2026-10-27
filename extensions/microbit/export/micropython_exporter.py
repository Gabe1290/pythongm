#!/usr/bin/env python3
"""MicroPython exporter for micro:bit objects (Stage X, units X1-X2).

docs/MICROBIT_STAGE_X_PLAN.md is the map. In the shape of
``extensions/thymio/export/aseba_exporter.py`` -- object discovery, the
objects/<name>.json merge, and the per-object output all mirror it -- but
the output unit is a standalone ``main.py`` per micro:bit object (one real
board = one flat script, no event-handler indirection), not one shared
runtime. Condition/radio/sensor/generic-variable translators are added in
X3-X4; until then every action outside the X2 set is reported as
unsupported, which is the correct, honest state for this stage -- not a
bug.

Expressions (``_expr``) pass through as-is for now: quoted text and plain
numbers/identifiers are already valid Python/MicroPython syntax (a
variable name becomes a top-level global -- see the plan's "Variable
semantics"), so most authored values need no translation at all. GameMaker's
``irandom``/``random``/``choose`` builtins (the ones
``runtime/action_executor.py``'s ``_parse_value`` calls out as
intentionally supported, and the ones ``samples/microbit_1`` actually
uses) are NOT yet rewritten onto Python's ``random`` module -- deferred to
X4, where the generic ``set_variable`` translator first needs it, since no
code reachable before X4/X5 wiring calls ``_expr`` on a GM-function
expression yet.
"""
import json
from datetime import datetime
from pathlib import Path

from core.logger import get_logger

from ..images import IMAGES
from ..melodies import MELODIES
from ..actions import SENSORS

logger = get_logger(__name__)

# microbit_read_sensor's SENSORS entries -> the real device call. "sound
# level" is handled separately (V1/V2, below) since microphone is V2-only.
_SENSOR_CALLS = {
    "accelerometer x": "accelerometer.get_x()",
    "accelerometer y": "accelerometer.get_y()",
    "accelerometer z": "accelerometer.get_z()",
    "acceleration strength": "accelerometer.get_strength()",
    "compass heading": "compass.heading()",
    "light level": "display.read_light_level()",
    "temperature": "temperature()",
    "pin 0 analog": "pin0.read_analog()",
    "pin 1 analog": "pin1.read_analog()",
    "pin 2 analog": "pin2.read_analog()",
}
assert set(_SENSOR_CALLS) | {"sound level"} == set(SENSORS), \
    "every microbit_read_sensor choice needs a device call"


def _expr(raw, default="0") -> str:
    """A parameter's raw text as MicroPython source (not evaluated -- the
    device evaluates it at runtime). See the module docstring for the
    current, deliberately limited, scope."""
    text = str(raw if raw is not None and raw != "" else default).strip()
    return text if text else default


def _image_literal(spec: str) -> str:
    """``Image.<NAME>`` for a built-in name, else ``Image("...")`` -- the
    colon-separated digit-grid format our own action schema uses is
    already exactly what MicroPython's ``Image()`` constructor takes
    (confirmed against ``images.py``'s own docstring), so no reformatting
    is needed, only the literal/name choice."""
    name = spec.strip().upper()
    if name in IMAGES:
        return f"Image.{name}"
    return f"Image({spec.strip()!r})"


def _melody_call(raw_melody: str, tempo_expr: str) -> str:
    """``music.<NAME>`` for a built-in name, else ``music.play(notes,
    tempo=(4, bpm))`` -- mirrors ``handlers.py``'s own quoted-vs-bare
    handling: a quoted value is literal note text with the quotes
    stripped; an unquoted value is tried as a built-in name first, and
    used as literal note text otherwise (handlers.py's own fallback)."""
    raw = str(raw_melody)
    quoted = raw.strip().startswith('"')
    bare = raw.strip().strip('"').strip()
    if not quoted and bare.upper() in MELODIES:
        return f"music.{bare.upper()}"
    return f"music.play({bare!r}, tempo=(4, {tempo_expr}))"


class MicropythonExporter:
    """Export a project's micro:bit objects to standalone ``main.py`` files,
    one per object under ``<output>/<object_name>/main.py`` -- a real board
    only auto-runs a file with that exact name, so two boards' programs
    can't share one flat output directory."""

    def __init__(self):
        self.unsupported = set()
        self.v1_incompatible = set()
        self.indent_level = 0
        self.current_object = None
        self.board_version = "v2"

    def export(self, project_path, output_path=None, board_version="v2") -> bool:
        """``board_version`` is ``"v1"`` or ``"v2"`` (O6: a per-export
        choice, not a per-project setting, since a classroom with mixed
        boards shouldn't need two project copies). V2-only actions are
        skipped and warned on a V1 export (O2), not silently emitted to
        fail with an AttributeError on the device."""
        self.board_version = board_version
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
            self.v1_incompatible = set()
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
        imports, one-time setup from the Create event, then a single
        ``while True:`` loop whose body is the Step event (event polling
        joins the loop body starting in X5). Setup/body are generated
        before the import line so it can name only the modules actually
        used -- ``music``/``radio`` are separate MicroPython modules, not
        part of ``from microbit import *``."""
        setup_section = self._generate_setup(obj_data)
        self.indent_level = 1
        body = self._generate_loop_body(obj_data)
        self.indent_level = 0

        used_source = (setup_section or "") + "\n" + (body or "")
        imports = ["from microbit import *"]
        if "music." in used_source:
            imports.append("import music")
        if "radio." in used_source:
            imports.append("import radio")

        lines = [self._generate_header(obj_name, project_data), ""]
        lines.extend(imports)
        lines.append("")

        # One-time device setup these calls need before they're safe to
        # use, regardless of how many actions in the object call them:
        # radio.on() powers the radio on; an uncalibrated compass starts
        # an on-device calibration dance (tilt to light every LED) the
        # moment heading() is first called, so calibrate explicitly up
        # front instead of surprising the student mid-game.
        one_time = []
        if "radio." in used_source:
            one_time.append("radio.on()")
        if "compass.heading()" in used_source:
            one_time.append("# First use of the compass calibrates it (tilt the board")
            one_time.append("# until every LED lights, per the micro:bit's own routine).")
            one_time.append("compass.calibrate()")
        if one_time:
            lines.extend(one_time)
            lines.append("")

        if setup_section:
            lines.append(setup_section)
            lines.append("")

        lines.append("while True:")
        lines.append(body if body else "    pass")

        if self.unsupported:
            lines.append("")
            lines.append("# Not exported in this version (unsupported action type(s)): "
                         + ", ".join(sorted(self.unsupported)))

        if self.v1_incompatible:
            lines.append("")
            lines.append(f"# Not exported -- needs a V2 board ({self.board_version} chosen): "
                         + ", ".join(sorted(self.v1_incompatible)))

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
        X4: conditions + the generic variable/block subset)."""
        translators = {
            "microbit_show_image": self._translate_show_image,
            "microbit_scroll_text": self._translate_scroll_text,
            "microbit_show_number": self._translate_show_number,
            "microbit_set_pixel": self._translate_set_pixel,
            "microbit_clear_display": self._translate_clear_display,
            "microbit_set_brightness": self._translate_set_brightness,
            "microbit_play_tone": self._translate_play_tone,
            "microbit_play_melody": self._translate_play_melody,
            "microbit_stop_sound": self._translate_stop_sound,
            "microbit_radio_set_group": self._translate_radio_set_group,
            "microbit_radio_send": self._translate_radio_send,
            "microbit_read_sensor": self._translate_read_sensor,
        }
        return translators.get(action_type)

    # -- Display (X2) -------------------------------------------------------

    def _translate_show_image(self, params) -> str:
        image = _image_literal(str(params.get("image", "HEART")))
        hold = _expr(params.get("hold"), "0")
        lines = [f"display.show({image})"]
        if hold.strip() != "0":
            lines.append(f"sleep_ms({hold})")
        return '\n'.join(lines)

    def _translate_scroll_text(self, params) -> str:
        text = _expr(params.get("text", '"Hello"'), '"Hello"')
        delay = _expr(params.get("delay"), "150")
        return f"display.scroll({text}, delay={delay})"

    def _translate_show_number(self, params) -> str:
        value = _expr(params.get("value", "0"), "0")
        return f"display.show({value})"

    def _translate_set_pixel(self, params) -> str:
        x = _expr(params.get("x"), "0")
        y = _expr(params.get("y"), "0")
        brightness = _expr(params.get("brightness"), "9")
        return f"display.set_pixel({x}, {y}, {brightness})"

    def _translate_clear_display(self, params) -> str:
        return "display.clear()"

    def _translate_set_brightness(self, params) -> str:
        # Real-device scale conversion, found while writing this plan: our
        # schema/simulator use 0-255 (simulator.py clamps to that range),
        # but display.set_brightness() on the device takes 0-9. Computed
        # at runtime, not at export time, so a variable value still works.
        value = _expr(params.get("brightness"), "255")
        return f"display.set_brightness(round(({value}) / 255 * 9))"

    # -- Sound (X2) -----------------------------------------------------------

    def _translate_play_tone(self, params) -> str:
        frequency = _expr(params.get("frequency"), "440")
        duration = _expr(params.get("duration"), "500")
        return f"music.pitch({frequency}, {duration})"

    def _translate_play_melody(self, params) -> str:
        melody = str(params.get("melody", "DADADADUM"))
        tempo = _expr(params.get("tempo"), "120")
        return _melody_call(melody, tempo)

    def _translate_stop_sound(self, params) -> str:
        return "music.stop()"

    # -- Radio (X3) -----------------------------------------------------------

    def _translate_radio_set_group(self, params) -> str:
        # radio.on() itself is injected once in generate_main, not here --
        # calling it again every time the group changes is harmless but
        # noisy, and the group may be set more than once.
        group = _expr(params.get("group"), "0")
        return f"radio.config(group={group})"

    def _translate_radio_send(self, params) -> str:
        # radio.send() only takes a string on the device, unlike the
        # simulator's clean_message() which keeps numbers as numbers for
        # the in-process transport -- every value is wrapped here.
        value = _expr(params.get("value", 1), "1")
        return f"radio.send(str({value}))"

    # -- Sensors (X3) ---------------------------------------------------------

    def _translate_read_sensor(self, params):
        sensor = str(params.get("sensor", SENSORS[0])).strip().lower()
        var_raw = str(params.get("variable") or "sensor_value").strip()
        # "global.X" and a plain name both collapse to the same thing on a
        # single-board export: a top-level Python global in that board's
        # own file (see the plan's "Variable semantics").
        var_name = var_raw[len("global."):] if var_raw.startswith("global.") else var_raw

        if sensor == "sound level":
            if self.board_version == "v1":
                self.v1_incompatible.add("microbit_read_sensor (sound level)")
                return None
            return f"{var_name} = microphone.sound_level()"

        call = _SENSOR_CALLS.get(sensor)
        if call is None:
            self.unsupported.add(f"microbit_read_sensor ({sensor})")
            return None
        return f"{var_name} = {call}"


def export(project_path, output_path=None, board_version="v2") -> bool:
    """Module-level convenience wrapper, matching the Aseba exporter's shape."""
    return MicropythonExporter().export(project_path, output_path, board_version)
