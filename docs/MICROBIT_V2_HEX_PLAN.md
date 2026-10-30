# micro:bit extension -- V2 combined `.hex` and the Universal Hex

Written 2026-10-27. Status: **done, same day (H0-H7)** -- verified against the real
firmware and by independent checks, **not on a real board**.
Picks up the two items `docs/MICROBIT_STAGE_X_PLAN.md` (X8) left open and
`TODO.md` lists: a ready-to-flash `.hex` for a **V2** board, and a single file
for **both** board versions (the "Universal Hex"). Work the units in order, one
unit per commit (code + tests + verification), push after each, tick the box
with the commit hash -- the same discipline as Stages S and X.

## Goal

From the File menu's "Export micro:bit (MicroPython) code...", a teacher can
build one `.hex` that a student drags onto a **factory-fresh** board's MICROBIT
USB drive and the program runs -- with no MicroPython flashed beforehand:

1. for a V2 board (this plan's first half, H1-H4);
2. for either board, one file (the second half, H5-H6).

V1 already works (`extensions/microbit/export/hex_build.py`, X8) and is not
touched here except to be combined.

## What the research found (corrects the X8 notes)

Read from the MIT-licensed reference implementation `microbit-foundation/
microbit-fs` (`src/micropython-fs-builder.ts`, `flash-regions.ts`), then
**measured on the real firmware** (`micropython-microbit-v2.1.2.hex`, the latest
V2 release, MIT, 1,239,726 bytes of text):

- **The V2 filesystem is NOT littlefs.** X8's notes called it "littlefs-style,
  multi-file"; that was wrong. V1 and V2 use the **same** chunk filesystem
  (MicroPython's `filesystem.c`): a doubly-linked list of **128-byte chunks**,
  each with a 1-byte head marker and a 1-byte tail pointer (126 data bytes), the
  first chunk of a file marked `0xFE` and carrying the file name and the data end
  offset. `0xFF` is an unused chunk, `0x00` a freed one, `0xFD` marks the
  "persistent data" page. What differs is only **where** the filesystem is.
- **V2 says where in a table, not at a fixed address.** The firmware ends its
  last page with a Flash Regions Table: 16-byte rows (id, hash type, first page,
  length, hash data) then a 16-byte header (`0x597f30fe` ... `0xc1b1d79d`, version,
  table length, region count, log2 of the page size). Region id 3 is the
  filesystem. On v2.1.2: **pages 109-114, `0x6D000` to `0x73000`, 24,576 bytes**,
  empty (no data) in the stock hex; the MicroPython runtime region ends at
  `0x68000`; the hex also has data at `0x77000` and `0x7E000` and a UICR block at
  `0x10001014`, all of which must survive.
- **That is why V1's trick doesn't carry over:** V1 appends one script at a fixed
  address (`0x3E000`) *below* the firmware's flash end; V2's firmware already
  reaches `0x68000`, and the filesystem lives in a table-described region.
- **Capacity:** the last filesystem page is the persistent-data page, so 5 pages
  = 160 chunks = about 20 KB of file data (less headers). A `main.py` beyond that
  is refused with a clear message, not truncated.
- **The Universal Hex is a separate, pure transform** (`microbit-universal-hex`,
  MIT; the spec text is CC-BY-SA-4.0, so it is cited and not copied): take each
  board's finished single-board hex and re-pack it into 512-byte blocks
  delimited by custom record types (0x0A block start / 0x0B block end / 0x0C
  padded data / 0x0D custom data / 0x0E other data) tagged with a board id
  (`0x9900` V1, `0x9903` V2). Neither board's builder needs to know about it.

## Design decisions

- **Inside the extension**, `extensions/microbit/export/`, zero core changes
  (same rule as X). New modules, each pure (bytes/str in, bytes/str out, no Qt,
  no pygame, no device):
  `intel_hex.py` (parse / emit), `flash_regions.py` (find the table, read the
  regions), `mpfs.py` (the chunk filesystem: build and read), `universal_hex.py`
  (H5). `hex_build.py` gains `build_v2_hex(main_py)` and `build_universal_hex`.
- **Vendor v2.1.2**, like V1: committed under `export/firmware/`, marked
  `binary` in `.gitattributes`, SHA-256
  `66fae07b71777e9e3a6b5122a27930b24cc0be5002ab9a67e92494c54a1645ef` recorded in
  `THIRD_PARTY_LICENSES.md` with the MIT notice. (It is 1.2 MB of text; the V1 one
  was 0.6 MB.)
- **Build by parse -> memory map -> add the file -> re-emit**, as the reference
  does, rather than splicing text: the filesystem sits *between* the runtime and
  later data, so records must come out in ascending address order. Output uses
  16-byte data records and extended-linear-address records; the firmware's own
  start-address record and the end-of-file record are kept.
- **File name is `main.py`**, one file. Errors are typed (`ScriptTooLargeError`
  reused) and messages say what to do.
- **The export dialog** already asks V1 or V2 (O6); the "build a ready-to-flash
  .hex" offer, today V1-only, learns V2, and gains a "both boards" choice at H6.

## How it is verified (and what is NOT)

No V2 board is available, and a **reference oracle could not be run**: executing
the JavaScript `microbit-fs` library needs a downloaded Node binary and npm
packages, which this environment's safety classifier refused to run. So the
builder is written from the library's documented source and checked by:

1. **Real firmware, measured:** the table parser must reproduce the numbers above
   from the actual v2.1.2 file (a test reads the vendored hex).
2. **A hand-derived known-answer vector:** the exact bytes of a tiny `main.py`'s
   chunk(s), worked out by hand from the documented layout and written into the
   test as literals, independent of the builder's code.
3. **An independent reader** (`mpfs.read_files`) that follows the device's own
   algorithm (find `0xFE` chunks, follow tail pointers, check back-links, trim by
   the end offset); build -> read round-trips for sizes at every boundary (0, 1,
   125, 126, 127, many chunks, the maximum, one past it).
4. **Invariants on the real firmware:** every byte outside the filesystem region
   is identical before and after; the persistent marker is exactly where the
   layout says; checksums valid; addresses ascending; the data past the
   filesystem (`0x77000`, UICR) is still there.
5. **Universal Hex:** a separator (the inverse) recovers each board's records
   exactly; every block is exactly 512 bytes long; both boards' data is present
   and tagged.

**Still needs a real board, and says so:** that a built V2 `.hex` boots and runs
a program, that a Universal Hex flashes on both a V1 and a V2, and that the
cross-check against the reference library (if someone with Node runs it) agrees.
These go in `docs/RELEASE_QA_CHECKLIST.md` s11a.

## Units

| Unit | What | Done |
|---|---|---|
| H0 | Commit this plan. | [x] `3d0d0982` |
| H1 | Vendor the V2 v2.1.2 firmware (+ licence/SHA-256, `.gitattributes`); `intel_hex.py` (parse to a sparse memory map, emit ascending 16-byte records with extended-address records) and `flash_regions.py` (find the table, read the regions). Tests: round-trip a real hex; the parser reports the measured v2.1.2 numbers. | [x] `8e470a06` |
| H2 | `mpfs.py`: the chunk filesystem builder and independent reader, generic over (start, end, page size). Hand-derived known-answer vector, boundary round-trips, error cases (name too long, empty file, no space). | [x] `d8408be1` |
| H3 | `build_v2_hex(main_py)`: firmware + filesystem -> one hex. Tests on the real firmware (invariants above), the too-large error, determinism. | [x] `ac44e8ab` |
| H4 | Wire V2 into the export flow: the "ready-to-flash .hex" offer for a V2 choice; typed errors become dialogs; tests with the dialogs mocked, extending X8's. | [x] `122dfe89` |
| H5 | `universal_hex.py`: port `iHexToCustomFormatBlocks` / `createUniversalHex` / `separateUniversalHex` (MIT, attributed). Tests: 512-byte blocks, board-id tagging, separator round-trip, V1-style data-record handling. | [x] `99116626` |
| H6 | `build_universal_hex(main_py)` (V1 hex + V2 hex -> one) and the "both boards" option in the export dialog; tests. | [x] `b997fd15` |
| H7 | Close-out: extension README, plan/TODO/CLAUDE notes, QA checklist rows, `THIRD_PARTY_LICENSES.md`. | [x] `4cced0c8` |

## Result (2026-10-27)

- `extensions/microbit/export/`: `intel_hex.py` (sparse memory map, strict
  parse/emit), `flash_regions.py` (the V2 regions table), `mpfs.py` (the chunk
  file system, build + read), `universal_hex.py` (the "sections" format), and in
  `hex_build.py`: `build_v2_hex`, `build_universal_hex`, their file helpers,
  `extract_v2_script`, and the limits (`v1_max_script_size()` 8,187,
  `v2_max_script_size()` 20,150, `universal_max_script_size()` 8,187).
- The export dialog's version question has a third choice, "Both (one .hex for V1
  and V2 boards)": it exports under V1's rules (the program must run on the older
  board) and offers the Universal Hex; V2 alone now also gets a ready-to-flash hex.
- ~300 new tests across `test_microbit_{intel_hex,flash_regions,mpfs,
  v2_hex_build,universal_hex,universal_build}.py` plus the extended dialog tests.
  Mutation-checked throughout, and **one mutation "passed" the first time because
  the sed that applied it silently matched nothing** -- re-done with the
  mutation verified as applied (a "no failures" mutation run proves nothing until
  you've confirmed the file really changed).
- **Corrects the earlier notes:** the V2 file system is NOT littlefs-style (X8's
  O5 write-up said so; the reference source says otherwise and the real firmware
  confirms it): same chunk file system as V1, found through a table.

## Still open

- **A real board.** That a built V2 `.hex` boots and runs, and that a Universal Hex
  flashes on both a V1 and a V2, is untested -- `docs/RELEASE_QA_CHECKLIST.md` s11a.
- **Running the JavaScript reference itself** (`microbit-fs` over our firmware and script, diffing the
  file-system region) was refused twice by the environment (it will not run a downloaded Node binary) and
  was replaced on 2026-10-30 by a stronger, offline set of checks that needs no third-party code to run:
  - the file-system **chunk format** equals bytes the reference spec says it captured from a *real
    micro:bit* (a file that exactly fills a chunk, one byte short, one over, a 10-chunk file, files at
    scattered chunk positions), in both directions: `tests/test_microbit_mpfs_hardware_vectors.py`;
  - `create_universal_hex` equals the reference's own golden Universal Hex **byte for byte** (844,812
    characters, real MakeCode hexes) and `separate_universal_hex` returns what its tests expect;
  - `read_flash_regions` reads the reference's V2 firmware fixture exactly as its spec expects;
  - the last two: `tools/verify_microbit_hex_against_reference.py` (network, 11 assertions, pinned commits +
    SHA-256, all equal).
  What is *not* covered: our own V2 v2.1.2 firmware has no golden output to diff against, so the end-to-end
  `.hex` is still untried on a board (above).
- ~~The older Universal Hex **"blocks"** layout~~ -- done 2026-10-30: `hex_to_blocks` /
  `create_universal_hex(blocks=True)`, equal to the reference's golden blocks file byte for byte (the last block
  of the whole file is left unpadded, as there; every other block is exactly 512 characters).
  `tests/test_microbit_universal_blocks.py`. Not offered in the export dialog: the sections layout stays the
  default (the specification's recommendation), and nothing needs blocks unless a real board proves it does.
- ~~The Stage X dialog strings are untranslated~~ -- done: all 36 strings are in the
  `PyGameMakerIDE` context of the 10 shipped languages, pinned by
  `tests/test_microbit_export_ui_translations.py`.

## Expected size

H1 and H2 are the substance; H3-H4 are short once those exist; H5 is a faithful
port of about 450 lines of TypeScript; H6-H7 are short.
