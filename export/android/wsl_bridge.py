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

            # pip install
            _report("Installing Python packages in WSL...")
            for pkg in self.PIP_PACKAGES:
                result = subprocess.run(
                    ['wsl', 'pip3', 'install', '--user', pkg],
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

        Converts the Windows *build_dir* to a WSL path, then runs
        ``cd <path> && python3 -m buildozer android debug``.

        Returns a :class:`subprocess.Popen` with ``stdout`` piped.
        """
        wsl_build_dir = self.windows_to_wsl_path(build_dir_windows)

        shell_cmd = (
            'cd "{}" && '
            'export PATH="$HOME/.local/bin:$PATH" && '
            'python3 -m buildozer android debug'
        ).format(wsl_build_dir)

        logger.info("Running buildozer in WSL:")
        logger.info("  Windows dir: %s", build_dir_windows)
        logger.info("  WSL dir:     %s", wsl_build_dir)
        logger.info("  Command:     %s", shell_cmd)

        process = subprocess.Popen(
            ['wsl', 'bash', '-c', shell_cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        return process
