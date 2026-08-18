# Plan: export-system polish (technical half of Section D)

Status: **not started.** Written 2026-08-18 per `docs/REMAINING_WORK_2026-08-15.md`
Section D, scoped down on explicit instruction to the **purely technical**
items only. Section D's product/business/data-practice items (analytics,
ads, in-app purchases, push notifications, crash reporting, cloud saves)
are deliberately excluded — those are decisions for software used by
children, not engineering tasks, and stay parked until named individually.
Steam/itch.io/console export targets stay "further out still," per the
original doc, and are not sized here.

Investigated against the **current** codebase, post the
`docs/EYEBALL_FIXES_2026-08-16.md` overhaul (now fully closed) — Section D
was written before that overhaul landed, so its framing of "the export
system" is stale in one important way: desktop `.exe`/Linux/macOS exports
now freeze the real, tested `runtime/game_runner.py` via
`export/desktop/pygame_desktop_exporter.py`, not a second hand-written
engine. Nothing below touches engine correctness; this is packaging and
distribution polish on top of an already-correct build.

Three independent areas, one per section: HTML5, Desktop, Kivy/Android.
Nothing here shares code across targets, so these can be picked up in any
order or in parallel across sessions.

---

## 1. HTML5 — external-asset loading, PWA manifest, service worker

### Current state

`export/HTML5/html5_exporter.py` produces **exactly one self-contained
`.html` file**. Every sprite/background/sound is base64-encoded
(`encode_sprites`/`encode_sounds`, lines ~448-551) into the project-data
JSON, which is itself gzip-compressed and base64-encoded again, then
string-substituted into the HTML template alongside `engine.js` and
(optionally) a ~17MB embedded Pyodide runtime. No manifest, no service
worker, no separate asset files exist anywhere in `export/HTML5/` today —
this would be greenfield, not an extension of existing scaffolding.

### The load-bearing constraint this must not break

The single-file shape is a **feature**, not an oversight: a teacher can
email one `.html` file, or drop it on a USB stick, and a student
double-clicks it and plays — no web server, no `file://` CORS problems
(everything is already inline, so there's nothing to `fetch()`). External
assets loaded via `fetch()`/`Image.src`/`Audio.src` from **relative URLs**
do not work when the page is opened via `file://` in most browsers
(blocked by the same-origin policy) — they need real HTTP.

**Decision, not a guess: external-asset loading must be an opt-in
second export mode, default OFF.** The existing single-file inline export
stays the default and is untouched. A new checkbox/option
(`external_assets: bool`, mirroring the existing `offline_pyodide` opt-in
toggle's shape) switches to a **folder** export: `index.html` +
`assets/sprites/*.png` + `assets/sounds/*.ogg` + `engine.js` as a separate
file, all served relative to the HTML. This is for the case Section D's
own item actually describes — a teacher deploying to GitHub Pages or a
school LMS where separate cacheable files and a smaller initial payload
are worth it — not a replacement for the single-file default most
students will still use.

### A real simplification worth knowing before scoping this too big

Browsers treat `data:` URIs and ordinary relative URLs identically via
`img.src = ...` / `new Audio(src)` / `fetch(src)` — the same assignment
works for both. `engine.js`'s asset-loading code path likely does **not**
need to change; only the *string value* baked into `gameData` changes
(a relative path instead of a data URI). This means Phase 2 below is
probably much smaller than "external asset loading" sounds.

### Phase breakdown

1. **Folder-export mode, sprites + backgrounds only.** New
   `external_assets` export option (default `False`). When `True`,
   `HTML5Exporter.export()` writes `output_path/` as a folder: `assets/
   sprites/<name>.<ext>` copied verbatim (no base64), `engine.js` as its
   own file, `index.html` referencing both by relative path.
   `gameData`'s sprite entries become relative paths instead of data
   URIs. Prove byte-for-byte pixel parity against the current inline mode
   for one bundled sample (mirrors this repo's own "prove behaviour-
   preserving" discipline for every prior export change).
2. **Sounds.** Same treatment, `assets/sounds/`. Confirm `Audio.src`
   accepts a relative path with no engine.js change (per the
   simplification above) before writing any new loading code.
3. **A "how to host this" note.** When `external_assets` is chosen, the
   export should write a short `README.txt` alongside `index.html`
   explaining it needs a real web server (even `python -m http.server`
   locally) — `file://` will not work, and that surprise needs to be
   caught before a teacher tries it and gets a blank page.
4. **PWA manifest + service worker (separate, smaller follow-on,
   depends on Phase 1-3 existing first).** A `manifest.json` (name, icons,
   `display: standalone`) and a minimal service worker that caches the
   asset folder for offline replay after the first load. Only meaningful
   for the external-assets folder mode (the single-file mode is already
   fully offline-capable the instant it's downloaded — nothing to add a
   service worker in front of). Icon generation needs a decision: reuse
   the project's own sprite art (which one?) or a generic pygm2 icon —
   flag as an open question when this phase actually starts, don't guess
   now.

Sizing: **small** (Phases 1-3), plus a **small** follow-on for Phase 4.

---

## 2. Desktop (.exe/Linux/macOS) — version-info, code signing, auto-update

Three genuinely different-sized features bundled under one Section D
bullet; sized separately.

### 2a. Version-info embedding — small, concretely buildable now

**Current state**: Windows gets a DPI-awareness manifest and an optional
`.ico` only (`export/exe/exe_exporter.py`) — no `.exe` file-version/
product-version/company metadata (what Explorer's Properties → Details
tab shows) exists anywhere. **A real, adjacent bug**: macOS's
`CFBundleVersion`/`CFBundleShortVersionString` are hardcoded to
`'1.0.0'` (`macos_exporter.py`, `_spec_trailer`) instead of the actual
project version — worth fixing in the same pass, since it's the same
underlying gap (the project's real version never reaches the packaged
binary's own metadata on either platform).

**Plan**: generate a `VSVersionInfo` resource (via
`PyInstaller.utils.win32.versioninfo`, already a PyInstaller dependency —
no new package needed) from the project's name/version, pass it to
`EXE()` as `version=<path>` in `SPEC_TEMPLATE_ONEFILE`/`_ONEDIR` next to
the existing `icon_path` handling in `_spec_exe_options`
(`export/exe/exe_exporter.py`). Fix macOS's hardcoded bundle version to
read from `project_data` in the same commit — it's the identical gap on
the other platform. Linux has no equivalent metadata concept (ELF
binaries don't carry this), so nothing to do there.

**Sizing: small, one session.** No open design questions — this is
filling in a documented-but-never-built gap
(`export/EXPORT_ARCHITECTURE.md` already claims "optional icon and
version info" as if it existed).

### 2b. Code signing — mechanism only; real signing needs the user's own certificate

**Current state**: both spec templates explicitly disable signing
(`codesign_identity=None, entitlements_file=None`) — not a stub to fill
in, a deliberate off-switch. macOS's `_check_xcode_tools` is diagnostic-
only. No Windows `signtool` invocation anywhere.

**Why this can't be fully built without you**: Windows code signing
needs a purchased Authenticode certificate (a recurring cost, typically
hundreds of dollars a year, from a CA); macOS distribution outside the
Mac App Store needs an Apple Developer Program membership ($99/year) plus
a Developer ID Application certificate and **notarization**
(`xcrun notarytool` — submit the signed binary, poll until Apple's
automated scan finishes, staple the ticket to the app). Neither can be
tested, let alone used for real, without those credentials — this is a
cost/account decision, not something to build speculatively.

**Plan (mechanism, not the credential itself)**: add
`signing_identity`/`certificate_path` export options that, when empty
(the default), change nothing — builds stay unsigned exactly as today.
When provided: Windows runs `signtool sign /f <cert> /p <password> /t
<timestamp-url> <exe>` as a post-build step; macOS passes a real
`codesign_identity` into the existing (currently-`None`) spec field, then
runs `xcrun notarytool submit --wait` + `xcrun stapler staple` as
post-build steps. Both are no-ops (skipped, logged) when no credential is
configured, so this ships safely with zero behavior change for every
export that doesn't opt in.

**Sizing: medium** — the mechanism is small, but proving it actually
works needs a real certificate to sign with, which is out of this
session's reach regardless of how it's scoped. Recommend building the
Windows half first if/when picked up (a signing cert is more commonly
available than an Apple notarization workflow) and treating macOS
notarization as its own follow-on.

### 2c. Auto-updater — recommend deferring; weakest-justified item on this list

**What it would need**: a hosted version-check endpoint (e.g. polling
GitHub Releases' API, which means every exported game phones home to
GitHub on launch), a downloaded-update staging mechanism, and — the hard
part on Windows — a running `.exe` cannot overwrite itself, so "auto"
update needs either a separate small updater/launcher binary or a
"download the new version, please restart" prompt that's barely
different from just linking to a download page.

**Why to defer rather than size**: Section D's own wording scopes this to
the **exported student game** (a desktop `.exe` a student built from
their project), not the IDE itself. A one-off classroom project export
phoning home to check for updates is a real complexity/privacy cost
(exactly the kind of "software used by children" concern Section D's
product-decision items were excluded for, even though this one is
nominally "technical") for a use case that doesn't obviously need it —
students don't typically redistribute-and-later-update their own game
exports the way a long-lived deployed application does. If **the IDE
application itself** having an update-check were wanted, that's a
different, separately-scoped feature outside what Section D listed here.
Recommend not sizing this further without a concrete driving scenario.

---

## 3. Kivy/Android — debug vs. release export presets

### Current state

`export/android/android_exporter.py` always runs `buildozer android
debug` (line ~601) — hardcoded, no release path exists. No Android
keystore/signing configuration exists anywhere (`buildspec_generator.py`,
`android_exporter.py`, the buildozer.spec template all confirmed clean of
`keystore`/`release_` references). Notably, **iOS already has the
scaffolding for this same problem** — commented-out `ios.codesign.*`
stanzas in `buildspec_generator.py`/the buildozer.spec template, disabled
via `ios.codesign.allowed = false` — Android has no equivalent, even
disabled.

### What a release build needs, and the one real risk

Android release builds need a **keystore** (a `.jks`/`.keystore` file + a
key alias + two passwords — the store password and the key password).
buildozer/python-for-android already have first-class support for this
via the standard `P4A_RELEASE_KEYSTORE` /
`P4A_RELEASE_KEYSTORE_PASSWD` / `P4A_RELEASE_KEYALIAS` /
`P4A_RELEASE_KEYALIAS_PASSWD` environment variables — pygm2 doesn't need
to reinvent signing, only plumb its own UI through to those.

**The one genuinely consequential risk**: Google Play requires the
**same** keystore for every future update to a given app — lose it, and
that app can never be updated again under the same listing, ever. Any UI
for this needs to say so, in those terms, before generating or accepting
a keystore, matching this repo's own "stop lying to users about
consequences" standing preference. Passwords must never be written to
`project.json` or logged (masked `QLineEdit` input, held only in memory
for the duration of the build subprocess via the env vars above).

### Plan

1. **A `build_type: "debug" | "release"` export option, default
   `"debug"`** — every existing export keeps working exactly as today
   with zero UI change unless release is explicitly chosen. Wire the
   selection into `android_exporter.py`'s buildozer invocation (replacing
   the hardcoded `'debug'` string) and into `buildspec_generator.py`'s
   `android.release_artifact` (APK vs. the newer Play-required AAB format
   — recommend defaulting release builds to AAB, since that's what Play
   Console now requires for new app submissions; keep APK for debug,
   which is what a developer sideloads to test).
2. **Keystore UI.** A dialog offering "use an existing keystore" (browse
   to a `.jks` + enter alias/passwords) or "generate a new one" (runs
   `keytool -genkeypair`, then immediately shows the **"back this up,
   losing it is permanent" warning** named above before the dialog can be
   dismissed). Passwords passed to the buildozer subprocess via the
   `P4A_RELEASE_*` env vars, never persisted.
3. **A release-build regression test** mirroring this repo's own
   established "drive the real exporter, stub what can't run in CI"
   convention — buildozer itself can't execute in CI (matches the
   existing debug-build tests' own limitation), so this proves the
   **generated buildozer.spec and the subprocess command line** are
   correct for a release build, the same tier of proof
   `tests/test_kivy_*.py` already uses elsewhere in this export path.

Sizing: **medium** — buildozer/p4a already solve the hard part
(signing itself); the real work is a correct, honest UI around keystore
handling and wiring the existing env-var contract through.

---

## Suggested order

Independent of each other; pick based on what's actually wanted next.
If forced to rank by (value delivered) / (risk + cost), roughly:

1. **2a — version-info embedding.** Smallest, most concretely buildable,
   fixes a real existing bug (macOS's hardcoded version) along the way.
2. **1 (Phases 1-3) — HTML5 external assets.** Bounded, well-understood
   once the single-file-stays-default decision above is accepted.
3. **3 — Kivy release builds.** Real value for anyone actually
   publishing to Play, but needs the most new UI/UX care (the keystore
   warning).
4. **1 (Phase 4) — PWA manifest/service worker.** Depends on (2).
5. **2b — code signing mechanism.** Buildable any time, but delivers
   nothing until a real certificate exists to use it with.
6. **2c — auto-updater.** Not recommended without a concrete driving
   scenario; revisit only if one shows up.
