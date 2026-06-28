# Frequently Asked Questions

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

> [Back to Home](Home)

---

## General Questions

### What is PyGameMaker?

PyGameMaker is an open-source game development IDE inspired by GameMaker 7.0. It allows you to create 2D games using visual programming (Google Blockly) or an event-action system, without needing to write code.

### Is PyGameMaker free?

Yes! PyGameMaker is completely free and open-source — the source code is under the MIT License, and the documentation under CC BY 4.0.

### What platforms can I export to?

- Windows (standalone .exe)
- HTML5 (web browsers)
- Linux (native binary)
- Mobile (iOS/Android via Kivy)

### Do I need programming experience?

No! PyGameMaker is designed for beginners. You can create games using:
- Drag-and-drop Blockly blocks
- Point-and-click event/action system
- No coding required

### Is it compatible with GameMaker files?

PyGameMaker is inspired by GameMaker 7.0 but uses its own project format. You cannot directly import GameMaker files, but the concepts and workflow are similar.

---

## Installation

### What are the system requirements?

- Python 3.10 or higher
- Windows, Linux, or macOS
- 4 GB RAM minimum (8 GB recommended)
- ~500 MB disk space

### How do I install PyGameMaker?

See [[Getting-Started]] for detailed installation instructions. The short version:

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### Python is not recognized / not found

Make sure Python is installed and added to your system PATH. You can verify by running:

```bash
python --version
```

If this fails, reinstall Python and check "Add Python to PATH" during installation.

### I get import errors when starting

Try reinstalling the dependencies:

```bash
pip install -r requirements.txt --force-reinstall
```

---

## Projects

### Where are my projects saved?

Projects are saved in folders you choose. Each project contains:
- `project.json` - Main project file
- Folders for sprites, sounds, objects, rooms, etc.

### Can I have multiple projects open?

Currently, PyGameMaker opens one project at a time. Use **File > Open Project** to switch between projects.

### How do I backup my project?

Simply copy the entire project folder. All assets and settings are contained within. Consider using git for version control:

```bash
cd my_project
git init
git add .
git commit -m "Initial backup"
```

### My project won't open / is corrupted

Try these steps:
1. Check if `project.json` exists and isn't empty
2. Open `project.json` in a text editor to check for JSON errors
3. Restore from a backup if available
4. Check the console output for specific error messages

---

## Objects and Events

### What's the difference between an object and an instance?

- **Object**: A blueprint/template defining behavior
- **Instance**: A specific copy of an object placed in a room

For example, `obj_enemy` is an object. Placing 5 enemies in a room creates 5 instances of `obj_enemy`.

### Why isn't my event triggering?

Common causes:
1. **Wrong event type**: Make sure you're using the right event (e.g., "Key Press" vs "Keyboard")
2. **No instances**: The object must have instances in the room
3. **Object not visible**: Check the visible property
4. **Execution order**: Some events run before others

### How do I make objects interact?

Use Collision events:
1. Open the object that should detect collision
2. Add **Collision with [other_object]** event
3. Add actions for what happens on collision

### What's the difference between "Keyboard" and "Key Press" events?

- **Keyboard [key]**: Triggers every frame while the key is held
- **Key Press [key]**: Triggers once when the key is first pressed
- **Key Release [key]**: Triggers once when the key is released

---

## Rooms

### Which room loads first?

The first room in the resource tree (top of the list) loads when the game starts. Drag rooms to reorder them.

### How do I change rooms?

Use room actions:
- **Next Room**: Go to the next room in order
- **Previous Room**: Go to the previous room
- **Go to Room**: Jump to a specific room

### Objects disappear when I change rooms

Objects are destroyed when leaving a room unless they are marked as **Persistent** in their properties.

### My room is too big/small on screen

The game window size matches the first room's dimensions. You can:
- Change room size to match desired window size
- Use Views to show only part of the room

---

## Graphics and Sprites

### What image formats are supported?

- PNG (recommended, supports transparency)
- JPEG/JPG
- BMP
- GIF (first frame only)

### My sprite appears at the wrong position

Check the **Origin** setting in the sprite editor. The origin is the anchor point for positioning. Common settings:
- Top-left (0, 0): Default
- Center: Good for rotating objects
- Bottom-center: Good for characters

### How do I animate a sprite?

1. Create a sprite with multiple frames (horizontal strip)
2. Set **Number of Frames** in sprite properties
3. Adjust **Animation Speed** (frames per second)

### Sprites are blurry

This happens when scaling sprites. For pixel art, disable interpolation/smoothing in game settings if available.

---

## Sound and Music

### What audio formats are supported?

- WAV (uncompressed)
- OGG (recommended for music)
- MP3

### Sound doesn't play

Check:
1. Audio file exists in the sounds folder
2. File format is supported
3. You're using the correct sound name in actions
4. Browser may require user interaction (for HTML5)

### How do I loop background music?

Use the **Play Music** action with the loop option enabled, or use **Play Sound** with the loop parameter set to true.

---

## Exporting

### My exported game doesn't work

Common issues:
- **Windows**: Missing DLLs - make sure the entire output folder is included
- **HTML5**: Browser blocking local files - host on a server
- **Missing assets**: Check that all files are included

### The exported file is huge

Game size includes Python and all libraries. To reduce size:
- Remove unused assets
- Compress images and audio
- Use appropriate formats (OGG instead of WAV)
- Enable UPX compression for Windows builds

### Can I sell games made with PyGameMaker?

Yes! Games you create are entirely yours to sell. PyGameMaker's source code is under the permissive MIT License, so you can use it freely in commercial projects — and unlike copyleft licenses, you are not required to open-source your own modifications (though contributions back are always welcome).

---

## Blockly / Visual Programming

### Where do I find the Blockly editor?

1. Open an object
2. Click the **Blockly** tab in the object editor
3. The visual programming workspace appears

### How do I switch between Blockly and events?

Both systems work on the same object. The Blockly tab and Events tab show different views of the same logic. Changes in one are reflected in the other.

### My Blockly blocks disappeared

Check:
1. You're viewing the correct object
2. Scroll around the workspace (blocks might be off-screen)
3. Check the zoom level

---

## Performance

### My game runs slowly

Tips for better performance:
1. Reduce the number of instances
2. Avoid heavy calculations in Step events
3. Use alarms instead of frame counting
4. Optimize sprite sizes
5. Destroy instances that leave the room

### The Step event runs too often

The Step event runs every frame (60 times/second by default). Use:
- Alarms for delayed actions
- Conditions to check before heavy operations
- Lower room speed if appropriate

---

## Getting Help

### Where can I report bugs?

Report bugs on the [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) page. Include:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Your operating system and Python version

### How can I contribute?

Contributions are welcome! See the GitHub repository for:
- Code contributions
- Bug reports
- Feature requests
- Translations
- Documentation improvements

### Where can I learn more?

- [[Getting-Started]] - Installation and basics
- [[Creating-Your-First-Game]] - Step-by-step tutorial
- [[Events-and-Actions]] - Complete reference
- [[Visual-Programming]] - Blockly guide
