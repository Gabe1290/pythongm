# PyGameMaker Junior: Teacher Guide

## What Junior Is

Junior is a simplified edition of PyGameMaker for students aged about 8 to 9.
It is the same program and the same project files as the other editions. It
only hides things, so a project made in Junior opens normally in Beginner,
Advanced or Development, and the other way round.

## Switching It On

1. Open **Tools > Preferences > General > IDE Edition** and choose **Junior**.
2. Click OK, then **restart the IDE**. The look, font and menus apply at
   startup.
3. To go back, repeat the steps and choose another edition. Preferences stays
   in the Tools menu in Junior for this reason.

Notes:
- **Shared computers:** the edition is a per-user setting. If you set up
  many machines, set `"edition": "junior"` in `.pygamemaker/config.json` in
  the user's home folder.
- **Theme and font:** if someone ever changed the theme or font in
  Preferences on a machine, that choice wins over Junior's larger font and
  high-contrast theme. Reset them there if the machine looks unchanged.
- **Blockly toolbox:** Junior's block set applies to **new** projects. An
  existing project keeps the block set it was saved with. Switching edition in
  Preferences also applies the new edition's block set to the open project.

## What Students See

| Area | In Junior |
|---|---|
| Look | Larger font, larger toolbar icons, high-contrast theme |
| File menu | New, Open, Save, Save As, Close, Recent, **Export as HTML5**, Exit |
| Assets menu | Import sprite, sound, background; **Create Sprite**, Object, Room |
| Build menu | **Test Game** |
| Tools menu | Preferences, Restore Deleted Assets, Language |
| Object editor | **Blockly only.** No Event List tab, no Code Editor tab |
| Blockly toolbox | 46 blocks, exactly those the Junior tutorials use |
| Blockly right-click | Duplicate and Delete on blocks; Undo, Redo and Clean up on the workspace |
| Export | HTML5 only |

Hidden on purpose: other exports (desktop, Android, Kivy, zip), GameMaker
import, auto-save settings, Project Settings, Find and Replace, scripts and
fonts, object and room packages, Debug and Build, Configure Action Blocks and
the maintenance tools.

Still visible: the small "Standard" events panel on the left of the object
editor. It shows the events Blockly builds. Students can ignore it.

## Suggested Lesson Plan (about 60 minutes)

| Time | Activity |
|---|---|
| 0-10 | Tour: toolbar, resources, play button. Open a sample from the Welcome tab and press F5 |
| 10-25 | Student handout, Parts 1 and 2: draw a sprite |
| 25-45 | Parts 3 and 4: make an object move, build a room, play |
| 45-55 | Part 5: export as HTML5 and open it in the browser |
| 55-60 | Share, and the "Think About It" questions as an exit ticket |

For a 45-minute slot, do Parts 1 to 4 and leave the export for next time.

Next lessons: the Junior tutorials under **Help > Tutorials**: Getting Started,
Your First Game, Pong, Breakout, Fruit Fusion, Fruit Basket. Each has its own
student handout and teacher guide.

## Common Problems

| Symptom | Cause and fix |
|---|---|
| Object does not move | No block under the event, or the object is not placed in the room |
| Hero slides forever | Needs **Keyboard: No key** with **Stop moving** |
| Sprite not visible | Object has no sprite chosen |
| "Name Already Used" | A sprite with that name exists. Choose another name |
| A name is rejected | Use letters, numbers and underscores, with no spaces or special characters |
| Deleted by mistake | Tools > Restore Deleted Assets |
| Grey game window | Often a slow or low-memory computer. Wait, then retry |
| Exported game needs internet | Games using Python code load a runtime online. When asked, choose to bundle it for offline use |
| A sample uses a block students cannot find | Samples may use blocks outside Junior's set. They still run. Students just cannot add that block again |

## Limits to Know

- Students cannot add the blocks that Beginner has and Junior does not, for
  example Set Gravity, If Collision and Sleep, even when a sample uses them.
- A sprite starts at 32 by 32 pixels. Students can resize it in the sprite
  editor.
- HTML5 is the only way to share. A teacher who needs another format can
  switch the edition to Beginner and use **Build > Export Game**.

## Checking Work

Ask each student to show: one sprite they drew, one object that moves, a room,
and the exported `.html` file running in the browser.
