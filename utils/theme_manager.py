#!/usr/bin/env python3
"""
Theme Manager for PyGameMaker IDE
Provides different color themes for the application loaded from JSON
"""

import json
import os
from typing import Dict, Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


class ThemeManager:
    """Manages application themes and color schemes"""
    
    _themes: Dict = {}
    _themes_loaded: bool = False
    
    @classmethod
    def _load_themes(cls):
        """Load theme definitions from themes.json"""
        if cls._themes_loaded:
            return
        
        # Find themes.json in the same directory as this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        themes_file = os.path.join(current_dir, 'themes.json')
        
        if not os.path.exists(themes_file):
            print(f"⚠️ themes.json not found at {themes_file}, using fallback themes")
            cls._themes = cls._get_fallback_themes()
        else:
            try:
                with open(themes_file, 'r') as f:
                    cls._themes = json.load(f)
                print(f"✅ Loaded themes from {themes_file}")
            except Exception as e:
                print(f"❌ Error loading themes.json: {e}")
                cls._themes = cls._get_fallback_themes()
        
        cls._themes_loaded = True
    
    @classmethod
    def _get_fallback_themes(cls) -> Dict:
        """Get fallback theme definitions if JSON file is missing"""
        return {
            'default': {
                'name': 'Default',
                'style': 'Fusion',
                'palette': None,
            }
        }
    
    @classmethod
    def apply_theme(cls, theme_name: str):
        """Apply a theme to the application
        
        Args:
            theme_name: Name of the theme ('default', 'dark', 'light')
        """
        cls._load_themes()
        theme_name = theme_name.lower()
        
        if theme_name not in cls._themes:
            print(f"⚠️ Unknown theme: {theme_name}, using default")
            theme_name = 'default'
        
        theme = cls._themes[theme_name]
        app = QApplication.instance()
        
        if not app:
            print("❌ No QApplication instance found")
            return
        
        # Set application style
        app.setStyle(theme['style'])
        
        # Apply palette if theme has custom colors
        if 'colors' in theme:
            palette = cls._create_palette(theme['colors'])
            app.setPalette(palette)
            print(f"✅ Applied {theme['name']} theme with custom palette")
        else:
            # Reset to default palette
            app.setPalette(QApplication.style().standardPalette())
            print(f"✅ Applied {theme['name']} theme (system default)")
        
        # Apply stylesheet for additional styling
        stylesheet = cls._generate_stylesheet(theme_name, theme.get('colors', {}))
        app.setStyleSheet(stylesheet)
    
    @classmethod
    def _create_palette(cls, colors: Dict[str, str]) -> QPalette:
        """Create a QPalette from color definitions
        
        Args:
            colors: Dictionary mapping palette roles to color hex strings
            
        Returns:
            QPalette with the specified colors
        """
        palette = QPalette()
        
        # Map color names to QPalette color roles
        color_map = {
            'window': QPalette.Window,
            'window_text': QPalette.WindowText,
            'base': QPalette.Base,
            'alternate_base': QPalette.AlternateBase,
            'tooltip_base': QPalette.ToolTipBase,
            'tooltip_text': QPalette.ToolTipText,
            'text': QPalette.Text,
            'button': QPalette.Button,
            'button_text': QPalette.ButtonText,
            'bright_text': QPalette.BrightText,
            'link': QPalette.Link,
            'highlight': QPalette.Highlight,
            'highlight_text': QPalette.HighlightedText,
        }
        
        # Set colors for all states
        for color_name, hex_color in colors.items():
            if color_name in color_map:
                color = QColor(hex_color)
                role = color_map[color_name]
                palette.setColor(QPalette.Active, role, color)
                palette.setColor(QPalette.Inactive, role, color)
                
                # Handle disabled state
                if color_name == 'disabled_text':
                    palette.setColor(QPalette.Disabled, QPalette.Text, color)
                    palette.setColor(QPalette.Disabled, QPalette.WindowText, color)
                elif color_name == 'disabled_button_text':
                    palette.setColor(QPalette.Disabled, QPalette.ButtonText, color)
                else:
                    # Disabled colors are slightly dimmer
                    disabled_color = QColor(hex_color)
                    disabled_color.setAlpha(128)
                    palette.setColor(QPalette.Disabled, role, disabled_color)
        
        return palette
    
    @classmethod
    def _generate_stylesheet(cls, theme_name: str, colors: Dict[str, str]) -> str:
        """Generate stylesheet from theme colors
        
        Args:
            theme_name: Name of the theme
            colors: Dictionary of color values
            
        Returns:
            CSS stylesheet string
        """
        if theme_name == 'default' or not colors:
            return ""
        
        # Helper function to get color with fallback
        def c(key: str, fallback: str = "#000000") -> str:
            return colors.get(key, fallback)
        
        return f"""
            /* Main window and panels */
            QMainWindow, QDialog, QWidget {{
                background-color: {c('panel_background')};
                color: {c('text')};
            }}
            
            /* Tree widgets (asset tree) */
            QTreeWidget, QTreeView {{
                background-color: {c('tree_background')};
                color: {c('text')};
                border: 1px solid {c('border')};
                alternate-background-color: {c('tree_alternate')};
            }}
            
            QTreeWidget::item, QTreeView::item {{
                color: {c('text')};
                padding: 4px;
            }}
            
            QTreeWidget::item:selected, QTreeView::item:selected {{
                background-color: {c('tree_selected')};
                color: {c('tree_selected_text')};
            }}
            
            QTreeWidget::item:hover, QTreeView::item:hover {{
                background-color: {c('tree_hover')};
            }}
            
            QTreeWidget::branch {{
                background-color: {c('tree_background')};
            }}
            
            /* Tab widget - text stays same color as menu text */
            QTabBar::tab {{
                color: {c('tab_text')};
            }}
            
            QTabBar::tab:selected {{
                color: {c('tab_selected_text')};
            }}
            
            /* Tooltips */
            QToolTip {{
                color: {c('tooltip_text')};
                background-color: {c('tooltip_base')};
                border: 1px solid {c('border')};
                padding: 4px;
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {c('menu_background')};
                color: {c('menu_text')};
                border-bottom: 1px solid {c('border')};
                padding: 2px;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                color: {c('menu_text')};
                padding: 4px 12px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {c('menu_selected')};
                color: {c('menu_selected_text')};
            }}
            
            QMenuBar::item:pressed {{
                background-color: {c('menu_pressed')};
            }}
            
            /* Menus (dropdowns) */
            QMenu {{
                background-color: {c('dropdown_background')};
                color: {c('text')};
                border: 1px solid {c('dropdown_border')};
                padding: 4px;
            }}
            
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                background-color: transparent;
            }}
            
            QMenu::item:selected {{
                background-color: {c('menu_selected')};
                color: {c('menu_selected_text')};
            }}
            
            QMenu::separator {{
                height: 1px;
                background: {c('menu_separator')};
                margin: 4px 0px;
            }}
            
            /* Toolbar */
            QToolBar {{
                background-color: {c('toolbar_background')};
                border: none;
                padding: 2px;
                spacing: 3px;
            }}
            
            QToolButton {{
                background-color: transparent;
                color: {c('text')};
                border: none;
                padding: 4px;
            }}
            
            QToolButton:hover {{
                background-color: {c('toolbar_button_hover')};
                border: 1px solid {c('link')};
            }}
            
            QToolButton:pressed {{
                background-color: {c('toolbar_button_pressed')};
            }}
            
            /* Scroll bars */
            QScrollBar:vertical {{
                background: {c('scrollbar_background')};
                width: 14px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {c('scrollbar_handle')};
                min-height: 30px;
                border-radius: 7px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {c('scrollbar_handle_hover')};
            }}
            
            QScrollBar:horizontal {{
                background: {c('scrollbar_background')};
                height: 14px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {c('scrollbar_handle')};
                min-width: 30px;
                border-radius: 7px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: {c('scrollbar_handle_hover')};
            }}
            
            QScrollBar::add-line, QScrollBar::sub-line {{
                border: none;
                background: none;
            }}
            
            /* Tab widgets */
            QTabWidget::pane {{
                border: 1px solid {c('tab_border')};
                background: {c('tab_pane')};
                top: -1px;
            }}
            
            QTabBar::tab {{
                background: {c('tab_background')};
                color: {c('tab_text')};
                padding: 8px 16px;
                border: 1px solid {c('tab_border')};
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background: {c('tab_selected')};
                color: {c('tab_selected_text')};
            }}
            
            QTabBar::tab:hover {{
                background: {c('tab_hover')};
            }}
            
            /* Text inputs */
            QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
                background-color: {c('input_background')};
                color: {c('text')};
                border: 1px solid {c('input_border')};
                padding: 4px;
                selection-background-color: {c('input_selection')};
                selection-color: {c('highlight_text')};
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid {c('input_focus_border')};
            }}
            
            /* Combo boxes */
            QComboBox {{
                background-color: {c('input_background')};
                color: {c('text')};
                border: 1px solid {c('input_border')};
                padding: 4px;
            }}
            
            QComboBox:hover {{
                border: 1px solid {c('input_focus_border')};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {c('dropdown_background')};
                color: {c('text')};
                selection-background-color: {c('menu_selected')};
                border: 1px solid {c('dropdown_border')};
            }}
            
            /* List widgets */
            QListWidget {{
                background-color: {c('input_background')};
                color: {c('text')};
                border: 1px solid {c('border')};
            }}
            
            QListWidget::item:selected {{
                background-color: {c('tree_selected')};
                color: {c('tree_selected_text')};
            }}
            
            QListWidget::item:hover {{
                background-color: {c('tree_hover')};
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {c('button')};
                color: {c('button_text')};
                border: 1px solid {c('border')};
                padding: 6px 16px;
                min-width: 60px;
            }}
            
            QPushButton:hover {{
                background-color: {c('button_hover')};
                border: 1px solid {c('input_focus_border')};
            }}
            
            QPushButton:pressed {{
                background-color: {c('button_pressed')};
            }}
            
            QPushButton:disabled {{
                background-color: {c('button_disabled')};
                color: {c('disabled_button_text')};
            }}
            
            /* Checkboxes */
            QCheckBox {{
                color: {c('text')};
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {c('checkbox_border')};
                background: {c('checkbox_background')};
            }}
            
            QCheckBox::indicator:checked {{
                background: {c('checkbox_checked')};
                border: 1px solid {c('input_focus_border')};
            }}
            
            /* Radio buttons */
            QRadioButton {{
                color: {c('text')};
                spacing: 8px;
            }}
            
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {c('checkbox_border')};
                background: {c('checkbox_background')};
                border-radius: 8px;
            }}
            
            QRadioButton::indicator:checked {{
                background: {c('checkbox_checked')};
                border: 1px solid {c('input_focus_border')};
            }}
            
            /* Group boxes */
            QGroupBox {{
                color: {c('text')};
                border: 1px solid {c('groupbox_border')};
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            
            /* Splitters */
            QSplitter::handle {{
                background-color: {c('border')};
            }}
            
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            
            QSplitter::handle:vertical {{
                height: 2px;
            }}
            
            /* Status bar */
            QStatusBar {{
                background-color: {c('statusbar_background')};
                color: {c('statusbar_text')};
            }}
            
            QStatusBar::item {{
                border: none;
            }}
            
            /* Progress bars */
            QProgressBar {{
                border: 1px solid {c('border')};
                background-color: {c('input_background')};
                text-align: center;
                color: {c('text')};
            }}
            
            QProgressBar::chunk {{
                background-color: {c('highlight')};
            }}
            
            /* Sliders */
            QSlider::groove:horizontal {{
                border: 1px solid {c('border')};
                height: 8px;
                background: {c('input_background')};
            }}
            
            QSlider::handle:horizontal {{
                background: {c('button')};
                border: 1px solid {c('border')};
                width: 18px;
                margin: -5px 0;
            }}
            
            QSlider::handle:horizontal:hover {{
                background: {c('button_hover')};
            }}
        """
    
    @classmethod
    def get_available_themes(cls) -> list:
        """Get list of available theme names
        
        Returns:
            List of theme names
        """
        cls._load_themes()
        return list(cls._themes.keys())
    
    @classmethod
    def get_theme_display_name(cls, theme_name: str) -> str:
        """Get the display name for a theme
        
        Args:
            theme_name: Internal theme name
            
        Returns:
            Human-readable theme name
        """
        cls._load_themes()
        theme = cls._themes.get(theme_name.lower(), {})
        return theme.get('name', theme_name.title())