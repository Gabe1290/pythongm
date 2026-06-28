# Getting Started

> [English](Getting-Started) | [Français](Demarrage_fr) | [Deutsch](Erste_Schritte_de) | [Italiano](Iniziare_it) | [Español](Empezar_es) | [Português](Comecar_pt) | [Slovenščina](Zacetek_sl) | [Українська](Pochatok_uk) | [Русский](Nachalo_ru)

---

> [Back to Home](Home)

This guide will help you get PyGameMaker up and running on your system.

---

## System Requirements

- **Python** 3.10 or higher
- **Operating System:** Windows, Linux, or macOS
- **Disk Space:** ~500 MB for installation
- **RAM:** 4 GB minimum, 8 GB recommended

---

## Installation

### Step 1: Install Python

Download Python 3.10+ from [python.org](https://www.python.org/downloads/) and install it. Make sure to check "Add Python to PATH" during installation on Windows.

### Step 2: Clone the Repository

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
```

Or download the ZIP file from the [Releases page](https://github.com/Gabe1290/pythongm/releases).

### Step 3: Create a Virtual Environment

Creating a virtual environment keeps PyGameMaker's dependencies isolated:

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run PyGameMaker

```bash
python main.py
```

---

## First Launch

When you first launch PyGameMaker, you'll see:

1. **Menu Bar** - File, Edit, Resources, Run, and Help menus
2. **Resource Tree** - Left panel showing project assets (Sprites, Sounds, Backgrounds, Objects, Rooms)
3. **Workspace** - Central area for editing assets
4. **Properties Panel** - Right panel for asset properties

---

## Creating Your First Project

1. Go to **File > New Project**
2. Choose a location and name for your project
3. A new project folder will be created with the standard structure

---

## Project Structure

Each PyGameMaker project contains:

```
my_project/
├── project.json      # Project settings
├── sprites/          # Sprite images
├── sounds/           # Audio files
├── backgrounds/      # Background images
├── objects/          # Game object definitions
├── rooms/            # Level layouts
├── fonts/            # Font files
├── scripts/          # Custom scripts
└── data/             # Custom data files
```

---

## Changing Language

PyGameMaker supports multiple languages:

1. Go to **Edit > Preferences** (or **File > Settings**)
2. Select your preferred language from the dropdown
3. Restart PyGameMaker to apply the change

Available languages: English, French, German, Italian, Spanish, Portuguese, Slovenian, Ukrainian, Russian

---

## Next Steps

- [[Creating-Your-First-Game]] - Build a simple game step by step
- [[Object-Editor]] - Learn how to create game objects
- [[Room-Editor]] - Design your game levels
- [[Events-and-Actions]] - Understand game logic

---

## Troubleshooting

### Python not found
Make sure Python is installed and added to your PATH. Try running `python --version` to verify.

### Missing dependencies
If you get import errors, try reinstalling dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### Display issues
On Linux, you may need to install additional packages:
```bash
sudo apt install python3-pyqt6 libxcb-cursor0
```

---

## Getting Help

- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Report bugs or request features
- [[FAQ]] - Common questions and answers
