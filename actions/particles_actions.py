#!/usr/bin/env python3
"""
GameMaker 8.0 Actions - Particles Actions
"""

from actions.core import ActionDefinition, ActionParameter


PARTICLES_ACTIONS = {
    "create_particle_system": ActionDefinition(
        name="create_particle_system",
        display_name="Create Particle System",
        category="particles",
        tab="particles",
        description="Create a particle system",
        icon="✨",
        parameters=[
            ActionParameter("depth", "int", "Depth", "Drawing depth", default=0)
        ],
        implemented=False
    ),
    "destroy_particle_system": ActionDefinition(
        name="destroy_particle_system",
        display_name="Destroy Particle System",
        category="particles",
        tab="particles",
        description="Remove particle system",
        icon="💥",
        implemented=False
    ),
    "clear_particles": ActionDefinition(
        name="clear_particles",
        display_name="Clear All Particles",
        category="particles",
        tab="particles",
        description="Remove all particles",
        icon="🧹",
        implemented=False
    ),
    "create_particle_type": ActionDefinition(
        name="create_particle_type",
        display_name="Create Particle Type",
        category="particles",
        tab="particles",
        description="Define particle type",
        icon="⚙️",
        parameters=[
            ActionParameter("sprite", "sprite", "Sprite", "Particle sprite"),
            ActionParameter("size_min", "float", "Min Size", "Minimum size", default=1.0),
            ActionParameter("size_max", "float", "Max Size", "Maximum size", default=1.0),
            ActionParameter("size_increase", "float", "Size Increase", "Size change", default=0),
            ActionParameter("color", "color", "Color", "Particle color", default="#FFFFFF"),
            ActionParameter("alpha", "float", "Alpha", "Transparency", default=1.0),
            ActionParameter("speed_min", "float", "Min Speed", "Minimum speed", default=0),
            ActionParameter("speed_max", "float", "Max Speed", "Maximum speed", default=0),
            ActionParameter("direction_min", "float", "Min Direction", "Min angle", default=0),
            ActionParameter("direction_max", "float", "Max Direction", "Max angle", default=360),
            ActionParameter("life_min", "int", "Min Life", "Min lifetime (steps)", default=100),
            ActionParameter("life_max", "int", "Max Life", "Max lifetime (steps)", default=100)
        ],
        implemented=False
    ),
    "create_emitter": ActionDefinition(
        name="create_emitter",
        display_name="Create Particle Emitter",
        category="particles",
        tab="particles",
        description="Create particle emitter",
        icon="🌀",
        parameters=[
            ActionParameter("x", "int", "X", "X position", default=0),
            ActionParameter("y", "int", "Y", "Y position", default=0),
            ActionParameter("width", "int", "Width", "Emitter width", default=0),
            ActionParameter("height", "int", "Height", "Emitter height", default=0),
            ActionParameter("shape", "choice", "Shape", "Emitter shape",
                          default="rectangle", options=["rectangle", "ellipse", "diamond", "line"])
        ],
        implemented=False
    ),
    "destroy_emitter": ActionDefinition(
        name="destroy_emitter",
        display_name="Destroy Particle Emitter",
        category="particles",
        tab="particles",
        description="Remove particle emitter",
        icon="💥",
        implemented=False
    ),
    "burst_particles": ActionDefinition(
        name="burst_particles",
        display_name="Burst Particles",
        category="particles",
        tab="particles",
        description="Emit particles once",
        icon="💥",
        parameters=[
            ActionParameter("particle_type", "int", "Particle Type", "Type to emit", default=0),
            ActionParameter("number", "int", "Number", "Number of particles", default=10)
        ],
        implemented=False
    ),
    "stream_particles": ActionDefinition(
        name="stream_particles",
        display_name="Stream Particles",
        category="particles",
        tab="particles",
        description="Emit particles continuously",
        icon="🌊",
        parameters=[
            ActionParameter("particle_type", "int", "Particle Type", "Type to emit", default=0),
            ActionParameter("number", "int", "Number", "Particles per step", default=1)
        ],
        implemented=False
    ),
}

# ============================================================================
