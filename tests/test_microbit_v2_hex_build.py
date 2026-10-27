"""The V2 combined hex (docs/MICROBIT_V2_HEX_PLAN.md, unit H3).

Built around the REAL vendored v2.1.2 firmware. With no V2 board and no
reference oracle, the strongest checks are invariants: every byte outside the
file system is the firmware's own, the file system holds exactly the expected
bytes, the script reads back through the device's own algorithm, and the result
is still a valid V2 hex (checksums, ascending addresses, the regions table).
"""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from extensions.microbit.export import hex_build, mpfs  # noqa: E402
from extensions.microbit.export.flash_regions import (  # noqa: E402
    FlashRegionsError, read_flash_regions)
from extensions.microbit.export.intel_hex import MemoryMap, parse_hex  # noqa: E402

V2_HEX = hex_build.V2_FIRMWARE_HEX
SCRIPT = (b"from microbit import *\n\nwhile True:\n    if button_a.was_pressed():\n"
          b"        display.show(Image.HAPPY)\n    sleep(50)\n")

FS_START, FS_END = 0x6D000, 0x73000


@pytest.fixture(scope="module")
def firmware():
    return parse_hex(V2_HEX.read_text(encoding="ascii"))


@pytest.fixture(scope="module")
def built():
    return hex_build.build_v2_hex(SCRIPT)


def _outside_fs(memory):
    """The map with the file system region removed."""
    out = MemoryMap()
    for start, data in memory.segments():
        for lo, hi in ((start, min(start + len(data), FS_START)),
                       (max(start, FS_END), start + len(data))):
            if lo < hi:
                out.set(lo, data[lo - start:hi - start])
    return out


# --- the result is a valid V2 hex -------------------------------------------------------------

def test_the_output_parses_with_strict_checksums_and_ends_with_eof(built):
    lines = built.splitlines()
    assert lines[-1] == ":00000001FF"
    memory, starts = parse_hex(built)                    # raises on any bad checksum
    assert starts == [":0400000320009C51EC"]             # the firmware's own start record kept
    assert lines[-2] == starts[0]


def test_records_are_ascending_and_at_most_16_bytes(built):
    upper, last = 0, -1
    for line in built.splitlines():
        rtype = int(line[7:9], 16)
        if rtype == 4:
            upper = int(line[9:13], 16) << 16
        elif rtype == 0:
            assert int(line[1:3], 16) <= 16
            address = upper + int(line[3:7], 16)
            assert address > last
            last = address


def test_it_is_still_recognised_as_a_v2_micropython_hex(built):
    memory, _ = parse_hex(built)
    regions = read_flash_regions(memory)
    assert (regions.fs_start, regions.fs_end) == (FS_START, FS_END)
    assert regions.runtime_end == 0x68000
    assert regions.micropython_version.startswith("micro:bit v2.1.2")


# --- nothing else changed ----------------------------------------------------------------------

def test_every_byte_outside_the_file_system_is_the_firmwares_own(firmware, built):
    fw_memory, _ = firmware
    out_memory, _ = parse_hex(built)
    assert _outside_fs(out_memory) == _outside_fs(fw_memory)


def test_the_runtime_the_trailing_data_and_the_uicr_are_all_still_there(built):
    memory, _ = parse_hex(built)
    spans = {(s, len(d)) for s, d in memory.segments()}
    assert (0x00000, 2816) in spans and (0x01000, 107520) in spans
    assert any(s == 0x1C000 for s, _ in spans)
    assert any(s == 0x77000 for s, _ in spans)           # data past the file system
    assert any(s == 0x7E000 for s, _ in spans)
    assert (0x10001014, 8) in spans                       # the UICR block


def test_the_file_system_region_holds_exactly_the_expected_bytes(firmware, built):
    out_memory, _ = parse_hex(built)
    inside = out_memory.slice(FS_START, FS_END)
    expected = MemoryMap()
    mpfs_layout = mpfs.FsLayout(FS_START, FS_END, 4096)
    mpfs.add_file(expected, mpfs_layout, "main.py", SCRIPT)
    assert inside == expected
    # concretely: a ~130-byte script is one chunk at the region start + the marker
    assert [(s, len(d)) for s, d in inside.segments()] == [(0x6D000, 128), (0x72000, 1)]
    assert out_memory.get(0x72000, 1) == b"\xfd"


def test_the_stock_firmware_file_system_was_empty(firmware):
    fw_memory, _ = firmware
    assert len(fw_memory.slice(FS_START, FS_END)) == 0


# --- the script reads back ----------------------------------------------------------------------

def test_the_script_reads_back_through_the_devices_own_algorithm(built):
    assert hex_build.extract_v2_script(built) == SCRIPT
    memory, _ = parse_hex(built)
    layout = mpfs.layout_from_regions(read_flash_regions(memory))
    assert mpfs.read_files(memory, layout) == {"main.py": SCRIPT}


@pytest.mark.parametrize("size", [1, 117, 118, 125, 126, 127, 1000, 5000])
def test_scripts_of_many_sizes_round_trip(size):
    script = bytes((i * 13 + 5) & 0xFF for i in range(size))
    assert hex_build.extract_v2_script(hex_build.build_v2_hex(script)) == script


def test_building_is_deterministic_and_independent_of_the_cache(built):
    assert hex_build.build_v2_hex(SCRIPT) == built
    again = hex_build.build_v2_hex(SCRIPT, firmware_hex=V2_HEX.read_text(encoding="ascii"))
    assert again == built


def test_building_does_not_disturb_the_cached_firmware():
    hex_build.build_v2_hex(b"a=1\n")
    memory, _, layout = hex_build._v2_firmware()
    assert len(memory.slice(layout.start, layout.end)) == 0


# --- limits and errors ---------------------------------------------------------------------------

def test_the_documented_maximum_builds_and_one_more_byte_is_refused():
    limit = hex_build.v2_max_script_size()
    assert limit == 20150
    biggest = hex_build.build_v2_hex(bytes(limit))
    assert len(hex_build.extract_v2_script(biggest)) == limit
    with pytest.raises(hex_build.ScriptTooLargeError, match=r"20151 bytes.*20150"):
        hex_build.build_v2_hex(bytes(limit + 1))


def test_an_empty_script_is_refused():
    with pytest.raises(ValueError, match="empty"):
        hex_build.build_v2_hex(b"")


def test_the_v1_firmware_is_refused_as_not_a_v2_hex():
    v1 = hex_build.V1_FIRMWARE_HEX.read_text(encoding="ascii")
    with pytest.raises(FlashRegionsError, match="not a micro:bit V2"):
        hex_build.build_v2_hex(SCRIPT, firmware_hex=v1)


def test_a_hex_without_a_main_py_cannot_be_extracted():
    plain = V2_HEX.read_text(encoding="ascii")
    with pytest.raises(ValueError, match="No main.py"):
        hex_build.extract_v2_script(plain)


def test_extracting_from_a_v1_hex_is_refused_too():
    with pytest.raises(FlashRegionsError):
        hex_build.extract_v2_script(hex_build.V1_FIRMWARE_HEX.read_text(encoding="ascii"))


# --- the file-based wrapper and the V1 path stay intact -------------------------------------------

def test_build_v2_combined_hex_writes_the_same_text(tmp_path):
    main_py = tmp_path / "main.py"
    main_py.write_bytes(SCRIPT)
    out = tmp_path / "main.hex"
    hex_build.build_v2_combined_hex(main_py, out)
    assert out.read_text(encoding="utf-8") == hex_build.build_v2_hex(SCRIPT)


def test_the_v1_builder_is_unchanged_by_the_new_code(tmp_path):
    out = tmp_path / "v1.hex"
    main_py = tmp_path / "main.py"
    main_py.write_bytes(b"print(1)\n")
    hex_build.build_v1_combined_hex(main_py, out)
    assert hex_build.extract_script(out.read_text(encoding="utf-8")) == b"print(1)\n"


# --- the real exporter's output ---------------------------------------------------------------------

def test_the_real_microbit_1_program_builds_into_a_v2_hex_and_reads_back(tmp_path):
    from extensions.microbit.export.micropython_exporter import MicropythonExporter
    project = REPO_ROOT / "samples" / "microbit_1" / "project.json"
    exporter = MicropythonExporter()
    assert exporter.export(str(project), str(tmp_path), "v2")
    main_py = Path(next(iter(exporter.exported_files.values())))
    script = main_py.read_bytes()
    assert 0 < len(script) <= hex_build.v2_max_script_size()
    out = hex_build.build_v2_hex(script)
    assert hex_build.extract_v2_script(out) == script
    memory, _ = parse_hex(out)
    # and the file system region holds more than one chunk for a program this size
    assert len(memory.slice(FS_START, FS_END)) > 128
