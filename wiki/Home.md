# PyGameMaker IDE

> **Select your language / Choisissez votre langue / Wählen Sie Ihre Sprache:**
>
> [English](Home) | [Français](Home_fr) | [Deutsch](Home_de) | [Italiano](Home_it) | [Español](Home_es) | [Português](Home_pt) | [Slovenščina](Home_sl) | [Українська](Home_uk) | [Русский](Home_ru)

---

**A visual game development environment inspired by GameMaker 7.0**

PyGameMaker is an open-source IDE that makes 2D game creation accessible through visual block-based programming (Google Blockly) and an event-action system. Create games without deep programming knowledge, then export them to Windows, Linux, HTML5, or mobile platforms.

---

## Choose Your Skill Level

PyGameMaker uses **presets** to control which events and actions are available. This helps beginners focus on essential features while allowing experienced users to access the full toolset.

| Preset | Best For | Features |
|--------|----------|----------|
| [**Beginner**](Beginner-Preset) | New to game development | 4 events, 17 actions - Movement, collisions, score, rooms |
| [**Intermediate**](Intermediate-Preset) | Some experience | +4 events, +12 actions - Lives, health, sound, alarms, drawing |
| **Advanced** | Experienced users | All 40+ events and actions available |

**New users:** Start with the [Beginner Preset](Beginner-Preset) to learn the fundamentals without being overwhelmed.

See the [Preset Guide](Preset-Guide) for a complete overview of the preset system.

---

## Features at a Glance

| Feature | Description |
|---------|-------------|
| **Visual Programming** | Drag-and-drop coding with Google Blockly 12.x |
| **Event-Action System** | GameMaker 7.0 compatible event-driven logic |
| **Skill-Based Presets** | Beginner, Intermediate, and Advanced feature sets |
| **Multi-Platform Export** | Windows EXE, HTML5, Linux, Kivy (mobile/desktop) |
| **Asset Management** | Sprites, sounds, backgrounds, fonts, and rooms |
| **Multi-Language UI** | English, French, German, Italian, Spanish, Portuguese, Slovenian, Ukrainian, Russian |
| **Extensible** | Plugin system for custom events and actions |

---

## Getting Started

### System Requirements

- **Python** 3.10 or higher
- **Operating System:** Windows, Linux, or macOS

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Gabe1290/pythongm.git
   cd pythongm
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run PyGameMaker:
   ```bash
   python main.py
   ```

---

## Core Concepts

### Objects
Game entities with sprites, properties, and behaviors. Each object can have multiple events with associated actions.

### Events
Triggers that execute actions when specific conditions occur:
- **Create** - When an instance is created
- **Step** - Every frame (typically 60 FPS)
- **Draw** - Custom rendering phase
- **Destroy** - When an instance is destroyed
- **Keyboard** - Key press, release, or held
- **Mouse** - Clicks, movement, enter/leave
- **Collision** - When instances touch
- **Alarm** - Countdown timers (12 available)

See the [Event Reference](Event-Reference) for complete documentation.

### Actions
Operations performed when events trigger. 40+ built-in actions for:
- Movement and physics
- Drawing and sprites
- Score, lives, and health
- Sound and music
- Instance and room management

See the [Full Action Reference](Full-Action-Reference) for complete documentation.

### Rooms
Game levels where you place object instances, set backgrounds, and define the play area.

---

## Visual Programming with Blockly

PyGameMaker integrates Google Blockly for visual programming. Blocks are organized into categories:

- **Events** - Create, Step, Draw, Keyboard, Mouse
- **Movement** - Speed, direction, position, gravity
- **Timing** - Alarms and delays
- **Drawing** - Shapes, text, sprites
- **Score/Lives/Health** - Game state tracking
- **Instance** - Create and destroy objects
- **Room** - Navigation and management
- **Values** - Variables and expressions
- **Sound** - Audio playback
- **Output** - Debug and display

---

## Export Options

### Windows EXE
Standalone Windows executables using PyInstaller. No Python required on the target machine.

### HTML5
Single-file web games that run in any modern browser. Compressed with gzip for fast loading.

### Linux
Native Linux executables for Python 3.10+ environments.

### Kivy
Cross-platform apps for mobile (iOS/Android) and desktop via Buildozer.

---

## Project Structure

```
project_name/
├── project.json      # Project configuration
├── backgrounds/      # Background images and metadata
├── data/             # Custom data files
├── fonts/            # Font definitions
├── objects/          # Object definitions (JSON)
├── rooms/            # Room layouts (JSON)
├── scripts/          # Custom scripts
├── sounds/           # Audio files and metadata
├── sprites/          # Sprite images and metadata
└── thumbnails/       # Generated asset thumbnails
```

---

## Wiki Contents

### Presets & Reference
- [Preset Guide](Preset-Guide) - Overview of the preset system
- [Beginner Preset](Beginner-Preset) - Essential features for new users
- [Intermediate Preset](Intermediate-Preset) - Additional features for growing skills
- [Event Reference](Event-Reference) - Complete event documentation
- [Full Action Reference](Full-Action-Reference) - Complete action documentation

### Tutorials & Guides
- [Getting-Started](Getting-Started) - First steps with PyGameMaker
- [Creating-Your-First-Game](Creating-Your-First-Game) - Tutorial walkthrough
- [Tutorial: Breakout Game](Tutorial-Breakout) - Create a classic brick breaker game
- [Introduction to Game Creation](Getting-Started-Breakout) - Comprehensive beginner tutorial
- [Object-Editor](Object-Editor) - Working with game objects
- [Room-Editor](Room-Editor) - Designing levels
- [Events-and-Actions](Events-and-Actions) - Game logic reference
- [Visual-Programming](Visual-Programming) - Using Blockly blocks
- [Exporting-Games](Exporting-Games) - Build for different platforms
- [FAQ](FAQ) - Frequently asked questions

---

## Contributing

Contributions are welcome! See our contributing guidelines for:
- Bug reports and feature requests
- Code contributions
- Translations
- Documentation improvements

---

## License

PyGameMaker is licensed under the **GNU General Public License v3 (GPLv3)**.

Copyright (c) 2024-2025 Gabriel Thullen

---

## Links

- [GitHub Repository](https://github.com/Gabe1290/pythongm)
- [Issue Tracker](https://github.com/Gabe1290/pythongm/issues)
- [Releases](https://github.com/Gabe1290/pythongm/releases)
