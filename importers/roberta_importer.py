#!/usr/bin/env python3
"""
Open Roberta Lab XML importer for PyGameMaker (pygm2).

Converts Thymio programs exported from Open Roberta Lab (.xml, NEPO
blockly format) into pygm2 Thymio projects.

Usage:
    from importers.roberta_importer import import_roberta

    result = import_roberta("path/to/program.xml", "path/to/output_project")
"""

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.logger import get_logger

logger = get_logger(__name__)

# XML namespace used by Open Roberta exports
NS = {"rb": "http://de.fhg.iais.roberta.blockly"}


# ============================================================================
# Roberta event-block → pygm2 event mapping
# ============================================================================

# robControls_start_event EVENT field → pygm2 event name
_EVENT_MAP: Dict[str, str] = {
    # Thymio buttons (Roberta uses A-E)
    "BUTTON_A": "thymio_button_forward",
    "BUTTON_B": "thymio_button_backward",
    "BUTTON_C": "thymio_button_left",
    "BUTTON_D": "thymio_button_right",
    "BUTTON_E": "thymio_button_center",
    # Sensors / other
    "TAP":   "thymio_tap",
    "TIMER": "thymio_timer_0",
    "SOUND": "thymio_sound_detected",
}


# ============================================================================
# Result / error types
# ============================================================================

class RobertaImportError(Exception):
    """Raised when an Open Roberta XML cannot be imported."""


class RobertaImportResult:
    """Holds statistics from an import run."""

    def __init__(self):
        self.project_name: str = ""
        self.events_imported: int = 0
        self.actions_imported: int = 0
        self.warnings: List[str] = []

    def __repr__(self):
        return (f"RobertaImportResult(project={self.project_name!r}, "
                f"events={self.events_imported}, actions={self.actions_imported}, "
                f"warnings={len(self.warnings)})")


# ============================================================================
# Public entry point
# ============================================================================

def import_roberta(xml_path: str, output_dir: str) -> bool:
    """Import an Open Roberta XML into a pygm2 project directory.

    Returns True on success, False on failure.
    """
    try:
        result = import_roberta_detailed(xml_path, output_dir)
        for w in result.warnings:
            logger.warning(f"Roberta import: {w}")
        return True
    except RobertaImportError as exc:
        logger.error(f"Roberta import failed: {exc}")
        return False


def import_roberta_detailed(xml_path: str, output_dir: str) -> RobertaImportResult:
    """Import with full result details.  Raises *RobertaImportError* on failure."""

    xml_path = Path(xml_path)
    output_dir = Path(output_dir)

    if not xml_path.exists():
        raise RobertaImportError(f"File not found: {xml_path}")

    result = RobertaImportResult()
    result.project_name = xml_path.stem

    # ------------------------------------------------------------------
    # 1.  Parse the XML
    # ------------------------------------------------------------------
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        raise RobertaImportError(f"Invalid XML: {exc}") from exc

    root = tree.getroot()

    # Strip namespace prefix from tag for convenience
    tag = _strip_ns(root.tag)
    if tag != "export":
        raise RobertaImportError(
            f"Expected <export> root element, got <{tag}>")

    # Find <program>/<block_set>
    program_el = root.find("rb:program", NS)
    if program_el is None:
        # Try without namespace (some exports omit it)
        program_el = root.find("program")
    if program_el is None:
        raise RobertaImportError("No <program> element found")

    block_set = program_el.find("rb:block_set", NS)
    if block_set is None:
        block_set = program_el.find("block_set")
    if block_set is None:
        raise RobertaImportError("No <block_set> inside <program>")

    robottype = block_set.attrib.get("robottype", "")
    if robottype != "thymio":
        raise RobertaImportError(
            f"Expected robottype='thymio', got '{robottype}'")

    instance_el = block_set.find("rb:instance", NS)
    if instance_el is None:
        instance_el = block_set.find("instance")
    if instance_el is None:
        raise RobertaImportError("No <instance> inside <block_set>")

    # ------------------------------------------------------------------
    # 2.  Walk the top-level blocks and convert
    # ------------------------------------------------------------------
    events: Dict[str, Dict[str, Any]] = {}

    # In Open Roberta XML, the <instance> contains all blocks as direct
    # children.  The robControls_start block is a marker; all subsequent
    # sibling blocks form its sequential body (they are NOT nested inside
    # the start block).  Event handlers (robControls_start_event) start
    # their own stack and are handled separately.
    all_blocks = _child_blocks(instance_el)

    # First pass: find event handler blocks and their positions so we
    # can separate them from the main program.
    event_indices: set = set()
    for i, block in enumerate(all_blocks):
        btype = block.attrib.get("type", "")
        if btype == "robControls_start_event":
            event_field = _field(block, "EVENT")
            pygm2_event = _EVENT_MAP.get(event_field)
            if pygm2_event is None:
                result.warnings.append(
                    f"Unknown Roberta event '{event_field}', skipped")
            else:
                actions = _convert_statement(block, "DO", result)
                if actions:
                    events.setdefault(pygm2_event, {"actions": []})
                    events[pygm2_event]["actions"].extend(actions)
                    result.events_imported += 1
            event_indices.add(i)

    # Second pass: everything that is not a start marker or event
    # handler belongs to the main program ("create" event).
    create_actions: List[Dict] = []
    for i, block in enumerate(all_blocks):
        if i in event_indices:
            continue
        btype = block.attrib.get("type", "")
        if btype == "robControls_start":
            # The start block may itself contain a <statement name="DO">
            # with nested actions, plus a <next> chain.
            create_actions.extend(_convert_chain(block, result))
        else:
            # Sibling action / control-flow block — part of the main
            # program body.
            create_actions.extend(_convert_block(block, result))
    if create_actions:
        events["create"] = {"actions": create_actions}
        result.events_imported += 1

    # ------------------------------------------------------------------
    # 3.  Assemble the project
    # ------------------------------------------------------------------
    now = datetime.now().isoformat()

    object_data = {
        "name": "thymio_robot",
        "asset_type": "object",
        "sprite": "",
        "is_thymio": True,
        "visible": True,
        "solid": False,
        "persistent": False,
        "imported": True,
        "parent": "",
        "events": events,
        "created": now,
        "modified": now,
    }

    room_data = {
        "name": "room_main",
        "asset_type": "room",
        "width": 800,
        "height": 600,
        "speed": 60,
        "background": "",
        "background_color": "#FFFFFF",
        "instances": [
            {
                "object_name": "thymio_robot",
                "x": 400,
                "y": 300,
            }
        ],
        "imported": True,
        "created": now,
        "modified": now,
    }

    project_data = {
        "name": result.project_name,
        "version": "1.0.0",
        "created": now,
        "modified": now,
        "settings": {
            "window_title": result.project_name,
            "window_width": 800,
            "window_height": 600,
            "room_speed": 60,
        },
        "assets": {
            "sprites": {},
            "sounds": {},
            "backgrounds": {},
            "objects": {"thymio_robot": object_data},
            "rooms": {"room_main": room_data},
            "scripts": {},
            "fonts": {},
            "data": {},
        },
    }

    # ------------------------------------------------------------------
    # 4.  Write to output directory
    # ------------------------------------------------------------------
    output_dir.mkdir(parents=True, exist_ok=True)

    for subdir in ("sprites", "sounds", "backgrounds", "objects",
                    "rooms", "scripts", "fonts", "data", "thumbnails"):
        (output_dir / subdir).mkdir(exist_ok=True)

    _write_json(output_dir / "project.json", project_data)
    _write_json(output_dir / "objects" / "thymio_robot.json", object_data)
    _write_json(output_dir / "rooms" / "room_main.json", room_data)

    logger.info(f"Roberta import complete: {result}")
    return result


# ============================================================================
# Block conversion helpers
# ============================================================================

def _convert_chain(start_block, result: RobertaImportResult) -> List[Dict]:
    """Convert a top-level start block and its <next> chain.

    Actions that are direct children of the start block's <statement name="DO">
    are included, followed by any blocks chained via <next>.
    """
    actions: List[Dict] = []

    # Actions nested inside <statement name="DO">
    stmt = _statement(start_block, "DO")
    if stmt is not None:
        first = _first_block(stmt)
        if first is not None:
            actions.extend(_follow_chain(first, result))

    # Also follow <next> siblings of the start block itself
    nxt = _next_block(start_block)
    if nxt is not None:
        actions.extend(_follow_chain(nxt, result))

    return actions


def _convert_statement(parent_block, stmt_name: str,
                       result: RobertaImportResult) -> List[Dict]:
    """Convert the block chain inside a <statement name=...>.

    Open Roberta exports sometimes put chained blocks as direct siblings
    inside the ``<statement>`` (instead of linking them via ``<next>``).
    We handle both layouts: walk all sibling ``<block>`` children, and
    for each one also follow any ``<next>`` chain.
    """
    stmt = _statement(parent_block, stmt_name)
    if stmt is None:
        return []
    actions: List[Dict] = []
    for block in _child_blocks(stmt):
        actions.extend(_follow_chain(block, result))
    return actions


def _follow_chain(block, result: RobertaImportResult) -> List[Dict]:
    """Walk a <next> chain starting at *block*, converting each block."""
    actions: List[Dict] = []
    current = block
    while current is not None:
        converted = _convert_block(current, result)
        actions.extend(converted)
        current = _next_block(current)
    return actions


def _convert_block(block, result: RobertaImportResult) -> List[Dict]:
    """Convert a single Roberta block into zero or more pygm2 actions."""
    btype = block.attrib.get("type", "")

    # ---- Tone / note ----
    if btype in ("mbedActions_play_note", "mbedActions_play_tone"):
        freq = _field_or_value_float(block, "FREQUENCE", 440)
        dur_ms = _field_or_value_float(block, "DURATION", 500)
        dur_60 = max(1, round(dur_ms * 60 / 1000))
        result.actions_imported += 1
        return [_action("thymio_play_tone", frequency=str(int(freq)),
                        duration=str(dur_60))]

    # ---- Motors ----
    if btype == "mbedActions_motor_on":
        side = _field(block, "MOTOR_SIDE") or "BOTH"
        power = _value_str(block, "POWER", "200")
        result.actions_imported += 1
        if side == "BOTH":
            return [_action("thymio_move_forward", speed=power)]
        return [_action("thymio_set_motor_speed",
                        left_speed=power if side == "LEFT" else "0",
                        right_speed=power if side == "RIGHT" else "0")]

    if btype == "mbedActions_motor_stop":
        result.actions_imported += 1
        return [_action("thymio_stop_motors")]

    if btype == "mbedActions_motor_on_for":
        side = _field(block, "MOTOR_SIDE") or "BOTH"
        power = _value_str(block, "POWER", "200")
        result.actions_imported += 1
        result.warnings.append(
            "motor_on_for: duration not directly supported, "
            "imported as motor_on (set speed)")
        if side == "BOTH":
            return [_action("thymio_move_forward", speed=power)]
        return [_action("thymio_set_motor_speed",
                        left_speed=power if side == "LEFT" else "0",
                        right_speed=power if side == "RIGHT" else "0")]

    # ---- LEDs ----
    if btype == "mbedActions_leds_on":
        r, g, b = _extract_color(block)
        led = _field(block, "LED") or "TOP"
        result.actions_imported += 1
        if led in ("BOTTOM_LEFT", "BOTTOMLEFT"):
            return [_action("thymio_set_led_bottom_left",
                            r=str(r), g=str(g), b=str(b))]
        if led in ("BOTTOM_RIGHT", "BOTTOMRIGHT"):
            return [_action("thymio_set_led_bottom_right",
                            r=str(r), g=str(g), b=str(b))]
        return [_action("thymio_set_led_top",
                        r=str(r), g=str(g), b=str(b))]

    if btype == "mbedActions_leds_off":
        result.actions_imported += 1
        return [_action("thymio_leds_off")]

    # ---- Control flow: repeat ----
    if btype in ("controls_repeat_ext", "controls_repeat"):
        times = _value_str(block, "TIMES", "1")
        body = _convert_statement(block, "DO", result)
        if body:
            # Flatten: emit the body *times* times (pygm2 has no loop
            # action for Thymio — unroll up to a reasonable limit).
            try:
                n = int(times)
            except (ValueError, TypeError):
                n = 1
                result.warnings.append(
                    f"Repeat count is expression '{times}', using 1")
            n = min(n, 200)  # safety cap
            return body * n
        return []

    # ---- Control flow: wait ----
    if btype in ("robControls_wait_time", "robControls_wait"):
        result.warnings.append(
            "Wait/delay block has no direct Thymio equivalent, skipped")
        return [_comment_action(f"[Roberta] wait block ({btype})")]

    # ---- Variables ----
    if btype == "variables_set":
        var_name = _field(block, "VAR") or "var"
        value = _value_str(block, "VALUE", "0")
        result.actions_imported += 1
        return [_action("thymio_set_variable",
                        variable=var_name, value=value)]

    if btype == "math_change":
        var_name = _field(block, "VAR") or "var"
        delta = _value_str(block, "DELTA", "1")
        result.actions_imported += 1
        return [_action("thymio_set_variable",
                        variable=var_name, value=f"{var_name} + {delta}")]

    # ---- System sound ----
    if btype == "mbedActions_play_setVolume":
        result.warnings.append("Volume control not supported, skipped")
        return []

    # ---- Fallback: unknown block → comment ----
    result.warnings.append(f"Unsupported block type '{btype}'")
    return [_comment_action(f"[Roberta] unsupported: {btype}")]


# ============================================================================
# Action construction helpers
# ============================================================================

def _action(action_name: str, **params) -> Dict[str, Any]:
    return {"action": action_name, "parameters": params}


def _comment_action(text: str) -> Dict[str, Any]:
    return {"action": "comment", "parameters": {"text": text}}


# ============================================================================
# XML navigation helpers
# ============================================================================

def _strip_ns(tag: str) -> str:
    """Remove namespace prefix: ``{http://...}export`` → ``export``."""
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _child_blocks(parent) -> List:
    """Return all direct <block> children, with or without namespace."""
    blocks = parent.findall("rb:block", NS)
    if not blocks:
        blocks = parent.findall("block")
    return blocks


def _first_block(parent) -> Optional[Any]:
    """Return the first <block> child."""
    bl = parent.find("rb:block", NS)
    if bl is None:
        bl = parent.find("block")
    return bl


def _next_block(block) -> Optional[Any]:
    """Follow a <next><block>…</block></next> link."""
    nxt = block.find("rb:next", NS)
    if nxt is None:
        nxt = block.find("next")
    if nxt is None:
        return None
    return _first_block(nxt)


def _statement(block, name: str) -> Optional[Any]:
    """Find <statement name='...'>."""
    for child in block:
        tag = _strip_ns(child.tag)
        if tag == "statement" and child.attrib.get("name") == name:
            return child
    return None


def _field(block, name: str) -> Optional[str]:
    """Read text from <field name='...'> (returns None if absent)."""
    for child in block:
        tag = _strip_ns(child.tag)
        if tag == "field" and child.attrib.get("name") == name:
            return (child.text or "").strip()
    return None


def _value_element(block, name: str) -> Optional[Any]:
    """Find <value name='...'> and return its inner <block>."""
    for child in block:
        tag = _strip_ns(child.tag)
        if tag == "value" and child.attrib.get("name") == name:
            return _first_block(child)
    return None


def _value_str(block, name: str, default: str = "0") -> str:
    """Resolve a <value> to a string literal or variable reference."""
    inner = _value_element(block, name)
    if inner is None:
        return default
    return _resolve_value_block(inner, default)


def _resolve_value_block(block, default: str = "0") -> str:
    """Recursively resolve a value block to a string."""
    if block is None:
        return default
    btype = block.attrib.get("type", "")

    if btype in ("math_integer", "math_number"):
        return _field(block, "NUM") or default

    if btype == "variables_get":
        return _field(block, "VAR") or default

    if btype == "math_arithmetic":
        op_map = {"ADD": "+", "MINUS": "-", "MULTIPLY": "*",
                   "DIVIDE": "/", "MODULO": "%"}
        op = op_map.get(_field(block, "OP") or "", "+")
        a = _value_str(block, "A", "0")
        b = _value_str(block, "B", "0")
        return f"({a} {op} {b})"

    if btype == "math_negate":
        val = _value_str(block, "NUM", "0")
        return f"-({val})"

    if btype == "robSensors_timer_getSample":
        return "timer.value[0]"

    # Unresolved → return default with a note
    return default


def _field_or_value_float(block, name: str, default: float) -> float:
    """Get a numeric parameter that may be a <field> or a <value>."""
    # Try <field> first (used by mbedActions_play_note)
    f = _field(block, name)
    if f is not None:
        try:
            return float(f)
        except (ValueError, TypeError):
            pass
    # Try <value> (used by mbedActions_play_tone)
    v = _value_str(block, name, str(default))
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _extract_color(block) -> Tuple[int, int, int]:
    """Extract RGB from a Roberta colour block, scaled to Thymio 0-32 range."""
    color_block = _value_element(block, "COLOR")
    if color_block is None:
        return (0, 0, 0)

    btype = color_block.attrib.get("type", "")

    # robColour_picker stores hex string in COLOUR field
    if btype == "robColour_picker":
        hex_str = _field(color_block, "COLOUR") or "#000000"
        hex_str = hex_str.lstrip("#")
        try:
            r255 = int(hex_str[0:2], 16)
            g255 = int(hex_str[2:4], 16)
            b255 = int(hex_str[4:6], 16)
        except (ValueError, IndexError):
            return (0, 0, 0)
        return (_scale_color(r255), _scale_color(g255), _scale_color(b255))

    # robColour_rgb uses RED, GREEN, BLUE value sub-blocks
    if btype == "robColour_rgb":
        r = int(float(_value_str(color_block, "RED", "0")))
        g = int(float(_value_str(color_block, "GREEN", "0")))
        b = int(float(_value_str(color_block, "BLUE", "0")))
        return (_scale_color(r), _scale_color(g), _scale_color(b))

    return (0, 0, 0)


def _scale_color(val_255: int) -> int:
    """Scale 0-255 RGB to Thymio's 0-32 LED range."""
    return max(0, min(32, val_255 * 32 // 255))


# ============================================================================
# I/O helpers
# ============================================================================

def _write_json(path: Path, data: Dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
