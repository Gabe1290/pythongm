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
from export.message_localizer import resolve_translations
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


_GENERIC_ICON_PATH = Path(__file__).resolve().parent.parent.parent / "resources" / "icon.png"


def _write_pwa_icons(output_path: Path, icon_source: Optional[Path]) -> list:
    """Resize icon_source (or the generic pygm2 icon as fallback) into the
    two sizes a PWA manifest needs, written under assets/icons/. Returns
    the manifest.json "icons" list, or [] if no usable source image exists
    (a missing/corrupt icon must not fail the whole export -- the manifest
    just omits icons, and installability degrades gracefully)."""
    source = icon_source if (icon_source and icon_source.exists()) else _GENERIC_ICON_PATH
    if not source.exists():
        return []
    try:
        from PIL import Image
        img = Image.open(source).convert("RGBA")
    except Exception:
        logger.warning("PWA icon source %s could not be read; skipping icons", source)
        return []

    icons_dir = output_path / "assets" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    icons = []
    for size in (192, 512):
        resized = img.resize((size, size), Image.LANCZOS)
        dest = icons_dir / f"icon-{size}.png"
        resized.save(dest, "PNG")
        icons.append({
            "src": f"assets/icons/icon-{size}.png",
            "sizes": f"{size}x{size}",
            "type": "image/png",
        })
    return icons


def _write_pwa_manifest(output_path: Path, project_name: str, html_filename: str,
                        icon_source: Optional[Path]) -> None:
    """Write manifest.json for an installable PWA (docs/EXPORT_POLISH_PLAN.md
    item 1 Phase 4). Only meaningful alongside external_assets folder mode
    -- the single-file inline export is already fully offline the instant
    it's downloaded, nothing to install/cache in front of it."""
    icons = _write_pwa_icons(output_path, icon_source)
    manifest = {
        "name": str(project_name),
        "short_name": str(project_name)[:30],
        "start_url": f"./{html_filename}",
        "scope": "./",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#764ba2",
        "icons": icons,
    }
    (output_path / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding='utf-8')


def _write_pwa_service_worker(output_path: Path, html_filename: str,
                              external_files: list) -> None:
    """Write sw.js: a minimal cache-first service worker so the exported
    folder keeps working offline after the first successful load (the
    thing a PWA install is actually for). Cache-first, not
    network-first -- a classroom game shouldn't re-fetch assets it
    already has just because the network happens to be flaky that day."""
    cache_list = ['"./"', f'"./{html_filename}"'] + [
        json.dumps(f) for f in external_files
    ]
    sw_js = (
        "const CACHE_NAME = 'pygm-game-v1';\n"
        "const ASSETS_TO_CACHE = [\n    " + ",\n    ".join(cache_list) + "\n];\n\n"
        "self.addEventListener('install', event => {\n"
        "    event.waitUntil(\n"
        "        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS_TO_CACHE))\n"
        "    );\n"
        "    self.skipWaiting();\n"
        "});\n\n"
        "self.addEventListener('activate', event => {\n"
        "    event.waitUntil(\n"
        "        caches.keys().then(names => Promise.all(\n"
        "            names.filter(name => name !== CACHE_NAME).map(name => caches.delete(name))\n"
        "        ))\n"
        "    );\n"
        "    self.clients.claim();\n"
        "});\n\n"
        "self.addEventListener('fetch', event => {\n"
        "    event.respondWith(\n"
        "        caches.match(event.request).then(cached => cached || fetch(event.request))\n"
        "    );\n"
        "});\n"
    )
    (output_path / "sw.js").write_text(sw_js, encoding='utf-8')


def _copy_asset_file(full_path: Path, dest_dir: Path, asset_name: str,
                      url_prefix: str) -> str:
    """Copy full_path into dest_dir (creating it if needed), named after
    the sanitized asset_name with its original extension kept, and return
    the URL path (always forward slashes -- this is a URL, not an OS path,
    so str(Path(...)) would silently break on Windows) the exported page
    should reference it by.

    Two different asset names that happen to sanitize to the same
    filesystem-safe name must not silently overwrite each other and lose
    one asset's data -- disambiguated with a numeric suffix instead."""
    import shutil
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _sanitize_filename(asset_name) or "asset"
    suffix = full_path.suffix.lower()
    dest_path = dest_dir / f"{safe_name}{suffix}"
    n = 1
    while dest_path.exists():
        dest_path = dest_dir / f"{safe_name}_{n}{suffix}"
        n += 1
    shutil.copy2(full_path, dest_path)
    return f"{url_prefix}/{dest_path.name}"


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

                # Bake authored translations into the plain parameters, AFTER
                # the side-file merges above. engine.js has no notion of
                # translation dicts and deliberately is not being given one --
                # see export/message_localizer.py.
                project_data = resolve_translations(
                    project_data, export_settings.get('language', 'en'))

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

                # External-asset export mode (docs/EXPORT_POLISH_PLAN.md item
                # 1): opt-in, default off -- every existing export keeps
                # producing one self-contained .html file that works via
                # double-click with no server (a real, load-bearing property:
                # relative-path assets need real HTTP, file:// blocks fetch/
                # Image.src/Audio.src for a separate-origin-looking file in
                # most browsers). When on, sprites/sounds are copied as real
                # files under assets/ instead of base64-embedded.
                external_assets = bool(export_settings.get('external_assets'))
                assets_dir = (output_path / "assets") if external_assets else None

                # Encode sprites (base64, or copied as files -- see above)
                logger.info("  Encoding sprites...")
                sprites_data = self.encode_sprites(project_path, project_data, assets_dir)
                logger.info(f"  Encoded {len(sprites_data)} sprites")

                # Encode sounds (browser-playable formats only)
                sounds_data = self.encode_sounds(project_path, project_data, assets_dir)
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

                # Sanitize the name for the FILENAME — characters legal in a
                # project name but illegal in a filename (< > : " / \ | ? *
                # and control chars) otherwise crash the write on Windows
                # (e.g. a name like "Level 1: Go" or "Tom & <Jerry>"). The
                # in-page title keeps the real (HTML-escaped) name; only the
                # file on disk is sanitized. Computed here (not just before
                # writing) because the PWA manifest's start_url needs it too.
                safe_name = _sanitize_filename(str(project_name)) or "game"
                html_filename = f"{safe_name}.html"

                # pako/engine.js: inlined (default) or written as their own
                # files and referenced by <script src=...> (external_assets).
                # engine.js itself needs no changes for this switch -- it
                # only reads gameData/spritesData/soundsData/pako as
                # already-set globals, which a later <script> (external or
                # not) can see identically; see this module's docstring.
                if external_assets:
                    (output_path / "pako.min.js").write_text(
                        self.pako_code, encoding='utf-8')
                    (output_path / "engine.js").write_text(
                        engine_code_for_export, encoding='utf-8')
                    pako_script_tag = '<script src="pako.min.js"></script>'
                    engine_script_tag = '<script src="engine.js"></script>'
                    self._write_external_assets_readme(output_path)
                else:
                    pako_script_tag = f'<script>{self.pako_code}</script>'
                    engine_script_tag = f'<script>\n{engine_code_for_export}\n</script>'
                html_content = html_content.replace('{pako_script_tag}', pako_script_tag)
                html_content = html_content.replace('{engine_script_tag}', engine_script_tag)

                # PWA manifest + service worker (docs/EXPORT_POLISH_PLAN.md
                # item 1 Phase 4): opt-in, and only meaningful alongside
                # external_assets -- the single-file inline export is
                # already fully offline the instant it's downloaded, so
                # there's nothing a service worker would add in front of it.
                pwa = bool(export_settings.get('pwa')) and external_assets
                if pwa:
                    icon_setting = export_settings.get('icon_path')
                    icon_source = Path(icon_setting) if icon_setting else None
                    _write_pwa_manifest(output_path, project_name, html_filename, icon_source)
                    external_files = [
                        f"./{p.relative_to(output_path).as_posix()}"
                        for p in sorted(output_path.rglob('*')) if p.is_file()
                    ]
                    _write_pwa_service_worker(output_path, html_filename, external_files)
                    pwa_head_tags = (
                        '<link rel="manifest" href="manifest.json">\n'
                        '    <meta name="theme-color" content="#764ba2">'
                    )
                    pwa_sw_register_script = (
                        "<script>\n"
                        "        if ('serviceWorker' in navigator) {\n"
                        "            window.addEventListener('load', () => {\n"
                        "                navigator.serviceWorker.register('./sw.js').catch(err =>\n"
                        "                    console.warn('Service worker registration failed:', err));\n"
                        "            });\n"
                        "        }\n"
                        "    </script>"
                    )
                else:
                    pwa_head_tags = ''
                    pwa_sw_register_script = ''
                html_content = html_content.replace('{pwa_head_tags}', pwa_head_tags)
                html_content = html_content.replace('{pwa_sw_register_script}', pwa_sw_register_script)

                # On-screen d-pad / action buttons (reported: HTML5-exported
                # games were unplayable on a phone -- no keyboard, and
                # nothing to tap). Only emitted when the project actually
                # binds a keyboard event; engine.js's setupTouchControls()
                # additionally only ever reveals it on a real touchscreen.
                needs_dpad, action_keys = self._detect_keyboard_controls(project_data)
                touch_controls_html = self._build_touch_controls_html(needs_dpad, action_keys)
                html_content = html_content.replace('{touch_controls_html}', touch_controls_html)

                # Write output.
                output_file = output_path / html_filename
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

    def _write_external_assets_readme(self, output_path: Path) -> None:
        """external_assets mode writes a folder, not one file -- unlike the
        default export, opening index.html straight off disk (file://)
        will NOT work in most browsers, since a relative-path fetch/
        Image.src/Audio.src from a file:// page is blocked by the
        same-origin policy. That surprise needs to be caught before a
        teacher tries it and gets a blank page, not after."""
        readme = (
            "This export is a FOLDER, not a single file -- it needs a real "
            "web server, not double-clicking the .html file.\n\n"
            "Opening it directly from disk (a file:// URL) will show a "
            "blank page in most browsers: the game's sprites and sounds "
            "are separate files next to the HTML, and browsers block a "
            "page loaded from disk from fetching its own neighboring "
            "files for security reasons.\n\n"
            "To play it locally, run this in the folder and then open the "
            "printed address in a browser:\n\n"
            "    python -m http.server\n\n"
            "To publish it, upload the whole folder (the .html file, "
            "engine.js, pako.min.js, and the assets/ folder) to any web "
            "host -- GitHub Pages, itch.io, or your school's site all "
            "work.\n"
        )
        (output_path / "README-hosting.txt").write_text(readme, encoding='utf-8')

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

            self._fill_auto_collision_bbox(project_path, sprite_data)

    def _fill_auto_collision_bbox(self, project_path: Path, sprite_data: Dict) -> None:
        """Auto-derive bbox_left/top/right/bottom (frame 0's opaque-pixel
        bounds) when the author hasn't set an explicit override, mirroring
        runtime/game_runner.py's GameSprite._compute_collision_bbox (a
        pygame.mask bounding-rect union) -- but via PIL, the image library
        this exporter already imports, so no pygame dependency here.

        Without this, engine.js's makeSpriteInfo (export/HTML5/templates/
        engine.js) always fell back to the full sprite frame as the
        collision box (its own comment already flagged the gap: "without
        this the collision box here silently defaulted to the full frame"
        -- the reading side existed, nothing ever populated it). Any sprite
        with transparent padding then had a taller/wider real-world hitbox
        on HTML5 than on desktop -- found via the promo game's platform
        level: desktop's penguin sprite auto-trims to a 30px collision
        height (1px transparent padding top AND bottom of a 32px frame),
        letting it pass through a 32px gap and rest flush on the ground;
        HTML5's untrimmed 32px box couldn't fit the same gap, and rendered
        the sprite hovering ~1px above a flush landing (the collision
        box's bottom, at the frame's true edge, sits below where the
        sprite's own opaque pixels actually end).
        """
        if all(k in sprite_data for k in ('bbox_left', 'bbox_top', 'bbox_right', 'bbox_bottom')):
            return  # explicit author override -- already correct, don't touch
        file_path = sprite_data.get('file_path') or sprite_data.get('image_file')
        if not file_path:
            return
        full_path = project_path / file_path
        if not full_path.exists():
            return
        try:
            from PIL import Image
            img = Image.open(full_path).convert("RGBA")
        except Exception as e:
            logger.debug(f"  bbox auto-derive: could not open {full_path}: {e}")
            return

        width = int(sprite_data.get('width') or img.width)
        height = int(sprite_data.get('height') or img.height)
        frames = max(1, int(sprite_data.get('frames') or 1))
        frame_width = int(sprite_data.get('frame_width') or (width // frames if frames > 1 else width))
        frame_height = int(sprite_data.get('frame_height') or height)
        # Frame 0 is always the top-left frame_width x frame_height region,
        # regardless of animation_type (single/strip_h/strip_v/grid) --
        # clamped so a stale/mismatched metadata field can't crop outside
        # the actual image.
        frame_width = max(1, min(frame_width, img.width))
        frame_height = max(1, min(frame_height, img.height))
        frame0 = img.crop((0, 0, frame_width, frame_height))
        bbox = frame0.split()[-1].getbbox()  # alpha channel's non-zero bounds
        if bbox is None:
            return  # fully transparent frame -- leave unset, engine.js falls back to full frame
        sprite_data['bbox_left'] = bbox[0]
        sprite_data['bbox_top'] = bbox[1]
        sprite_data['bbox_right'] = bbox[2]
        sprite_data['bbox_bottom'] = bbox[3]

    # left/right/up/down cover both arrow keys and their WASD equivalents --
    # either binding means the game has directional movement, so the on-
    # screen control is a single d-pad either way, matching the (arrows-
    # only) virtual D-pad export/Kivy/kivy_exporter.py already ships for
    # Android (VirtualDPad / NEEDS_DPAD).
    _MOVEMENT_KEY_NAMES = {'left', 'right', 'up', 'down', 'w', 'a', 's', 'd'}
    # GM event markers, not physical keys -- never a button.
    _PSEUDO_KEY_NAMES = {'nokey', 'anykey'}
    _ACTION_KEY_LABELS = {
        'space': '⎵', 'enter': '⏎', 'escape': 'Esc', 'tab': 'Tab',
        'backspace': '⌫', 'delete': 'Del',
    }

    def _detect_keyboard_controls(self, project_data: Dict):
        """Scan every object's keyboard/keyboard_press/keyboard_release
        events for the key names actually bound anywhere in the project.

        Returns (needs_dpad, action_keys): needs_dpad is True if any
        movement key (arrows or WASD) is bound anywhere; action_keys is
        the sorted list of every OTHER real key bound (e.g. "space", "z"),
        each becoming its own on-screen button -- e.g. Sky Strike binds
        space (shoot) and z (bomb) on top of its arrow/WASD movement, so
        it gets a d-pad plus two action buttons; a project with no
        keyboard events at all (e.g. a mouse/touch-only puzzle) gets
        neither, and _build_touch_controls_html then emits nothing.
        """
        used = set()
        for obj_data in project_data.get('assets', {}).get('objects', {}).values():
            if not isinstance(obj_data, dict):
                continue
            events = obj_data.get('events', {})
            if not isinstance(events, dict):
                continue
            for event_name in ('keyboard', 'keyboard_press', 'keyboard_release'):
                event_data = events.get(event_name)
                if isinstance(event_data, dict):
                    for key in event_data.keys():
                        used.add(str(key).lower())
        used -= self._PSEUDO_KEY_NAMES
        needs_dpad = bool(used & self._MOVEMENT_KEY_NAMES)
        action_keys = sorted(used - self._MOVEMENT_KEY_NAMES)
        return needs_dpad, action_keys

    def _build_touch_controls_html(self, needs_dpad: bool, action_keys) -> str:
        """Builds the #touchControls markup engine.js's setupTouchControls()
        wires up and reveals on a real touchscreen. Empty string (nothing
        rendered) when the project binds no keyboard event at all."""
        if not needs_dpad and not action_keys:
            return ''
        parts = ['<div id="touchControls">']
        if needs_dpad:
            parts.append(
                '<div id="dpad">'
                '<button class="dpad-btn dpad-up" data-key="up" aria-label="Up">▲</button>'
                '<button class="dpad-btn dpad-left" data-key="left" aria-label="Left">◀</button>'
                '<button class="dpad-btn dpad-right" data-key="right" aria-label="Right">▶</button>'
                '<button class="dpad-btn dpad-down" data-key="down" aria-label="Down">▼</button>'
                '</div>'
            )
        if action_keys:
            parts.append('<div id="actionButtons">')
            for key in action_keys:
                label = self._ACTION_KEY_LABELS.get(key, key.upper())
                safe_key = html.escape(key)
                safe_label = html.escape(label)
                parts.append(
                    f'<button class="action-btn" data-key="{safe_key}" '
                    f'aria-label="{safe_key}">{safe_label}</button>'
                )
            parts.append('</div>')
        parts.append('</div>')
        return ''.join(parts)

    # Formats browsers can decode via <audio>/Audio(); .mid/.midi have no
    # browser support and are skipped with a warning.
    _SOUND_MIME = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.ogg': 'audio/ogg',
        '.m4a': 'audio/mp4',
    }

    def encode_sounds(self, project_path: Path, project_data: Dict,
                      assets_output_dir: Optional[Path] = None) -> Dict[str, str]:
        """Sound name -> either a base64 data URL (default, assets_output_dir
        omitted -- every existing caller), or (docs/EXPORT_POLISH_PLAN.md
        item 1, external_assets export option) a relative URL under
        assets_output_dir/sounds/ when assets_output_dir is given. engine.js
        needs no change either way: `new Audio(src)` accepts a data: URI or
        an ordinary relative URL identically."""
        encoded = {}
        sound_dir = (assets_output_dir / "sounds") if assets_output_dir else None
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
                if sound_dir is not None:
                    encoded[sound_name] = _copy_asset_file(
                        full_path, sound_dir, sound_name, "assets/sounds")
                else:
                    b64 = base64.b64encode(full_path.read_bytes()).decode('utf-8')
                    encoded[sound_name] = f"data:{mime};base64,{b64}"
            except Exception as e:
                logger.warning(f"  Failed to encode sound {sound_name}: {e}")
        return encoded

    def encode_sprites(self, project_path: Path, project_data: Dict,
                       assets_output_dir: Optional[Path] = None) -> Dict[str, str]:
        """Sprite/background name -> either a base64 data URL (default,
        assets_output_dir omitted -- every existing caller), or
        (docs/EXPORT_POLISH_PLAN.md item 1, external_assets export option)
        a relative URL under assets_output_dir/sprites/ when
        assets_output_dir is given. engine.js needs no change either way:
        `img.src = spritesData[name]` accepts a data: URI or an ordinary
        relative URL identically."""
        encoded = {}
        sprite_dir = (assets_output_dir / "sprites") if assets_output_dir else None

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
                if sprite_dir is not None:
                    encoded[sprite_name] = _copy_asset_file(
                        full_path, sprite_dir, sprite_name, "assets/sprites")
                else:
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

        # Encode backgrounds (same guards/logging as sprites, #1/#2). Shares
        # sprite_dir/assets/sprites -- a background is drawn the same way a
        # sprite is (Image().src), no reason for its own top-level folder.
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
                if sprite_dir is not None:
                    encoded[bg_name] = _copy_asset_file(
                        full_path, sprite_dir, bg_name, "assets/sprites")
                else:
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
