#!/usr/bin/env python3
"""BlockWorldEditSession -- the room + fly-camera pair the editor widget
drives, and the same picking/rendering functions extensions/block_world
already exposes to the running game.

Mirrors tools/preview_block_world.py's make_room()/place() shape (a real
GameRoom plus a minimal GameInstance-shaped camera planted in
room.instances) -- that is the proven, already-working technique for
getting extensions.block_world.renderer.render_block_world_view and its
picking helpers (pick_voxel/screen_ray/etc.) to operate outside a real
running game, so this wraps an EXISTING room instead of reinventing that
plumbing. The plan doc's original idea of a camera with "no GameInstance
at all" turned out to not fit render_block_world_view's actual calling
convention (it looks the camera up via room._find_first_instance by
object_name) -- this follows what the renderer really needs, verified
against its source, not the plan's initial guess.
"""
from runtime.game_runner import GameInstance, GameRoom
from extensions.block_world.state import block_world_state

# Deliberately unrepresentable as an authored object name (leading/trailing
# dunders around spaces aren't valid identifiers), so this can never collide
# with a real object in the project being edited.
EDITOR_CAMERA_OBJECT_NAME = "__block_world_editor_camera__"

DEFAULT_CELL_SIZE = 32
DEFAULT_RENDER_DISTANCE = 24
DEFAULT_FOV = 66


class BlockWorldEditSession:
    """Owns the GameRoom being edited and a fly-camera instance planted in
    it. The camera is editor-only state -- it is never written back to the
    room's saved data (to_block_list only serializes blocks, not
    instances), and it moves with no gravity/collision at all: this is a
    build-mode camera, not a gameplay one, matching
    tools/preview_block_world.py's own "press C to fly through walls"
    debug-camera precedent.
    """

    def __init__(self, room: GameRoom, cell_size: int = DEFAULT_CELL_SIZE,
                 render_distance: int = DEFAULT_RENDER_DISTANCE):
        self.room = room
        self.cell_size = cell_size

        self.camera = GameInstance(EDITOR_CAMERA_OBJECT_NAME, 0, 0, {},
                                    action_executor=None)
        self.camera._cached_object_data = {"solid": False}
        self.camera._cached_width = cell_size
        self.camera._cached_height = cell_size
        self.camera.facing_angle = 0.0
        room.instances.append(self.camera)

        cfg = block_world_state(room)["camera"]
        cfg.update({
            "enabled": True,
            "camera_object": EDITOR_CAMERA_OBJECT_NAME,
            "cell_size": cell_size,
            "z_layer": 0,
            "fov": DEFAULT_FOV,
            "render_distance": render_distance,
            "wall_textured": True,
            "pitch": 0.0,
        })

    @property
    def camera_config(self) -> dict:
        return block_world_state(self.room)["camera"]

    def place(self, cell_x: float, cell_y: float, facing_deg: float = 0.0,
              z_layer: int = 0) -> None:
        """Put the camera at the given cell (in cell units, not pixels),
        matching preview_block_world.place()'s exact convention."""
        self.camera.x = cell_x * self.cell_size
        self.camera.y = cell_y * self.cell_size
        self.camera.facing_angle = facing_deg
        self.camera_config["z_layer"] = int(z_layer)

    def close(self) -> None:
        """Remove the editor's fly-camera from the room. Call this before
        handing the room off to anything that isn't this editor (e.g. a
        save path that serializes room.instances), since the camera must
        never leak into saved data."""
        if self.camera in self.room.instances:
            self.room.instances.remove(self.camera)


def make_empty_room(name: str = "block_world_edit", width_cells: int = 32,
                     height_cells: int = 32,
                     cell_size: int = DEFAULT_CELL_SIZE) -> GameRoom:
    """A bare GameRoom with no blocks, for standalone/demo/test use before
    real room-loading (Phase 3) wires this editor to an actual project."""
    return GameRoom(name, {"width": width_cells * cell_size,
                            "height": height_cells * cell_size},
                     action_executor=None)
