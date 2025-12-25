#!/usr/bin/env python3
"""
Room Preview/Test System
Allows quick testing of rooms from the editor
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, QProcess
from PySide6.QtWidgets import QMessageBox


class RoomPreviewRunner(QObject):
    """Manages running room previews"""

    # Signals
    preview_started = Signal(str)  # room_name
    preview_finished = Signal(int)  # exit_code
    preview_error = Signal(str)    # error_message
    preview_output = Signal(str)   # stdout/stderr output

    def __init__(self, project_path: Path, parent=None):
        super().__init__(parent)
        self.project_path = Path(project_path)
        self.process = None
        self.current_room = None
        self.start_instance_id = None

    def _is_packaged(self) -> bool:
        """Check if running from a packaged executable (Nuitka/PyInstaller)"""
        import os
        exe_exists = os.path.exists(sys.executable)
        file_dir = os.path.dirname(os.path.abspath(__file__))
        return (
            getattr(sys, 'frozen', False) or  # PyInstaller
            not exe_exists or  # Nuitka: sys.executable doesn't exist
            file_dir.startswith('/tmp/') or  # Nuitka onefile extraction
            file_dir.startswith(os.environ.get('TEMP', ''))  # Windows temp
        )

    def start_preview(self, room_name: str, start_instance_id: Optional[int] = None):
        """Start room preview"""
        if self.process and self.process.state() == QProcess.Running:
            QMessageBox.warning(
                None,
                "Preview Running",
                "A preview is already running. Stop it first."
            )
            return False

        # Check if running from packaged app - room preview requires subprocess
        if self._is_packaged():
            QMessageBox.warning(
                None,
                "Room Preview Not Available",
                "Room preview is not available in the standalone executable.\n\n"
                "Please use 'Run Game' (F5) instead to test the full game."
            )
            self.preview_error.emit("Room preview not available in packaged app")
            return False

        self.current_room = room_name
        self.start_instance_id = start_instance_id

        # Create temporary preview config
        preview_config = self.create_preview_config(room_name, start_instance_id)

        # Save preview config
        preview_config_path = self.project_path / ".preview_config.json"
        try:
            with open(preview_config_path, 'w') as f:
                json.dump(preview_config, f, indent=2)
        except Exception as e:
            self.preview_error.emit(f"Failed to save preview config: {e}")
            return False

        # Find the game runner script
        runner_script = self.find_runner_script()
        if not runner_script:
            self.preview_error.emit("Could not find game runner script")
            return False

        # Setup process
        self.process = QProcess(self)
        self.process.setWorkingDirectory(str(self.project_path))

        # Connect signals
        self.process.readyReadStandardOutput.connect(self.on_stdout)
        self.process.readyReadStandardError.connect(self.on_stderr)
        self.process.finished.connect(self.on_finished)
        self.process.errorOccurred.connect(self.on_error)

        # Start the process
        python_exe = sys.executable
        args = [str(runner_script), "--preview", str(preview_config_path)]

        print(f"🎮 Starting room preview: {room_name}")
        if start_instance_id:
            print(f"   Starting from instance: {start_instance_id}")
        print(f"   Command: {python_exe} {' '.join(args)}")

        self.process.start(python_exe, args)

        if self.process.waitForStarted(3000):
            self.preview_started.emit(room_name)
            return True
        else:
            self.preview_error.emit("Failed to start preview process")
            return False

    def stop_preview(self):
        """Stop the current preview"""
        if self.process and self.process.state() == QProcess.Running:
            print("🛑 Stopping room preview...")
            self.process.terminate()

            # Wait for graceful termination
            if not self.process.waitForFinished(2000):
                print("⚠️  Process didn't terminate gracefully, killing...")
                self.process.kill()

            return True
        return False

    def is_running(self) -> bool:
        """Check if preview is currently running"""
        return self.process is not None and self.process.state() == QProcess.Running

    def create_preview_config(self, room_name: str, start_instance_id: Optional[int]) -> Dict[str, Any]:
        """Create preview configuration"""
        config = {
            "preview_mode": True,
            "start_room": room_name,
            "window_title": f"Preview: {room_name}",
            "show_fps": True,
            "show_debug_info": True,
            "allow_escape_to_quit": True
        }

        if start_instance_id is not None:
            config["start_instance_id"] = start_instance_id

        return config

    def find_runner_script(self) -> Optional[Path]:
        """Find the game runner script"""
        # Look for common runner script names
        possible_names = [
            "game_runner.py",
            "run_game.py",
            "main.py",
            "runner.py"
        ]

        for name in possible_names:
            runner_path = self.project_path / name
            if runner_path.exists():
                return runner_path

        # Check in runtime folder
        runtime_folder = self.project_path.parent / "runtime"
        if runtime_folder.exists():
            for name in possible_names:
                runner_path = runtime_folder / name
                if runner_path.exists():
                    return runner_path

        return None

    def on_stdout(self):
        """Handle stdout from preview process"""
        if self.process:
            output = bytes(self.process.readAllStandardOutput()).decode('utf-8', errors='ignore')
            if output.strip():
                print(f"[Preview] {output.strip()}")
                self.preview_output.emit(output)

    def on_stderr(self):
        """Handle stderr from preview process"""
        if self.process:
            output = bytes(self.process.readAllStandardError()).decode('utf-8', errors='ignore')
            if output.strip():
                print(f"[Preview Error] {output.strip()}")
                self.preview_output.emit(output)

    def on_finished(self, exit_code, exit_status):
        """Handle preview process finished"""
        print(f"🏁 Room preview finished (exit code: {exit_code})")
        self.preview_finished.emit(exit_code)
        self.current_room = None
        self.start_instance_id = None

    def on_error(self, error):
        """Handle preview process error"""
        error_messages = {
            QProcess.FailedToStart: "Failed to start preview process",
            QProcess.Crashed: "Preview process crashed",
            QProcess.Timedout: "Preview process timed out",
            QProcess.WriteError: "Write error in preview process",
            QProcess.ReadError: "Read error in preview process",
            QProcess.UnknownError: "Unknown error in preview process"
        }

        error_msg = error_messages.get(error, f"Preview error: {error}")
        print(f"❌ {error_msg}")
        self.preview_error.emit(error_msg)
