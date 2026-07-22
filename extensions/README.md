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
