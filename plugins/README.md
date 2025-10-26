# PyGameMaker IDE Plugins

This directory contains plugins that extend PyGameMaker's events and actions.

## Creating a Plugin

Create a Python file in this directory with the following structure:

```python
#!/usr/bin/env python3
"""
My Custom Plugin
"""

from events.event_types import EventType
from events.action_types import ActionType, ActionParameter

# Plugin Metadata
PLUGIN_NAME = "My Plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "Your Name"
PLUGIN_DESCRIPTION = "Description of what your plugin does"

# Define custom events (optional)
PLUGIN_EVENTS = {
    "my_event": EventType(
        name="my_event",
        display_name="My Custom Event",
        description="Description of when this event triggers",
        icon="🎯",
        category="Custom",
        parameters=[]
    ),
}

# Define custom actions (required)
PLUGIN_ACTIONS = {
    "my_action": ActionType(
        name="my_action",
        display_name="My Custom Action",
        description="Description of what this action does",
        category="Custom",
        icon="⚡",
        parameters=[
            ActionParameter(
                name="message",
                display_name="Message",
                param_type="string",
                default_value="Hello!",
                description="A message to display"
            )
        ]
    ),
}

# Define action executors (required)
class PluginExecutor:
    """Handles execution of plugin actions"""

    def execute_my_action_action(self, instance, parameters):
        """Execute my custom action"""
        message = parameters.get("message", "")
        print(f"My Action: {message}")
        # Add your action logic here
```

## Available Parameter Types

- `string`: Text input
- `number`: Integer input
- `float`: Decimal number input
- `choice`: Dropdown selection (requires `choices` list)
- `boolean`: Checkbox
- `color`: Color picker
- `sprite`: Sprite selector
- `object`: Object selector
- `sound`: Sound selector
- `room`: Room selector
- `code`: Multi-line code editor
- `position`: X,Y coordinate pair
- `action_list`: List of actions (for conditionals)

## Plugin Files

- `audio_actions.py` - Example plugin for sound/music actions
- `drawing_actions.py` - Example plugin for drawing actions

## Loading Plugins

Plugins are automatically loaded when the IDE starts. To reload plugins during development,
restart the IDE or use the Plugin Manager (coming soon).
