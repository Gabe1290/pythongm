"""HTML5 export — move_to_contact's `direction` parameter used a bare
parseFloat, which cannot parse GameMaker's own "current direction of
travel" keyword convention (`direction: "direction"`, a common authored
pattern — the promo game's platform-level player used exactly this in its
collision_with_pf_obj_brique handler). parseFloat("direction") is NaN, and
the old `|| 0` fallback silently meant "always push right" (0 degrees),
regardless of which way the instance actually approached whatever it
collided with.

Fix: move_to_contact now resolves both direction and max_distance through
parseNumParam, which gained a new capability for this: a bare instance
attribute name (e.g. "direction", "speed") now resolves via a direct
property lookup, matching desktop's _parse_value
(hasattr(instance, value_str) -> getattr(...)) — checked before the
existing self.x/other.x/facing_angle/irandom() substitution-and-whitelist
expression path, same precedence order desktop uses.

Bare "direction" resolving is necessary but not sufficient by itself:
tests/test_html5_platform_collision_regression.py covers the deeper bug
this exposed in the platform level's own collision handler (removing
move_to_contact from it entirely, since a fully correct direction value
STILL pushes further into whatever was just blocked, which is right for
landing on a platform's top but wrong for a side wall).

Verification tier, per this repo's "no Node in CI" convention: source-
level assertions on engine.js.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_parse_num_param_resolves_bare_instance_attribute():
    m = re.search(r"function parseNumParam\([^)]*\)\s*\{(.*?)\n\}", ENGINE, re.S)
    assert m
    body = m.group(1)
    assert "typeof inst[s] === 'number'" in body
    assert "return inst[s];" in body


def test_move_to_contact_no_longer_uses_bare_parsefloat():
    m = re.search(r"case 'move_to_contact':\s*\{(.*?)\n            \}", ENGINE, re.S)
    assert m, "move_to_contact not found"
    body = m.group(1)
    assert "parseFloat(params.direction)" not in body
    assert "parseNumParam(params.direction, this, 0)" in body
    assert "parseNumParam(params.max_distance" in body


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
