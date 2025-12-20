# PyGameMaker

A GameMaker-style visual game development IDE for creating 2D games with Python.

![Version](https://img.shields.io/badge/version-0.10.0--alpha-blue)
![License](https://img.shields.io/badge/license-GPLv3-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)

## Educational Goals

This project serves a dual educational purpose:

1. **Learn Python through Game Development** - Use PyGameMaker to create games visually, then examine the generated Python/Pygame code to understand how game logic translates to real programming concepts.

2. **Learn Advanced Python through IDE Development** - Contribute to PyGameMaker itself and explore real-world software engineering: Qt GUI development, plugin architecture, code generation, internationalization, and more.

## Overview

PyGameMaker provides a familiar drag-and-drop interface inspired by classic GameMaker, allowing users to create games visually using:

- **Blockly Visual Programming** - Build game logic with visual code blocks
- **Traditional Event/Action System** - GM80-style event-driven programming
- **Asset Management** - Sprites, sounds, backgrounds, objects, and rooms
- **Multiple Export Targets** - HTML5, standalone executables, and more

## Features

- Visual sprite editor with animation strip support
- Room editor with instance placement
- Object editor with Blockly-based event programming
- Real-time game preview and testing
- Project import/export
- Multi-language support (English, French, German, Italian, Slovenian, Ukrainian)

## Requirements

- Python 3.10 or higher
- PySide6 (Qt for Python)
- Pygame
- Pillow

## Installation

```bash
# Clone the repository
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install PySide6 pygame Pillow
```

## Running

```bash
python main.py
```

## Project Structure

```
pygm2/
├── core/           # Core application logic
├── editors/        # Asset editors (sprite, object, room)
├── dialogs/        # UI dialogs
├── widgets/        # Custom Qt widgets
├── export/         # Game exporters (HTML5, EXE, Kivy)
├── config/         # Configuration and Blockly settings
├── translations/   # Language files
├── tutorials/      # Built-in tutorials
├── scripts/        # Build and utility scripts
└── docs/           # Documentation
```

## Building Standalone Executable

```bash
python scripts/build_nuitka.py
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Third-Party Libraries

- [PySide6](https://www.qt.io/qt-for-python) - Qt for Python (LGPLv3/GPLv3)
- [Pygame](https://www.pygame.org/) - Game development library (LGPLv2.1)
- [Pillow](https://python-pillow.org/) - Image processing (HPND License)
- [Blockly](https://developers.google.com/blockly) - Visual programming (Apache 2.0)

## Author

Gabriel Thullen

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
