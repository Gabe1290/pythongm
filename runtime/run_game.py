#!/usr/bin/env python3
"""
Standalone game runner script for subprocess execution.

This script is run in a separate process to avoid OpenGL conflicts
between Qt WebEngine (Chromium) and pygame's SDL/OpenGL.
"""

import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from runtime.game_runner import GameRunner
from core.logger import get_logger
logger = get_logger(__name__)


def _parse_args(argv):
    """Split argv into (positional, net_mode, net_host, net_port).

    Hand-rolled rather than argparse: the one existing caller
    (core/ide_window.py's subprocess.Popen) always passes exactly
    [project_json, language] positionally with no flags, and this keeps
    that path's behaviour (including the exact usage/error messages and
    exit(1) below) completely unchanged. --net-host/--net-client/
    --net-port are purely additive, for command-line multiplayer testing
    without authoring a set_network_mode action
    (see extensions/multiplayer_lan/handlers.py's PYGM_NET_* env vars).
    """
    positional = []
    net_mode = None
    net_host = None
    net_port = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--net-host":
            net_mode = "host"
            i += 1
        elif arg == "--net-client":
            net_mode = "client"
            i += 1
            if i < len(argv):
                net_host = argv[i]
                i += 1
        elif arg == "--net-port":
            i += 1
            if i < len(argv):
                net_port = argv[i]
                i += 1
        else:
            positional.append(arg)
            i += 1
    return positional, net_mode, net_host, net_port


def main() -> None:
    """Entry point for standalone game runner.

    Expects command line arguments:
        <path_to_project.json> - Path to the project JSON file
        [language_code] - Optional language code (default: 'en')
        [--net-host | --net-client HOST] [--net-port PORT] - Optional LAN
            multiplayer bootstrap (see extensions/multiplayer_lan)
    """
    positional, net_mode, net_host, net_port = _parse_args(sys.argv[1:])

    if len(positional) < 1:
        logger.error("Usage: python run_game.py <path_to_project.json> [language_code] "
                      "[--net-host | --net-client HOST] [--net-port PORT]")
        sys.exit(1)

    project_json = positional[0]
    language = positional[1] if len(positional) > 1 else 'en'

    if not os.path.exists(project_json):
        logger.error(f"Error: Project file not found: {project_json}")
        sys.exit(1)

    # Set the PYGM_NET_* env vars the multiplayer extension's frame-update
    # hooks read as a fallback (extensions/multiplayer_lan/handlers.py's
    # _env_config) -- this script stays extension-agnostic and never
    # imports that extension directly.
    if net_mode == "host":
        os.environ["PYGM_NET_MODE"] = "host"
    elif net_mode == "client":
        os.environ["PYGM_NET_MODE"] = "client"
        if net_host:
            os.environ["PYGM_NET_HOST_ADDR"] = net_host
    if net_port is not None:
        os.environ["PYGM_NET_PORT"] = str(net_port)

    try:
        runner = GameRunner(project_json)
        runner.language = language  # Set the language for runtime translations
        runner.run()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Game error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
