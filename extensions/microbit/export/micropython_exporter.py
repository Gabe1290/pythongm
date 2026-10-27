#!/usr/bin/env python3
"""MicroPython exporter for micro:bit objects (Stage X, units X1-X4).

docs/MICROBIT_STAGE_X_PLAN.md is the map. In the shape of
``extensions/thymio/export/aseba_exporter.py`` -- object discovery, the
objects/<name>.json merge, and the per-object output all mirror it -- but
the output unit is a standalone ``main.py`` per micro:bit object (one real
board = one flat script, no event-handler indirection), not one shared
runtime.

Expressions (``_expr``) pass through as-is for anything that isn't a
GameMaker builtin: quoted text and plain numbers/identifiers are already
valid Python/MicroPython syntax (a variable name becomes a top-level
global -- see the plan's "Variable semantics"). ``irandom``/``random``/
``choose`` (the ones ``runtime/action_executor.py``'s ``_parse_value``
calls out as intentionally supported, and the ones ``samples/microbit_1``
actually uses) ARE rewritten onto Python's ``random`` module (X4, where
``set_variable``'s value expressions first need it) -- anything else
(``GM_MATH_FUNCTIONS`` and friends) still passes through unchanged, a
documented, narrower-than-core MVP limit.

Event polling (X5) is not wired yet, so only the Create and Step events
are scanned; any condition/variable action elsewhere in the object is
correctly invisible to this exporter for now, not a bug.
"""
import json
import re
from datetime import datetime
from pathlib import Path

from core.logger import get_logger

from ..images import IMAGES
from ..melodies import MELODIES
from ..actions import SENSORS, GESTURES

logger = get_logger(__name__)

# Flat-list control-flow markers, exactly as runtime/action_executor.py's
# _execute_action_list_inner recognises them (including its aliases).
_START_BLOCK = ("start_block", "start")
_END_BLOCK = ("end_block", "end")
_ELSE = ("else_action", "else_block", "else")

# Actions whose handler returns True/False and so guard the next unit,
# GameMaker-style (core's own _QUESTION_ACTIONS is a different, core-only
# list; this exporter's set is its own, scoped to what X4 translates).
_QUESTION_ACTIONS = frozenset({
    "microbit_if_button", "microbit_if_gesture",
    "microbit_if_tilt", "microbit_if_pixel",
    "test_variable",
})

_COMPARE_OPS = {
    "equal": "==", "less": "<", "greater": ">",
    "less_equal": "<=", "greater_equal": ">=", "not_equal": "!=",
}

_IRANDOM_RE = re.compile(r'\birandom\s*\(')
_RANDOM_RE = re.compile(r'\brandom\s*\(')
_CHOOSE_RE = re.compile(r'\bchoose\s*\(')

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


def _rewrite_choose(text: str) -> str:
    """``choose(a, b, c)`` -> ``random.choice([a, b, c])``, matching the
    real closing parenthesis (bracket-depth aware) so a nested call
    inside an argument survives."""
    out = []
    i = 0
    while True:
        m = _CHOOSE_RE.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        out.append('random.choice([')
        depth = 1
        j = m.end()
        while j < len(text) and depth > 0:
            if text[j] == '(':
                depth += 1
            elif text[j] == ')':
                depth -= 1
            if depth > 0:
                out.append(text[j])
            j += 1
        out.append('])')
        i = j
    return ''.join(out)


def _rewrite_gm_builtins(text: str) -> str:
    """Rewrite GameMaker's ``irandom()``/``random()``/``choose()`` onto
    Python's ``random`` module -- the three builtins
    ``runtime/action_executor.py``'s ``_parse_value`` calls out as
    intentionally supported, and the ones ``samples/microbit_1`` actually
    uses (``irandom(5) + 1`` for a dice roll). Anything else passes
    through unchanged (the module docstring's documented MVP limit)."""
    text = _rewrite_choose(text)
    text = _IRANDOM_RE.sub('random.randint(0, ', text)
    text = _RANDOM_RE.sub('random.uniform(0, ', text)
    return text


def _expr(raw, default="0") -> str:
    """A parameter's raw text as MicroPython source (not evaluated -- the
    device evaluates it at runtime). See the module docstring for the
    current, deliberately limited, scope."""
    text = str(raw if raw is not None and raw != "" else default).strip()
    text = text if text else default
    return _rewrite_gm_builtins(text)


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
        body = self._generate_loop_body(obj_data)

        used_source = (setup_section or "") + "\n" + (body or "")
        imports = ["from microbit import *"]
        if "music." in used_source:
            imports.append("import music")
        if "radio." in used_source:
            imports.append("import radio")
        if "random." in used_source:
            imports.append("import random")

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
        nodes, _ = self._parse_actions(actions, 0)
        lines = self._render_nodes(nodes, 0)
        if not lines:
            return ""
        return '\n'.join(["# -- setup (from the Create event) --"] + lines)

    def _generate_loop_body(self, obj_data) -> str:
        events = obj_data.get('events', {})
        actions = events.get('step', {}).get('actions', [])
        nodes, _ = self._parse_actions(actions, 0)
        lines = self._render_nodes(nodes, 1)
        return '\n'.join(lines)

    # -- Flat-list control flow -> nested Python (X4) ------------------------
    #
    # runtime/action_executor.py's _execute_action_list_inner interprets a
    # FLAT action list at runtime: a question's result sets a skip_next
    # flag that skips exactly the next single unit (one action, or a
    # whole start_block...end_block group), with else_action attaching the
    # alternative. This parses that same flat shape once, ahead of time,
    # into a small tree, then renders it as real nested Python if/else --
    # correct for the recursive "a skipped question also skips its own
    # guarded unit" case Blockly actually generates (chained test_variable
    # guards, no blocks). A bare nested question immediately followed by
    # an else_action with no start_block/end_block (which the live
    # interpreter's single condition_was_false flag handles ambiguously,
    # and Blockly never emits -- CLAUDE.md's "Decided in S10") instead
    # gets well-defined nested if/else here; a deliberate, documented, and
    # narrower divergence, not a regression, since no currently authored
    # content takes that shape.

    def _is_question(self, action_name: str) -> bool:
        return action_name in _QUESTION_ACTIONS

    def _parse_actions(self, actions, i, stop_at=()):
        """Parse ``actions[i:]`` into a list of nodes, stopping (without
        consuming) at any action name in ``stop_at``. Returns
        ``(nodes, next_index)``."""
        nodes = []
        n = len(actions)
        while i < n:
            if actions[i].get("action", "") in stop_at:
                return nodes, i
            node, i = self._parse_one(actions, i)
            if node is not None:
                nodes.append(node)
        return nodes, i

    def _parse_one(self, actions, i):
        """Parse exactly one statement starting at ``actions[i]``: a plain
        action, or -- if it's a question -- an ``("if", cond, then, else)``
        node whose branches are each a guarded unit. Returns
        ``(node_or_None, next_index)``."""
        action = actions[i]
        name = action.get("action", "")

        if name in _START_BLOCK:
            body, i = self._parse_actions(actions, i + 1, stop_at=_END_BLOCK)
            if i < len(actions):
                i += 1  # consume the matching end_block
            return ("block", body), i

        if self._is_question(name):
            cond = self._translate_condition(action)
            i += 1
            then_body, i = self._parse_guarded_unit(actions, i)
            else_body = None
            if i < len(actions) and actions[i].get("action", "") in _ELSE:
                i += 1
                else_body, i = self._parse_guarded_unit(actions, i)
            if cond is None:
                return None, i
            return ("if", cond, then_body, else_body), i

        translated = self._translate_action(action)
        i += 1
        if translated is None:
            return None, i
        return ("stmt", translated), i

    def _parse_guarded_unit(self, actions, i):
        """The single unit a question guards: a whole
        start_block...end_block group, or exactly one further statement
        (itself possibly another question, handled recursively)."""
        if i >= len(actions):
            return [], i
        if actions[i].get("action", "") in _START_BLOCK:
            node, i = self._parse_one(actions, i)
            return (node[1] if node else []), i
        node, i = self._parse_one(actions, i)
        return ([node] if node else []), i

    def _render_nodes(self, nodes, indent: int):
        pad = '    ' * indent
        lines = []
        for kind, *rest in nodes:
            if kind == "stmt":
                lines.extend(pad + line for line in rest[0].split('\n'))
            elif kind == "block":
                lines.extend(self._render_nodes(rest[0], indent))
            elif kind == "if":
                cond, then_body, else_body = rest
                lines.append(f"{pad}if {cond}:")
                then_lines = self._render_nodes(then_body, indent + 1)
                lines.extend(then_lines if then_lines else [pad + "    pass"])
                if else_body is not None:
                    lines.append(f"{pad}else:")
                    else_lines = self._render_nodes(else_body, indent + 1)
                    lines.extend(else_lines if else_lines else [pad + "    pass"])
        return lines

    def _translate_action(self, action):
        """One statement action -> one (or more) lines of MicroPython, or
        ``None`` if this action type isn't exported yet -- tracked in
        ``unsupported`` rather than silently dropped (the Kivy warning
        precedent)."""
        action_type = action.get('action', '')
        translator = self._get_action_translator(action_type)
        if translator is None:
            self.unsupported.add(action_type)
            return None
        return translator(action.get('parameters', {}))

    def _translate_condition(self, action):
        """One question action -> a Python boolean expression (used in an
        ``if <expr>:``), or ``None`` if unsupported/V1-incompatible."""
        action_type = action.get('action', '')
        translator = self._get_condition_translator(action_type)
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
            "set_variable": self._translate_set_variable,
            "comment": self._translate_comment,
        }
        return translators.get(action_type)

    def _get_condition_translator(self, action_type):
        """Question actions (X4): each returns a Python boolean expression,
        not a statement -- rendered inside ``if <expr>:`` by
        ``_render_nodes``."""
        translators = {
            "microbit_if_button": self._translate_if_button,
            "microbit_if_gesture": self._translate_if_gesture,
            "microbit_if_tilt": self._translate_if_tilt,
            "microbit_if_pixel": self._translate_if_pixel,
            "test_variable": self._translate_test_variable,
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

    # -- Generic variable + comment subset (X4) --------------------------

    def _variable_name(self, params) -> str:
        """"global.X" and a plain name both collapse to a top-level
        Python global on a single-board export; "other" scope has no
        meaning (no other instances on one board) and is unsupported."""
        return str(params.get("variable") or params.get("variable_name") or "").strip()

    def _translate_set_variable(self, params):
        scope = str(params.get("scope", "self")).strip().lower()
        if scope == "other":
            self.unsupported.add("set_variable (other scope)")
            return None
        var = self._variable_name(params)
        if not var:
            return None
        value = _expr(params.get("value", "0"), "0")
        if params.get("relative", False):
            return f"{var} += ({value})"
        return f"{var} = {value}"

    def _translate_comment(self, params):
        text = str(params.get("text", "")).strip()
        if not text:
            return None
        return '\n'.join(f"# {line}" for line in text.splitlines())

    # -- Conditions (X4) -----------------------------------------------------

    def _translate_test_variable(self, params):
        scope = str(params.get("scope", "self")).strip().lower()
        if scope == "other":
            self.unsupported.add("test_variable (other scope)")
            return None
        var = self._variable_name(params)
        if not var:
            return None
        value = _expr(params.get("value", "0"), "0")
        op = _COMPARE_OPS.get(str(params.get("operation", "equal")).strip().lower(), "==")
        return f"{var} {op} ({value})"

    def _translate_if_button(self, params):
        button = str(params.get("button", "a")).strip().lower()
        if button == "a":
            return "button_a.is_pressed()"
        if button == "b":
            return "button_b.is_pressed()"
        if button == "ab":
            return "(button_a.is_pressed() and button_b.is_pressed())"
        if button == "logo":
            if self.board_version == "v1":
                self.v1_incompatible.add("microbit_if_button (logo)")
                return None
            return "pin_logo.is_touched()"
        self.unsupported.add(f"microbit_if_button ({button})")
        return None

    def _translate_if_gesture(self, params):
        gesture = str(params.get("gesture", "shake")).strip().lower()
        if gesture not in GESTURES:
            self.unsupported.add(f"microbit_if_gesture ({gesture})")
            return None
        return f"accelerometer.is_gesture({gesture!r})"

    def _translate_if_tilt(self, params):
        axis = str(params.get("axis", "x")).strip().lower()
        if axis not in ("x", "y", "z"):
            self.unsupported.add(f"microbit_if_tilt ({axis})")
            return None
        comparison = str(params.get("comparison", ">")).strip()
        value = _expr(params.get("value"), "0")
        return f"accelerometer.get_{axis}() {comparison} ({value})"

    def _translate_if_pixel(self, params):
        x = _expr(params.get("x"), "0")
        y = _expr(params.get("y"), "0")
        comparison = str(params.get("comparison", ">")).strip()
        value = _expr(params.get("value"), "0")
        return f"display.get_pixel({x}, {y}) {comparison} ({value})"


def export(project_path, output_path=None, board_version="v2") -> bool:
    """Module-level convenience wrapper, matching the Aseba exporter's shape."""
    return MicropythonExporter().export(project_path, output_path, board_version)
