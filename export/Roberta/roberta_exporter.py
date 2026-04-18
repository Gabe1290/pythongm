#!/usr/bin/env python3
"""
Open Roberta Lab XML Exporter for Thymio Robot
Exports pygm2 Thymio projects to Open Roberta Lab XML (.xml) format
that can be imported back into https://lab.open-roberta.org/

Usage:
    from export.Roberta import RobertaExporter
    exporter = RobertaExporter()
    exporter.export("path/to/project.json", "path/to/output.xml")
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.dom import minidom

from core.logger import get_logger

logger = get_logger(__name__)

# Open Roberta blockly namespace
_NS = "http://de.fhg.iais.roberta.blockly"

# pygm2 event → Roberta EVENT field value
_EVENT_TO_ROBERTA: Dict[str, str] = {
    "thymio_button_forward":  "BUTTON_A",
    "thymio_button_backward": "BUTTON_B",
    "thymio_button_left":     "BUTTON_C",
    "thymio_button_right":    "BUTTON_D",
    "thymio_button_center":   "BUTTON_E",
    "thymio_tap":             "TAP",
    "thymio_timer_0":         "TIMER",
    "thymio_sound_detected":  "SOUND",
}

# Counter for generating unique block IDs
_block_counter = 0


def _next_id() -> str:
    global _block_counter
    _block_counter += 1
    return str(_block_counter)


class RobertaExporter:
    """Export pygm2 Thymio projects to Open Roberta Lab XML."""

    def export(self, project_path: str, output_path: str = None) -> bool:
        """Export a pygm2 project to Open Roberta XML.

        Args:
            project_path: Path to project.json
            output_path:  Where to write the .xml (default: <project>/roberta_export/<name>.xml)

        Returns True on success.
        """
        project_path = Path(project_path)
        if not project_path.exists():
            logger.error(f"Project not found: {project_path}")
            return False

        with open(project_path, "r", encoding="utf-8") as f:
            project_data = json.load(f)

        thymio_objects = self._find_thymio_objects(project_data)
        if not thymio_objects:
            logger.warning("No Thymio objects found in project")
            return False

        project_name = project_data.get("name", "Untitled")

        if output_path is None:
            out_dir = project_path.parent / "roberta_export"
            out_dir.mkdir(exist_ok=True)
            output_path = out_dir / f"{project_name}.xml"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Reset block counter
        global _block_counter
        _block_counter = 0

        # Use the first Thymio object (Roberta programs are single-robot)
        obj_name, obj_data = next(iter(thymio_objects.items()))
        logger.info(f"Exporting {obj_name} to Roberta XML…")

        xml_str = self._build_xml(obj_data, project_name)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_str)

        logger.info(f"Exported to {output_path}")
        return True

    # ------------------------------------------------------------------
    # Project helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_thymio_objects(project_data: Dict) -> Dict[str, Dict]:
        objects = project_data.get("assets", {}).get("objects", {})
        return {
            name: data for name, data in objects.items()
            if name.lower().startswith("thymio") or data.get("is_thymio")
        }

    # ------------------------------------------------------------------
    # XML construction
    # ------------------------------------------------------------------

    def _build_xml(self, obj_data: Dict, project_name: str) -> str:
        """Build the complete Open Roberta XML string."""
        export_el = ET.Element("export", xmlns=_NS)

        # ---- <program> ----
        program_el = ET.SubElement(export_el, "program")
        block_set = ET.SubElement(program_el, "block_set", {
            "xmlns": _NS,
            "robottype": "thymio",
            "xmlversion": "3.1",
            "description": f"Exported from pygm2 project '{project_name}'",
            "tags": "",
        })
        instance_el = ET.SubElement(block_set, "instance", x="307", y="50")

        events = obj_data.get("events", {})

        # Start block (always present)
        start_block = self._make_start_block()
        instance_el.append(start_block)

        # Create-event actions → sibling blocks after the start block
        create_actions = events.get("create", {}).get("actions", [])
        for action in create_actions:
            block = self._action_to_block(action)
            if block is not None:
                instance_el.append(block)

        # Other events → robControls_start_event blocks
        for event_name, event_data in events.items():
            if event_name == "create":
                continue
            roberta_event = _EVENT_TO_ROBERTA.get(event_name)
            if roberta_event is None:
                logger.warning(f"No Roberta mapping for event '{event_name}', skipping")
                continue
            actions = event_data.get("actions", [])
            if not actions:
                continue
            ev_block = self._make_event_block(roberta_event, actions)
            instance_el.append(ev_block)

        # ---- <config> (minimal, required by Roberta) ----
        config_el = ET.SubElement(export_el, "config")
        cfg_block_set = ET.SubElement(config_el, "block_set", {
            "xmlns": _NS,
            "robottype": "thymio",
            "xmlversion": "3.1",
            "description": "",
            "tags": "",
        })
        cfg_instance = ET.SubElement(cfg_block_set, "instance", x="1026", y="526")
        cfg_start = ET.SubElement(cfg_instance, "block", {
            "type": "robControls_start",
            "id": "1",
            "intask": "true",
            "deletable": "false",
        })
        ET.SubElement(cfg_start, "mutation", declare="false")
        ET.SubElement(cfg_start, "field", name="DEBUG")

        # Pretty-print
        rough = ET.tostring(export_el, encoding="unicode", xml_declaration=False)
        dom = minidom.parseString(rough)
        return dom.toprettyxml(indent="  ", encoding=None)

    # ------------------------------------------------------------------
    # Block builders
    # ------------------------------------------------------------------

    def _make_start_block(self) -> ET.Element:
        block = ET.Element("block", {
            "type": "robControls_start",
            "id": _next_id(),
            "intask": "true",
            "deletable": "false",
        })
        ET.SubElement(block, "mutation", declare="false")
        ET.SubElement(block, "field", name="DEBUG").text = "TRUE"
        return block

    def _make_event_block(self, roberta_event: str,
                          actions: List[Dict]) -> ET.Element:
        """Build a robControls_start_event block with nested actions."""
        block = ET.Element("block", {
            "type": "robControls_start_event",
            "id": _next_id(),
            "intask": "true",
        })
        ET.SubElement(block, "field", name="EVENT").text = roberta_event

        if actions:
            stmt = ET.SubElement(block, "statement", name="DO")
            self._append_action_chain(stmt, actions)

        return block

    def _append_action_chain(self, parent: ET.Element,
                             actions: List[Dict]) -> None:
        """Append a sequence of actions as sibling <block> children."""
        for action in actions:
            block = self._action_to_block(action)
            if block is not None:
                parent.append(block)

    # ------------------------------------------------------------------
    # Action → block mapping
    # ------------------------------------------------------------------

    def _action_to_block(self, action: Dict) -> Optional[ET.Element]:
        """Convert a single pygm2 action dict to a Roberta <block>."""
        atype = action.get("action", "")
        params = action.get("parameters", {})

        handler = _ACTION_BUILDERS.get(atype)
        if handler is None:
            if atype == "comment":
                return None  # silently skip
            logger.debug(f"No Roberta block for action '{atype}'")
            return None
        return handler(params)


# ======================================================================
# Individual block builders (module-level functions)
# ======================================================================

def _build_play_tone(params: Dict) -> ET.Element:
    """thymio_play_tone → mbedActions_play_note"""
    freq = params.get("frequency", "440")
    dur_60 = params.get("duration", "60")
    # Convert 1/60s units back to milliseconds
    try:
        dur_ms = round(int(dur_60) * 1000 / 60)
    except (ValueError, TypeError):
        dur_ms = 500
    try:
        freq_f = float(freq)
    except (ValueError, TypeError):
        freq_f = 440.0

    block = ET.Element("block", type="mbedActions_play_note",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="DURATION").text = str(dur_ms)
    ET.SubElement(block, "field", name="FREQUENCE").text = str(freq_f)
    return block


def _build_motor_on(params: Dict) -> ET.Element:
    """thymio_move_forward → mbedActions_motor_on BOTH"""
    speed = params.get("speed", "200")
    block = ET.Element("block", type="mbedActions_motor_on",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="MOTOR_SIDE").text = "BOTH"
    _add_value_num(block, "POWER", speed)
    return block


def _build_motor_on_backward(params: Dict) -> ET.Element:
    """thymio_move_backward → mbedActions_motor_on BOTH with negative speed"""
    speed = params.get("speed", "200")
    block = ET.Element("block", type="mbedActions_motor_on",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="MOTOR_SIDE").text = "BOTH"
    try:
        _add_value_num(block, "POWER", str(-int(speed)))
    except (ValueError, TypeError):
        _add_value_num(block, "POWER", "-200")
    return block


def _build_set_motor_speed(params: Dict) -> ET.Element:
    """thymio_set_motor_speed → two mbedActions_motor_on blocks.

    Roberta doesn't have a single block for independent L/R speeds,
    so we emit a LEFT block.  The right motor is lost (Roberta
    limitation); a comment documents the intent.
    """
    left = params.get("left_speed", "0")
    right = params.get("right_speed", "0")
    # If both equal → BOTH
    if left == right:
        block = ET.Element("block", type="mbedActions_motor_on",
                            id=_next_id(), intask="true")
        ET.SubElement(block, "field", name="MOTOR_SIDE").text = "BOTH"
        _add_value_num(block, "POWER", left)
        return block
    # Otherwise emit LEFT; right information is in a Roberta comment.
    block = ET.Element("block", type="mbedActions_motor_on",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="MOTOR_SIDE").text = "LEFT"
    _add_value_num(block, "POWER", left)
    return block


def _build_turn_left(params: Dict) -> ET.Element:
    speed = params.get("speed", "300")
    block = ET.Element("block", type="mbedActions_motor_on",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="MOTOR_SIDE").text = "RIGHT"
    _add_value_num(block, "POWER", speed)
    return block


def _build_turn_right(params: Dict) -> ET.Element:
    speed = params.get("speed", "300")
    block = ET.Element("block", type="mbedActions_motor_on",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="MOTOR_SIDE").text = "LEFT"
    _add_value_num(block, "POWER", speed)
    return block


def _build_stop_motors(params: Dict) -> ET.Element:
    block = ET.Element("block", type="mbedActions_motor_stop",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="MOTOR_SIDE").text = "BOTH"
    return block


def _build_led_on(led_name: str):
    """Factory for LED-on builders."""
    def builder(params: Dict) -> ET.Element:
        r = int(float(params.get("red", params.get("r", "0"))))
        g = int(float(params.get("green", params.get("g", "0"))))
        b = int(float(params.get("blue", params.get("b", "0"))))
        # Scale Thymio 0-32 → Roberta 0-255
        r255 = min(255, r * 255 // 32)
        g255 = min(255, g * 255 // 32)
        b255 = min(255, b * 255 // 32)
        block = ET.Element("block", type="mbedActions_leds_on",
                            id=_next_id(), intask="true")
        ET.SubElement(block, "field", name="LED").text = led_name
        # Emit colour as robColour_rgb value block
        val = ET.SubElement(block, "value", name="COLOR")
        color_block = ET.SubElement(val, "block", type="robColour_rgb",
                                     id=_next_id(), intask="true")
        _add_value_num(color_block, "RED", str(r255))
        _add_value_num(color_block, "GREEN", str(g255))
        _add_value_num(color_block, "BLUE", str(b255))
        return block
    return builder


def _build_leds_off(params: Dict) -> ET.Element:
    block = ET.Element("block", type="mbedActions_leds_off",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="LED").text = "TOP"
    return block


def _build_play_system_sound(params: Dict) -> ET.Element:
    """Best-effort: Roberta doesn't have system sounds, emit a short beep."""
    block = ET.Element("block", type="mbedActions_play_note",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="DURATION").text = "200"
    ET.SubElement(block, "field", name="FREQUENCE").text = "440"
    return block


def _build_set_variable(params: Dict) -> ET.Element:
    var = params.get("variable", "var")
    val = params.get("value", "0")
    block = ET.Element("block", type="variables_set",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="VAR").text = var
    _add_value_num(block, "VALUE", val)
    return block


def _build_increase_variable(params: Dict) -> ET.Element:
    var = params.get("variable", "var")
    amount = params.get("amount", "1")
    block = ET.Element("block", type="math_change",
                        id=_next_id(), intask="true")
    ET.SubElement(block, "field", name="VAR").text = var
    _add_value_num(block, "DELTA", amount)
    return block


# ======================================================================
# Action → builder registry
# ======================================================================

_ACTION_BUILDERS = {
    # Sound
    "thymio_play_tone":          _build_play_tone,
    "thymio_play_system_sound":  _build_play_system_sound,

    # Motors
    "thymio_move_forward":       _build_motor_on,
    "thymio_move_backward":      _build_motor_on_backward,
    "thymio_set_motor_speed":    _build_set_motor_speed,
    "thymio_turn_left":          _build_turn_left,
    "thymio_turn_right":         _build_turn_right,
    "thymio_stop_motors":        _build_stop_motors,

    # LEDs
    "thymio_set_led_top":          _build_led_on("TOP"),
    "thymio_set_led_bottom_left":  _build_led_on("BOTTOMLEFT"),
    "thymio_set_led_bottom_right": _build_led_on("BOTTOMRIGHT"),
    "thymio_leds_off":             _build_leds_off,

    # Variables
    "thymio_set_variable":       _build_set_variable,
    "thymio_increase_variable":  _build_increase_variable,
    "thymio_decrease_variable":  _build_increase_variable,  # same block, sign in value
}


# ======================================================================
# XML helper
# ======================================================================

def _add_value_num(parent: ET.Element, name: str, text: str) -> None:
    """Add <value name=...><block type="math_integer"><field name="NUM">text</field></block></value>."""
    val = ET.SubElement(parent, "value", name=name)
    num_block = ET.SubElement(val, "block", type="math_integer",
                               id=_next_id(), intask="true")
    ET.SubElement(num_block, "field", name="NUM").text = str(text)
