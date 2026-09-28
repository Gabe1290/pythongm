# PyGameMaker extensions

An **extension** adds features to PyGameMaker — new actions, and new rendering —
without those features living in the core engine. This folder is where they go,
one subfolder each.

If you want to see how someone extends an IDE, this is the place to look: an
extension is ordinary Python, in a folder you can read top to bottom. The
[**2.5D raycast view**](raycast_2_5d/) is the worked example — a whole
first-person renderer, hooked in through the same contract a tiny plugin uses.

## Two packagings, one contract

| | Where | Use it for |
|---|---|---|
| **Plugin** (single file) | `plugins/name.py` | something small — a few related actions |
| **Extension** (folder) | `extensions/name/` | a feature that needs several modules |

Both expose the **same three things**, so there is only one contract to learn.
Moving from one to the other is just moving code.

## What a folder extension looks like

```
extensions/
  my_feature/
    extension.json     # manifest — required; it's what marks the folder
    __init__.py        # the entry point; exposes the contract below
    schemas.py         # (optional) split things out however you like
    README.md          # (recommended) what it does and how it hooks in
```

### `extension.json`

```json
{
  "name": "My Feature",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "What this adds to PyGameMaker",
  "enabled": true
}
```

`enabled: false` ships the extension switched off — useful for something
experimental that people opt into.

## Turning extensions on and off

The manifest sets the **default**; a user's config overrides it either way, so
nobody has to edit files to switch a feature off (or to opt into one that ships
disabled). The config key is `extensions`, a map of folder name → on/off:

```json
"extensions": { "my_feature": false }
```

An **absent** entry means "use the manifest". The config only records
deliberate choices, so an extension can never vanish because a key was missing.

From code:

```python
from events.plugin_loader import (
    list_available_extensions, set_extension_enabled,
)

list_available_extensions()          # folder, name, version, description, enabled
set_extension_enabled("my_feature", False)
```

`list_available_extensions()` reads manifests **without importing** any
extension code, so a settings screen can list them safely. Changes take effect
on the next restart, since actions register at startup.

### `__init__.py` — the contract

```python
from events.action_types import ActionType, ActionParameter

# 1. Action SCHEMAS: what the editor shows in the action picker / Blockly.
PLUGIN_ACTIONS = {
    "my_action": ActionType(
        name="my_action",
        display_name="My Action",
        description="What it does",
        category="My Category",
        parameters=[
            ActionParameter(name="amount", display_name="Amount",
                            param_type="number", default_value=1),
        ],
    ),
}

# 2. (optional) PLUGIN_EVENTS — new event types, same shape.

# 3. HANDLERS: what actually runs when the action fires.
class PluginExecutor:
    def execute_my_action_action(self, instance, parameters):
        # method name is execute_<action name>_action
        instance.x += float(parameters.get("amount", 1))
```

Because the folder is imported as a real **package**, you can split code up and
import your own modules relatively:

```python
from .schemas import PLUGIN_ACTIONS      # works
```

### Drawing a room yourself (the render hook)

Actions are enough for most extensions. A feature that *replaces how a room is
drawn* — an isometric view, a shader pass, the 2.5D raycast view — declares a
**room renderer** instead (see `runtime/extension_hooks.py`), the same
declarative way it declares actions:

```python
def render_room(room, screen):
    if not room.extension_state.get("my_view"):
        return False           # not mine — let the engine draw it top-down
    ...draw into screen...
    return True                # I drew this room

PLUGIN_ROOM_RENDERERS = [render_room]
```

Return `True` only if you actually drew it: core then skips its own top-down
pass but **still runs the per-instance draw-event pass**, so HUD actions
composite on top. Return `False` to decline. A renderer that raises is logged
and skipped, never crashing the game. Store per-room state in
`room.extension_state[<your key>]` rather than adding attributes to engine
classes. [`raycast_2_5d/`](raycast_2_5d/) is a full worked example.

### Drawing on top of one instance (the overlay hook)

The opposite shape: the room is ordinary, but *one instance* needs extra
drawing — a simulated robot body with its on-screen buttons. Declare an
**instance overlay**; after the room is drawn, every instance is offered to
it in screen space, below the GUI layer:

```python
def draw_robot(instance, screen):
    st = instance.extension_state.get("my_robot")
    if st:
        ...draw at st["x"], st["y"]...

PLUGIN_INSTANCE_OVERLAYS = [draw_robot]
```

Per-instance state goes in `instance.extension_state[<your key>]`, the
per-instance twin of the room dict above. Overlays don't claim; several may
draw on the same instance.

### Seeing raw input (the input hook)

On-screen buttons the player clicks, or keys that drive a simulated device,
aren't authored keyboard/mouse events. Declare a dict of the handlers you
need:

```python
PLUGIN_INPUT_HANDLERS = [{
    "key_down":   lambda instance, key: ...,        # per instance; -> True if you fired something
    "key_up":     lambda instance, key: ...,        # per instance
    "mouse_down": lambda runner, button, x, y: ...,  # once per click; -> True swallows it
    "mouse_up":   lambda runner, button, x, y: ...,  # once per release; -> True swallows it
}]
```

Keyboard handlers run inside the engine's per-instance loop right after
that instance's own keyboard events. Mouse handlers run before any mouse
event, with raw screen coordinates; returning `True` means "that click was
mine" and no mouse event fires for it.

### Adding a new kind of project asset (the asset-type hook)

Rooms, objects and sprites keep their payload in `<type>/<name>.json` next
to `project.json`. An extension can add a kind of its own — a robot arena,
say — and the project manager saves, loads, strips and cleans up its side
files exactly like the built-in ones:

```python
from core.asset_types import SideFileAssetType

PLUGIN_ASSET_TYPES = [SideFileAssetType(
    plural="arenas", singular="arena", description="Robot arenas",
    file_keys=("size", "walls"),   # merged from arenas/<name>.json on load
    strip_keys=("walls",),         # kept only in the side file on save
)]
```

`project.json` keeps the rest of each entry as a summary. Register it
before any project loads (extensions load at startup, so that's automatic).

### Adding menu entries and toolbar buttons (the IDE hooks)

A feature with its own tooling — a robot simulator window, a code export
for a device — needs a way in from the IDE window. Declare builders; each
gets the live Qt menu or toolbar once the built-in entries exist:

```python
def build_tools_menu(ide, menu):
    menu.addSeparator()
    sub = menu.addMenu(ide.tr("My Feature"))
    sub.addAction(ide.create_action(ide.tr("Open Simulator..."), None, lambda: ...))

def build_toolbar(ide, toolbar):
    toolbar.addAction(ide.create_action(ide.tr("My Feature"), None, lambda: ...))

PLUGIN_IDE_MENUS = [("tools", build_tools_menu)]   # file/edit/assets/build/tools/help
PLUGIN_IDE_TOOLBAR = [build_toolbar]
```

These only run in the IDE; the game process ignores them.

A new asset kind (see the asset-type hook above) also needs a row in the
asset tree and a way to open it:

```python
from core.ide_extension_points import AssetTreeCategory

PLUGIN_ASSET_TREE_CATEGORIES = [AssetTreeCategory(
    plural="arenas", singular="arena", label="Arenas", icon="🏟️",
    open_editor=lambda ide, name, data: ...,          # double-click
    new_asset_template=lambda name: {"name": name, "asset_type": "arena", "imported": True},
)]
```

The category appears after "Rooms"; `importable=False` (the default) means
it's authored in its editor rather than imported from a file.

A feature that owns a *family of events* (a robot's sensors and buttons)
can add its own tab beside "Standard" in the object editor:

```python
from core.ide_extension_points import ObjectEditorPanel

PLUGIN_OBJECT_EDITOR_PANELS = [ObjectEditorPanel(
    key="robot", label="🤖 Robot", factory=RobotEventsPanel,   # a QWidget class
    owned_events=lambda: ROBOT_EVENT_TYPES.keys(),
    is_visible=lambda: Config.get("show_robot_tab", False),
)]
```

The panel widget exposes `events_modified`/`event_selected` signals and
`load_events_data(dict)`/`get_events_data()`; the editor merges the panel's
events back into the object and drops owned events the panel removed.

## How loading works

`events/plugin_loader.py` is the single load point, called by **both** the IDE
(so your actions appear in the editor) and the game runtime (so they actually
run). It loads `plugins/*.py` first, then `extensions/*/`.

Two consequences worth knowing:

- **Names are first-come.** If an action name already exists, the later
  registration is skipped. Core actions win over plugins, and plugins win over
  extensions. Pick distinctive names.
- **The IDE loads schemas only.** It has no game running, so it registers your
  `PLUGIN_ACTIONS` but not your `PluginExecutor`. The handlers register in the
  game process. If your action appears in the editor but does nothing when you
  press Play, that's the split to check.

## Writing one

1. Copy an existing extension folder, or start from the skeleton above.
2. Restart the IDE — extensions load at startup.
3. Your actions appear in the action picker under the `category` you gave them.

See `docs/RAYCAST_EXTENSION_PLAN.md` for the roadmap, and
[`raycast_2_5d/README.md`](raycast_2_5d/README.md) for a complete extension you
can read end to end.
