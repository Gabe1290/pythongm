"""HTML5 export structural coverage for Block World's mine-to-collect
block rewards (set_block_reward) -- see tests/test_block_world_reward.py's
docstring for the full design rationale (the auto-step movement model
means a lone decorative block is never something you bump into or aim
Break Block at; embedding a rewarded block in a wall face and mining it
now pays out score automatically, matching what a GameMaker-taught student
expects from a visible ore/gem block).

No JS engine/Playwright in CI (same standing limitation as every other
HTML5 block-world/raycast test) -- source-level structural assertions,
matching test_html5_block_world_jump_inventory.py's tier for this same
extension. Real behavioural proof (a Playwright-driven headless-Chromium
run against a real export) was done ad hoc during development, not
committed here.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

BW_JS = (REPO_ROOT / "extensions" / "block_world" / "export_html5.js").read_text(encoding="utf-8")


def test_set_block_reward_registered():
    assert "registerExtensionAction('set_block_reward'" in BW_JS


def test_set_block_reward_writes_to_camera_config():
    m = re.search(r"registerExtensionAction\('set_block_reward'(.*?)\n\}\);", BW_JS, re.S)
    assert m, "set_block_reward not found"
    body = m.group(1)
    assert "cfg.rewards" in body
    assert "BLOCK_FACE_COLORS.hasOwnProperty(blockType)" in body


def test_break_block_pays_out_registered_rewards():
    m = re.search(r"registerExtensionAction\('break_block'(.*?)\n\}\);", BW_JS, re.S)
    assert m, "break_block not found"
    body = m.group(1)
    assert "cfg.rewards" in body
    assert "game.score += points" in body
    # After removal, not before -- a refused/no-op break must not pay out.
    remove_idx = body.index("bwRemoveBlock(")
    reward_idx = body.index("game.score += points")
    assert remove_idx < reward_idx


def test_reward_lookup_uses_the_broken_block_type():
    m = re.search(r"registerExtensionAction\('break_block'(.*?)\n\}\);", BW_JS, re.S)
    body = m.group(1)
    assert "const rewards = (cfg && cfg.rewards) || {};" in body
    assert "const points = rewards[bt];" in body


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
