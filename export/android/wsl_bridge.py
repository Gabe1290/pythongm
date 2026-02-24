#!/usr/bin/env python3
"""
WSL Bridge for Android APK Export on Windows.

Handles detection, path conversion, dependency installation,
and buildozer execution inside Windows Subsystem for Linux.
"""

import subprocess
import re
from pathlib import Path
from typing import Optional, Tuple, List, Callable

from core.logger import get_logger

logger = get_logger(__name__)


class WSLBridge:
    """Manages communication with WSL for running Buildozer on Windows.

    Responsibilities:
    - Detect whether WSL is installed and has a usable Linux distro
    - Convert Windows paths to WSL /mnt/... paths
    - Check and install Linux-side dependencies
    - Execute buildozer inside WSL and stream output back
    """

    # System packages needed inside WSL for buildozer
    APT_PACKAGES = [
        'python3', 'python3-pip', 'python3-venv',
        'openjdk-17-jdk',
        'build-essential', 'autoconf', 'automake', 'libtool',
        'pkg-config', 'cmake', 'zip', 'unzip',
        'python3-dev', 'libffi-dev', 'libssl-dev',
        'git',
    ]

    PIP_PACKAGES = [
        'buildozer',
        'cython<3.0',
    ]

    def __init__(self):
        self._distro_name: Optional[str] = None
        self._wsl_available: Optional[bool] = None

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def is_wsl_available(self) -> bool:
        """Check if WSL is installed and has at least one Linux distro.

        Caches the result for the lifetime of this object.
        """
        if self._wsl_available is not None:
            return self._wsl_available

        try:
            result = subprocess.run(
                ['wsl', '--status'],
                capture_output=True, text=True, timeout=10,
                encoding='utf-8', errors='replace'
            )
            if result.returncode != 0:
                logger.info("WSL not available: wsl --status returned %d",
                            result.returncode)
                self._wsl_available = False
                return False

            distro = self._get_default_distro()
            if distro is None:
                logger.info("WSL installed but no Linux distro found")
                self._wsl_available = False
                return False

            self._distro_name = distro
            self._wsl_available = True
            logger.info("WSL available with distro: %s", distro)
            return True

        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            logger.info("WSL not available: %s", exc)
            self._wsl_available = False
            return False

    def _get_default_distro(self) -> Optional[str]:
        """Return the name of the default WSL distro, or None."""
        try:
            result = subprocess.run(
                ['wsl', '-l', '-q'],
                capture_output=True, timeout=10
            )
            if result.returncode != 0:
                return None

            # wsl -l output is UTF-16LE on Windows
            output = result.stdout.decode('utf-16-le', errors='replace')
            lines = [l.strip().strip('\x00') for l in output.splitlines()]
            lines = [l for l in lines if l]
            return lines[0] if lines else None

        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

    def get_wsl_info(self) -> dict:
        """Return diagnostic information about the WSL installation."""
        info = {
            'available': False,
            'distro': None,
            'version': None,
            'message': '',
        }

        if not self.is_wsl_available():
            info['message'] = 'WSL is not installed or has no Linux distro.'
            return info

        info['available'] = True
        info['distro'] = self._distro_name

        try:
            result = subprocess.run(
                ['wsl', '-l', '-v'],
                capture_output=True, timeout=10
            )
            output = result.stdout.decode('utf-16-le', errors='replace')
            for line in output.splitlines():
                if self._distro_name and self._distro_name in line:
                    for part in line.split():
                        if part in ('1', '2'):
                            info['version'] = part
                            break
        except Exception:
            pass

        info['message'] = 'WSL {} with {}'.format(
            info['version'] or '?', info['distro'])
        return info

    # ------------------------------------------------------------------
    # Path Conversion
    # ------------------------------------------------------------------

    def windows_to_wsl_path(self, windows_path: str) -> str:
        """Convert a Windows path to a WSL ``/mnt/...`` path.

        Uses ``wslpath`` inside WSL with a regex fallback.
        """
        # Try wslpath first (most reliable)
        try:
            result = subprocess.run(
                ['wsl', 'wslpath', '-u', windows_path],
                capture_output=True, text=True, timeout=5,
                encoding='utf-8', errors='replace'
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Fallback: manual conversion  C:\foo -> /mnt/c/foo
        path = windows_path.replace('\\', '/')
        match = re.match(r'^([A-Za-z]):(.*)', path)
        if match:
            drive = match.group(1).lower()
            rest = match.group(2)
            return '/mnt/{}{}'.format(drive, rest)

        return path

    # ------------------------------------------------------------------
    # Dependency Checking and Installation
    # ------------------------------------------------------------------

    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """Check if all required dependencies are installed in WSL.

        Returns ``(all_ok, list_of_missing_items)``.
        """
        missing: List[str] = []

        for cmd in ['python3', 'pip3', 'java', 'autoconf', 'cmake',
                    'zip', 'unzip', 'git']:
            if not self._wsl_command_exists(cmd):
                missing.append(cmd)

        for pkg in ['buildozer', 'cython']:
            if not self._wsl_pip_package_installed(pkg):
                missing.append('pip:{}'.format(pkg))

        return (len(missing) == 0, missing)

    def _wsl_command_exists(self, command: str) -> bool:
        try:
            result = subprocess.run(
                ['wsl', 'which', command],
                capture_output=True, timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _wsl_pip_package_installed(self, package: str) -> bool:
        try:
            result = subprocess.run(
                ['wsl', 'python3', '-c',
                 'import {}; print("ok")'.format(package)],
                capture_output=True, text=True, timeout=10,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0 and 'ok' in result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def install_dependencies(
        self, progress_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str]:
        """Install all required dependencies inside WSL.

        Returns ``(success, message)``.
        """
        def _report(msg: str):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        try:
            # Use 'wsl -u root' instead of 'wsl sudo' to avoid
            # password prompts that would block the subprocess.
            # apt update
            _report("Updating package lists in WSL...")
            result = subprocess.run(
                ['wsl', '-u', 'root', 'apt-get', 'update', '-y'],
                capture_output=True, text=True, timeout=300,
                encoding='utf-8', errors='replace'
            )
            if result.returncode != 0:
                return (False,
                        "Failed to update apt packages:\n{}".format(
                            (result.stderr or 'unknown error')[-500:]))

            # apt install — openjdk-17-jdk is large, allow plenty of time
            _report("Installing system packages in WSL "
                    "(Java JDK + build tools, this may take a while)...")
            cmd = ['wsl', '-u', 'root', 'apt-get', 'install', '-y'] + self.APT_PACKAGES
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=1800,
                encoding='utf-8', errors='replace'
            )
            if result.returncode != 0:
                return (False,
                        "Failed to install system packages:\n{}".format(
                            (result.stderr or 'unknown error')[-500:]))

            # pip install — use --break-system-packages for Ubuntu 24.04+
            # which enforces PEP 668 (externally-managed-environment).
            # Run via 'bash -c' so that version specs like 'cython<3.0'
            # are not misinterpreted as shell redirections.
            _report("Installing Python packages in WSL...")
            for pkg in self.PIP_PACKAGES:
                pip_cmd = "pip3 install --user --break-system-packages '{}'".format(pkg)
                result = subprocess.run(
                    ['wsl', 'bash', '-c', pip_cmd],
                    capture_output=True, text=True, timeout=300,
                    encoding='utf-8', errors='replace'
                )
                if result.returncode != 0:
                    return (False,
                            "Failed to install pip package '{}':\n{}".format(
                                pkg, (result.stderr or 'unknown error')[-500:]))

            _report("All WSL dependencies installed successfully.")
            return (True, "Dependencies installed successfully")

        except subprocess.TimeoutExpired as exc:
            return (False,
                    "Installation timed out.\n"
                    "Step: {}\n\n"
                    "This usually means a large package (like Java JDK) is "
                    "being downloaded.\n"
                    "You can try installing manually in WSL to see "
                    "progress.".format(exc.cmd))
        except Exception as exc:
            return (False, "Installation error: {}".format(exc))

    # ------------------------------------------------------------------
    # Buildozer Execution
    # ------------------------------------------------------------------

    def run_buildozer(self, build_dir_windows: str) -> subprocess.Popen:
        """Launch buildozer inside WSL as a streaming subprocess.

        Copies the game files from the Windows temp directory into
        WSL's native filesystem (``/tmp/pygm_build``), runs buildozer
        there, and copies the APK back.  Building on the native Linux
        filesystem avoids ``/mnt/c/`` I/O slowness and path-resolution
        issues that can prevent SDK tools like ``aidl`` from working.

        The build script is piped via stdin because ``wsl bash -c``
        strips ``$`` variable references from the argument string.

        Returns a :class:`subprocess.Popen` with ``stdout`` piped.
        """
        wsl_src = self.windows_to_wsl_path(build_dir_windows)

        # Build entirely inside WSL's native filesystem for speed and
        # to avoid /mnt/c/ issues with the Android SDK tools.
        # Use stdin pipe because 'wsl bash -c' eats $ expansions.
        build_script = (
            '#!/bin/bash\n'
            'set -e\n'
            'BUILD_DIR=$(mktemp -d /tmp/pygm_build_XXXXXX)\n'
            'echo "Build directory: $BUILD_DIR"\n'
            'cp -r "{src}"/* "$BUILD_DIR"/\n'
            'cd "$BUILD_DIR"\n'
            'export PATH="$HOME/.local/bin:$PATH"\n'
            'export PIP_BREAK_SYSTEM_PACKAGES=1\n'
            'python3 -m buildozer android debug\n'
            'EXIT_CODE=$?\n'
            'mkdir -p "{src}/bin"\n'
            'cp "$BUILD_DIR"/bin/*.apk "{src}/bin/" 2>/dev/null || true\n'
            'exit $EXIT_CODE\n'
        ).format(src=wsl_src)

        logger.info("Running buildozer in WSL (native filesystem):")
        logger.info("  Windows dir: %s", build_dir_windows)
        logger.info("  WSL source:  %s", wsl_src)
        logger.info("  Build will run in /tmp/pygm_build_*")

        process = subprocess.Popen(
            ['wsl', 'bash'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace',
        )

        # Write the script to stdin and close it so bash can proceed
        process.stdin.write(build_script)
        process.stdin.close()

        return process
