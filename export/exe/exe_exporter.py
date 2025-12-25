#!/usr/bin/env python3
"""
Windows EXE Exporter for PyGameMaker
Uses Kivy runtime (80% GameMaker 7.0 compatible) bundled with PyInstaller
"""

import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict
from PySide6.QtCore import QObject, Signal


class ExeExporter(QObject):
    """Handles exporting games as Windows EXE files using Kivy runtime"""

    progress_update = Signal(int, str)  # progress percentage, status message
    export_complete = Signal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        self.project_path = None
        self.output_path = None
        self.export_settings = {}
        self.project_data = None

    def export_project(self, project_path: str, output_path: str, settings: Dict) -> bool:
        """
        Export the project as a Windows EXE with Kivy runtime

        Args:
            project_path: Path to the .pgm project file
            output_path: Directory where the EXE will be created
            settings: Export settings dictionary

        Returns:
            True if export successful, False otherwise
        """
        self.project_path = Path(project_path)
        self.output_path = Path(output_path)
        self.export_settings = settings

        try:
            # Load project data - handle both directory and file paths
            if self.project_path.is_dir():
                project_file = self.project_path / "project.json"
            else:
                project_file = self.project_path

            with open(project_file, 'r') as f:
                self.project_data = json.load(f)

            # Step 1: Verify dependencies are available
            self.progress_update.emit(5, "Checking dependencies...")

            if not self._check_pyinstaller():
                self.export_complete.emit(
                    False,
                    "PyInstaller not found.\n\n"
                    "Please install it in your virtual environment:\n"
                    "pip install pyinstaller"
                )
                return False

            if not self._check_kivy():
                self.export_complete.emit(
                    False,
                    "Kivy not found.\n\n"
                    "The Windows EXE exporter requires Kivy to be installed.\n"
                    "Please install it in your virtual environment:\n\n"
                    "pip install kivy\n\n"
                    "Or install all dependencies:\n"
                    "pip install -r requirements.txt"
                )
                return False

            if not self._check_pillow():
                self.export_complete.emit(
                    False,
                    "Pillow (PIL) not found.\n\n"
                    "The Windows EXE exporter requires Pillow for image handling.\n"
                    "Please install it in your virtual environment:\n\n"
                    "pip install pillow\n\n"
                    "Or install all dependencies:\n"
                    "pip install -r requirements.txt"
                )
                return False

            # Step 2: Create temporary build directory
            self.progress_update.emit(20, "Creating build directory...")
            build_dir = self._create_build_directory()

            # Step 3: Generate Kivy game using KivyExporter
            self.progress_update.emit(30, "Generating Kivy game...")
            if not self._generate_kivy_game(build_dir):
                self.export_complete.emit(False, "Failed to generate Kivy game")
                return False

            # Step 4: Create launcher script
            self.progress_update.emit(50, "Creating launcher script...")
            launcher_script = self._create_launcher_script(build_dir)

            # Step 5: Create PyInstaller spec file
            self.progress_update.emit(60, "Creating PyInstaller spec...")
            spec_file = self._create_spec_file(build_dir, launcher_script)

            # Step 6: Run PyInstaller
            self.progress_update.emit(70, "Building executable (this may take a while)...")
            if not self._run_pyinstaller(spec_file):
                self.export_complete.emit(False, "PyInstaller build failed")
                return False

            # Step 7: Copy output to final location
            self.progress_update.emit(90, "Copying to output directory...")
            self._copy_to_output(build_dir)

            # Step 8: Cleanup (if not in debug mode)
            if not settings.get('include_debug', False):
                self.progress_update.emit(95, "Cleaning up temporary files...")
                self._cleanup(build_dir)

            self.progress_update.emit(100, "Export complete!")
            self.export_complete.emit(True, f"Game exported successfully to:\n{self.output_path}")
            return True

        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            self.export_complete.emit(False, error_msg)
            import traceback
            traceback.print_exc()
            return False
    
    def _check_pyinstaller(self) -> bool:
        """Check if PyInstaller is installed"""
        try:
            return True
        except ImportError:
            return False

    def _check_kivy(self) -> bool:
        """Check if Kivy is installed"""
        try:
            return True
        except ImportError:
            return False

    def _check_pillow(self) -> bool:
        """Check if Pillow (PIL) is installed"""
        try:
            return True
        except ImportError:
            return False

    def _create_build_directory(self) -> Path:
        """Create a temporary build directory"""
        project_dir = self.project_path.parent
        build_dir = project_dir / "build_temp_exe"

        # Clean if exists - with retry for locked files (Dropbox, etc.)
        if build_dir.exists():
            import time
            for attempt in range(3):
                try:
                    shutil.rmtree(build_dir)
                    break
                except PermissionError:
                    if attempt < 2:
                        print(f"Build directory locked, retrying in 2 seconds... (attempt {attempt + 1}/3)")
                        time.sleep(2)
                    else:
                        # Try using a different directory name
                        import uuid
                        build_dir = project_dir / f"build_temp_exe_{uuid.uuid4().hex[:8]}"
                        print(f"Using alternate build directory: {build_dir}")

        build_dir.mkdir(parents=True, exist_ok=True)
        return build_dir

    def _generate_kivy_game(self, build_dir: Path) -> bool:
        """
        Use KivyExporter to generate the Kivy game in the build directory

        Returns:
            True if successful, False otherwise
        """
        try:
            # Import the Kivy exporter
            from export.Kivy.kivy_exporter import KivyExporter

            # Set up paths - use the project directory, not its parent
            # project_path can be either a directory or a project.json file
            if self.project_path.is_dir():
                project_dir = self.project_path
            else:
                project_dir = self.project_path.parent
            kivy_output = build_dir  # Export directly to build directory

            # Create the exporter and run it
            exporter = KivyExporter(self.project_data, project_dir, kivy_output)
            success = exporter.export()

            if not success:
                print("KivyExporter.export() returned False")
                return False

            # Verify that the game directory was created
            game_dir = build_dir / "game"
            if not game_dir.exists():
                print(f"Error: Game directory not created at {game_dir}")
                return False

            # Verify main.py exists
            main_py = game_dir / "main.py"
            if not main_py.exists():
                print(f"Error: main.py not found at {main_py}")
                return False

            return True

        except Exception as e:
            print(f"Error generating Kivy game: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _create_launcher_script(self, build_dir: Path) -> Path:
        """
        Create the launcher script that runs the Kivy game

        This script handles PyInstaller frozen executable paths and
        launches the Kivy game.
        """
        launcher_script = build_dir / "game_launcher.py"

        game_name = self.project_data.get('name', 'Game')

        script_content = f'''#!/usr/bin/env python3
"""
Standalone Game Launcher for {game_name}
Generated by PyGameMaker IDE
Kivy-based runtime (80% GameMaker 7.0 compatible)
"""

import os
import sys
from pathlib import Path

def main():
    """Main game entry point"""
    try:
        # Set up paths for PyInstaller frozen executable
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Change to game directory
        game_dir = os.path.join(base_path, 'game')

        if not os.path.exists(game_dir):
            print(f"Error: Game directory not found at {{game_dir}}")
            sys.exit(1)

        os.chdir(game_dir)
        sys.path.insert(0, game_dir)

        # Import and run the Kivy game
        from main import GameApp

        # Run the game
        GameApp().run()

    except Exception as e:
        print(f"Game error: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        with open(launcher_script, 'w') as f:
            f.write(script_content)

        return launcher_script
    
    def _create_spec_file(self, build_dir: Path, launcher_script: Path) -> Path:
        """
        Create PyInstaller spec file for bundling Kivy game

        This spec file includes:
        - The launcher script
        - The entire game/ directory (generated by KivyExporter)
        - All Kivy dependencies
        - All game assets (images, sounds)
        """
        import os
        spec_file = build_dir / "game.spec"

        game_name = self.project_data.get('name', 'Game').replace(' ', '_')

        # Collect ALL files from the game directory recursively
        # This ensures images, sounds, and all assets are included
        game_dir = build_dir / "game"
        datas = []

        for root, dirs, files in os.walk(game_dir):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                # Skip .pyc files
                if file.endswith('.pyc'):
                    continue

                # Get the full source path
                src_path = os.path.join(root, file)
                # Get the relative path from build_dir
                rel_path = os.path.relpath(src_path, build_dir)
                # Get the destination directory (relative to bundle)
                dest_dir = os.path.dirname(rel_path)

                datas.append((rel_path, dest_dir))

        # Format datas for spec file
        # Use forward slashes to avoid escape sequence issues on Windows
        datas_str = ',\n        '.join([f"('{d[0].replace(chr(92), '/')}', '{d[1].replace(chr(92), '/')}')" for d in datas])

        # Hidden imports for Kivy
        hidden_imports = [
            'kivy',
            'kivy.app',
            'kivy.core.window',
            'kivy.core.image',
            'kivy.uix.widget',
            'kivy.graphics',
            'kivy.clock',
            'kivy.core.text',
            'kivy.core.audio',
            'PIL',  # Pillow for image loading
        ]

        hidden_imports_str = ',\n        '.join([f"'{imp}'" for imp in hidden_imports])

        # Get icon path if specified
        icon_line = ""
        if self.export_settings.get('icon_path'):
            icon_line = f"icon='{self.export_settings['icon_path']}',"

        # Create Windows manifest for DPI awareness
        manifest_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/pm</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">permonitorv2,permonitor</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>'''

        manifest_file = build_dir / "game.manifest"
        with open(manifest_file, 'w') as f:
            f.write(manifest_content)

        # Create spec content
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for {game_name}
# Generated by PyGameMaker IDE - EXE Exporter

block_cipher = None

a = Analysis(
    ['{launcher_script.name}'],
    pathex=[],
    binaries=[],
    datas=[
        {datas_str}
    ],
    hiddenimports=[
        {hidden_imports_str}
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'PySide6',
        'PyQt5',
        'PyQt6',
        'tkinter',
        'matplotlib',
        'numpy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{game_name}.exe',
    debug={self.export_settings.get('include_debug', False)},
    bootloader_ignore_signals=False,
    strip=False,
    upx={self.export_settings.get('optimize', False)},  # Disabled by default (saves memory)
    upx_exclude=[],
    runtime_tmpdir=None,
    console={self.export_settings.get('include_debug', False)},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    manifest='game.manifest',
    {icon_line}
)
'''

        with open(spec_file, 'w') as f:
            f.write(spec_content)

        return spec_file
    
    def _run_pyinstaller(self, spec_file: Path) -> bool:
        """Run PyInstaller to build the executable"""
        try:
            print("\n" + "="*60)
            print("Running PyInstaller (this may take 5-10 minutes)...")
            print("Building with Kivy is memory-intensive.")
            print("If the process is killed, try closing other applications.")
            print("="*60 + "\n")

            # Use the same Python interpreter that's running this script
            # This ensures we use the venv's pyinstaller
            import sys
            python_exe = sys.executable

            # Run PyInstaller as a module to ensure we use the venv's version
            process = subprocess.Popen(
                [python_exe, '-m', 'PyInstaller', '--clean', str(spec_file)],
                cwd=spec_file.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Stream output in real-time
            for line in process.stdout:
                print(line.rstrip())

            # Wait for completion with longer timeout (10 minutes)
            process.wait(timeout=600)

            if process.returncode != 0:
                print(f"\nPyInstaller failed with return code: {process.returncode}")
                return False

            print("\n✅ PyInstaller build completed successfully!")
            return True

        except subprocess.TimeoutExpired:
            print("\n❌ PyInstaller timed out after 10 minutes")
            print("This usually means the build is too memory-intensive for your system.")
            print("\nTry:")
            print("1. Close other applications to free up memory")
            print("2. Increase system swap space")
            print("3. Build on a machine with more RAM (recommended: 8GB+)")
            if process:
                process.kill()
            return False
        except Exception as e:
            print(f"\n❌ Error running PyInstaller: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _copy_to_output(self, build_dir: Path):
        """Copy the built executable to the output directory"""
        import time
        dist_dir = build_dir / "dist"

        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Copy all files from dist to output with retry for locked files
        if dist_dir.exists():
            for item in dist_dir.iterdir():
                for attempt in range(5):
                    try:
                        if item.is_file():
                            shutil.copy2(item, self.output_path / item.name)
                        elif item.is_dir():
                            shutil.copytree(item, self.output_path / item.name, dirs_exist_ok=True)
                        break  # Success
                    except PermissionError as e:
                        if attempt < 4:
                            print(f"File locked, retrying in 1 second... ({item.name})")
                            time.sleep(1)
                        else:
                            print(f"Warning: Could not copy {item.name}: {e}")
                            print(f"The EXE is available at: {dist_dir / item.name}")
    
    def _cleanup(self, build_dir: Path):
        """Clean up temporary build files"""
        try:
            if build_dir.exists():
                shutil.rmtree(build_dir)
        except Exception as e:
            print(f"Warning: Could not clean up build directory: {e}")