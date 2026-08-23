"""HTML5's checkCollisions() fired a collision_with_X handler EVERY frame
the two instances kept overlapping, not just once when the overlap
started -- unlike desktop's GameRunner.detect_collisions_for_instance,
which tracks _active_collisions/_collision_cooldowns so a handler fires
once per new collision (a documented GameMaker semantic).

This mattered for any handler that responds to contact by MOVING the
instance closer to the other object, most concretely move_to_contact:
its loop moves one step before checking whether it has reached contact,
so called on an instance that is ALREADY overlapping (which is exactly
its own resting state after the first landing), it immediately finds
"still touching" on the very first step and stops -- having moved 1px
further IN. Re-fired every frame forever (the old, ungated behavior),
that is an unbounded 1px/frame sink.

Found via the promo game's side-scroller: landing from a jump settled
the player about a pixel into the ground floor (ordinary "snap to
contact" overshoot, harmless on its own) -- and then, because
collision_with_ss_obj_ground kept re-firing every subsequent frame while
resting, move_to_contact kept walking 1px deeper each time, sinking the
player through the floor over roughly a second of play.

Fix: checkCollisions() now tracks the same (otherId, eventName) pair
state desktop does (_activeCollisions / _collisionCooldowns on
GameObject), firing a handler only when the pair transitions from not-
overlapping to overlapping, with the same 5-frame cooldown desktop uses.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_game_object_constructor_initializes_collision_tracking_state():
    m = re.search(r"class GameObject \{.*?constructor\(name, x, y, data, objectData\)\s*\{(.*?)\n    \}",
                  ENGINE, re.S)
    assert m, "GameObject constructor not found"
    body = m.group(1)
    assert "this._activeCollisions = new Set();" in body
    assert "this._collisionCooldowns = new Map();" in body


def test_check_collisions_gates_on_new_pair_only():
    m = re.search(r"checkCollisions\(game\) \{(.*?)\n    \}", ENGINE, re.S)
    assert m, "checkCollisions not found"
    body = m.group(1)
    assert "this._activeCollisions.has(pairKey)" in body
    assert "this._collisionCooldowns.has(pairKey)" in body
    assert "this._collisionCooldowns.set(pairKey, 5)" in body
    assert "this._activeCollisions = currentCollisions;" in body


# ---------------------------------------------------------------------------
# End-to-end: a real GameRoom.step() loop only fires the handler once while
# two instances keep overlapping, matching desktop's semantics.
# ---------------------------------------------------------------------------

def test_end_to_end_handler_fires_once_per_continuous_overlap():
    """Executes the real engine.js (class declarations and all) under Node's
    vm module, then drives GameObject.checkCollisions directly -- the same
    approach the repo's other engine.js behavioural tests use when Node is
    available, skipping cleanly when it isn't (see other engine.js tests'
    "no Node in CI" notes for the general convention this follows; CI here
    happens to have Node installed, so this runs for real there).

    The driver code below is concatenated onto engine.js's source and run
    as a SINGLE vm.runInContext call, rather than run separately and then
    read back via `sandbox.GameObject`: top-level `class`/`let`/`const`
    declarations in a vm-executed script are NOT reflected as properties
    on the contextified sandbox object (the same "let x; window.x is still
    undefined" behavior real browsers have) -- only `var`/function
    declarations are. Concatenating means the driver code shares the same
    top-level lexical scope engine.js's `class GameObject` was declared
    in, so it can reference `GameObject` directly.
    """
    import shutil
    if shutil.which("node") is None:
        import pytest
        pytest.skip("Node not available; source-level assertions above are the guard")

    import subprocess
    import tempfile

    driver = """
    const fireCount = { n: 0 };
    class Room {
      constructor() { this.instances = []; }
    }
    const player = new GameObject('p', 0, 0, {}, {});
    const wall = new GameObject('w', 0, 0, {}, {});
    wall.name = 'wall';
    player.name = 'player';
    player.events = { collision_with_wall: { actions: [] } };
    player.executeActions = (actions, game) => { fireCount.n++; };
    player.getBoundingBox = () => ({x: 0, y: 0, width: 10, height: 10});
    wall.getBoundingBox = () => ({x: 0, y: 0, width: 10, height: 10});
    wall.toDestroy = false;
    const room = new Room();
    room.instances = [player, wall];
    const game = { currentRoom: room };
    for (let i = 0; i < 10; i++) player.checkCollisions(game);
    console.log(JSON.stringify({fireCount: fireCount.n}));
    """

    script = """
    const vm = require('vm');
    const fs = require('fs');
    const src = fs.readFileSync(process.argv[2], 'utf8');
    const driver = fs.readFileSync(process.argv[3], 'utf8');
    const sandbox = { console, Math, Set, Map, window: { addEventListener: () => {} } };
    vm.createContext(sandbox);
    vm.runInContext(src + "\\n" + driver, sandbox);
    """
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
        f.write(script)
        script_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
        f.write(driver)
        driver_path = f.name
    result = subprocess.run(
        ["node", script_path, str(REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js"), driver_path],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stderr
    import json
    out = json.loads(result.stdout.strip().splitlines()[-1])
    assert out["fireCount"] == 1


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
