# Extensions

*[Home](Home) | [3D View](3D-View) | [Network](Network) | [Full Action Reference](Full-Action-Reference)*

---

An **extension** is a self-contained add-on that adds capabilities to
PyGameMaker without changing the core engine. An extension can contribute:

- new **actions** (they appear in the action picker like any built-in action),
- a new way to **draw a room** (a custom renderer), and
- matching **export code**, so games that use it still export to HTML5 and
  Kivy/Android.

The built-in **2.5D Raycast** extension (the [3D View](3D-View) feature) is the
worked example: it adds four "3D View" actions and a first-person renderer, and
it exports to all three targets. The built-in **LAN Multiplayer** extension
(the [Network](Network) feature) is a second, larger one: it adds 15
"Network" actions and six events, and networks a game over the local network
from the desktop export (as host or client) and the HTML5 export (as client).

---

## Enabling and disabling

Extensions ship **enabled**. You can turn one off (or opt into one that ships
disabled) without editing any code, via the `extensions` key in your config —
a map of `folder name → on/off`:

```json
"extensions": { "raycast_2_5d": false }
```

An **absent** entry means "use the extension's own default", so nothing ever
disappears because a key was missing. Changes take effect on the next start
(actions register at launch).

With the 2.5D Raycast extension disabled, a room that enables the first-person
view simply renders top-down.

---

## When a project needs an extension

Because an extension can be turned off, PyGameMaker helps you avoid surprises:

- **On load**, if a project uses actions from an extension that is currently
  disabled, the IDE shows a warning naming the extension and the affected
  features (so a 3D game doesn't silently render top-down).
- **On save**, the project records the extensions its actions depend on in
  `project.json` (a `requires_extensions` list) — a durable note anyone you
  share the project with can see. A project that uses no extension actions
  simply omits the field.

---

## Extensions vs plugins

Both add actions; they differ only in packaging:

| | Plugin | Extension |
|---|--------|-----------|
| Shape | a single `.py` file in `plugins/` | a folder in `extensions/` with a manifest |
| Best for | a small set of actions | a feature that spans several files and/or draws/exports |
| Example | the **Audio** actions (`plugins/audio_actions.py`) | **2.5D Raycast** (`extensions/raycast_2_5d/`) |

---

## What an extension folder looks like

For the curious (and for anyone writing one), an extension is a readable folder:

```
extensions/raycast_2_5d/
├── extension.json     # manifest: name, version, enabled, provides_actions
├── actions.py         # the action schemas (shown in the picker)
├── handlers.py        # what the actions do at runtime
├── renderer.py        # the custom room renderer (the raycaster)
├── state.py           # per-room state (namespaced under the room)
├── hud.py             # minimap / DOOM-bar geometry builders
├── export_html5.js    # the HTML5 port, injected into the web export
├── export_kivy.py     # the Kivy port, injected into the mobile/desktop export
└── README.md          # how it all fits together
```

The manifest's `provides_actions` list is what lets the IDE name the exact
extension when a project needs a disabled one.

---

## See Also

- [3D View](3D-View) — the feature the 2.5D Raycast extension provides
- [Network](Network) — the feature the LAN Multiplayer extension provides
- [Full Action Reference](Full-Action-Reference) — extension actions appear here too
- [Exporting Games](Exporting-Games) — extension features carry into exports
