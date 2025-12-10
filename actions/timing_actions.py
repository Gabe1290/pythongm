#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Timing Actions
"""

from actions.core import ActionDefinition, ActionParameter


TIMING_ACTIONS = {
    "set_alarm": ActionDefinition(
        name="set_alarm",
        display_name="Set Alarm",
        category="timing",
        tab="timing",
        description="Set an alarm to trigger after N steps",
        icon="⏰",
        parameters=[
            ActionParameter("alarm_number", "choice", "Alarm", "Which alarm (0-11)",
                          default="0", options=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]),
            ActionParameter("steps", "string", "Steps", "Number of steps until alarm triggers (-1 to disable)", default="30"),
            ActionParameter("relative", "boolean", "Relative", "Add to current alarm value", default=False)
        ]
    ),
    "set_timeline": ActionDefinition(
        name="set_timeline",
        display_name="Set Timeline",
        category="timing",
        tab="timing",
        description="Set instance timeline",
        icon="⏱️",
        parameters=[
            ActionParameter("timeline", "timeline", "Timeline", "Timeline to use")
        ]
    ),
    "set_timeline_position": ActionDefinition(
        name="set_timeline_position",
        display_name="Set Timeline Position",
        category="timing",
        tab="timing",
        description="Set timeline position",
        icon="⏱️",
        parameters=[
            ActionParameter("position", "int", "Position", "Timeline position", default=0),
            ActionParameter("relative", "boolean", "Relative", "Add to current position", default=False)
        ]
    ),
    "set_timeline_speed": ActionDefinition(
        name="set_timeline_speed",
        display_name="Set Timeline Speed",
        category="timing",
        tab="timing",
        description="Set timeline playback speed",
        icon="⏱️",
        parameters=[
            ActionParameter("speed", "float", "Speed", "Timeline speed", default=1.0)
        ]
    ),
    "start_timeline": ActionDefinition(
        name="start_timeline",
        display_name="Start Timeline",
        category="timing",
        tab="timing",
        description="Start timeline playback",
        icon="▶️"
    ),
    "pause_timeline": ActionDefinition(
        name="pause_timeline",
        display_name="Pause Timeline",
        category="timing",
        tab="timing",
        description="Pause timeline",
        icon="⏸️"
    ),
    "stop_timeline": ActionDefinition(
        name="stop_timeline",
        display_name="Stop Timeline",
        category="timing",
        tab="timing",
        description="Stop and reset timeline",
        icon="⏹️"
    ),
}

# ============================================================================
