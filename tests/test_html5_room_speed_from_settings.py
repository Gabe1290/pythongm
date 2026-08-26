"""HTML5's GameRoom.roomSpeed (which scales hspeed/vspeed's per-frame
position delta to reproduce desktop's real-world speed on an uncapped,
requestAnimationFrame-driven loop — see the constructor's own comment)
was hardcoded to 60 regardless of what the project actually configured.

Desktop reads settings.room_speed ONCE, globally, into GameRunner.fps —
the pygame clock's real tick rate, so hspeed/vspeed apply at exactly that
many real steps per second. Any project whose room_speed isn't 60 played
at the wrong real-world speed on HTML5 only: the promo game's
room_speed: 30 made HTML5 run exactly 2x desktop's real speed (reported
as "HTML5 speed is now ok, the desktop IDE is too slow" right after the
HTML5-side hspeed had been tuned to feel right at HTML5's — wrongly
double-fast — pace).

Fix: buildRoom now reads gameData.settings.room_speed (falling back to
60 when absent/invalid, matching GameRunner's own default) into the new
room's roomSpeed at construction time. set_room_speed can still change it
at runtime same as before; this only fixes the STARTING value.
"""
import base64
import gzip
import json
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENGINE = (REPO_ROOT / "export" / "HTML5" / "templates" / "engine.js").read_text(encoding="utf-8")


def test_build_room_reads_configured_room_speed():
    m = re.search(r"buildRoom\(roomName\) \{(.*?)\n        const instancesData", ENGINE, re.S)
    assert m, "buildRoom not found"
    body = m.group(1)
    assert "this.gameData.settings && this.gameData.settings.room_speed" in body
    assert "room.roomSpeed = " in body
    assert ": 60" in body  # the fallback


def _export_with_room_speed(room_speed):
    from export.HTML5.html5_exporter import HTML5Exporter

    proj = Path(tempfile.mkdtemp(prefix="html5_room_speed_")) / "proj"
    (proj / "rooms").mkdir(parents=True)
    data = {
        "name": "room_speed_html5",
        "settings": {"window_width": 200, "window_height": 200, "room_speed": room_speed},
        "assets": {
            "sprites": {}, "sounds": {}, "backgrounds": {}, "objects": {},
            "rooms": {
                "rm_a": {"name": "rm_a", "width": 200, "height": 200, "instances": []},
            },
        },
        "room_order": ["rm_a"],
    }
    (proj / "project.json").write_text(json.dumps(data), encoding="utf-8")
    out = proj.parent / "out"
    out.mkdir()
    assert HTML5Exporter().export(proj, out)

    html = next(out.glob("*.html")).read_text(encoding="utf-8")
    m = re.search(r'const gameData = decompressData\("([A-Za-z0-9+/=]+)"\)', html)
    assert m
    embedded = json.loads(gzip.decompress(base64.b64decode(m.group(1))))
    assert embedded["settings"]["room_speed"] == room_speed


def test_room_speed_30_survives_export_round_trip():
    """The promo game's actual setting — proves the exported gameData
    still carries it for buildRoom to read (the fix's own reading of it
    is covered by source-level assertions above; no JS engine here)."""
    _export_with_room_speed(30)


def test_room_speed_60_also_survives_export_round_trip():
    _export_with_room_speed(60)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
