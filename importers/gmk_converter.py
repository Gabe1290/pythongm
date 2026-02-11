#!/usr/bin/env python3
"""
Converts parsed GMK data into a pygm2 project directory.

Takes a GmkProject (from gmk_parser) and writes a complete pygm2
project including project.json, sprite PNGs, sound files, object JSONs,
room JSONs, etc.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image

from importers.gmk_mappings import (
    GM_ACTION_MAP,
    GM_ACTION_PARAMS,
    ARG_KIND_TO_RESOURCE,
    gm_color_to_hex,
    resolve_event,
)
from importers.gmk_parser import (
    GmkProject,
    GmkSprite,
    GmkSound,
    GmkBackground,
    GmkScript,
    GmkFont,
    GmkObject,
    GmkRoom,
    GmkAction,
    GmkEvent,
)

logger = logging.getLogger(__name__)


class GmkConverter:
    """
    Converts a parsed GmkProject to pygm2 project format.

    Creates the full directory structure and writes all files.
    """

    # Subdirectories to create in the project
    ASSET_DIRS = [
        "sprites", "sounds", "backgrounds", "objects",
        "rooms", "scripts", "fonts", "data", "thumbnails",
    ]

    def __init__(self, gmk_project: GmkProject, output_dir: Path):
        self.gmk = gmk_project
        self.output_dir = Path(output_dir)
        self._warnings: List[str] = []

        # Name lookup: resource_type -> list of names indexed by resource ID
        self.resource_names: Dict[str, List[Optional[str]]] = {}
        self._build_resource_name_index()

    @property
    def warnings(self):
        return list(self._warnings)

    def _warn(self, msg: str):
        logger.warning(msg)
        self._warnings.append(msg)

    def _build_resource_name_index(self):
        """Build lookup tables from resource ID (array index) to name."""
        self.resource_names["sprites"] = [
            s.name if s else None for s in self.gmk.sprites
        ]
        self.resource_names["sounds"] = [
            s.name if s else None for s in self.gmk.sounds
        ]
        self.resource_names["backgrounds"] = [
            b.name if b else None for b in self.gmk.backgrounds
        ]
        self.resource_names["paths"] = [
            p.name if p else None for p in self.gmk.paths
        ]
        self.resource_names["scripts"] = [
            s.name if s else None for s in self.gmk.scripts
        ]
        self.resource_names["fonts"] = [
            f.name if f else None for f in self.gmk.fonts
        ]
        self.resource_names["timelines"] = [
            t.name if t else None for t in self.gmk.timelines
        ]
        self.resource_names["objects"] = [
            o.name if o else None for o in self.gmk.objects
        ]
        self.resource_names["rooms"] = [
            r.name if r else None for r in self.gmk.rooms
        ]

    def _resolve_name(self, resource_type: str, index: int) -> str:
        """Resolve a resource ID to its name. Returns '' for invalid refs."""
        names = self.resource_names.get(resource_type, [])
        if index < 0:
            return ""
        if 0 <= index < len(names) and names[index] is not None:
            return names[index]
        return ""

    # ================================================================
    # Main conversion
    # ================================================================

    def convert(self) -> dict:
        """
        Convert the GMK project and write all files to output_dir.

        Returns:
            dict: The project.json data structure
        """
        self._create_directory_structure()

        now = datetime.now().isoformat()

        project_data = {
            "name": self.output_dir.name,
            "version": "1.0.0",
            "created": now,
            "modified": now,
            "settings": self._convert_settings(),
            "assets": {
                "sprites": self._convert_sprites(),
                "sounds": self._convert_sounds(),
                "backgrounds": self._convert_backgrounds(),
                "objects": self._convert_objects(),
                "rooms": self._convert_rooms(),
                "scripts": self._convert_scripts(),
                "fonts": self._convert_fonts(),
                "data": {},
            },
        }

        return project_data

    def _create_directory_structure(self):
        """Create the project directory and all asset subdirectories."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for subdir in self.ASSET_DIRS:
            (self.output_dir / subdir).mkdir(exist_ok=True)

    # ================================================================
    # Settings
    # ================================================================

    def _convert_settings(self) -> dict:
        gs = self.gmk.settings
        # Determine window size from first room if available
        width = gs.game_width if gs else 640
        height = gs.game_height if gs else 480
        room_speed = gs.game_speed if gs else 30

        # Try to get dimensions from first room
        for room in self.gmk.rooms:
            if room is not None:
                width = room.width
                height = room.height
                room_speed = room.speed
                break

        return {
            "window_title": gs.caption if gs else self.output_dir.name,
            "window_width": width,
            "window_height": height,
            "room_speed": room_speed,
            "fullscreen": gs.fullscreen if gs else False,
            "starting_lives": 3,
            "show_lives_in_caption": False,
            "starting_score": 0,
            "show_score_in_caption": False,
            "starting_health": 100,
            "show_health_in_caption": False,
        }

    # ================================================================
    # Sprites
    # ================================================================

    def _convert_sprites(self) -> dict:
        sprites = {}
        now = datetime.now().isoformat()

        for gmk_spr in self.gmk.sprites:
            if gmk_spr is None or not gmk_spr.subimages:
                continue

            try:
                spr_data = self._convert_single_sprite(gmk_spr, now)
                if spr_data:
                    sprites[gmk_spr.name] = spr_data
            except Exception as e:
                self._warn(f"Failed to convert sprite '{gmk_spr.name}': {e}")

        return sprites

    def _convert_single_sprite(self, gmk_spr: GmkSprite, now: str) -> dict:
        """Convert a single sprite: BGRA data → PNG file(s)."""
        name = gmk_spr.name
        num_frames = len(gmk_spr.subimages)

        if num_frames == 1:
            # Single frame: save as one PNG
            w, h, bgra = gmk_spr.subimages[0]
            file_name = f"{name}.png"
            self._bgra_to_png(bgra, w, h, self.output_dir / "sprites" / file_name)

            return {
                "name": name,
                "asset_type": "sprite",
                "file_path": f"sprites/{file_name}",
                "width": w,
                "height": h,
                "origin_x": gmk_spr.origin_x,
                "origin_y": gmk_spr.origin_y,
                "frames": 1,
                "frame_width": w,
                "frame_height": h,
                "animation_type": "single",
                "speed": 10.0,
                "imported": True,
                "created": now,
                "modified": now,
            }
        else:
            # Multiple frames: save as horizontal strip
            frame_w, frame_h = gmk_spr.subimages[0][0], gmk_spr.subimages[0][1]
            strip_width = frame_w * num_frames
            strip_img = Image.new("RGBA", (strip_width, frame_h), (0, 0, 0, 0))

            for i, (w, h, bgra) in enumerate(gmk_spr.subimages):
                frame_img = self._bgra_to_image(bgra, w, h)
                strip_img.paste(frame_img, (i * frame_w, 0))

            file_name = f"{name}.png"
            strip_img.save(self.output_dir / "sprites" / file_name, "PNG")

            return {
                "name": name,
                "asset_type": "sprite",
                "file_path": f"sprites/{file_name}",
                "width": strip_width,
                "height": frame_h,
                "origin_x": gmk_spr.origin_x,
                "origin_y": gmk_spr.origin_y,
                "frames": num_frames,
                "frame_width": frame_w,
                "frame_height": frame_h,
                "animation_type": "strip_h",
                "speed": 10.0,
                "imported": True,
                "created": now,
                "modified": now,
            }

    # ================================================================
    # Sounds
    # ================================================================

    def _convert_sounds(self) -> dict:
        sounds = {}
        now = datetime.now().isoformat()

        for gmk_snd in self.gmk.sounds:
            if gmk_snd is None:
                continue

            try:
                snd_data = self._convert_single_sound(gmk_snd, now)
                if snd_data:
                    sounds[gmk_snd.name] = snd_data
            except Exception as e:
                self._warn(f"Failed to convert sound '{gmk_snd.name}': {e}")

        return sounds

    def _convert_single_sound(self, gmk_snd: GmkSound, now: str) -> Optional[dict]:
        """Convert a single sound: write audio data to file."""
        if gmk_snd.data is None:
            return None

        name = gmk_snd.name
        # Determine file extension from file_type or file_name
        ext = gmk_snd.file_type.lstrip(".")
        if not ext and gmk_snd.file_name:
            ext = Path(gmk_snd.file_name).suffix.lstrip(".")
        if not ext:
            ext = "wav"  # default

        file_name = f"{name}.{ext}"
        out_path = self.output_dir / "sounds" / file_name

        # Sound data may be zlib-compressed (GM7/v701 stores it that way)
        data = gmk_snd.data
        if len(data) >= 2 and data[0] == 0x78 and data[1] in (0x01, 0x5E, 0x9C, 0xDA):
            import zlib
            try:
                data = zlib.decompress(data)
            except zlib.error:
                pass  # not actually zlib, write as-is

        out_path.write_bytes(data)

        return {
            "name": name,
            "asset_type": "sound",
            "file_path": f"sounds/{file_name}",
            "volume": min(1.0, max(0.0, gmk_snd.volume)),
            "loop": False,
            "imported": True,
            "created": now,
            "modified": now,
        }

    # ================================================================
    # Backgrounds
    # ================================================================

    def _convert_backgrounds(self) -> dict:
        backgrounds = {}
        now = datetime.now().isoformat()

        for gmk_bg in self.gmk.backgrounds:
            if gmk_bg is None or gmk_bg.data is None:
                continue

            try:
                name = gmk_bg.name
                file_name = f"{name}.png"
                self._bgra_to_png(
                    gmk_bg.data, gmk_bg.width, gmk_bg.height,
                    self.output_dir / "backgrounds" / file_name,
                )
                backgrounds[name] = {
                    "name": name,
                    "asset_type": "background",
                    "file_path": f"backgrounds/{file_name}",
                    "width": gmk_bg.width,
                    "height": gmk_bg.height,
                    "tile_horizontal": False,
                    "tile_vertical": False,
                    "imported": True,
                    "created": now,
                    "modified": now,
                }
            except Exception as e:
                self._warn(f"Failed to convert background '{gmk_bg.name}': {e}")

        return backgrounds

    # ================================================================
    # Scripts
    # ================================================================

    def _convert_scripts(self) -> dict:
        scripts = {}
        now = datetime.now().isoformat()

        for gmk_scr in self.gmk.scripts:
            if gmk_scr is None:
                continue

            python_code = _gml_to_python(gmk_scr.code)
            scripts[gmk_scr.name] = {
                "name": gmk_scr.name,
                "asset_type": "script",
                "code": python_code,
                "language": "python",
                "imported": True,
                "created": now,
                "modified": now,
            }

        return scripts

    # ================================================================
    # Fonts
    # ================================================================

    def _convert_fonts(self) -> dict:
        fonts = {}
        now = datetime.now().isoformat()

        for gmk_font in self.gmk.fonts:
            if gmk_font is None:
                continue

            fonts[gmk_font.name] = {
                "name": gmk_font.name,
                "asset_type": "font",
                "font_name": gmk_font.font_name,
                "size": gmk_font.size,
                "bold": gmk_font.bold,
                "italic": gmk_font.italic,
                "charset": "ascii",
                "imported": True,
                "created": now,
                "modified": now,
            }

        return fonts

    # ================================================================
    # Objects
    # ================================================================

    def _convert_objects(self) -> dict:
        objects = {}
        now = datetime.now().isoformat()

        for gmk_obj in self.gmk.objects:
            if gmk_obj is None:
                continue

            try:
                obj_data = self._convert_single_object(gmk_obj, now)
                if obj_data:
                    objects[gmk_obj.name] = obj_data
                    # Write external object file
                    self._write_object_file(gmk_obj.name, obj_data)
            except Exception as e:
                self._warn(f"Failed to convert object '{gmk_obj.name}': {e}")

        return objects

    def _convert_single_object(self, gmk_obj: GmkObject, now: str) -> dict:
        """Convert a single object with its events and actions."""
        sprite_name = self._resolve_name("sprites", gmk_obj.sprite_id)
        parent_name = self._resolve_name("objects", gmk_obj.parent_id)

        # Convert events
        events = self._convert_events(gmk_obj.events)

        obj_data = {
            "name": gmk_obj.name,
            "asset_type": "object",
            "sprite": sprite_name,
            "visible": gmk_obj.visible,
            "solid": gmk_obj.solid,
            "persistent": gmk_obj.persistent,
            "depth": gmk_obj.depth,
            "events": events,
            "imported": True,
            "created": now,
            "modified": now,
        }

        if parent_name:
            obj_data["parent"] = parent_name

        return obj_data

    def _convert_events(self, gm_events: List[GmkEvent]) -> dict:
        """
        Convert a list of GM events to pygm2 event structure.

        Handles merging keyboard events into nested structures.
        """
        events = {}
        object_names = self.resource_names.get("objects", [])

        for gm_event in gm_events:
            event_key, sub_key, extra = resolve_event(
                gm_event.event_type,
                gm_event.event_number,
                object_names,
            )

            actions = self._convert_actions(gm_event.actions)
            event_data = {"actions": actions}
            event_data.update(extra)

            if sub_key is not None:
                # Nested event (keyboard): merge into parent dict
                if event_key not in events:
                    events[event_key] = {}
                events[event_key][sub_key] = event_data
            else:
                events[event_key] = event_data

        return events

    def _convert_actions(self, gm_actions: List[GmkAction]) -> List[dict]:
        """Convert a list of GM actions to pygm2 action dicts."""
        actions = []
        for gm_act in gm_actions:
            converted = self._convert_single_action(gm_act)
            if converted:
                actions.append(converted)
        return actions

    def _convert_single_action(self, gm_act: GmkAction) -> Optional[dict]:
        """
        Convert a single GM action to a pygm2 action dict.

        Falls back to execute_code for unmapped actions with code,
        or comment for unmapped actions without code.
        """
        key = (gm_act.library_id, gm_act.action_id)

        # Special case: code execution (type 2) always becomes execute_code
        if gm_act.execution_type == 2:
            code = gm_act.code or ""
            if not code and gm_act.argument_values:
                code = gm_act.argument_values[0]
            return {
                "action": "execute_code",
                "parameters": {"code": code},
            }

        # Look up the action in the mapping
        pygm2_action = GM_ACTION_MAP.get(key)
        if pygm2_action is None:
            # Unmapped action: fall back
            return self._fallback_action(gm_act)

        # Build parameters dict from argument values
        param_names = GM_ACTION_PARAMS.get(key, [])
        parameters = {}

        for i, param_name in enumerate(param_names):
            if i < len(gm_act.argument_values):
                raw_value = gm_act.argument_values[i]

                # Resolve resource references
                if i < len(gm_act.argument_types):
                    arg_type = gm_act.argument_types[i]
                    resource_type = ARG_KIND_TO_RESOURCE.get(arg_type)
                    if resource_type:
                        resolved = self._resolve_resource_arg(raw_value, resource_type)
                        if resolved:
                            raw_value = resolved

                parameters[param_name] = raw_value

        # Convert binary direction strings to named directions
        if pygm2_action == "start_moving_direction" and "directions" in parameters:
            parameters["directions"] = _convert_direction_string(
                parameters["directions"]
            )

        # Handle the 'relative' flag for applicable actions
        if gm_act.is_relative and parameters:
            parameters["relative"] = True

        # Handle the 'not' flag for question actions
        if gm_act.is_not:
            parameters["not_flag"] = True

        return {
            "action": pygm2_action,
            "parameters": parameters,
        }

    def _resolve_resource_arg(self, value: str, resource_type: str) -> Optional[str]:
        """
        Resolve a resource reference argument.

        GM actions store resource references as string representations of
        integer IDs. Try to parse and resolve to the resource name.
        """
        try:
            index = int(value)
            return self._resolve_name(resource_type, index)
        except (ValueError, TypeError):
            return None  # not an integer, leave as-is

    def _fallback_action(self, gm_act: GmkAction) -> dict:
        """Create a fallback action for unmapped GM actions."""
        # If there's code, use execute_code
        if gm_act.code:
            return {
                "action": "execute_code",
                "parameters": {"code": gm_act.code},
            }
        # If there are arguments that look like code
        if gm_act.argument_values:
            for val in gm_act.argument_values:
                if val and len(val) > 10 and any(c in val for c in "{}();="):
                    return {
                        "action": "execute_code",
                        "parameters": {"code": val},
                    }

        # Otherwise emit a comment
        desc = (f"Unmapped GM action: lib={gm_act.library_id}, "
                f"id={gm_act.action_id}, kind={gm_act.action_kind}")
        if gm_act.function_name:
            desc += f", func={gm_act.function_name}"
        return {
            "action": "comment",
            "parameters": {"text": desc},
        }

    def _write_object_file(self, name: str, obj_data: dict):
        """Write object data to objects/<name>.json."""
        path = self.output_dir / "objects" / f"{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj_data, f, indent=2, ensure_ascii=False)

    # ================================================================
    # Rooms
    # ================================================================

    def _convert_rooms(self) -> dict:
        rooms = {}
        now = datetime.now().isoformat()

        # Use room_order if available, otherwise use natural order
        room_indices = self.gmk.room_order if self.gmk.room_order else range(len(self.gmk.rooms))

        for idx in room_indices:
            if idx < 0 or idx >= len(self.gmk.rooms):
                continue
            gmk_room = self.gmk.rooms[idx]
            if gmk_room is None:
                continue

            try:
                room_data = self._convert_single_room(gmk_room, now)
                if room_data:
                    rooms[gmk_room.name] = room_data
            except Exception as e:
                self._warn(f"Failed to convert room '{gmk_room.name}': {e}")

        return rooms

    def _convert_single_room(self, gmk_room: GmkRoom, now: str) -> dict:
        """Convert a single room and write the room file."""
        name = gmk_room.name
        bg_color = gm_color_to_hex(gmk_room.background_color)

        # Resolve background image (first visible non-foreground bg)
        bg_image = ""
        for bg in gmk_room.backgrounds:
            if bg.visible and not bg.foreground and bg.background_id >= 0:
                bg_image = self._resolve_name("backgrounds", bg.background_id)
                break

        # Convert instances
        instances = []
        for inst in gmk_room.instances:
            obj_name = self._resolve_name("objects", inst.object_id)
            if not obj_name:
                self._warn(f"Room '{name}': instance with unknown object ID {inst.object_id}")
                continue
            inst_data = {
                "object": obj_name,
                "x": inst.x,
                "y": inst.y,
            }
            if inst.creation_code:
                inst_data["creation_code"] = inst.creation_code
            instances.append(inst_data)

        # Write external room file
        room_file_data = {
            "name": name,
            "asset_type": "room",
            "width": gmk_room.width,
            "height": gmk_room.height,
            "background_color": bg_color,
            "background_image": bg_image,
            "tile_horizontal": False,
            "tile_vertical": False,
            "instances": instances,
            "creation_code": gmk_room.creation_code or "",
            "enable_views": gmk_room.enable_views,
            "created": now,
            "modified": now,
            "imported": True,
        }
        room_path = self.output_dir / "rooms" / f"{name}.json"
        with open(room_path, "w", encoding="utf-8") as f:
            json.dump(room_file_data, f, indent=2, ensure_ascii=False)

        # Return project.json entry (metadata + external reference)
        return {
            "name": name,
            "asset_type": "room",
            "width": gmk_room.width,
            "height": gmk_room.height,
            "background_color": bg_color,
            "background_image": bg_image,
            "tile_horizontal": False,
            "tile_vertical": False,
            "instance_count": len(instances),
            "instances": [],
            "_external_file": f"rooms/{name}.json",
            "created": now,
            "modified": now,
            "imported": True,
        }

    # ================================================================
    # Image conversion helpers
    # ================================================================

    def _bgra_to_image(self, bgra_data: bytes, width: int, height: int) -> Image.Image:
        """Convert BGRA pixel data to a PIL RGBA Image."""
        expected = width * height * 4
        if len(bgra_data) < expected:
            # Pad with transparent pixels if data is short
            bgra_data = bgra_data + b"\x00" * (expected - len(bgra_data))

        # Swap B and R channels: BGRA → RGBA
        rgba = bytearray(bgra_data[:expected])
        for i in range(0, len(rgba), 4):
            rgba[i], rgba[i + 2] = rgba[i + 2], rgba[i]

        return Image.frombytes("RGBA", (width, height), bytes(rgba))

    def _bgra_to_png(self, bgra_data: bytes, width: int, height: int, output_path: Path):
        """Convert BGRA pixel data to a PNG file."""
        img = self._bgra_to_image(bgra_data, width, height)
        img.save(output_path, "PNG")


# ============================================================================
# Direction string conversion
# ============================================================================

# GM stores directions as a 9-character binary string where each position
# maps to a direction: 0=down-left, 1=down, 2=down-right, 3=left, 4=stop,
# 5=right, 6=up-left, 7=up, 8=up-right.  A '1' means that direction is
# selected; multiple '1's mean "pick randomly from these".

_GM_DIR_POSITIONS = [
    "down-left", "down", "down-right",
    "left", "stop", "right",
    "up-left", "up", "up-right",
]


def _convert_direction_string(value):
    """Convert a GM 9-char binary direction string to pygm2 direction name(s).

    Returns a single name like ``"up"`` when one direction is set, or a
    list like ``["up", "down"]`` for random choice (multiple directions).
    Non-binary values are returned unchanged.
    """
    if not isinstance(value, str) or len(value) != 9 or not set(value) <= {"0", "1"}:
        return value  # not a binary direction string

    names = [_GM_DIR_POSITIONS[i] for i, ch in enumerate(value) if ch == "1"]
    if not names:
        return "stop"
    if len(names) == 1:
        return names[0]
    return names


# ============================================================================
# GML-to-Python transpiler (basic)
# ============================================================================

import re as _re


def _gml_to_python(gml_code: str) -> str:
    """
    Transpile simple GML (GameMaker Language) code to Python.

    Handles: // comments, braces→indentation, if/else, &&/||,
    place_free(), random(), semicolons, common GML instance vars.
    """
    # Flatten to a list of tokens/statements by removing braces and splitting on semicolons
    # Step 1: strip outer script braces if present
    # The outer { } may be preceded by comments
    code = gml_code.strip()
    code_lines = code.split("\n")
    # Find first non-comment, non-blank line
    first_code = -1
    for li, ln in enumerate(code_lines):
        s = ln.strip()
        if s and not s.startswith("//"):
            first_code = li
            break
    # If the first code line is just "{" and last non-blank is "}", strip them
    if first_code >= 0 and code_lines[first_code].strip() == "{":
        last_code = -1
        for li in range(len(code_lines) - 1, -1, -1):
            if code_lines[li].strip():
                last_code = li
                break
        if last_code > first_code and code_lines[last_code].strip() == "}":
            code_lines[first_code] = ""
            code_lines[last_code] = ""
            code = "\n".join(code_lines)

    # Step 2: Convert to statements list preserving structure
    lines = code.split("\n")
    result = []
    indent = 0
    pending_if = False  # True when we just emitted an if/elif/else and need body

    i = 0
    while i < len(lines):
        raw = lines[i].rstrip()
        i += 1
        stripped = raw.strip()

        if not stripped:
            if not pending_if:
                result.append("")
            continue

        # Convert // comments to #
        stripped = _re.sub(r"//(.*)$", r"#\1", stripped)

        if stripped.startswith("#"):
            result.append("    " * indent + stripped)
            continue

        # Handle standalone opening brace
        if stripped == "{":
            indent += 1
            continue

        # Handle standalone closing brace
        if stripped == "}":
            indent = max(0, indent - 1)
            pending_if = False
            continue

        # Handle inline block: { stmt1; stmt2; }
        m = _re.match(r"^\{\s*(.+?)\s*;?\s*\}$", stripped)
        if m:
            stmts = m.group(1).split(";")
            for s in stmts:
                s = s.strip()
                if s:
                    result.append("    " * indent + _convert_gml_expr(s))
            pending_if = False
            continue

        # Convert the line's GML expressions
        stripped = _convert_gml_expr(stripped)

        # Handle if (cond)
        m = _re.match(r"if\s*\((.+)\)\s*\{?\s*$", stripped)
        if m:
            cond = m.group(1).rstrip(" {")
            result.append("    " * indent + f"if {cond}:")
            indent += 1
            pending_if = True
            if not stripped.endswith("{"):
                # Next line(s) form the body - look ahead
                i, indent = _consume_if_body(lines, i, indent, result)
                pending_if = False
            continue

        m = _re.match(r"else\s+if\s*\((.+)\)\s*\{?\s*$", stripped)
        if m:
            cond = m.group(1).rstrip(" {")
            result.append("    " * indent + f"elif {cond}:")
            indent += 1
            pending_if = True
            if not stripped.endswith("{"):
                i, indent = _consume_if_body(lines, i, indent, result)
                pending_if = False
            continue

        m = _re.match(r"else\s*\{?\s*$", stripped)
        if m:
            result.append("    " * indent + "else:")
            indent += 1
            pending_if = True
            if not stripped.endswith("{"):
                i, indent = _consume_if_body(lines, i, indent, result)
                pending_if = False
            continue

        # Remove trailing semicolons
        if stripped.endswith(";"):
            stripped = stripped[:-1].rstrip()

        if stripped:
            result.append("    " * indent + stripped)
            pending_if = False

    # Remove leading/trailing blank lines
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()

    return "\n".join(result)


# GML instance variables that need instance. prefix
_GML_INSTANCE_VARS = {
    "hspeed", "vspeed", "speed", "direction", "x", "y",
    "image_index", "image_speed", "sprite_index", "image_angle",
    "image_xscale", "image_yscale", "image_alpha", "image_blend",
    "visible", "solid", "depth", "persistent", "object_index",
    "alarm", "friction", "gravity", "gravity_direction",
    "bbox_left", "bbox_right", "bbox_top", "bbox_bottom",
    "xstart", "ystart", "xprevious", "yprevious",
}


def _convert_gml_expr(line: str) -> str:
    """Convert GML operators and functions in a single line."""
    # Operators
    line = line.replace("&&", " and ")
    line = line.replace("||", " or ")

    # place_free(x, y) → not game.check_collision_at_position(...)
    line = _re.sub(
        r"place_free\(([^,]+),\s*([^)]+)\)",
        r'not game.check_collision_at_position(instance, \1, \2, "solid")',
        line,
    )
    # Remove double negation from !place_free
    line = _re.sub(
        r"not\s+not\s+game\.check_collision_at_position",
        r"game.check_collision_at_position",
        line,
    )

    # random(n) → random.random() * n
    line = _re.sub(r"\brandom\(([^)]+)\)", r"random.random() * \1", line)

    # Instance variable prefixing — skip content inside string literals
    for var in _GML_INSTANCE_VARS:
        # Split line into string-literal and non-literal segments
        # so we only prefix vars outside of quotes
        parts = _re.split(r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', line)
        for pi in range(0, len(parts), 2):  # even indices = outside strings
            parts[pi] = _re.sub(
                rf"(?<![.\w])\b{_re.escape(var)}\b(?![.\w(])",
                f"instance.{var}",
                parts[pi],
            )
        line = "".join(parts)

    # Fix double-prefixed (instance.instance.x)
    line = line.replace("instance.instance.", "instance.")

    # Clean up multiple spaces
    line = _re.sub(r"  +", " ", line)

    return line


def _consume_if_body(lines, i, indent, result):
    """
    After an if/elif/else without '{', consume the next statement as body.
    The body might be an inline block { stmt; stmt; } on the next line.
    """
    # Skip blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1

    if i >= len(lines):
        return i, indent

    next_line = lines[i].strip()

    # Standalone opening brace → the brace block becomes the body
    if next_line == "{":
        i += 1
        # indent is already incremented by caller
        return i, indent

    # Inline block: { stmt1; stmt2; }
    m = _re.match(r"^\{\s*(.+?)\s*;?\s*\}$", next_line)
    if m:
        stmts = m.group(1).split(";")
        for s in stmts:
            s = s.strip()
            if s:
                result.append("    " * indent + _convert_gml_expr(s))
        i += 1
        indent -= 1  # body consumed, dedent
        return i, indent

    # Single statement body
    stmt = _convert_gml_expr(next_line.rstrip(";").strip())
    if stmt:
        result.append("    " * indent + stmt)
    i += 1
    indent -= 1  # body consumed, dedent
    return i, indent
