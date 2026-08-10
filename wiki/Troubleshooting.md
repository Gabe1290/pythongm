# Troubleshooting

> [English](Troubleshooting) | [Français](Troubleshooting_fr) | [Deutsch](Troubleshooting_de) | [Italiano](Troubleshooting_it) | [Español](Troubleshooting_es) | [Português](Troubleshooting_pt) | [Русский](Troubleshooting_ru) | [Slovenščina](Troubleshooting_sl) | [Українська](Troubleshooting_uk)

---

> [Back to Home](Home)

Common problems and where to look. For installation-specific issues
(Python not found, missing dependencies, Linux display libraries), see
[[Getting-Started]]'s own Troubleshooting section first — this page
covers problems that come up once PyGameMaker is already running.

---

## My game crashes or exits immediately when I press Test Game (F5)

**Run the IDE from a terminal, not a desktop shortcut, to see the error.**
A crashing test-game subprocess has its traceback logged to the IDE's own
console output (`python main.py` in a terminal) — if you launched the IDE
without a visible console (e.g. a Windows shortcut), that message has
nowhere to appear. Re-launch from a terminal and reproduce the crash to
see the real Python traceback.

Common causes:
- An **Execute Code** action or Code Editor custom code with a syntax
  error or a typo in a `game.*`/`self.*` call
- A collision or comparison action referencing an object that was since
  renamed or deleted

---

## The IDE itself crashed when I tried to open an editor

Check **`~/pygamemaker_crash.log`** (in your home folder) — object/room/
sprite editor crashes are written there specifically so they're visible
even when the IDE was launched without a console window. Include the
relevant section of that file if you report the bug.

---

## Export says "X not found" / a dependency is missing

Desktop and mobile exports (Windows .exe, macOS .app, Linux binary, Kivy/
Android/iOS) bundle a runtime via PyInstaller or Buildozer, and those
tools must be installed in the **same Python that runs the IDE** — a
system-wide install elsewhere on the machine doesn't count. The export
dialog's own error message gives the exact fix, but the short version:

- **No administrator rights needed.** Either activate your virtual
  environment and run `pip install <package>`, or install into your own
  account with `pip install --user <package>` — both work without admin.
- Installing everything at once: `pip install -r requirements.txt`
- **No setup at all?** Use the **HTML5 (Web Browser)** export instead —
  it needs nothing installed locally and the result runs in any browser.
  (Note this only applies to *building* the export — a finished `.exe`/
  `.app` needs nothing installed on the machine that just *runs* it.)

---

## I got a warning before Export ("X uses Y but there is no Z")

Export runs a project validation pass first and shows anything it finds
before the Export dialog appears — for example an object using
**Next Room** in a project with only one room, which would have no
effect. These are **warnings, not errors**: click OK and the export
continues; they're pointing at logic that likely won't do what you
expect, not blocking you from shipping.

---

## A sprite shows a red "(not imported)" badge in the resource tree

This means the sprite's image file is missing from disk (usually because
a project was copied or shared without its `sprites/` folder). It's
purely informational — runtime and export ignore it — and **clears
itself automatically the next time you save**, once the file is actually
present again. No manual fix needed beyond making sure the image file is
where the sprite expects it.

---

## Something else is wrong

- Check [[FAQ]] for common questions
- Report bugs on the [GitHub Issue Tracker](https://github.com/Gabe1290/pythongm/issues) — include your OS, Python version, and (if relevant) the console output or `~/pygamemaker_crash.log`

---

## Next Steps

- [[Getting-Started]] - Installation-time troubleshooting
- [[Exporting-Games]] - Full export reference
- [[FAQ]] - Frequently asked questions
