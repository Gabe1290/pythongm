#!/usr/bin/env python3
"""Runtime handlers for the Block World extension's actions (Phase 2a).

Mirrors extensions/raycast_2_5d/handlers.py: a plugin's handlers run as
methods of a PluginExecutor instance, reaching the engine through
instance.action_executor (the plugins/audio_actions pattern), not through
ActionExecutor directly.
"""

import json
import math
from pathlib import Path

from .state import (BLOCK_TYPES, DEFAULT_HOTBAR, block_world_state, can_enter,
                    cell_of, get_block, ground_layer, is_breakable,
                    load_block_list, load_world_state, peek_camera,
                    remove_block, set_block)


def _truthy(raw):
    """Coerce an action parameter to a bool. Strings matter: project JSON
    stores "false", which is truthy under a bare bool()."""
    if isinstance(raw, str):
        return raw.strip().lower() in ("true", "1", "yes")
    return bool(raw)


# Jump mechanic (Tier 7a, docs/DEFERRED_GAPS_2026_PLAN.md). Tuning defaults
# in cells/step (cells/step^2 for gravity) -- a game-feel choice, freely
# overridden per project via enable_block_world_view's `gravity` param and
# jump's own `speed` param. DEFAULT_JUMP_SPEED^2 / (2*DEFAULT_GRAVITY) gives
# a peak height of ~1.5 cells (clears a one-block obstacle with headroom to
# spare) over ~8-9 steps to the top of the arc.
DEFAULT_GRAVITY = 0.04
DEFAULT_JUMP_SPEED = 0.35
# Falling never accelerates past this many cells/step. A discrete per-step
# simulation can tunnel through a thin floor if a single step's fall
# distance exceeds it -- every placed block is exactly one layer thick, so
# capping well under 1.0 keeps the ground <= check (in apply_gravity) able
# to always catch the crossing frame.
TERMINAL_FALL_SPEED = -0.9
# Tolerance for "close enough to the ground to count as grounded" -- guards
# against float drift from repeated +=/-= on z_layer/vz ever leaving jump
# permanently unusable by a hair's width.
JUMP_GROUND_EPS = 1e-6


class PluginExecutor:
    """Handles execution of the Block World actions."""

    @staticmethod
    def _executor(instance):
        return getattr(instance, "action_executor", None)

    def _pick(self, instance, parameters):
        """Resolve the camera and ask what its centre ray is pointing at.

        Returns ``(room, target, placement)`` or None when there is nothing
        to act on -- no room, no block-world view, or no camera instance.

        Every number here is read back from the SAME camera config the
        renderer projects from, and the angle uses the renderer's own
        ``radians(-facing_angle)`` conversion. Recomputing either
        independently is how picking drifts away from the crosshair.

        The ray follows the camera's look pitch (Phase 2c), not just its
        facing angle: the crosshair is fixed at screen centre, but a tilted
        view puts the horizon somewhere else on screen, so the ray through
        screen centre has real vertical slope whenever pitch != 0.
        ``screen_ray``/``pick_voxel`` are exactly what the mouse-aim preview
        tool already uses for this -- at pitch 0 they reduce to the same
        level walk ``pick_block`` does, so this is not a behaviour change for
        an unpitched view.
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return None
        room = ae.game_runner.current_room
        cfg = peek_camera(room)
        if not cfg or not cfg.get("enabled"):
            return None
        camera = room._find_first_instance(cfg.get("camera_object", ""))
        if camera is None:
            return None

        try:
            reach = int(float(ae._parse_value(parameters.get("reach", 5), instance)))
        except (TypeError, ValueError):
            reach = 5
        reach = max(1, reach)

        cell_size = int(cfg.get("cell_size", 32))
        cx, cy = room._sprite_top_left(camera)
        from .renderer import pick_voxel, screen_ray, horizon_for, eye_z_for  # lazy: pygame
        # The layer the EYE is in, not the layer the feet are on. With the
        # default two-block-tall body those differ, and a level crosshair
        # addresses whatever is at eye height -- picking the feet layer would
        # break blocks the crosshair is not on. eye_z_for is the one place
        # this is computed, so the render path can never disagree with it.
        eye_z = eye_z_for(cfg)

        gr = ae.game_runner
        screen_w = getattr(gr, "window_width", 0) or 0
        screen_h = getattr(gr, "window_height", 0) or 0
        if not screen_w or not screen_h:
            screen = getattr(gr, "screen", None)
            if screen is not None:
                screen_w, screen_h = screen.get_size()
        screen_w = screen_w or 640
        screen_h = screen_h or 480

        fov_rad = math.radians(cfg.get("fov", 66))
        pitch = float(cfg.get("pitch", 0.0))
        horizon = horizon_for(screen_h, pitch)
        angle_rad, z_per_px = screen_ray(
            screen_w / 2.0, screen_h / 2.0,
            math.radians(-camera.facing_angle), fov_rad, screen_w, screen_h,
            cell_size, horizon=horizon)

        target, placement = pick_voxel(
            room,
            cx + camera._cached_width / 2,
            cy + camera._cached_height / 2,
            eye_z, angle_rad, z_per_px, cell_size, reach)
        return room, target, placement

    def execute_set_look_pitch_action(self, instance, parameters):
        """Tilt the view up or down (Phase 2c).

        Clamped by the renderer, so holding a look control against the limit
        just stops rather than folding the view inside out.

        Parameters:
            pitch: degrees, positive up
            relative: add to the current angle instead of replacing it
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        cfg = peek_camera(ae.game_runner.current_room)
        if not cfg:
            return
        try:
            pitch = float(ae._parse_value(parameters.get("pitch", 0), instance))
        except (TypeError, ValueError):
            return
        if _truthy(parameters.get("relative", False)):
            pitch += float(cfg.get("pitch", 0.0))
        # Clamp at the setter, not just in the renderer: a held look control
        # accumulating past the limit would have to be wound all the way back
        # before the view responded again.
        from .renderer import clamp_pitch  # lazy: keeps pygame out of the IDE
        cfg["pitch"] = clamp_pitch(pitch)

    def execute_select_hotbar_slot_action(self, instance, parameters):
        """Choose the hotbar's selected block, for place_block to build with.

        Sets two plain instance attributes: `hotbar_index` (wrapped into
        range) and `hotbar_block` (the resolved block type id). Bind
        place_block's `block` parameter to the literal expression
        `"hotbar_block"` to use it -- place_block itself needs no change,
        since its `block` parameter already resolves a bare instance-
        variable-name expression (see ActionExecutor._parse_value).

        Works even outside an active block-world view: this only touches
        the calling instance, not room state, so a menu/inventory screen
        can set the starting slot before the 3D view is ever enabled.

        Parameters:
            index: hotbar slot index, wrapping around at either end
            relative: add to the current slot instead of jumping to it, for
                cycling with a "[ ]"-style control
        """
        ae = self._executor(instance)
        if ae is None:
            return
        try:
            index = int(float(ae._parse_value(parameters.get("index", 0), instance)))
        except (TypeError, ValueError):
            return
        if _truthy(parameters.get("relative", False)):
            index += int(getattr(instance, "hotbar_index", 0))
        index %= len(DEFAULT_HOTBAR)
        instance.hotbar_index = index
        instance.hotbar_block = DEFAULT_HOTBAR[index]

    def execute_move_and_collide_action(self, instance, parameters):
        """Move (dx, dy) this step, collision-checked against the block
        grid, with automatic footing: standing on the highest block at the
        mover's own (x, y), stepping up onto anything at most
        state.DEFAULT_MAX_STEP_UP higher. Movement is axis-separated (x then
        y checked independently) so sliding along a wall works, the same as
        every other collision-aware sample in this repo.

        If the calling instance IS the room's block-world camera, its
        footing after moving becomes the camera's z_layer -- climbing a
        step is exactly the layer underfoot going up by one, which raises
        the eye and re-projects the whole view. A non-camera instance still
        moves and collides correctly; it just has nowhere engine-level to
        store its own layer yet (a limitation worth lifting later, not one
        this action tries to work around).

        Vertical behaviour depends on whether gravity is configured
        (enable_block_world_view's `gravity` param, Tier 7a):
          - gravity <= 0 (default -- every project predating Tier 7a):
            UNCHANGED legacy behaviour. Footing snaps to ground instantly in
            both directions; there is no falling animation, a drop is just
            a step down.
          - gravity > 0: stepping UP still snaps instantly when grounded
            (can_enter already refused anything taller than
            state.DEFAULT_MAX_STEP_UP). Stepping onto lower/open ground, or
            already being airborne, is left alone here -- apply_gravity
            (bind it in the STEP event, which fires every frame regardless
            of movement input, unlike this action's usual keyboard-held
            binding) carries the camera down for real.

        Promoted from tools/preview_block_world.py's own movement code
        (which this extension's Phase 4 Unit 4 already promoted the
        ground_layer/can_enter/cell_of half of into state.py), with one
        deliberate improvement over the demo: this uses the instance's true
        sprite top-left (room._sprite_top_left), not its raw x/y, so a
        mover with a non-zero sprite origin collides correctly -- the demo
        camera never had one, so the shortcut never showed up there.

        Parameters:
            dx, dy: how far to move this step, in pixels
            collide: off ignores the block grid entirely (flying/debug),
                default True
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        room = ae.game_runner.current_room
        cfg = peek_camera(room)
        if not cfg or not cfg.get("enabled"):
            return

        try:
            dx = float(ae._parse_value(parameters.get("dx", 0), instance))
            dy = float(ae._parse_value(parameters.get("dy", 0), instance))
        except (TypeError, ValueError):
            return
        collide = _truthy(parameters.get("collide", True))
        cell_size = int(cfg.get("cell_size", 32))

        camera = room._find_first_instance(cfg.get("camera_object", ""))
        is_camera = camera is instance
        gravity_on = is_camera and float(cfg.get("gravity", 0.0)) > 0

        tl_x, tl_y = room._sprite_top_left(instance)
        ground = ground_layer(room, cell_of(tl_x, cell_size), cell_of(tl_y, cell_size))
        # can_enter's step-up gate compares against where the mover
        # actually IS. Grounded (legacy mode, or gravity mode at rest)
        # that's the ground below it; airborne in gravity mode it's the
        # camera's own tracked height instead -- the two differ once a
        # jump/fall is in progress, and a mid-air body should not suddenly
        # be allowed to "step up" onto a tall block just because the ground
        # far below it happens to be low.
        standing = float(cfg.get("z_layer", ground)) if gravity_on else ground

        nx = tl_x + dx
        if not collide or can_enter(room, cell_of(nx, cell_size), cell_of(tl_y, cell_size), standing):
            instance.x += dx
            tl_x = nx
        ny = tl_y + dy
        if not collide or can_enter(room, cell_of(tl_x, cell_size), cell_of(ny, cell_size), standing):
            instance.y += dy
            tl_y = ny

        if not is_camera:
            return

        ground = ground_layer(room, cell_of(tl_x, cell_size), cell_of(tl_y, cell_size))
        if not gravity_on:
            cfg["z_layer"] = float(ground)
            return
        if float(cfg.get("vz", 0.0)) == 0.0 and ground > standing:
            cfg["z_layer"] = float(ground)
        # Otherwise: airborne, or grounded with lower/equal footing ahead --
        # apply_gravity owns z_layer from here.

    def execute_apply_gravity_action(self, instance, parameters):
        """Continuous vertical physics for the block-world camera: gravity
        accelerates it downward each step, a positive vz (set by `jump`)
        carries it up first, and it lands cleanly -- vz zeroed, z_layer
        clamped to the exact block top -- once its height reaches the
        ground below it.

        Bind this in the object's STEP event, not a keyboard-held event:
        step fires every frame regardless of input, so falling continues
        even while no movement key is held -- move_and_collide (usually
        keyboard-bound, horizontal-only) and this action are deliberately
        independent for exactly that reason.

        A no-op unless enable_block_world_view's `gravity` parameter is set
        above 0 -- keeps every project that predates Tier 7a completely
        unaffected, and calling this without configuring gravity is itself
        a no-op rather than a confusing half-behaviour.
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        room = ae.game_runner.current_room
        cfg = peek_camera(room)
        if not cfg or not cfg.get("enabled"):
            return
        gravity = float(cfg.get("gravity", 0.0))
        if gravity <= 0:
            return
        camera = room._find_first_instance(cfg.get("camera_object", ""))
        if camera is not instance:
            return

        cell_size = int(cfg.get("cell_size", 32))
        tl_x, tl_y = room._sprite_top_left(instance)
        ground = ground_layer(room, cell_of(tl_x, cell_size), cell_of(tl_y, cell_size))

        z = float(cfg.get("z_layer", ground))
        vz = float(cfg.get("vz", 0.0)) - gravity
        vz = max(vz, TERMINAL_FALL_SPEED)
        z += vz
        if z <= ground:
            z = float(ground)
            vz = 0.0

        cfg["z_layer"] = z
        cfg["vz"] = vz

    def execute_jump_action(self, instance, parameters):
        """Give the block-world camera upward velocity -- only while it is
        grounded (not already mid-jump or falling), so holding/mashing the
        jump key cannot double-jump or fly.

        Needs gravity configured (enable_block_world_view's `gravity`
        parameter) and apply_gravity bound in the step event, or there is
        no physics to carry the camera back down; a no-op without both, the
        same guard apply_gravity itself uses.

        Parameters:
            speed: initial upward velocity, in cells/step
                (default handlers.DEFAULT_JUMP_SPEED)
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        room = ae.game_runner.current_room
        cfg = peek_camera(room)
        if not cfg or not cfg.get("enabled"):
            return
        if float(cfg.get("gravity", 0.0)) <= 0:
            return
        camera = room._find_first_instance(cfg.get("camera_object", ""))
        if camera is not instance:
            return

        cell_size = int(cfg.get("cell_size", 32))
        tl_x, tl_y = room._sprite_top_left(instance)
        ground = ground_layer(room, cell_of(tl_x, cell_size), cell_of(tl_y, cell_size))
        z = float(cfg.get("z_layer", ground))
        vz = float(cfg.get("vz", 0.0))
        if vz != 0.0 or z > ground + JUMP_GROUND_EPS:
            return  # already airborne -- no double/air jump

        try:
            speed = float(ae._parse_value(parameters.get("speed", DEFAULT_JUMP_SPEED), instance))
        except (TypeError, ValueError):
            speed = DEFAULT_JUMP_SPEED
        cfg["vz"] = speed

    def execute_place_block_action(self, instance, parameters):
        """Put a block in the empty cell the camera's centre ray reaches.

        A no-op when there is nowhere to put one -- the camera is flush
        against a block, or the target cell is already occupied. Silent
        rather than an error: holding the build key against a wall is
        ordinary play, not a mistake worth reporting.

        With Enable Block World View's Inventory parameter on (Tier 7c),
        also a no-op if the calling instance's inventory has none of the
        chosen block type left -- creative-mode unlimited placing (the
        default, Inventory off) is otherwise completely unchanged.

        Parameters:
            block: which block type to place (default "stone")
            reach: how many cells ahead you can build (default 5)
        """
        picked = self._pick(instance, parameters)
        if picked is None:
            return
        room, _target, placement = picked
        if placement is None:
            return

        ae = self._executor(instance)
        block = ae._parse_value(parameters.get("block", "stone"), instance)
        block = str(block) if block else "stone"
        if block not in BLOCK_TYPES:
            return

        cfg = peek_camera(room)
        if cfg and _truthy(cfg.get("inventory", False)):
            inventory = getattr(instance, "block_inventory", None) or {}
            if inventory.get(block, 0) <= 0:
                return
            inventory[block] -= 1
            instance.block_inventory = inventory

        # No "is this cell empty?" check: pick_voxel guarantees it. It only
        # ever returns a cell it has already read as air (see its docstring),
        # so a guard here would be unreachable code pretending to be a safety
        # net.
        set_block(room, *placement, block)

    def execute_break_block_action(self, instance, parameters):
        """Remove the block the camera's centre ray hits first.

        Block types marked unbreakable (see state.is_breakable) are left
        alone -- that check lives here and nowhere else, so an indestructible
        block is still aimed at, still occludes, and can still be built
        against. Swinging at one is a silent no-op, the same as swinging at
        thin air.

        With Enable Block World View's Inventory parameter on (Tier 7c),
        the broken block type is added to the calling instance's inventory
        (place_block then draws from it); off (the default), breaking has no
        inventory side effect at all, matching every project that predates
        Tier 7c.

        A block type registered via set_block_protection (Tier 7b) also
        needs its required key present in the calling instance's inventory
        -- checked after is_breakable (an absolutely unbreakable block stays
        that way regardless), before removal. Possessing the key only GATES
        the break; it is not itself consumed (a tool, not a one-time key).
        Requires Inventory to be on, or the check can never be satisfied --
        see set_block_protection's own docstring.

        Parameters:
            reach: how many cells ahead you can reach (default 5)
        """
        picked = self._pick(instance, parameters)
        if picked is None:
            return
        room, target, _placement = picked
        if target is None:
            return
        block_type = get_block(room, *target)
        if not is_breakable(block_type):
            return

        cfg = peek_camera(room)
        protection = cfg.get("protection", {}) if cfg else {}
        required_key = protection.get(block_type)
        if required_key:
            inventory = getattr(instance, "block_inventory", None) or {}
            if inventory.get(required_key, 0) <= 0:
                return

        remove_block(room, *target)

        if cfg and _truthy(cfg.get("inventory", False)):
            inventory = getattr(instance, "block_inventory", None) or {}
            inventory[block_type] = inventory.get(block_type, 0) + 1
            instance.block_inventory = inventory

        rewards = cfg.get("rewards", {}) if cfg else {}
        points = rewards.get(block_type)
        if points:
            ae = self._executor(instance)
            if ae is not None and ae.game_runner:
                ae.game_runner.score += int(points)
                ae.game_runner.show_score_in_caption = True

    def execute_set_block_reward_action(self, instance, parameters):
        """Award score when break_block successfully removes a chosen block
        type (mine-to-collect ore/gem) -- a scored counterpart to
        set_block_protection's tool/key gate, same call-once-per-type
        pattern, same camera-config storage.

        Runs AFTER remove_block succeeds (protection/is_breakable already
        passed), so a protected or unbreakable rewarded block only pays out
        once actually mined, not on a swing that silently no-ops.

        Parameters:
            block_type: which block type awards score when broken
            points: score awarded per block of this type broken
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        room = ae.game_runner.current_room
        cfg = peek_camera(room)
        if not cfg or not cfg.get("enabled"):
            return

        block_type = ae._parse_value(parameters.get("block_type", ""), instance)
        block_type = str(block_type) if block_type else ""
        if block_type not in BLOCK_TYPES:
            return
        try:
            points = float(ae._parse_value(parameters.get("points", 0), instance))
        except (TypeError, ValueError):
            return

        cfg.setdefault("rewards", {})[block_type] = points

    def execute_set_block_protection_action(self, instance, parameters):
        """Require a specific block type to be present in inventory before
        a protected block type can be broken (Tier 7b) -- a tool/key gate,
        layered on top of (not a replacement for) state.is_breakable's
        absolute unbreakable flag.

        Call once per protected type; each call adds/overwrites one entry
        rather than replacing the whole set, so authoring several
        protections is several calls (e.g. all in the room's create event,
        right after enable_block_world_view -- protection lives on the
        camera config the same way gravity/inventory do, so it resets
        whenever the view is re-enabled and needs re-registering then, same
        as those two).

        Needs Enable Block World View's Inventory parameter on. Without it,
        the calling instance never has a block_inventory to check against,
        so a registered protection makes that block type permanently
        unbreakable -- an honest, if probably unintended, consequence
        rather than a special-cased no-op.

        Parameters:
            block_type: which block type becomes protected
            required_key: which block type must be in inventory to break it
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        room = ae.game_runner.current_room
        cfg = peek_camera(room)
        if not cfg or not cfg.get("enabled"):
            return

        block_type = ae._parse_value(parameters.get("block_type", ""), instance)
        block_type = str(block_type) if block_type else ""
        required_key = ae._parse_value(parameters.get("required_key", ""), instance)
        required_key = str(required_key) if required_key else ""
        if block_type not in BLOCK_TYPES or required_key not in BLOCK_TYPES:
            return

        cfg.setdefault("protection", {})[block_type] = required_key

    def execute_enable_block_world_view_action(self, instance, parameters):
        """Switch the current room to a first-person voxel view (single
        layer, Phase 2a), or back to the normal top-down view. The renderer
        that actually draws it (renderer.py) claims the room through the
        extension_hooks seam once this sets the camera's 'enabled' flag.

        Parameters (all optional except enable):
            enable: True to switch to the block-world view (default True)
            camera_object: Object name whose x/y/facing_angle is the camera
                (default: the calling instance's own object)
            z_layer, fov, render_distance, cell_size, columns: projection settings
            wall_color / floor_color / ceiling_color: flat-shade colours
            wall_textured: off forces flat block colours
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return

        enable = _truthy(ae._parse_value(parameters.get("enable", True), instance))

        room = ae.game_runner.current_room
        if not enable:
            block_world_state(room)["camera"] = {"enabled": False}
            return

        camera_object = ae._parse_value(parameters.get("camera_object", ""), instance)
        camera_object = str(camera_object) if camera_object else instance.object_name

        def _num(key, default):
            try:
                return float(ae._parse_value(parameters.get(key, default), instance))
            except (TypeError, ValueError):
                return default

        def _bool(key, default):
            return _truthy(parameters.get(key, default))

        from .renderer import DEFAULT_EYE_HEIGHT, clamp_pitch  # lazy: pygame

        block_world_state(room)["camera"] = {
            "enabled": True,
            "camera_object": camera_object,
            # A float from Tier 7a on: gravity mode (see execute_apply_gravity_
            # action) needs sub-layer positions mid-jump/fall. Still an exact
            # whole number at rest, so nothing downstream that expects a clean
            # layer index changes when gravity is off (the default).
            "z_layer": _num("z_layer", 0),
            "fov": _num("fov", 66),
            "render_distance": int(_num("render_distance", 20)),
            "cell_size": int(_num("cell_size", 32)),
            "columns": int(_num("columns", 320)),
            "wall_color": str(parameters.get("wall_color", "#8a8a8a")),
            "floor_color": str(parameters.get("floor_color", "#3a2f1c")),
            "ceiling_color": str(parameters.get("ceiling_color", "#87CEEB")),
            "wall_textured": _bool("wall_textured", True),
            # Look angle in degrees, positive up (Phase 2c). Clamped here too
            # -- was the one pitch-writing site that wasn't, rescued only by
            # horizon_for's own defensive clamp at render time.
            "pitch": clamp_pitch(_num("pitch", 0)),
            # Horizontal (top/bottom) faces cast every Nth screen row and
            # upscale the result; 0 falls back to a flat average colour,
            # which is cheaper on a scene showing a lot of deck.
            "top_cast_res": int(_num("top_cast_res", 4)),
            # Camera height in cells (Phase 3's two-block-tall body by
            # default). Was previously read everywhere with this same
            # fallback but never actually written here, so no authored
            # action could ever change it -- see docs/VOXEL_WORLD_PLAN.md.
            "eye_height": _num("eye_height", DEFAULT_EYE_HEIGHT),
            # Tier 7a jump mechanic. 0 (default) = every project that
            # predates Tier 7a: move_and_collide's original instant-footing
            # behaviour, completely unchanged. >0 switches on real gravity/
            # falling -- see apply_gravity and jump.
            "gravity": _num("gravity", 0.0),
            "vz": 0.0,
            # Tier 7c inventory-with-counts. Off (default) = every project
            # that predates Tier 7c: place_block/break_block completely
            # unchanged, unlimited creative-mode placing. On = break_block
            # picks up what it breaks, place_block consumes from it.
            "inventory": _bool("inventory", False),
        }

        # Tier 7e Phase 2 procedural terrain. Off (default) = every project
        # that predates Tier 7e: the room's seed stays None, so
        # ensure_chunks_loaded/generate_chunk are permanent no-ops and
        # behaviour is completely unchanged. This is stored OUTSIDE the
        # "camera" dict above (which this action wholesale replaces every
        # call) so a room's generated terrain survives toggling the view
        # off and back on -- see state.py's _fresh() docstring.
        if _bool("generate", False):
            block_world_state(room)["seed"] = int(_num("seed", 0))
        else:
            block_world_state(room)["seed"] = None

    def execute_load_block_world_action(self, instance, parameters):
        """Load a pre-authored world into the current room from a JSON data
        file, replacing whatever blocks are there.

        Bind this in `game_start`, not `create` -- `create` re-fires on
        `restart_room` (see this repo's own landmine notes), and reloading
        the file back on top of live edits would silently discard whatever
        the player broke or placed since the room was entered.

        The file holds EITHER a flat JSON list in the `state.to_block_list`
        shape: `[{"x":, "y":, "z":, "type":}, ...]` -- the same shape a
        generator script (tools/gen_block_world_*.py) or `to_block_list`
        itself produces -- OR (Tier 7e Phase 2) a `{"seed": <int|null>,
        "blocks": [...]}` dict, the shape a generation-enabled room's own
        save (editors/block_world_editor/io.py) produces once it has a
        seed; `"blocks"` there is only the TOUCHED chunks (see
        to_touched_block_list), with everything else regenerating on
        demand from the seed. Format is detected from the parsed JSON's
        type (list vs. dict) -- a pre-Phase-2 file, which is always a bare
        list, is unaffected. Silently does nothing on a missing file,
        unreadable JSON, or an unknown block type -- consistent with this
        extension's other actions (a flush wall, an unbreakable swing)
        treating bad input as a no-op rather than crashing the game.

        Parameters:
            data_file: path to the JSON file, relative to the project
                folder (e.g. "blocks/room1.json")
        """
        ae = self._executor(instance)
        if ae is None or not ae.game_runner or not ae.game_runner.current_room:
            return
        room = ae.game_runner.current_room

        # Not run through _parse_value: a real path ("blocks/room1.json")
        # contains "/", which _parse_value's expression heuristic reads as
        # division and mangles -- the same reason wall_color/floor_color
        # above are read as plain strings, not expressions.
        data_file = str(parameters.get("data_file", ""))
        if not data_file:
            return

        project_path = getattr(ae.game_runner, "project_path", None)
        if not project_path:
            return

        try:
            with open(Path(project_path) / data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                load_world_state(room, data.get("seed"), data.get("blocks", []))
            else:
                load_block_list(room, data)
        except (OSError, ValueError, KeyError, TypeError):
            # Bad path, bad JSON, or an unknown block type in the file --
            # see the docstring above for why this is a silent no-op.
            pass

    def execute_draw_block_world_hud_action(self, instance, parameters):
        """Draw the Block World HUD: a centre crosshair plus a hotbar strip
        along the bottom, the selected slot highlighted.

        A MACRO action (see hud.py) -- emits ordinary rectangle/line/text
        draw-queue commands, so no target needs a new renderer, the same
        pattern raycast_2_5d's draw_minimap/draw_doom_hud use.

        Reads the selected slot from the CALLING instance's hotbar_index
        (see select_hotbar_slot, default 0 if never set) -- call this from
        the player/camera object's own Draw event, the same way a raycast
        game's HUD actions run on the camera.

        Also reads the calling instance's block_inventory (Tier 7c) if it
        has one -- only present once Enable Block World View's Inventory
        parameter is on and something has actually been broken/placed, so
        a creative-mode game (Inventory off, the default) never shows
        counts at all.
        """
        from .hud import build_block_world_hud_commands

        ae = self._executor(instance)
        if ae is None or not ae.game_runner:
            return
        if not hasattr(instance, "_draw_queue"):
            instance._draw_queue = []

        gr = ae.game_runner
        screen_w = getattr(gr, "window_width", 0) or 0
        screen_h = getattr(gr, "window_height", 0) or 0
        if not screen_w or not screen_h:
            screen = getattr(gr, "screen", None)
            if screen is not None:
                screen_w, screen_h = screen.get_size()
        screen_w = screen_w or 640
        screen_h = screen_h or 480

        def _num(key, default):
            try:
                return float(parameters.get(key, default))
            except (TypeError, ValueError):
                return float(default)

        cmds = build_block_world_hud_commands(
            screen_width=screen_w, screen_height=screen_h,
            hotbar=DEFAULT_HOTBAR,
            selected_index=int(getattr(instance, "hotbar_index", 0)),
            slot_size=_num("slot_size", 40), gap=_num("gap", 6),
            margin_bottom=_num("margin_bottom", 16),
            back_color=parameters.get("back_color", "#202020"),
            border_color=parameters.get("border_color", "#ffffff"),
            selected_color=parameters.get("selected_color", "#ffd040"),
            text_color=parameters.get("text_color", "#ffffff"),
            crosshair_size=_num("crosshair_size", 12),
            crosshair_color=parameters.get("crosshair_color", "#ffffff"),
            counts=getattr(instance, "block_inventory", None),
        )
        instance._draw_queue.extend(cmds)
