# PyGameMaker 2.0 Extension System — Compatibility Plan

**Provenance:** designed in a mobile session (off-machine, no repo access) on
2026-08-09 and brought in via `docs/SESSION_NOTES.md`'s 2026-08-09 entry. The
brief below is reproduced from that session's handoff doc, with two edits:
garbled UTF-8 (the mobile export double-encoded em dashes, ellipses, and
`≥` as `â€¦`-style mojibake) fixed throughout, and a **verification update**
(next section) confirming the prototype's three claimed properties actually
hold against a real, current file in this repo — not just the file the phone
session had local access to. Per this repo's standing "audit is a lead, not
ground truth" discipline, re-verify anything below against current code
before implementing it; this plan hasn't touched `core/project_manager.py`
or any other real loader code yet.

## Verification update (2026-08-09, done in-repo)

The original design session proved its three properties against a local
`project_1_0.json` that isn't part of this repo (the user's own working
copy). Re-ran the identical `compat_demo.py` logic in this session against
**`samples/plateforme_3/project.json`** (the actual bundled sample) instead,
in a scratch directory — not touching the real sample file. All three
properties held:

1. `Loader_2_0` reads the real `plateforme_3` project cleanly — no
   `format_version`, defaults to `(1, 0)`, zero missing extensions, zero
   unknown actions.
2. `Loader_1_0.load_guarded` refuses a 2.0-tagged copy of that same file
   (`REFUSE`, no crash, no save).
3. `Loader_2_0` with no extensions installed round-trips a 2.0-tagged copy
   **byte-for-byte** (`orig == back` on the full parsed dict), correctly
   flagging `obj_pingus.step`'s injected `thymio_drive`/`set_camera_3d` as
   unknown (neither exists in this repo's action registry today, real or
   Thymio-plugin).

This is real confirmation the loader *design* is sound against this
project's actual file shape — it says nothing about the real
`core/project_manager.py` loader/saver, which hasn't been touched.

## Implementation update (2026-08-09) — Task 1 DONE; Task 2 mostly already existed

**Task 1 is done, shipped as v1.1.2** (`core/project_format.py`,
`ProjectManager.load_project()`, `core/ide_window.py`'s
`_show_load_failure_message`; tests in
`tests/test_project_format_guard.py`). Two corrections to this plan's
original assumptions, found while implementing:

1. **Version number was stale.** The plan said "ship 1.0.1" — written
   when the phone session's mental model of this repo's release state
   was `1.0`. `CHANGELOG.md`/`git tag` show the actual current line is
   **1.1.x** (`v1.1.1` released 2026-07-14); this shipped as **1.1.2**
   instead. If you're picking this plan up later and the repo has moved
   further, check `__init__.py`'s `__version__` again before assuming
   any specific number.
2. **`version` field confirmed** (open question from the original plan):
   `ProjectManager._validate_project_data` requires it and treats it as
   the *project's own* version (e.g. `"1.0.0"` in a brand-new project),
   never the app/format version — confirming `format_version` as a
   genuinely separate new field was the right call.

**Bigger finding: most of Task 2 already exists, under different names,
and has one confirmed live bug.** `events/plugin_loader.py` already
implements an extension-dependency system that predates this plan:

- `requires_extensions` (a plain list of extension *folder names* — the
  phone plan's `required_extensions` dict, simplified) is auto-derived
  from a project's action names and written into `project.json` on
  every save (`ProjectManager._prepare_project_data_for_save`), via
  `required_extensions_for_project()`.
- `missing_extensions_for_project()` detects when a project uses actions
  from an extension that's installed but currently *disabled*, and
  `not_installed_extensions_for_project()` detects when it names an
  extension folder that's *not present at all* — exactly the "opened by
  an editor without the extension" case this plan exists for. Both are
  wired into `core/ide_window.py`'s `_warn_missing_extensions()`, shown
  as a `QMessageBox` right after a project loads.
- Unknown actions already survive a save verbatim (nothing in
  `_prepare_project_data_for_save` touches `assets.objects`), and the
  Object Events panel already renders an action `get_action_type()`
  doesn't recognize with a distinct `❓ <raw action id>` label
  (`editors/object_editor/object_events_panel.py`'s
  `_set_action_item_text`) instead of crashing or hiding it.

**Confirmed bug in the existing system** (found by testing it directly,
not by inspection alone): `_prepare_project_data_for_save` recomputes
`requires_extensions` from scratch on every save via
`required_extensions_for_project()`, which can only name extensions that
are **present on disk** (it iterates `list_available_extensions()`, a
glob of the local `extensions/` folder). If editor B has an extension
folder editor A had, editor B's resave computes an empty `reqs` for that
folder's actions and the code does `data.pop('requires_extensions',
None)` — **silently erasing the manifest record**, even though the
actual unrecognized actions are still sitting untouched in
`assets.objects`. Reproduced directly:
```python
from events.plugin_loader import required_extensions_for_project
required_extensions_for_project({
    "requires_extensions": ["threed"],
    "assets": {"objects": {"obj_pingus": {"events": {"step": {"actions": [
        {"action": "set_camera_3d", "parameters": {}},
    ]}}}}},
})  # -> [] , not ["threed"] — "threed" isn't installed here to confirm it
```
This is exactly the preserve-on-save invariant Task 2.3 asks for, and
it's currently violated. **This is Tier 3 item 13's real starting
point** — fix `_prepare_project_data_for_save` to keep any
`requires_extensions` entry it can't positively verify is stale (i.e.
any folder name not present in `list_available_extensions()` at all),
rather than trusting a recomputation that structurally can't see
absent extensions. The rest of "Task 2" doesn't need building from
scratch; it needs this one fidelity fix plus the `format_version`
guard's Task 1 (done) sitting alongside it.

**Tasks 3 and 4 are correspondingly smaller than drafted, too** — see
each task's own section below for what already exists vs. what's still
a real gap.

## 1. Goal

Introduce a 2.0 extension system while guaranteeing that a project using
extensions **never crashes or silently corrupts** when opened in an editor
that doesn't have those extensions installed. This matters because the
audience is children on mixed hardware who may be running different
versions of the app.

## 2. How the project file works (confirmed from a real `project.json`)

- A single `project.json` sits next to resource folders. Assets are grouped
  under `assets` into: `sprites`, `sounds`, `backgrounds`, `objects`,
  `rooms`, `scripts`, `fonts`, `data`.
- Objects hold behaviour in an `events` dict keyed by event name (`create`,
  `step`, `collision_with_<obj>`, `keyboard`, `keyboard_release`, …). Each
  event has an `actions` list.
- **Each action is stored symbolically:** `{"action": "<type_id>",
  "parameters": {...}}`. There is **no generated Python code** in the
  project file — the action string references a handler that lives in code.
- **Consequence:** a "missing extension" is simply an action whose `action`
  type isn't registered by any installed component. Its type + parameters
  remain intact in the JSON regardless, so nothing is lost as long as the
  loader/saver don't discard it.

## 3. Decisions already made (settled — do not re-litigate)

1. **Extensions are a 2.0 feature.** 1.0 does not use extensions.
2. **Required extensions are recorded in the project file itself** (a
   manifest), so a project is self-describing and needs no network to
   explain what it requires.
3. **New top-level `format_version` field**, kept separate from the
   existing `version` field (which stays the *project's own* version).
   Absence of `format_version` → treat the file as format `1.0`.
4. **`required_extensions` is a dict keyed by extension id**, matching the
   project's existing dict-keyed-by-name convention:
   ```json
   "format_version": "2.0",
   "required_extensions": {
     "thymio": { "name": "Thymio Robotics", "min_version": "1.0.0" },
     "threed":  { "name": "3D",              "min_version": "1.0.0" }
   }
   ```
5. **Backwards-compatibility invariants** — must hold anywhere the file is
   read or written:
   - *Graceful default:* a missing key yields a sensible default, never an
     error.
   - *Tolerant reader:* ignore and preserve unknown keys; never reject a
     file over them.
   - *Preserve-on-save:* round-trip unknown top-level keys **and** unknown
     actions with zero data loss.
6. **Missing-extension UX:** an unrecognised action renders as a
   **visible, greyed-out, non-editable placeholder block**, preserved
   verbatim on save, accompanied by an **offer to install** the missing
   extension.
7. **Two known extensions** to design against: **Thymio** (robotics) and
   **3D**. (Note: this repo already ships a real folder-extension pattern
   for the raycast 2.5D feature — see `docs/RAYCAST_EXTENSION_PLAN.md` —
   worth reading before designing the "3D" extension's packaging, since it
   may be able to reuse that mechanism rather than invent a second one.)
8. **1.0 is already released on GitHub** with few downloads. Decision:
   don't chase already-downloaded copies; protect future downloads via a
   **1.0.1 patch release**.

## 4. Work to do, in order

### Task 1 — Ship a format-version guard *(do first)* — ✅ DONE, v1.1.2

**Why first:** any build that later meets a newer-format file must refuse
gracefully instead of crashing or saving over it (which would strip the
manifest). Shipped as `core/project_format.py`
(`SUPPORTED_FORMAT = (1, 9)`, `ProjectTooNewError`,
`check_project_format()`, near-identical to the sketch this section used
to have here), called from `ProjectManager.load_project()` immediately
after `json.load` and before any further processing, with a specific
`QMessageBox` at the UI layer (`ide_window.py`'s
`_show_load_failure_message`) rather than a generic load-failure
message. Tests: `tests/test_project_format_guard.py` (13 tests,
including a byte-for-byte on-disk-unchanged assertion after a refused
load — the concrete "does not crash or corrupt" proof). Shipped as
**v1.1.2** (not 1.0.1 — see the Implementation update above for why).

### Task 2 — Extension-dependency manifest read/write — ✅ DONE

**Mostly already existed** (see the Implementation update above) as
`events/plugin_loader.py`'s `requires_extensions` field +
`required_extensions_for_project()`/`missing_extensions_for_project()`/
`not_installed_extensions_for_project()`, auto-derived and written on
every save. The one confirmed gap is fixed:
`ProjectManager._prepare_project_data_for_save` no longer lets a
recomputed (necessarily incomplete — it can only see extensions present
on disk) `required_extensions_for_project()` result silently drop an
existing `requires_extensions` entry the current editor can't verify is
stale; it unions the recomputed set with any entry absent from
`list_available_extensions()`, only dropping entries it can positively
confirm are gone. `tests/test_extension_manifest_preservation.py` (5
tests) covers the resave-wipe case, the genuinely-stale-entry-gets-
dropped case, and a mixed verifiable/unverifiable case. The reader side
(tolerant of an absent/malformed `requires_extensions`, preserves
unknown top-level keys) needed no change —
`_validate_project_data` only requires `name`/`version`/`assets`.

### Task 3 — Placeholder rendering for unknown actions — ✅ DONE

`editors/object_editor/object_events_panel.py`'s `_set_action_item_text`
already rendered an unrecognized action as `❓ <raw action id>` instead
of crashing or hiding it, and already survived a save untouched. Fixed
the two real gaps: it now renders **amber** (distinct from both a
normal action and a comment's gray-italic) via a new
`events.plugin_loader.extension_for_action()` lookup, which also names
the owning extension in the label when its manifest is present on disk
(`❓ set_camera_3d (needs 3D)`) — falling back to the raw id alone when
no installed extension claims it. Double-clicking one no longer
silently no-ops; `edit_action` shows a `QMessageBox.information`
explaining whether the extension is installed-but-disabled or not
present at all, and reassures the user the action itself is unaffected
and will round-trip unchanged. `tests/test_extension_action_ui.py` (6
tests, using mocked `get_action_type`/`extension_for_action` rather than
relying on real global `ACTION_TYPES`/extension state, which can already
be mutated by `load_all_plugins()` having run earlier in the same
pytest session).

### Task 4 — Install offer wired to the manifest — partially done

**Partially already existed**, as a *warning*, not an *offer* — and
still is; this session fixed the warning's honesty but did not build a
real offer. `core/ide_window.py`'s `_warn_missing_extensions()` already
shows a `QMessageBox` naming each disabled/not-installed extension and
which actions need it. Fixed: its text used to say "Enable the
extensions in your config" — investigated and confirmed **no such
config UI exists anywhere in the app**
(`events.plugin_loader.set_extension_enabled()` is defined but never
called from any UI code), so that sentence was dropped rather than left
pointing at something that doesn't exist. **Still not built, and
deliberately so:** an actual one-click "enable this extension" UI. It
would need a real settings surface (Preferences? a new dialog? —
undecided) plus a restart prompt, since extensions register at startup.
Scope this properly before starting, the same way Asset Manager/Clean
Project need their own scoping pass — don't bolt it onto an unrelated
dialog. For an extension that's missing entirely (no folder on disk),
there is nothing to "install" in this bundled-extensions model anyway —
the honest message there is "update PyGameMaker," which
`_warn_missing_extensions` already provides via
`not_installed_extensions_for_project`.

## 5. Open questions to resolve against the real codebase

- **Is the current loader strict or tolerant about unknown keys?** If
  strict, loosen it (Task 2.3) — this protects every future format change,
  not just this one.
- **What does the existing `version` field mean today** — the project's
  version, or the app/format version? Confirm before finalising the
  `format_version` split.
- **Extension delivery model:** are Thymio / 3D bundled with the app (so
  "install" = "enable") or downloaded? This decides the install-offer flow
  and whether it must work offline — likely yes, given the audience. This
  repo's existing Thymio integration is bundled (`plugins/`,
  `extensions/`), which is a strong prior for "3D" following the same
  model rather than a network install.
- **Does the writer currently drop keys or actions it doesn't recognise?**
  If so, fix it before any 2.0 files exist, or old-but-2.0-aware editors
  will quietly lose data.
- **3D as a stress case:** a 3D project opened without the extension may
  be more than a few stray placeholder actions — it could affect
  rendering or room setup. Worth pressure-testing the placeholder approach
  against it once the basics work. (The raycast 2.5D extension is the
  closest existing precedent for a rendering-affecting extension in this
  codebase and is worth studying before designing 3D's placeholder story.)

## 6. Design-session artifacts (reference)

- **`project_2_0.json`** (this folder) — a real project (`plateforme_3`,
  captured 2026-06-17 as a personal working copy named
  `plateforme_3_refresh2`) upgraded to the 2.0 format: manifest + two
  injected extension actions, `thymio_drive` and `set_camera_3d`, in
  `obj_pingus`'s `step` event. **This is a point-in-time snapshot, not the
  current bundled `samples/plateforme_3/project.json`** — notably it
  still has the pre-2026-07-15 fragile stomp-test expression
  (`vspeed > 0 and y < other.y+8`) that CLAUDE.md's 2026-07-15 session
  note fixed to `vspeed > 0 and y - vspeed < other.y+8`. Don't copy logic
  out of it back into the real sample; it's here purely as the format-
  compatibility demo's input data. **One deliberate deviation from the
  original artifact:** `niveau_01`'s ~110-entry `tiles` array (pure
  background tile placements, never read by `compat_demo.py`'s logic) was
  truncated to `[]` when committing this to keep the file reviewable —
  everything `assets.objects`/`format_version`/`required_extensions`
  related, which the proof actually exercises, is untouched.
- **`compat_demo.py`** (this folder) — the loader prototype plus three
  tests proving, against `project_2_0.json`:
  1. a 2.0-aware loader reads a 1.0 file cleanly (defaults to "needs
     nothing");
  2. a 1.0-era loader refuses a 2.0 file with a warning and **without
     crashing or saving**;
  3. a 2.0-aware loader with the extensions **not** installed round-trips
     a 2.0 file **byte-for-byte** — manifest and unknown actions both
     preserved.

  As shipped it expects a local `project_1_0.json` (the pre-upgrade
  ancestor of `project_2_0.json`, not included — it was the phone
  session's own file) to regenerate `project_2_0.json` from scratch. To
  re-run the proof with what's actually in this repo, point `SRC` at
  `samples/plateforme_3/project.json` instead — this is exactly what the
  verification update above did.

Good starting scaffolding for the real loader code and the Task 2 test.
