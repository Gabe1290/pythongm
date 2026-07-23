"""HTML5 extension mechanism — Stage C, unit C1a (docs/RAYCAST_EXTENSION_PLAN.md).

engine.js gains a generic extension seam mirroring the desktop
runtime/extension_hooks + plugin action registry: an extension ships an
export_html5.js that the exporter concatenates at a marker, and that code
registers room renderers and/or action handlers. This unit proves the seam is
present and wired BEFORE the raycast JS is moved onto it (C1b/C1c), exactly as
Stage B1 proved the desktop hook before B2/B3.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(
    encoding="utf-8")


# --- The seam exists and is wired in engine.js -----------------------------

def test_engine_defines_the_registries():
    assert "function registerRoomRenderer(fn)" in ENGINE
    assert "function renderExtensionRoom(room, ctx)" in ENGINE
    assert "function registerExtensionAction(name, fn)" in ENGINE
    assert "const _extRoomRenderers = []" in ENGINE
    assert "const _extActions = {}" in ENGINE


def test_render_gives_extensions_first_refusal():
    """GameRoom.render calls the hook first; a claim runs the HUD/draw pass
    and returns (mirrors the desktop _render_room seam)."""
    render = ENGINE[ENGINE.index("    render(ctx) {"):]
    render = render[:render.index("// Fill the whole canvas")]
    assert "if (renderExtensionRoom(this, ctx)) {" in render
    assert "runDrawEvent(ctx)" in render
    assert "return;" in render


def test_unknown_action_falls_through_to_the_extension_registry():
    """executeAction's default consults _extActions before warning."""
    default = ENGINE[ENGINE.index("            default:\n                if (_extActions"):]
    assert "_extActions[actionType](this, params, game)" in default[:400]


def test_injection_marker_is_present_before_the_bootstrap():
    assert "// __PYGM_EXTENSION_JS__" in ENGINE
    assert ENGINE.index("// __PYGM_EXTENSION_JS__") < ENGINE.index(
        "window.addEventListener('load'"), "marker must precede the bootstrap"


# --- The exporter concatenates enabled extensions' export_html5.js ---------

def _write_fixture_extension(tmp_path, folder, js):
    d = tmp_path / folder
    d.mkdir()
    (d / "export_html5.js").write_text(js, encoding="utf-8")
    return d


def test_exporter_injects_enabled_extension_js(tmp_path, monkeypatch):
    import events.plugin_loader as pl
    from export.HTML5.html5_exporter import HTML5Exporter

    _write_fixture_extension(tmp_path, "demo_ext",
                             "registerExtensionAction('demo_noop', function(){});")
    monkeypatch.setattr(pl, "get_extension_directory", lambda: tmp_path)
    monkeypatch.setattr(pl, "list_available_extensions",
                        lambda: [{"folder": "demo_ext", "enabled": True}])

    ex = HTML5Exporter()
    assert "registerExtensionAction('demo_noop'" in ex.engine_code
    assert "// --- extension: demo_ext ---" in ex.engine_code
    # The marker itself is consumed by the substitution.
    assert HTML5Exporter.EXTENSION_JS_MARKER not in ex.engine_code


def test_disabled_extension_contributes_nothing(tmp_path, monkeypatch):
    import events.plugin_loader as pl
    from export.HTML5.html5_exporter import HTML5Exporter

    _write_fixture_extension(tmp_path, "off_ext", "OFF_MARKER;")
    monkeypatch.setattr(pl, "get_extension_directory", lambda: tmp_path)
    monkeypatch.setattr(pl, "list_available_extensions",
                        lambda: [{"folder": "off_ext", "enabled": False}])

    ex = HTML5Exporter()
    assert "OFF_MARKER" not in ex.engine_code


def test_no_extension_js_leaves_the_engine_valid(tmp_path, monkeypatch):
    """With nothing to inject, the marker is simply removed — engine.js stands
    on its own (raycast still ships from engine.js until C1b)."""
    import events.plugin_loader as pl
    from export.HTML5.html5_exporter import HTML5Exporter

    monkeypatch.setattr(pl, "get_extension_directory", lambda: tmp_path)
    monkeypatch.setattr(pl, "list_available_extensions", lambda: [])

    ex = HTML5Exporter()
    assert HTML5Exporter.EXTENSION_JS_MARKER not in ex.engine_code
    assert "class GameRoom {" in ex.engine_code
