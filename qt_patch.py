#!/usr/bin/env python3
"""qt_patch.py - Enhanced Qt compatibility patches"""

def apply_qt_patches():
    try:
        from PySide6.QtWidgets import QApplication, QStyle, QCommonStyle
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        
        print("🔧 Applying comprehensive Qt standardIcon patch...")
        
        # Fix HighDPI warning
        try:
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
        except:
            pass
        
        # Set application attributes
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # PATCH standardIcon to handle integers safely
        original_standard_icon = QCommonStyle.standardIcon
        
        def safe_standard_icon(self, standard_pixmap, option=None, widget=None):
            try:
                # Convert integers to proper Qt enums
                icon_map = {
                    0: QStyle.StandardPixmap.SP_TitleBarMenuButton,
                    9: QStyle.StandardPixmap.SP_MessageBoxInformation,
                    10: QStyle.StandardPixmap.SP_MessageBoxWarning,
                    11: QStyle.StandardPixmap.SP_MessageBoxCritical,
                    21: QStyle.StandardPixmap.SP_DirOpenIcon,
                    22: QStyle.StandardPixmap.SP_DirClosedIcon,
                    24: QStyle.StandardPixmap.SP_FileIcon,
                    37: QStyle.StandardPixmap.SP_DirIcon,
                    49: QStyle.StandardPixmap.SP_ArrowUp,
                    50: QStyle.StandardPixmap.SP_ArrowDown,
                    51: QStyle.StandardPixmap.SP_ArrowLeft,
                    52: QStyle.StandardPixmap.SP_ArrowRight,
                }
                
                if isinstance(standard_pixmap, int):
                    standard_pixmap = icon_map.get(standard_pixmap, QStyle.StandardPixmap.SP_FileIcon)
                
                return original_standard_icon(self, standard_pixmap, option, widget)
            except:
                return QIcon()  # Return empty icon on error
        
        # Apply the patch
        QCommonStyle.standardIcon = safe_standard_icon
        
        print("✅ Comprehensive Qt standardIcon patch applied successfully")
        return True
        
    except Exception as e:
        print(f"⚠️ Qt patch warning: {e}")
        return True

# Auto-apply when imported
apply_qt_patches()