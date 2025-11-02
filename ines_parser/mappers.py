"""
Mapper information database

Provides lookup tables for mapper names and additional information.
Based on NESdev Wiki mapper list.
"""

from typing import Dict, Optional, List

# Mapper database: mapper_number -> (primary_name, [alternate_names], notes)
MAPPER_DATABASE: Dict[int, tuple] = {
    0: ("NROM", [], ""),
    1: ("MMC1", ["SxROM"], ""),
    2: ("UxROM", [], ""),
    3: ("CNROM", [], ""),
    4: ("MMC3", ["TxROM", "MMC6"], ""),
    5: ("MMC5", ["ExROM"], "Contains expansion sound"),
    7: ("AxROM", [], ""),
    9: ("MMC2", ["PxROM"], ""),
    10: ("MMC4", ["FxROM"], ""),
    11: ("Color Dreams", [], ""),
    13: ("CPROM", [], ""),
    15: ("100-in-1 Contra Function 16", [], "Multicart"),
    16: ("Bandai EPROM (24C02)", [], ""),
    18: ("Jaleco SS8806", [], ""),
    19: ("Namco 163", [], "Contains expansion sound"),
    21: ("VRC4", ["VRC4a", "VRC4c"], ""),
    22: ("VRC2", ["VRC2a"], ""),
    23: ("VRC2/VRC4", ["VRC2b", "VRC4e"], ""),
    24: ("VRC6", ["VRC6a"], "Contains expansion sound"),
    25: ("VRC4", ["VRC4b", "VRC4d"], ""),
    26: ("VRC6", ["VRC6b"], "Contains expansion sound"),
    34: ("BNROM", ["NINA-001"], ""),
    64: ("RAMBO-1", [], "MMC3 clone with extra features"),
    66: ("GxROM", ["MxROM"], ""),
    68: ("After Burner", [], "ROM-based nametables"),
    69: ("Sunsoft FME-7", ["Sunsoft 5B"], "The 5B is the FME-7 with expansion sound"),
    71: ("Camerica/Codemasters", [], "Similar to UNROM"),
    73: ("VRC3", [], ""),
    74: ("Pirate MMC3 derivative", [], "Has both CHR ROM and CHR RAM (2k)"),
    75: ("VRC1", [], ""),
    76: ("Namco 109 variant", [], ""),
    79: ("NINA-03/NINA-06", [], "It's either 003 or 006, we don't know right now"),
    85: ("VRC7", [], "Contains expansion sound"),
    86: ("JALECO-JF-13", [], ""),
    94: ("Senjou no Ookami", [], ""),
    105: ("NES-EVENT", [], "Similar to MMC1"),
    113: ("NINA-03/NINA-06??", [], "For multicarts including mapper 79 games"),
    118: ("TxSROM", ["MMC3"], "MMC3 with independent mirroring control"),
    119: ("TQROM", ["MMC3"], "Has both CHR ROM and CHR RAM"),
    159: ("Bandai EPROM (24C01)", [], ""),
    166: ("SUBOR", [], ""),
    167: ("SUBOR", [], ""),
    180: ("Crazy Climber", [], "Variation of UNROM, fixed first bank at $8000"),
    185: ("CNROM with protection diodes", [], ""),
    192: ("Pirate MMC3 derivative", [], "Has both CHR ROM and CHR RAM (4k)"),
    206: ("DxROM", ["Namco 118", "MIMIC-1"], "Simplified MMC3 predecessor lacking some features"),
    210: ("Namco 175 and 340", [], "Namco 163 with different mirroring"),
    228: ("Action 52", [], ""),
    232: ("Camerica/Codemasters Quattro", [], "Multicarts"),
}


def get_mapper_name(mapper_number: int) -> str:
    """
    Get the primary name for a mapper number.
    
    Args:
        mapper_number: The mapper number
        
    Returns:
        Primary mapper name, or "Unknown" if not found
    """
    if mapper_number in MAPPER_DATABASE:
        return MAPPER_DATABASE[mapper_number][0]
    return f"Unknown ({mapper_number})"


def get_mapper_alternate_names(mapper_number: int) -> List[str]:
    """
    Get alternate names for a mapper.
    
    Args:
        mapper_number: The mapper number
        
    Returns:
        List of alternate names, empty list if none
    """
    if mapper_number in MAPPER_DATABASE:
        return MAPPER_DATABASE[mapper_number][1]
    return []


def get_mapper_notes(mapper_number: int) -> str:
    """
    Get notes/information about a mapper.
    
    Args:
        mapper_number: The mapper number
        
    Returns:
        Notes string, empty if none
    """
    if mapper_number in MAPPER_DATABASE:
        return MAPPER_DATABASE[mapper_number][2]
    return ""


def get_mapper_info(mapper_number: int) -> Dict[str, any]:
    """
    Get complete mapper information.
    
    Args:
        mapper_number: The mapper number
        
    Returns:
        Dictionary with 'name', 'alternates', and 'notes'
    """
    if mapper_number in MAPPER_DATABASE:
        name, alternates, notes = MAPPER_DATABASE[mapper_number]
        return {
            'name': name,
            'alternates': alternates,
            'notes': notes,
            'all_names': [name] + alternates,
        }
    
    return {
        'name': f"Unknown ({mapper_number})",
        'alternates': [],
        'notes': '',
        'all_names': [f"Unknown ({mapper_number})"],
    }


def is_known_mapper(mapper_number: int) -> bool:
    """
    Check if a mapper number is in the database.
    
    Args:
        mapper_number: The mapper number
        
    Returns:
        True if mapper is known, False otherwise
    """
    return mapper_number in MAPPER_DATABASE

