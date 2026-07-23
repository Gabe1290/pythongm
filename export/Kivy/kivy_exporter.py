#!/usr/bin/env python3
"""
Kivy Exporter for PyGameMaker IDE
Exports projects to Kivy format for mobile deployment
"""

import shutil
from pathlib import Path
from typing import Dict, List, Any

from core.logger import get_logger
logger = get_logger(__name__)

from export.Kivy.code_generator import ActionCodeGenerator


def _bg_color_to_rgb(value) -> tuple:
    """Normalize a room background color to (r, g, b) floats in 0-1.

    Rooms saved by the IDE store hex strings ("#c0c0c0"), but the
    Mobile-(Kivy) dialog path goes through project_adapter, which
    historically rewrote the value to a [r, g, b, a] float list — so both
    forms must be accepted (audit H9). Falls back to gray on anything else.
    """
    if isinstance(value, str):
        hex_str = value[1:] if value.startswith('#') else value
        try:
            return (int(hex_str[0:2], 16) / 255.0,
                    int(hex_str[2:4], 16) / 255.0,
                    int(hex_str[4:6], 16) / 255.0)
        except (ValueError, IndexError):
            return (0.5, 0.5, 0.5)
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        try:
            return (float(value[0]), float(value[1]), float(value[2]))
        except (TypeError, ValueError):
            return (0.5, 0.5, 0.5)
    return (0.5, 0.5, 0.5)


def _exported_asset_filename(asset_name: str, file_path) -> str:
    """The filename an asset is copied to under the flat export dir.

    Keyed on the (project-unique) ASSET NAME plus the source file's extension,
    NOT the source basename — otherwise two assets whose source files merely
    share a basename (e.g. `player/idle.png` and `enemy/idle.png`, or a sprite
    and a background both named `tile.png` imported from different folders)
    overwrite each other on disk and clobber each other's path/frame-metadata
    map entries (EIO-11). Asset names are unique within their type, so this is
    collision-free per type; sprites and backgrounds share `assets/images/`, so
    a sprite and a background with the *same asset name* would still collide —
    that's a far rarer, pre-existing edge left as-is.
    """
    return f"{asset_name}{Path(str(file_path)).suffix}"


# Kivy/SDL key codes, keyed by the event sub-key names the IDE writes.
#
# Until 2026-07-20 this lived as THREE copies inside the code generator and
# held ONLY the four arrows, so a keyboard event on any other key generated
# `if key == 0:` and silently never fired on Android. Letter keys are common
# in the samples (maze_3's R/N/P debug keys, raycast_3's map toggle), and the
# desktop runtime and engine.js both support them, so this was a real
# three-target divergence rather than a missing feature.
_KIVY_KEY_MAP = {
    'right': '275',
    'left': '276',
    'up': '273',
    'down': '274',
    'space': '32',
    'enter': '13',
    'escape': '27',
}
for _c in "abcdefghijklmnopqrstuvwxyz":
    _KIVY_KEY_MAP[_c] = str(ord(_c))        # 'a' -> 97 ... 'z' -> 122
for _d in "0123456789":
    _KIVY_KEY_MAP[_d] = str(ord(_d))        # '0' -> 48 ... '9' -> 57


class KivyExporter:
    """Export PyGameMaker projects to Kivy format"""

    def __init__(self, project_data: Dict[str, Any], project_path: Path, output_path: Path):
        self.project_data = project_data
        self.project_path = Path(project_path)
        self.output_path = Path(output_path)
        self.grid_size = 32  # Default grid size for snapping
        # sprite_name -> exported asset path, so the set_sprite action can
        # resolve a sprite by name. Sprites are copied to
        # assets/images/<asset_name><ext> by _export_sprite (name-keyed, not
        # source-basename-keyed — see _exported_asset_filename), matching
        # _generate_object's initial-sprite path.
        self.sprite_path_map = {
            name: f"assets/images/{_exported_asset_filename(name, data.get('file_path', ''))}"
            for name, data in project_data.get('assets', {}).get('sprites', {}).items()
            if data.get('file_path')
        }
        # sound_name -> exported asset path, for the play_sound action.
        # Sounds are copied to assets/sounds/<asset_name><ext> by _export_sound.
        self.sound_path_map = {
            name: f"assets/sounds/{_exported_asset_filename(name, data.get('file_path', ''))}"
            for name, data in project_data.get('assets', {}).get('sounds', {}).items()
            if data.get('file_path')
        }
        # background_name -> exported asset path, for the draw_background
        # draw-queue command. Backgrounds are copied to
        # assets/images/<asset_name><ext> by _export_background (same directory
        # as sprites, but kept in its own map — not merged into sprite_path_map).
        self.background_path_map = {
            name: f"assets/images/{_exported_asset_filename(name, data.get('file_path', ''))}"
            for name, data in project_data.get('assets', {}).get('backgrounds', {}).items()
            if data.get('file_path')
        }
        # exported sprite path -> frame metadata, so the runtime draws a single
        # frame of a multi-frame strip (and animates it) instead of blitting the
        # whole sheet. frame_width/height are per-frame; 'width' is the full
        # strip width, so it is NOT a frame-width fallback for multi-frame art.
        self.sprite_meta_map = {}
        for _name, _data in project_data.get('assets', {}).get('sprites', {}).items():
            _fp = _data.get('file_path')
            if not _fp:
                continue
            _frames = max(1, int(_data.get('frames', 1) or 1))
            _fw = int(_data.get('frame_width') or (_data.get('width') if _frames == 1 else 0) or 0)
            _fh = int(_data.get('frame_height') or _data.get('height') or 0)
            self.sprite_meta_map[f"assets/images/{_exported_asset_filename(_name, _fp)}"] = {
                'frames': _frames,
                'frame_width': _fw,
                'frame_height': _fh,
                'speed': float(_data.get('speed', 1.0) or 1.0),
            }

    def export(self) -> bool:
        """Export project to Kivy format"""
        try:

            logger.info("=" * 60)
            logger.info("Starting Kivy Export")
            logger.info("=" * 60)

            # Diagnostic output
            logger.debug("Project Data Diagnostic:")
            logger.debug(f"  Project name: {self.project_data.get('name', 'Unknown')}")
            logger.debug(f"  Output path: {self.output_path}")
            logger.debug(f"  Project path: {self.project_path}")

            assets = self.project_data.get('assets', {})
            logger.debug("Assets found:")
            for asset_type, asset_dict in assets.items():
                logger.debug(f"  - {asset_type}: {len(asset_dict)} items")
                if asset_type in ['rooms', 'objects']:
                    for name in asset_dict.keys():
                        logger.debug(f"    - {name}")
                        # Show event info for objects
                        if asset_type == 'objects':
                            obj_data = asset_dict[name]
                            if isinstance(obj_data, dict):
                                events = obj_data.get('events', [])
                                if events:
                                    if isinstance(events, list):
                                        logger.debug(f"      - {len(events)} event(s)")
                                    elif isinstance(events, dict):
                                        logger.debug(f"      - {len(events)} event(s) in dict (keys: {list(events.keys())[:3]}...)")
                                    else:
                                        logger.debug(f"      - events is {type(events).__name__} (expected list or dict)")

            logger.debug("")

            # Create directory structure
            self._create_directory_structure()
            logger.info("Directory structure created")

            # Export assets
            self._export_assets()
            logger.info(f"Exported {self._count_assets()} asset(s)")

            # Generate main application
            self._generate_main_app()
            logger.info("Main application generated")

            # Generate game scenes/rooms
            self._generate_scenes()
            logger.info(f"Generated {len(self.project_data.get('assets', {}).get('rooms', {}))} room(s)")

            # Generate object classes
            self._generate_objects()
            logger.info(f"Generated {len(self.project_data.get('assets', {}).get('objects', {}))} object type(s)")

            # Generate utility files
            self._generate_utils()
            logger.info("Game logic utilities generated")

            # Generate the high-score table module
            self._generate_highscore_module()
            logger.info("High-score module generated")

            # Generate the sprite frame-metadata module
            self._generate_sprite_meta_module()
            logger.info("Sprite metadata module generated")

            # Generate the asset name -> exported path lookup module
            self._generate_asset_paths_module()
            logger.info("Asset paths module generated")

            # Generate build configuration
            self._generate_buildozer_spec()
            logger.info("Buildozer spec generated")

            # Generate requirements file
            self._generate_requirements()
            logger.info("Requirements file generated")

            # Generate README
            self._generate_readme()
            logger.info("README created")

            logger.info("=" * 60)
            logger.info("Export completed successfully!")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _create_directory_structure(self):
        """Create the output directory structure"""
        dirs = [
            self.output_path / "game",
            self.output_path / "game" / "assets",
            self.output_path / "game" / "assets" / "images",
            self.output_path / "game" / "assets" / "sounds",
            self.output_path / "game" / "objects",
            self.output_path / "game" / "scenes",
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"  Created: {dir_path}")

        # Create __init__.py files to make directories Python packages
        package_dirs = [
            self.output_path / "game" / "objects",
            self.output_path / "game" / "scenes",
        ]

        for pkg_dir in package_dirs:
            init_file = pkg_dir / "__init__.py"
            init_file.write_text("# Auto-generated package file\n", encoding="utf-8")
            logger.debug(f"  Created: {init_file}")

    def _count_assets(self) -> int:
        """Count total number of assets"""
        count = 0
        assets = self.project_data.get('assets', {})
        for asset_type in ['sprites', 'sounds', 'backgrounds']:
            count += len(assets.get(asset_type, {}))
        return count

    def _export_assets(self):
        """Export all game assets"""
        assets = self.project_data.get('assets', {})

        # Export sprites
        for sprite_name, sprite_data in assets.get('sprites', {}).items():
            self._export_sprite(sprite_name, sprite_data)

        # Export sounds
        for sound_name, sound_data in assets.get('sounds', {}).items():
            self._export_sound(sound_name, sound_data)

        # Export backgrounds
        for bg_name, bg_data in assets.get('backgrounds', {}).items():
            self._export_background(bg_name, bg_data)

    def _export_sprite(self, name: str, data: Dict):
        """Export a sprite asset"""
        file_path = data.get('file_path', '')
        if file_path:
            src = self.project_path / file_path
            if src.exists():
                dst = (self.output_path / "game" / "assets" / "images"
                       / _exported_asset_filename(name, file_path))
                shutil.copy2(src, dst)

    def _export_sound(self, name: str, data: Dict):
        """Export a sound asset"""
        file_path = data.get('file_path', '')
        if file_path:
            src = self.project_path / file_path
            if src.exists():
                dst = (self.output_path / "game" / "assets" / "sounds"
                       / _exported_asset_filename(name, file_path))
                shutil.copy2(src, dst)

    def _export_background(self, name: str, data: Dict):
        """Export a background asset"""
        file_path = data.get('file_path', '')
        if file_path:
            src = self.project_path / file_path
            if src.exists():
                dst = (self.output_path / "game" / "assets" / "images"
                       / _exported_asset_filename(name, file_path))
                shutil.copy2(src, dst)

    def _generate_main_app(self):
        """Generate the main Kivy application file"""
        rooms = self.project_data.get('assets', {}).get('rooms', {})
        project_name = self.project_data.get('name', 'Game')

        # Get first room as starting room
        room_names = list(rooms.keys())
        first_room = room_names[0] if room_names else "room0"

        # Get room dimensions
        room_data = rooms.get(first_room, {})
        room_width = self._safe_room_dim(room_data.get('width'), 640)
        room_height = self._safe_room_dim(room_data.get('height'), 480)

        # A views room displays the game WINDOW (a slice of the larger room),
        # not the room, so the OS window / Android fit-scale must use the window
        # size. Non-views rooms are unchanged (window == room). Prefer project
        # window settings, then view 0's port, then the room.
        first_views = bool(room_data.get('views_enabled',
                                         room_data.get('enable_views', False)))
        if first_views:
            settings = self.project_data.get('settings', {})
            v0 = {}
            vraw = room_data.get('views', {})
            if isinstance(vraw, dict):
                v0 = vraw.get('view_0', {}) or {}
            room_width = int(settings.get('window_width')
                             or v0.get('port_w') or room_width)
            room_height = int(settings.get('window_height')
                              or v0.get('port_h') or room_height)

        # Generate imports for all rooms
        room_imports = []
        room_class_map = {}
        for room_name in room_names:
            class_name = self._get_room_class_name(room_name)
            module_name = self._get_room_module_name(room_name)
            room_imports.append(f"from scenes.{module_name} import {class_name}")
            room_class_map[room_name] = class_name

        room_imports_str = '\n'.join(room_imports)

        # Generate room list for navigation
        room_list_str = ', '.join([f'"{name}"' for name in room_names])

        # Generate room class mapping
        room_mapping_str = ', '.join([f'"{name}": {cls}' for name, cls in room_class_map.items()])

        # Generate room metadata (dimensions + bg color per room)
        room_meta_entries = []
        for rname in room_names:
            rd = rooms.get(rname, {})
            rw = self._safe_room_dim(rd.get('width'), 640)
            rh = self._safe_room_dim(rd.get('height'), 480)
            br, bg_, bb = _bg_color_to_rgb(rd.get('background_color', '#808080'))
            room_meta_entries.append(
                f'"{rname}": ({rw}, {rh}, {br:.3f}, {bg_:.3f}, {bb:.3f})')
        room_meta_str = ', '.join(room_meta_entries)

        code = '''#!/usr/bin/env python3
"""
Generated Kivy Game Application
Exported from PyGameMaker IDE
"""

# Register this module as 'main' in sys.modules so that
# "from main import ..." in game objects resolves to THIS module
# instead of re-importing main.py (which would re-execute Kivy
# config and crash the GL context on Android).
import sys as _sys
_sys.modules.setdefault('main', _sys.modules[__name__])

# Room dimensions - used for window sizing
GAME_WIDTH = {room_width}
GAME_HEIGHT = {room_height}

import os
os.environ['KIVY_WINDOW'] = 'sdl2'

# --- Native crash handler (catches SIGSEGV / SIGABRT) ---
import faulthandler as _fh
try:
    _fh_file = open(os.path.join(
        os.environ.get('ANDROID_APP_PATH', '.'), 'native_crash.log'), 'w')
    _fh.enable(file=_fh_file, all_threads=True)
except Exception:
    _fh.enable()  # Fallback: write to stderr (goes to logcat on Android)

# --- Platform detection ---
IS_ANDROID = False
try:
    import android  # noqa: F401 - available on python-for-android
    IS_ANDROID = True
except ImportError:
    pass

if not IS_ANDROID:
    # Desktop: Get Windows DPI scale and adjust window size to compensate
    def get_dpi_scale():
        try:
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except (OSError, AttributeError):
                # OSError: shcore missing (pre-Win 8.1); AttributeError: no SetProcessDpiAwareness
                pass
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
            ctypes.windll.user32.ReleaseDC(0, hdc)
            return dpi / 96.0
        except Exception:
            return 1.0

    DPI_SCALE = get_dpi_scale()
    ADJUSTED_WIDTH = int(GAME_WIDTH / DPI_SCALE)
    ADJUSTED_HEIGHT = int(GAME_HEIGHT / DPI_SCALE)

    from kivy.config import Config
    Config.set('graphics', 'width', str(ADJUSTED_WIDTH))
    Config.set('graphics', 'height', str(ADJUSTED_HEIGHT))
    Config.set('graphics', 'resizable', '0')
    Config.set('graphics', 'fullscreen', '0')
else:
    # Android: fullscreen, no fixed window size
    DPI_SCALE = 1.0
    ADJUSTED_WIDTH = GAME_WIDTH
    ADJUSTED_HEIGHT = GAME_HEIGHT
    from kivy.config import Config
    Config.set('graphics', 'fullscreen', 'auto')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, PushMatrix, PopMatrix
from kivy.graphics import Scale as ScaleInstr, Translate as TranslateInstr
from kivy.graphics import Ellipse, Triangle
from kivy.core.image import Image as CoreImage

# Force adjusted window size (desktop only)
if not IS_ANDROID:
    Window.size = (ADJUSTED_WIDTH, ADJUSTED_HEIGHT)

# Import all game scenes
{room_imports_str}

# Global game manager reference
_game_app = None

# Whether any object listens to keyboard events. A game with no keyboard
# input (e.g. touch/mouse-driven puzzles) gets no virtual D-pad overlay,
# which would otherwise cover the corner and swallow taps there.
NEEDS_DPAD = {needs_dpad}
NEEDS_MAP_BUTTON = {needs_map_button}

# Room configuration
ROOM_ORDER = [{room_list_str}]
ROOM_CLASSES = {{{room_mapping_str}}}
ROOM_META = {{{room_meta_str}}}

# Crash logger - writes to file so we can diagnose Android crashes
import os as _os, traceback as _tb, datetime as _dt
_log_path = None
def _get_log_path():
    global _log_path
    if _log_path:
        return _log_path
    if IS_ANDROID:
        # Try several Android-writable locations
        for d in [_os.environ.get('ANDROID_APP_PATH', ''),
                  '/sdcard', '/storage/emulated/0',
                  _os.path.expanduser('~'), '.']:
            if d and _os.path.isdir(d):
                _log_path = _os.path.join(d, 'pygm_crash.log')
                return _log_path
    _log_path = 'pygm_crash.log'
    return _log_path

def _log(msg):
    # Always print to stdout (goes to logcat on Android)
    print(f"[PYGM] {{msg}}")
    try:
        with open(_get_log_path(), 'a', encoding='utf-8', errors='replace') as f:
            f.write(f"[{{_dt.datetime.now():%H:%M:%S}}] {{msg}}\\n")
            f.flush()
    except (OSError, ValueError):
        # OSError: disk/perm failure; ValueError: stream closed during shutdown
        pass

_log("=== App starting ===")


def get_game_app():
    """Get the global game app instance"""
    return _game_app


# Sound playback — SoundLoader-backed, cached by exported asset path so a
# repeated sound effect loads once. Failures are logged, never fatal.
_sound_cache = {{}}

def play_sound(path, volume=1.0):
    """Play a sound effect by its exported asset path (e.g. assets/sounds/x.wav)."""
    try:
        from kivy.core.audio import SoundLoader
        snd = _sound_cache.get(path)
        if snd is None:
            snd = SoundLoader.load(path)
            _sound_cache[path] = snd
        if snd:
            snd.volume = float(volume)
            snd.play()
    except Exception as _e:
        _log(f"play_sound failed for {{path}}: {{_e}}")


_room_transition_pending = False

def goto_next_room():
    """Go to the next room in the room order"""
    global _room_transition_pending
    if _game_app and not _room_transition_pending:
        _room_transition_pending = True
        _game_app.goto_next_room()


def goto_previous_room():
    """Go to the previous room in the room order"""
    global _room_transition_pending
    if _game_app and not _room_transition_pending:
        _room_transition_pending = True
        _game_app.goto_previous_room()


def goto_room(room_name):
    """Go to a specific room by name"""
    global _room_transition_pending
    if _game_app and not _room_transition_pending:
        _room_transition_pending = True
        _game_app.goto_room(room_name)


def next_room_exists():
    """Check if there is a next room after the current one"""
    if _game_app:
        return _game_app.current_room_index + 1 < len(ROOM_ORDER)
    return False


def previous_room_exists():
    """Check if there is a previous room before the current one"""
    if _game_app:
        return _game_app.current_room_index > 0
    return False


def get_score():
    """Get the current score"""
    if _game_app:
        return _game_app.score
    return 0


def set_score(value, relative=False):
    """Set the score value"""
    if _game_app:
        if relative:
            _game_app.score += value
        else:
            _game_app.score = value
        _game_app.show_score_in_caption = True
        _game_app.update_caption()


def get_lives():
    """Get the current lives"""
    if _game_app:
        return _game_app.lives
    return 0


def set_lives(value, relative=False):
    """Set the lives value"""
    if _game_app:
        _old_lives = _game_app.lives
        if relative:
            _game_app.lives += value
        else:
            _game_app.lives = value
        _game_app.show_lives_in_caption = True
        _game_app.update_caption()
        # IDE-runtime parity: when lives cross from >0 to <=0, fire
        # no_more_lives once on EVERY instance that defines it.
        if _old_lives > 0 and _game_app.lives <= 0 and _game_app.scene:
            for _inst in list(_game_app.scene.instances):
                if hasattr(_inst, 'on_no_more_lives'):
                    try:
                        _inst.on_no_more_lives()
                    except Exception as _exc:
                        print(f"[ERROR] on_no_more_lives: {{_exc}}")


def get_health():
    """Get the current health"""
    if _game_app:
        return _game_app.health
    return 100


def set_health(value, relative=False):
    """Set the health value"""
    if _game_app:
        _old_health = _game_app.health
        if relative:
            _game_app.health += value
        else:
            _game_app.health = value
        _game_app.health = max(0, min(100, _game_app.health))
        _game_app.show_health_in_caption = True
        _game_app.update_caption()
        # IDE-runtime parity: when health crosses from >0 to <=0, fire
        # no_more_health once on EVERY instance that defines it — mirrors
        # set_lives/no_more_lives above. Missing until 2026-07-20.
        if _old_health > 0 and _game_app.health <= 0 and _game_app.scene:
            for _inst in list(_game_app.scene.instances):
                if hasattr(_inst, 'on_no_more_health'):
                    try:
                        _inst.on_no_more_health()
                    except Exception as _exc:
                        print(f"[ERROR] on_no_more_health: {{_exc}}")


def set_window_caption(caption="", show_score=True, show_lives=True, show_health=False):
    """Set window caption settings"""
    if _game_app:
        _game_app.window_caption = caption
        _game_app.show_score_in_caption = show_score
        _game_app.show_lives_in_caption = show_lives
        _game_app.show_health_in_caption = show_health
        _game_app.update_caption()


_popup_open = False
_current_popup = None
_pending_room_switch = None

# --- Android Activity restart for room switching ---
import json as _json
_STATE_FILE = _os.path.join(
    _os.environ.get('ANDROID_APP_PATH', '.'), '_pygm_state.json')

def _save_state_and_restart(room_index):
    """Save game state and restart the Android Activity for a clean GL context."""
    app = get_game_app()
    state = {{
        'room': room_index,
        'score': app.score if app else 0,
        'lives': app.lives if app else 3,
        'health': app.health if app else 100,
    }}
    _log(f"_save_state_and_restart: saving {{state}}")
    try:
        with open(_STATE_FILE, 'w', encoding='utf-8') as f:
            _json.dump(state, f, ensure_ascii=False)
            f.flush()
            _os.fsync(f.fileno())
    except Exception as exc:
        _log(f"_save_state_and_restart: write failed: {{exc}}")
        return False

    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        if activity is None:
            _log("_save_state_and_restart: mActivity is None")
            return False
        Intent = autoclass('android.content.Intent')
        intent = Intent(activity, PythonActivity)
        intent.addFlags(
            Intent.FLAG_ACTIVITY_NEW_TASK
            | Intent.FLAG_ACTIVITY_CLEAR_TASK)
        _log("_save_state_and_restart: restarting Activity")
        activity.startActivity(intent)
        _log("_save_state_and_restart: startActivity done, exiting process")
        _os._exit(0)  # Hard exit - no GL cleanup that could corrupt
        return True
    except Exception as exc:
        _log(f"_save_state_and_restart: failed: {{exc}}")
        import traceback; traceback.print_exc()
        return False

def _load_saved_state():
    """Load saved game state from a previous Activity restart."""
    if not _os.path.exists(_STATE_FILE):
        return None
    try:
        with open(_STATE_FILE, encoding='utf-8') as f:
            state = _json.load(f)
        _os.remove(_STATE_FILE)
        _log(f"_load_saved_state: restored {{state}}")
        return state
    except Exception as exc:
        _log(f"_load_saved_state: failed: {{exc}}")
        try:
            _os.remove(_STATE_FILE)
        except OSError:
            pass
        return None


def show_message(message):
    """Show a message dialog - pauses the game until dismissed"""
    global _popup_open, _current_popup
    _log(f"show_message: '{{message}}'")

    # Prevent duplicate messages
    if _popup_open:
        _log("show_message: already open, skipping")
        return
    _popup_open = True

    # Pause the game loop while message is shown
    app = get_game_app()
    if app and app.update_event:
        Clock.unschedule(app.update_event)
        app.update_event = None

    if IS_ANDROID:
        # Use pre-created overlay (no widget tree changes)
        def _on_overlay_dismiss():
            global _popup_open, _pending_room_switch
            _log("_on_overlay_dismiss called")
            _popup_open = False
            if _pending_room_switch is not None:
                room_index = _pending_room_switch
                _pending_room_switch = None
                _log(f"_on_overlay_dismiss: deferred room switch to {{room_index}}")
                a2 = get_game_app()
                if a2:
                    Clock.schedule_once(
                        lambda dt: a2._switch_to_room(room_index), 0)
            else:
                _log("_on_overlay_dismiss: resuming game loop")
                a2 = get_game_app()
                if a2 and a2.scene and not a2.update_event:
                    a2.update_event = Clock.schedule_interval(
                        a2.scene.update, 1.0/60.0)
        if hasattr(app, '_msg_overlay'):
            app._msg_overlay.show(str(message), on_dismiss=_on_overlay_dismiss)
        else:
            _log("show_message: no _msg_overlay, skipping")
            _popup_open = False
        return

    # --- Desktop: use Kivy Popup ---
    content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    content.add_widget(Label(text=str(message)))
    btn = Button(text='OK', size_hint_y=None, height=40)
    content.add_widget(btn)

    popup = Popup(title='Message',
                  content=content,
                  size_hint=(None, None),
                  size=(300, 200),
                  auto_dismiss=False)

    def on_key_down(window, key, scancode, codepoint, modifiers):
        if key == 13 or key == 271:  # Enter or NumPad Enter
            popup.dismiss()
            return True

    def on_dismiss(instance):
        global _popup_open, _current_popup, _pending_room_switch
        _log("on_dismiss: popup closing")
        _popup_open = False
        _current_popup = None
        Window.unbind(on_key_down=on_key_down)

        if _pending_room_switch is not None:
            room_index = _pending_room_switch
            _pending_room_switch = None
            _log(f"on_dismiss: deferred room switch to index {{room_index}}")
            a2 = get_game_app()
            if a2:
                Clock.schedule_once(
                    lambda dt: a2._switch_to_room(room_index), 0)
        else:
            _log("on_dismiss: resuming game loop (no room switch)")
            a2 = get_game_app()
            if a2 and a2.scene and not a2.update_event:
                a2.update_event = Clock.schedule_interval(
                    a2.scene.update, 1.0/60.0)

    popup.bind(on_dismiss=on_dismiss)
    btn.bind(on_release=popup.dismiss)
    Window.bind(on_key_down=on_key_down)
    _current_popup = popup
    popup.open()
    btn.focus = True

def dismiss_message():
    """Dismiss any open message popup"""
    global _current_popup
    if _current_popup:
        _current_popup.dismiss()


# --- Virtual D-pad for Android touch controls ---
if IS_ANDROID:
    class VirtualDPad(Widget):
        """On-screen D-pad for touch-based arrow key input"""

        KEY_UP = 273
        KEY_DOWN = 274
        KEY_RIGHT = 275
        KEY_LEFT = 276
        KEY_MAP_TOGGLE = 109        # 'm' — only shown when the game uses it

        def __init__(self, scene_ref=None, **kwargs):
            super().__init__(**kwargs)
            self.scene_ref = scene_ref
            self._active_keys = set()
            self._btn_size = 70
            self._padding = 50
            self._alpha = 0.35
            self._buttons = {{}}
            Clock.schedule_once(lambda dt: self._draw_buttons(), 0)

        def _draw_buttons(self, *args):
            """Calculate button positions and draw D-pad"""
            s = self._btn_size
            pad = self._padding
            # D-pad center: bottom-right of screen
            cx = Window.width - pad - s * 1.5
            cy = pad + s * 1.5

            self._buttons = {{
                self.KEY_UP:    (cx, cy + s, s, s),
                self.KEY_DOWN:  (cx, cy - s, s, s),
                self.KEY_LEFT:  (cx - s, cy, s, s),
                self.KEY_RIGHT: (cx + s, cy, s, s),
            }}
            # Optional map-toggle button, top-LEFT of the screen so it can't be
            # confused with movement or sit under the thumb that drives it.
            # Only present when the game actually binds 'm' (NEEDS_MAP_BUTTON),
            # so ordinary keyboard games don't grow a mystery button.
            if NEEDS_MAP_BUTTON:
                self._buttons[self.KEY_MAP_TOGGLE] = (pad, Window.height - pad - s, s, s)

            self.canvas.clear()
            with self.canvas:
                for key_code, (bx, by, bw, bh) in self._buttons.items():
                    Color(1, 1, 1, self._alpha)
                    Ellipse(pos=(bx, by), size=(bw, bh))
                # Arrow triangles
                Color(0.2, 0.2, 0.2, self._alpha + 0.3)
                bx, by, bw, bh = self._buttons[self.KEY_UP]
                Triangle(points=[bx+bw/2, by+bh*0.8, bx+bw*0.2, by+bh*0.3, bx+bw*0.8, by+bh*0.3])
                bx, by, bw, bh = self._buttons[self.KEY_DOWN]
                Triangle(points=[bx+bw/2, by+bh*0.2, bx+bw*0.2, by+bh*0.7, bx+bw*0.8, by+bh*0.7])
                bx, by, bw, bh = self._buttons[self.KEY_LEFT]
                Triangle(points=[bx+bw*0.2, by+bh/2, bx+bw*0.7, by+bh*0.8, bx+bw*0.7, by+bh*0.2])
                bx, by, bw, bh = self._buttons[self.KEY_RIGHT]
                Triangle(points=[bx+bw*0.8, by+bh/2, bx+bw*0.3, by+bh*0.8, bx+bw*0.3, by+bh*0.2])
                if self.KEY_MAP_TOGGLE in self._buttons:
                    # A little grid glyph, so the button reads as "map" rather
                    # than as another movement control.
                    bx, by, bw, bh = self._buttons[self.KEY_MAP_TOGGLE]
                    Line(rectangle=(bx+bw*0.25, by+bh*0.25, bw*0.5, bh*0.5), width=1.5)
                    Line(points=[bx+bw*0.5, by+bh*0.25, bx+bw*0.5, by+bh*0.75], width=1.2)
                    Line(points=[bx+bw*0.25, by+bh*0.5, bx+bw*0.75, by+bh*0.5], width=1.2)

        def _hit_test(self, x, y):
            """Return key code if touch is inside a button, else None"""
            for key_code, (bx, by, bw, bh) in self._buttons.items():
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    return key_code
            return None

        def on_touch_down(self, touch):
            key = self._hit_test(touch.x, touch.y)
            if key is not None:
                touch.grab(self)
                self._press_key(key)
                return True
            return False

        def on_touch_move(self, touch):
            if touch.grab_current is self:
                new_key = self._hit_test(touch.x, touch.y)
                for old_key in list(self._active_keys):
                    if old_key != new_key:
                        self._release_key(old_key)
                if new_key is not None and new_key not in self._active_keys:
                    self._press_key(new_key)
                return True
            return False

        def on_touch_up(self, touch):
            if touch.grab_current is self:
                touch.ungrab(self)
                for key in list(self._active_keys):
                    self._release_key(key)
                return True
            return False

        def _press_key(self, key_code):
            if key_code not in self._active_keys:
                self._active_keys.add(key_code)
                if self.scene_ref:
                    self.scene_ref.on_keyboard(None, key_code, 0, '', [])

        def _release_key(self, key_code):
            if key_code in self._active_keys:
                self._active_keys.discard(key_code)
                if self.scene_ref:
                    self.scene_ref.on_keyboard_up(None, key_code, 0)

        def update_scene(self, new_scene):
            """Update scene reference on room switch"""
            # Clear active keys without calling the old scene's handlers
            # (the old scene is being destroyed)
            self._active_keys.clear()
            self.scene_ref = new_scene
else:
    VirtualDPad = None


# --- Android message overlay (replaces Kivy Popup) ---
# Pre-created and always in the widget tree. No add_widget / remove_widget
# during gameplay.  Showing/hiding only changes canvas Color.a and Label.text.
class _MsgOverlay(Widget):
    _active = False
    _on_dismiss = None

    def __init__(self, **kw):
        super().__init__(**kw)
        self.size_hint = (1, 1)
        with self.canvas:
            self._bg_color = Color(0, 0, 0, 0)
            Rectangle(pos=(-500, -500), size=(19999, 19999))
        self._label = Label(
            text='', font_size='20sp', color=(1, 1, 1, 1),
            halign='center', valign='middle',
            size_hint=(0.8, 0.6),
            pos_hint={{'center_x': 0.5, 'center_y': 0.55}})
        self._label.bind(
            size=lambda inst, val: setattr(inst, 'text_size', val))
        self.add_widget(self._label)
        self._hint = Label(
            text='', font_size='16sp', color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.15),
            pos_hint={{'center_x': 0.5, 'y': 0.08}})
        self.add_widget(self._hint)

    def show(self, text, on_dismiss=None):
        self._active = True
        self._on_dismiss = on_dismiss
        self._label.text = str(text)
        self._hint.text = 'Tap to continue'
        self._bg_color.a = 0.85

    def dismiss(self):
        if not self._active:
            return
        self._active = False
        self._bg_color.a = 0
        self._label.text = ' '
        self._hint.text = ' '
        cb = self._on_dismiss
        self._on_dismiss = None
        if cb:
            cb()

    def on_touch_down(self, touch):
        if self._active:
            self.dismiss()
            return True
        return False


class GameApp(App):
    """Main game application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_room_index = 0
        self.scene = None
        self.scene_container = None
        self.dpad = None
        self.update_event = None

        # Game state (initialized in build() from saved state or defaults)
        self.score = 0
        self.lives = 3
        self.health = 100

        # Caption display settings
        self.window_caption = ""
        self.show_score_in_caption = False
        self.show_lives_in_caption = False
        self.show_health_in_caption = False
        self.project_name = "{project_name}"

    def update_caption(self):
        """Update window caption with score/lives/health if enabled"""
        parts = []

        if self.window_caption:
            parts.append(self.window_caption)

        if self.show_score_in_caption:
            parts.append(f"Score: {{self.score}}")

        if self.show_lives_in_caption:
            parts.append(f"Lives: {{self.lives}}")

        if self.show_health_in_caption:
            parts.append(f"Health: {{int(self.health)}}")

        caption = " | ".join(parts) if parts else self.project_name
        Window.set_title(caption)

    def build(self):
        """Build the application"""
        global _game_app
        _game_app = self

        Window.clearcolor = (0, 0, 0, 1)

        # Check for saved state from an Activity restart (Android room switch)
        _saved = _load_saved_state()
        if _saved:
            _start_idx = _saved.get('room', 0)
            self.score = _saved.get('score', 0)
            self.lives = _saved.get('lives', 3)
            self.health = _saved.get('health', 100)
        else:
            _start_idx = 0
        _start_name = ROOM_ORDER[_start_idx]
        _start_class = ROOM_CLASSES[_start_name]
        _log(f"build: starting room={{_start_name}} (index {{_start_idx}})")

        # Create root layout container
        self.root_layout = FloatLayout()

        # Create the starting scene
        self.scene = _start_class()
        self.current_room_index = _start_idx

        if IS_ANDROID:
            # Scale game to fill screen with correct aspect ratio
            self.scene_container = self._create_scaled_container(self.scene)
            self.root_layout.add_widget(self.scene_container)
            # Add virtual D-pad overlay (only for keyboard-driven games)
            if VirtualDPad is not None and NEEDS_DPAD:
                self.dpad = VirtualDPad(scene_ref=self.scene)
                self.dpad.size_hint = (1, 1)
                self.root_layout.add_widget(self.dpad)
            # Pre-created message overlay (replaces Popup on Android)
            self._msg_overlay = _MsgOverlay()
            self.root_layout.add_widget(self._msg_overlay)
        else:
            # Desktop: fixed window size
            Window.size = (ADJUSTED_WIDTH, ADJUSTED_HEIGHT)
            self.root_layout.add_widget(self.scene)
            def force_size(dt):
                Window.size = (ADJUSTED_WIDTH, ADJUSTED_HEIGHT)
            Clock.schedule_once(force_size, 0.1)

        # Schedule game loop at 60 FPS
        self.update_event = Clock.schedule_interval(self.scene.update, 1.0/60.0)

        return self.root_layout

    def _create_scaled_container(self, scene):
        """Create a persistent container that scales game to fill screen.

        The container and its GL transform instructions (PushMatrix,
        Translate, Scale, PopMatrix) are created once and reused across
        room switches.  Only the scene widget inside is swapped.
        """
        screen_w = Window.width
        screen_h = Window.height
        # Fit-scale the DISPLAYED surface (the window/ports for a views room,
        # the room otherwise) — not the room, which for a views game is larger
        # than what the camera actually shows.
        game_w = getattr(scene, 'display_width', scene.room_width)
        game_h = getattr(scene, 'display_height', scene.room_height)

        scale = min(screen_w / game_w, screen_h / game_h)
        offset_x = (screen_w - game_w * scale) / 2
        offset_y = (screen_h - game_h * scale) / 2

        container = Widget()
        with container.canvas.before:
            PushMatrix()
            self._ctr_translate = TranslateInstr(offset_x, offset_y, 0)
            self._ctr_scale = ScaleInstr(scale, scale, 1)
        with container.canvas.after:
            PopMatrix()

        container.add_widget(scene)
        return container

    def goto_next_room(self):
        """Switch to the next room"""
        next_index = self.current_room_index + 1
        if next_index < len(ROOM_ORDER):
            self._switch_to_room(next_index)
        else:
            show_message("Already at last room")

    def goto_previous_room(self):
        """Switch to the previous room"""
        if self.current_room_index > 0:
            self._switch_to_room(self.current_room_index - 1)
        else:
            show_message("Already at first room")

    def goto_room(self, room_name):
        """Switch to a specific room by name"""
        if room_name in ROOM_ORDER:
            index = ROOM_ORDER.index(room_name)
            self._switch_to_room(index)
        else:
            show_message(f"Room '{{room_name}}' not found")

    def _switch_to_room(self, room_index):
        """Internal method to switch rooms"""
        global _pending_room_switch
        _log(f"_switch_to_room({{room_index}}) called")
        if room_index < 0 or room_index >= len(ROOM_ORDER):
            _log(f"_switch_to_room: invalid index {{room_index}}")
            return

        # If a message popup is open, defer the room switch until it's dismissed
        if _popup_open:
            _log("_switch_to_room: popup open, deferring")
            _pending_room_switch = room_index
            return

        # Stop update loop before switching
        if self.update_event:
            Clock.unschedule(self.update_event)
            self.update_event = None

        _log(f"_switch_to_room: scheduling _do_room_switch({{room_index}})")
        Clock.schedule_once(lambda dt: self._do_room_switch(room_index), 0)

    def _do_room_switch(self, room_index):
        """Switch to a new room with clean remove/add."""
        global _room_transition_pending

        try:
            room_name = ROOM_ORDER[room_index]
            room_class = ROOM_CLASSES[room_name]
            meta = ROOM_META[room_name]
            _log(f"_do_room_switch: target={{room_name}}")

            # 1. Unbind old scene's keyboard handlers from Window.
            # Swallow broadly: Kivy's Window.unbind does not document its
            # exception types, and we cannot tell from here whether the
            # handlers were ever bound (depends on whether the scene was
            # ever entered before the room switch).
            old_scene = self.scene
            if old_scene:
                try:
                    Window.unbind(on_keyboard=old_scene.on_keyboard)
                    Window.unbind(on_key_up=old_scene.on_keyboard_up)
                except Exception:
                    pass

            # 2. Remove old scene from widget tree (no canvas clearing)
            if IS_ANDROID:
                if old_scene and self.scene_container:
                    self.scene_container.remove_widget(old_scene)
            else:
                if old_scene:
                    self.root_layout.remove_widget(old_scene)

            # 3. Create new scene
            _log(f"_do_room_switch: creating {{room_class.__name__}}")
            new_scene = room_class()

            # 4. Add new scene to widget tree. Use the scene's DISPLAYED size
            # (window/ports for a views room, else the room) so a views room
            # sizes to its camera window, not the larger room.
            disp_w = getattr(new_scene, 'display_width', meta[0])
            disp_h = getattr(new_scene, 'display_height', meta[1])
            if IS_ANDROID:
                self.scene_container.add_widget(new_scene)
                screen_w = Window.width
                screen_h = Window.height
                scale = min(screen_w / disp_w, screen_h / disp_h)
                self._ctr_translate.x = (screen_w - disp_w * scale) / 2
                self._ctr_translate.y = (screen_h - disp_h * scale) / 2
                self._ctr_scale.x = scale
                self._ctr_scale.y = scale
            else:
                self.root_layout.add_widget(new_scene)
                new_w = int(disp_w / DPI_SCALE)
                new_h = int(disp_h / DPI_SCALE)
                Window.size = (new_w, new_h)

            # 5. Update references
            self.scene = new_scene
            self.current_room_index = room_index

            # 6. Update D-pad scene reference
            if self.dpad:
                self.dpad.update_scene(new_scene)

            # 7. Start update loop for new scene
            self.update_event = Clock.schedule_interval(
                new_scene.update, 1.0/60.0)

            _log(f"_do_room_switch: SUCCESS - switched to {{room_name}}")

        except Exception as exc:
            _log(f"_do_room_switch: EXCEPTION: {{exc}}")
            import traceback
            traceback.print_exc()

        _room_transition_pending = False

    def on_stop(self):
        """Cleanup when app stops"""
        if self.update_event:
            Clock.unschedule(self.update_event)
        return True


if __name__ == '__main__':
    try:
        GameApp().run()
    except Exception as _e:
        _log(f"FATAL: {{_e}}")
        import traceback
        _log(traceback.format_exc())
        raise
'''

        # Format the template with actual values. The name lands in a
        # double-quoted Python string literal (self.project_name = "..."),
        # so escape backslashes and quotes — a name with a '"' or trailing
        # '\' would otherwise produce invalid main.py and break the whole
        # export (KA-M1).
        first_room_class = self._get_room_class_name(first_room)
        project_name_literal = project_name.replace('\\', '\\\\').replace('"', '\\"')
        code_formatted = code.format(
            room_width=room_width,
            room_height=room_height,
            room_imports_str=room_imports_str,
            room_list_str=room_list_str,
            room_mapping_str=room_mapping_str,
            room_meta_str=room_meta_str,
            project_name=project_name_literal,
            first_room_class=first_room_class,
            needs_dpad=self._project_uses_keyboard(),
            needs_map_button=self._project_binds_key('m')
        )

        output_file = self.output_path / "game" / "main.py"
        output_file.write_text(code_formatted, encoding="utf-8")

    def _project_binds_key(self, key_name: str) -> bool:
        """True if any object has a keyboard-family event bound to key_name.

        Drives whether the exported Android build shows the optional map
        button, so an ordinary keyboard game doesn't grow a mystery control.
        """
        wanted = str(key_name).lower()
        for obj_data in self.project_data.get('assets', {}).get('objects', {}).values():
            if not isinstance(obj_data, dict):
                continue
            events = obj_data.get('events', {})
            if not isinstance(events, dict):
                continue
            for name, data in events.items():
                if not str(name).startswith('keyboard'):
                    continue
                if isinstance(data, dict):
                    for sub in data.keys():
                        if str(sub).lower() == wanted:
                            return True
        return False

    def _project_uses_keyboard(self) -> bool:
        """True if any object has a keyboard-family event (drives whether
        the exported Android build shows the virtual D-pad overlay)."""
        for obj_data in self.project_data.get('assets', {}).get('objects', {}).values():
            if not isinstance(obj_data, dict):
                continue
            events = obj_data.get('events', {})
            if isinstance(events, dict):
                keys = events.keys()
            elif isinstance(events, list):
                keys = [e.get('event_type', '') for e in events if isinstance(e, dict)]
            else:
                continue
            for key in keys:
                if str(key).startswith('keyboard') or str(key) == 'nokey':
                    return True
        return False

    def _generate_scenes(self):
        """Generate scene files for each room"""
        rooms = self.project_data.get('assets', {}).get('rooms', {})

        if not rooms:
            logger.warning("No rooms found in project data")
            return

        for room_name, room_data in rooms.items():
            try:
                logger.debug(f"  Generating scene: {room_name}")
                self._generate_scene(room_name, room_data)
                logger.debug(f"  Scene {room_name} generated")
            except Exception as e:
                logger.error(f"  Failed to generate scene {room_name}: {e}")
                import traceback
                traceback.print_exc()

    EXTENSION_SCENE_MARKER = "    # __PYGM_EXTENSION_SCENE_CODE__"

    def _inject_extension_scene_code(self, scene_code: str) -> str:
        """Replace the scene's extension marker with each enabled extension's
        contributed class-body code (Stage C).

        Done AFTER ``.format()`` so the injected Python — which contains its own
        ``{ }`` dict literals — needs no brace-doubling. The raycast renderer
        ships from ``extensions/raycast_2_5d/export_kivy.py``; the scene template
        itself names no extension.
        """
        return scene_code.replace(self.EXTENSION_SCENE_MARKER,
                                  self._collect_extension_scene_code())

    EXTENSION_BASE_MARKER = "    # __PYGM_EXTENSION_BASE_CODE__"

    def _inject_extension_base_code(self, base_code: str) -> str:
        """Replace base_object.py's extension marker with each enabled
        extension's contributed base-class methods (Stage C2c). Post-.format(),
        so injected { } dict/set literals need no brace-doubling."""
        return base_code.replace(self.EXTENSION_BASE_MARKER,
                                 self._collect_extension_base_code())

    def _collect_extension_base_code(self) -> str:
        """The base-object class-body code every ENABLED extension contributes
        via export_kivy.py's BASE_OBJECT_CODE string (Stage C2c)."""
        return self._collect_extension_code("BASE_OBJECT_CODE")

    def _collect_extension_scene_code(self) -> str:
        """The scene class-body code every ENABLED extension contributes (Stage
        C). An extension ships an ``export_kivy.py`` exposing ``SCENE_CODE`` — a
        string of 4-space-indented methods injected verbatim at the marker."""
        return self._collect_extension_code("SCENE_CODE")

    def _collect_extension_code(self, symbol: str) -> str:
        """Concatenate ``symbol`` (a class-body-code string) from every ENABLED
        extension's ``export_kivy.py`` (Stage C). Shared by the scene and
        base-object injectors; the loader's enable/disable config is honoured.
        """
        try:
            from events.plugin_loader import (
                list_available_extensions, get_extension_directory)
            ext_dir = get_extension_directory()
            parts = []
            for info in list_available_extensions():
                if not info.get("enabled", True):
                    continue
                py = ext_dir / info["folder"] / "export_kivy.py"
                if py.exists():
                    ns = {}
                    exec(compile(py.read_text(encoding="utf-8"), str(py), "exec"), ns)
                    code = ns.get(symbol, "")
                    if code:
                        parts.append(code)
            return "\n".join(parts)
        except Exception as exc:   # never let extension collection break export
            logger.warning(f"Could not collect extension Kivy {symbol}: {exc}")
            return ""

    def _generate_scene(self, room_name: str, room_data: Dict):
        """Generate a single scene file"""
        class_name = self._get_room_class_name(room_name)

        # Get room properties (clamped — a 0/negative dim would divide-by-
        # zero in the Android scaler, KA-L2)
        width = self._safe_room_dim(room_data.get('width'), 1024)
        height = self._safe_room_dim(room_data.get('height'), 768)
        instances = room_data.get('instances', [])

        # Get background properties
        bg_color = room_data.get('background_color', '#808080')  # Default gray
        bg_image = room_data.get('background', '') or room_data.get('background_image', '')

        # Resolve the background's actual exported filename. _export_background
        # copies the file to <asset_name><ext> (name-keyed — see
        # _exported_asset_filename), so hardcoding "<asset>.png" missed any
        # non-PNG background and the room rendered without it (L22). Fall back to
        # "<name>.png" for legacy data with no file_path.
        bg_filename = ''
        if bg_image:
            bg_meta = self.project_data.get('assets', {}).get('backgrounds', {}).get(bg_image, {})
            bg_fp = bg_meta.get('file_path', '')
            bg_filename = _exported_asset_filename(bg_image, bg_fp) if bg_fp else f"{bg_image}.png"

        # Convert hex string or [r, g, b, a] list to RGB floats (0-1 range)
        r, g, b = _bg_color_to_rgb(bg_color)

        # Camera / views config baked into the scene (single-view follow).
        views_enabled = bool(room_data.get('views_enabled',
                                           room_data.get('enable_views', False)))
        views_raw = room_data.get('views', {})
        if not isinstance(views_raw, dict):
            views_raw = {}
        views_list = []
        for vi in range(8):
            vd = views_raw.get(f'view_{vi}', {})
            if not isinstance(vd, dict):
                vd = {}
            vw_ = int(vd.get('view_w', width) or width)
            vh_ = int(vd.get('view_h', height) or height)
            views_list.append({
                'visible': bool(vd.get('visible', vi == 0)),
                'view_x': int(vd.get('view_x', 0) or 0),
                'view_y': int(vd.get('view_y', 0) or 0),
                'view_w': vw_,
                'view_h': vh_,
                'port_x': int(vd.get('port_x', 0) or 0),
                'port_y': int(vd.get('port_y', 0) or 0),
                # A port defaults to the view size (1:1 view->screen), not the
                # room — the whole point of a view is to show a room *slice*.
                'port_w': int(vd.get('port_w', vw_) or vw_),
                'port_h': int(vd.get('port_h', vh_) or vh_),
                'follow': vd.get('follow') or None,
                'hborder': int(vd.get('hborder', 32) or 0),
                'vborder': int(vd.get('vborder', 32) or 0),
                'hspeed': int(vd.get('hspeed', -1)),
                'vspeed': int(vd.get('vspeed', -1)),
            })
        views_repr = repr(views_list)

        # Window/port size for a views room: the display surface is the game
        # WINDOW (a slice of the larger room), not the room. Prefer the project
        # window settings; fall back to view 0's port, then the room size.
        settings = self.project_data.get('settings', {})
        v0 = views_list[0]
        window_width = int(settings.get('window_width') or v0['port_w'] or width)
        window_height = int(settings.get('window_height') or v0['port_h'] or height)

        # Import ALL project objects (not just room-placed ones) so
        # create_instance can dynamically create any object type (e.g., obj_box_store)
        all_objects = self.project_data.get('assets', {}).get('objects', {})
        object_imports = set(all_objects.keys())

        logger.debug(f"    Room has {len(instances)} instances")
        if instances and len(instances) > 0:
            # Debug: show structure of first instance
            first_inst = instances[0]
            logger.debug(f"    First instance keys: {list(first_inst.keys()) if isinstance(first_inst, dict) else 'not a dict'}")
            logger.debug(f"    First instance sample: {first_inst}")

        for instance in instances:
            # Try multiple possible key names for object type
            obj_type = (instance.get('object_type') or
                       instance.get('object_name') or
                       instance.get('type') or
                       instance.get('object') or
                       instance.get('obj_type') or
                       '')

            if obj_type:
                object_imports.add(obj_type)
                logger.debug(f"      Found object type: {obj_type}")

        logger.debug(f"    Total unique object types: {len(object_imports)}")

        import_lines = '\n'.join([
            f"from objects.{self._get_object_module_name(obj)} import {self._get_object_class_name(obj)}"
            for obj in sorted(object_imports)
        ])

        # Generate instance creation code
        instance_code = []
        for i, instance in enumerate(instances):
            # Try multiple possible key names for object type
            obj_type = (instance.get('object_type') or
                       instance.get('object_name') or
                       instance.get('type') or
                       instance.get('object') or
                       instance.get('obj_type') or
                       '')
            x = instance.get('x', 0)
            y_gamemaker = instance.get('y', 0)

            # KIVY COORDINATE FIX: Flip Y-axis for room layout
            # GameMaker: Y=0 at top, increases downward, position is sprite origin (usually top-left)
            # Kivy: Y=0 at bottom, increases upward, position is bottom-left corner
            # Formula: y_kivy = room_height - y_gamemaker - sprite_height
            # Use grid_size as the object height for coordinate conversion
            y = height - y_gamemaker - self.grid_size

            if obj_type:
                class_name_obj = self._get_object_class_name(obj_type)
                instance_code.append(
                    f"        inst_{i} = {class_name_obj}(self, {x}, {y})"
                )
                instance_code.append(
                    f"        self.add_instance(inst_{i})"
                )

        instances_init = '\n'.join(instance_code) if instance_code else "        pass"

        # Get tiling properties
        tile_horizontal = room_data.get('tile_horizontal', False)
        tile_vertical = room_data.get('tile_vertical', False)

        # Generate background image loading code (if background image is set).
        # Emitted as the body of _draw_bg_image(self) (8-space method indent) so
        # the same instructions can render into either the legacy canvas.before
        # context (non-views rooms) or the multi-view Fbo (views rooms).
        if bg_image:
            if tile_horizontal or tile_vertical:
                # Generate tiled background code
                bg_image_body = f'''\
        # Load and draw tiled background image
        Color(1, 1, 1, 1)  # Reset color to white for untinted textures
        bg_img = load_image('assets/images/{bg_filename}')
        if bg_img:
            # Tile the background
            tex = bg_img.texture
            tex_width = tex.width
            tex_height = tex.height
            tile_h = {tile_horizontal}
            tile_v = {tile_vertical}

            # Calculate how many tiles we need
            cols = int(self.room_width / tex_width) + 1 if tile_h else 1
            rows = int(self.room_height / tex_height) + 1 if tile_v else 1

            # Draw tiles
            for row in range(rows):
                for col in range(cols):
                    x = col * tex_width
                    y = row * tex_height
                    # Only draw if at least partially visible
                    if x < self.room_width and y < self.room_height:
                        Rectangle(texture=tex, pos=(x, y), size=(tex_width, tex_height))'''
            else:
                bg_image_body = f'''\
        # Load and draw background image (stretched to fit)
        Color(1, 1, 1, 1)  # Reset color to white for untinted textures
        bg_img = load_image('assets/images/{bg_filename}')
        if bg_img:
            Rectangle(texture=bg_img.texture, pos=(0, 0), size=(self.room_width, self.room_height))'''
        else:
            bg_image_body = "        pass  # No background image"

        # Generate object class registry for dynamic instance creation
        registry_entries = ', '.join([
            f'"{obj}": {self._get_object_class_name(obj)}'
            for obj in sorted(object_imports)
        ])
        object_registry = f"_object_classes = {{{registry_entries}}}"

        code = '''#!/usr/bin/env python3
"""
Scene: {room_name}
Generated from PyGameMaker IDE
"""

from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, PushMatrix, PopMatrix
from kivy.graphics import Translate as TranslateInstr
from kivy.graphics import Fbo, ClearColor, ClearBuffers, InstructionGroup
from kivy.core.window import Window
from utils import load_image

try:
    from asset_paths import SPRITE_PATHS
except ImportError:
    SPRITE_PATHS = {{}}

# Import object types
{import_lines}

# Object class registry for dynamic instance creation
{object_registry}


class {class_name}(Widget):
    """Game scene for {room_name}"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.room_width = {width}
        self.room_height = {height}
        self.instances = []
        self.instances_to_destroy = []
        self._pending_creates = []

        # Camera / views (GameMaker-style large-level scrolling + multi-view).
        # view_x/view_y hold the live camera position in Kivy space (y-up).
        self.views_enabled = {views_enabled}
        self.views = {views_repr}
        self._cam_translate = None
        # Extensions may add per-scene state and an opaque overlay renderer
        # (e.g. the raycast 2.5D first-person view). _init_extensions is a
        # no-op unless an extension injects it (Stage C); _extension_hud_group
        # is the generic screen-space HUD group composited over any such overlay.
        self._extension_hud_group = None
        self._init_extensions()
        # Displayed surface: for a views room it's the game WINDOW (a slice of
        # the larger room); otherwise it's the room itself. The exporter sizes
        # the OS window / Android fit-scale to this via scene.display_width/height.
        self.window_width = {window_width}
        self.window_height = {window_height}
        if self.views_enabled:
            self.display_width, self.display_height = self.window_width, self.window_height
        else:
            self.display_width, self.display_height = self.room_width, self.room_height

        # Multi-view render target. The whole room is drawn ONCE into an Fbo
        # (offscreen texture); each visible view then blits its room region
        # (view_x/y/w/h) into its screen port with tex_coords. Two viewports
        # (e.g. main + minimap) can therefore show the same room at once —
        # impossible with a single scene transform. Non-views rooms keep the
        # original child-widget path completely untouched.
        self._fbo = None
        self._view_group = None
        if self.views_enabled:
            self.size = (self.display_width, self.display_height)
            self._fbo = Fbo(size=(self.room_width, self.room_height),
                            with_stencilbuffer=True)
            with self._fbo:
                self._fbo_clear = ClearColor({bg_r:.3f}, {bg_g:.3f}, {bg_b:.3f}, 1)
                ClearBuffers()
                self._draw_bg_image()
            self.canvas.add(self._fbo)
            self._view_group = InstructionGroup()
            self.canvas.add(self._view_group)

        # Keyboard state tracking
        self.keys_pressed = {{}}

        # Draw background (child-widget path only; the views path drew it into
        # the Fbo above)
        if not self.views_enabled:
            self._draw_background()

        # Bind keyboard events
        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_key_up=self.on_keyboard_up)

        # Initialize room
        self.create_instances()

        # First camera placement + port blit so frame 0 is already correct.
        if self.views_enabled:
            self.update_views()
            self._render_views()

        # First extension-overlay frame (a create event may have enabled it
        # during create_instances), so frame 0 already shows it.
        self._render_extension_overlay()

    def _draw_background(self):
        """Draw the room background color + image under the camera transform.

        Non-views path only. PushMatrix + a Translate (updated each frame by
        update_views) open the camera in canvas.before; PopMatrix in
        canvas.after closes it. When views are disabled the Translate stays at
        (0, 0, 0), so rendering is identical to the pre-camera exporter.
        """
        with self.canvas.before:
            PushMatrix()
            self._cam_translate = TranslateInstr(0, 0, 0)
            # Background color: RGB = ({bg_r:.3f}, {bg_g:.3f}, {bg_b:.3f})
            self._bg_color_instr = Color({bg_r:.3f}, {bg_g:.3f}, {bg_b:.3f}, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=(self.room_width, self.room_height))
            self._draw_bg_image()
        with self.canvas.after:
            PopMatrix()

    def _draw_bg_image(self):
        """Draw the room background image (if any) into the active canvas/Fbo.

        Called inside a `with self.canvas.before:` (non-views) or `with self._fbo:`
        (views) block, so the instructions land in whichever is active.
        """
{bg_image_body}

    def _render_views(self):
        """Blit each visible view's room region into its screen port.

        The Fbo texture holds the whole room; for each visible view we draw one
        textured Rectangle at the port (port_x/y/w/h), sampling the room region
        (view_x/y/w/h) via normalized tex_coords. A minimap is just a view whose
        view_w/h span the whole room drawn into a small port. No-op when views
        are disabled.
        """
        if not self.views_enabled or self._fbo is None:
            return
        tex = self._fbo.texture
        rw = float(self.room_width) or 1.0
        rh = float(self.room_height) or 1.0
        self._view_group.clear()
        self._view_group.add(Color(1, 1, 1, 1))
        for view in self.views:
            if not view.get('visible'):
                continue
            vx, vy = float(view['view_x']), float(view['view_y'])
            vw, vh = float(view['view_w']), float(view['view_h'])
            u0, u1 = vx / rw, (vx + vw) / rw
            v0, v1 = vy / rh, (vy + vh) / rh
            tc = (u0, v0, u1, v0, u1, v1, u0, v1)
            self._view_group.add(Rectangle(
                texture=tex,
                pos=(int(view.get('port_x', 0)), int(view.get('port_y', 0))),
                size=(int(view['port_w']), int(view['port_h'])),
                tex_coords=tc))

    def set_views_enabled(self, flag):
        """Runtime enable_views action. Flips the flag; the multi-view render
        needs the Fbo built at construction (baked views_enabled), so enabling
        views on a room that started without them won't retro-fit the camera —
        set views_enabled in the room config for the camera to render."""
        self.views_enabled = bool(flag)

    def apply_set_view(self, index, updates):
        """Runtime set_view action: patch view `index`'s fields and re-blit.
        Reconfiguring a view (follow target, borders, region, port) works live
        when views are enabled; unknown/out-of-range indices are ignored."""
        if 0 <= index < len(self.views):
            self.views[index].update(updates)
            self._render_views()

    # Extension hooks (Stage C). Defaults are no-ops; the raycast extension
    # injects overriding _init_extensions / _render_extension_overlay and its
    # render methods at the __PYGM_EXTENSION_SCENE_CODE__ marker below.
    def _init_extensions(self):
        pass

    def _render_extension_overlay(self):
        return False

    # __PYGM_EXTENSION_SCENE_CODE__

    def _class_name_to_snake_case(self, name):
        """Convert PascalCase class name to snake_case for collision events"""
        # ObjWall -> obj_wall, ObjPlayer -> obj_player
        import re
        # Insert underscore before uppercase letters (except first)
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\\1_\\2', name)
        # Insert underscore before uppercase letters preceded by lowercase
        return re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', s1).lower()

    def create_instances(self):
        """Create all instances in the room"""
{instances_init}
        # Call on_create for all room-placed instances after they are all added
        for inst in self.instances:
            if hasattr(inst, 'on_create'):
                inst.on_create()

    def add_instance(self, instance):
        """Add an instance to the room.

        Views rooms render every instance into the Fbo (so the per-view blits
        pick them up), so the instance's canvas is attached to the Fbo rather
        than added as a child widget. Non-views rooms use the child-widget path.
        """
        self.instances.append(instance)
        depth = getattr(instance, 'depth', 0)
        if self.views_enabled and self._fbo is not None:
            # Fbo children render in ADD order: first added is drawn first
            # (furthest back). GameMaker wants highest depth first, so insert
            # after every already-added instance with a greater depth.
            idx = sum(1 for inst in self.instances
                      if inst is not instance and getattr(inst, 'depth', 0) > depth)
            try:
                self._fbo.insert(idx, instance.canvas)
            except Exception:
                self._fbo.add(instance.canvas)   # older Kivy: no insert()
        else:
            # Kivy draws `children` in REVERSE: children[0] is drawn LAST, i.e.
            # on top. GameMaker wants the LOWEST depth in front, so keep
            # `children` sorted ASCENDING by depth and insert at the first
            # child whose depth is >= ours. Equal depths: the newer instance
            # lands in front of older ones, matching the desktop runtime's
            # stable descending sort.
            idx = len(self.children)
            for i, child in enumerate(self.children):
                if getattr(child, 'depth', 0) >= depth:
                    idx = i
                    break
            self.add_widget(instance, index=idx)

    def remove_instance(self, instance):
        """Remove an instance from the room"""
        if instance in self.instances:
            self.instances.remove(instance)
            if self.views_enabled and self._fbo is not None:
                self._fbo.remove(instance.canvas)
            elif instance in self.children:
                self.remove_widget(instance)

    def count_instances(self, class_name):
        """Count active instances of a given object type"""
        # Convert snake_case name to PascalCase for class name matching
        # e.g., 'obj_box' -> 'ObjBox', 'obj_box_store' -> 'ObjBoxStore'
        pascal_name = ''.join(part.capitalize() for part in class_name.split('_')) if '_' in class_name else class_name
        count = 0
        for inst in self.instances:
            # Skip instances pending destruction
            if inst in self.instances_to_destroy:
                continue
            inst_class = inst.__class__.__name__
            inst_obj = getattr(inst, 'object_name', '')
            if inst_class == class_name or inst_class == pascal_name or inst_obj == class_name:
                if not getattr(inst, '_destroyed', False):
                    count += 1
        return count

    def create_instance(self, class_name, x, y):
        """Create a new instance of the given object type at (x, y)"""
        # Look up the class by name from the global object registry
        obj_class = _object_classes.get(class_name)
        if obj_class:
            instance = obj_class(self, x, y)
            self.add_instance(instance)
            # Defer on_create until after collision cleanup so that
            # destroy_instance actions complete before the new instance
            # checks instance counts in its create event
            self._pending_creates.append(instance)
            return instance
        return None

    def _find_view_target(self, name):
        """First live instance of object `name` (snake_case or PascalCase)."""
        if not name:
            return None
        pascal = ''.join(p.capitalize() for p in name.split('_')) if '_' in name else name
        for inst in self.instances:
            if inst in self.instances_to_destroy:
                continue
            cls = inst.__class__.__name__
            if cls == name or cls == pascal or getattr(inst, 'object_name', '') == name:
                return inst
        return None

    def update_views(self):
        """GameMaker-style camera follow + clamp for EVERY visible view, in
        Kivy's y-up space (mirrors runtime/game_runner.update_views). Each view
        with a follow target does border-based follow with an optional per-axis
        speed limit, clamped to room bounds; views without a follow target keep
        their configured position (e.g. a fixed minimap). _render_views then
        blits each view's region into its port.
        """
        if not self.views_enabled:
            return
        for view in self.views:
            if not view.get('visible') or not view.get('follow'):
                continue
            target = self._find_view_target(view['follow'])
            if target is None:
                continue

            vw = int(view['view_w'])
            vh = int(view['view_h'])
            hb = int(view['hborder'])
            vb = int(view['vborder'])
            old_x = int(view['view_x'])
            old_y = int(view['view_y'])
            new_x, new_y = old_x, old_y
            tx = float(target.x)
            ty = float(target.y)

            # Horizontal border follow
            if tx < old_x + hb:
                new_x = int(tx - hb)
            elif tx > old_x + vw - hb:
                new_x = int(tx - vw + hb)
            # Vertical border follow
            if ty < old_y + vb:
                new_y = int(ty - vb)
            elif ty > old_y + vh - vb:
                new_y = int(ty - vh + vb)

            # Per-axis speed limit (-1 == unlimited)
            hsp = int(view.get('hspeed', -1))
            vsp = int(view.get('vspeed', -1))
            if hsp >= 0:
                dx = new_x - old_x
                if dx > hsp:
                    new_x = old_x + hsp
                elif dx < -hsp:
                    new_x = old_x - hsp
            if vsp >= 0:
                dy = new_y - old_y
                if dy > vsp:
                    new_y = old_y + vsp
                elif dy < -vsp:
                    new_y = old_y - vsp

            # Clamp to room bounds (if the view is smaller than the room)
            new_x = max(0, min(new_x, self.room_width - vw)) if vw < self.room_width else 0
            new_y = max(0, min(new_y, self.room_height - vh)) if vh < self.room_height else 0

            view['view_x'] = new_x
            view['view_y'] = new_y

    def update(self, dt):
        """Main game loop update - GAMEMAKER 7.0 EVENT ORDER"""
        try:
            self._update_impl(dt)
        except Exception as exc:
            import traceback
            print(f"[ERROR] update: {{exc}}")
            traceback.print_exc()

    def _update_impl(self, dt):
        """Internal update (separated for error handling)"""
        # GAMEMAKER 7.0 EVENT EXECUTION ORDER:
        # 1. Begin Step events
        # 2. Alarm events
        # 3. Keyboard, Key press, Key release (handled by Kivy elsewhere)
        # 4. Mouse events (handled by Kivy elsewhere)
        # 5. Normal Step events
        # 6. (Instances move to new positions)
        # 7. Collision events
        # 8. End Step events
        # 9. Draw events (handled by Kivy rendering)

        # Snapshot the instance list so that room switches or instance
        # creation/destruction during callbacks don't mutate the list
        # while we iterate it.
        _live = list(self.instances)

        # 1. BEGIN STEP EVENTS
        for instance in _live:
            if hasattr(instance, 'on_begin_step'):
                instance.on_begin_step(dt)

        # 2. ALARM EVENTS (process countdown timers)
        for instance in _live:
            if hasattr(instance, '_process_alarms'):
                instance._process_alarms()

        # 3. KEYBOARD EVENTS
        # Check for "nokey" event - triggers when no keys are pressed
        if not self.keys_pressed:
            for instance in _live:
                if hasattr(instance, 'on_nokey'):
                    instance.on_nokey()

        # 4. NORMAL STEP EVENTS
        for instance in _live:
            if hasattr(instance, 'on_update'):
                instance.on_update(dt)

        # 5. MOVEMENT - instances move to new positions
        for instance in _live:
            if hasattr(instance, '_process_movement'):
                instance._process_movement(dt)

        # 6. COLLISION EVENTS
        # PERFORMANCE FIX: OPTIMIZED O(n^2/2) collision detection
        # Check each pair of objects only ONCE instead of twice
        # Track which types each instance is colliding with (for negated collision events)
        colliding_with = {{}}  # instance id -> set of snake_case class names
        _live = list(self.instances)
        num_instances = len(_live)
        for i in range(num_instances):
            instance = _live[i]

            # Only check against instances we haven't checked yet (j > i)
            # This prevents checking A->B and then B->A (duplicate work)
            for j in range(i + 1, num_instances):
                other = _live[j]

                # Check collision between instance and other
                if instance.check_collision(other):
                    instance._collision_other = other
                    other._collision_other = instance

                    # Track collision types for negated collision detection
                    other_class_snake = self._class_name_to_snake_case(other.__class__.__name__)
                    instance_class_snake = self._class_name_to_snake_case(instance.__class__.__name__)
                    colliding_with.setdefault(id(instance), set()).add(other_class_snake)
                    colliding_with.setdefault(id(other), set()).add(instance_class_snake)

                    # Call collision event on BOTH objects (reciprocal events)
                    instance_event = f"on_collision_{{other_class_snake}}"
                    if hasattr(instance, instance_event):
                        getattr(instance, instance_event)(other)

                    # Also notify the other object
                    other_event = f"on_collision_{{instance_class_snake}}"
                    if hasattr(other, other_event):
                        getattr(other, other_event)(instance)

        # 6b. NEGATED COLLISION EVENTS
        # Fire on_not_collision_* events when an instance is NOT colliding with a target type
        # Skip instances created during this frame since they weren't part of
        # positive collision detection and would falsely trigger
        pending_ids = set(id(inst) for inst in self._pending_creates)
        for instance in _live:
            if id(instance) in pending_ids:
                continue
            for attr_name in dir(instance):
                if attr_name.startswith('on_not_collision_'):
                    target_type = attr_name.replace('on_not_collision_', '')
                    instance_collisions = colliding_with.get(id(instance), set())
                    if target_type not in instance_collisions:
                        getattr(instance, attr_name)()

        # 7. END STEP EVENTS
        for instance in _live:
            if hasattr(instance, 'on_end_step'):
                instance.on_end_step(dt)

        # 7b. SOUND QUEUE DRAIN - plays anything execute_code queued via
        # self._sound_queue.append(...) this frame (create/step/mouse/
        # collision/keyboard, not just draw), unconditionally so it works
        # for objects with no draw event too.
        for instance in _live:
            instance._drain_sound_queue()

        # 7c. CAMERA - follow/clamp every visible view, then re-blit each view's
        # room region into its screen port (the Fbo already holds the room).
        self.update_views()
        self._render_views()

        # 7d. EXTENSION OVERLAY - an extension (e.g. the raycast 2.5D view) may
        # draw an opaque first-person overlay over the top-down widgets. The
        # return value gates the screen-space HUD compositing in step 8.
        _overlay_on = self._render_extension_overlay()

        # 8. DRAW EVENTS - sprites render via each widget's canvas; the
        # GameMaker draw event renders through the per-instance draw queue
        # (room coordinates, y-down — see GameObject._render_draw_queue)
        #
        # Depth order: higher depth draws FIRST (further back), so a lower
        # depth ends up in front — descending, matching the desktop runtime
        # and engine.js. Until 2026-07-20 this ran in instance-creation order
        # (the exporter ignored `depth` entirely).
        #
        # Visibility: GameMaker does not run an invisible instance's draw
        # event at all. The desktop runtime gets this from render()'s early
        # return; this loop used to run it regardless.
        #
        # Extension overlay: the overlay above (e.g. the raycast view) is OPAQUE
        # and lives on the scene's canvas.after, which paints over every child
        # widget — so a HUD rendered through the per-instance _dq_group (a child
        # widget's canvas) would be invisible. When an overlay drew, the draw
        # queue is instead rendered into a scene-level group added AFTER the
        # overlay, and flipped against the WINDOW height rather than the room
        # height, because a HUD is screen-space. See docs/RAYCAST_HUD_PLAN.md.
        _hud = None
        if _overlay_on:
            if getattr(self, '_extension_hud_group', None) is None:
                self._extension_hud_group = InstructionGroup()
                # Added after the overlay group, so it paints on top of the
                # opaque first-person frame.
                self.canvas.after.add(self._extension_hud_group)
            _hud = self._extension_hud_group
            _hud.clear()
        elif getattr(self, '_extension_hud_group', None) is not None:
            self._extension_hud_group.clear()

        for instance in sorted(_live, key=lambda i: getattr(i, 'depth', 0), reverse=True):
            if getattr(instance, 'visible', True) and hasattr(instance, 'on_draw'):
                instance._draw_queue = []
                instance.on_draw(dt)
                if _hud is not None:
                    for cmd in instance._draw_queue:
                        try:
                            instance._dq_render_cmd(_hud, cmd,
                                                    float(self.display_height))
                        except Exception as exc:
                            print(f"[ERROR] extension HUD {{cmd.get('type')}}: {{exc}}")
                    instance._draw_queue = []
                else:
                    instance._render_draw_queue()

        # 9. CLEANUP - Remove destroyed instances
        if self.instances_to_destroy:
            for instance in self.instances_to_destroy:
                self.remove_instance(instance)
            self.instances_to_destroy.clear()

        # 10. DEFERRED CREATE EVENTS - Fire on_create for dynamically created instances
        # This runs after cleanup so that destroyed instances are gone when
        # the new instance checks instance counts (e.g., win conditions)
        if self._pending_creates:
            pending = list(self._pending_creates)
            self._pending_creates.clear()
            for instance in pending:
                if hasattr(instance, 'on_create') and not getattr(instance, '_destroyed', False):
                    instance.on_create()

    def destroy_instance(self, instance):
        """Mark instance for destruction"""
        if instance not in self.instances_to_destroy:
            self.instances_to_destroy.append(instance)

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Handle keyboard press events"""
        # Ignore if this scene is no longer the active one (after room switch)
        from main import get_game_app
        _app = get_game_app()
        if _app and _app.scene is not self:
            return False
        try:
            self.keys_pressed[key] = True
            for instance in list(self.instances):
                if hasattr(instance, 'on_keyboard'):
                    instance.on_keyboard(key, scancode, codepoint, modifier)
        except Exception as exc:
            print(f"[ERROR] on_keyboard: {{exc}}")
        return False

    def on_keyboard_up(self, window, key, scancode):
        """Handle keyboard release events"""
        from main import get_game_app
        _app = get_game_app()
        if _app and _app.scene is not self:
            return False
        try:
            if key in self.keys_pressed:
                del self.keys_pressed[key]
            for instance in list(self.instances):
                if hasattr(instance, 'on_keyboard_up'):
                    instance.on_keyboard_up(key, scancode)
        except Exception as exc:
            print(f"[ERROR] on_keyboard_up: {{exc}}")
        return False

    def _touch_to_room(self, touch):
        """Convert a window touch position to room coordinates (y-down).

        On Android the scene sits inside a canvas-scaled container whose
        transform does NOT apply to touch coordinates, so it is inverted
        here. On desktop the scene fills the (possibly DPI-adjusted)
        window, so window coords are rescaled to room coords.
        """
        from main import get_game_app
        _app = get_game_app()
        x, y = touch.x, touch.y
        if _app is not None and getattr(_app, '_ctr_scale', None) is not None:
            sc = _app._ctr_scale.x or 1.0
            x = (x - _app._ctr_translate.x) / sc
            y = (y - _app._ctr_translate.y) / sc
        elif Window.width and Window.height:
            # display_width == room_width for a non-views room, so this is
            # unchanged there; for a views room it maps into window pixels.
            x = x * self.display_width / float(Window.width)
            y = y * self.display_height / float(Window.height)
        if self.views_enabled and self.views:
            # Displayed pixels are relative to the main view (view 0) port; add
            # its room-space camera origin. (Touch through a secondary port /
            # minimap is not resolved — main view only.)
            v0 = self.views[0]
            x = float(v0['view_x']) + (x - int(v0.get('port_x', 0)))
            y = float(v0['view_y']) + (y - int(v0.get('port_y', 0)))
        return x, self.room_height - y

    def on_touch_down(self, touch):
        """Dispatch a touch/click as the GameMaker left-mouse press event.

        Matches the IDE runtime: the event fires on EVERY instance that
        has it (no hit-test), with mouse_x/mouse_y set in room coords.
        """
        if super().on_touch_down(touch):
            return True
        from main import get_game_app
        _app = get_game_app()
        if _app is not None and _app.scene is not self:
            return False
        mx, my = self._touch_to_room(touch)
        for instance in list(self.instances):
            if hasattr(instance, 'on_mouse_left_press'):
                instance.mouse_x = mx
                instance.mouse_y = my
                try:
                    instance.on_mouse_left_press()
                except Exception as exc:
                    print(f"[ERROR] on_mouse_left_press: {{exc}}")
        return False

    def on_touch_up(self, touch):
        """Dispatch touch release as the GameMaker left-mouse release event."""
        if super().on_touch_up(touch):
            return True
        from main import get_game_app
        _app = get_game_app()
        if _app is not None and _app.scene is not self:
            return False
        mx, my = self._touch_to_room(touch)
        for instance in list(self.instances):
            if hasattr(instance, 'on_mouse_left_release'):
                instance.mouse_x = mx
                instance.mouse_y = my
                try:
                    instance.on_mouse_left_release()
                except Exception as exc:
                    print(f"[ERROR] on_mouse_left_release: {{exc}}")
        return False
'''

        # Format the template with actual values
        code_formatted = code.format(
            room_name=room_name,
            class_name=class_name,
            width=width,
            height=height,
            views_enabled=views_enabled,
            views_repr=views_repr,
            window_width=window_width,
            window_height=window_height,
            import_lines=import_lines,
            object_registry=object_registry,
            instances_init=instances_init,
            bg_r=r,
            bg_g=g,
            bg_b=b,
            bg_image_body=bg_image_body
        )
        code_formatted = self._inject_extension_scene_code(code_formatted)

        output_file = (self.output_path / "game" / "scenes" /
                       f"{self._get_room_module_name(room_name)}.py")
        output_file.write_text(code_formatted, encoding="utf-8")

    def _generate_objects(self):
        """Generate object class files"""
        # First generate base object class
        try:
            logger.debug("  Generating base object class...")
            self._generate_base_object()
            logger.debug("  Base object generated")
        except Exception as e:
            logger.error(f"  CRITICAL ERROR: Failed to generate base object: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to generate base object class: {e}")

        # Then generate specific object types
        objects = self.project_data.get('assets', {}).get('objects', {})

        if not objects:
            logger.warning("  No objects found in project data")
            return

        # Scan all collision events to detect which objects are pushable
        # An object is pushable if another object has an if_can_push collision event targeting it
        pushable_objects = set()
        for obj_name, obj_data in objects.items():
            events = obj_data.get('events', {})
            if isinstance(events, dict):
                for event_key, event_data in events.items():
                    if event_key.startswith('collision_with_') and isinstance(event_data, dict):
                        target = event_data.get('target_object', event_key.replace('collision_with_', ''))
                        actions = event_data.get('actions', [])
                        for action in actions:
                            if isinstance(action, dict) and action.get('action') == 'if_can_push':
                                pushable_objects.add(target)
        if pushable_objects:
            logger.debug(f"  Detected pushable objects: {pushable_objects}")

        failed_objects = []
        for obj_name, obj_data in objects.items():
            try:
                logger.debug(f"  Generating object: {obj_name}")
                self._generate_object(obj_name, obj_data, pushable=obj_name in pushable_objects)
                logger.debug(f"  Object {obj_name} generated")
            except Exception as e:
                logger.error(f"  CRITICAL ERROR: Failed to generate object {obj_name}: {e}")
                import traceback
                traceback.print_exc()
                failed_objects.append(obj_name)

        if failed_objects:
            raise RuntimeError(f"Failed to generate {len(failed_objects)} object(s): {', '.join(failed_objects)}")

    def _generate_sprite_meta_module(self):
        """Write game/sprite_meta.py — frame metadata keyed by exported sprite
        path. base_object.set_sprite reads it to slice a single frame from a
        multi-frame strip (and to animate it). Written verbatim as a JSON-ish
        dict literal, so no str.format brace escaping is involved.
        """
        import json as _json
        body = _json.dumps(self.sprite_meta_map, indent=4, sort_keys=True)
        code = (
            '#!/usr/bin/env python3\n'
            '"""Sprite frame metadata (frames / per-frame size / anim speed),\n'
            'keyed by exported asset path. Generated from the project sprites."""\n\n'
            'SPRITE_META = ' + body + '\n'
        )
        (self.output_path / "game" / "sprite_meta.py").write_text(code, encoding="utf-8")

    def _generate_asset_paths_module(self):
        """Write game/asset_paths.py — sprite/sound name -> exported asset
        path lookup. Structured actions (draw_sprite, play_sound, ...) get
        their path resolved at code-generation time via sprite_path_map /
        sound_path_map; hand-authored execute_code that references an asset
        by name (self._sound_queue.append('snd_x'), a draw-queue
        {'type': 'sprite', 'sprite_name': ...} dict) has no such generation
        step, so base_object.py resolves it at runtime from this module
        instead. Written verbatim, like sprite_meta.py — no str.format brace
        escaping involved.
        """
        import json as _json
        code = (
            '#!/usr/bin/env python3\n'
            '"""Sprite/sound/background name -> exported asset path, for\n'
            'execute_code that references an asset by name rather than\n'
            'through a structured action. Generated from the project\'s\n'
            'assets."""\n\n'
            'SPRITE_PATHS = ' + _json.dumps(self.sprite_path_map, indent=4, sort_keys=True) + '\n\n'
            'SOUND_PATHS = ' + _json.dumps(self.sound_path_map, indent=4, sort_keys=True) + '\n\n'
            'BACKGROUND_PATHS = ' + _json.dumps(self.background_path_map, indent=4, sort_keys=True) + '\n'
        )
        (self.output_path / "game" / "asset_paths.py").write_text(code, encoding="utf-8")

    def _generate_highscore_module(self):
        """Write game/highscore.py — a standalone high-score table module.

        Written verbatim (NOT through str.format), so its many literal braces
        need no escaping — unlike the main.py template. main.py and the object
        modules reach it lazily via `from highscore import show_highscore`.
        """
        code = r'''#!/usr/bin/env python3
"""High-score table for the exported game.

Persists the top scores to highscores.json next to the game (or under
ANDROID_APP_PATH on Android), and shows a Kivy popup table. show_highscore()
optionally prompts for a name when the current score qualifies, mirroring the
IDE runtime's show_highscore action.
"""

import os
import json

_MAX_ENTRIES = 10
_FILE = os.path.join(os.environ.get('ANDROID_APP_PATH', '.'), 'highscores.json')


def _load():
    try:
        with open(_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [(str(e['name']), int(e['score'])) for e in data]
    except Exception:
        return []


def _save(entries):
    try:
        with open(_FILE, 'w', encoding='utf-8') as f:
            json.dump([{'name': n, 'score': s} for n, s in entries], f)
    except Exception as e:
        print('highscore save failed:', e)


def _qualifies(score, entries):
    if len(entries) < _MAX_ENTRIES:
        return True
    return bool(entries) and score > min(s for _, s in entries)


def _add(name, score):
    entries = _load()
    entries.append((name, int(score)))
    entries.sort(key=lambda e: e[1], reverse=True)
    entries = entries[:_MAX_ENTRIES]
    _save(entries)
    return entries


def clear_highscore():
    """Erase the high-score table."""
    _save([])


def _current_score():
    try:
        from main import get_score
        return int(get_score())
    except Exception:
        return 0


def _show_table(entries, new_index=-1):
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.popup import Popup

    root = BoxLayout(orientation='vertical', padding=12, spacing=6)
    root.add_widget(Label(text='[b]High Scores[/b]', markup=True,
                          size_hint_y=None, height=40))
    if entries:
        for i, (name, score) in enumerate(entries):
            color = (0.40, 0.80, 0.40, 1) if i == new_index else (0.90, 0.90, 0.90, 1)
            root.add_widget(Label(text='%d.  %s  -  %d' % (i + 1, name, score),
                                  color=color))
    else:
        root.add_widget(Label(text='(no scores yet)'))
    close_btn = Button(text='Close', size_hint_y=None, height=44)
    root.add_widget(close_btn)
    popup = Popup(title='', content=root, size_hint=(0.7, 0.85), auto_dismiss=True)
    close_btn.bind(on_release=popup.dismiss)
    popup.open()


def show_highscore(allow_new_entry=True):
    """Show the high-score table; prompt for a name first if the current
    score qualifies and allow_new_entry is True."""
    score = _current_score()
    entries = _load()
    if allow_new_entry and score > 0 and _qualifies(score, entries):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
        from kivy.uix.popup import Popup

        box = BoxLayout(orientation='vertical', padding=12, spacing=6)
        box.add_widget(Label(text='New high score: %d!\nEnter your name:' % score,
                             size_hint_y=None, height=60))
        field = TextInput(text='Player', multiline=False,
                          size_hint_y=None, height=40)
        box.add_widget(field)
        ok_btn = Button(text='OK', size_hint_y=None, height=44)
        box.add_widget(ok_btn)
        name_popup = Popup(title='', content=box, size_hint=(0.7, 0.55),
                           auto_dismiss=False)

        def _confirm(*_args):
            name = (field.text or 'Player').strip()[:20] or 'Player'
            updated = _add(name, score)
            new_index = -1
            for i, (n, s) in enumerate(updated):
                if n == name and s == int(score):
                    new_index = i
                    break
            name_popup.dismiss()
            _show_table(updated, new_index)

        ok_btn.bind(on_release=_confirm)
        name_popup.open()
    else:
        _show_table(entries)
'''
        output_file = self.output_path / "game" / "highscore.py"
        output_file.write_text(code, encoding="utf-8")

    def _generate_base_object(self):
        """Generate the base GameObject class"""
        code = '''#!/usr/bin/env python3
"""
Base GameObject class
GameMaker-style base object with movement and collision
"""

from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, Ellipse, InstructionGroup
from kivy.core.image import Image as CoreImage
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
import math
from utils import load_image

try:
    from sprite_meta import SPRITE_META
except Exception:
    SPRITE_META = {{}}

try:
    from asset_paths import SPRITE_PATHS, SOUND_PATHS, BACKGROUND_PATHS
except Exception:
    SPRITE_PATHS = {{}}
    SOUND_PATHS = {{}}
    BACKGROUND_PATHS = {{}}


class GameObject(Widget):
    """Base class for all game objects - GAMEMAKER 7.0 COMPATIBLE"""

    def __init__(self, scene, x=0, y=0, **kwargs):
        super().__init__(**kwargs)

        self.scene = scene
        # Use float for sub-pixel precision (smooth movement)
        self._x = float(x)
        self._y = float(y)

        # Movement properties (GameMaker style with bidirectional sync)
        self._hspeed = 0.0  # Horizontal speed (float for smooth movement)
        self._vspeed = 0.0  # Vertical speed (float for smooth movement)
        self._speed = 0.0   # Movement speed (magnitude)
        self._direction = 0  # Movement direction in degrees
        self._friction = 0
        self._gravity = 0
        self._gravity_direction = 270
        # Raycast (first-person) camera look direction, GM angle convention
        # (0=right, 90=up), independent of movement — see set_facing_angle /
        # enable_raycast_view and the scene's raycast render.
        self.facing_angle = 0.0

        # GAMEMAKER 7.0: 12 alarm clocks per instance
        self.alarms = [-1] * 12  # -1 = inactive, >= 0 = active countdown

        # Physics properties
        self.solid = False
        self.pushable = False

        # Sprite properties
        self.sprite_name = None
        self.image = None
        self.image_width = 0
        self.image_height = 0

        # Collision tracking
        self._collision_other = None

        # Grid properties
        self.grid_size = {grid_size}

        self.size = (self.grid_size, self.grid_size)  # Default size based on grid
        self.pos = (x, y)

        # Visibility property - invisible objects can still collide, just don't render
        self.visible = True

        # GameMaker draw depth. Higher depth is drawn FIRST (further back), so
        # a lower depth ends up in front. Subclasses override from the object's
        # own `depth`; the default keeps sort order stable for anything that
        # doesn't set one.
        self.depth = 0

        # Has sprite - objects without sprites have no collision mask
        self.has_sprite = False

        # Animation state — image_index is the current frame (float so
        # image_speed can be fractional); a single-frame sprite never animates.
        self.image_index = 0.0
        self.image_speed = 1.0
        self._sprite_frames = 1
        self._frame_w = 0
        self._frame_h = 0
        self._sprite_texture = None
        self._last_frame_drawn = -1

        # Don't draw anything here - wait for set_sprite
        self.rect = None

        # Draw-queue (GameMaker draw event) state. The draw event appends
        # command dicts in ROOM coordinates (y-down, like the IDE runtime);
        # _render_draw_queue converts and renders them each frame.
        self._draw_queue = []
        self._dq_group = None

        # Sounds queued from execute_code via self._sound_queue.append('snd_x')
        # (or {{'sound': name, 'volume': v}}). execute_code has no live `game`
        # object here to call game.sounds[...].play() on directly (unlike the
        # desktop runtime), so it queues by name instead; drained once per
        # frame by the scene's update() loop via _drain_sound_queue below.
        self._sound_queue = []

        # Mouse position in room coordinates (y-down). Set by the scene's
        # touch dispatch right before a mouse event handler runs, so
        # execute_code referencing self.mouse_x / self.mouse_y works.
        self.mouse_x = 0.0
        self.mouse_y = 0.0

    # GAMEMAKER 7.0: Bidirectional speed/direction synchronization
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = float(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = float(value)

    @property
    def hspeed(self):
        return self._hspeed

    @hspeed.setter
    def hspeed(self, value):
        self._hspeed = float(value)
        self._sync_speed_direction_from_components()

    @property
    def vspeed(self):
        return self._vspeed

    @vspeed.setter
    def vspeed(self, value):
        self._vspeed = float(value)
        self._sync_speed_direction_from_components()

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = float(value)
        self._sync_components_from_speed_direction()

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = float(value)
        self._sync_components_from_speed_direction()

    @property
    def friction(self):
        return self._friction

    @friction.setter
    def friction(self, value):
        self._friction = float(value)

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value):
        self._gravity = float(value)

    @property
    def gravity_direction(self):
        return self._gravity_direction

    @gravity_direction.setter
    def gravity_direction(self, value):
        self._gravity_direction = float(value)

    def _sync_speed_direction_from_components(self):
        """Update speed/direction when hspeed/vspeed change (GM 7.0 behavior)"""
        if self._hspeed != 0 or self._vspeed != 0:
            self._speed = math.sqrt(self._hspeed**2 + self._vspeed**2)
            self._direction = math.degrees(math.atan2(-self._vspeed, self._hspeed))
        else:
            self._speed = 0

    def _sync_components_from_speed_direction(self):
        """Update hspeed/vspeed when speed/direction change (GM 7.0 behavior)"""
        if self._speed != 0:
            rad = math.radians(self._direction)
            self._hspeed = self._speed * math.cos(rad)
            self._vspeed = -self._speed * math.sin(rad)
        else:
            self._hspeed = 0
            self._vspeed = 0

    def set_sprite(self, sprite_path):
        """Set the object's sprite - enables collision detection.

        Multi-frame strips (an N-frame animation packed as one wide PNG) are
        sliced to a single frame via the texture region; a single frame is
        drawn from the current image_index and animated by _advance_animation.
        Without this the whole sheet blitted at once (all frames visible).
        """
        self.sprite_name = sprite_path
        img = load_image(sprite_path)

        if img:
            self.image = img
            meta = SPRITE_META.get(sprite_path, {{}})
            frames = max(1, int(meta.get('frames', 1) or 1))
            fw = int(meta.get('frame_width') or 0) or img.width
            fh = int(meta.get('frame_height') or 0) or img.height
            self._sprite_frames = frames
            self._frame_w = fw
            self._frame_h = fh
            self._sprite_texture = img.texture
            self.image_speed = float(meta.get('speed', 1.0) or 1.0)
            self.image_width = fw
            self.image_height = fh
            self.size = (fw, fh)
            self.has_sprite = True  # Object has a sprite, can collide
            if self.image_index >= frames:
                self.image_index = 0.0

            # Only draw if visible (invisible objects can still collide)
            if self.visible:
                self._redraw_frame(int(self.image_index) % frames)
            else:
                # Invisible but still has collision - don't draw anything
                self.canvas.clear()
                self.rect = None

    def _redraw_frame(self, frame):
        """(Re)build the draw rectangle for frame index ``frame``."""
        if not self._sprite_texture:
            return
        if self._sprite_frames > 1:
            texture = self._sprite_texture.get_region(
                frame * self._frame_w, 0, self._frame_w, self._frame_h)
        else:
            texture = self._sprite_texture
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(texture=texture, pos=self.pos, size=self.size)
        self._last_frame_drawn = frame

    def _advance_animation(self, dt):
        """Advance the sprite animation; redraw only when the frame changes.

        Wrapping past the last frame fires the animation_end event
        (on_animation_end), matching the IDE runtime's GameInstance.step.
        The advance runs even while invisible (parity); only the redraw
        is gated on visibility.
        """
        if self._sprite_frames <= 1:
            return
        if self.image_speed:
            self.image_index += self.image_speed * dt
            if self.image_index >= self._sprite_frames or self.image_index < 0:
                self.image_index = self.image_index % self._sprite_frames
                if hasattr(self, 'on_animation_end'):
                    try:
                        self.on_animation_end()
                    except Exception as exc:
                        print(f"[ERROR] on_animation_end: {{exc}}")
        if not self.visible:
            return
        frame = int(self.image_index) % self._sprite_frames
        if frame != self._last_frame_drawn:
            self._redraw_frame(frame)

    def _process_alarms(self):
        """Process alarm clocks (GAMEMAKER 7.0 feature)"""
        for i in range(12):
            if self.alarms[i] > 0:
                self.alarms[i] -= 1
                if self.alarms[i] == 0:
                    self.alarms[i] = -1  # Deactivate alarm
                    # Trigger alarm event
                    event_name = f"on_alarm_{{i}}"
                    if hasattr(self, event_name):
                        getattr(self, event_name)()

    def _process_movement(self, dt=1.0/60.0):
        """Process movement (called each frame) - GAMEMAKER 7.0 COMPATIBLE"""
        # FIXED: Now uses dt for frame-independent movement
        # speeds are in pixels per frame at 60 FPS, scaled by dt
        # This ensures consistent speed regardless of actual frame rate

        # Advance sprite animation (no-op for single-frame sprites). Runs each
        # frame for every live instance via the scene's per-instance call.
        self._advance_animation(dt)

        # NOTE: speed/direction are now auto-synced with hspeed/vspeed via properties
        # No manual sync needed!

        # Apply gravity (GM 7.0: adds to speed each step)
        if self._gravity != 0:
            grav_rad = math.radians(self._gravity_direction)
            # Directly modify internal values to avoid triggering sync multiple times
            self._hspeed += self._gravity * math.cos(grav_rad)
            self._vspeed += -self._gravity * math.sin(grav_rad)
            # Sync once after both changes
            self._sync_speed_direction_from_components()

        # Apply friction (GM 7.0: reduces speed towards zero)
        if self._friction != 0:
            if abs(self._hspeed) > self._friction:
                self._hspeed -= self._friction if self._hspeed > 0 else -self._friction
            else:
                self._hspeed = 0.0

            if abs(self._vspeed) > self._friction:
                self._vspeed -= self._friction if self._vspeed > 0 else -self._friction
            else:
                self._vspeed = 0.0
            # Sync after friction application
            self._sync_speed_direction_from_components()

        # Only move if there's actual speed
        if self._hspeed == 0 and self._vspeed == 0:
            return

        # MOVEMENT FIX: Scale movement by dt for frame-independence
        # speeds are in pixels/frame at 60 FPS, so scale by (dt * 60)
        # This makes movement consistent regardless of actual frame rate
        speed_factor = dt * 60.0 if dt > 0 else 1.0
        new_x = self._x + float(self._hspeed * speed_factor)
        new_y = self._y + float(self._vspeed * speed_factor)

        # PERFORMANCE FIX: Optimized solid collision checking
        # Only check solid-to-solid collisions to prevent overlap
        # Other collision events are handled by _check_collisions method
        can_move = True
        if self.solid and self.scene:
            old_x, old_y = self.x, self.y
            self.x, self.y = new_x, new_y

            # Only check against other solid objects (much smaller set)
            for other in self.scene.instances:
                if other != self and other.solid and self.check_collision(other):
                    can_move = False
                    break

            if not can_move:
                self.x, self.y = old_x, old_y
            else:
                self._update_position()
        else:
            self.x = new_x
            self.y = new_y
            self._update_position()

    def _update_position(self):
        """Update visual position with sub-pixel precision for smooth rendering"""
        # PERFORMANCE FIX: Keep float precision for smooth movement
        self.pos = (float(self.x), float(self.y))
        if self.rect is not None:
            self.rect.pos = self.pos
            # PERFORMANCE FIX: Removed canvas.ask_update() - Kivy auto-updates on property changes
            # Calling ask_update() every frame for every object was causing major slowdowns

    def check_collision(self, other):
        """Check AABB (Axis-Aligned Bounding Box) collision with another object

        PERFORMANCE: This is a fast rectangular collision check.
        Returns True if this object overlaps with the other object.

        GameMaker behavior:
        - Objects without sprites have no collision mask (no collisions)
        - Invisible objects WITH sprites can still collide
        """
        # No collision if either object has no sprite (no collision mask)
        if not self.has_sprite or not other.has_sprite:
            return False

        return (
            self.x < other.x + other.size[0] and
            self.x + self.size[0] > other.x and
            self.y < other.y + other.size[1] and
            self.y + self.size[1] > other.y
        )

    def check_collision_at(self, x, y, object_name=None):
        """Return True if this object would collide at absolute (x, y).

        Mirrors the pygame runtime's if_collision check: callers pass an
        absolute target position (self.x + offset). object_name may be
        None/'any' (any object), 'solid' (solid objects only), or a specific
        object type name.
        """
        if not self.scene:
            return False
        if object_name and '_' in object_name:
            pascal = ''.join(p.capitalize() for p in object_name.split('_'))
        else:
            pascal = object_name
        old_x, old_y = self.x, self.y
        self.x, self.y = x, y
        hit = False
        try:
            for other in self.scene.instances:
                if other is self or getattr(other, '_destroyed', False):
                    continue
                if object_name in (None, '', 'any'):
                    match = True
                elif object_name == 'solid':
                    match = getattr(other, 'solid', False)
                else:
                    match = (other.__class__.__name__ == object_name or
                             other.__class__.__name__ == pascal or
                             getattr(other, 'object_name', '') == object_name)
                if match and self.check_collision(other):
                    hit = True
                    break
        finally:
            self.x, self.y = old_x, old_y
        return hit

    def destroy(self):
        """Destroy this instance"""
        if hasattr(self, 'on_destroy'):
            self.on_destroy()
        if self.scene:
            self.scene.destroy_instance(self)

    def is_on_grid(self):
        """Check if object is close to grid alignment"""
        # Tolerance must account for variable frame rates
        # At 30 FPS with speed 4: movement = 4 * 2.0 = 8 pixels/frame
        # Use generous tolerance to handle frame rate variations
        base_speed = max(abs(self.hspeed), abs(self.vspeed), 4)
        tolerance = base_speed * 2.5  # Handle up to ~24 FPS

        # Find nearest grid position
        nearest_x = round(self.x / self.grid_size) * self.grid_size
        nearest_y = round(self.y / self.grid_size) * self.grid_size

        # Check if we're close enough to that grid position
        x_diff = abs(self.x - nearest_x)
        y_diff = abs(self.y - nearest_y)

        return x_diff <= tolerance and y_diff <= tolerance

    def snap_to_grid(self):
        """Snap object to nearest grid position"""
        self.x = round(self.x / self.grid_size) * self.grid_size
        self.y = round(self.y / self.grid_size) * self.grid_size
        self._update_position()

    def _check_wall_ahead(self, dx, dy):
        """Check if there's a wall in the direction we want to move"""
        if not self.scene:
            return False
        # Temporarily move to check position
        old_x, old_y = self.x, self.y
        self.x += dx
        self.y += dy

        # Check for collision with any solid object
        collision = False
        for other in self.scene.instances:
            if other != self and other.solid and self.check_collision(other):
                collision = True
                break

        # Restore position
        self.x, self.y = old_x, old_y

        return collision

    def stop_movement(self):
        """Stop all movement"""
        self.hspeed = 0
        self.vspeed = 0
        self.speed = 0

    def _move_grid(self, dx, dy):
        """Move by grid amount, checking for walls and pushable objects

        This method handles:
        1. Wall collision checking (prevents moving into walls)
        2. Box pushing (if the target has a pushable box)
        3. Position update

        Object transformations (e.g., box -> box_store) are handled by the
        IDE's collision event system, not by _move_grid.

        hspeed/vspeed should be set before calling this to indicate direction
        """
        # Check for wall collision
        if self._check_wall_ahead(dx, dy):
            self.hspeed = 0
            self.vspeed = 0
            return

        # Check for pushable/blocking objects at target position
        if not self.scene:
            return
        target_x = self.x + dx
        target_y = self.y + dy
        threshold = self.grid_size // 2

        for other in self.scene.instances[:]:  # Use slice copy since we may modify list
            if other == self:
                continue
            # Check if other object is at target position
            if (abs(other.x - target_x) < threshold and abs(other.y - target_y) < threshold):
                # Found object at target - check if it's pushable
                if other.pushable:
                    # Try to push the object
                    behind_x = other.x + dx
                    behind_y = other.y + dy

                    # Check if space behind is free
                    can_push = True
                    for blocker in self.scene.instances:
                        if blocker != self and blocker != other:
                            if (abs(blocker.x - behind_x) < threshold and
                                abs(blocker.y - behind_y) < threshold and
                                (blocker.solid or blocker.pushable)):
                                can_push = False
                                break

                    if can_push:
                        # Push the object
                        other.x += dx
                        other.y += dy
                        other._update_position()
                    else:
                        # Can't push - don't move
                        self.hspeed = 0
                        self.vspeed = 0
                        return
                elif other.solid:
                    # Solid blocking object - stop
                    self.hspeed = 0
                    self.vspeed = 0
                    return

        # Move the player
        self.x += dx
        self.y += dy
        self._update_position()

        # Clear speed after grid movement
        self.hspeed = 0
        self.vspeed = 0

    # Event handlers (to be overridden by subclasses)
    def on_create(self):
        """Called when instance is created"""
        pass

    def on_update(self, dt):
        """Called each frame"""
        pass

    def on_destroy(self):
        """Called when instance is destroyed"""
        pass

    def on_keyboard(self, key, scancode, codepoint, modifier):
        """Called when a key is pressed"""
        pass

    def on_keyboard_up(self, key, scancode):
        """Called when a key is released"""
        pass

    def destroy_at_position(self, x, y, radius=32, object_filter='all', relative=False):
        """Destroy matching instances within radius px of (x, y).

        Mirrors the IDE runtime's execute_destroy_at_position_action,
        excluding the caller. Relative GM offsets: y grows downward in GM
        room coords, so the kivy-space offset is self.y - y.
        """
        if not self.scene:
            return
        cx = self.x + x if relative else x
        cy = self.y - y if relative else y
        for other in list(self.scene.instances):
            if other is self:
                continue
            if object_filter == 'solid' and not other.solid:
                continue
            if object_filter == 'non-solid' and other.solid:
                continue
            if object_filter not in ('all', 'any', 'solid', 'non-solid'):
                other_name = getattr(other, 'object_name', other.__class__.__name__)
                if other_name != object_filter and other.__class__.__name__ != object_filter:
                    continue
            dx = other.x - cx
            dy = other.y - cy
            in_range = (dx * dx + dy * dy <= radius * radius) if radius > 0 \
                else (dx == 0 and dy == 0)
            if in_range:
                self.scene.destroy_instance(other)

    def jump_to_random(self, snap_h=1, snap_v=1):
        """Move to a random room position (snapped), avoiding solids
        best-effort — mirrors the IDE runtime's execute_jump_to_random."""
        import random
        if not self.scene:
            return
        w = int(self.image_width or self.grid_size)
        h = int(self.image_height or self.grid_size)
        snap_h = max(1, int(snap_h or 1))
        snap_v = max(1, int(snap_v or 1))
        for _attempt in range(20):
            nx = random.randrange(0, max(1, int(self.scene.room_width) - w))
            ny = random.randrange(0, max(1, int(self.scene.room_height) - h))
            nx = (nx // snap_h) * snap_h
            ny = (ny // snap_v) * snap_v
            self.x = float(nx)
            self.y = float(ny)
            self._update_position()
            blocked = False
            for other in self.scene.instances:
                if other is not self and other.solid and self.check_collision(other):
                    blocked = True
                    break
            if not blocked:
                break

    # ---- Draw-queue rendering (GameMaker draw event parity) ----

    @staticmethod
    def _dq_color(value):
        """Normalize a draw-queue color ((r,g,b[,a]) 0-255 or '#RRGGBB')
        to a Kivy rgba tuple of 0-1 floats."""
        try:
            if isinstance(value, str):
                hex_str = value[1:] if value.startswith('#') else value
                return (int(hex_str[0:2], 16) / 255.0,
                        int(hex_str[2:4], 16) / 255.0,
                        int(hex_str[4:6], 16) / 255.0, 1)
            r, g, b = value[0], value[1], value[2]
            a = value[3] if len(value) > 3 else 255
            return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)
        except Exception:
            return (1, 1, 1, 1)

    # __PYGM_EXTENSION_BASE_CODE__
    def _render_draw_queue(self):
        """Render queued draw commands as Kivy canvas instructions.

        Commands use the IDE runtime's schema and room coordinates (y=0 at
        the TOP); this converts to Kivy's y-up frame via the room height.
        Mirrors GameRunner._process_draw_queue: rectangle / circle /
        ellipse / line / text / scaled_text; unknown types are skipped.
        The queue is cleared afterwards, matching the runtime.
        """
        if self._dq_group is None:
            self._dq_group = InstructionGroup()
            self.canvas.after.add(self._dq_group)
        group = self._dq_group
        group.clear()
        room_h = self.scene.room_height if self.scene else 0
        for cmd in self._draw_queue:
            try:
                self._dq_render_cmd(group, cmd, room_h)
            except Exception as exc:
                print(f"[ERROR] draw-queue {{cmd.get('type')}}: {{exc}}")
        self._draw_queue = []

    def _drain_sound_queue(self):
        """Play + clear sounds queued via self._sound_queue.append(...).

        Mirrors the desktop runtime's ActionExecutor._drain_sound_queue.
        Called once per frame per live instance from the scene's update()
        loop (not tied to on_draw, so it works for objects with no draw
        event too).
        """
        if not self._sound_queue:
            return
        from main import play_sound
        for item in self._sound_queue:
            if isinstance(item, dict):
                name = item.get('sound', '')
                volume = item.get('volume', 1.0)
            else:
                name = item
                volume = 1.0
            path = SOUND_PATHS.get(name, '')
            if path:
                play_sound(path, volume)
            else:
                print(f"[WARN] queued sound not found in export: {{name}}")
        self._sound_queue = []

    def _dq_render_cmd(self, group, cmd, room_h):
        """Render one draw-queue command dict into ``group``."""
        ctype = cmd.get('type')
        color = self._dq_color(cmd.get('color', '#FFFFFF'))
        if ctype == 'rectangle':
            x1 = float(cmd.get('x1', 0))
            y1 = float(cmd.get('y1', 0))
            x2 = float(cmd.get('x2', 100))
            y2 = float(cmd.get('y2', 100))
            group.add(Color(*color))
            if cmd.get('filled', True):
                group.add(Rectangle(pos=(x1, room_h - y2),
                                    size=(x2 - x1, y2 - y1)))
            else:
                group.add(Line(rectangle=(x1, room_h - y2,
                                          x2 - x1, y2 - y1), width=1))
        elif ctype == 'ellipse':
            x1 = float(cmd.get('x1', 0))
            y1 = float(cmd.get('y1', 0))
            x2 = float(cmd.get('x2', 100))
            y2 = float(cmd.get('y2', 100))
            group.add(Color(*color))
            if cmd.get('filled', True):
                group.add(Ellipse(pos=(x1, room_h - y2),
                                  size=(x2 - x1, y2 - y1)))
            else:
                group.add(Line(ellipse=(x1, room_h - y2,
                                        x2 - x1, y2 - y1), width=1))
        elif ctype == 'circle':
            x = float(cmd.get('x', 0))
            y = float(cmd.get('y', 0))
            radius = float(cmd.get('radius', 10))
            group.add(Color(*color))
            if cmd.get('filled', True):
                group.add(Ellipse(pos=(x - radius, room_h - y - radius),
                                  size=(2 * radius, 2 * radius)))
            else:
                group.add(Line(circle=(x, room_h - y, radius), width=1))
        elif ctype == 'line':
            group.add(Color(*color))
            group.add(Line(points=[float(cmd.get('x1', 0)),
                                   room_h - float(cmd.get('y1', 0)),
                                   float(cmd.get('x2', 100)),
                                   room_h - float(cmd.get('y2', 100))],
                           width=1))
        elif ctype == 'arrow':
            # Shaft + two tip segments, pre-computed by the draw_arrow
            # codegen (see code_generator.py) the same way the pygame
            # runtime's execute_draw_arrow_action pre-computes them.
            x1 = float(cmd.get('x1', 0))
            y1 = float(cmd.get('y1', 0))
            x2 = float(cmd.get('x2', 100))
            y2 = float(cmd.get('y2', 100))
            t1x = float(cmd.get('tip1_x', x2))
            t1y = float(cmd.get('tip1_y', y2))
            t2x = float(cmd.get('tip2_x', x2))
            t2y = float(cmd.get('tip2_y', y2))
            group.add(Color(*color))
            group.add(Line(points=[x1, room_h - y1, x2, room_h - y2], width=1))
            group.add(Line(points=[x2, room_h - y2, t1x, room_h - t1y], width=1))
            group.add(Line(points=[x2, room_h - y2, t2x, room_h - t2y], width=1))
        elif ctype in ('text', 'scaled_text'):
            label = CoreLabel(text=str(cmd.get('text', '')), font_size=18)
            label.refresh()
            texture = label.texture
            if texture is None:
                return
            width, height = texture.size
            if ctype == 'scaled_text':
                width = max(1, int(width * float(cmd.get('xscale', 1.0))))
                height = max(1, int(height * float(cmd.get('yscale', 1.0))))
            x = float(cmd.get('x', 0))
            y = float(cmd.get('y', 0))
            # CoreLabel glyphs are white; the Color instruction tints them.
            group.add(Color(*color))
            group.add(Rectangle(texture=texture,
                                pos=(x, room_h - y - height),
                                size=(width, height)))
        elif ctype == 'sprite':
            # draw_sprite: sprite resolved to its exported asset path at
            # code-generation time ('sprite_path' — structured actions), or
            # by name via SPRITE_PATHS for hand-authored execute_code draw
            # commands (which the code generator never sees); unknown
            # sprites skip.
            path = cmd.get('sprite_path') or SPRITE_PATHS.get(cmd.get('sprite_name'), '')
            img = load_image(path) if path else None
            if img is None:
                return
            x = float(cmd.get('x', 0))
            y = float(cmd.get('y', 0))
            tex = img.texture
            # Multi-frame sprite: crop the requested frame from the horizontal
            # strip, mirroring _redraw_frame. Until 2026-07-21 this drew the
            # whole spritesheet, ignoring subimage. Frame metadata is keyed by
            # asset path in SPRITE_META (same as _redraw_frame reads it).
            meta = SPRITE_META.get(path, {{}})
            frames = max(1, int(meta.get('frames', 1) or 1))
            if frames > 1:
                fw = int(meta.get('frame_width') or 0) or int(tex.width // frames)
                fh = int(meta.get('frame_height') or 0) or int(tex.height)
                idx = int(cmd.get('subimage', 0)) % frames
                tex = tex.get_region(idx * fw, 0, fw, fh)
            group.add(Color(1, 1, 1, 1))
            group.add(Rectangle(texture=tex,
                                pos=(x, room_h - y - tex.height),
                                size=(tex.width, tex.height)))
        elif ctype == 'lives':
            # draw_lives: one sprite per remaining life, left-to-right;
            # text fallback when no usable sprite (runtime _draw_lives).
            path = cmd.get('sprite_path') or ''
            img = load_image(path) if path else None
            count = max(0, int(cmd.get('count', 0)))
            x = float(cmd.get('x', 0))
            y = float(cmd.get('y', 0))
            scale = float(cmd.get('scale', 1.0) or 1.0)
            if img is not None:
                tex = img.texture
                tw = tex.width * scale
                th = tex.height * scale
                group.add(Color(1, 1, 1, 1))
                for i in range(count):
                    group.add(Rectangle(texture=tex,
                                        pos=(x + i * tw, room_h - y - th),
                                        size=(tw, th)))
            else:
                label = CoreLabel(text='Lives: ' + str(count), font_size=18)
                label.refresh()
                if label.texture is None:
                    return
                group.add(Color(1, 1, 1, 1))
                group.add(Rectangle(texture=label.texture,
                                    pos=(x, room_h - y - label.texture.size[1]),
                                    size=label.texture.size))
        elif ctype == 'background':
            # draw_background: background resolved by name via
            # BACKGROUND_PATHS (backgrounds are copied alongside sprites
            # into assets/images/ by _export_background, but kept in a
            # separate name->path map so a background can't collide with
            # a same-named sprite). 'tiled' repeats it across the room.
            path = cmd.get('background_path') or BACKGROUND_PATHS.get(cmd.get('background_name'), '')
            img = load_image(path) if path else None
            if img is None:
                return
            x = float(cmd.get('x', 0))
            y = float(cmd.get('y', 0))
            tex = img.texture
            bw, bh = tex.width, tex.height
            group.add(Color(1, 1, 1, 1))
            if cmd.get('tiled'):
                # Mirrors the desktop runtime's _draw_background tiling math
                # (screen.get_width/height there -> Window.width/height here).
                screen_w = Window.width
                screen_h = Window.height
                start_x = (x % bw) - bw if x < 0 else (x % bw)
                if start_x > 0:
                    start_x -= bw
                start_y = (y % bh) - bh if y < 0 else (y % bh)
                if start_y > 0:
                    start_y -= bh
                cy = start_y
                while cy < screen_h:
                    cx = start_x
                    while cx < screen_w:
                        group.add(Rectangle(texture=tex, pos=(cx, room_h - cy - bh), size=(bw, bh)))
                        cx += bw
                    cy += bh
            else:
                group.add(Rectangle(texture=tex, pos=(x, room_h - y - bh), size=(bw, bh)))
        elif ctype == 'health_bar':
            # draw_health_bar: filled back rect, filled health-proportion
            # rect on top, unfilled border — mirrors runtime._draw_health_bar.
            x1 = float(cmd.get('x1', 0))
            y1 = float(cmd.get('y1', 0))
            x2 = float(cmd.get('x2', 100))
            y2 = float(cmd.get('y2', 20))
            health = float(cmd.get('health', 100))
            back_color = self._dq_color(cmd.get('back_color', '#FF0000'))
            bar_color = self._dq_color(cmd.get('bar_color', '#00FF00'))
            bar_w = x2 - x1
            bar_h = y2 - y1
            pos = (x1, room_h - y2)
            group.add(Color(*back_color))
            group.add(Rectangle(pos=pos, size=(bar_w, bar_h)))
            health_w = bar_w * max(0.0, min(100.0, health)) / 100.0
            if health_w > 0:
                group.add(Color(*bar_color))
                group.add(Rectangle(pos=pos, size=(health_w, bar_h)))
            group.add(Color(0, 0, 0, 1))
            group.add(Line(rectangle=(x1, room_h - y2, bar_w, bar_h), width=1))
'''

        # Format the template with actual values
        code_formatted = code.format(grid_size=self.grid_size)
        code_formatted = self._inject_extension_base_code(code_formatted)

        output_file = self.output_path / "game" / "objects" / "base_object.py"
        output_file.write_text(code_formatted, encoding="utf-8")

    def _generate_object(self, obj_name: str, obj_data: Dict, pushable: bool = False):
        """Generate a specific object class"""
        class_name = self._get_object_class_name(obj_name)

        # Get object properties
        sprite_name = obj_data.get('sprite', '')
        solid = obj_data.get('solid', False)
        visible = obj_data.get('visible', True)
        # GameMaker draw depth: higher = drawn first (further back).
        depth = obj_data.get('depth', 0)
        persistent = obj_data.get('persistent', False)

        # Get sprite file path if sprite is set
        sprite_path = ""
        if sprite_name:
            sprites = self.project_data.get('assets', {}).get('sprites', {})
            if sprite_name in sprites:
                sprite_file = sprites[sprite_name].get('file_path', '')
                if sprite_file:
                    sprite_path = f"assets/images/{_exported_asset_filename(sprite_name, sprite_file)}"

        # Generate event handlers from object's events
        events = obj_data.get('events', [])

        logger.debug(f"    Raw events for {obj_name}: {type(events).__name__}")

        # Handle different event storage formats
        if isinstance(events, dict):
            # Events stored as dict/OrderedDict - convert to list
            logger.debug(f"    Converting events dict to list for {obj_name}")
            logger.debug(f"    Event keys in dict: {list(events.keys())}")
            events_list = []
            for event_key, event_data in events.items():
                logger.debug(f"      Processing event '{event_key}': {type(event_data).__name__}")
                if isinstance(event_data, dict):
                    logger.debug(f"        Event data keys: {list(event_data.keys())}")

                    # Special handling for keyboard events
                    if event_key == 'keyboard':
                        # Keyboard events have sub-events for each key
                        # Each key (right, left, up, down) has its own actions
                        for key_name, key_data in event_data.items():
                            if isinstance(key_data, dict) and 'actions' in key_data:
                                # Create a keyboard event for this specific key
                                key_event = {
                                    'event_type': 'keyboard',
                                    'key_name': key_name,
                                    'actions': key_data.get('actions', []),
                                }
                                events_list.append(key_event)
                                logger.debug(f"        Added keyboard sub-event for '{key_name}' with {len(key_event['actions'])} actions")
                    elif event_key == 'keyboard_press':
                        # Keyboard_press events fire once per key press (not continuously)
                        # Keys are named press_down, press_left, press_right, press_up
                        for key_name, key_data in event_data.items():
                            if isinstance(key_data, dict) and 'actions' in key_data:
                                actions = key_data.get('actions', [])
                                if actions:  # Only add if there are actual actions
                                    # Map press_down -> down, press_left -> left, etc.
                                    normalized_key = key_name.replace('press_', '') if key_name.startswith('press_') else key_name
                                    key_event = {
                                        'event_type': 'keyboard_press',
                                        'key_name': normalized_key,
                                        'actions': actions,
                                    }
                                    events_list.append(key_event)
                                    logger.debug(f"        Added keyboard_press sub-event for '{key_name}' -> '{normalized_key}' with {len(actions)} actions")
                    elif event_key == 'keyboard_release':
                        # keyboard_release events fire once when a key is let go.
                        # Keys may be named release_left etc. or plain left.
                        for key_name, key_data in event_data.items():
                            if isinstance(key_data, dict) and 'actions' in key_data:
                                actions = key_data.get('actions', [])
                                if actions:
                                    normalized_key = key_name.replace('release_', '') if key_name.startswith('release_') else key_name
                                    key_event = {
                                        'event_type': 'keyboard_release',
                                        'key_name': normalized_key,
                                        'actions': actions,
                                    }
                                    events_list.append(key_event)
                                    logger.debug(f"        Added keyboard_release sub-event for '{key_name}' -> '{normalized_key}' with {len(actions)} actions")
                    else:
                        # Regular event - add the event type if not present
                        if 'event_type' not in event_data:
                            event_data['event_type'] = event_key
                        events_list.append(event_data)
                        actions_count = len(event_data.get('actions', []))
                        logger.debug(f"        Added event with type: {event_data.get('event_type')} ({actions_count} actions)")
                elif isinstance(event_data, list):
                    # Event data is already a list of event dicts
                    logger.debug(f"        Event data is a list with {len(event_data)} items")
                    for evt in event_data:
                        if isinstance(evt, dict):
                            if 'event_type' not in evt:
                                evt['event_type'] = event_key
                            events_list.append(evt)
                else:
                    logger.debug(f"        Warning: Skipping event '{event_key}' - data is {type(event_data).__name__}")
            events = events_list
            logger.debug(f"    Final events list has {len(events)} event(s)")
        elif not isinstance(events, list):
            logger.debug(f"    Warning: events for {obj_name} is {type(events).__name__}, converting to empty list")
            events = []

        # Show what events we're working with
        if events:
            logger.debug(f"    Processing {len(events)} event(s):")
            for i, evt in enumerate(events[:3]):  # Show first 3
                if isinstance(evt, dict):
                    logger.debug(f"      Event {i}: type={evt.get('event_type')}, actions={len(evt.get('actions', []))}")

        event_methods = self._generate_event_methods(obj_name, events)

        # Generate sprite line
        if sprite_path:
            sprite_line = f"self.set_sprite('{sprite_path}')"
        else:
            sprite_line = "pass"

        code = '''#!/usr/bin/env python3
"""
Object: {obj_name}
Generated from PyGameMaker IDE
"""

from objects.base_object import GameObject
from kivy.core.window import Window


class {class_name}(GameObject):
    """Game object: {obj_name}"""

    def __init__(self, scene, x=0, y=0, **kwargs):
        super().__init__(scene, x, y, **kwargs)

        self.solid = {solid}
        self.visible = {visible}
        self.persistent = {persistent}
        self.pushable = {pushable}
        self.depth = {depth}

        # Set sprite
        {sprite_line}

{event_methods}
'''

        # Format the template with actual values
        code_formatted = code.format(
            obj_name=obj_name,
            class_name=class_name,
            solid=solid,
            visible=visible,
            persistent=persistent,
            pushable=pushable,
            depth=depth,
            sprite_line=sprite_line,
            event_methods=event_methods
        )

        output_file = (self.output_path / "game" / "objects" /
                       f"{self._get_object_module_name(obj_name)}.py")
        output_file.write_text(code_formatted, encoding="utf-8")

    def _generate_event_methods(self, obj_name: str, events: List[Dict]) -> str:
        """Generate event handler methods from event data"""
        methods = []

        logger.debug(f"    _generate_event_methods called with {len(events)} events")

        # Filter out any non-dict events (malformed data)
        valid_events = []
        for i, event in enumerate(events):
            if isinstance(event, dict):
                logger.debug(f"      Event {i}: {event.get('event_type', 'unknown')} (key: {event.get('key_name', 'N/A')}) with {len(event.get('actions', []))} actions")
                valid_events.append(event)
            else:
                logger.debug(f"      Warning: Skipping malformed event in {obj_name}: {type(event).__name__}")

        events = valid_events

        if not events:
            logger.debug("      No valid events found, returning pass")
            return "    pass\n"

        # Group keyboard events together (but NOT nokey - that's handled separately)
        keyboard_events = [e for e in events if e.get('event_type') == 'keyboard' and e.get('key_name') and e.get('key_name') != 'nokey']
        keyboard_press_events = [e for e in events if e.get('event_type') == 'keyboard_press' and e.get('key_name')]
        keyboard_release_events = [e for e in events if e.get('event_type') == 'keyboard_release' and e.get('key_name')]
        nokey_events = [e for e in events if e.get('event_type') == 'keyboard' and e.get('key_name') == 'nokey']
        other_events = [e for e in events if not (e.get('event_type') in ['keyboard', 'keyboard_press', 'keyboard_release'] and e.get('key_name'))]

        # Generate consolidated keyboard handler if there are keyboard events (continuous checking)
        if keyboard_events:
            logger.debug(f"      Generating consolidated keyboard handler for {len(keyboard_events)} key(s)")
            keyboard_method = self._generate_keyboard_handler(keyboard_events)
            methods.append(keyboard_method)

        # Generate keyboard_press handler if there are keyboard_press events (one-shot per press)
        if keyboard_press_events:
            logger.debug(f"      Generating keyboard_press handler for {len(keyboard_press_events)} key(s)")
            keyboard_press_method = self._generate_keyboard_press_handler(keyboard_press_events)
            methods.append(keyboard_press_method)

        # Generate keyboard_release handler -> on_keyboard_up (the scene
        # dispatches on_key_up to instance.on_keyboard_up). Without this the
        # release actions (e.g. stop_movement on key-up in the platformer
        # samples) were silently dropped (M35).
        if keyboard_release_events:
            logger.debug(f"      Generating keyboard_release handler for {len(keyboard_release_events)} key(s)")
            keyboard_release_method = self._generate_keyboard_release_handler(keyboard_release_events)
            methods.append(keyboard_release_method)

        # Generate on_nokey method for nokey events
        if nokey_events:
            logger.debug("      Generating nokey handler")
            nokey_event = nokey_events[0]  # There should only be one nokey event
            actions = nokey_event.get('actions', [])
            if actions:
                action_code = self._generate_action_code(obj_name, actions, nokey_event)
                nokey_method = '''    def on_nokey(self):
        """Event handler: keyboard nokey (no keys pressed)"""
{action_code}
'''.format(action_code=action_code)
                methods.append(nokey_method)

        # Generate other event handlers
        for event in other_events:
            event_type = event.get('event_type', '')
            actions = event.get('actions', [])

            if not actions:
                continue

            # Map event types to method names
            method_name = self._get_event_method_name(event)
            if not method_name:
                continue

            # Generate method signature
            if event_type == 'keyboard':
                params = "self, key, scancode, codepoint, modifier"
            elif event_type == 'keyboard_up':
                params = "self, key, scancode"
            elif event_type.startswith('not_collision_with_'):
                params = "self"
            elif event_type == 'collision' or event_type.startswith('collision_with_'):
                params = "self, other"
            elif event_type in ['step', 'draw']:
                params = "self, dt"
            else:
                params = "self"

            # Generate action code
            action_code = self._generate_action_code(obj_name, actions, event)

            method = '''    def {method_name}({params}):
        """Event handler: {event_type}"""
{action_code}
'''.format(method_name=method_name, params=params, event_type=event_type, action_code=action_code)
            methods.append(method)

        # Two generators can target the same method name (e.g. the grid
        # keyboard handler and a step event both emit on_update; keyboard and
        # keyboard_press both emit on_keyboard). Python keeps only the LAST
        # def, silently shadowing the earlier one. Merge same-named methods
        # into one so neither body is lost (M37).
        methods = self._merge_duplicate_methods(methods)

        return '\n'.join(methods) if methods else "    pass\n"

    def _merge_duplicate_methods(self, methods: List[str]) -> List[str]:
        """Merge generated method bodies that share a def name.

        Same-named event methods always share a signature here (on_update ->
        self, dt; on_keyboard -> the press signature), so the bodies can be
        concatenated under a single def without argument conflicts.
        """
        import re

        order = []          # preserves first-seen order: ('method', name) | ('raw', text)
        grouped = {}        # name -> [method_text, ...]
        for m in methods:
            match = re.search(r'def\s+(\w+)\s*\(', m)
            if not match:
                order.append(('raw', m))
                continue
            name = match.group(1)
            if name not in grouped:
                grouped[name] = []
                order.append(('method', name))
            grouped[name].append(m)

        result = []
        for kind, key in order:
            if kind == 'raw':
                result.append(key)
            elif len(grouped[key]) == 1:
                result.append(grouped[key][0])
            else:
                result.append(self._merge_method_bodies(grouped[key]))
        return result

    @staticmethod
    def _merge_method_bodies(texts: List[str]) -> str:
        """Combine several same-named method texts into one def."""
        first_lines = texts[0].rstrip('\n').split('\n')
        header = [first_lines[0]]  # the def line
        body_start = 1
        if body_start < len(first_lines) and first_lines[body_start].strip().startswith('"""'):
            header.append(first_lines[body_start])  # keep the first docstring
            body_start = 1  # docstrings are dropped per-body below

        bodies = []
        for text in texts:
            lines = text.rstrip('\n').split('\n')
            j = 1
            if j < len(lines) and lines[j].strip().startswith('"""'):
                j += 1
            body = lines[j:]
            non_empty = [ln for ln in body if ln.strip()]
            # Skip a body that is just 'pass' when other bodies have content.
            if len(non_empty) == 1 and non_empty[0].strip() == 'pass':
                continue
            bodies.extend(body)

        if not any(ln.strip() for ln in bodies):
            bodies = ['        pass']
        return '\n'.join(header + bodies) + '\n'

    def _generate_keyboard_handler(self, keyboard_events: List[Dict]) -> str:
        """Generate a consolidated keyboard handler for all key-specific events"""
        # For grid-based movement games, keyboard input should be handled in the step event
        # NOT in keyboard handlers, to avoid conflicts and wall-phasing issues

        # Check if ANY keyboard event uses grid-based movement. The marker is
        # if_on_grid specifically — keying off plain set_hspeed/set_vspeed
        # (M36) misfired on platformers, replacing free motion with grid
        # snapping and discarding every non-speed action (jump, sprite flip,
        # collision checks). Plain speed-setting keyboard events now generate
        # the normal handler, which keeps all their actions.
        uses_grid_movement = False
        for event in keyboard_events:
            actions = event.get('actions', [])
            for action in actions:
                if isinstance(action, dict):
                    action_type = action.get('action_type', action.get('action', ''))
                    if action_type == 'if_on_grid':
                        uses_grid_movement = True
                        break
            if uses_grid_movement:
                break

        # If using grid movement, generate step-based keyboard checking instead
        if uses_grid_movement:
            return self._generate_grid_keyboard_handler(keyboard_events)

        # Otherwise, generate normal keyboard handler
        key_map = _KIVY_KEY_MAP

        code_lines = []
        code_lines.append("    def on_keyboard(self, key, scancode, codepoint, modifier):")
        code_lines.append('        """Handle keyboard press events"""')

        for i, event in enumerate(keyboard_events):
            key_name = event.get('key_name', '')
            actions = event.get('actions', [])
            key_code = key_map.get(str(key_name).lower(), '0')  # case-insensitive: samples write 'N'/'P' as well as 'r'

            if_keyword = "if" if i == 0 else "elif"
            code_lines.append(f"        {if_keyword} key == {key_code}:  # {key_name}")

            if actions:
                generator = ActionCodeGenerator(base_indent=3, sprite_paths=self.sprite_path_map, sound_paths=self.sound_path_map, background_paths=self.background_path_map)
                for action in actions:
                    if isinstance(action, dict):
                        generator.process_action(action, 'keyboard')
                    elif isinstance(action, str) and action.strip():
                        generator.add_line(action)

                action_code = generator.get_code()
                if action_code.strip():
                    code_lines.append(action_code)
                else:
                    code_lines.append("            pass")
            else:
                code_lines.append("            pass")

        return '\n'.join(code_lines)

    def _generate_grid_keyboard_handler(self, keyboard_events: List[Dict]) -> str:
        """Generate an on_update method that checks keyboard state for grid-based movement

        Grid movement logic:
        - When on a grid position, check keys and set movement direction
        - When NOT on grid, continue moving until we reach a grid position
        - Track whether keys are released mid-movement with _want_to_stop flag
        """
        # Extract speed values from the keyboard events
        speed_values = {'right': 4, 'left': -4, 'up': 4, 'down': -4}
        for event in keyboard_events:
            key_name = event.get('key_name', '')
            actions = event.get('actions', [])
            for action in actions:
                if isinstance(action, dict):
                    action_type = action.get('action_type', action.get('action', ''))
                    if action_type == 'if_on_grid':
                        params = action.get('parameters', {})
                        then_actions = params.get('then_actions', [])
                        for inner in then_actions:
                            if isinstance(inner, dict):
                                inner_type = inner.get('action_type', inner.get('action', ''))
                                inner_params = inner.get('parameters', {})
                                if inner_type == 'set_hspeed' and key_name in ['right', 'left']:
                                    speed_values[key_name] = inner_params.get('value', 4)
                                elif inner_type == 'set_vspeed' and key_name in ['up', 'down']:
                                    # Flip for Kivy coordinates
                                    val = inner_params.get('value', 4)
                                    speed_values[key_name] = -val if isinstance(val, (int, float)) else val
                    elif action_type == 'set_hspeed' and key_name in ['right', 'left']:
                        params = action.get('parameters', {})
                        speed_values[key_name] = params.get('value', 4)
                    elif action_type == 'set_vspeed' and key_name in ['up', 'down']:
                        params = action.get('parameters', {})
                        val = params.get('value', 4)
                        speed_values[key_name] = -val if isinstance(val, (int, float)) else val

        code_lines = []
        code_lines.append("    def on_update(self, dt):")
        code_lines.append('        """Step event with keyboard checking for grid-based movement"""')
        code_lines.append("")
        code_lines.append("        # Initialize grid movement state if not present")
        code_lines.append("        if not hasattr(self, '_grid_target_x'):")
        code_lines.append("            self._grid_target_x = None  # Target grid X position")
        code_lines.append("            self._grid_target_y = None  # Target grid Y position")
        code_lines.append("            self._grid_moving = False   # Currently moving to a target")
        code_lines.append("")
        code_lines.append("        # Check if any movement key is currently pressed")
        code_lines.append("        key_right = self.scene.keys_pressed.get(275, False)")
        code_lines.append("        key_left = self.scene.keys_pressed.get(276, False)")
        code_lines.append("        key_up = self.scene.keys_pressed.get(273, False)")
        code_lines.append("        key_down = self.scene.keys_pressed.get(274, False)")
        code_lines.append("        any_key_pressed = key_right or key_left or key_up or key_down")
        code_lines.append("")
        code_lines.append("        grid = self.grid_size")
        code_lines.append("")
        code_lines.append("        # If we're currently moving to a target, check if we've reached it")
        code_lines.append("        if self._grid_moving:")
        code_lines.append("            reached_x = True")
        code_lines.append("            reached_y = True")
        code_lines.append("            ")
        code_lines.append("            # Check X target")
        code_lines.append("            if self._grid_target_x is not None:")
        code_lines.append("                if self.hspeed > 0 and self.x >= self._grid_target_x:")
        code_lines.append("                    self.x = self._grid_target_x")
        code_lines.append("                    reached_x = True")
        code_lines.append("                elif self.hspeed < 0 and self.x <= self._grid_target_x:")
        code_lines.append("                    self.x = self._grid_target_x")
        code_lines.append("                    reached_x = True")
        code_lines.append("                elif self.hspeed != 0:")
        code_lines.append("                    reached_x = False")
        code_lines.append("            ")
        code_lines.append("            # Check Y target")
        code_lines.append("            if self._grid_target_y is not None:")
        code_lines.append("                if self.vspeed > 0 and self.y >= self._grid_target_y:")
        code_lines.append("                    self.y = self._grid_target_y")
        code_lines.append("                    reached_y = True")
        code_lines.append("                elif self.vspeed < 0 and self.y <= self._grid_target_y:")
        code_lines.append("                    self.y = self._grid_target_y")
        code_lines.append("                    reached_y = True")
        code_lines.append("                elif self.vspeed != 0:")
        code_lines.append("                    reached_y = False")
        code_lines.append("            ")
        code_lines.append("            # If we've reached the target, check if we should continue or stop")
        code_lines.append("            if reached_x and reached_y:")
        code_lines.append("                self._update_position()")
        code_lines.append("                # Check if the same direction key is still held - continue moving")
        code_lines.append("                continue_moving = False")
        code_lines.append("                if self.hspeed > 0 and key_right:")
        code_lines.append("                    self._grid_target_x = self.x + grid")
        code_lines.append("                    continue_moving = True")
        code_lines.append("                elif self.hspeed < 0 and key_left:")
        code_lines.append("                    self._grid_target_x = self.x - grid")
        code_lines.append("                    continue_moving = True")
        code_lines.append("                elif self.vspeed > 0 and key_up:")
        code_lines.append("                    self._grid_target_y = self.y + grid")
        code_lines.append("                    continue_moving = True")
        code_lines.append("                elif self.vspeed < 0 and key_down:")
        code_lines.append("                    self._grid_target_y = self.y - grid")
        code_lines.append("                    continue_moving = True")
        code_lines.append("                ")
        code_lines.append("                if not continue_moving:")
        code_lines.append("                    # Stop moving")
        code_lines.append("                    self.hspeed = 0")
        code_lines.append("                    self.vspeed = 0")
        code_lines.append("                    self._grid_moving = False")
        code_lines.append("                    self._grid_target_x = None")
        code_lines.append("                    self._grid_target_y = None")
        code_lines.append("")
        code_lines.append("        # If not moving, check for new movement input")
        code_lines.append("        if not self._grid_moving and any_key_pressed:")
        code_lines.append("            # Snap to nearest grid position first (in case we're slightly off)")
        code_lines.append("            snap_x = round(self.x / grid) * grid")
        code_lines.append("            snap_y = round(self.y / grid) * grid")
        code_lines.append("            self.x = snap_x")
        code_lines.append("            self.y = snap_y")
        code_lines.append("            ")
        code_lines.append("            # Set target based on key pressed (priority: right, left, up, down)")
        code_lines.append("            if key_right:")
        code_lines.append("                self._grid_target_x = snap_x + grid")
        code_lines.append("                self._grid_target_y = snap_y")
        code_lines.append(f"                self.hspeed = {abs(speed_values.get('right', 4))}")
        code_lines.append("                self.vspeed = 0")
        code_lines.append("                self._grid_moving = True")
        code_lines.append("            elif key_left:")
        code_lines.append("                self._grid_target_x = snap_x - grid")
        code_lines.append("                self._grid_target_y = snap_y")
        code_lines.append(f"                self.hspeed = -{abs(speed_values.get('left', 4))}")
        code_lines.append("                self.vspeed = 0")
        code_lines.append("                self._grid_moving = True")
        code_lines.append("            elif key_up:")
        code_lines.append("                self._grid_target_x = snap_x")
        code_lines.append("                self._grid_target_y = snap_y + grid")
        code_lines.append("                self.hspeed = 0")
        code_lines.append(f"                self.vspeed = {abs(speed_values.get('up', 4))}")
        code_lines.append("                self._grid_moving = True")
        code_lines.append("            elif key_down:")
        code_lines.append("                self._grid_target_x = snap_x")
        code_lines.append("                self._grid_target_y = snap_y - grid")
        code_lines.append("                self.hspeed = 0")
        code_lines.append(f"                self.vspeed = -{abs(speed_values.get('down', 4))}")
        code_lines.append("                self._grid_moving = True")
        code_lines.append("")

        return '\n'.join(code_lines)

    def _generate_keyboard_press_handler(self, keyboard_press_events: List[Dict]) -> str:
        """Generate an on_keyboard handler for keyboard_press events (one-shot per key press)

        Unlike keyboard events which check continuously, keyboard_press fires once per key press.
        This is ideal for Sokoban-style grid movement where each press moves one cell.
        """
        key_map = _KIVY_KEY_MAP

        code_lines = []
        code_lines.append("    def on_keyboard(self, key, scancode, codepoint, modifier):")
        code_lines.append('        """Handle keyboard press events (one-shot per press)"""')

        for i, event in enumerate(keyboard_press_events):
            key_name = event.get('key_name', '')
            actions = event.get('actions', [])
            key_code = key_map.get(str(key_name).lower(), '0')  # case-insensitive: samples write 'N'/'P' as well as 'r'

            if_keyword = "if" if i == 0 else "elif"
            code_lines.append(f"        {if_keyword} key == {key_code}:  # {key_name}")

            if actions:
                # Generate action code for this key press
                generator = ActionCodeGenerator(base_indent=3, sprite_paths=self.sprite_path_map, sound_paths=self.sound_path_map, background_paths=self.background_path_map)
                for action in actions:
                    if isinstance(action, dict):
                        generator.process_action(action, 'keyboard_press')
                    elif isinstance(action, str) and action.strip():
                        generator.add_line(action)

                action_code = generator.get_code()
                if action_code.strip():
                    code_lines.append(action_code)
                else:
                    code_lines.append("            pass")
            else:
                code_lines.append("            pass")

        return '\n'.join(code_lines)

    def _generate_keyboard_release_handler(self, keyboard_release_events: List[Dict]) -> str:
        """Generate an on_keyboard_up handler for keyboard_release events.

        The scene binds Window on_key_up -> on_keyboard_up(key, scancode) and
        dispatches it to each instance, so release actions land here.
        """
        key_map = _KIVY_KEY_MAP

        code_lines = []
        code_lines.append("    def on_keyboard_up(self, key, scancode):")
        code_lines.append('        """Handle keyboard release events"""')

        for i, event in enumerate(keyboard_release_events):
            key_name = event.get('key_name', '')
            actions = event.get('actions', [])
            key_code = key_map.get(str(key_name).lower(), '0')  # case-insensitive: samples write 'N'/'P' as well as 'r'

            if_keyword = "if" if i == 0 else "elif"
            code_lines.append(f"        {if_keyword} key == {key_code}:  # {key_name}")

            if actions:
                generator = ActionCodeGenerator(base_indent=3, sprite_paths=self.sprite_path_map, sound_paths=self.sound_path_map, background_paths=self.background_path_map)
                for action in actions:
                    if isinstance(action, dict):
                        generator.process_action(action, 'keyboard_release')
                    elif isinstance(action, str) and action.strip():
                        generator.add_line(action)

                action_code = generator.get_code()
                if action_code.strip():
                    code_lines.append(action_code)
                else:
                    code_lines.append("            pass")
            else:
                code_lines.append("            pass")

        return '\n'.join(code_lines)

    def _get_event_method_name(self, event: Dict) -> str:
        """Get the method name for an event - GAMEMAKER 7.0 COMPLETE"""
        event_type = event.get('event_type', '')

        # Handle negated collision events: not_collision_with_obj_name
        if event_type.startswith('not_collision_with_'):
            collision_obj = event_type.replace('not_collision_with_', '')
            return f"on_not_collision_{collision_obj.lower()}"

        # Handle collision events with specific format: collision_with_obj_name
        if event_type.startswith('collision_with_'):
            # Extract object name from collision_with_obj_name
            collision_obj = event_type.replace('collision_with_', '')
            return f"on_collision_{collision_obj.lower()}"

        # Handle alarm events (alarm_0 through alarm_11)
        if event_type.startswith('alarm_'):
            return f"on_{event_type}"  # on_alarm_0, on_alarm_1, etc.

        # Map event types to method names (GAMEMAKER 7.0 COMPLETE)
        event_map = {
            'create': 'on_create',
            'step': 'on_update',
            'begin_step': 'on_begin_step',
            'end_step': 'on_end_step',
            'destroy': 'on_destroy',
            'keyboard': 'on_keyboard',
            'keyboard_press': 'on_keyboard_press',
            'keyboard_release': 'on_keyboard_release',
            'keyboard_up': 'on_keyboard_up',  # Legacy name
            'draw': 'on_draw',
            'draw_gui': 'on_draw_gui',
            # Flat mouse-event keys as written by the IDE events panel
            # (mirrors runtime _FLAT_MOUSE_KEY_ALIASES; audit H11). The
            # scene's on_touch_down/on_touch_up dispatch these — press and
            # held variants fire on touch down, matching the IDE runtime,
            # which has no per-frame held-mouse loop either. Right/middle
            # buttons have no touch equivalent and stay unexported.
            'mouse_left_press': 'on_mouse_left_press',
            'mouse_left_button': 'on_mouse_left_press',
            'mouse_left_down': 'on_mouse_left_press',
            'mouse_left_release': 'on_mouse_left_release',
            'room_start': 'on_room_start',
            'room_end': 'on_room_end',
            'animation_end': 'on_animation_end',
            'no_more_lives': 'on_no_more_lives',
            'no_more_health': 'on_no_more_health',
            'game_start': 'on_game_start',
            'game_end': 'on_game_end',
            'outside_room': 'on_outside_room',
            'intersect_boundary': 'on_intersect_boundary',
        }

        if event_type == 'collision':
            collision_obj = event.get('collision_object', 'object')
            return f"on_collision_{collision_obj.lower()}"

        return event_map.get(event_type, '')

    def _generate_action_code(self, obj_name: str, actions: List[Dict], event: Dict) -> str:
        """Generate Python code from action list - WITH BLOCK SYSTEM"""
        event_type = event.get('event_type', '')

        if not actions:
            return "        pass"

        logger.debug(f"        _generate_action_code: {len(actions)} actions for event {event_type}")

        # Use the new ActionCodeGenerator for proper block/indentation handling
        generator = ActionCodeGenerator(base_indent=2, sprite_paths=self.sprite_path_map, sound_paths=self.sound_path_map, background_paths=self.background_path_map)

        for i, action in enumerate(actions):
            logger.debug(f"          Action {i}: {type(action).__name__}")

            if isinstance(action, dict):
                action_type = action.get('action_type', action.get('action', ''))
                logger.debug(f"            Type: '{action_type}'")

                # Process action with block system
                generator.process_action(action, event_type)

            elif isinstance(action, str):
                # String action - add as raw code
                logger.debug(f"            String action: '{action[:80]}'")
                if action.strip():
                    generator.add_line(action)

        # Get the generated code
        code = generator.get_code()

        # CRITICAL: Always return valid Python code with at least 'pass'
        if not code or not code.strip():
            logger.debug(f"          Warning: No code generated for event {event_type}, using 'pass'")
            return "        pass"

        return code

    def _generate_utils(self):
        """Generate utility functions file"""
        code = '''#!/usr/bin/env python3
"""
Game Utility Functions
Helper functions for the game
"""

from kivy.core.image import Image as CoreImage
import os
import sys


_image_cache = {}
_base_path = None


def get_base_path():
    """Get the base path for assets, handling PyInstaller frozen executables"""
    global _base_path
    if _base_path is not None:
        return _base_path

    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        # Assets are in _MEIPASS/game/
        _base_path = os.path.join(sys._MEIPASS, 'game')
    else:
        # Running as script - use the directory containing this file
        _base_path = os.path.dirname(os.path.abspath(__file__))

    return _base_path


def get_asset_path(relative_path):
    """Get absolute path to an asset file"""
    base = get_base_path()
    return os.path.join(base, relative_path)


def load_image(path):
    """Load an image with caching"""
    if path in _image_cache:
        return _image_cache[path]

    # Convert relative path to absolute path
    abs_path = get_asset_path(path)

    try:
        if os.path.exists(abs_path):
            img = CoreImage(abs_path)
            _image_cache[path] = img
            return img
        else:
            print(f"[WARN] Image not found: {abs_path}")
            print(f"       Base path: {get_base_path()}")
            print(f"       Relative path: {path}")
    except Exception as e:
        print(f"[ERROR] Failed to load image {abs_path}: {e}")

    return None


def clear_image_cache():
    """Clear the image cache"""
    global _image_cache
    _image_cache.clear()
'''

        output_file = self.output_path / "game" / "utils.py"
        output_file.write_text(code, encoding="utf-8")

    def _generate_buildozer_spec(self):
        """Generate buildozer.spec for Android builds"""
        project_name = self.project_data.get('name', 'MyGame')
        package_name = project_name.lower().replace(' ', '')

        spec = '''[app]
title = {project_name}
package.name = {package_name}
package.domain = org.pygamemaker

source.dir = ./game
source.include_exts = py,png,jpg,wav,mp3,ogg

version = 1.0

requirements = python3,kivy

orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
'''

        # Format the template with actual values
        spec_formatted = spec.format(
            project_name=project_name,
            package_name=package_name
        )

        output_file = self.output_path / "buildozer.spec"
        output_file.write_text(spec_formatted, encoding="utf-8")

    def _generate_requirements(self):
        """Generate requirements.txt"""
        requirements = '''kivy>=2.1.0
'''

        output_file = self.output_path / "requirements.txt"
        output_file.write_text(requirements, encoding="utf-8")

    def _generate_readme(self):
        """Generate README with instructions"""
        project_name = self.project_data.get('name', 'MyGame')

        readme = '''# {project_name}

Exported from PyGameMaker IDE

## Running the Game

### Desktop (Linux/Mac/Windows)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the game:
   ```bash
   cd game
   python3 main.py
   ```

### Android

1. Install Buildozer:
   ```bash
   pip install buildozer
   ```

2. Build APK:
   ```bash
   buildozer android debug
   ```

3. The APK will be in `bin/` directory

## Controls

Use arrow keys or WASD for movement.

## Project Structure

- `game/` - Main game code
  - `main.py` - Application entry point
  - `utils.py` - Utility functions
  - `objects/` - Game object classes
  - `scenes/` - Game scenes/rooms
  - `assets/` - Game assets (images, sounds)
- `buildozer.spec` - Android build configuration
- `requirements.txt` - Python dependencies

## Notes

This game was created with PyGameMaker IDE, a GameMaker-inspired
game development environment for Python.
'''

        # Format the template with actual values
        readme_formatted = readme.format(project_name=project_name)

        output_file = self.output_path / "README.md"
        output_file.write_text(readme_formatted, encoding="utf-8")

    @staticmethod
    def _safe_room_dim(value, default):
        """Clamp a room width/height to a sane positive int. An explicit
        0 / negative / non-numeric dimension (corrupt or foreign-imported
        project) reaches the Android scaler's min(screen/game) division and
        raises ZeroDivisionError at startup — the pygame runtime clamps via
        _sane_room_dimension, so mirror that here (KA-L2)."""
        try:
            v = int(value)
        except (TypeError, ValueError):
            return default
        return v if v >= 1 else default

    @staticmethod
    def _get_room_module_name(room_name: str) -> str:
        """Python module name for a room's scene file: non-identifier
        characters become underscores ("level 1" -> "level_1"), matching
        _get_object_module_name. ROOM_ORDER / ROOM_CLASSES keep the ORIGINAL
        room name as the lookup key; only the scene filename, its import,
        and the class identifier are sanitized (KA-H1)."""
        import re
        sanitized = re.sub(r'\W', '_', room_name)
        if not sanitized or sanitized[0].isdigit():
            sanitized = f"room_{sanitized}"
        return sanitized

    def _get_room_class_name(self, room_name: str) -> str:
        """Convert a room name to a valid PascalCase class identifier.

        Sanitizes first: a room named "level 1" (space) or "1_intro"
        (leading digit) — common in GMK imports, like maze_3's "obj
        trigger" object — otherwise emitted `class Level 1(Widget):` /
        `scenes/level 1.py`, a SyntaxError that broke the whole export."""
        cls = ''.join(
            word.capitalize()
            for word in self._get_room_module_name(room_name).split('_') if word)
        # A punctuation-only name reduces to all-underscores -> empty class
        # name -> `class (Widget):` SyntaxError (KA-L1).
        return cls or 'Room'

    @staticmethod
    def _get_object_module_name(obj_name: str) -> str:
        """Python module name for an object: non-identifier characters
        become underscores ("obj trigger" -> "obj_trigger"). Registry keys
        and create_instance lookups keep the ORIGINAL name; only module
        filenames / import statements / class names need sanitizing."""
        import re
        sanitized = re.sub(r'\W', '_', obj_name)
        if not sanitized or sanitized[0].isdigit():
            sanitized = f"obj_{sanitized}"
        return sanitized

    def _get_object_class_name(self, obj_name: str) -> str:
        """Convert object name to a valid PascalCase class identifier.

        Sanitizes first: maze_3 ships an object named "obj trigger" (space,
        from the GMK import) which used to emit `class Obj trigger` — a
        SyntaxError that made the whole maze_3 Kivy export unimportable.
        """
        cls = ''.join(
            word.capitalize()
            for word in self._get_object_module_name(obj_name).split('_') if word)
        # A punctuation-only name reduces to all-underscores -> empty class
        # name -> `class (GameObject):` SyntaxError (KA-L1).
        return cls or 'Obj'


def export_to_kivy(project_data: Dict[str, Any], project_path: Path,
                   output_path: Path) -> bool:
    """
    Export a PyGameMaker project to Kivy format

    Args:
        project_data: Project data dictionary
        project_path: Path to project directory
        output_path: Output directory for export

    Returns:
        True if export successful, False otherwise
    """
    exporter = KivyExporter(project_data, project_path, output_path)
    return exporter.export()
