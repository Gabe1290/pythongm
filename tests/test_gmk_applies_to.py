"""GMK "Applies to" selector — parser + converter (treasure playtest finding #2).

The user's treasure playtest found the Explorer x pil collision destroying SELF
instead of OTHER (the pill). Root cause was two-layered:

- gmk_parser read the wrong int32 into GmkAction.applies_to: the field right
  after is_question is the "has an Applies-To selector" BOOL (destroy/change =
  1, play_sound = 0); the actual WHO value (-1 self / -2 other / >= 0 object
  index) sat later in the record and was read into a discarded local.
- gmk_converter never routed applies_to into parameters at all, so every
  imported action ran against self.

Now the parser assigns the real WHO field, and the converter emits
target="other" / target="object"+target_object=<name> for the actions whose
runtime handlers support per-target application (destroy_instance,
change_instance, destroy_at_position), and logs a WARNING for any other action
carrying a non-self target (visible behavior change instead of a silent one).

The canonical case pinned here is treasure's power-pill event:
    play_sound(bonus)                                   applies to self
    destroy_instance                                    applies to OTHER (the pill)
    change_instance(-> monster)                         applies to all SCARED
    change_instance(-> scared)                          applies to all MONSTER
    set_alarm(160, #0)                                  applies to SCARED (warned)
Before the fix the explorer destroyed itself on pickup and the monsters never
turned scared.
"""
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from conftest import skip_without_pygame

pytestmark = skip_without_pygame

from importers.gmk_parser import GmkParser  # noqa: E402
from importers.gmk_importer import import_gmk_detailed  # noqa: E402

TREASURE = REPO_ROOT / "samples" / "treasure.gmk"


def _explorer_pil_actions_raw():
    parsed = GmkParser().parse(str(TREASURE))
    objs = {o.name: o for o in parsed.objects if o is not None}
    explorer = objs["explorer"]
    names = [o.name if o else None for o in parsed.objects]
    for ev in explorer.events:
        if ev.event_type == 4 and names[ev.event_number] == "pil":
            return ev.actions, names
    raise AssertionError("explorer collision-with-pil event not found")


def test_parser_reads_the_real_applies_to_field():
    actions, names = _explorer_pil_actions_raw()
    by_fn = {a.function_name: a for a in actions}
    # play_sound has no Applies-To selector -> self
    assert by_fn["action_sound"].applies_to == -1
    # the pill pickup destroys OTHER (the pill), not self
    assert by_fn["action_kill_object"].applies_to == -2
    # the two change actions apply to object indices resolving to scared/monster
    changes = [a for a in actions if a.function_name == "action_change_object"]
    assert sorted(names[a.applies_to] for a in changes) == ["monster", "scared"]


@pytest.fixture(scope="module")
def treasure_import():
    out = Path(tempfile.mkdtemp(prefix="gmk_applies_to_")) / "import"
    import_gmk_detailed(str(TREASURE), str(out))
    return out


def test_pill_pickup_destroys_the_pill_not_the_player(treasure_import):
    exp = json.loads(
        (treasure_import / "objects" / "explorer.json").read_text(encoding="utf-8"))
    actions = exp["events"]["collision_with_pil"]["actions"]
    destroy = next(a for a in actions if a["action"] == "destroy_instance")
    assert destroy["parameters"].get("target") == "other"


def test_pill_pickup_scares_all_monsters(treasure_import):
    exp = json.loads(
        (treasure_import / "objects" / "explorer.json").read_text(encoding="utf-8"))
    actions = exp["events"]["collision_with_pil"]["actions"]
    changes = [a for a in actions if a["action"] == "change_instance"]
    got = {(a["parameters"].get("target"), a["parameters"].get("target_object"),
            a["parameters"].get("object")) for a in changes}
    # every already-scared monster resets to monster, every monster turns scared
    assert got == {("object", "scared", "monster"), ("object", "monster", "scared")}


def test_self_actions_emit_no_target(treasure_import):
    exp = json.loads(
        (treasure_import / "objects" / "explorer.json").read_text(encoding="utf-8"))
    actions = exp["events"]["collision_with_pil"]["actions"]
    sound = next(a for a in actions if a["action"] == "play_sound")
    assert "target" not in sound["parameters"]


def test_eaten_scared_monster_reverts_via_other(treasure_import):
    exp = json.loads(
        (treasure_import / "objects" / "explorer.json").read_text(encoding="utf-8"))
    actions = exp["events"]["collision_with_scared"]["actions"]
    change = next(a for a in actions if a["action"] == "change_instance")
    assert change["parameters"].get("target") == "other"
    assert change["parameters"].get("object") == "monster"


def test_unsupported_targets_warn_not_silent(caplog):
    """Actions the runtime can't retarget (set_alarm / jump_to_start / ...)
    must WARN when the .gmk gave them a non-self target, so the behavior
    change is visible to the importing user."""
    with caplog.at_level(logging.WARNING, logger="importers.gmk_converter"):
        out = Path(tempfile.mkdtemp(prefix="gmk_applies_warn_")) / "import"
        import_gmk_detailed(str(TREASURE), str(out))
    warnings = [r.getMessage() for r in caplog.records if "Applies to" in r.getMessage()]
    assert any("jump_to_start" in w for w in warnings)
    assert any("set_alarm" in w for w in warnings)
    # and none of them are for the actions we DO support
    assert not any("destroy_instance" in w or "change_instance" in w
                   for w in warnings)
