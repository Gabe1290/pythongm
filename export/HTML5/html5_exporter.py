#!/usr/bin/env python3
"""
HTML5 Game Exporter for PyGameMaker
Exports projects as standalone HTML5 games with GameMaker 7.0 compatibility
"""

import json
import base64
import gzip
from pathlib import Path
from typing import Dict

from core.logger import get_logger
logger = get_logger(__name__)


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

                # Load room instances from external files
                self._load_room_instances(project_path, project_data)

                logger.info(f"  Loaded project: {project_data['name']}")

                # Encode sprites as base64
                logger.info("  Encoding sprites...")
                sprites_data = self.encode_sprites(project_path, project_data)
                logger.info(f"  Encoded {len(sprites_data)} sprites")

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

                compression_ratio_game = (len(game_data_compressed) * 100) // len(game_data_json)
                compression_ratio_sprites = (len(sprites_data_compressed) * 100) // len(sprites_data_json)

                logger.debug("  Compressed sizes:")
                logger.debug(f"     Game data: {len(game_data_compressed):,} bytes ({compression_ratio_game}%)")
                logger.debug(f"     Sprites data: {len(sprites_data_compressed):,} bytes ({compression_ratio_sprites}%)")
                logger.debug(f"  Total size reduction: {len(game_data_json) + len(sprites_data_json) - len(game_data_compressed) - len(sprites_data_compressed):,} bytes saved")

                # Replace placeholders
                html_content = self.template_html.replace('{game_name}', project_data['name'])
                html_content = html_content.replace('{width}', str(width))
                html_content = html_content.replace('{height}', str(height))
                html_content = html_content.replace('{game_data}', f'"{game_data_compressed}"')
                html_content = html_content.replace('{sprites_data}', f'"{sprites_data_compressed}"')
                html_content = html_content.replace('{engine_code}', self.engine_code)

                # Write output
                output_file = output_path / f"{project_data['name']}.html"
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
