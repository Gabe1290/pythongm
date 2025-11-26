#!/usr/bin/env python3
"""Extract export methods from ide_window.py into ide_exporters.py"""

from pathlib import Path

# Method names to extract
EXPORT_METHODS = [
    "export_html5",
    "export_kivy",
    "export_project",
    "export_project_zip",
    "open_project_zip",
    "toggle_auto_save_zip",
    "toggle_auto_save",
    "show_auto_save_settings",
    "export_windows_exe",
]

# Read the original file
with open("core/ide_window.py", "r") as f:
    lines = f.readlines()

# Find method boundaries
method_ranges = {}
current_method = None
method_start = None
indent_level = None

for i, line in enumerate(lines):
    # Check if this is a method definition
    if line.strip().startswith("def ") and line.startswith("    def "):
        # Save previous method
        if current_method and current_method in EXPORT_METHODS:
            method_ranges[current_method] = (method_start, i)

        # Extract method name
        method_name = line.strip().split("(")[0].replace("def ", "")

        if method_name in EXPORT_METHODS:
            current_method = method_name
            method_start = i
            indent_level = len(line) - len(line.lstrip())

# Save last method
if current_method and current_method in EXPORT_METHODS:
    method_ranges[current_method] = (method_start, len(lines))

print(f"Found {len(method_ranges)} export methods to extract:")
for method_name in method_ranges:
    start, end = method_ranges[method_name]
    print(f"  - {method_name}: lines {start+1}-{end}")

# Create the new ide_exporters module
exporter_content = '''#!/usr/bin/env python3
"""
IDE Export Functions
Handles all export-related functionality for the IDE
"""

from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QFileDialog, QDialog
from PySide6.QtCore import QObject
from dialogs.project_dialogs import ExportProjectDialog
from utils.config import Config


class IDEExporters(QObject):
    """Handles export operations for the IDE"""

    def __init__(self, ide_window):
        super().__init__()
        self.ide = ide_window

'''

# Add each extracted method
for method_name in EXPORT_METHODS:
    if method_name in method_ranges:
        start, end = method_ranges[method_name]
        method_lines = lines[start:end]

        # Adjust self references
        adjusted_lines = []
        for line in method_lines:
            # Replace self with self.ide for IDE window references
            if "def " not in line:  # Don't change method definition
                # Careful replacement - only replace self. references
                line = line.replace("self.current_project", "self.ide.current_project")
                line = line.replace("self.project_manager", "self.ide.project_manager")
                line = line.replace("self.update_status", "self.ide.update_status")
                line = line.replace("self.statusBar", "self.ide.statusBar")
                line = line.replace("self.tr", "self.ide.tr")
                line = line.replace("self.auto_save", "self.ide.auto_save")
                line = line.replace("self.export_project_zip", "self.export_project_zip")
            adjusted_lines.append(line)

        exporter_content += "".join(adjusted_lines) + "\n"

# Write the new module
with open("core/ide_exporters.py", "w") as f:
    f.write(exporter_content)

print(f"\n✓ Created core/ide_exporters.py")
print(f"  Total methods extracted: {len(method_ranges)}")
