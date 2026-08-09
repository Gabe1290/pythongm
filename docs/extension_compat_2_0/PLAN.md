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

### Task 1 — Ship 1.0.1 with a format-version guard *(do first)*

**Why first:** any 1.0 build that later meets a 2.0 file must refuse
gracefully instead of crashing or saving over it (which would strip the
manifest). This guard must live in the 1.0 line and go out as 1.0.1.

**Add this to the loader module:**
```python
# --- format-version guard (new in 1.0.1) -----------------------------------
SUPPORTED_FORMAT = (1, 9)   # this build understands any 1.x project

class ProjectTooNewError(Exception):
    def __init__(self, fmt):
        self.fmt = fmt

def check_project_format(project_dict):
    raw = project_dict.get("format_version", "1.0")   # 1.0 files omit the key
    try:
        fmt = tuple(int(p) for p in str(raw).split("."))
    except ValueError:
        fmt = (1, 0)
    if fmt > SUPPORTED_FORMAT:
        raise ProjectTooNewError(fmt)
    return fmt
```

**Integration (order matters):**
1. Call `check_project_format(data)` **immediately after `json.load`**,
   before building anything from the data — so a too-new file is rejected
   before any code path could later save over it. In this repo that's
   `core/project_manager.py`'s project-loading path — confirm the exact
   call site before implementing (it wasn't checked against real code in
   the design session).
2. Catch `ProjectTooNewError` at the UI layer and show a QMessageBox, e.g.
   *"This project was made with a newer version of PyGameMaker (format
   2.0). Please update to open it."* Then **abort the open** — the load
   must not complete.
3. Bump version to **1.0.1**, tag, and cut a patch release on GitHub.

**Needs before implementing:** locate the function that opens
`project.json` in `core/project_manager.py` (or wherever it actually is)
to place the call precisely — this repo's real loader wasn't consulted
when this plan was drafted.

### Task 2 — Implement the 2.0 format read/write

1. **Reader:** read `format_version` (default `"1.0"`) and
   `required_extensions` (default `{}`); compute
   `missing = required - installed`.
2. **Writer:** when saving a project that uses ≥1 extension action, write
   `format_version: "2.0"` and a `required_extensions` manifest listing
   every extension whose actions appear. When no extension is used, keep
   writing 1.0-style (no `format_version`) so ordinary files stay
   maximally compatible.
3. **Make the reader tolerant** (preserve unknown top-level keys) and the
   **writer full-fidelity** (preserve unknown actions verbatim).
4. **Add a round-trip test** on a real file asserting byte-identical
   preservation when the extensions aren't installed — `compat_demo.py`
   in this folder does exactly this (now proven against
   `samples/plateforme_3/project.json` too, see the verification update
   above) and is good starting scaffolding for both the real loader code
   and this test.

### Task 3 — Placeholder rendering for unknown actions

- In the event / Blockly editor, an action whose type is registered by
  neither core nor any installed extension renders as a **greyed-out,
  non-editable block**, labelled with the extension it needs (looked up
  from the `required_extensions` manifest entry).
- It must be preserved **verbatim** on save (guaranteed by Task 2.3).

### Task 4 — Install offer wired to the manifest

- When a project loads with missing extensions, present a prompt (one per
  missing extension, or one combined) using the manifest's display `name`:
  *"This project needs {name}. Install it?"*
- The label and identity come straight from the manifest entry, so the
  offer works even for an action the editor otherwise knows nothing about.

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
