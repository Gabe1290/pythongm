#!/usr/bin/env python3
"""Check our micro:bit hex code against the reference libraries' own test files (needs the network).

``extensions/microbit/export/universal_hex.py`` and ``flash_regions.py`` are ports of
microbit-foundation/microbit-universal-hex and microbit-fs (both MIT). Those repositories ship real firmware
and MakeCode hex files and the outputs their own libraries produced, and their test suites assert exact
equality with them. This tool downloads those fixtures (about 5 MB; each pinned to one commit and checked
against SHA-256) and makes the same assertions of OUR code (nothing of theirs is executed):

1. ``create_universal_hex([(0x9901, duck-32), (0x9903, ghost-32)])``  ==  the golden *sections* file.
2. ``create_universal_hex([(0x9901, duck-16), (0x9903, ghost-16)], blocks=True)``  ==  the golden *blocks* file.
3. ``separate_universal_hex`` of each golden file gives back the hexes the reference's own tests expect.
4. ``read_flash_regions`` of the reference's V2 firmware fixture finds what its flash-regions spec expects
   (page size, file-system start/end, runtime end, MicroPython version).

The file-system chunk format itself is checked, without the network, against bytes the reference spec says it
captured from a real micro:bit: tests/test_microbit_mpfs_hardware_vectors.py.

Run:  ``py -3.12 tools/verify_microbit_hex_against_reference.py``   (exit 0 = all equal).
Result on 2026-10-30: all equal. The fixtures are too large to commit; the properties are pinned
on small data by tests/test_microbit_universal_blocks.py and tests/test_microbit_universal_hex.py.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extensions.microbit.export import universal_hex as uh  # noqa: E402

COMMIT = "e108bfadcf04bde8634e282197a37c910db50fe5"            # microbit-universal-hex
BASE = f"https://raw.githubusercontent.com/microbit-foundation/microbit-universal-hex/{COMMIT}/src/__tests__/hex-files/"
FS_COMMIT = "c4f74269063a7372f8fe6ef3839539aeda612632"         # microbit-fs
FS_URL = (f"https://raw.githubusercontent.com/microbit-foundation/microbit-fs/{FS_COMMIT}"
          "/src/__tests__/upy-v2-beta-region.hex")
FS_SHA256 = "a4be3a115e5a2535a849a03e95260c83438ce7634090df504656b61621478b14"
SHA256 = {
    "1-duck-umbrella-16.hex": "60fc62bb0c570b083308575cd461d78c4fce4bba4eef690fb8171cea60822f65",
    "2-ghost-music-16.hex": "23e32e39296ce46b4767b648a87a48a2cbe6145db664d966d351b84d117ae6c8",
    "1-duck-umbrella-32.hex": "6ae1cc560f02d36d33d031f7aab7a7e42944317090f154caa1d6cba17a2c9b12",
    "2-ghost-music-32.hex": "ae481179ca5176b2abd28a6ecde6b7881dae8e7390f6ce722662f581974999a7",
    "combined-16-blocks-1-9901-2-9903.hex": "110bcf2d75a66509415c95648b5bff918274c350c44c29dcbf9998c9057ad656",
    "combined-32-sections-1-9901-2-9903.hex": "b967106749cedda1100edbea227f956af7238b874cdd3cf0a3ac472e7735787f",
}


def _download(url, pinned, label):
    data = urllib.request.urlopen(url, timeout=120).read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != pinned:
        sys.exit(f"{label}: SHA-256 {digest} is not the pinned {pinned} (did the upstream file change?)")
    return data.decode("utf-8")


def fetch(name):
    return _download(BASE + name, SHA256[name], name)


def first_difference(ours, want):
    for i, (a, b) in enumerate(zip(ours.split("\n"), want.split("\n"))):
        if a != b:
            return f"first difference at line {i}:\n   ours: {a}\n   want: {b}"
    return f"one is a prefix of the other ({len(ours)} vs {len(want)} characters)"


def main():
    files = {name: fetch(name) for name in SHA256}
    duck16, ghost16 = files["1-duck-umbrella-16.hex"], files["2-ghost-music-16.hex"]
    duck32, ghost32 = files["1-duck-umbrella-32.hex"], files["2-ghost-music-32.hex"]
    golden_blocks = files["combined-16-blocks-1-9901-2-9903.hex"]
    golden_sections = files["combined-32-sections-1-9901-2-9903.hex"]
    results = []

    def check(label, ours, want):
        ok = ours == want
        results.append(ok)
        text = isinstance(ours, str) and isinstance(want, str)
        size = f"  ({len(ours):,} / {len(want):,} characters)" if text and len(want) > 60 else ""
        print(("EQUAL     " if ok else "DIFFERENT ") + label + size)
        if not ok:
            print("   " + (first_difference(ours, want) if text else f"ours {ours!r}, want {want!r}"))

    check("sections: create_universal_hex == the golden sections file",
          uh.create_universal_hex([(0x9901, duck32), (0x9903, ghost32)]), golden_sections)
    check("blocks:   create_universal_hex(blocks=True) == the golden blocks file",
          uh.create_universal_hex([(0x9901, duck16), (0x9903, ghost16)], blocks=True), golden_blocks)

    # what the reference's own tests expect from separateUniversalHex on each golden file
    sep_sections = uh.separate_universal_hex(golden_sections)
    sep_blocks = uh.separate_universal_hex(golden_blocks)
    check("separate(sections)[0] == duck-32", sep_sections[0][1], duck32)
    check("separate(sections)[1] == ghost-32 (no start-address record, opening ELA added)",
          sep_sections[1][1], ":020000040000FA\n" + ghost32.replace(":040000050000FA55A8\n", ""))
    check("separate(blocks)[0] == duck-16", sep_blocks[0][1], duck16)
    check("separate(blocks)[1] == ghost-16 (opening ELA added)", sep_blocks[1][1], ":020000040000FA\n" + ghost16)
    check("board ids read from both files", repr([hex(b) for b, _ in sep_sections + sep_blocks]),
          repr(["0x9901", "0x9903", "0x9901", "0x9903"]))
    # the V2 firmware fixture and the values microbit-fs's flash-regions.spec.ts expects of it
    from extensions.microbit.export.flash_regions import read_flash_regions
    from extensions.microbit.export.intel_hex import parse_hex
    regions = read_flash_regions(parse_hex(_download(FS_URL, FS_SHA256, "upy-v2-beta-region.hex"))[0])
    runtime_end_page = -(-0x61F24 // 4096)                      # the spec: the last byte MicroPython uses
    check("flash regions: page size 4096", regions.page_size, 4096)
    check("flash regions: file system 0x6D000..0x73000", (regions.fs_start, regions.fs_end), (0x6D000, 0x73000))
    check("flash regions: runtime ends on the page after MicroPython's last byte", regions.runtime_end,
          runtime_end_page * 4096)
    check("flash regions: MicroPython version string", regions.micropython_version,
          "micro:bit v2.0.99+b260810 on 2020-11-17; MicroPython b260810 on 2020-11-17")
    print("\n%d of %d equal" % (sum(results), len(results)))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
