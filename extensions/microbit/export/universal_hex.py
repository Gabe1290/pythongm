#!/usr/bin/env python3
"""The micro:bit Universal Hex (docs/MICROBIT_V2_HEX_PLAN.md, unit H5).

A Universal Hex is ONE ``.hex`` file that flashes on either board version: it
holds a complete single-board hex for each target, every target's records
re-packed into a *section* that a board's interface firmware (DAPLink) either
accepts or skips by its **board id** (``0x9900`` V1, ``0x9903`` V2). This module
turns per-board Intel Hex strings into one Universal Hex, and back.

How a section is built (the "sections" format, the one the specification
recommends and the reference library uses by default):

* an extended-linear-address record, then a **Block Start** record (type
  ``0x0A``) carrying the board id and the marker ``0xC0DE``;
* the board's own records. For V1 ids they stay ordinary data records; for every
  other board each data record's type becomes **Custom Data** (``0x0D``), which a
  V1 interface ignores -- so a V1 board flashes only its own section;
* extended-segment addresses are converted to extended-linear ones; start-address
  records are dropped;
* **Padded Data** records (``0x0C``) and a final **Block End** record (``0x0B``)
  whose data is padding, so the section's text length is an exact multiple of
  **512 characters** (newlines counted).

Only the *last* section keeps the end-of-file record. Written from the documented
behaviour and TypeScript source of the MIT-licensed
``microbit-foundation/microbit-universal-hex`` (see ``THIRD_PARTY_LICENSES.md``);
the specification text itself (CC-BY-SA-4.0, microbit-foundation/spec-universal-
hex) is cited, not copied. The older "blocks" layout is not implemented.
"""
import binascii

from .intel_hex import make_record

BOARD_ID_V1 = 0x9900
BOARD_ID_V2 = 0x9903
V1_BOARD_IDS = (0x9900, 0x9901)         # these keep ordinary data records
BLOCK_SIZE = 512

# standard record types
TYPE_DATA = 0x00
TYPE_EOF = 0x01
TYPE_EXT_SEGMENT = 0x02
TYPE_START_SEGMENT = 0x03
TYPE_EXT_LINEAR = 0x04
TYPE_START_LINEAR = 0x05
# the Universal Hex's custom types
TYPE_BLOCK_START = 0x0A
TYPE_BLOCK_END = 0x0B
TYPE_PADDED_DATA = 0x0C
TYPE_CUSTOM_DATA = 0x0D
TYPE_OTHER_DATA = 0x0E

RECORD_DATA_MAX_BYTES = 32              # DAPLink does not accept more
_MIN_RECORD_LEN = 11                    # ':' + count + address + type + checksum
MAX_RECORD_LEN = _MIN_RECORD_LEN + RECORD_DATA_MAX_BYTES * 2
EOF_RECORD = ":00000001FF"


class UniversalHexError(ValueError):
    """The input cannot be turned into (or read as) a Universal Hex."""


# -- records -------------------------------------------------------------------------------

def _valid_type(record_type):
    return (TYPE_DATA <= record_type <= TYPE_START_LINEAR
            or TYPE_BLOCK_START <= record_type <= TYPE_OTHER_DATA)


def create_record(address, record_type, data=b""):
    if not 0 <= address <= 0xFFFF:
        raise UniversalHexError(f"Record ({record_type}) address out of range: {address}")
    if len(data) > RECORD_DATA_MAX_BYTES:
        raise UniversalHexError(
            f"Record ({record_type}) data has too many bytes ({len(data)}).")
    if not _valid_type(record_type):
        raise UniversalHexError(f"Record type '{record_type}' is not valid.")
    return make_record(address, record_type, bytes(data))


def _validate(record):
    if len(record) < _MIN_RECORD_LEN:
        raise UniversalHexError(f"Record length too small: {record}")
    if len(record) > MAX_RECORD_LEN:
        raise UniversalHexError(f"Record length is too large: {record}")
    if record[0] != ":":
        raise UniversalHexError(f'Record does not start with a ":": {record}')


def get_record_type(record):
    _validate(record)
    try:
        record_type = int(record[7:9], 16)
    except ValueError:
        raise UniversalHexError(f"Record '{record}' is not hexadecimal.") from None
    if not _valid_type(record_type):
        raise UniversalHexError(
            f"Record type '{record[7:9]}' from record '{record}' is not valid.")
    return record_type


def get_record_data(record):
    try:
        return binascii.unhexlify(record[9:-2])
    except (binascii.Error, ValueError):
        raise UniversalHexError(f'Could not parse Intel Hex record "{record}".') from None


def parse_record(record):
    """``(address, record_type, data)`` of a record."""
    _validate(record)
    try:
        raw = binascii.unhexlify(record[1:])
    except (binascii.Error, ValueError):
        raise UniversalHexError(f'Could not parse Intel Hex record "{record}".') from None
    count = raw[0]
    if len(raw) > count + 5:
        raise UniversalHexError(
            f'Parsed record "{record}" is larger than indicated by the byte count.')
    return (raw[1] << 8) | raw[2], raw[3], raw[4:4 + count]


def ext_lin_address_record(address):
    if not 0 <= address <= 0xFFFFFFFF:
        raise UniversalHexError(
            f"Address '{address}' for Extended Linear Address record is out of range.")
    return create_record(0, TYPE_EXT_LINEAR,
                         bytes([(address >> 24) & 0xFF, (address >> 16) & 0xFF]))


def block_start_record(board_id):
    if not 0 <= board_id <= 0xFFFF:
        raise UniversalHexError("Board ID out of range when creating Block Start record.")
    return create_record(0, TYPE_BLOCK_START,
                         bytes([(board_id >> 8) & 0xFF, board_id & 0xFF, 0xC0, 0xDE]))


def block_end_record(pad_bytes):
    return create_record(0, TYPE_BLOCK_END, b"\xff" * pad_bytes)


def padded_data_record(pad_bytes):
    return create_record(0, TYPE_PADDED_DATA, b"\xff" * pad_bytes)


def convert_record_to(record, record_type):
    """The same record with another type (data kept, checksum recomputed)."""
    address, _type, data = parse_record(record)
    return make_record(address, record_type, data)


def convert_ext_segment_to_linear(record):
    """An extended-segment-address record as an extended-linear one. Only
    segment bases that are multiples of 0x10000 can be converted."""
    data = get_record_data(record)
    if len(data) != 2 or data[0] & 0xF or data[1] != 0:
        raise UniversalHexError(f"Invalid Extended Segment Address record {record}")
    return ext_lin_address_record(data[0] << 12)


def split_records(text):
    """The non-empty lines of a hex string (``\\r`` removed)."""
    return [line for line in text.replace("\r", "").split("\n") if line]


def find_data_field_length(records):
    """The most data bytes any record carries (16 at least) -- the size padding
    records are made to match."""
    longest, at_longest = 16, 0
    for record in records:
        length = (len(record) - _MIN_RECORD_LEN) // 2
        if length > longest:
            longest, at_longest = length, 0
        elif length == longest:
            at_longest += 1
        if at_longest > 12:
            break
    if longest > RECORD_DATA_MAX_BYTES:
        raise UniversalHexError(f"Intel Hex record data size is too large: {longest}")
    return longest


# -- detection ------------------------------------------------------------------------------

def _is_universal_records(records):
    return (len(records) >= 2
            and get_record_type(records[0]) == TYPE_EXT_LINEAR
            and get_record_type(records[1]) == TYPE_BLOCK_START
            and get_record_type(records[-1]) == TYPE_EOF)


def is_universal_hex(text):
    """True if the text opens with an extended-linear-address record followed by
    a Block Start record (the cheap test the reference library uses)."""
    first = ":02000004"
    if not text.startswith(first):
        return False
    # find the next record: the line ending is unknown, so scan for its ':'
    i = len(first)
    while True:
        i += 1
        if not (text[i:i + 1] != ":" and i < MAX_RECORD_LEN + 3):
            break
    return text[i:i + len(":0400000A")] == ":0400000A"


def _is_makecode_for_v1(records):
    """MakeCode's V1 hex files stash project data after the end-of-file record,
    which cannot be merged; recognised only to give a useful error."""
    ext_ram = ext_lin_address_record(0x20000000)
    try:
        i = records.index(EOF_RECORD)
    except ValueError:
        i = -1
    if i == len(records) - 1:
        # a MakeCode v0 hex puts its metadata in RAM just before the EoF
        while True:
            i -= 1
            if not i > 0:
                break
            if records[i] == ext_ram:
                return True
    while True:
        i += 1
        if i >= len(records):
            break
        # MakeCode v2/v3 store the project in "other data" records; v1 in RAM space
        if get_record_type(records[i]) == TYPE_OTHER_DATA or records[i] == ext_ram:
            return True
    return False


def _misplaced_eof(board_id, index, total, records):
    if _is_makecode_for_v1(records):
        return UniversalHexError(
            f"Board ID {board_id} Hex is from MakeCode, import this hex into the "
            "MakeCode editor to create a Universal Hex.")
    return UniversalHexError(
        f"EoF record found at record {index} of {total} in Board ID {board_id} hex")


# -- building -------------------------------------------------------------------------------

def hex_to_section(hex_text, board_id):
    """One board's Intel Hex as a Universal Hex *section* (see the module
    docstring). The end-of-file record is kept if the input had one."""
    records = split_records(hex_text)
    if not records:
        return ""
    if _is_universal_records(records):
        raise UniversalHexError(f"Board ID {board_id} Hex is already a Universal Hex.")

    lines = []
    length = 0

    def add(record):
        nonlocal length
        lines.append(record)
        length += len(record) + 1                  # +1 for the newline

    index = 0
    first_type = get_record_type(records[0])
    if first_type == TYPE_EXT_LINEAR:
        add(records[0])
        index = 1
    elif first_type == TYPE_EXT_SEGMENT:
        add(convert_ext_segment_to_linear(records[0]))
        index = 1
    else:
        add(ext_lin_address_record(0))
    add(block_start_record(board_id))

    custom_data = board_id not in V1_BOARD_IDS
    end_of_file = False
    while index < len(records):
        record = records[index]
        index += 1
        record_type = get_record_type(record)
        if record_type == TYPE_DATA:
            add(convert_record_to(record, TYPE_CUSTOM_DATA) if custom_data else record)
        elif record_type == TYPE_EXT_SEGMENT:
            add(convert_ext_segment_to_linear(record))
        elif record_type == TYPE_EXT_LINEAR:
            add(record)
        elif record_type == TYPE_EOF:
            end_of_file = True
            break
        # start-address records (and anything else) are dropped
    if index != len(records):
        raise _misplaced_eof(board_id, index, len(records), records)

    length += len(block_end_record(0)) + 1         # the closing Block End, before padding
    no_data_chars = len(padded_data_record(0)) + 1
    max_bytes = find_data_field_length(records)
    capacity_chars = max_bytes * 2
    needed = (BLOCK_SIZE - length % BLOCK_SIZE) % BLOCK_SIZE
    while needed > capacity_chars:
        pad = min((needed - no_data_chars) >> 1, max_bytes)
        add(padded_data_record(pad))
        needed = (BLOCK_SIZE - length % BLOCK_SIZE) % BLOCK_SIZE
    lines.append(block_end_record(needed >> 1))
    if end_of_file:
        lines.append(EOF_RECORD)
    lines.append("")
    return "\n".join(lines)


def hex_to_blocks(hex_text, board_id, pad_final_block=True):
    """One board's Intel Hex in the older Universal Hex **"blocks"** layout: every 512-character
    block is self-contained -- extended-linear-address, Block Start, the records that fit, padding,
    Block End -- instead of one section per board. A port of ``iHexToCustomFormatBlocks`` from
    microbit-universal-hex (MIT). Every block is padded to exactly 512 characters, so a following
    section stays aligned (the reference's current code leaves a hex's last block unpadded, which its
    own test marks a known TODO; the golden file it ships pads it, and so does this). The one block
    that stays short is the very last of a whole file when ``pad_final_block`` is False: it closes with
    a zero-length Block End and the end-of-file record, exactly as in that golden file
    (``create_universal_hex`` passes False for the last hex). The end-of-file record is kept if the
    input had one.
    """
    records = split_records(hex_text)
    if not records:
        return ""
    if _is_universal_records(records):
        raise UniversalHexError(f"Board ID {board_id} Hex is already a Universal Hex.")

    custom_data = board_id not in V1_BOARD_IDS
    start = block_start_record(board_id)
    current_ext = ext_lin_address_record(0)
    ext_len = len(current_ext) + 1
    start_len = len(start) + 1
    end_base = len(block_end_record(0)) + 1
    pad_base = len(padded_data_record(0)) + 1
    capacity = find_data_field_length(records)

    def close_block(block, block_len):
        """Pad with Padded Data records, then end the block with a Block End that makes it exactly
        BLOCK_SIZE characters. ``block_len`` does not yet count the Block End."""
        while BLOCK_SIZE - block_len > capacity * 2 + end_base:
            block.append(padded_data_record(min((BLOCK_SIZE - block_len - end_base - pad_base) >> 1, capacity)))
            block_len += len(block[-1]) + 1
        block.append(block_end_record((BLOCK_SIZE - block_len - end_base) >> 1))

    lines = []
    i = 0
    while i < len(records):
        first_type = get_record_type(records[i])
        if first_type == TYPE_EXT_LINEAR:
            current_ext = records[i]
            i += 1
        elif first_type == TYPE_EXT_SEGMENT:
            current_ext = convert_ext_segment_to_linear(records[i])
            i += 1
        block = [current_ext, start]
        block_len = ext_len + start_len
        end_of_file = False
        # the Block End is always reserved room (end_base) while records are added
        while i < len(records) and BLOCK_SIZE >= block_len + end_base + len(records[i]) + 1:
            record = records[i]
            i += 1
            record_type = get_record_type(record)
            if custom_data and record_type == TYPE_DATA:
                record = convert_record_to(record, TYPE_CUSTOM_DATA)
            elif record_type == TYPE_EXT_LINEAR:
                current_ext = record
            elif record_type == TYPE_EXT_SEGMENT:
                record = convert_ext_segment_to_linear(record)
                current_ext = record
            elif record_type == TYPE_EOF:
                end_of_file = True
                break
            block.append(record)
            block_len += len(record) + 1
        if end_of_file and i != len(records):
            raise _misplaced_eof(board_id, i, len(records), records)
        if end_of_file and not pad_final_block:
            block.append(block_end_record(0))
        else:
            close_block(block, block_len)
        lines.extend(block)
        if end_of_file:
            lines.append(EOF_RECORD)
    lines.append("")
    return "\n".join(lines)


def create_universal_hex(hexes, blocks=False):
    """One Universal Hex from ``[(board_id, intel_hex_text), ...]``, in order.
    Only the last section keeps the end-of-file record. ``blocks=True`` writes the older
    "blocks" layout (``hex_to_blocks``) instead of one section per board."""
    if not hexes:
        return ""
    convert = hex_to_blocks if blocks else hex_to_section
    eof_line = EOF_RECORD + "\n"
    parts = []
    for board_id, text in hexes[:-1]:
        section = convert(text, board_id)
        if section.endswith(eof_line):
            section = section[:-len(eof_line)]
        parts.append(section)
    last_id, last_text = hexes[-1]
    last = hex_to_blocks(last_text, last_id, pad_final_block=False) if blocks else hex_to_section(last_text, last_id)
    parts.append(last)
    if not last.endswith(eof_line):
        parts.append(eof_line)
    return "".join(parts)


# -- reading --------------------------------------------------------------------------------

def separate_universal_hex(text):
    """The inverse of ``create_universal_hex``: ``[(board_id, intel_hex_text)]``,
    each with its end-of-file record, in the order the boards first appear."""
    records = split_records(text)
    if not records:
        raise UniversalHexError("Empty Universal Hex.")
    if not _is_universal_records(records):
        raise UniversalHexError("Universal Hex format invalid.")

    pass_through = (TYPE_DATA, TYPE_EOF, TYPE_EXT_SEGMENT, TYPE_START_SEGMENT)
    hexes = {}                                  # board id -> {"last": record, "hex": [records]}
    current = 0
    i = 0
    while i < len(records):
        record = records[i]
        record_type = get_record_type(record)
        if record_type in pass_through:
            hexes[current]["hex"].append(record)
        elif record_type == TYPE_CUSTOM_DATA:
            hexes[current]["hex"].append(convert_record_to(record, TYPE_DATA))
        elif record_type == TYPE_EXT_LINEAR:
            following = records[i + 1]          # safe: a Universal Hex ends with an EoF
            if get_record_type(following) == TYPE_BLOCK_START:
                start = get_record_data(following)
                if len(start) != 4:
                    raise UniversalHexError(f"Block Start record invalid: {following}")
                current = (start[0] << 8) + start[1]
                hexes.setdefault(current, {"last": record, "hex": [record]})
                i += 1
            if hexes[current]["last"] != record:
                hexes[current]["last"] = record
                hexes[current]["hex"].append(record)
        i += 1

    out = []
    for board_id, entry in hexes.items():
        lines = entry["hex"]
        if lines[-1] != EOF_RECORD:
            lines.append(EOF_RECORD)
        out.append((board_id, "\n".join(lines) + "\n"))
    return out
