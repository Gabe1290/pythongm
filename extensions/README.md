# PyGameMaker extensions

An **extension** adds features to PyGameMaker — new actions, and (from Stage B)
new rendering — without those features living in the core engine. This folder
is where they go, one subfolder each.

If you want to see how someone extends an IDE, this is the place to look: an
extension is ordinary Python, in a folder you can read top to bottom.

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

`enabled: false` ships the extension switched off — it won't load.

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

See `docs/RAYCAST_EXTENSION_PLAN.md` for the roadmap, including the render
hooks that let an extension take over drawing (Stage B).
