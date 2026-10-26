"""
iNES Parser Library

A Python library for parsing iNES format NES ROM files.
Supports iNES 1.0, NES 2.0, Archaic iNES formats, and UNIF detection,
plus GoodTools/No-Intro ROM filename conventions.
"""

from .parser import (
    parse_ines_header,
    INESHeader,
    INESFormat,
    Mirroring,
    TVSystem,
    ConsoleType,
    CPUTiming,
    INES_HEADER_SIZE,
    INES_TRAINER_SIZE,
)

from .filename import (
    parse_rom_filename,
    RomFilenameInfo,
    DumpStatus,
    expected_tv_system,
)

from .tables import (
    get_mapper_name,
    get_mapper_alternate_names,
    get_mapper_notes,
    get_mapper_info,
    is_known_mapper,
    get_vs_ppu_type_name,
    get_vs_hw_type_name,
    get_extended_console_type_name,
    get_expansion_device_name,
    get_submapper_name,
    is_known_submapper,
)

__version__ = "1.5.0"
__author__ = "Leonid Kabanov"
__all__ = [
    "parse_ines_header",
    "INESHeader",
    "INESFormat",
    "Mirroring",
    "TVSystem",
    "ConsoleType",
    "CPUTiming",
    "INES_HEADER_SIZE",
    "INES_TRAINER_SIZE",
    "parse_rom_filename",
    "RomFilenameInfo",
    "DumpStatus",
    "expected_tv_system",
    "get_mapper_name",
    "get_mapper_alternate_names",
    "get_mapper_notes",
    "get_mapper_info",
    "is_known_mapper",
    "get_vs_ppu_type_name",
    "get_vs_hw_type_name",
    "get_extended_console_type_name",
    "get_expansion_device_name",
    "get_submapper_name",
    "is_known_submapper",
]

