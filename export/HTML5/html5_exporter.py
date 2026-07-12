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
from typing import Dict

from core.logger import get_logger
logger = get_logger(__name__)


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

    def __init__(self):
        # Load templates from files
        template_dir = Path(__file__).parent / "templates"
        self.template_html = (template_dir / "game_template.html").read_text(encoding='utf-8')
        self.engine_code = (template_dir / "engine.js").read_text(encoding='utf-8')

    def export(self, project_path: Path, output_path: Path) -> bool:
            """Export project to HTML5"""
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

                logger.info(f"  Loaded project: {project_data['name']}")

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
                    '{game_name}', html.escape(str(project_data['name'])))
                html_content = html_content.replace('{width}', str(width))
                html_content = html_content.replace('{height}', str(height))
                html_content = html_content.replace('{game_data}', f'"{game_data_compressed}"')
                html_content = html_content.replace('{sprites_data}', f'"{sprites_data_compressed}"')
                html_content = html_content.replace('{sounds_data}', f'"{sounds_data_compressed}"')
                html_content = html_content.replace('{engine_code}', self.engine_code)

                # Write output. Sanitize the name for the FILENAME —
                # characters legal in a project name but illegal in a
                # filename (< > : " / \ | ? * and control chars) otherwise
                # crash the write on Windows (e.g. a name like "Level 1: Go"
                # or "Tom & <Jerry>"). The in-page title keeps the real
                # (HTML-escaped) name; only the file on disk is sanitized.
                safe_name = _sanitize_filename(str(project_data['name'])) or "game"
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
                return False

    def _load_room_instances(self, project_path: Path, project_data: Dict) -> None:
        """Load room instances from external room files into project_data"""
        rooms_data = project_data.get('assets', {}).get('rooms', {})
        rooms_dir = project_path / "rooms"

        for room_name, room_data in rooms_data.items():
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
            file_path = sprite_info.get('file_path', '')
            if file_path:
                full_path = project_path / file_path
                if full_path.exists():
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

        # Encode backgrounds
        backgrounds_data = project_data.get('assets', {}).get('backgrounds', {})
        for bg_name, bg_info in backgrounds_data.items():
            file_path = bg_info.get('file_path', '')
            if file_path:
                full_path = project_path / file_path
                if full_path.exists():
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
