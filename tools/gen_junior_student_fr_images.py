#!/usr/bin/env python3
"""Generate the screenshots for the French Junior student handout
(docs/junior/images/).

Drives a real PyGameMakerIDE in the "junior" edition through a tiny scratch
project (one sprite+object that moves in 4 directions, a second sprite+
object for a bonus fruit-pickup mechanic, one room) and grabs seven
widgets: the whole IDE window on the Welcome tab (no project loaded yet),
the main toolbar, the Sprite Editor, the Object Editor's Blockly tab with
the 4-direction movement blocks, the Room Editor with just the hero placed,
the Object Editor's Blockly tab again with the bonus collision/score blocks
added, and the Room Editor again with fruit instances placed too.

Unlike every other headless-capture script in this repo (tools/
capture_tutorial_screenshots.py, tools/gen_tutorial_15/16_handout_images.py),
this one does NOT force QT_QPA_PLATFORM=offscreen: this dev box has a real
(if invisible, Wayland) display, and a real QWebEngineView -- which the
Object Editor's Blockly tab is -- has no proven working pattern for pixel
grabs under `offscreen` in this repo (confirmed by a throwaway spike before
writing this: a bare QWebEngineView.setHtml(...) grabbed under `offscreen`
saved a blank white PNG; the identical code on the real display, after
waiting for loadFinished plus a couple of processEvents/sleep cycles,
produced real rendered pixels). If this is ever run somewhere with no
display at all, set QT_QPA_PLATFORM=offscreen yourself and expect the
Blockly screenshots specifically to need re-verification.

Run: venv/bin/python3 tools/gen_junior_student_fr_images.py
"""
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "docs" / "junior" / "images"
WINDOW_SIZE = (1700, 1100)


def _make_app():
    from PySide6.QtWidgets import QApplication
    from utils.config import Config

    # Same privacy fix as tools/capture_tutorial_screenshots.py: must run
    # before the IDE window is constructed, or the Welcome tab's "recent
    # projects" panel can leak this machine's own project history.
    Config.set("recent_projects", [])
    Config.add_recent_project = staticmethod(lambda *a, **k: None)
    Config.set("edition", "junior")

    app = QApplication.instance() or QApplication([])

    # Install the real compiled French .qm translators into the app BEFORE
    # any widget is constructed, so self.tr() calls resolve for real (not
    # just Blockly's own JS layer, which reads the language config
    # directly and would otherwise be the only thing in French).
    from core.language_manager import get_language_manager
    lm = get_language_manager()
    # set_language() no-ops if it already thinks "fr" is current (this dev
    # box's real on-disk config already has language=fr from a previous
    # real IDE session) -- but that's manager-STATE tracking, not proof a
    # QTranslator is installed in THIS fresh QApplication. Force it.
    lm.current_language = None
    if not lm.set_language("fr"):
        raise RuntimeError("could not install the French translator")

    return app


def _make_ide(app):
    from core.ide_window import PyGameMakerIDE
    ide = PyGameMakerIDE()
    ide.resize(*WINDOW_SIZE)
    ide.show()
    app.processEvents()
    return ide


def _new_scratch_project(ide, name):
    scratch = Path(tempfile.mkdtemp(prefix="pygm_junior_fr_shots_"))
    ok = ide.project_manager.create_project(name, str(scratch), "empty", "")
    if not ok:
        raise RuntimeError(f"could not create scratch project {name!r} in {scratch}")
    project_path = ide.project_manager.current_project_path
    project_data = ide.project_manager.current_project_data
    ide.on_project_loaded(project_path, project_data)
    return scratch


def _sync(ide):
    ide.asset_manager.save_assets_to_project_data(ide.project_manager.current_project_data)
    ide.asset_tree.refresh_from_project(ide.project_manager.current_project_data)


def _sprite_png(path, size, color, shape="hero"):
    from PIL import Image, ImageDraw
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if shape == "hero":
        # A simple rounded "hero" blob -- a circle with two little ears --
        # reads as a character, not a GameMaker-tutorial placeholder
        # rectangle. Real pixel art isn't the point of the screenshot;
        # something a kid would recognise as "a character" is.
        draw.ellipse([4, 8, w - 4, h - 2], fill=color)
        draw.ellipse([2, 0, 14, 12], fill=color)
        draw.ellipse([w - 14, 0, w - 2, 12], fill=color)
    elif shape == "fruit":
        # A round fruit with a small stem -- reads as "something to pick
        # up", distinct from the hero's silhouette.
        draw.ellipse([2, 6, w - 2, h - 2], fill=color)
        draw.rectangle([w // 2 - 1, 0, w // 2 + 1, 7], fill=(90, 60, 20, 255))
    img.save(path)


def _capture_widget(widget, app, filename):
    app.processEvents()
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / filename
    pix = widget.grab()
    if not pix.save(str(dest)):
        raise RuntimeError(f"failed to save screenshot to {dest}")
    print(f"  wrote {dest.relative_to(ROOT)} ({pix.width()}x{pix.height()})")


def _close_editor(ide, key):
    """Tear down an open editor tab directly (bypassing close_editor_tab's
    unsaved-changes prompt, which would hang this headless script) so a
    later re-open gets a fresh editor/BlocklyWidget reflecting updated
    asset data -- open_object_editor/open_room_editor just refocus an
    already-open tab without reloading it."""
    editor = ide.open_editors.pop(key, None)
    if editor is None:
        return
    for i in range(ide.editor_tabs.count()):
        if ide.editor_tabs.widget(i) is editor:
            ide.editor_tabs.removeTab(i)
            break
    editor.deleteLater()


def _capture_object_blockly(ide, app, am, object_name, filename):
    """Open `object_name`'s editor, force the Blockly tab's lazy
    construction, wait for the real QWebEngineView page load and JS apply,
    and grab it. Closes any previously-open editor for this object first
    so a second call (after mutating its events) shows the NEW data --
    see _close_editor's docstring for why a plain re-open can't do this."""
    key = ide._editor_key("objects", object_name)
    _close_editor(ide, key)
    ide.open_object_editor(object_name, am.get_asset("objects", object_name))
    object_editor = ide.open_editors[key]
    app.processEvents()

    # Force the Blockly tab's lazy construction (in "junior" this already
    # happens via a QTimer.singleShot(0, ...) queued by __init__ itself,
    # since Blockly is the only tab left -- the explicit setCurrentIndex
    # below is a harmless no-op there and the real trigger elsewhere).
    object_editor.center_tabs.setCurrentIndex(object_editor._blockly_tab_index)
    for _ in range(20):
        app.processEvents()
        if getattr(object_editor, "blockly_tab", None) is not None:
            break
        time.sleep(0.05)
    else:
        raise RuntimeError(f"Blockly tab never initialised for {object_name}")

    from PySide6.QtCore import QEventLoop, QTimer
    blockly_widget = object_editor.blockly_tab.blockly_widget
    if not blockly_widget._page_ready:
        loop = QEventLoop()
        blockly_widget.web_view.loadFinished.connect(lambda ok: loop.quit())
        QTimer.singleShot(10000, loop.quit)
        loop.exec()
    for _ in range(8):
        app.processEvents()
        time.sleep(0.15)
    _capture_widget(object_editor, app, filename)


def _capture_room(ide, am, app, room_name, filename):
    """Same close-then-reopen reasoning as _capture_object_blockly, for the
    Room Editor's instance list / canvas."""
    key = ide._editor_key("rooms", room_name)
    _close_editor(ide, key)
    ide.open_room_editor(room_name, am.get_asset("rooms", room_name))
    room_editor = ide.open_editors[key]
    app.processEvents()
    _capture_widget(room_editor, app, filename)


def main():
    app = _make_app()
    ide = _make_ide(app)

    # -- Whole IDE, Welcome tab, no project loaded ---------------------
    # Captured before _new_scratch_project() runs, so it matches what a
    # student actually sees on first launch: "Aucun projet charge" / the
    # New Project / Open Project / sample-game buttons.
    _capture_widget(ide, app, "ide_welcome.png")

    scratch = _new_scratch_project(ide, "scratch_junior_fr")
    am = ide.asset_manager
    sprite_dir = scratch / "_capture_sprites"
    sprite_dir.mkdir(exist_ok=True)

    try:
        # -- Toolbar ---------------------------------------------------
        # grab() captures the toolbar's full laid-out width, which on this
        # box's wide virtual display is mostly empty space well past the
        # last real icon -- crop down to just the icon cluster + a little
        # padding so the handout image isn't a thin, hard-to-read strip.
        from PySide6.QtWidgets import QToolBar
        toolbar = ide.findChild(QToolBar, "MainToolbar")
        _capture_widget(toolbar, app, "toolbar.png")
        from PIL import Image
        toolbar_path = OUT / "toolbar.png"
        with Image.open(toolbar_path) as img:
            img.crop((0, 0, min(400, img.width), img.height)).save(toolbar_path)

        # -- Hero sprite ----------------------------------------------------
        png_path = sprite_dir / "spr_heros.png"
        _sprite_png(png_path, (48, 48), (240, 140, 60, 255), shape="hero")
        asset_data = am.import_asset(png_path, "sprites", "spr_heros")
        if asset_data is None:
            raise RuntimeError("failed to import sprite spr_heros")
        _sync(ide)
        ide.open_sprite_editor("spr_heros", am.get_asset("sprites", "spr_heros"))
        key = ide._editor_key("sprites", "spr_heros")
        sprite_editor = ide.open_editors[key]
        app.processEvents()
        _capture_widget(sprite_editor, app, "sprite_editor.png")

        # -- Hero object: 4-direction movement -------------------------
        # "no key held" nests under "keyboard" as subtype "nokey" (no
        # underscore) -- this is what Blockly's own generator actually
        # writes (blockly_generators.js: `event_keyboard_nokey ->
        # {event: 'keyboard', subtype: 'nokey'}`). A flat top-level
        # "keyboard_no_key" key (matching events/event_types.py's
        # EVENT_TYPES name) loads into the generic "Keyboard: held, key=
        # no_key" block instead of the dedicated "Keyboard: No key" block
        # -- confirmed by trying it first and getting exactly that, plus a
        # round-trip-safety warning. Worth a real bug report separately;
        # not this script's job to fix.
        hero_events = {
            "keyboard": {
                "left": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "-4"}},
                ]},
                "right": {"actions": [
                    {"action": "set_hspeed", "parameters": {"speed": "4"}},
                ]},
                "up": {"actions": [
                    {"action": "set_vspeed", "parameters": {"speed": "-4"}},
                ]},
                "down": {"actions": [
                    {"action": "set_vspeed", "parameters": {"speed": "4"}},
                ]},
                "nokey": {"actions": [
                    {"action": "stop_movement", "parameters": {}},
                ]},
            },
        }
        am.create_asset("obj_heros", "objects", sprite="spr_heros",
                        solid=False, visible=True, events=hero_events)
        _sync(ide)
        _capture_object_blockly(ide, app, am, "obj_heros", "objet_blockly.png")

        # -- Room: hero only ----------------------------------------------
        # A new project already has a default room ("room0",
        # core/project_manager.py's _create_default_project_data) -- the
        # guide has students use/place into THAT one rather than create a
        # new one, so place the hero directly into it instead of calling
        # am.create_asset (which would just make a second, unused room).
        room_data = am.get_asset("rooms", "room0")
        if room_data is None:
            raise RuntimeError("expected a default 'room0' in a new project")
        room_data["width"], room_data["height"] = 640, 480
        room_data["background_color"] = "#dff0ff"
        room_data["instances"] = [{
            "object_name": "obj_heros", "x": 300, "y": 220, "rotation": 0,
            "scale_x": 1.0, "scale_y": 1.0, "visible": True,
        }]
        _sync(ide)
        _capture_room(ide, am, app, "room0", "salle_editeur.png")

        # -- Bonus: fruit sprite + object -----------------------------------
        fruit_png = sprite_dir / "spr_fruit.png"
        _sprite_png(fruit_png, (28, 28), (220, 40, 40, 255), shape="fruit")
        fruit_asset = am.import_asset(fruit_png, "sprites", "spr_fruit")
        if fruit_asset is None:
            raise RuntimeError("failed to import sprite spr_fruit")
        am.create_asset("obj_fruit", "objects", sprite="spr_fruit",
                        solid=False, visible=True, events={})
        _sync(ide)

        # -- Bonus: hero collision + score (the action names/params below
        # are what the Score-Add / Destroy-Other / Draw-Score BLOCKS
        # actually generate, per blockly_generators.js -- NOT "add_score",
        # which isn't a registered action at all). Built as a FRESH dict
        # with the bonus events listed BEFORE "keyboard" (Python/JSON
        # preserve key order, and Blockly lays out blocks in that same
        # order) so this screenshot's viewport -- same window size as the
        # movement-only one, not tall enough for all 7 blocks at once --
        # shows the new collision/draw blocks at the top instead of the
        # already-illustrated movement blocks scrolled into view instead.
        hero_data = am.get_asset("objects", "obj_heros")
        hero_data["events"] = {
            "collision_with_obj_fruit": {
                "actions": [
                    {"action": "set_score", "parameters": {"value": "10", "relative": True}},
                    {"action": "destroy_instance", "parameters": {"target": "other"}},
                ],
                "target_object": "obj_fruit",
            },
            "draw": {"actions": [
                {"action": "draw_score", "parameters": {"x": "10", "y": "10", "caption": "Score: "}},
            ]},
            **hero_data["events"],
        }
        _sync(ide)
        _capture_object_blockly(ide, app, am, "obj_heros", "objet_blockly_bonus.png")

        # -- Bonus: room with fruits placed too ------------------------
        room_data["instances"].extend([
            {"object_name": "obj_fruit", "x": 120, "y": 100, "rotation": 0,
             "scale_x": 1.0, "scale_y": 1.0, "visible": True},
            {"object_name": "obj_fruit", "x": 480, "y": 380, "rotation": 0,
             "scale_x": 1.0, "scale_y": 1.0, "visible": True},
            {"object_name": "obj_fruit", "x": 500, "y": 90, "rotation": 0,
             "scale_x": 1.0, "scale_y": 1.0, "visible": True},
        ])
        _sync(ide)
        _capture_room(ide, am, app, "room0", "salle_fruits.png")

        print("Junior FR student handout capture complete.")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
