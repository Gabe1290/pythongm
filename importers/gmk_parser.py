#!/usr/bin/env python3
"""
GameMaker .gmk binary file parser.

Parses .gmk files (versions 530, 600, 701, 800, 810) into intermediate
Python dataclasses.  Does NOT convert to pygm2 format -- that is handled
by gmk_converter.py.
"""

import logging
import struct
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from importers.gmk_reader import GmkStream, GmkReadError

logger = logging.getLogger(__name__)

GMK_MAGIC = 1234321
SUPPORTED_VERSIONS = (530, 600, 700, 701, 800, 810)


# ============================================================================
# DATACLASSES for parsed resources
# ============================================================================

@dataclass
class GmkHeader:
    magic: int
    version: int
    game_id: int
    guid: bytes


@dataclass
class GmkSprite:
    name: str
    origin_x: int = 0
    origin_y: int = 0
    subimages: List[Tuple[int, int, bytes]] = field(default_factory=list)
    # Each subimage is (width, height, bgra_pixel_data)


@dataclass
class GmkSound:
    name: str
    kind: int = 0
    file_type: str = ""
    file_name: str = ""
    data: Optional[bytes] = None
    effects: int = 0
    volume: float = 1.0
    pan: float = 0.0
    preload: bool = True


@dataclass
class GmkBackground:
    name: str
    width: int = 0
    height: int = 0
    transparent: bool = False
    smooth: bool = False
    preload: bool = True
    use_as_tileset: bool = False
    tile_width: int = 16
    tile_height: int = 16
    h_offset: int = 0
    v_offset: int = 0
    h_sep: int = 0
    v_sep: int = 0
    data: Optional[bytes] = None  # BGRA pixel data


@dataclass
class GmkPath:
    name: str
    smooth: bool = False
    closed: bool = False
    precision: int = 4
    points: List[Tuple[float, float, float]] = field(default_factory=list)


@dataclass
class GmkScript:
    name: str
    code: str = ""


@dataclass
class GmkFont:
    name: str
    font_name: str = ""
    size: int = 12
    bold: bool = False
    italic: bool = False
    range_start: int = 32
    range_end: int = 127
    charset: int = 0
    aa_level: int = 0


@dataclass
class GmkAction:
    library_id: int = 0
    action_id: int = 0
    action_kind: int = 0
    has_relative: bool = False
    is_question: bool = False
    applies_to: int = -1
    execution_type: int = 0
    function_name: str = ""
    code: str = ""
    can_be_relative: bool = False
    is_relative: bool = False
    argument_count: int = 0
    argument_types: List[int] = field(default_factory=list)
    argument_values: List[str] = field(default_factory=list)
    is_not: bool = False


@dataclass
class GmkEvent:
    event_type: int
    event_number: int
    actions: List[GmkAction] = field(default_factory=list)


@dataclass
class GmkObject:
    name: str
    sprite_id: int = -1
    solid: bool = False
    visible: bool = True
    depth: int = 0
    persistent: bool = False
    parent_id: int = -1
    mask_id: int = -1
    events: List[GmkEvent] = field(default_factory=list)


@dataclass
class GmkRoomBackground:
    visible: bool = False
    foreground: bool = False
    background_id: int = -1
    x: int = 0
    y: int = 0
    tile_h: bool = True
    tile_v: bool = True
    hspeed: int = 0
    vspeed: int = 0
    stretch: bool = False


@dataclass
class GmkRoomView:
    visible: bool = False
    xview: int = 0
    yview: int = 0
    wview: int = 640
    hview: int = 480
    xport: int = 0
    yport: int = 0
    wport: int = 640
    hport: int = 480
    border_h: int = 32
    border_v: int = 32
    hspeed: int = -1
    vspeed: int = -1
    follow_object_id: int = -1


@dataclass
class GmkInstance:
    x: int = 0
    y: int = 0
    object_id: int = -1
    instance_id: int = 0
    creation_code: str = ""
    locked: bool = False


@dataclass
class GmkTile:
    x: int = 0
    y: int = 0
    background_id: int = -1
    tile_x: int = 0
    tile_y: int = 0
    width: int = 16
    height: int = 16
    depth: int = 1000000
    tile_id: int = 0
    locked: bool = False


@dataclass
class GmkRoom:
    name: str
    caption: str = ""
    width: int = 640
    height: int = 480
    snap_x: int = 16
    snap_y: int = 16
    isometric: bool = False
    speed: int = 30
    persistent: bool = False
    background_color: int = 0xC0C0C0
    draw_background_color: bool = True
    creation_code: str = ""
    backgrounds: List[GmkRoomBackground] = field(default_factory=list)
    enable_views: bool = False
    views: List[GmkRoomView] = field(default_factory=list)
    instances: List[GmkInstance] = field(default_factory=list)
    tiles: List[GmkTile] = field(default_factory=list)


@dataclass
class GmkTimeline:
    name: str
    moments: List[Tuple[int, List[GmkAction]]] = field(default_factory=list)


@dataclass
class GmkGameSettings:
    fullscreen: bool = False
    color_outside: int = 0
    game_width: int = 640
    game_height: int = 480
    game_speed: int = 30
    caption: str = ""


@dataclass
class GmkProject:
    header: GmkHeader = None
    settings: GmkGameSettings = None
    sprites: List[Optional[GmkSprite]] = field(default_factory=list)
    sounds: List[Optional[GmkSound]] = field(default_factory=list)
    backgrounds: List[Optional[GmkBackground]] = field(default_factory=list)
    paths: List[Optional[GmkPath]] = field(default_factory=list)
    scripts: List[Optional[GmkScript]] = field(default_factory=list)
    fonts: List[Optional[GmkFont]] = field(default_factory=list)
    timelines: List[Optional[GmkTimeline]] = field(default_factory=list)
    objects: List[Optional[GmkObject]] = field(default_factory=list)
    rooms: List[Optional[GmkRoom]] = field(default_factory=list)
    last_instance_id: int = 100000
    last_tile_id: int = 10000000
    room_order: List[int] = field(default_factory=list)


# ============================================================================
# BMP PARSING HELPER
# ============================================================================

def _bmp_to_bgra(bmp_data: bytes, transparent: bool = True) -> Tuple[int, int, bytes]:
    """
    Parse a BMP image and return (width, height, bgra_pixel_data).

    GM7 stores sprite subimages as zlib-compressed BMP data.
    The bottom-left pixel color is used as the transparency key.
    """
    if len(bmp_data) < 54 or bmp_data[0:2] != b"BM":
        raise ValueError("Not a valid BMP file")

    # BMP header
    data_offset = struct.unpack_from("<I", bmp_data, 10)[0]
    width = struct.unpack_from("<i", bmp_data, 18)[0]
    height = struct.unpack_from("<i", bmp_data, 22)[0]
    bpp = struct.unpack_from("<H", bmp_data, 28)[0]

    if bpp not in (24, 32):
        raise ValueError(f"Unsupported BMP bit depth: {bpp}")

    abs_height = abs(height)
    bottom_up = height > 0
    channels = bpp // 8
    # BMP scanlines are padded to 4-byte boundaries
    row_size = (width * channels + 3) & ~3

    # Read pixel data
    pixels = bmp_data[data_offset:]

    # Build BGRA output (top-down, no padding)
    bgra = bytearray(width * abs_height * 4)

    for row in range(abs_height):
        src_row = (abs_height - 1 - row) if bottom_up else row
        src_offset = src_row * row_size
        for col in range(width):
            src_pixel = src_offset + col * channels
            dst_pixel = (row * width + col) * 4
            if src_pixel + channels <= len(pixels):
                bgra[dst_pixel] = pixels[src_pixel]        # B
                bgra[dst_pixel + 1] = pixels[src_pixel + 1]  # G
                bgra[dst_pixel + 2] = pixels[src_pixel + 2]  # R
                if channels == 4:
                    bgra[dst_pixel + 3] = pixels[src_pixel + 3]  # A
                else:
                    bgra[dst_pixel + 3] = 255  # opaque

    # Apply transparency key: bottom-left pixel color
    if transparent and width > 0 and abs_height > 0:
        # Bottom-left pixel in our top-down output is at row (abs_height-1), col 0
        key_offset = ((abs_height - 1) * width) * 4
        key_b = bgra[key_offset]
        key_g = bgra[key_offset + 1]
        key_r = bgra[key_offset + 2]
        for i in range(0, len(bgra), 4):
            if (bgra[i] == key_b and bgra[i + 1] == key_g
                    and bgra[i + 2] == key_r):
                bgra[i + 3] = 0  # transparent

    return width, abs_height, bytes(bgra)


# ============================================================================
# PARSER
# ============================================================================

class GmkParseError(Exception):
    """Error while parsing a .gmk file."""
    pass


class GmkParser:
    """
    Parses a GameMaker .gmk binary file into a GmkProject structure.
    Supports versions 530, 600, 700, 701 (encrypted), 800, and 810.
    """

    def __init__(self):
        self.stream: Optional[GmkStream] = None
        self.file_version: int = 0
        self._warnings: List[str] = []

    @property
    def warnings(self):
        return list(self._warnings)

    def _warn(self, msg: str):
        logger.warning(msg)
        self._warnings.append(msg)

    def parse(self, file_path: str) -> GmkProject:
        path = Path(file_path)
        if not path.exists():
            raise GmkParseError(f"File not found: {path}")

        logger.info(f"Reading GMK file: {path} ({path.stat().st_size} bytes)")
        data = path.read_bytes()
        self.stream = GmkStream(data)
        self._warnings = []

        try:
            project = GmkProject()
            project.header = self._parse_header()
            self.file_version = project.header.version
            logger.info(f"GMK version {self.file_version}, "
                        f"game ID {project.header.game_id}")

            project.settings = self._parse_settings()

            # Triggers and constants only exist in v800+
            if self.file_version >= 800:
                self._skip_triggers()
                self._skip_constants()

            logger.info("Parsing sounds...")
            project.sounds = self._parse_resource_section(self._parse_single_sound)
            logger.info(f"  Found {sum(1 for s in project.sounds if s)} sounds")

            logger.info("Parsing sprites...")
            project.sprites = self._parse_resource_section(self._parse_single_sprite)
            logger.info(f"  Found {sum(1 for s in project.sprites if s)} sprites")

            logger.info("Parsing backgrounds...")
            project.backgrounds = self._parse_resource_section(self._parse_single_background)
            logger.info(f"  Found {sum(1 for b in project.backgrounds if b)} backgrounds")

            logger.info("Parsing paths...")
            project.paths = self._parse_resource_section(self._parse_single_path)
            logger.info(f"  Found {sum(1 for p in project.paths if p)} paths")

            logger.info("Parsing scripts...")
            project.scripts = self._parse_resource_section(self._parse_single_script)
            logger.info(f"  Found {sum(1 for s in project.scripts if s)} scripts")

            logger.info("Parsing fonts...")
            project.fonts = self._parse_resource_section(self._parse_single_font)
            logger.info(f"  Found {sum(1 for f in project.fonts if f)} fonts")

            logger.info("Parsing timelines...")
            project.timelines = self._parse_resource_section(self._parse_single_timeline)
            logger.info(f"  Found {sum(1 for t in project.timelines if t)} timelines")

            logger.info("Parsing objects...")
            project.objects = self._parse_resource_section(self._parse_single_object)
            logger.info(f"  Found {sum(1 for o in project.objects if o)} objects")

            logger.info("Parsing rooms...")
            project.rooms = self._parse_resource_section(self._parse_single_room)
            logger.info(f"  Found {sum(1 for r in project.rooms if r)} rooms")

            # Last instance/tile IDs
            project.last_instance_id = self.stream.read_int32()
            project.last_tile_id = self.stream.read_int32()

            # Skip includes, extensions, game information, library creation code
            self._skip_remaining_sections()

            # Room execution order
            try:
                ver = self.stream.read_int32()
                count = self.stream.read_int32()
                project.room_order = [self.stream.read_int32() for _ in range(count)]
            except GmkReadError:
                self._warn("Could not read room execution order")

            logger.info(f"Parse complete. {len(self._warnings)} warnings.")
            return project

        except GmkReadError as e:
            raise GmkParseError(f"Read error: {e}") from e
        except GmkParseError:
            raise
        except Exception as e:
            raise GmkParseError(
                f"Parse error at position 0x{self.stream.position:X}: {e}"
            ) from e

    # ----------------------------------------------------------------
    # Header
    # ----------------------------------------------------------------

    def _parse_header(self) -> GmkHeader:
        magic = self.stream.read_int32()
        if magic != GMK_MAGIC:
            raise GmkParseError(
                f"Invalid GMK magic number: {magic} (expected {GMK_MAGIC})"
            )
        version = self.stream.read_int32()
        if version not in SUPPORTED_VERSIONS:
            raise GmkParseError(
                f"Unsupported GMK version: {version} "
                f"(expected one of {SUPPORTED_VERSIONS})"
            )

        if version == 701:
            # v701 encrypted header: read seed, skip garbage, decrypt game_id
            return self._parse_header_v701(magic, version)
        else:
            game_id = self.stream.read_int32()
            guid = b"\x00" * 16
            if version >= 600:
                guid = self.stream.read_bytes(16)
            return GmkHeader(magic=magic, version=version,
                             game_id=game_id, guid=guid)

    def _parse_header_v701(self, magic: int, version: int) -> GmkHeader:
        """Parse v701 encrypted header and enable stream decryption."""
        # Anti-decompiler: read two garbage counts, skip garbage, read seed
        s1 = self.stream.read_int32()
        s2 = self.stream.read_int32()
        self.stream.skip(s1 * 4)
        seed = self.stream.read_int32()
        self.stream.skip(s2 * 4)

        # Read first byte of game_id unencrypted
        b0 = self.stream.read_byte()

        # Enable decryption from here on
        self.stream.enable_decryption(seed)

        # Read remaining 3 bytes of game_id (now decrypted)
        b1 = self.stream.read_byte()
        b2 = self.stream.read_byte()
        b3 = self.stream.read_byte()
        game_id = b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)

        guid = self.stream.read_bytes(16)

        return GmkHeader(magic=magic, version=version,
                         game_id=game_id, guid=guid)

    # ----------------------------------------------------------------
    # Settings
    # ----------------------------------------------------------------

    def _parse_settings(self) -> GmkGameSettings:
        settings = GmkGameSettings()
        ver = self.stream.read_int32()

        if ver >= 800:
            # v800+: settings are in a zlib block
            sub = self.stream.read_zlib_stream()
        else:
            # v702 and earlier: settings are read directly from stream
            sub = self.stream

        try:
            settings.fullscreen = sub.read_bool()
            if ver >= 600:
                _interpolate = sub.read_bool()
            _no_border = sub.read_bool()
            _cursor = sub.read_bool()
            _scale = sub.read_int32()
            if ver >= 542:
                _resizable = sub.read_bool()
                _always_on_top = sub.read_bool()
                settings.color_outside = sub.read_int32()

            _set_resolution = sub.read_bool()
            if ver >= 542:
                _color_depth = sub.read_int32()
                _resolution = sub.read_int32()
                _frequency = sub.read_int32()

            _no_buttons = sub.read_bool()
            if ver > 530:
                _vsync = sub.read_int32()  # bitmask, not bool
            if ver >= 800:
                _no_screen_saver = sub.read_bool()

            _f4_fullscreen = sub.read_bool()
            _f1_help = sub.read_bool()
            _esc_end = sub.read_bool()
            _f5_save_f6_load = sub.read_bool()
            if ver > 600:
                _f9_screenshot = sub.read_bool()
                _close_button = sub.read_bool()

            _priority = sub.read_int32()
            _freeze_on_lose_focus = sub.read_bool()
            _loading_bar = sub.read_int32()

            if _loading_bar == 2:  # custom load bar
                if ver >= 800:
                    if sub.read_bool():
                        sub.read_zlib_data()
                    if sub.read_bool():
                        sub.read_zlib_data()
                else:
                    # pre-v800: check int32 != -1
                    if sub.read_int32() != -1:
                        sub.read_zlib_data()
                    if sub.read_int32() != -1:
                        sub.read_zlib_data()

            _show_custom_load = sub.read_bool()
            if _show_custom_load:
                if ver >= 800:
                    if sub.read_bool():
                        sub.read_zlib_data()
                else:
                    if sub.read_int32() != -1:
                        sub.read_zlib_data()

            _transparent = sub.read_bool()
            _translucency = sub.read_int32()
            _scale_progress = sub.read_bool()

            # Icon data
            icon_len = sub.read_int32()
            if icon_len > 0:
                sub.read_bytes(icon_len)

            # Error handling
            _display_errors = sub.read_bool()
            _log_errors = sub.read_bool()
            _abort_errors = sub.read_bool()
            _error_flags = sub.read_int32()

            # Author / metadata
            _author = sub.read_string()
            if ver > 600:
                _version_str = sub.read_string()
            else:
                _version_str = ""
            _last_changed = sub.read_double()
            _information = sub.read_string()

            # Constants (inside settings for pre-v800)
            if ver < 800:
                const_count = sub.read_int32()
                for _ in range(const_count):
                    _cname = sub.read_string()
                    _cvalue = sub.read_string()

            # Version info (v600+)
            if ver > 600:
                _ver_major = sub.read_int32()
                _ver_minor = sub.read_int32()
                _ver_release = sub.read_int32()
                _ver_build = sub.read_int32()
                _company = sub.read_string()
                _product = sub.read_string()
                _copyright = sub.read_string()
                _description = sub.read_string()

            # v800 has a last-changed timestamp at the end of the inflated block
            if ver >= 800:
                _timestamp = sub.read_double()

        except GmkReadError:
            self._warn("Settings block truncated, using defaults")

        return settings

    # ----------------------------------------------------------------
    # Triggers / Constants (v800+ only)
    # ----------------------------------------------------------------

    def _skip_triggers(self):
        ver = self.stream.read_int32()
        count = self.stream.read_int32()
        for _ in range(count):
            self.stream.read_zlib_data()
        self.stream.read_int32()  # timestamp

    def _skip_constants(self):
        ver = self.stream.read_int32()
        count = self.stream.read_int32()
        for _ in range(count):
            _name = self.stream.read_string()
            _value = self.stream.read_string()
        self.stream.read_int32()  # timestamp

    # ----------------------------------------------------------------
    # Generic resource section parser
    # ----------------------------------------------------------------

    def _parse_resource_section(self, parse_func) -> list:
        """
        Parse a resource section, handling both v800 (per-resource zlib)
        and v701/earlier (no per-resource zlib) formats.

        Read order per ENIGMA/LateralGM: exists → name → (timestamp) → subversion → data.
        """
        group_ver = self.stream.read_int32()
        count = self.stream.read_int32()
        resources = []

        for i in range(count):
            try:
                if group_ver >= 800:
                    sub = self.stream.read_zlib_stream()
                else:
                    sub = self.stream

                exists = sub.read_bool()
                if not exists:
                    resources.append(None)
                    continue

                name = sub.read_string()
                if group_ver == 800:
                    sub.skip(8)  # last-changed timestamp (v800 only)
                subver = sub.read_int32()

                resource = parse_func(sub, name, subver)
                resources.append(resource)
            except Exception as e:
                self._warn(f"Failed to parse resource #{i}: {e}")
                resources.append(None)

        return resources

    # ----------------------------------------------------------------
    # Individual resource parsers
    # ----------------------------------------------------------------

    def _parse_single_sprite(self, s: GmkStream, name: str, subver: int) -> Optional[GmkSprite]:
        sprite = GmkSprite(name=name)

        if subver < 800:
            # Pre-v800: width/height/bbox/transparency before origin
            spr_width = s.read_int32()
            spr_height = s.read_int32()
            _bbox_left = s.read_int32()
            _bbox_right = s.read_int32()
            _bbox_bottom = s.read_int32()
            _bbox_top = s.read_int32()
            _transparent = s.read_bool()
            if subver > 400:
                _smooth = s.read_bool()
                _preload = s.read_bool()
            else:
                s.skip(4)  # v400: skip(4) + inverted preload
                _preload = not s.read_bool()
            _bbox_mode = s.read_int32()
            _precise = s.read_bool()
            transparent = True  # used for BMP key color
        else:
            transparent = False

        sprite.origin_x = s.read_int32()
        sprite.origin_y = s.read_int32()
        subimage_count = s.read_int32()

        for _ in range(subimage_count):
            if subver >= 800:
                # v800+: raw BGRA pixel data
                img_ver = s.read_int32()
                width = s.read_int32()
                height = s.read_int32()
                if width > 0 and height > 0:
                    data_length = s.read_int32()
                    bgra_data = s.read_bytes(data_length)
                    sprite.subimages.append((width, height, bgra_data))
            else:
                # Pre-v800: sentinel check then zlib-compressed BMP data
                check = s.read_int32()
                if check == -1:
                    continue
                try:
                    bmp_data = s.read_zlib_data()
                    w, h, bgra = _bmp_to_bgra(bmp_data, transparent)
                    sprite.subimages.append((w, h, bgra))
                except Exception as e:
                    self._warn(f"Failed to parse BMP subimage for '{name}': {e}")

        if subver >= 800:
            # v800+: shape/alpha/separate_mask/bbox read after subimages
            _shape = s.read_int32()
            _alpha_tolerance = s.read_int32()
            _separate_mask = s.read_bool()
            _bbox_mode = s.read_int32()
            _bbox_left = s.read_int32()
            _bbox_right = s.read_int32()
            _bbox_bottom = s.read_int32()
            _bbox_top = s.read_int32()

        return sprite

    def _parse_single_sound(self, s: GmkStream, name: str, subver: int) -> Optional[GmkSound]:
        sound = GmkSound(name=name)

        sound.kind = s.read_int32()
        sound.file_type = s.read_string()

        if subver >= 600:
            sound.file_name = s.read_string()

        has_data = s.read_bool()
        if has_data:
            if subver >= 600:
                # v600+: length-prefixed raw data
                data_len = s.read_int32()
                sound.data = s.read_bytes(data_len)
            else:
                # v440: zlib-compressed data
                sound.data = s.read_zlib_data()

        sound.effects = s.read_int32()
        sound.volume = s.read_double()
        sound.pan = s.read_double()
        sound.preload = s.read_bool()

        return sound

    def _parse_single_background(self, s: GmkStream, name: str, subver: int) -> Optional[GmkBackground]:
        bg = GmkBackground(name=name)

        if subver < 710:
            # Pre-710: transparent/smooth/preload appear before tileset fields
            bg.transparent = s.read_bool()
            if subver > 400:
                bg.smooth = s.read_bool()
                bg.preload = s.read_bool()
            else:
                s.skip(4)  # v400: skip(4) + inverted preload
                bg.preload = not s.read_bool()

        if subver >= 543:
            bg.use_as_tileset = s.read_bool()
            bg.tile_width = s.read_int32()
            bg.tile_height = s.read_int32()
            bg.h_offset = s.read_int32()
            bg.v_offset = s.read_int32()
            bg.h_sep = s.read_int32()
            bg.v_sep = s.read_int32()

        if subver >= 710:
            # v710+: inner version + raw BGRA data (no transparent/width/height prefix)
            bg_inner_ver = s.read_int32()  # 800
            bg.width = s.read_int32()
            bg.height = s.read_int32()
            if bg.width > 0 and bg.height > 0:
                data_len = s.read_int32()
                bg.data = s.read_bytes(data_len)
        else:
            # Pre-710: dimensions + bool guard + sentinel + zlib BMP
            bg.width = s.read_int32()
            bg.height = s.read_int32()
            has_data = s.read_bool()
            if has_data:
                # Always read the data block when has_data is true,
                # even if dimensions are 0 (dimensions may come from BMP itself)
                check = s.read_int32()
                if check != -1:
                    try:
                        bmp_data = s.read_zlib_data()
                        w, h, bgra = _bmp_to_bgra(bmp_data, bg.transparent)
                        bg.width = w
                        bg.height = h
                        bg.data = bgra
                    except Exception as e:
                        self._warn(f"Failed to parse BMP for background '{name}': {e}")

        return bg

    def _parse_single_path(self, s: GmkStream, name: str, subver: int) -> Optional[GmkPath]:
        path = GmkPath(name=name)

        path.smooth = s.read_bool()
        path.closed = s.read_bool()
        path.precision = s.read_int32()
        _bg_room = s.read_int32()
        _snap_x = s.read_int32()
        _snap_y = s.read_int32()

        point_count = s.read_int32()
        for _ in range(point_count):
            x = s.read_double()
            y = s.read_double()
            speed = s.read_double()
            path.points.append((x, y, speed))

        return path

    def _parse_single_script(self, s: GmkStream, name: str, subver: int) -> Optional[GmkScript]:
        script = GmkScript(name=name)
        script.code = s.read_string()
        return script

    def _parse_single_font(self, s: GmkStream, name: str, subver: int) -> Optional[GmkFont]:
        font = GmkFont(name=name)

        font.font_name = s.read_string()
        font.size = s.read_int32()
        font.bold = s.read_bool()
        font.italic = s.read_bool()
        font.range_start = s.read_int32()
        font.range_end = s.read_int32()

        return font

    def _parse_single_timeline(self, s: GmkStream, name: str, subver: int) -> Optional[GmkTimeline]:
        timeline = GmkTimeline(name=name)

        moment_count = s.read_int32()
        for _ in range(moment_count):
            step = s.read_int32()
            actions = self._parse_actions(s)
            timeline.moments.append((step, actions))

        return timeline

    def _parse_single_object(self, s: GmkStream, name: str, subver: int) -> Optional[GmkObject]:
        obj = GmkObject(name=name)
        obj.sprite_id = s.read_int32()
        obj.solid = s.read_bool()
        obj.visible = s.read_bool()
        obj.depth = s.read_int32()
        obj.persistent = s.read_bool()
        obj.parent_id = s.read_int32()
        obj.mask_id = s.read_int32()

        num_event_types = s.read_int32() + 1

        for event_type in range(num_event_types):
            while True:
                event_number = s.read_int32()
                if event_number == -1:
                    break
                actions = self._parse_actions(s)
                event = GmkEvent(
                    event_type=event_type,
                    event_number=event_number,
                    actions=actions,
                )
                obj.events.append(event)

        return obj

    def _parse_single_room(self, s: GmkStream, name: str, subver: int) -> Optional[GmkRoom]:
        room = GmkRoom(name=name)

        room.caption = s.read_string()
        room.width = s.read_int32()
        room.height = s.read_int32()
        room.snap_y = s.read_int32()
        room.snap_x = s.read_int32()
        if subver > 520:
            room.isometric = s.read_bool()
        room.speed = s.read_int32()
        room.persistent = s.read_bool()
        room.background_color = s.read_int32()
        if subver > 520:
            room.draw_background_color = s.read_bool()
        room.creation_code = s.read_string()

        # Background definitions
        bg_count = s.read_int32()
        for _ in range(bg_count):
            bg = GmkRoomBackground()
            bg.visible = s.read_bool()
            bg.foreground = s.read_bool()
            bg.background_id = s.read_int32()
            bg.x = s.read_int32()
            bg.y = s.read_int32()
            bg.tile_h = s.read_bool()
            bg.tile_v = s.read_bool()
            bg.hspeed = s.read_int32()
            bg.vspeed = s.read_int32()
            bg.stretch = s.read_bool()
            room.backgrounds.append(bg)

        # Views
        room.enable_views = s.read_bool()
        view_count = s.read_int32()
        for _ in range(view_count):
            view = GmkRoomView()
            view.visible = s.read_bool()
            view.xview = s.read_int32()
            view.yview = s.read_int32()
            view.wview = s.read_int32()
            view.hview = s.read_int32()
            view.xport = s.read_int32()
            view.yport = s.read_int32()
            view.wport = s.read_int32()
            view.hport = s.read_int32()
            view.border_h = s.read_int32()
            view.border_v = s.read_int32()
            view.hspeed = s.read_int32()
            view.vspeed = s.read_int32()
            view.follow_object_id = s.read_int32()
            room.views.append(view)

        # Instances
        instance_count = s.read_int32()
        for _ in range(instance_count):
            inst = GmkInstance()
            inst.x = s.read_int32()
            inst.y = s.read_int32()
            inst.object_id = s.read_int32()
            inst.instance_id = s.read_int32()
            inst.creation_code = s.read_string()
            inst.locked = s.read_bool()
            room.instances.append(inst)

        # Tiles
        tile_count = s.read_int32()
        for _ in range(tile_count):
            tile = GmkTile()
            tile.x = s.read_int32()
            tile.y = s.read_int32()
            tile.background_id = s.read_int32()
            tile.tile_x = s.read_int32()
            tile.tile_y = s.read_int32()
            tile.width = s.read_int32()
            tile.height = s.read_int32()
            tile.depth = s.read_int32()
            tile.tile_id = s.read_int32()
            tile.locked = s.read_bool()
            room.tiles.append(tile)

        # Room editor info (14 fields, stored after tiles in all versions)
        _remember = s.read_bool()
        _editor_width = s.read_int32()
        _editor_height = s.read_int32()
        _show_grid = s.read_bool()
        _show_objects = s.read_bool()
        _show_tiles = s.read_bool()
        _show_backgrounds = s.read_bool()
        _show_foregrounds = s.read_bool()
        _show_views = s.read_bool()
        _delete_underlying_objects = s.read_bool()
        _delete_underlying_tiles = s.read_bool()
        if subver == 520:
            s.skip(6 * 4)  # extra tile info for v520
        _current_tab = s.read_int32()
        _scroll_bar_x = s.read_int32()
        _scroll_bar_y = s.read_int32()

        return room

    # ----------------------------------------------------------------
    # Action parsing (shared by objects and timelines)
    # ----------------------------------------------------------------

    def _parse_actions(self, s: GmkStream) -> List[GmkAction]:
        ver = s.read_int32()  # 400
        action_count = s.read_int32()
        actions = []

        for _ in range(action_count):
            action = self._parse_single_action(s)
            actions.append(action)

        return actions

    def _parse_single_action(self, s: GmkStream) -> GmkAction:
        act = GmkAction()

        sub_ver = s.read_int32()  # 440
        act.library_id = s.read_int32()
        act.action_id = s.read_int32()
        act.action_kind = s.read_int32()
        act.has_relative = s.read_bool()
        act.is_question = s.read_bool()
        act.applies_to = s.read_int32()
        act.execution_type = s.read_int32()

        act.function_name = s.read_string()
        act.code = s.read_string()

        act.argument_count = s.read_int32()

        arg_type_count = s.read_int32()
        act.argument_types = [s.read_int32() for _ in range(arg_type_count)]

        # "who" applies-to field, "relative" flag, and arg value count
        _who = s.read_int32()
        act.is_relative = s.read_bool()
        arg_val_count = s.read_int32()

        # Read all argument values (arg_val_count, typically 8)
        # Store the first argument_count, discard the rest
        for i in range(arg_val_count):
            val = s.read_string()
            if i < act.argument_count:
                act.argument_values.append(val)

        act.is_not = s.read_bool()

        return act

    # ----------------------------------------------------------------
    # Skip remaining sections at end of file
    # ----------------------------------------------------------------

    def _skip_remaining_sections(self):
        try:
            # Includes (v800: zlib blocks; pre-v800: complex structure)
            ver = self.stream.read_int32()
            count = self.stream.read_int32()
            if ver >= 800:
                for _ in range(count):
                    self.stream.read_zlib_data()
            else:
                for _ in range(count):
                    self._skip_include_pre800()

            # Extension packages
            ver = self.stream.read_int32()
            count = self.stream.read_int32()
            for _ in range(count):
                _ext_name = self.stream.read_string()

            # Game information
            ver = self.stream.read_int32()
            if ver >= 800:
                self.stream.read_zlib_data()
            else:
                _bg_color = self.stream.read_int32()
                if ver > 430:
                    _show_in_window = self.stream.read_bool()
                _caption = self.stream.read_string()
                _left = self.stream.read_int32()
                _top = self.stream.read_int32()
                _width = self.stream.read_int32()
                _height = self.stream.read_int32()
                _show_border = self.stream.read_bool()
                _allow_resize = self.stream.read_bool()
                _always_on_top = self.stream.read_bool()
                _freeze_game = self.stream.read_bool()
                _info_text = self.stream.read_string()

            # Library creation code
            ver = self.stream.read_int32()
            count = self.stream.read_int32()
            for _ in range(count):
                _lib_code = self.stream.read_string()

        except GmkReadError:
            self._warn("Could not fully parse post-resource sections (non-critical)")

    def _skip_include_pre800(self):
        """Skip a single include entry for pre-v800 format."""
        _filename = self.stream.read_string()
        _filepath = self.stream.read_string()
        _original = self.stream.read_bool()
        _orig_size = self.stream.read_int32()
        _store_in_editable = self.stream.read_bool()
        if _store_in_editable:
            data_len = self.stream.read_int32()
            if data_len > 0:
                self.stream.skip(data_len)
        _export_type = self.stream.read_int32()
        _export_folder = self.stream.read_string()
        _overwrite = self.stream.read_bool()
        _free_memory = self.stream.read_bool()
        _remove_at_end = self.stream.read_bool()
