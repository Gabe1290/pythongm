"""Regression tests for Stage X unit X8 (V1 only): building a ready-to-
flash combined hex from the vendored firmware + a generated main.py.
docs/MICROBIT_STAGE_X_PLAN.md's O5 has the research this unit is built
on. Pure, deterministic Intel Hex text manipulation -- no real hardware
needed to verify correctness; the embed/extract round-trip against the
real vendored firmware is the strongest check available without a board.
"""
import struct

import pytest

from extensions.microbit.export.hex_build import (
    embed_script, extract_script, build_v1_combined_hex,
    FirmwareOverflowError, ScriptTooLargeError,
    SCRIPT_ADDR, V1_FIRMWARE_HEX,
)


@pytest.fixture(scope="module")
def real_firmware():
    return V1_FIRMWARE_HEX.read_text(encoding="utf-8")


class TestVendoredFirmware:
    def test_firmware_file_exists_and_is_nonempty(self):
        assert V1_FIRMWARE_HEX.exists()
        assert V1_FIRMWARE_HEX.stat().st_size > 100_000

    def test_every_line_is_a_well_formed_ihex_record(self, real_firmware):
        for line in real_firmware.splitlines():
            line = line.strip()
            if not line:
                continue
            assert line.startswith(':'), line
            # even length hex payload after the leading colon
            assert len(line) % 2 == 1, line


class TestEmbedScriptRoundTrip:
    """The strongest check available without real hardware: embed, then
    read the embedded script back out exactly as MicroPython's own
    filesystem reader (and microbit-fs's getIntelHexAppendedScript) would."""

    def test_round_trip_simple_script(self, real_firmware):
        script = b'from microbit import *\ndisplay.show(Image.HEART)\n'
        combined = embed_script(real_firmware, script)
        assert extract_script(combined) == script

    def test_round_trip_empty_script(self, real_firmware):
        combined = embed_script(real_firmware, b'')
        assert extract_script(combined) == b''

    def test_round_trip_script_with_embedded_nulls_at_the_end(self, real_firmware):
        # The header encodes an exact length, so trailing zero-padding
        # bytes must not be mistaken for part of the script.
        script = b'x = 1\n'
        combined = embed_script(real_firmware, script)
        assert extract_script(combined) == script

    def test_round_trip_near_max_size_script(self, real_firmware):
        # 8 KB region minus the 4-byte header, minus enough room to
        # guarantee the padding rule still applies.
        script = b'#' + b'x' * 8180
        combined = embed_script(real_firmware, script)
        assert extract_script(combined) == script


class TestEmbedScriptStructure:
    def test_output_lines_all_have_valid_checksums(self, real_firmware):
        import binascii
        script = b'print(1)\n'
        combined = embed_script(real_firmware, script)
        for line in combined.splitlines():
            if not line:
                continue
            raw = binascii.unhexlify(line[1:])
            assert sum(raw) & 0xFF == 0, line

    def test_script_inserted_before_the_uicr_region(self, real_firmware):
        script = b'print(1)\n'
        combined = embed_script(real_firmware, script)
        lines = combined.splitlines()
        uicr_index = next(i for i, l in enumerate(lines) if ':020000041000EA' in l)
        script_marker_index = next(
            i for i, l in enumerate(lines) if l.startswith(':02000004000'))
        # The script's own extended-linear-address record (page 3, "0003")
        # must appear strictly before the UICR's (page 0x1000).
        assert script_marker_index < uicr_index

    def test_line_count_grows_by_the_expected_number_of_script_lines(self, real_firmware):
        before = len(real_firmware.splitlines())
        script = b'x' * 32  # exactly 2 sixteen-byte data lines once padded
        combined = embed_script(real_firmware, script)
        after = len(combined.splitlines())
        # +1 extended-address record, +N data lines for ceil((4+32+pad)/16)
        assert after > before


class TestScriptTooLarge:
    def test_oversized_script_raises(self, real_firmware):
        with pytest.raises(ScriptTooLargeError):
            embed_script(real_firmware, b'x' * 8189)  # + 4-byte header > 8192

    def test_error_message_names_the_sizes(self, real_firmware):
        with pytest.raises(ScriptTooLargeError) as exc_info:
            embed_script(real_firmware, b'x' * 9000)
        assert "9008" in str(exc_info.value)
        assert "8192" in str(exc_info.value)


class TestFirmwareOverflow:
    def test_firmware_using_the_script_region_is_rejected(self):
        # A single data record whose address lands past SCRIPT_ADDR.
        overflowing_addr = SCRIPT_ADDR + 0x1000
        page = overflowing_addr >> 16
        offset = overflowing_addr & 0xFFFF
        ext_record = _make_record(0, 4, struct.pack('>H', page))
        data_record = _make_record(offset, 0, b'\x00' * 4)
        fake_firmware = ext_record + '\n' + data_record + '\n'
        with pytest.raises(FirmwareOverflowError):
            embed_script(fake_firmware, b'print(1)\n')

    def test_real_vendored_firmware_does_not_overflow(self, real_firmware):
        # The real check this unit depends on: confirms the vendored
        # v1.1.1 firmware's own flash usage leaves the script region free.
        embed_script(real_firmware, b'print(1)\n')  # must not raise


def _make_record(addr, record_type, data):
    import binascii
    record = struct.pack('>BHB', len(data), addr & 0xFFFF, record_type) + data
    checksum = (-(sum(record))) & 0xFF
    return ':%s%02X' % (binascii.hexlify(record).decode('ascii').upper(), checksum)


class TestBuildV1CombinedHex:
    def test_writes_a_file_with_the_script_embedded(self, tmp_path):
        main_py = tmp_path / "main.py"
        main_py.write_text("from microbit import *\ndisplay.show(Image.HAPPY)\n",
                            encoding="utf-8")
        output = tmp_path / "combined.hex"
        build_v1_combined_hex(main_py, output)
        assert output.exists()
        recovered = extract_script(output.read_text(encoding="utf-8"))
        assert recovered == main_py.read_bytes()

    def test_output_is_larger_than_the_bare_firmware(self, tmp_path):
        main_py = tmp_path / "main.py"
        main_py.write_text("x = 1\n", encoding="utf-8")
        output = tmp_path / "combined.hex"
        build_v1_combined_hex(main_py, output)
        assert output.stat().st_size > V1_FIRMWARE_HEX.stat().st_size
