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
                print(f"📦 Exporting {project_path.name} to HTML5...")

                # Load project
                project_file = project_path / "project.json"
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)

                print(f"  ✓ Loaded project: {project_data['name']}")

                # Encode sprites as base64
                print("  📸 Encoding sprites...")
                sprites_data = self.encode_sprites(project_path, project_data)
                print(f"  ✓ Encoded {len(sprites_data)} sprites")

                # Get window size from first room if settings not available
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
                        settings = project_data.get('settings', {})
                        width = settings.get('window_width', 1024)
                        height = settings.get('window_height', 768)

                print(f"  📐 Canvas size: {width}x{height}")

                # Generate HTML
                print("  🎨 Generating HTML...")

                # Serialize the data
                game_data_json = json.dumps(project_data, separators=(',', ':'))
                sprites_data_json = json.dumps(sprites_data, separators=(',', ':'))

                print("  📊 Original sizes:")
                print(f"     Game data: {len(game_data_json):,} bytes")
                print(f"     Sprites data: {len(sprites_data_json):,} bytes")

                # Compress the data using gzip
                game_data_compressed = base64.b64encode(
                    gzip.compress(game_data_json.encode('utf-8'), compresslevel=9)
                ).decode('ascii')

                sprites_data_compressed = base64.b64encode(
                    gzip.compress(sprites_data_json.encode('utf-8'), compresslevel=9)
                ).decode('ascii')

                compression_ratio_game = (len(game_data_compressed) * 100) // len(game_data_json)
                compression_ratio_sprites = (len(sprites_data_compressed) * 100) // len(sprites_data_json)

                print("  📦 Compressed sizes:")
                print(f"     Game data: {len(game_data_compressed):,} bytes ({compression_ratio_game}%)")
                print(f"     Sprites data: {len(sprites_data_compressed):,} bytes ({compression_ratio_sprites}%)")
                print(f"  💾 Total size reduction: {len(game_data_json) + len(sprites_data_json) - len(game_data_compressed) - len(sprites_data_compressed):,} bytes saved")

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

                print("  ✅ Export complete!")
                print(f"  📄 File: {output_file.name}")
                print(f"  💾 Size: {file_size_kb:.1f} KB")
                print(f"\n🎮 Open {output_file.name} in a web browser to play!")

                return True

            except Exception as e:
                print(f"❌ Export failed: {e}")
                import traceback
                traceback.print_exc()
                return False

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
                            elif ext == '.gi':
                                mime_type = 'image/gif'

                            encoded[sprite_name] = f"data:{mime_type};base64,{b64}"
                    except Exception as e:
                        print(f"  ⚠️  Failed to encode {sprite_name}: {e}")

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
                        print(f"  ⚠️  Failed to encode background {bg_name}: {e}")

        return encoded


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python html5_exporter.py <project_path> <output_directory>")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not project_path.exists():
        print(f"❌ Project path not found: {project_path}")
        sys.exit(1)

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    exporter = HTML5Exporter()
    success = exporter.export(project_path, output_path)

    sys.exit(0 if success else 1)
