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


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_game.py <path_to_project.json> [language_code]")
        sys.exit(1)

    project_json = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'en'

    if not os.path.exists(project_json):
        print(f"Error: Project file not found: {project_json}")
        sys.exit(1)

    try:
        runner = GameRunner(project_json)
        runner.language = language  # Set the language for runtime translations
        runner.run()
        sys.exit(0)
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
