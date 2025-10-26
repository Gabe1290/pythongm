#!/usr/bin/env python3
"""UI helper utilities placeholder"""

class UIHelpers:
    @staticmethod
    def get_asset_icon_text(asset_type):
        icons = {
            'sprites': '🖼️', 'sounds': '🔊', 'objects': '📦',
            'rooms': '🏠', 'scripts': '📜', 'fonts': '🔤'
        }
        return icons.get(asset_type, '📄')
    
    @staticmethod
    def format_file_size(size_bytes):
        if size_bytes == 0:
            return "0 B"
        return f"{size_bytes} bytes"
