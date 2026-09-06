"""The three Block World renderers must agree on how many columns to cast.

`columns` is the picture-quality/speed dial, and neither bundled sample sets
it, so all three targets fall back to their own hardcoded default. Those
defaults are three separate literals in three hand-written renderers (desktop
Python, `export_html5.js`, `export_kivy.py`) -- exactly the shape of divergence
this repo keeps finding, where an exported game quietly renders at a different
resolution than the one the author tested with Test Game.

Nothing at runtime couples them, so this does.
"""
import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

EXT = REPO_ROOT / "extensions" / "block_world"

from extensions.block_world.state import DEFAULT_COLUMNS  # noqa: E402


def test_the_default_is_the_one_that_was_measured():
    """Not a round number picked by feel: 160 gives 4px strips on the standard
    640px window, nearly doubles the frame rate on open terrain, and is what
    TODO.md records the before/after numbers for."""
    assert DEFAULT_COLUMNS == 160


def test_desktop_reads_the_shared_constant_rather_than_a_literal():
    src = (EXT / "renderer.py").read_text(encoding="utf-8")
    assert "min(w, DEFAULT_COLUMNS)" in src
    # The action schema and the handler must not re-state the number either.
    for name in ("actions.py", "handlers.py"):
        text = (EXT / name).read_text(encoding="utf-8")
        assert "DEFAULT_COLUMNS" in text, "%s hardcodes its own default" % name


def test_the_action_parameter_offers_the_same_default():
    """What the IDE writes into a new project must match what an omitted
    parameter falls back to, or a project renders differently depending on
    whether the author touched the field."""
    from events.action_types import ActionParameter  # noqa: F401
    from extensions.block_world.actions import PLUGIN_ACTIONS

    action = PLUGIN_ACTIONS["enable_block_world_view"]
    columns = next(p for p in action.parameters if p.name == "columns")
    assert columns.default_value == DEFAULT_COLUMNS


def _js_number_after(src, pattern):
    match = re.search(pattern, src)
    assert match, "pattern not found in export_html5.js: %s" % pattern
    return int(match.group(1))


def test_html5_export_uses_the_same_default():
    src = (EXT / "export_html5.js").read_text(encoding="utf-8")
    assert _js_number_after(
        src, r"const numColumns = cfg\.columns \|\| Math\.min\(w, (\d+)\)"
    ) == DEFAULT_COLUMNS
    assert _js_number_after(
        src, r"columns: Math\.trunc\(num\('columns', (\d+)\)\)"
    ) == DEFAULT_COLUMNS


def test_kivy_export_uses_the_same_default():
    """Parsed out of the generated-code strings the exporter emits, so a
    literal that only appears in a comment cannot satisfy it."""
    src = (EXT / "export_kivy.py").read_text(encoding="utf-8")
    numbers = [int(n) for n in re.findall(
        r"int\(min\(W, (\d+)\)\)|_tofloat\(params\.get\('columns'\), (\d+)\)",
        src) for n in n if n]
    assert numbers, "no Kivy columns default found"
    assert set(numbers) == {DEFAULT_COLUMNS}, (
        "Kivy defaults %s disagree with %d" % (sorted(set(numbers)),
                                               DEFAULT_COLUMNS))


def test_no_stray_320_columns_default_survives_anywhere():
    """The previous value, in case a fourth copy exists that the sweep missed."""
    offenders = []
    for path in EXT.rglob("*"):
        if path.suffix not in (".py", ".js") or not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if "320" in line and "column" in line.lower() and not line.lstrip().startswith(("#", "//", "*")):
                offenders.append("%s: %s" % (path.name, line.strip()))
    assert not offenders, "a columns default of 320 survives:\n" + "\n".join(offenders)


def test_the_python_sources_still_parse():
    for name in ("renderer.py", "actions.py", "handlers.py", "state.py",
                 "export_kivy.py"):
        ast.parse((EXT / name).read_text(encoding="utf-8"))
