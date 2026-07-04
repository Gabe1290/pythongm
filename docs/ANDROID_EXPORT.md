# Exporting a game to Android (.apk)

How to turn a pygm2 project into an installable Android app, what the
build actually does, how long it takes, and how it behaves in a
classroom setting (shared machines, sessions that end before the build
is finished).

## Where the option is

**Build → Export Game…** then pick **Android Package (.apk)** in the
dialog and choose an output folder. The APK lands in that folder when
the build finishes.

Under the hood the IDE converts the project to a [Kivy](https://kivy.org)
app (`export/Kivy/`), writes a `buildozer.spec`, and drives
[buildozer](https://buildozer.readthedocs.io) /
python-for-android, which cross-compiles Python, SDL2, and Kivy for ARM
and packages everything into a debug-signed `.apk`.

## Requirements

### Linux (the typical classroom machine)

Buildozer runs natively. One-time setup per machine/user:

```bash
sudo apt install openjdk-17-jdk build-essential autoconf automake \
     libtool pkg-config cmake zip unzip git python3-dev libffi-dev libssl-dev
pip3 install --user buildozer 'cython<3.0'
```

Internet access is required for the **first** build (Android SDK/NDK
download, ~2 GB).

### Windows

Buildozer does not run on Windows; the IDE drives it through **WSL 2**.
Install WSL once (`wsl --install` in an admin PowerShell, then reboot
and create the Linux user). On the first Android export the IDE
installs the Linux-side dependencies into WSL automatically.

### macOS

`brew install openjdk@17` plus `pip3 install --user buildozer 'cython<3.0'`.

## How long it takes — and why

| Build | Duration | What happens |
| ----- | -------- | ------------ |
| First build ever | **40–90 minutes** | downloads the Android SDK/NDK (~2 GB), then cross-compiles CPython, SDL2, Kivy, Pillow… for two ARM architectures |
| Rebuild of the same project | **a few minutes** | only the game files changed; the compiled toolchain and gradle caches are reused |
| First build of a *second* project | **~10–40 minutes** | the SDK/NDK are shared, but each project compiles its own python-for-android distribution |

The progress dialog stays informative throughout; the export has a
3-hour hang failsafe (2 h on native Linux), far above any healthy build
time — if it triggers, something is genuinely stuck (network, disk
full), not merely slow.

## Where the build state lives (the caching story)

Everything persistent is in the **user's home directory** (inside WSL on
Windows):

| Location | Contents | Shared |
| -------- | -------- | ------ |
| `~/.buildozer/` | Android SDK, NDK, platform tools (~2 GB) | by all projects of this user |
| `~/pygm_builds/<project>/` | the project's build workspace: compiled python-for-android distribution, gradle caches (~5–6 GB) | per project |
| your chosen export folder | the final `.apk` | — |

The `~/pygm_builds` path is deliberately **not** a hidden (dot) folder:
buildozer silently skips source files under any path containing a
dot-prefixed directory, so don't move the workspace under one.

Mind the disk quota on school machines: one student building one game
uses roughly **8 GB** of home-directory space.

## Interrupted builds, ended sessions, "can we continue next week?"

**Yes — provided the user's home directory persists between sessions.**
All build state (SDK/NDK and the per-project workspace) lives in the
home directory, so logging out, shutting the machine down, or simply
running out of lesson time loses nothing. A week later, the same user on
the same account re-runs **Build → Export Game… → Android Package**:

- if the previous build finished the toolchain compile, the rebuild
  takes minutes;
- if the previous build was interrupted mid-compile, python-for-android
  resumes at the level of completed recipes (finished components are
  not recompiled), so the work done so far is kept.

The build is **not** a background job — closing the IDE or the session
stops it — but re-launching the export continues from the cache rather
than starting over.

Two classroom caveats:

1. **Ephemeral profiles lose everything.** If the machines reset user
   accounts on logout (guest sessions, disk-freeze software, wiped
   `/home`), every build is a first build (40–90 min). For APK work you
   need persistent per-student accounts (local or network home
   directories both work, though NFS homes build noticeably slower).
2. **Caches cannot be copied between users.** The build workspace
   embeds absolute paths (`/home/<user>/…`) in its compiled artifacts
   and metadata, so seeding `alice`'s cache from `bob`'s home (or from a
   teacher image with a different home path) breaks the packaging step.
   Same user + same home path = safe; anything else = let it build
   fresh.

## Installing the APK

The produced file is a **debug-signed** APK — ideal for the classroom,
not accepted by the Play Store. To install:

- copy it to the device (USB, web share…) and open it — Android will
  ask to allow installing from unknown sources; or
- with USB debugging enabled: `adb install <game>.apk`.

## What games export well

Sprite/action games and draw-queue + mouse/touch games (like the
bundled `match3_1` sample) are supported: taps are delivered as the
left-mouse-press event and draw-queue rendering works. Remaining
limitations (right/middle mouse, a few draw-queue command types,
`execute_code` environment differences) are listed under
"Kivy/Android export" in `TODO.md`.

## Troubleshooting

- **"Requires WSL (not detected)" (Windows)** — install WSL 2 and try
  again; the radio button label tells you what the IDE detected.
- **Timeout message** — the failsafe fired. Check network and free disk
  space (`df -h` / the Windows drive hosting WSL), then re-run: the
  build resumes from cache.
- **Build fails immediately on Linux** — usually a missing system
  package; the error dialog lists the `apt install` line to run.
- **Where are the logs?** The export dialog streams buildozer's output;
  for a full log re-run the export with "Include Debug Info" checked so
  the temporary build directory is kept.
