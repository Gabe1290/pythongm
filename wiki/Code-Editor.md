# Code Editor

> [English](Code-Editor) | [Français](Code-Editor_fr) | [Deutsch](Code-Editor_de)

---

> [Back to Home](Home)

Every object in PyGameMaker has a **Code Editor** tab alongside Event List
and Blockly — a third way to work with the same events and actions,
this time as real Python. It isn't a one-way export: code you write here
is parsed back into structured events and actions, so it stays in sync
with the other two views.

---

## Opening the Code Editor

1. Open an object in the Object Editor
2. Click the **💻 Code Editor** tab

![The Code Editor in "View Generated Code" mode: a class with one method
per event (on_create, on_step, on_collision_obj_power, ...), showing the
real Python your visual events and actions compile to](images/code-editor.png)

---

## Two Modes

A dropdown at the top switches between them:

### 📖 View Generated Code

Read-only. Shows the Python your object's current events and actions
compile to — one method per event (`on_create`, `on_step`,
`on_collision_obj_enemy`, ...), calling into `self.*` and `game.*` just
like the runtime does. An action the generator doesn't have a clean
Python mapping for still appears, marked with a comment
(`# Unknown action: ...`) above the line it produced — nothing is hidden,
even for edge cases. Click **🔄 Refresh** to re-generate after changing
events elsewhere.

### ✏️ Edit Custom Code

Editable, with Python syntax highlighting. Start typing (or edit the
seed code carried over from View mode) and PyGameMaker parses your class
about 1.5 seconds after you stop — a status pill next to the toolbar
shows **idle / busy / error / empty** as it does. On a successful parse,
your methods **replace** the object's events and actions (not merge) —
whatever event methods your code defines become that object's event
list, visible immediately back in the Event List and Blockly tabs.

If parsing fails (a syntax error, or code the parser can't map back to
events), the status pill shows the error and nothing is applied yet —
your object's events stay as they were until the code parses cleanly.

---

## Why Use It

- **Speed** — some logic (a multi-branch calculation, a loop, a one-off
  formula) is faster to type than to assemble from blocks or an action
  list.
- **Learning bridge** — switch a beginner-built object's events into View
  mode to see the real code equivalent, a natural next step for a student
  moving from visual programming toward Python.
- **Precision** — anything expressible as a plain Python method on the
  object works, without waiting for a matching visual action to exist.

This is the same underlying mechanism as the **Execute Code** action
available from the action list / Blockly (category *Control*) — the Code
Editor tab just works at the scale of a whole object instead of one
action at a time.

---

## Next Steps

- [[Object-Editor]] - Where the Code Editor tab lives
- [[Visual-Programming]] - The Blockly view of the same events
- [[Events-and-Actions]] - What each action actually does
