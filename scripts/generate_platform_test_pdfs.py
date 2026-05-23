#!/usr/bin/env python3
"""Generate per-platform IDE testing checklists as printable PDFs.

Produces three PDFs in docs/:
  - PyGameMaker_Test_Windows.pdf
  - PyGameMaker_Test_macOS.pdf
  - PyGameMaker_Test_Linux.pdf

Each PDF contains every test item with a checkbox, and platform-specific
notes are highlighted while irrelevant items are marked "N/A" or adjusted.
"""

from fpdf import FPDF
import os
import textwrap

OUTDIR = os.path.join(os.path.dirname(__file__), os.pardir, "docs")

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

# Each item: (number, text, platform_notes)
# platform_notes is a dict mapping platform -> override text or None to skip
# If a platform is absent from platform_notes, the item applies as-is.
# If platform_notes[platform] is None, the item is skipped for that platform.
# If platform_notes[platform] is a string, it replaces the base text.

PHASES = []

def phase(title, time, items, note=None):
    PHASES.append({"title": title, "time": time, "items": items, "note": note})


# --- Phase 0 ---
phase("Phase 0 — Setup", "5 min", [
    (1, "Pull a fresh build from the rc.9 release page. Run on a clean machine where possible (no leftover .config/pygamemaker etc. — student install scenario).", {
        "Windows": "Pull a fresh build from the rc.9 release page. Run the .exe directly without admin elevation on a clean machine (no leftover config — student install scenario).",
        "macOS": "Pull a fresh build from the rc.9 release page. Run on a clean machine where possible (no leftover ~/.config/pygamemaker etc. — student install scenario).",
        "Linux": "Pull a fresh build from the rc.9 release page. Run on a clean machine where possible (no leftover ~/.config/pygamemaker etc. — student install scenario).",
    }),
    (2, "Verify the About dialog reports Version 1.0.0-rc.9.", {}),
    (3, "Confirm the binary launches correctly on this platform.", {
        "Windows": "Confirm SmartScreen doesn't block the .exe. If a SmartScreen prompt appears, 'Run anyway' should work.",
        "macOS": "Confirm the binary is executable. You may need to right-click → Open the first time to bypass Gatekeeper.",
        "Linux": "Confirm the binary is executable (chmod +x if needed). Verify no missing shared libraries (ldd check).",
    }),
], note="Pass criteria: app launches, About shows correct version.")


# --- Phase 1 ---
phase("Phase 1 — Cold launch / smoke", "10 min", [
    (4, "Launch with no project loaded — Welcome tab visible, asset tree empty.", {}),
    (5, "Open the demo / sample project that ships with the build. Asset tree populates within 2s.", {}),
    (6, "Switch language to French via Tools → Language → Français. Confirm the manual-restart message appears (auto-restart was removed in rc.7). Restart, verify French strings throughout.", {}),
    (7, "Switch back to English, restart.", {}),
    (8, 'Run the "Catch the Coins" tutorial — it should open in a detached, movable, non-blocking dialog (rc.7 change).', {}),
], note="Pass criteria: no crashes, no Python tracebacks in console, tutorial dialog floats freely.")


# --- Phase 2 ---
phase("Phase 2 — Project lifecycle", "10 min", [
    (9, "File → New Project — create a project in a fresh folder. Default assets / templates load.", {}),
    (10, "File → Save Project — confirm project.json and asset folders write to disk.", {}),
    (11, "Modify something (rename a sprite). Window title shows * dirty marker. Save — * clears.", {}),
    (12, "File → Close Project then File → Open Recent → <your project> — reloads correctly.", {}),
    (13, "Open project, then File → Open another project → first project's editors all close, second loads cleanly.", {}),
    (14, "File → Save Project As... — exports to a new location, asset references resolve.", {}),
], note="Pass criteria: project state persists round-trip; switching projects doesn't leak open editors or stale data.")


# --- Phase 3 ---
phase("Phase 3 — Asset CRUD", "15 min", [
    (15, "Create — right-click asset tree → New (for each asset type: sprite, sound, background, object, room, playground). Asset appears in tree, default name auto-numbers if duplicate.", {}),
    (16, "Rename — right-click → Rename. New name appears in tree, project.json reflects new name. [STAR] If an editor is open for that asset, the editor's tab text and its asset_name update too.", {}),
    (17, "Delete — right-click → Delete. Asset removed from tree and disk. If the asset is in use elsewhere (e.g. an object's sprite), confirm a sensible error/warning.", {}),
    (18, "Duplicate — right-click → Duplicate. New asset with _copy suffix.", {}),
    (19, "Import: Sprite — Import a PNG via toolbar → Import Sprite. Multi-frame GIF imports as animated frames. Sound — Import via toolbar → Import Sound. GMK — File → Import GameMaker .gmk File... (pick any .gmk file). Per-phase progress logged; all assets land.", {}),
], note="Pass criteria: every asset type round-trips through CRUD. No orphan files left behind on delete.")


# --- Phase 4 ---
phase("Phase 4 — Object editor", "20 min", [
    (20, "Open an object. Verify tabs: Event List / Blockly / Code Editor.", {}),
    (21, "Add a Create event via the events panel on the left. Drag a few Blockly blocks onto the Blockly tab. Confirm: auto-sync is bidirectional (edits in Blockly appear in events panel and vice versa). Code Editor tab shows generated Python code reflecting both.", {}),
    (22, "[STAR] Switch to the Blockly tab — events panel snaps narrower (rc.8 layout change). Switch back to Event List — events panel restores its wider default.", {}),
    (23, "Parent property inheritance (rc.7): Set Parent to another object. Properties not explicitly set on this object inherit from the parent. sprite / visible / solid / persistent are deliberately not inherited.", {}),
    (24, "Add a Collision event with another object. The collision target dropdown lists actual project objects (no hardcoded obj_wall placeholder).", {}),
    (25, "Add an alarm event (alarm_0). Confirm the events serialize under the nested alarm → alarm_0 format (rc.8).", {}),
    (26, "Modify, save (Ctrl+S). Tab * clears. Auto-save: leave a pending edit alone for 3s — the autosave indicator triggers, no * left.", {
        "macOS": "Modify, save (Cmd+S). Tab * clears. Auto-save: leave a pending edit alone for 3s — the autosave indicator triggers, no * left.",
    }),
    (27, "[STAR] Crash regression check: open an object with no events at all (fresh object). The editor must not throw a NameError on events_data or project_data (rc.9 fix in load_data / load_project_assets).", {}),
], note="Pass criteria: all three tabs stay in sync; saves persist; alarm events work end-to-end.")


# --- Phase 5 ---
phase("Phase 5 — Sprite editor", "10 min", [
    (28, "Open a sprite. Pencil, eraser, fill, selection tools work.", {}),
    (29, "Origin crosshair: set via preset dropdown (Top-Left, Center, Center-Bottom). Verify X/Y spinboxes match. Save and reopen — origin persists.", {}),
    (30, "Multi-frame: add a frame, modify it. Frame strip updates.", {}),
    (31, "Save → confirm PNG file on disk reflects the edit.", {}),
], note="Pass criteria: sprite edits round-trip correctly.")


# --- Phase 6 ---
phase("Phase 6 — Room editor", "15 min", [
    (32, "Open a room. Object palette on the left lists project objects with their sprites.", {}),
    (33, "Drag-place a few instances. Grid + snap toggles work. Cut / Copy / Paste / Duplicate one of the placed instances via the toolbar buttons.", {}),
    (34, "Background layer config: open Properties → Backgrounds → 8-layer dialog. Set a background image. Toggle tile_horizontal / tile_vertical, scroll speeds. Save and reopen — settings persist.", {}),
    (35, "[STAR] Change the sprite assigned to an object that's used in this room. The room canvas should refresh and show the new sprite immediately (rc.9 refresh_object_sprites fix).", {}),
    (36, "Save with Tile Palette open and instances on canvas.", {}),
], note="Pass criteria: room layout persists; object→sprite changes propagate without reopening.")


# --- Phase 7 ---
phase("Phase 7 — Playground editor (Thymio)", "10 min", [
    (37, "Open a playground. Wall / robot / block paint modes work.", {}),
    (38, "Set arena dimensions and ground texture. Confirm ground texture file copies into project's playgrounds/ folder.", {}),
    (39, "Link a placed robot to a Thymio object. Modify, save.", {}),
    (40, "[STAR] Click Float — playground editor pops out into its own window (rc.9 capability). Modify — title shows *. Click Attach — returns to tab strip.", {}),
    (41, "Run — playground simulator launches with the linked robot's code.", {}),
], note="Pass criteria: playground edits persist; floating works on parity with other editors. (Skip if your students don't use Thymio.)")


# --- Phase 8 ---
phase("Phase 8 — Floating windows [STAR] (rc.8/rc.9 core feature)", "20 min", [
    (42, "Open an Object editor. Click Float — pops into a movable window. Original tab is removed. Welcome tab reappears if no other tabs.", {}),
    (43, "Modify. Window title shows *. Save — * clears.", {}),
    (44, "Close the floating window (X) — editor returns to a tab.", {}),
    (45, "Open two object editors. Float them both. Drag side-by-side. Edit each independently. Save each.", {}),
    (46, "With two editors open, add a sprite to the project (asset tree → Import). Both floating editors' Blockly sprite dropdowns refresh without closing/reopening.", {}),
    (47, 'Global mode toggle on the main toolbar: click "Tabbed" flips to "Floating", every tabbed editor pops out. Click "Floating" flips back to "Tabbed", every floating editor returns to tabs. Setting persists across IDE restart.', {}),
    (48, "Recovery scenario: float an editor, drag the window mostly off-screen so only a sliver is visible. Click the toolbar mode toggle — the off-screen window snaps back to a tab. (Student-rescue flow.)", {}),
    (49, 'With global mode = "Floating", open a new asset from the asset tree — it should immediately appear as a floating window, not a tab.', {}),
    (50, "Float an editor with unsaved changes. Press Ctrl+W in the floating window — save prompt appears with the floating window as parent (not the IDE main window). Save / Discard / Cancel all behave correctly.", {
        "macOS": "Float an editor with unsaved changes. Press Cmd+W in the floating window — save prompt appears with the floating window as parent (not the IDE main window). Save / Discard / Cancel all behave correctly.",
    }),
    (51, "Float an editor, then switch projects (File → Open another project). Floating window closes cleanly, no leak, no error in console (rc.8 teardown fix).", {}),
    (52, "Open the same asset twice (e.g. via the asset tree double-click). The IDE focuses the existing window/tab, doesn't create a duplicate.", {}),
], note="Pass criteria: every detach/reattach combination works; no console errors; floating-window minimum height is now ~half what it was — two editors fit side-by-side at common laptop resolutions.")


# --- Phase 9 ---
phase("Phase 9 — Multi-editor invariants [STAR] (rc.9 audit area)", "15 min", [
    (53, "Asset rename with floating editor: open obj_player, float it. From the asset tree rename obj_player → obj_hero. Floating window title updates to obj_hero. Editor still saves to the new asset (no orphan obj_player.json left behind).", {}),
    (54, "Cross-editor sprite refresh: open obj_a floated, open obj_b tabbed. Add a new sprite to the project. Both editors' Blockly sprite dropdowns include the new sprite without manual refresh.", {}),
    (55, "Cross-editor save broadcast: in obj_a, change properties and save. obj_b's view of the project (e.g. parent dropdown showing obj_a) reflects any rename/property changes.", {}),
    (56, "[STAR] Undo/Redo focus routing: float obj_a, focus its window, press Ctrl+Z. Undo applies to obj_a (not the active tab). Repeat with obj_b floated and focused.", {
        "macOS": "[STAR] Undo/Redo focus routing: float obj_a, focus its window, press Cmd+Z. Undo applies to obj_a (not the active tab). Repeat with obj_b floated and focused.",
    }),
    (57, "[STAR] Cut/Copy/Paste/Duplicate in a floated Room editor: place an instance, click on it, Ctrl+X / Ctrl+C / Ctrl+V / Ctrl+D — operations target the floated room editor.", {
        "macOS": "[STAR] Cut/Copy/Paste/Duplicate in a floated Room editor: place an instance, click on it, Cmd+X / Cmd+C / Cmd+V / Cmd+D — operations target the floated room editor.",
    }),
    (58, "Connection leak smoke: float, attach, float, attach an editor 10x in a row. No console growth in connection counts; no duplicate-emit symptoms.", {}),
], note="Pass criteria: detached editors are first-class targets for keyboard shortcuts and asset broadcasts.")


# --- Phase 10 ---
phase("Phase 10 — Save / dirty state / auto-save", "10 min", [
    (59, "Toggle Auto-save off in an editor's toolbar. Edit — * shows, no auto-save fires. Click Save — * clears.", {}),
    (60, 'With auto-save on, edit and wait 3s — auto-save fires; status pill shows "Saved".', {}),
    (61, "Modify two editors, then File → Close Project. Each editor independently prompts about unsaved changes.", {}),
    (62, "Close a single editor (Ctrl+W on tab) with unsaved changes — same prompt, scoped to that editor.", {
        "macOS": "Close a single editor (Cmd+W on tab) with unsaved changes — same prompt, scoped to that editor.",
    }),
], note="Pass criteria: dirty state is per-editor, save prompts target the right asset.")


# --- Phase 11 ---
phase("Phase 11 — Editions and Blockly presets", "10 min", [
    (63, "Tools → Edition → Beginner. Object editor's Blockly toolbox shrinks to beginner blocks; events panel filters accordingly.", {}),
    (64, "Tools → Edition → Advanced — full block set returns.", {}),
    (65, "Tools → Edition → Committee Demo — committee-approved minimal toolbox. Save the edition with the project. Reopen — preset persists.", {}),
    (66, "Tools → Configure Action Blocks... — toolbox configuration dialog. Save a custom preset, apply.", {}),
], note="Pass criteria: edition gating actually hides what it claims to hide; preset persists in project.json.")


# --- Phase 12 ---
phase("Phase 12 — Thymio integration", "10 min", [
    (67, "Tools → Configure Thymio Blocks. Confirm Thymio-specific block list.", {}),
    (68, "In an object's events panel, switch to the Thymio tab. Add a thymio_button_forward event with a movement action.", {}),
    (69, "Open a Thymio playground. Place a Thymio robot, link it to the object above.", {}),
    (70, "Run the playground (Run). Verify the robot responds to the Thymio events.", {}),
    (71, "Aseba export — both paths: (a) playground editor → File → Export produces a working .playground file Aseba Studio can open; (b) main IDE → File → Export Aseba (Thymio) code… writes one .aesl file per Thymio object plus a README.md. Both load in Aseba Studio.", {}),
], note="Pass criteria: Thymio events fire end-to-end; both Aseba export paths round-trip into Aseba Studio. (Skip if your install doesn't use Thymio.)")


# --- Phase 13 ---
phase("Phase 13 — Game runtime", "15 min", [
    (72, "Open a sample project with movement. Test Game (Run in toolbar) launches the game window.", {}),
    (73, "Verify movement actions (rc.9 fix): trigger a move_free action via a key press. Robot/object should move (this would have NameError'd before rc.9).", {}),
    (74, "Collision events: trigger a collision between objects. Collision handler runs.", {}),
    (75, "Alarm events: set an alarm via Blockly (set_alarm action), trigger it. Alarm fires after the configured step count.", {}),
    (76, "Score / Lives / Health: score updates, draws on screen.", {}),
    (77, "Room transitions: next_room, goto_room, restart_room all work.", {}),
    (78, "Debug Game: launches with debug overlay (FPS, state).", {}),
    (79, "Build a tiny test game using only Blockly — verify it runs end-to-end without writing any Python.", {}),
], note="Pass criteria: all common runtime actions work; no NameErrors from the rc.9-fixed code paths.")


# --- Phase 14 ---
phase("Phase 14 — Importers", "10 min", [
    (80, "GMK import (File → Import GameMaker .gmk File...): pick a real .gmk file. Per-phase progress logs to console. Imported assets appear in tree.", {}),
    (81, "Open an imported sprite — frames load, dimensions correct.", {}),
    (82, "Open an imported object — events visible.", {}),
    (83, "Roberta import (if relevant): File → Import Roberta. Smoke-test only.", {}),
], note="Pass criteria: GMK round-trip lands assets without crashing; object events at least display.")


# --- Phase 15 ---
phase("Phase 15 — Exporters", "30 min, parallelizable", [
    (84, "HTML5 Export (File → Export → HTML5): produces a self-contained folder with index.html + assets. Open in a browser — game runs.", {}),
    (85, "Windows EXE (File → Export → Build for Windows): .exe produced. Run on a clean Windows VM — game runs without Python installed. [STAR] Test that the exporter doesn't NameError on its process variable in the subprocess.TimeoutExpired path (rc.9 fix).", {
        "macOS": "Windows EXE (File → Export → Build for Windows): .exe produced (cross-compile if available). [STAR] Test that the exporter doesn't NameError on its process variable in the subprocess.TimeoutExpired path (rc.9 fix).",
        "Linux": "Windows EXE (File → Export → Build for Windows): .exe produced (cross-compile if available). [STAR] Test that the exporter doesn't NameError on its process variable in the subprocess.TimeoutExpired path (rc.9 fix).",
    }),
    (86, "Linux build (if available on your machine).", {
        "Windows": "Linux build: N/A on Windows (skip unless cross-compile tooling is installed).",
        "macOS": "Linux build: N/A on macOS (skip unless cross-compile tooling is installed).",
        "Linux": "Linux build: build and run locally. Confirm the binary launches without missing shared libraries.",
    }),
    (87, "macOS build (if you have a Mac).", {
        "Windows": "macOS build: N/A on Windows (skip).",
        "macOS": "macOS build: build and run locally. Confirm the .app bundle launches. Check code signing if applicable.",
        "Linux": "macOS build: N/A on Linux (skip).",
    }),
    (88, "Android build (Buildozer): only if Android tooling is installed.", {
        "Windows": "Android build (Buildozer): only if Android tooling is installed. Confirm the WSL bridge path works.",
        "macOS": "Android build (Buildozer): only if Android tooling is installed.",
        "Linux": "Android build (Buildozer): only if Android tooling is installed.",
    }),
    (89, "iOS build (kivy-ios): macOS-only, optional.", {
        "Windows": None,  # skip on Windows
        "Linux": None,    # skip on Linux
        "macOS": "iOS build (kivy-ios): optional. Confirm Xcode project generation works.",
    }),
    (90, "Project ZIP export (File → Export → ZIP): ZIP file contains project + assets.", {}),
    (91, "Python sdist (auto-built by CI): pip install <name>.tar.gz in a venv works.", {}),
], note="Pass criteria: at minimum HTML5 + native-platform export + ZIP export work end-to-end.")


# --- Phase 16 ---
phase("Phase 16 — i18n / language switching", "10 min", [
    (92, "Cycle through every supported language (DE / ES / FR / IT / RU / SL / UK), restarting between each. Verify: menu bar translates, asset tree headers translate, editor toolbars translate, Blockly block labels translate (use the _blockly.qm files), tutorial dialog translates.", {}),
    (93, 'Confirm French shows the rc.7 hand-translated strings (1399 finished entries; should look complete, not "Form X" placeholders).', {}),
    (94, "After language switch, verify nothing logs KeyError for a missing translation.", {}),
], note="Pass criteria: core UI is translated; no missing-translation crashes.")


# --- Phase 17 ---
phase("Phase 17 — Stress / classroom edge cases", "15 min", [
    (95, "Rapid-click Save on an editor 50 times. No double-saves, no crash, no race.", {}),
    (96, "Open 10 editors, float them all. Window minimum-height (rc.9 halved) lets you see them all on a 1080p screen.", {}),
    (97, "Drag a floating window mostly off-screen — confirm the toolbar global mode toggle recovers it (Phase 8 #48 again, but try it on a multi-monitor setup if you have one).", {}),
    (98, "Press Ctrl+Z 50 times rapidly in a fresh editor — undo stack is bounded (200 per BaseEditor); no crash, no growing memory.", {
        "macOS": "Press Cmd+Z 50 times rapidly in a fresh editor — undo stack is bounded (200 per BaseEditor); no crash, no growing memory.",
    }),
    (99, "Open a corrupted .json project (manually edit project.json to break the JSON). Project load should fail with a user-readable error, not a Python traceback.", {}),
    (100, "Disk full / read-only project folder — save attempt produces a clean error dialog, not a silent failure.", {}),
    (101, "Two students on the same machine (multi-user simulation): user A's settings/recent-projects don't leak to user B.", {}),
], note="Pass criteria: no surprises in classroom-realistic conditions.")


# --- Phase 18 ---
phase("Phase 18 — Build artifacts (the actual release)", "10 min", [
    (102, "From the rc.9 GitHub Release page, download each platform's artifact.", {
        "Windows": "From the rc.9 GitHub Release page, download the Windows artifact (.exe / .msi).",
        "macOS": "From the rc.9 GitHub Release page, download the macOS artifact (.dmg / .app).",
        "Linux": "From the rc.9 GitHub Release page, download the Linux artifact (.AppImage / .deb / tarball).",
    }),
    (103, 'Run on a clean target (VM or fresh user account). Confirm it launches without "missing DLL" / "missing Qt plugin" errors.', {
        "Windows": 'Run on a clean Windows VM or fresh user account. Confirm it launches without "missing DLL" / "missing Qt plugin" errors.',
        "macOS": "Run on a clean macOS VM or fresh user account. Confirm it launches without missing framework / Qt plugin errors.",
        "Linux": 'Run on a clean Linux VM or fresh user account. Confirm it launches without "missing .so" / "missing Qt plugin" errors. Test on both Ubuntu and Fedora if possible.',
    }),
    (104, "Verify the executable's version metadata shows 1.0.0-rc.9.", {
        "Windows": "Verify the executable's File Properties shows version 1.0.0-rc.9 (the version_info.txt change should propagate to PE metadata).",
        "macOS": "Verify the .app bundle's Info.plist shows version 1.0.0-rc.9.",
        "Linux": "Verify the --version flag or About dialog shows version 1.0.0-rc.9.",
    }),
    (105, "Confirm pip-install of the Python sdist works in a venv: pip install pygamemaker-1.0.0rc9.tar.gz, then python -m pygamemaker launches.", {}),
], note="Pass criteria: all advertised platforms produce a working binary out of the box.")


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

STAR = chr(9733)  # ★

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT_FAMILY = "DejaVu"


class TestPDF(FPDF):
    def __init__(self, platform):
        super().__init__()
        self.platform = platform
        self.set_auto_page_break(auto=True, margin=20)
        # Register a Unicode-capable font
        self.add_font(FONT_FAMILY, "", os.path.join(FONT_DIR, "DejaVuSans.ttf"))
        self.add_font(FONT_FAMILY, "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"))
        self.add_font(FONT_FAMILY, "I", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"))

    def header(self):
        self.set_font(FONT_FAMILY, "B", 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f"PyGameMaker 1.0.0-rc.9 \u2014 {self.platform} Testing Checklist", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT_FAMILY, "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def phase_title(self, title, time):
        # Need room for title + at least ~30mm for first item
        if self.get_y() > 240:
            self.add_page()
        else:
            # Separator line between phases
            self.ln(4)
            self.set_draw_color(180, 180, 180)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)
        self.set_font(FONT_FAMILY, "B", 13)
        self.set_text_color(30, 30, 30)
        self.cell(0, 9, f"{title}  ({time})", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(60, 60, 60)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def pass_criteria(self, text):
        self.set_font(FONT_FAMILY, "I", 9)
        self.set_text_color(80, 80, 80)
        self.ln(2)
        self.multi_cell(0, 5, text)
        self.ln(4)

    def checklist_item(self, number, text, is_star=False):
        x_start = self.get_x()
        y_start = self.get_y()

        # Check for page break need
        # Estimate height: ~5mm per line, ~95 chars per line at this font
        est_lines = max(1, len(text) // 85 + 1)
        est_height = est_lines * 5 + 4
        if y_start + est_height > 275:
            self.add_page()
            y_start = self.get_y()

        # Checkbox
        self.set_draw_color(80, 80, 80)
        self.set_fill_color(255, 255, 255)
        checkbox_x = 12
        checkbox_y = y_start + 1
        self.rect(checkbox_x, checkbox_y, 4, 4)

        # Star marker for audit-critical items
        prefix = ""
        if is_star:
            prefix = STAR + " "
            self.set_text_color(200, 150, 0)
        else:
            self.set_text_color(40, 40, 40)

        # Number + text
        self.set_font(FONT_FAMILY, "B" if is_star else "", 9)
        self.set_x(19)
        num_text = f"{number}. "
        self.cell(self.get_string_width(num_text), 5, num_text)

        # Body text
        self.set_font(FONT_FAMILY, "", 9)
        if is_star:
            self.set_text_color(40, 40, 40)
        body_x = 19 + self.get_string_width(num_text)
        available_w = 190 - body_x + 10
        # Replace [STAR] markers with ★
        display_text = text.replace("[STAR] ", f"{STAR} ")
        self.set_x(body_x)
        self.multi_cell(available_w, 5, display_text)
        self.ln(1.5)


def generate_pdf(platform):
    pdf = TestPDF(platform)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Title page content
    pdf.set_font(FONT_FAMILY, "B", 22)
    pdf.set_text_color(20, 20, 20)
    pdf.ln(10)
    pdf.cell(0, 12, "PyGameMaker", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT_FAMILY, "", 14)
    pdf.cell(0, 8, "IDE Testing Checklist — v1.0.0-rc.9", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font(FONT_FAMILY, "B", 16)
    pdf.set_text_color(0, 80, 160)
    pdf.cell(0, 10, f"Platform: {platform}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Legend
    pdf.set_text_color(60, 60, 60)
    pdf.set_font(FONT_FAMILY, "", 10)
    pdf.cell(0, 6, f"Date: _______________    Tester: _______________    Build: rc.9", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.cell(0, 6, f"{STAR} = audit-critical item (must pass for 1.0 release)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(180, 180, 180)
    pdf.rect(12, pdf.get_y() + 1, 4, 4)
    pdf.set_x(19)
    pdf.cell(0, 6, "= checkbox (mark with X when passed)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # "Ready for 1.0" summary
    pdf.set_font(FONT_FAMILY, "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, 'What "ready for 1.0" means:', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT_FAMILY, "", 9)
    pdf.set_text_color(50, 50, 50)
    mandatory = [
        f"All {STAR} items pass (these are the rc.7 → rc.9 audit-driven regressions).",
        "Phases 1, 2, 3, 4, 8, 13 pass on at least Windows + one other platform.",
        "HTML5 + at least one native-platform export works end-to-end.",
    ]
    for m in mandatory:
        pdf.set_x(15)
        pdf.multi_cell(180, 5, f"  - {m}")
    pdf.ln(4)

    # Tips
    pdf.set_font(FONT_FAMILY, "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, "Tips:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT_FAMILY, "", 9)
    pdf.set_text_color(50, 50, 50)
    tips = [
        "Use a separate user account for testing to avoid polluting your dev environment.",
        "Keep the console visible while testing — many bugs log tracebacks without user-visible errors.",
        "Save the rc.9 builds for bisecting if a regression surfaces after promoting to 1.0.",
    ]
    for t in tips:
        pdf.set_x(15)
        pdf.multi_cell(180, 5, f"  - {t}")

    # Phases — flow continuously (no forced page break per phase)
    pdf.ln(6)
    for p in PHASES:
        pdf.phase_title(p["title"], p["time"])

        for num, text, pnotes in p["items"]:
            # Determine text for this platform
            if platform in pnotes:
                plat_text = pnotes[platform]
                if plat_text is None:
                    continue  # skip this item on this platform
                text = plat_text

            is_star = "[STAR]" in text or "[STAR]" in str(num)
            # Also check original for star markers
            if not is_star:
                is_star = text.startswith(f"{STAR}")

            pdf.checklist_item(num, text, is_star=is_star)

        if p["note"]:
            pdf.pass_criteria(p["note"])

    # Final sign-off page
    pdf.add_page()
    pdf.set_font(FONT_FAMILY, "B", 16)
    pdf.set_text_color(30, 30, 30)
    pdf.ln(20)
    pdf.cell(0, 10, "Sign-off", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    pdf.set_font(FONT_FAMILY, "", 11)
    pdf.set_text_color(50, 50, 50)

    fields = [
        f"Platform: {platform}",
        "All mandatory phases passed:   [ ] YES   [ ] NO",
        f"All {STAR} items passed:   [ ] YES   [ ] NO",
        "",
        "Blocking issues found: _________________________________________________",
        "",
        "___________________________________________________________________________",
        "",
        "___________________________________________________________________________",
        "",
        "Non-blocking issues / notes: _____________________________________________",
        "",
        "___________________________________________________________________________",
        "",
        "___________________________________________________________________________",
        "",
        "",
        "Tester signature: ________________________   Date: _______________",
    ]
    for f in fields:
        pdf.cell(0, 8, f, new_x="LMARGIN", new_y="NEXT")

    outpath = os.path.join(OUTDIR, f"PyGameMaker_Test_{platform}.pdf")
    pdf.output(outpath)
    return outpath


if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    for platform in ("Windows", "macOS", "Linux"):
        path = generate_pdf(platform)
        print(f"Generated: {path}")
