# Full code audit — 2026-09-07

Registry of findings from a complete, sequential (single-thread, no
multi-agent fan-out) read of the codebase at `main` HEAD `221d1220`.
Every item below was **verified by reading the code**, not just flagged
by pattern matching; the "How verified" line on each says what was traced.
Treat them the way `CLAUDE.md` says to treat every audit: **leads, not
ground truth** — re-verify against current code before fixing, land each
fix with a regression test, flip the checkbox with the commit hash.

Scope read: `runtime/*` (all mixins, room, instance, collision, input,
sprite, hooks, run_game), `events/*` (action/event schemas, plugin loader,
conditional + action editors), `core/*` (project/asset managers, project
format, logger, ide_window + all `core/ide/_*.py` mixins, exporters,
language manager), `utils/*`, `plugins/audio_actions.py`, all three
extensions (`raycast_2_5d`, `block_world`, `multiplayer_lan` incl. the
WebSocket transport, discovery and connect screen), `export/*` (base,
desktop + exe/linux/macos, HTML5 + pyodide bundle, android, ios, Kivy
adapter/generator entry points), `importers/*` (gmk reader/parser/
converter/importer, roberta), the object/room/sprite editors' save paths,
asset-tree operations/dialogs/utils, `dialogs/project_dialogs.py`,
`config/blockly_config.py`, `main.py`.

**Deliberately not re-raised** (rejected in earlier audits, see
`CLAUDE.md`): `eval`/`exec` as HIGH, "unbounded" per-project caches,
a `load_project` path whitelist, the "infinite slide loop", the dialog
speed-restore "leak", splitting the large files.

Severity: **HIGH** = crash, data loss or silently wrong game for a normal
user action; **MEDIUM** = wrong behaviour on a realistic but narrower
path, or a real hardening gap; **LOW** = edge case, polish, defence-in-depth.

Totals: **6 high / 13 medium / 20 low**.

Three candidates were dropped during verification and are recorded here
so they are not re-raised: "editors stay open after a Trash-dialog
delete" (the tree's `assetDeleted` signal already closes them and the
Trash only holds already-deleted assets); "discovery beacon starts before
the bind check" (`handlers.py:357` starts it *after* `_start_session`
succeeds); "`_get_docs_url` lacks pt/ja/zh" (no `USER_MANUAL_PT/JA/ZH.md`
exists, so the English fallback is correct).

---

## High

- [x] **H1 — Held-key set mutated while iterated: `RuntimeError: Set changed size during iteration` kills the game.**
  `runtime/input_handler.py:254` — `_process_held_keys` does
  `for sub_key in instance.keys_pressed:` and runs the sub-event's action
  list inside the loop. Any action in that list that opens a modal
  (`show_message`, `show_info`, `splash_show_image`, the high-score /
  name-entry dialogs) pumps events, and their KEYUP branches call
  `_release_held_key_silent` (`runtime/input_handler.py:276`, called from
  `runtime/game_runner.py:1851/1955/2127/2349`), which `discard()`s from
  the very set being iterated. Releasing the held key while the message is
  up raises inside the handler; `execute_action`'s try/except is around the
  handler, but the exception escapes `_process_held_keys` into the loop and
  `run_game_loop`'s outer `except Exception` returns False — the game
  exits. Trigger: a `keyboard` (held) sub-event whose actions show a
  message, and the player lets go of the key while it is displayed.
  *Fix:* iterate a snapshot (`for sub_key in list(instance.keys_pressed)`)
  and skip keys no longer held; same in any other `keys_pressed`
  iteration. *How verified:* traced M54's `_release_held_key_silent` back
  to the four dialog KEYUP branches and the iteration site.
  **Fixed `00e7ee62`.**

- [x] **H2 — Exported desktop games never load their high scores.**
  `export/desktop/pygame_desktop_exporter.py:559` (LAUNCHER_TEMPLATE) does
  `runner = GameRunner(str(project))` **then**
  `runner.highscore_file = writable_dir() / "highscores.json"`. But
  `GameRunner.__init__` → `load_project_data_only` already set
  `self.highscore_file` (`runtime/game_runner.py:213/336`) and called
  `load_highscores()` against the *bundle* path. Reassigning the attribute
  afterwards only redirects the *save*; the loaded table stays empty, so
  every launch of a one-file export starts with no scores even though the
  previous run wrote them. *Fix:* reassign then call
  `runner.load_highscores()` (or accept a `highscore_file=` kwarg in
  `GameRunner.__init__`). *How verified:* read both sites; no second load
  call exists in the launcher or in `run()`.
  **Fixed `e06ed3da`.**

- [x] **H3 — Multiplayer: a connection killed during `send()`/`broadcast()` never emits `CONN_CLOSED` → phantom players.**
  `extensions/multiplayer_lan/network.py:203` (and the raw-TCP siblings)
  call `self._flush_conn(cid, conn, [])` with a throwaway event list;
  `_kill` (`network.py:176`) appends the `CONN_CLOSED` event into *that*
  list, which is discarded. The next `poll()` drops the dead conn because
  `not alive` without emitting. Same pattern in
  `extensions/multiplayer_lan/ws_transport.py:351`. Consequence: when a
  client's socket dies on a write (the common case — the host writes 20×/s),
  `session.py` never sees the leave, `player_count` stays high, the
  player's avatar/ghost is never destroyed, and `player_left` never fires.
  *Fix:* have `_flush_conn` append to `self._pending_events` (or return
  the list) so send-path kills surface on the next `poll()`. *How
  verified:* read `send`, `broadcast`, `_flush_conn`, `_kill`, `poll` in
  both transports.
  **Fixed `23d2c2a2`.**

- [x] **H4 — Multiplayer host applies client-owned rows without validation → crash or hijacked host state.**
  `extensions/multiplayer_lan/handlers.py:814` `_apply_host_own_state`
  does `inst.x = row.get("x", inst.x)` etc. straight from the wire (no
  numeric coercion, no bounds), and at `:835` (also `:902`, `:935` for the
  host→client direction) `for key, val in (row.get("vars") or {}).items():
  setattr(inst, key, val)` with only a value-type whitelist — the **key**
  is unchecked. A misbehaving or hostile client can set `x` to a string
  (TypeError in the movement code → game loop exits on the host), or send
  `vars={"object_data": ..., "action_executor": ..., "keys_pressed": ...}`
  and overwrite engine attributes on the host's copy of its avatar. The
  ownership check (`_on_client_own`, `:769`) only proves *which* instance
  the client may write, not *what*. *Fix:* coerce x/y/rotation/frame with
  `float()`/`int()` in try/except and clamp to the room; restrict `vars`
  keys to identifiers that are not existing `GameInstance` attributes
  (or to a declared replicated-var set). *How verified:* read
  `_apply_host_own_state`, `_apply_ghosts`, `_apply_synced_local`,
  `sanitize_value` (values only).
  **Fixed `7d39c74d`.**

- [x] **H5 — Android/iOS export drops room tiles, background layers, views, and object flags because of hand-maintained key lists.**
  `export/android/android_exporter.py:77` copies only
  `width/height/background_color/background_image/tile_horizontal/
  tile_vertical` from `rooms/<name>.json`; `export/ios/ios_exporter.py:308`
  the same, and `ios_exporter.py:326` copies **only `events`** from
  `objects/<name>.json`. The Kivy generator reads `tiles`, `views`,
  `enable_views`, `persistent`, `backgrounds` from the room dict
  (`export/Kivy/kivy_exporter.py:363/1775/1804/2952`), and `sprite/visible/
  solid/persistent/depth/parent` are *child-only* keys that live in the
  side file (`utils/project_file_merge.py` `_OBJECT_FILE_KEYS`) — so on a
  manifest-ified project (every project saved by a current IDE) a mobile
  export has no tiles, no views and (iOS) objects with no sprite. Android's
  object list at `:119` also lacks `remember_destroyed`. The desktop
  exporter and `base_exporter.py` already use `merge_room_file` /
  `merge_object_file`. *Fix:* route both mobile exporters through the
  shared kernels and delete the local key lists. *How verified:* diffed
  the three lists against `_ROOM_FILE_KEYS`/`_OBJECT_FILE_KEYS` and the
  generator's reads.
  **Fixed `9f9f85af`.**

- [x] **H6 — Asset names from the Create dialog are unvalidated; a name with `/`, `..` or a trailing dot breaks save.**
  `core/ide/_assets.py:497` passes `QInputDialog.getText`'s result straight
  to `create_asset_with_data`. The asset-tree dialogs *do* validate
  (`widgets/asset_tree/asset_utils.py` `validate_asset_name`, used by
  `asset_dialogs.py` and the rename path), but this menu path does not.
  With a name like `obj/foo` or `..` the asset lands in memory, then on
  save `_safe_asset_path` (`core/project_manager.py:69`) skips the side
  file with a warning (data silently not written) or `open()` fails on
  Windows for `foo.`/`CON`, tripping the cross-file rollback and losing
  the whole save. *Fix:* call `validate_asset_name` in `create_asset` and
  reject with the same message the tree uses. *How verified:* grep for
  validation on this path (none), traced to `_safe_asset_path`.
  **Fixed `0dab3277`.**

## Medium

- [x] **M1 — Multiplayer per-room session is orphaned on room change, and `PYGM_NET_AUTOHOST` re-hosts on every room.**
  State is per `GameRoom` via `peek_multiplayer(room)`; `change_room`
  builds a new room whose `extension_state` is empty, so the live
  `NetworkSession` (sockets, beacon thread) on the old room is never
  closed and the new room reports "not connected". With `PYGM_NET_AUTOHOST`
  set, `_resolve_state` (`extensions/multiplayer_lan/handlers.py:977`,
  env fallback `:953/958`) auto-starts a *second* session for the new room,
  which fails to bind the same port (or binds an ephemeral one) and shows
  the `_notify` error every room change. *Fix:* hold the session on the
  `GameRunner` (or migrate `extension_state["multiplayer"]` in
  `change_room`), and make AUTOHOST idempotent per process. *How
  verified:* `_resolve_state` + `change_room`'s fresh `GameRoom`.
  **Fixed `a718b6d3`** (new generic `extension_hooks.
  register_room_change_hook` mechanism, same shape as the existing
  room-renderer/frame-update hooks so core stays extension-agnostic;
  the extension's own hook migrates the whole per-room state dict —
  session, beacon, roster — onto the new room, which also makes
  AUTOHOST idempotent as a direct consequence: it only auto-starts for
  a room that genuinely has no state yet).

- [x] **M2 — Sprite rename leaves `sprites/<old>.json` behind (stale side file resurrects on reuse).**
  `core/asset_manager.py:550` carries the side file only for
  `("rooms", "objects", "playgrounds")`; `delete_asset` (`:393`) already
  handles `sprites` too. After renaming `spr_a`→`spr_b`, `sprites/spr_a.json`
  stays, and a future sprite named `spr_a` loads that stale file's
  `frame_width`/`precise`/`speed` over its own (H3's exact failure mode,
  for the fourth side-file type). *Fix:* add `"sprites"` to the tuple.
  **Fixed `011bf4c2`.**

- [x] **M3 — Object rename ignores room instances keyed `"object"` (the legacy key still shipped in samples).**
  `core/asset_manager.py:620` only rewrites `instance["object_name"]`.
  The runtime (`runtime/room.py:213`) and room editor accept
  `instance["object"]` as well, and `samples/plateforme_1/rooms/niveau_01.json`
  uses it for all 120 instances. Renaming an object in such a project
  leaves every placed instance pointing at the old name → they vanish at
  runtime. *Fix:* check both keys (and normalise to `object_name` on the
  way through).
  **Fixed `3a7ff2af`** (updates whichever key is present; did not force
  normalization to `object_name`, out of scope for this fix).

- [x] **M4 — `test_question` is always "yes" in the real game process.**
  **Fixed `eebbd02d`.**
  `runtime/action_flow.py:794` builds a `QMessageBox`; at `:810` it returns
  `True` when `QApplication.instance() is None`. `runtime/run_game.py`
  (the Test Game subprocess and every desktop export) never creates a
  QApplication, so the branch that shows a dialog only runs in the
  in-process IDE fallback. Authors get a conditional that never asks.
  *Fix:* implement it on the pygame side with the existing modal machinery
  (`show_message_dialog` with Y/N keys), mirroring `splash_show_text`.

- [x] **M5 — `change_room` / `_readd_persistent_instances` crash on an instance whose object no longer exists.**
  `runtime/game_runner.py:1129` and `:1531` (also `:1154/:1495`) evaluate
  `inst.object_data.get('persistent', False)` with no `None` guard. Room
  construction tolerates an orphan instance (object deleted, instance
  still in the room JSON) by giving it `object_data=None`; the first room
  change then raises `AttributeError` and the game exits. *Fix:*
  `(inst.object_data or {}).get(...)` at each site (or drop orphans at
  room build with a warning).
  **Fixed `9c2b6756`.**

- [x] **M6 — `destroy_instance` / `change_instance` with target=other silently act on self when there is no collision partner.**
  `runtime/action_spawn.py:52-54` and `:201-202`: `if target == "other"
  and self._collision_other:` else falls through to `self`. A GMK-imported
  "destroy other" placed in a non-collision event (or the "Applies to →
  Other" radio the editor now offers for these two actions) destroys the
  *caller*. *Fix:* when target is `other` and there is no partner, log
  and return without acting (GM's behaviour).
  **Fixed `4e37d922`.**

- [x] **M7 — Audio plugin: emoji `print()` before the `try`, and volume not parsed.**
  `plugins/audio_actions.py:138` prints `🔊 Playing sound: …` *outside*
  the try; on a cp1252 Windows console (any exported `.exe` run from cmd,
  `PYTHONUTF8` unset) that raises `UnicodeEncodeError` and the action
  aborts before playing. The logger got `ConsoleSafeHandler` for exactly
  this (2026-08-17); plain `print` did not. `:136/158/190` also do
  `float(parameters.get("volume", 1.0))` — an expression like `global.vol`
  or a `"0,5"` typo raises `ValueError` instead of going through
  `_parse_value`. *Fix:* use the logger; route volume through
  `instance.action_executor._parse_value` with a `try`.
  **Fixed `430ac6fd`.**

- [x] **M8 — WebSocket transport accepts unmasked client frames and has no Origin check.**
  `extensions/multiplayer_lan/ws_transport.py:94-119` decodes frames
  whether or not the mask bit is set; RFC 6455 §5.1 requires a server to
  fail the connection on an unmasked client frame (the masking exists to
  defeat cache-poisoning by browser-initiated cross-origin sockets). No
  `Origin` header check in the handshake either, so any web page a student
  visits on the LAN can drive their exported game's host. Local-network
  threat model, but the host is a *teacher's* machine. *Fix:* reject
  unmasked frames; accept only `Origin` values that are absent
  (non-browser) or match the HTML5 export's host, configurable.
  **Fixed `ecd690e9`** (zero-configuration default: no Origin, loopback,
  or matching this connection's own local address are allowed; any
  other Origin is rejected — no new config surface needed).

- [x] **M9 — Pending TCP/WS connections never time out.**
  `extensions/multiplayer_lan/network.py:107` accepts sockets and keeps
  them until a `HELLO`/handshake arrives; nothing expires a peer that
  connects and stays silent (port scanners, a browser that opened the
  socket and hung). Each costs a slot up to `max_players` and a
  per-frame `recv` attempt forever. *Fix:* record `monotonic()` on accept
  and kill after ~5 s without a handshake.
  **Fixed `05ab7b0a`** (implemented at the session layer, where the
  app-level HELLO/pending-tracking already lives, rather than inside
  `network.py`'s raw accept — that module has no concept of "handshake").

- [x] **M10 — Shared-variable names can shadow multiplayer identity globals.**
  `extensions/multiplayer_lan/handlers.py:667` `_apply_session_state`
  writes `is_host`/`player_id`/`player_count`/… then
  `for key, val in session.shared.items(): gv[key] = val`. A
  `set_shared_var name="is_host"` from any client overwrites every
  machine's `global.is_host`, breaking every "if host" branch.
  `is_valid_shared_name` checks syntax only. *Fix:* reserve the identity
  names in `is_valid_shared_name` (refuse at the setter, host side too).
  **Fixed `e71c418f`.**

- [x] **M11 — `.trash_orphaned_files` ships inside desktop exports.**
  `export/desktop/pygame_desktop_exporter.py:100`
  `SKIPPED_PROJECT_DIRS = {".trash", ".git", "__pycache__", "build", "dist"}`
  — `utils/project_cleanup.py`'s orphan trash root (`.trash_orphaned_files`,
  added after the desktop rework) is copied verbatim into the bundle, the
  same "shipping soft-deleted assets undoes the author's deletion" case
  landmine 4 in the 2026-08-17 note fixed for `.trash`.
  `utils/project_compression.py` excludes both. *Fix:* single-source the
  exclusion set (import it from `utils/project_compression.py` or
  `asset_trash`/`project_cleanup`).
  **Fixed `94b53eaa`** (both files now import `TRASH_DIR_NAME`/
  `ORPHAN_TRASH_DIR_NAME` from `asset_trash`/`project_cleanup`).

- [x] **M12 — Unaccented French in user-facing multiplayer error text.**
  `extensions/multiplayer_lan/handlers.py:348-351` ("heberger", "peut-etre
  deja utilise", "systeme", "reseau prive") and `:404-405` ("Verifiez",
  "l'hote", "lance", "meme reseau"). These are shown to students in a
  blocking dialog. Violates the standing accents rule. Same in the
  `MessageTranslationsDialog` fallback list, `events/action_editor.py:1045`
  (`Francais`, `Espanol`, `Portugues`, `Slovenscina`). *Fix:* restore the
  accents (`héberger`, `peut-être déjà utilisé`, `système`, `réseau privé`,
  `Vérifiez`, `l'hôte`, `lancé`, `même réseau`; `Français`, `Español`,
  `Português`, `Slovenščina`).
  **Fixed `0139fbdf`** (also fixed `Russian`/`Ukrainian` → native
  `Русский`/`Українська` in the same fallback list).

- [x] **M13 — Import GMK: `any(candidate.iterdir())` raises when the candidate exists as a file.**
  `core/ide/_assets.py:207` — the "pick a free destination folder" loop
  does `while candidate.exists() and any(candidate.iterdir())`; if
  `~/Documents/PyGameMaker Projects/<name>` exists as a *file* (or is a
  broken junction on the CIFS-mounted Documents seen on the school box)
  `iterdir()` raises `NotADirectoryError`, caught by the outer broad
  except and reported as a generic import failure. *Fix:* `candidate.is_dir()
  and any(...)`, treat a file as occupied.
  **Fixed `db4fd3cf`.**

## Low

- [x] **L1 — `random` module exposed by name in the expression namespace.**
  **Fixed `ce591635`.**
  `runtime/action_executor.py:812` puts `'random': random_module` into
  the eval namespace, so `random.seed(0)` or `random.getstate()` are
  reachable from any expression field (the regex whitelist allows
  `.`, `(`, `)` and digits). Not a sandbox escape (no builtins, no
  strings) — defence-in-depth only; the documented `random()`/`irandom()`/
  `choose()` helpers are what authors should see. *Fix:* expose only the
  helper callables, not the module.

- [x] **L2 — `move_to_contact` loop has no iteration cap.**
  **Fixed `5caed972`.**
  `runtime/action_movement.py:286` steps `max_dist` pixels one at a time;
  an expression yielding a huge/inf `max_dist` (e.g. `1/0` → handled to
  0, but `10**9` isn't) spins the frame. *Fix:* clamp to room diagonal.

- [x] **L3 — Block World: `columns == 0` / `cell_size == 0` division.**
  **Fixed `81f272a4`.**
  `extensions/block_world/state.py:526/536` `cell_of` divides by
  `cell_size`; `renderer.py:994/999/1146` divides by the column count.
  Both come from action parameters / room data with no lower bound;
  `0` → `ZeroDivisionError` → game exits. *Fix:* clamp to `>= 1` at the
  action handler and in `state`.

- [x] **L4 — `separate_overlapping_instances` ignores the parent chain.**
  **Fixed `c06335b2`.**
  `runtime/collision.py:298` matches `object_name` directly whereas every
  other collision path resolves parents (`_object_matches`). A solid
  child object isn't separated. *Fix:* reuse the parent-aware matcher.

- [x] **L5 — `speed` is not derived from `hspeed`/`vspeed`.**
  **Fixed `3c59515f`.**
  `runtime/instance.py` keeps `speed` as a plain attribute set by
  `set_speed`/`set_direction_speed`; after `set_hspeed`/`set_vspeed`,
  `self.speed` in an expression still reports the stale value (GM
  recomputes). Documented in the parser as an expression name. *Fix:* a
  property computing `hypot(hspeed, vspeed)` when not explicitly set, or
  update it in the h/v setters.

- [x] **L6 — Mouse coordinates aren't view-translated in `if_mouse_over`/mouse-position expressions.**
  **Fixed `e80ae45c`.**
  `runtime/action_executor.py:1136` and `runtime/game_runner.py:1882/2231/2413`
  use `pygame.mouse.get_pos()` (screen space) but compare to instance
  room coordinates; in a room with views enabled and the view scrolled,
  `mouse_x`/`mouse_y` and mouse-over tests are off by the view offset.
  *Fix:* add the active view's `x/y` (and scale) once in a helper.

- [ ] **L7 — `find_renamed_asset` matches the category by its translated label.**
  `core/ide/_assets.py:409` compares `category_item.text(0).lower()` with
  `asset_type + 's'`; the category label is a `tr()`'d string (with an
  emoji prefix in some builds), so on any non-English IDE the lookup
  returns `None` and the post-rename tree refresh silently does nothing.
  *Fix:* match on the category item's stored asset type
  (`item.asset_type`), not its text.

- [ ] **L8 — `on_editor_data_modified` identifies the tab by bare title.**
  `core/ide/_editor_lifecycle.py:678` marks the first tab whose
  `tabText(i) == asset_name`; tabs are titled with the bare asset name
  (`:166/273/333`), so a sprite and an object that share a name (`player`
  is common) mark the wrong tab dirty. *Fix:* look the tab up by the
  editor's `_open_editor_key` (`<category>:<name>`) set by L5 (2026-06-15).

- [ ] **L9 — Importing `utils.config` creates `~/.pygamemaker` on the player's machine.**
  `utils/config.py:84/125` `mkdir`s the config dir at import/first
  `get`; the runtime imports it transitively, so every exported game
  drops an IDE config folder in the player's home. *Fix:* lazy-create
  on first *write* only.

- [ ] **L10 — HTML5 export mime sniffing knows only PNG/JPEG.**
  `export/HTML5/html5_exporter.py:887/923` default to `image/png` and
  special-case `.jpg`; `.bmp`/`.webp`/`.tga` (all accepted by the sprite
  importer, `core/asset_manager.py:26`) are embedded with the wrong mime
  and fail to decode in some browsers. *Fix:* `mimetypes.guess_type`
  with a small override table.

- [ ] **L11 — Pyodide offline bundle downloaded without an integrity check.**
  `export/HTML5/pyodide_bundle.py:71` fetches the archive over HTTPS and
  unpacks it; no size cap, no hash pin. A CDN incident ships arbitrary
  JS inside every offline export. *Fix:* pin the SHA-256 per version.

- [ ] **L12 — `GameRoom.parse_color(None)` crashes; `instance_data['x']` KeyError.**
  `runtime/room.py:96` and `:213` — a room JSON with `"background_color":
  null` or an instance missing `x` (hand edit, partial GMK conversion)
  raises at room build rather than defaulting. *Fix:* `.get('x', 0)`,
  `parse_color` returning the default on `None`/non-str.

- [ ] **L13 — Sound combo saves the placeholder as a value.**
  `events/action_editor.py:377` adds the translated
  "(No sounds available)" item when the project has no sounds; OK on the
  dialog saves that literal string as the `sound` parameter. *Fix:* add
  an empty sentinel item like the sprite branch does.

- [ ] **L14 — `_parse_execute_code_actions` rewrites saved data on load.**
  `editors/object_editor/events/_panel.py:627` replaces any
  `execute_code` whose text contains `thymio.` with parsed
  `thymio_*` actions the moment the object is *opened*; the next
  auto-save persists the rewrite. A project whose code merely mentions
  `thymio.` in a comment is mutated without user action. *Fix:* only
  rewrite when the parse is lossless (round-trips to identical code) or
  make it an explicit "Convert" action.

- [ ] **L15 — Object editor validation fails for a floated editor with no reachable IDE data.**
  `editors/object_editor/object_editor_main.py:1045` rejects a sprite
  "that does not exist" whenever `available_sprites` is empty; a floated
  window whose parent chain can't reach the IDE and hasn't received the
  push (`apply_available_sprites`) can't save at all. *Fix:* skip the
  check when the list is empty/unknown.

- [ ] **L16 — Duplicate-asset path doesn't copy room/object/sprite side files.**
  `widgets/asset_tree/asset_operations.py:322` copies `file_path` and
  `thumbnail` only; for manifest-ified rooms/objects the payload lives in
  `<type>/<name>.json`, so the duplicate has the *in-memory* copy only
  until the next full save — and none at all if the tree item's
  `asset_data` was loaded before the side-file merge. *Fix:* copy the
  side file when present.

- [ ] **L17 — Kivy export has no `remember_destroyed` support.**
  `grep remember_destroyed export/Kivy` is empty; an object with the flag
  respawns on room restart on Android/iOS (desktop + HTML5 honour it).
  *Fix:* port the `_destroyed_memory` keyed set to the Kivy `GameApp`.

- [ ] **L18 — `MultiActionEditor` parameter summary leaks nested action lists into the tree text.**
  `events/action_editor.py:919` joins `k=v` for every parameter including
  `then_actions` lists (whole dict reprs, truncated at 50 chars) — cosmetic,
  but makes nested conditionals unreadable in the Then/Else editor.
  *Fix:* use `ActionParametersFormatter` like the main events panel.

- [ ] **L19 — Console `print` in runtime paths bypasses the cp1252-safe logger.**
  Besides M7, `runtime/game_runner.py` `_print_net_status` and the
  `PYGM_FRAMES_COMPLETED` line use plain `print`; ASCII-only today, but
  any future emoji/accent there hits the same crash. *Fix:* route through
  `ConsoleSafeHandler` or keep an explicit ASCII-only comment + test.

- [ ] **L20 — `run_game.py` swallows a wrong `language` silently.**
  `runtime/run_game.py` accepts any second positional as the language
  code; a typo (`--net-host` mis-ordered, or `fr_FR`) yields English
  translations with no message. *Fix:* validate against
  `LanguageManager` codes and warn.

---

## Baseline

Full suite at HEAD `221d1220`, Windows 11, `py -3.12`, run in two halves
(`tests/test_[a-l]*.py` → 3118 passed / 9 skipped in 2:24;
`tests/test_[m-z]*.py` → 1313 passed / 1 skipped in 1:29):
**4431 passed, 10 skipped, 0 failed.** Any non-zero failure count is the
regression signal, not the exact pass number.

## Working the queue

One finding (or one shared-root-cause group) per commit, regression test
in the same commit, checkbox flipped with the hash, pushed to `main`
immediately. Highs first, in order; H3/H4/M1/M8/M9/M10 all live in
`extensions/multiplayer_lan/` and can be batched by file, but each keeps
its own test.
