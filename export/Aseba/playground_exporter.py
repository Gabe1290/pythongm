#!/usr/bin/env python3
"""
Playground Exporter - Exports playground data to Aseba .playground format.
The .playground format is a ZIP archive containing:
  - world.xml: XML scene definition
  - (optional) ground texture PNG
"""

import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path

from core.logger import get_logger
logger = get_logger(__name__)


class PlaygroundExporter:
    """Exports playground data to Aseba .playground ZIP format"""

    def export(self, playground_data, output_path, ground_texture_path=None):
        """
        Export playground data as a .playground ZIP file.

        Args:
            playground_data: dict with arena, colors, walls, robots
            output_path: path for the output .playground file
            ground_texture_path: optional path to a ground texture PNG
        """
        xml_str = self._generate_xml(playground_data, ground_texture_path)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('world.xml', xml_str)
            if ground_texture_path:
                texture_path = Path(ground_texture_path)
                if texture_path.exists():
                    zf.write(str(texture_path), texture_path.name)

        logger.info(f"Exported playground to: {output_path}")

    def _generate_xml(self, data, ground_texture_path=None):
        """Generate the world.xml content"""
        root = ET.Element('aseba-playground')

        # Description
        name = data.get('name', 'Playground')
        desc = ET.SubElement(root, 'description', lang='en')
        desc.text = f'Playground: {name}'

        # Colors
        for color in data.get('colors', []):
            ET.SubElement(root, 'color',
                          name=color['name'],
                          r=self._fmt(color['r']),
                          g=self._fmt(color['g']),
                          b=self._fmt(color['b']))

        # World / Arena
        arena = data.get('arena', {})
        arena_height = arena.get('height', 400)
        world_attrs = {
            'w': str(arena.get('width', 400)),
            'h': str(arena_height),
            'color': arena.get('color', 'white'),
        }
        if ground_texture_path:
            texture_name = Path(ground_texture_path).name
            world_attrs['groundTexture'] = texture_name
        ET.SubElement(root, 'world', **world_attrs)

        # Walls - flip Y to convert from screen coords (Y down) to Aseba coords (Y up)
        for wall in data.get('walls', []):
            attrs = {
                'x': self._fmt(wall['x']),
                'y': self._fmt(arena_height - wall['y']),
                'l1': self._fmt(wall['l1']),
                'l2': self._fmt(wall['l2']),
                'h': self._fmt(wall['h']),
                'color': wall.get('color', 'wall'),
                'angle': self._fmt(-wall.get('angle', 0)),
            }
            if wall.get('mass') is not None:
                attrs['mass'] = self._fmt(wall['mass'])
            ET.SubElement(root, 'wall', **attrs)

        # Robots - flip Y and angle for Aseba's coordinate system
        for robot in data.get('robots', []):
            attrs = {
                'type': robot.get('type', 'thymio2'),
                'x': self._fmt(robot['x']),
                'y': self._fmt(arena_height - robot['y']),
                'port': str(robot.get('port', 33333)),
                'angle': self._fmt(-robot.get('angle', 0)),
                'name': robot.get('name', 'Thymio'),
            }
            ET.SubElement(root, 'robot', **attrs)

        # Pretty-print
        rough_string = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(rough_string)
        pretty = dom.toprettyxml(indent='    ', encoding=None)
        # Remove the XML declaration line that minidom adds
        lines = pretty.split('\n')
        if lines and lines[0].startswith('<?xml'):
            lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
        # Add DOCTYPE after XML declaration
        lines.insert(1, '<!DOCTYPE aseba-playground>')
        return '\n'.join(lines)

    @staticmethod
    def _fmt(value):
        """Format a number, removing unnecessary trailing zeros"""
        if isinstance(value, float):
            formatted = f"{value:.2f}"
            # Remove trailing zeros but keep at least one decimal
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
                if '.' not in formatted:
                    formatted += '.0'
            return formatted
        return str(value)
