#!/usr/bin/env python3
"""
HTML5 Game Exporter for PyGameMaker
Exports projects as standalone HTML5 games with GameMaker 7.0 compatibility
"""

import json
import base64
import gzip
import html
from pathlib import Path
from typing import Dict, Optional

from core.logger import get_logger
logger = get_logger(__name__)


def project_needs_python(project_data: Dict) -> bool:
    """True if any object event (top level, nested branches, keyboard
    sub-maps) contains an execute_code action. Python port of
    engine.js's PythonBridge.projectNeedsPython, kept in exact sync with
    it — used here only to decide whether the offline Pyodide bundle is
    worth embedding (~17 MB); the JS copy still runs at play time to
    decide whether to load Pyodide at all in the first place."""
    def scan_actions(actions):
        for a in (actions or []):
            if not isinstance(a, dict):
                continue
            if a.get('action') == 'execute_code' or a.get('action_type') == 'execute_code':
                return True
            p = a.get('parameters') or {}
            if (scan_actions(p.get('then_actions')) or scan_actions(p.get('else_actions'))
                    or scan_actions(p.get('actions')) or scan_actions(a.get('sub_actions'))):
                return True
        return False

    objects = (project_data.get('assets') or {}).get('objects') or {}
    for obj in objects.values():
        if not isinstance(obj, dict):
            continue
        for ev in (obj.get('events') or {}).values():
            if not isinstance(ev, dict):
                continue
            if scan_actions(ev.get('actions')):
                return True
            for sub in ev.values():
                if isinstance(sub, dict) and scan_actions(sub.get('actions')):
                    return True
    return False


def _sanitize_filename(name: str) -> str:
    """Reduce a project name to a filesystem-safe basename.

    Replaces the characters illegal in a Windows filename (< > : " / \\ |
    ? * and control chars) with '_', and trims trailing dots/spaces (also
    illegal on Windows). The project's real name is preserved in the page
    itself (HTML-escaped); this only guards the file on disk.
    """
    import re
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    return cleaned.strip(' .')


class HTML5Exporter:
    """Export PyGameMaker projects to HTML5"""

    EXTENSION_JS_MARKER = "// __PYGM_EXTENSION_JS__"

    def __init__(self):
        # export()'s outer try/except is intentionally broad (catches and
        # logs any failure, returns False) — this preserves a specific,
        # actionable message (e.g. the offline-bundle download failure's
        # "internet access... uncheck it to..." text) for the caller to
        # surface in the UI instead of it being lost to the console log.
        self.last_error_message = None

        # Load templates from files
        template_dir = Path(__file__).parent / "templates"
        self.template_html = (template_dir / "game_template.html").read_text(encoding='utf-8')
        engine_code = (template_dir / "engine.js").read_text(encoding='utf-8')
        # Vendored inline (not loaded from a CDN <script src>) so every
        # HTML5 export is a genuinely self-contained single .html file --
        # gzip decompression of game_data/sprites_data/sounds_data needs it
        # unconditionally, so unlike the Pyodide bundle below this is never
        # optional. resources/vendor/pako.min.js is MIT+Zlib licensed
        # (license comment preserved verbatim on embed).
        pako_path = Path(__file__).resolve().parents[2] / "resources" / "vendor" / "pako.min.js"
        self.pako_code = pako_path.read_text(encoding='utf-8')
        # Stage C: concatenate each enabled extension's export_html5.js at the
        # marker, so engine.js stays extension-agnostic (the raycast renderer
        # and its actions ship from extensions/raycast_2_5d/export_html5.js).
        self.engine_code = engine_code.replace(
            self.EXTENSION_JS_MARKER, self._collect_extension_js())

    def _collect_extension_js(self) -> str:
        """The engine JS contributed by every ENABLED extension (Stage C).

        An extension ships an ``export_html5.js`` alongside its manifest; the
        loader's enable/disable config is honoured so a switched-off extension
        contributes nothing. engine.js concatenates these at
        ``EXTENSION_JS_MARKER`` — it never names a specific extension.
        """
        try:
            from events.plugin_loader import (
                list_available_extensions, get_extension_directory)
            ext_dir = get_extension_directory()
        except Exception as exc:  # never let extension collection break export
            logger.warning(f"Could not enumerate extensions for JS: {exc}")
            return ""
        parts = []
        for info in list_available_extensions():
            if not info.get("enabled", True):
                continue
            js_file = ext_dir / info["folder"] / "export_html5.js"
            if not js_file.exists():
                continue
            # Per-extension guard: one unreadable extension must not silently
            # drop EVERY extension's JS from the exported engine.
            try:
                parts.append(f"// --- extension: {info['folder']} ---\n"
                             + js_file.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.error(
                    f"Extension '{info['folder']}' export_html5.js could not be "
                    f"read; it is missing from the export: {exc}")
        return "\n".join(parts)

    EMBEDDED_PYODIDE_MARKER = "const EMBEDDED_PYODIDE = null; // __PYGM_EMBEDDED_PYODIDE_MARKER__"

    def _build_offline_pyodide_engine_code(self, progress_callback=None) -> str:
        """self.engine_code with EMBEDDED_PYODIDE filled in from the
        (downloaded-once, then cached) Pyodide core files -- see
        export/HTML5/pyodide_bundle.py. Raises RuntimeError (propagated
        to the caller, matching every other export failure path) if the
        files can't be obtained."""
        from export.HTML5.pyodide_bundle import ensure_pyodide_files, MIME_TYPES

        files = ensure_pyodide_files(progress_callback=progress_callback)
        embedded = {}
        for filename, data in files.items():
            if MIME_TYPES.get(filename, '').startswith('text/'):
                # Plain JS text compresses well; the exact inverse of
                # engine.js's PythonBridge._b64GzipToText.
                embedded[filename] = base64.b64encode(
                    gzip.compress(data, compresslevel=9)).decode('ascii')
            else:
                # pyodide.asm.wasm / pyodide-lock.json / python_stdlib.zip
                # are already-compressed formats; embedded as-is (the
                # latter two double as the literal payload of a
                # data:...;base64,<this> URI on the JS side, so they must
                # stay plain base64, not gzip-then-base64).
                embedded[filename] = base64.b64encode(data).decode('ascii')

        embedded_json = json.dumps(embedded, separators=(',', ':'))
        return self.engine_code.replace(
            self.EMBEDDED_PYODIDE_MARKER,
            f"const EMBEDDED_PYODIDE = {embedded_json};")

    def export(self, project_path: Path, output_path: Path,
               export_settings: Optional[Dict] = None,
               progress_callback=None) -> bool:
            """Export project to HTML5"""
            export_settings = export_settings or {}
            self.last_error_message = None
            try:
                logger.info(f"Exporting {project_path.name} to HTML5...")

                # Load project
                project_file = project_path / "project.json"
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)

                # Load room instances and object events from external files.
                # project.json's embedded object bodies can be stale (the IDE
                # only rewrites them on save; objects/<name>.json is the
                # source of truth the project loader also prefers), so
                # exporting without the merge shipped outdated events.
                self._load_room_instances(project_path, project_data)
                self._load_object_files(project_path, project_data)
                self._load_sprite_files(project_path, project_data)
                self._collect_extension_data(project_path, project_data)

                # A nameless (malformed/hand-edited) project.json must not
                # KeyError the whole export — default to 'game' (finding #4).
                project_name = project_data.get('name', 'game')
                logger.info(f"  Loaded project: {project_name}")

                # Offline Pyodide bundle (TODO.md: "Pyodide loads from the
                # jsDelivr CDN — a Python-using game needs internet on
                # first open"). Opt-in and only worth the ~17 MB it adds
                # when the project actually uses execute_code — a pure-
                # action game gets the default engine_code unchanged.
                engine_code_for_export = self.engine_code
                if export_settings.get('offline_pyodide') and project_needs_python(project_data):
                    logger.info("  Bundling offline Python runtime (Pyodide)...")
                    engine_code_for_export = self._build_offline_pyodide_engine_code(
                        progress_callback)

                # Encode sprites as base64
                logger.info("  Encoding sprites...")
                sprites_data = self.encode_sprites(project_path, project_data)
                logger.info(f"  Encoded {len(sprites_data)} sprites")

                # Encode sounds as base64 (browser-playable formats only)
                sounds_data = self.encode_sounds(project_path, project_data)
                logger.info(f"  Encoded {len(sounds_data)} sounds")

                # Get window size from settings or room dimensions
                settings = project_data.get('settings', {})
                width = settings.get('window_width')
                height = settings.get('window_height')

                # If no settings, use first room dimensions
                if not width or not height:
                    rooms = project_data.get('assets', {}).get('rooms', {})
                    if rooms:
                        first_room = next(iter(rooms.values()))
                        width = first_room.get('width', 1024)
                        height = first_room.get('height', 768)
                    else:
                        width = settings.get('window_width', 1024)
                        height = settings.get('window_height', 768)

                logger.info(f"  Canvas size: {width}x{height}")

                # Generate HTML
                logger.info("  Generating HTML...")

                # Serialize the data
                game_data_json = json.dumps(project_data, separators=(',', ':'))
                sprites_data_json = json.dumps(sprites_data, separators=(',', ':'))

                logger.debug("  Original sizes:")
                logger.debug(f"     Game data: {len(game_data_json):,} bytes")
                logger.debug(f"     Sprites data: {len(sprites_data_json):,} bytes")

                # Compress the data using gzip
                game_data_compressed = base64.b64encode(
                    gzip.compress(game_data_json.encode('utf-8'), compresslevel=9)
                ).decode('ascii')

                sprites_data_compressed = base64.b64encode(
                    gzip.compress(sprites_data_json.encode('utf-8'), compresslevel=9)
                ).decode('ascii')

                sounds_data_json = json.dumps(sounds_data, separators=(',', ':'))
                sounds_data_compressed = base64.b64encode(
                    gzip.compress(sounds_data_json.encode('utf-8'), compresslevel=9)
                ).decode('ascii')

                compression_ratio_game = (len(game_data_compressed) * 100) // len(game_data_json)
                compression_ratio_sprites = (len(sprites_data_compressed) * 100) // len(sprites_data_json)

                logger.debug("  Compressed sizes:")
                logger.debug(f"     Game data: {len(game_data_compressed):,} bytes ({compression_ratio_game}%)")
                logger.debug(f"     Sprites data: {len(sprites_data_compressed):,} bytes ({compression_ratio_sprites}%)")
                logger.debug(f"  Total size reduction: {len(game_data_json) + len(sprites_data_json) - len(game_data_compressed) - len(sprites_data_compressed):,} bytes saved")

                # Replace placeholders. The project name lands in HTML text
                # context (<title> and the title <div>), so escape it — a
                # legitimate name with '&' or '<' would otherwise corrupt the
                # markup (and in principle inject). width/height are ints and
                # the data blobs are base64, so those need no escaping (L1).
                html_content = self.template_html.replace(
                    '{game_name}', html.escape(str(project_name)))
                html_content = html_content.replace('{width}', str(width))
                html_content = html_content.replace('{height}', str(height))
                html_content = html_content.replace('{game_data}', f'"{game_data_compressed}"')
                html_content = html_content.replace('{sprites_data}', f'"{sprites_data_compressed}"')
                html_content = html_content.replace('{sounds_data}', f'"{sounds_data_compressed}"')
                html_content = html_content.replace('{pako_code}', self.pako_code)
                html_content = html_content.replace('{engine_code}', engine_code_for_export)

                # Write output. Sanitize the name for the FILENAME —
                # characters legal in a project name but illegal in a
                # filename (< > : " / \ | ? * and control chars) otherwise
                # crash the write on Windows (e.g. a name like "Level 1: Go"
                # or "Tom & <Jerry>"). The in-page title keeps the real
                # (HTML-escaped) name; only the file on disk is sanitized.
                safe_name = _sanitize_filename(str(project_name)) or "game"
                output_file = output_path / f"{safe_name}.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                file_size_kb = output_file.stat().st_size / 1024

                logger.info("  Export complete!")
                logger.info(f"  File: {output_file.name}")
                logger.info(f"  Size: {file_size_kb:.1f} KB")
                logger.info(f"Open {output_file.name} in a web browser to play!")

                return True

            except Exception as e:
                logger.error(f"Export failed: {e}")
                import traceback
                traceback.print_exc()
                self.last_error_message = str(e)
                return False

    def _load_room_instances(self, project_path: Path, project_data: Dict) -> None:
        """Load room instances from external room files into project_data"""
        rooms_data = project_data.get('assets', {}).get('rooms', {})
        rooms_dir = project_path / "rooms"

        for room_name, room_data in rooms_data.items():
            # A non-dict room value (a string reference, as the object loader
            # tolerates) must not AttributeError before the try below and
            # abort the whole export (finding #3).
            if not isinstance(room_data, dict):
                continue
            # Check if this room has an external file reference
            external_file = room_data.get('_external_file')
            if external_file:
                room_file = project_path / external_file
            else:
                # Try default location
                room_file = rooms_dir / f"{room_name}.json"

            if room_file.exists():
                try:
                    with open(room_file, 'r', encoding='utf-8') as f:
                        external_room_data = json.load(f)
                    # Merge instances from external file
                    if 'instances' in external_room_data:
                        room_data['instances'] = external_room_data['instances']
                        logger.debug(f"  Loaded {len(room_data['instances'])} instances for room: {room_name}")
                except Exception as e:
                    logger.warning(f"  Failed to load room file {room_file}: {e}")

    def _collect_extension_data(self, project_path: Path, project_data: Dict) -> None:
        """Merge each enabled extension's export-time data contribution into
        ``project_data['_extension_data']`` (Stage C-style, generalising the
        JS-code injection hook to DATA rather than code).

        An extension that needs project-relative files at runtime (Block
        World's ``load_block_world`` reads a JSON world file the desktop
        runtime opens directly off disk -- a browser export has no
        filesystem) ships an optional ``export_data.py`` exposing
        ``collect_export_data(project_path, project_data) -> dict``. Its
        return value is merged in here, at export time, so the exported page
        stays a single self-contained HTML file exactly like sprites/sounds
        already are (base64-embedded, never a second file the browser would
        have to fetch). engine.js never names a specific extension; this
        method doesn't either -- ``project_data['_extension_data']`` is
        reached at runtime via ``game.gameData._extension_data``, keyed
        however each extension's own JS chooses to key it.
        """
        try:
            from events.plugin_loader import (
                list_available_extensions, get_extension_directory)
            ext_dir = get_extension_directory()
        except Exception as exc:  # never let extension collection break export
            logger.warning(f"Could not enumerate extensions for data: {exc}")
            return
        merged = project_data.setdefault('_extension_data', {})
        for info in list_available_extensions():
            if not info.get("enabled", True):
                continue
            data_file = ext_dir / info["folder"] / "export_data.py"
            if not data_file.exists():
                continue
            # Per-extension guard: one broken extension must not silently
            # drop every other extension's export data.
            try:
                # __file__ isn't populated automatically inside an exec()'d
                # namespace (unlike a real import) -- set it so a
                # collect_export_data that resolves paths relative to its
                # own file (e.g. block_world's texture directory) works.
                ns = {"__file__": str(data_file)}
                exec(compile(data_file.read_text(encoding="utf-8"),
                             str(data_file), "exec"), ns)
                collector = ns.get("collect_export_data")
                if callable(collector):
                    extra = collector(project_path, project_data)
                    if isinstance(extra, dict):
                        merged.update(extra)
            except Exception as exc:
                logger.error(
                    f"Extension '{info['folder']}' export_data.py failed; "
                    f"its export data is missing from the export: {exc}")

    def _load_object_files(self, project_path: Path, project_data: Dict) -> None:
        """Merge objects/<name>.json side files into project_data (file wins),
        matching the project loader's precedence (merge_object_file)."""
        from utils.project_file_merge import merge_object_file

        objects_data = project_data.get('assets', {}).get('objects', {})
        objects_dir = project_path / "objects"
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
                    logger.debug(f"  Merged object file: {object_name}")
                except Exception as e:
                    logger.warning(f"  Failed to load object file {object_file}: {e}")

    def _load_sprite_files(self, project_path: Path, project_data: Dict) -> None:
        """Merge sprites/<name>.json side files into project_data (file wins),
        matching the project loader's precedence (merge_sprite_file).

        project.json's embedded sprite entries are stubs since sprites were
        manifest-ified (Tier 6) -- without this merge, encode_sprites (below)
        and every sprite field the shipped gameData carries for engine.js at
        browser runtime (frame_width/origin_x/animation_type/collision_mask/
        etc.) would silently go missing from every export."""
        from utils.project_file_merge import merge_sprite_file

        sprites_data = project_data.get('assets', {}).get('sprites', {})
        sprites_dir = project_path / "sprites"
        if not sprites_dir.exists():
            return

        for sprite_name, sprite_data in list(sprites_data.items()):
            if isinstance(sprite_data, str):
                sprite_data = {"name": sprite_name, "asset_type": "sprite"}
                sprites_data[sprite_name] = sprite_data
            sprite_file = sprites_dir / f"{sprite_name}.json"
            if sprite_file.exists():
                try:
                    with open(sprite_file, 'r', encoding='utf-8') as f:
                        file_sprite_data = json.load(f)
                    merge_sprite_file(sprite_data, file_sprite_data)
                    logger.debug(f"  Merged sprite file: {sprite_name}")
                except Exception as e:
                    logger.warning(f"  Failed to load sprite file {sprite_file}: {e}")

    # Formats browsers can decode via <audio>/Audio(); .mid/.midi have no
    # browser support and are skipped with a warning.
    _SOUND_MIME = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.ogg': 'audio/ogg',
        '.m4a': 'audio/mp4',
    }

    def encode_sounds(self, project_path: Path, project_data: Dict) -> Dict[str, str]:
        """Encode project sounds as base64 data URLs for the play_sound action."""
        encoded = {}
        sounds_data = project_data.get('assets', {}).get('sounds', {})
        for sound_name, sound_info in sounds_data.items():
            if not isinstance(sound_info, dict):
                continue
            file_path = sound_info.get('file_path', '')
            if not file_path:
                continue
            full_path = project_path / file_path
            if not full_path.exists():
                logger.warning(f"  Sound file not found: {full_path}")
                continue
            mime = self._SOUND_MIME.get(full_path.suffix.lower())
            if not mime:
                logger.warning(
                    f"  Skipping sound '{sound_name}': {full_path.suffix} has no "
                    f"browser playback support")
                continue
            try:
                b64 = base64.b64encode(full_path.read_bytes()).decode('utf-8')
                encoded[sound_name] = f"data:{mime};base64,{b64}"
            except Exception as e:
                logger.warning(f"  Failed to encode sound {sound_name}: {e}")
        return encoded

    def encode_sprites(self, project_path: Path, project_data: Dict) -> Dict[str, str]:
        """Encode sprites and backgrounds as base64 data URLs"""
        encoded = {}

        # Encode sprites
        sprites_data = project_data.get('assets', {}).get('sprites', {})
        for sprite_name, sprite_info in sprites_data.items():
            # A non-dict entry (a bare string path — a form the loaders
            # elsewhere tolerate) must not AttributeError and abort the
            # WHOLE export; skip it like encode_sounds does (finding #2).
            if not isinstance(sprite_info, dict):
                logger.warning(f"  Skipping sprite '{sprite_name}': unexpected entry type")
                continue
            file_path = sprite_info.get('file_path', '')
            if not file_path:
                # A missing file used to be dropped SILENTLY with a success
                # dialog — the user shipped invisible art with zero signal.
                # Log it, mirroring encode_sounds (finding #1).
                logger.warning(f"  Sprite '{sprite_name}' has no file_path; not encoded")
                continue
            full_path = project_path / file_path
            if not full_path.exists():
                logger.warning(f"  Sprite file not found for '{sprite_name}': {full_path}")
                continue
            try:
                with open(full_path, 'rb') as f:
                    sprite_bytes = f.read()
                    b64 = base64.b64encode(sprite_bytes).decode('utf-8')

                    # Detect image type
                    ext = full_path.suffix.lower()
                    mime_type = 'image/png'
                    if ext == '.jpg' or ext == '.jpeg':
                        mime_type = 'image/jpeg'
                    elif ext == '.gif':
                        mime_type = 'image/gif'

                    encoded[sprite_name] = f"data:{mime_type};base64,{b64}"
            except Exception as e:
                logger.warning(f"  Failed to encode {sprite_name}: {e}")

        # Encode backgrounds (same guards/logging as sprites, #1/#2)
        backgrounds_data = project_data.get('assets', {}).get('backgrounds', {})
        for bg_name, bg_info in backgrounds_data.items():
            if not isinstance(bg_info, dict):
                logger.warning(f"  Skipping background '{bg_name}': unexpected entry type")
                continue
            file_path = bg_info.get('file_path', '')
            if not file_path:
                logger.warning(f"  Background '{bg_name}' has no file_path; not encoded")
                continue
            full_path = project_path / file_path
            if not full_path.exists():
                logger.warning(f"  Background file not found for '{bg_name}': {full_path}")
                continue
            try:
                with open(full_path, 'rb') as f:
                    bg_bytes = f.read()
                    b64 = base64.b64encode(bg_bytes).decode('utf-8')

                    ext = full_path.suffix.lower()
                    mime_type = 'image/png'
                    if ext == '.jpg' or ext == '.jpeg':
                        mime_type = 'image/jpeg'

                    encoded[bg_name] = f"data:{mime_type};base64,{b64}"
            except Exception as e:
                logger.warning(f"  Failed to encode background {bg_name}: {e}")

        return encoded


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        logger.info("Usage: python html5_exporter.py <project_path> <output_directory>")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not project_path.exists():
        logger.error(f"Project path not found: {project_path}")
        sys.exit(1)

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    exporter = HTML5Exporter()
    success = exporter.export(project_path, output_path)

    sys.exit(0 if success else 1)
