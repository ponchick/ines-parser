"""Tests for ines_parser.parser: header field parsing."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ines_parser import INESHeader, Mirroring, parse_ines_header  # noqa: E402

MAGIC = b"NES\x1a"


def raw_bytes(fields: dict) -> bytes:
    b = bytearray(16)
    b[0:4] = MAGIC
    for offset, value in fields.items():
        b[offset] = value
    return bytes(b)


class TestNametableBit0:
    """Flags-6 bit 0 stays meaningful together with the four-screen bit
    (mapper 30/218/286 conventions), so it is exposed separately."""

    def test_four_screen_with_bit0(self):
        # Real-world pattern: flags 6 = 0xEB (bit 0 + bit 3 both set).
        h = INESHeader(raw_bytes({6: 0xEB}))
        assert h.four_screen
        assert h.mirroring == Mirroring.FOUR_SCREEN
        assert h.nametable_bit0

    def test_four_screen_without_bit0(self):
        h = INESHeader(raw_bytes({6: 0xE8}))
        assert h.four_screen
        assert not h.nametable_bit0

    def test_vertical_implies_bit0(self):
        h = INESHeader(raw_bytes({6: 0x41}))
        assert h.mirroring == Mirroring.VERTICAL
        assert h.nametable_bit0

    def test_horizontal_clears_bit0(self):
        h = INESHeader(raw_bytes({6: 0x40}))
        assert h.mirroring == Mirroring.HORIZONTAL
        assert not h.nametable_bit0

    def test_to_dict_contains_bit0(self):
        h = parse_ines_header(raw_bytes({6: 0xEB}))
        assert h is not None
        d = h.to_dict()
        assert d["nametable_bit0"] is True
        assert d["four_screen"] is True

    def test_detailed_str_mentions_bit0_for_four_screen(self):
        h = parse_ines_header(raw_bytes({6: 0xEB}))
        assert "Nametable bit 0: True" in h.detailed_str()
        plain = parse_ines_header(raw_bytes({6: 0x40}))
        assert "Nametable bit 0" not in plain.detailed_str()


class TestBasicParsing:
    def test_classic_mmc3(self):
        h = INESHeader(raw_bytes({4: 2, 5: 1, 6: 0x41}))
        assert h.mapper == 4
        assert h.prg_rom_size == 32 * 1024
        assert h.chr_rom_size == 8 * 1024
        assert h.mirroring == Mirroring.VERTICAL
        assert h.format.value == "iNES"

    def test_mapper_high_nibble(self):
        h = INESHeader(raw_bytes({4: 2, 6: 0x20, 7: 0x20}))
        assert h.mapper == 34

    def test_nes2_mapper_and_submapper(self):
        h = INESHeader(raw_bytes({6: 0xC0, 7: 0x08, 8: 0x31}))
        assert h.format.value == "NES 2.0"
        assert h.mapper == 268
        assert h.submapper == 3

    def test_parse_factory_garbage_handling(self):
        # Short input raises inside INESHeader, so the lenient factory
        # converts it to None.
        assert parse_ines_header(b"short") is None
        # Wrong magic and UNIF are detected but not parsed: a header object
        # comes back, flagged invalid rather than None.
        for raw in (b"NEX\x1a" + b"\x00" * 12, b"UNIF" + b"\x00" * 12):
            h = parse_ines_header(raw)
            assert h is not None
            assert not h.is_valid()
