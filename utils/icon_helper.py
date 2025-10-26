#!/usr/bin/env python3
"""
Safe icon helper to prevent standardIcon errors
FIXED VERSION - All calls are now safe
"""

from PySide6.QtWidgets import QStyle, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

def get_standard_icon(icon_type):
    """
    Get a standard icon safely - COMPLETELY BULLETPROOF VERSION
    
    Args:
        icon_type: Either a QStyle.StandardPixmap enum or an integer
        
    Returns:
        QIcon: The requested icon or a default icon
    """
    
    try:
        # If it's already the right type, use it directly
        if hasattr(icon_type, '__class__') and 'StandardPixmap' in str(icon_type.__class__):
            return QApplication.style().standardIcon(icon_type)
        
        # If it's an integer, convert to enum safely
        if isinstance(icon_type, int):
            # Comprehensive icon mapping
            icon_map = {
                0: QStyle.StandardPixmap.SP_TitleBarMenuButton,
                1: QStyle.StandardPixmap.SP_TitleBarMinButton,
                2: QStyle.StandardPixmap.SP_TitleBarMaxButton,
                3: QStyle.StandardPixmap.SP_TitleBarCloseButton,
                4: QStyle.StandardPixmap.SP_TitleBarNormalButton,
                9: QStyle.StandardPixmap.SP_MessageBoxInformation,
                10: QStyle.StandardPixmap.SP_MessageBoxWarning,
                11: QStyle.StandardPixmap.SP_MessageBoxCritical,
                12: QStyle.StandardPixmap.SP_MessageBoxQuestion,
                13: QStyle.StandardPixmap.SP_DesktopIcon,
                14: QStyle.StandardPixmap.SP_TrashIcon,
                21: QStyle.StandardPixmap.SP_DirOpenIcon,
                22: QStyle.StandardPixmap.SP_DirClosedIcon,
                23: QStyle.StandardPixmap.SP_DirLinkIcon,
                24: QStyle.StandardPixmap.SP_FileIcon,
                37: QStyle.StandardPixmap.SP_DirIcon,
                38: QStyle.StandardPixmap.SP_DialogOkButton,
                39: QStyle.StandardPixmap.SP_DialogCancelButton,
                49: QStyle.StandardPixmap.SP_ArrowUp,
                50: QStyle.StandardPixmap.SP_ArrowDown,
                51: QStyle.StandardPixmap.SP_ArrowLeft,
                52: QStyle.StandardPixmap.SP_ArrowRight,
            }
            
            if icon_type in icon_map:
                return QApplication.style().standardIcon(icon_map[icon_type])
            else:
                # Default to file icon for unknown numbers
                return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        
        # If it's a StandardPixmap enum, use it directly
        if isinstance(icon_type, QStyle.StandardPixmap):
            return QApplication.style().standardIcon(icon_type)
        
        # Default fallback for any other type
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        
    except Exception as e:
        print(f"Warning: Icon helper error: {e}")
        # Ultimate fallback - create empty icon
        return QIcon()

# Convenience functions - all now completely safe
def get_file_icon():
    """Get file icon safely"""
    try:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
    except:
        return QIcon()

def get_folder_icon():
    """Get folder icon safely""" 
    try:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirClosedIcon)
    except:
        return QIcon()

def get_folder_open_icon():
    """Get open folder icon safely"""
    try:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
    except:
        return QIcon()

def get_ok_icon():
    """Get OK button icon safely"""
    try:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)
    except:
        return QIcon()

def get_cancel_icon():
    """Get cancel button icon safely"""
    try:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
    except:
        return QIcon()

def get_warning_icon():
    """Get warning icon safely"""
    try:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
    except:
        return QIcon()

def get_error_icon():
    """Get error icon safely"""
    try:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
    except:
        return QIcon()

def get_info_icon():
    """Get information icon safely"""
    try:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
    except:
        return QIcon()

# Safe wrapper function for any standardIcon call
def safe_standard_icon_call(style_obj, icon_param):
    """
    Safely call standardIcon on any style object
    
    Args:
        style_obj: QStyle object (from widget.style() or QApplication.style())
        icon_param: Icon parameter (int or StandardPixmap)
    
    Returns:
        QIcon: Safe icon or empty icon
    """
    try:
        # Use our safe icon helper
        if isinstance(icon_param, int):
            return get_standard_icon(icon_param)
        elif isinstance(icon_param, QStyle.StandardPixmap):
            return style_obj.standardIcon(icon_param)
        else:
            return get_file_icon()  # Safe default
    except:
        return QIcon()
