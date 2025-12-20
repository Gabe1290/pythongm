#!/usr/bin/env python3
"""
Fix for Qt standardIcon error in PyGameMaker IDE
The error occurs when calling standardIcon() with int instead of proper Qt enum
"""

import sys
from pathlib import Path

# =============================================================================
# UPDATED qt_patch.py - Fix standardIcon calls
# =============================================================================

def apply_qt_patches():
    """Apply Qt patches including standardIcon fixes"""
    try:
        from PySide6.QtWidgets import QApplication, QStyle
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        
        print("🔧 Applying comprehensive Qt standardIcon patch...")
        
        # Fix the HighDPI warning by setting it before QApplication
        if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
            try:
                # This needs to be set before QApplication is created
                QApplication.setHighDpiScaleFactorRoundingPolicy(
                    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
                )
            except:
                pass
        
        # Set application attributes for better compatibility
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Patch standardIcon calls to use proper Qt enums
        patch_standard_icon_calls()
        
        print("✅ Comprehensive Qt standardIcon patch applied successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Qt import error: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Qt patch warning: {e}")
        return True

def patch_standard_icon_calls():
    """Patch standardIcon calls to use proper Qt enums instead of integers"""
    try:
        from PySide6.QtWidgets import QStyle, QCommonStyle
        from PySide6.QtCore import QObject
        
        # Create mapping from integers to proper Qt StandardPixmap enums
        STANDARD_ICON_MAP = {
            0: QStyle.StandardPixmap.SP_TitleBarMenuButton,
            1: QStyle.StandardPixmap.SP_TitleBarMinButton,
            2: QStyle.StandardPixmap.SP_TitleBarMaxButton,
            3: QStyle.StandardPixmap.SP_TitleBarCloseButton,
            4: QStyle.StandardPixmap.SP_TitleBarNormalButton,
            5: QStyle.StandardPixmap.SP_TitleBarShadeButton,
            6: QStyle.StandardPixmap.SP_TitleBarUnshadeButton,
            7: QStyle.StandardPixmap.SP_TitleBarContextHelpButton,
            8: QStyle.StandardPixmap.SP_DockWidgetCloseButton,
            9: QStyle.StandardPixmap.SP_MessageBoxInformation,
            10: QStyle.StandardPixmap.SP_MessageBoxWarning,
            11: QStyle.StandardPixmap.SP_MessageBoxCritical,
            12: QStyle.StandardPixmap.SP_MessageBoxQuestion,
            13: QStyle.StandardPixmap.SP_DesktopIcon,
            14: QStyle.StandardPixmap.SP_TrashIcon,
            15: QStyle.StandardPixmap.SP_ComputerIcon,
            16: QStyle.StandardPixmap.SP_DriveFDIcon,
            17: QStyle.StandardPixmap.SP_DriveHDIcon,
            18: QStyle.StandardPixmap.SP_DriveCDIcon,
            19: QStyle.StandardPixmap.SP_DriveDVDIcon,
            20: QStyle.StandardPixmap.SP_DriveNetIcon,
            21: QStyle.StandardPixmap.SP_DirOpenIcon,
            22: QStyle.StandardPixmap.SP_DirClosedIcon,
            23: QStyle.StandardPixmap.SP_DirLinkIcon,
            24: QStyle.StandardPixmap.SP_FileIcon,
            25: QStyle.StandardPixmap.SP_FileLinkIcon,
            26: QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton,
            27: QStyle.StandardPixmap.SP_ToolBarVerticalExtensionButton,
            28: QStyle.StandardPixmap.SP_FileDialogStart,
            29: QStyle.StandardPixmap.SP_FileDialogEnd,
            30: QStyle.StandardPixmap.SP_FileDialogToParent,
            31: QStyle.StandardPixmap.SP_FileDialogNewFolder,
            32: QStyle.StandardPixmap.SP_FileDialogDetailedView,
            33: QStyle.StandardPixmap.SP_FileDialogInfoView,
            34: QStyle.StandardPixmap.SP_FileDialogContentsView,
            35: QStyle.StandardPixmap.SP_FileDialogListView,
            36: QStyle.StandardPixmap.SP_FileDialogBack,
            37: QStyle.StandardPixmap.SP_DirIcon,
            38: QStyle.StandardPixmap.SP_DialogOkButton,
            39: QStyle.StandardPixmap.SP_DialogCancelButton,
            40: QStyle.StandardPixmap.SP_DialogHelpButton,
            41: QStyle.StandardPixmap.SP_DialogOpenButton,
            42: QStyle.StandardPixmap.SP_DialogSaveButton,
            43: QStyle.StandardPixmap.SP_DialogCloseButton,
            44: QStyle.StandardPixmap.SP_DialogApplyButton,
            45: QStyle.StandardPixmap.SP_DialogResetButton,
            46: QStyle.StandardPixmap.SP_DialogDiscardButton,
            47: QStyle.StandardPixmap.SP_DialogYesButton,
            48: QStyle.StandardPixmap.SP_DialogNoButton,
            49: QStyle.StandardPixmap.SP_ArrowUp,
            50: QStyle.StandardPixmap.SP_ArrowDown,
            51: QStyle.StandardPixmap.SP_ArrowLeft,
            52: QStyle.StandardPixmap.SP_ArrowRight,
            53: QStyle.StandardPixmap.SP_ArrowBack,
            54: QStyle.StandardPixmap.SP_ArrowForward,
            55: QStyle.StandardPixmap.SP_DirHomeIcon,
            56: QStyle.StandardPixmap.SP_CommandLink,
            57: QStyle.StandardPixmap.SP_VistaShield,
            58: QStyle.StandardPixmap.SP_BrowserReload,
            59: QStyle.StandardPixmap.SP_BrowserStop,
            60: QStyle.StandardPixmap.SP_MediaPlay,
            61: QStyle.StandardPixmap.SP_MediaStop,
            62: QStyle.StandardPixmap.SP_MediaPause,
            63: QStyle.StandardPixmap.SP_MediaSkipForward,
            64: QStyle.StandardPixmap.SP_MediaSkipBackward,
            65: QStyle.StandardPixmap.SP_MediaSeekForward,
            66: QStyle.StandardPixmap.SP_MediaSeekBackward,
            67: QStyle.StandardPixmap.SP_MediaVolume,
            68: QStyle.StandardPixmap.SP_MediaVolumeMuted,
        }
        
        # Store original standardIcon method
        original_standard_icon = QCommonStyle.standardIcon
        
        def patched_standard_icon(self, standard_pixmap, option=None, widget=None):
            """Patched standardIcon that handles both ints and proper enums"""
            try:
                # If it's an integer, convert to proper enum
                if isinstance(standard_pixmap, int):
                    if standard_pixmap in STANDARD_ICON_MAP:
                        standard_pixmap = STANDARD_ICON_MAP[standard_pixmap]
                    else:
                        # Default to a safe icon
                        standard_pixmap = QStyle.StandardPixmap.SP_FileIcon
                
                # Call original method with proper enum
                return original_standard_icon(self, standard_pixmap, option, widget)
                
            except Exception as e:
                print(f"⚠️ standardIcon patch error: {e}")
                # Return a default icon on error
                try:
                    return original_standard_icon(self, QStyle.StandardPixmap.SP_FileIcon, option, widget)
                except:
                    from PySide6.QtGui import QIcon
                    return QIcon()  # Empty icon as last resort
        
        # Apply the patch
        QCommonStyle.standardIcon = patched_standard_icon
        
        print("🔧 standardIcon calls patched successfully")
        
    except Exception as e:
        print(f"⚠️ standardIcon patch error: {e}")

# =============================================================================
# FIND AND FIX STANDARDICON CALLS IN YOUR CODE
# =============================================================================

def find_standard_icon_calls():
    """Find and fix standardIcon calls in your codebase"""
    
    print("\n🔍 FINDING standardIcon CALLS IN YOUR CODE")
    print("=" * 50)
    
    import re
    from pathlib import Path
    
    # Look for standardIcon calls in your project
    project_dir = Path("/home/gabe/Dropbox/pygm")
    if not project_dir.exists():
        project_dir = Path(".")
    
    py_files = list(project_dir.glob("**/*.py"))
    
    for py_file in py_files:
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Look for standardIcon calls with integers
                    if 'standardIcon' in line and re.search(r'standardIcon\s*\(\s*\d+', line):
                        print(f"📍 Found problematic call in {py_file}:{i}")
                        print(f"   {line.strip()}")
                        
                        # Suggest fix
                        fixed_line = fix_standard_icon_line(line)
                        if fixed_line != line:
                            print(f"   Fix: {fixed_line.strip()}")
                        print()
                        
        except Exception as e:
            continue
    
    print("✅ Scan complete")

def fix_standard_icon_line(line):
    """Fix a single line with standardIcon call"""
    
    # Common integer to enum mappings
    replacements = {
        'standardIcon(0)': 'standardIcon(QStyle.StandardPixmap.SP_TitleBarMenuButton)',
        'standardIcon(9)': 'standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)',
        'standardIcon(10)': 'standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)',
        'standardIcon(11)': 'standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)',
        'standardIcon(21)': 'standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)',
        'standardIcon(22)': 'standardIcon(QStyle.StandardPixmap.SP_DirClosedIcon)',
        'standardIcon(24)': 'standardIcon(QStyle.StandardPixmap.SP_FileIcon)',
        'standardIcon(37)': 'standardIcon(QStyle.StandardPixmap.SP_DirIcon)',
        'standardIcon(49)': 'standardIcon(QStyle.StandardPixmap.SP_ArrowUp)',
        'standardIcon(50)': 'standardIcon(QStyle.StandardPixmap.SP_ArrowDown)',
        'standardIcon(51)': 'standardIcon(QStyle.StandardPixmap.SP_ArrowLeft)',
        'standardIcon(52)': 'standardIcon(QStyle.StandardPixmap.SP_ArrowRight)',
    }
    
    fixed_line = line
    for old, new in replacements.items():
        if old in line:
            fixed_line = line.replace(old, new)
            break
    
    return fixed_line

# =============================================================================
# MAIN PATCH APPLICATION
# =============================================================================

if __name__ == "__main__":
    print("🔧 Qt StandardIcon Fix")
    print("This fixes PySide6 standardIcon errors")
    apply_qt_patches()
    find_standard_icon_calls()
else:
    # Auto-apply when imported
    apply_qt_patches()
