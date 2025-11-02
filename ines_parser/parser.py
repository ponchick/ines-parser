#!/bin/env python3
"""
iNES ROM header parser with full NES 2.0 support
Based on the iNES and NES 2.0 file format specifications
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from .mappers import (
    get_mapper_name,
    get_mapper_alternate_names,
    get_mapper_notes,
    get_mapper_info,
    is_known_mapper,
)


# iNES format constants
INES_HEADER_SIZE = 16
INES_TRAINER_SIZE = 512


class INESFormat(Enum):
    """iNES format version"""
    UNKNOWN = "Unknown"
    ARCHAIC = "Archaic iNES"
    INES_0_7 = "iNES 0.7"
    INES = "iNES"
    NES_2_0 = "NES 2.0"
    UNIF = "UNIF"


class Mirroring(Enum):
    """Nametable mirroring type"""
    HORIZONTAL = "H"  # Vertical arrangement
    VERTICAL = "V"    # Horizontal arrangement
    FOUR_SCREEN = "F"  # Alternative/4-screen


class TVSystem(Enum):
    """TV system type"""
    NTSC = "NTSC"
    PAL = "PAL"
    DUAL = "Dual"
    DENDY = "Dendy"


class ConsoleType(Enum):
    """Console type for NES 2.0"""
    NES_FAMICOM = "NES/Famicom"
    VS_SYSTEM = "VS System"
    PLAYCHOICE_10 = "PlayChoice-10"
    EXTENDED = "Extended"


class CPUTiming(Enum):
    """CPU/PPU timing mode"""
    RP2C02_NTSC = "RP2C02 (NTSC NES)"
    RP2C07_PAL = "RP2C07 (Licensed PAL NES)"
    MULTIPLE_REGION = "Multiple-region"
    UA6538_DENDY = "UA6538 (Dendy)"


class INESHeader:
    """Parsed iNES header data with full NES 2.0 support"""
    
    def __init__(self, header_bytes: bytes):
        if len(header_bytes) < 16:
            raise ValueError(f"Header too short: {len(header_bytes)} bytes (expected 16)")
        
        self.raw_header = header_bytes[:16]
        self.format = self._detect_format()
        
        if self.format == INESFormat.UNIF:
            return
        
        if self.format == INESFormat.UNKNOWN:
            return
        
        # Parse common fields (bytes 4-6)
        self.prg_rom_size_lsb = header_bytes[4]
        self.chr_rom_size_lsb = header_bytes[5]
        
        # Parse Flags 6
        flags6 = header_bytes[6]
        self.mirroring = self._parse_mirroring(flags6)
        self.has_battery = bool(flags6 & 0x02)
        self.has_trainer = bool(flags6 & 0x04)
        self.four_screen = bool(flags6 & 0x08)
        mapper_low = (flags6 & 0xF0) >> 4
        
        # Parse Flags 7
        flags7 = header_bytes[7]
        self.console_type = self._parse_console_type(flags7)
        self.is_vs_unisystem = bool(flags7 & 0x01)
        self.is_playchoice_10 = bool(flags7 & 0x02)
        mapper_mid = (flags7 & 0xF0) >> 4
        
        # Initial mapper (will be extended for NES 2.0)
        self.mapper = (mapper_mid << 4) | mapper_low
        self.submapper = None
        
        # Parse extended fields based on format
        if self.format == INESFormat.NES_2_0:
            self._parse_nes2_0(header_bytes)
        else:
            # iNES 1.0 size calculation
            self.prg_rom_size = self.prg_rom_size_lsb * 16 * 1024
            self.chr_rom_size = self.chr_rom_size_lsb * 8 * 1024
            self._parse_ines(header_bytes)
        
        # Initialize NES 2.0 specific fields to None for iNES 1.0
        if self.format != INESFormat.NES_2_0:
            self.submapper = None
            self.prg_ram_size = None
            self.prg_nvram_size = None
            self.chr_ram_size = None
            self.chr_nvram_size = None
            self.cpu_timing = None
            self.vs_ppu_type = None
            self.vs_hw_type = None
            self.extended_console_type = None
            self.misc_rom_count = None
            self.expansion_device = None
    
    def _detect_format(self) -> INESFormat:
        """Detect iNES format version according to specification"""
        if self.raw_header.startswith(b"UNIF"):
            return INESFormat.UNIF
        
        if not self.raw_header.startswith(b"NES\x1a"):
            return INESFormat.UNKNOWN
        
        flags7 = self.raw_header[7]
        
        # Check for NES 2.0: byte 7 AND $0C = $08
        if (flags7 & 0x0C) == 0x08:
            return INESFormat.NES_2_0
        
        # Check for Archaic iNES: byte 7 AND $0C = $04
        if (flags7 & 0x0C) == 0x04:
            return INESFormat.ARCHAIC
        
        # Check for iNES: byte 7 AND $0C = $00, and bytes 12-15 are all 0
        if ((flags7 & 0x0C) == 0x00 and
            self.raw_header[12] == 0 and
            self.raw_header[13] == 0 and
            self.raw_header[14] == 0 and
            self.raw_header[15] == 0):
            return INESFormat.INES
        
        # Otherwise, iNES 0.7 or archaic iNES
        return INESFormat.INES_0_7
    
    def _parse_mirroring(self, flags6: int) -> Mirroring:
        """Parse mirroring from Flags 6"""
        if flags6 & 0x08:  # Four-screen / alternative nametable
            return Mirroring.FOUR_SCREEN
        elif flags6 & 0x01:  # Horizontal arrangement (vertical mirroring)
            return Mirroring.VERTICAL
        else:  # Vertical arrangement (horizontal mirroring)
            return Mirroring.HORIZONTAL
    
    def _parse_console_type(self, flags7: int) -> ConsoleType:
        """Parse console type from Flags 7"""
        console_bits = flags7 & 0x03
        if console_bits == 0:
            return ConsoleType.NES_FAMICOM
        elif console_bits == 1:
            return ConsoleType.VS_SYSTEM
        elif console_bits == 2:
            return ConsoleType.PLAYCHOICE_10
        else:
            return ConsoleType.EXTENDED
    
    def _parse_ines(self, header_bytes: bytes):
        """Parse iNES-specific fields (bytes 8-10)"""
        # Flags 8: PRG RAM size
        self.prg_ram_size_units = header_bytes[8]
        if self.prg_ram_size_units == 0:
            self.prg_ram_size = 8 * 1024  # 8KB for compatibility
        else:
            self.prg_ram_size = self.prg_ram_size_units * 8 * 1024
        
        # Flags 9: TV system
        flags9 = header_bytes[9]
        self.tv_system = TVSystem.PAL if (flags9 & 0x01) else TVSystem.NTSC
        
        # Flags 10: Extended TV system and bus conflicts
        flags10 = header_bytes[10]
        tv_bits = flags10 & 0x03
        if tv_bits == 2:
            self.tv_system = TVSystem.PAL
        elif tv_bits in [1, 3]:
            self.tv_system = TVSystem.DUAL
        
        self.has_prg_ram = not bool(flags10 & 0x10)
        self.has_bus_conflicts = bool(flags10 & 0x20)
    
    def _parse_rom_size_nes2_0(self, lsb: int, msb_nibble: int, unit_size: int) -> int:
        """
        Parse ROM size for NES 2.0 format.
        Supports both simple notation and exponent-multiplier notation.
        
        Args:
            lsb: LSB byte (byte 4 for PRG, byte 5 for CHR)
            msb_nibble: MSB nibble from byte 9 (bits 0-3 for PRG, bits 4-7 for CHR)
            unit_size: Size of one unit (16384 for PRG, 8192 for CHR)
        
        Returns:
            Size in bytes
        """
        if msb_nibble <= 0x0E:
            # Simple notation: (msb_nibble << 8) | lsb units
            size_units = (msb_nibble << 8) | lsb
            return size_units * unit_size
        else:
            # Exponent-multiplier notation: msb_nibble = 0xF
            # Format: 1111 EEEE EEMM
            # Exponent is bits 2-7 of lsb, multiplier is bits 0-1 of lsb
            exponent = (lsb >> 2) & 0x3F
            multiplier_raw = lsb & 0x03
            multiplier = multiplier_raw * 2 + 1  # 1, 3, 5, or 7
            
            return (2 ** exponent) * multiplier
    
    def _parse_nes2_0(self, header_bytes: bytes):
        """Parse NES 2.0-specific fields (full implementation)"""
        # Byte 8: Mapper MSB and Submapper
        flags8 = header_bytes[8]
        mapper_highest = (flags8 & 0x0F) << 8
        self.mapper = self.mapper | mapper_highest
        self.submapper = (flags8 & 0xF0) >> 4
        
        # Byte 9: PRG-ROM and CHR-ROM size MSB
        flags9 = header_bytes[9]
        prg_msb = flags9 & 0x0F
        chr_msb = (flags9 & 0xF0) >> 4
        
        # Calculate ROM sizes using NES 2.0 formula
        self.prg_rom_size = self._parse_rom_size_nes2_0(
            self.prg_rom_size_lsb, prg_msb, 16 * 1024
        )
        self.chr_rom_size = self._parse_rom_size_nes2_0(
            self.chr_rom_size_lsb, chr_msb, 8 * 1024
        )
        
        # Byte 10: PRG-RAM/EEPROM size
        flags10 = header_bytes[10]
        prg_ram_shift = flags10 & 0x0F
        prg_nvram_shift = (flags10 & 0xF0) >> 4
        
        if prg_ram_shift == 0:
            self.prg_ram_size = 0
        else:
            self.prg_ram_size = 64 << prg_ram_shift
        
        if prg_nvram_shift == 0:
            self.prg_nvram_size = 0
        else:
            self.prg_nvram_size = 64 << prg_nvram_shift
        
        # Byte 11: CHR-RAM size
        flags11 = header_bytes[11]
        chr_ram_shift = flags11 & 0x0F
        chr_nvram_shift = (flags11 & 0xF0) >> 4
        
        if chr_ram_shift == 0:
            self.chr_ram_size = 0
        else:
            self.chr_ram_size = 64 << chr_ram_shift
        
        if chr_nvram_shift == 0:
            self.chr_nvram_size = 0
        else:
            self.chr_nvram_size = 64 << chr_nvram_shift
        
        # Byte 12: CPU/PPU Timing
        flags12 = header_bytes[12]
        timing_mode = flags12 & 0x03
        if timing_mode == 0:
            self.cpu_timing = CPUTiming.RP2C02_NTSC
            self.tv_system = TVSystem.NTSC
        elif timing_mode == 1:
            self.cpu_timing = CPUTiming.RP2C07_PAL
            self.tv_system = TVSystem.PAL
        elif timing_mode == 2:
            self.cpu_timing = CPUTiming.MULTIPLE_REGION
            self.tv_system = TVSystem.DUAL
        else:  # timing_mode == 3
            self.cpu_timing = CPUTiming.UA6538_DENDY
            self.tv_system = TVSystem.DENDY
        
        # Byte 13: Vs. System Type or Extended Console Type
        flags13 = header_bytes[13]
        if self.console_type == ConsoleType.VS_SYSTEM:
            self.vs_ppu_type = flags13 & 0x0F
            self.vs_hw_type = (flags13 & 0xF0) >> 4
            self.extended_console_type = None
        elif self.console_type == ConsoleType.EXTENDED:
            self.extended_console_type = flags13 & 0x0F
            self.vs_ppu_type = None
            self.vs_hw_type = None
        else:
            self.vs_ppu_type = None
            self.vs_hw_type = None
            self.extended_console_type = None
        
        # Byte 14: Miscellaneous ROMs
        flags14 = header_bytes[14]
        self.misc_rom_count = flags14 & 0x03
        
        # Byte 15: Default Expansion Device
        flags15 = header_bytes[15]
        self.expansion_device = flags15 & 0x3F
        
        # Bus conflicts not applicable in NES 2.0
        self.has_bus_conflicts = False
    
    def is_valid(self) -> bool:
        """Check if this is a valid, parseable iNES file"""
        return self.format not in [INESFormat.UNKNOWN, INESFormat.UNIF, INESFormat.ARCHAIC]
    
    def get_mapper_name(self) -> str:
        """Get the primary mapper name from database"""
        return get_mapper_name(self.mapper)
    
    def get_mapper_info(self) -> Dict[str, Any]:
        """Get complete mapper information"""
        return get_mapper_info(self.mapper)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert header to dictionary for easy access"""
        if not self.is_valid():
            return {
                'format': self.format.value,
                'valid': False
            }
        
        mapper_info = self.get_mapper_info()
        
        result = {
            'format': self.format.value,
            'valid': True,
            'prg_rom_size': self.prg_rom_size,
            'chr_rom_size': self.chr_rom_size,
            'prg_rom_size_kb': self.prg_rom_size // 1024,
            'chr_rom_size_kb': self.chr_rom_size // 1024,
            'mapper': self.mapper,
            'mapper_name': mapper_info['name'],
            'mapper_alternates': mapper_info['alternates'],
            'mapper_notes': mapper_info['notes'],
            'mirroring': self.mirroring.value,
            'has_battery': self.has_battery,
            'has_trainer': self.has_trainer,
            'four_screen': self.four_screen,
            'is_vs_unisystem': self.is_vs_unisystem,
            'is_playchoice_10': self.is_playchoice_10,
            'console_type': self.console_type.value,
        }
        
        # Add format-specific fields
        if hasattr(self, 'prg_ram_size') and self.prg_ram_size is not None:
            result['prg_ram_size'] = self.prg_ram_size
        if hasattr(self, 'tv_system'):
            result['tv_system'] = self.tv_system.value
        
        # NES 2.0 specific fields
        if self.format == INESFormat.NES_2_0:
            if self.submapper is not None:
                result['submapper'] = self.submapper
            if self.prg_nvram_size is not None:
                result['prg_nvram_size'] = self.prg_nvram_size
            if self.chr_ram_size is not None:
                result['chr_ram_size'] = self.chr_ram_size
            if self.chr_nvram_size is not None:
                result['chr_nvram_size'] = self.chr_nvram_size
            if self.cpu_timing is not None:
                result['cpu_timing'] = self.cpu_timing.value
            if self.vs_ppu_type is not None:
                result['vs_ppu_type'] = self.vs_ppu_type
            if self.vs_hw_type is not None:
                result['vs_hw_type'] = self.vs_hw_type
            if self.extended_console_type is not None:
                result['extended_console_type'] = self.extended_console_type
            if self.misc_rom_count is not None:
                result['misc_rom_count'] = self.misc_rom_count
            if self.expansion_device is not None:
                result['expansion_device'] = self.expansion_device
        
        # iNES 1.0 specific fields
        if hasattr(self, 'has_bus_conflicts'):
            result['has_bus_conflicts'] = self.has_bus_conflicts
        
        return result
    
    def __str__(self) -> str:
        """Human-readable string representation (minimal info)"""
        if self.format == INESFormat.UNIF:
            return "UNIF format (not supported)"
        if self.format == INESFormat.UNKNOWN:
            return "Not an iNES file"
        if self.format == INESFormat.ARCHAIC:
            return "Archaic iNES (not supported)"
        
        # Minimal output: mapper name, PRG size, and CHR size if present
        mapper_name = self.get_mapper_name()
        parts = [f"mapper: {self.mapper} ({mapper_name})"]
        parts.append(f"PRG: {self.prg_rom_size // 1024}k")
        
        if self.chr_rom_size > 0:
            parts.append(f"CHR: {self.chr_rom_size // 1024}k")
        
        return ", ".join(parts)
    
    def detailed_str(self) -> str:
        """Detailed human-readable string representation"""
        if not self.is_valid():
            return str(self)
        
        mapper_info = self.get_mapper_info()
        
        # Full output with all fields
        parts = [
            f"mapper: {self.mapper} ({mapper_info['name']})",
            f"mirroring: {self.mirroring.value}",
            f"PRG ROM: {self.prg_rom_size // 1024}k",
            f"CHR ROM: {self.chr_rom_size // 1024}k"
        ]
        
        # Mapper info
        if mapper_info['alternates']:
            parts.append(f"Alt names: {', '.join(mapper_info['alternates'])}")
        if mapper_info['notes']:
            parts.append(f"Notes: {mapper_info['notes']}")
        
        # NES 2.0 specific fields
        if self.format == INESFormat.NES_2_0:
            if self.submapper is not None:
                parts.append(f"Submapper: {self.submapper}")
            if self.prg_ram_size and self.prg_ram_size > 0:
                parts.append(f"PRG RAM: {self.prg_ram_size // 1024}k")
            if self.prg_nvram_size and self.prg_nvram_size > 0:
                parts.append(f"PRG NVRAM: {self.prg_nvram_size // 1024}k")
            if self.chr_ram_size and self.chr_ram_size > 0:
                parts.append(f"CHR RAM: {self.chr_ram_size // 1024}k")
            if self.chr_nvram_size and self.chr_nvram_size > 0:
                parts.append(f"CHR NVRAM: {self.chr_nvram_size // 1024}k")
            if self.cpu_timing:
                parts.append(f"CPU Timing: {self.cpu_timing.value}")
            if self.console_type == ConsoleType.VS_SYSTEM:
                if self.vs_ppu_type is not None:
                    parts.append(f"VS PPU Type: {self.vs_ppu_type}")
                if self.vs_hw_type is not None:
                    parts.append(f"VS HW Type: {self.vs_hw_type}")
            if self.extended_console_type is not None:
                parts.append(f"Extended Console: {self.extended_console_type}")
            if self.misc_rom_count and self.misc_rom_count > 0:
                parts.append(f"Misc ROMs: {self.misc_rom_count}")
        
        # Add optional fields
        if self.has_trainer:
            parts.append("Trainer: Yes")
        if self.has_battery:
            parts.append("Battery: Yes")
        if self.is_vs_unisystem:
            parts.append("VS Unisystem")
        if self.is_playchoice_10:
            parts.append("PlayChoice-10")
        if hasattr(self, 'tv_system'):
            parts.append(f"TV System: {self.tv_system.value}")
        if hasattr(self, 'has_bus_conflicts') and self.format != INESFormat.NES_2_0:
            parts.append(f"Bus Conflicts: {self.has_bus_conflicts}")
        
        return ", ".join(parts)


def parse_ines_header(header_bytes: bytes) -> Optional[INESHeader]:
    """
    Parse iNES header from bytes
    
    Args:
        header_bytes: First 16+ bytes of the ROM file
        
    Returns:
        INESHeader object or None if parsing failed
    """
    try:
        return INESHeader(header_bytes)
    except Exception:
        return None
