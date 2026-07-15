"""HTML5 export — views/camera (large-level scrolling), Phase 1.

The exported engine gained a GameMaker-style 8-view camera mirroring the
desktop runtime (game_runner.py): per-frame follow+clamp (updateViews) and
a per-view clip+translate render. Source-level assertions here; the
behavioural proof (follow math + render offset in real Chromium) is the
Playwright harness run during development (Playwright isn't a CI dep).
"""
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_view_state_initialized_on_room():
    assert "this.viewsEnabled" in ENGINE
    # 8 views built from data.views with the runtime's default schema
    assert "for (let i = 0; i < 8; i++)" in ENGINE
    for field in ("view_x", "view_w", "port_x", "port_w",
                  "follow", "hborder", "vborder", "hspeed", "vspeed"):
        assert field in ENGINE, field


def test_update_views_follow_and_clamp():
    m = re.search(r"updateViews\(\)\s*\{(.*?)\n    \}", ENGINE, re.S)
    assert m, "updateViews not found"
    body = m.group(1)
    assert "view.follow" in body and "findFirstInstance" in body
    assert "hborder" in body and "hspeed" in body          # border + speed limit
    assert "this.width - vw" in body                       # room clamp
    # it runs each frame before render
    assert "this.currentRoom.updateViews()" in ENGINE


def test_render_applies_per_view_clip_and_translate():
    m = re.search(r"    render\(ctx\)\s*\{(.*?)\n    \}\n\n    // Room contents",
                  ENGINE, re.S)
    assert m, "GameRoom.render not found in expected shape"
    body = m.group(1)
    assert "_activeViews()" in body
    assert "ctx.clip()" in body
    # offset = port - view (mirrors the desktop per-view render loop)
    assert "view.port_x - view.view_x" in body and "view.port_y - view.view_y" in body
    # legacy no-view path still renders at origin
    assert "_renderContents(ctx)" in body


def test_view_actions_dispatched():
    assert "case 'enable_views'" in ENGINE
    assert "case 'set_view'" in ENGINE
    # set_view only touches provided fields
    assert "game.currentRoom.views[vi]" in ENGINE


def test_views_project_exports_and_boots_shape():
    """A minimal views_enabled project exports to a valid HTML file whose
    embedded data carries the view config (round-trips through the blob)."""
    import base64
    import gzip
    import json
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="views_exp_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "v", "settings": {"window_width": 800, "window_height": 600},
        "assets": {"sprites": {}, "sounds": {}, "backgrounds": {}, "objects": {},
                   "rooms": {"rm": {"name": "rm", "width": 2400, "height": 800,
                                    "views_enabled": True,
                                    "views": {"view_0": {"visible": True, "view_w": 800,
                                                         "view_h": 600, "follow": "p"}},
                                    "instances": []}}},
        "room_order": ["rm"],
    }
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = proj.parent / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out)
    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    embedded = json.loads(gzip.decompress(base64.b64decode(m.group(1))))
    assert embedded["assets"]["rooms"]["rm"]["views_enabled"] is True
