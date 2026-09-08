"""L19, docs/FULL_AUDIT_2026-09-07.md: console print in runtime paths
bypasses the cp1252-safe logger.

runtime/game_runner.py has two bare print() calls (PYGM_FRAMES_COMPLETED,
PYGM_NET_STATUS) that are deliberately NOT routed through
core.logger.ConsoleSafeHandler (M7's fix for the same class of bug in
plugins/audio_actions.py): external tooling
(tools/verify_desktop_export.py, tools/smoke_run_multiplayer.py) greps
stdout for their exact literal text, and ConsoleSafeHandler's format()
sanitization could change the line being matched against. Both are
ASCII-only today, so the crash M7 fixed elsewhere (emoji/accented text
hitting a cp1252 Windows console's encode step) can't happen here yet --
but nothing enforced that staying true. A future edit adding a French
label or an emoji to either literal would hit the identical crash.

Rather than routing through the logger (which would risk changing the
exact grepped text), this pins the literal content to pure ASCII
statically, so a future regression breaks THIS test instead of a
player's console.
"""
import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GAME_RUNNER = REPO_ROOT / "runtime" / "game_runner.py"


def _print_call_string_literals():
    """Every plain string literal that's an argument (positional or
    embedded via % formatting) to a bare print(...) call in
    game_runner.py."""
    tree = ast.parse(GAME_RUNNER.read_text(encoding="utf-8"))
    literals = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "print"):
            for arg in node.args:
                for sub in ast.walk(arg):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        literals.append(sub.value)
    return literals


def test_the_ast_walk_actually_finds_the_two_known_markers():
    """Sanity check on the test itself: if this fails, the ASCII check
    below is silently checking nothing."""
    literals = _print_call_string_literals()
    joined = " ".join(literals)
    assert "PYGM_FRAMES_COMPLETED" in joined
    assert "PYGM_NET_STATUS" in joined


def test_every_print_call_in_game_runner_is_pure_ascii():
    literals = _print_call_string_literals()
    assert literals
    for text in literals:
        assert text.isascii(), (
            f"non-ASCII text in a bare print() call in game_runner.py: {text!r} "
            "-- this bypasses ConsoleSafeHandler by design (grepped by "
            "external tooling), so it will crash on a cp1252 Windows console "
            "exactly like the M7 bug this pin exists to prevent"
        )
