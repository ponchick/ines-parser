#!/usr/bin/env python3
"""
Scan and analyze iNES ROM files from directories and archives.

This script scans a directory for ROM files (.nes) and archives (.7z, .zip, .rar),
extracts and analyzes ROM headers, displaying information about mapper, mirroring,
ROM sizes, and other header fields. Supports filtering and detailed output.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for ines_parser package import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import libarchive - make it optional
try:
    import libarchive
    LIBARCHIVE_AVAILABLE = True
except ImportError:
    LIBARCHIVE_AVAILABLE = False

# Import from ines_parser package
from ines_parser import parse_ines_header, INESHeader, INES_HEADER_SIZE


# Constants
DEFAULT_ARCHIVE_PATH = 'nes_archive/'
# All potential archive formats that libarchive can support
ALL_ARCHIVE_FORMATS = {'.7z', '.zip', '.rar'}
# Archive extensions depend on libarchive availability
if LIBARCHIVE_AVAILABLE:
    ARCHIVE_EXTENSIONS = ALL_ARCHIVE_FORMATS
else:
    ARCHIVE_EXTENSIONS = set()
# All supported extensions
SUPPORTED_EXTENSIONS = ARCHIVE_EXTENSIONS | {'.nes'}


def read_header_from_blocks(entry) -> Optional[bytes]:
    """
    Read the first INES_HEADER_SIZE bytes from an archive entry.
    
    Args:
        entry: Archive entry to read from
        
    Returns:
        Header bytes or None if insufficient data
    """
    blocks = []
    total_size = 0
    
    for block in entry.get_blocks():
        blocks.append(block)
        total_size += len(block)
        if total_size >= INES_HEADER_SIZE:
            break
    
    header_bytes = b''.join(blocks)
    return header_bytes[:INES_HEADER_SIZE] if len(header_bytes) >= INES_HEADER_SIZE else None


def format_header_info(header: INESHeader, show_all_fields: bool = False) -> str:
    """
    Format header information for display.
    
    Args:
        header: Parsed iNES header
        show_all_fields: If True, show all header fields (mirroring, battery, trainer, etc.)
        
    Returns:
        Formatted string with header information
    """
    if not header.is_valid():
        return header.format.value
    
    # Use detailed format if requested, otherwise minimal
    if show_all_fields:
        return header.detailed_str()
    else:
        return str(header)


def matches_filters(header: INESHeader, filter_trainer: bool = False,
                   filter_mapper: int = None, filter_mirroring: str = None,
                   min_prg_size: int = None, max_prg_size: int = None,
                   min_chr_size: int = None, max_chr_size: int = None) -> bool:
    """
    Check if ROM header matches all specified filters.
    
    Args:
        header: Parsed iNES header
        filter_trainer: If True, only accept ROMs with trainer
        filter_mapper: If specified, only accept this mapper number
        filter_mirroring: If specified, only accept this mirroring type (H/V/F)
        min_prg_size: Minimum PRG ROM size in KB
        max_prg_size: Maximum PRG ROM size in KB
        min_chr_size: Minimum CHR ROM size in KB
        max_chr_size: Maximum CHR ROM size in KB
        
    Returns:
        True if ROM matches all filters
    """
    if not header.is_valid():
        return False
    
    # Filter by trainer
    if filter_trainer and not header.has_trainer:
        return False
    
    # Filter by mapper
    if filter_mapper is not None and header.mapper != filter_mapper:
        return False
    
    # Filter by mirroring
    if filter_mirroring is not None and header.mirroring.value != filter_mirroring:
        return False
    
    # Filter by PRG ROM size
    prg_size_kb = header.prg_rom_size // 1024
    if min_prg_size is not None and prg_size_kb < min_prg_size:
        return False
    if max_prg_size is not None and prg_size_kb > max_prg_size:
        return False
    
    # Filter by CHR ROM size
    chr_size_kb = header.chr_rom_size // 1024
    if min_chr_size is not None and chr_size_kb < min_chr_size:
        return False
    if max_chr_size is not None and chr_size_kb > max_chr_size:
        return False
    
    return True


def process_nes_file(file_path: Path, base_path: Path, 
                     filter_trainer: bool = False, 
                     show_all_fields: bool = False,
                     filter_mapper: int = None,
                     filter_mirroring: str = None,
                     min_prg_size: int = None,
                     max_prg_size: int = None,
                     min_chr_size: int = None,
                     max_chr_size: int = None) -> bool:
    """
    Process a plain .nes file and display ROM information.
    
    Args:
        file_path: Path to the .nes file
        base_path: Base path for relative path display
        
    Returns:
        True if processing succeeded, False otherwise
    """
    relative_path = file_path.relative_to(base_path)
    
    try:
        with open(file_path, 'rb') as f:
            header_bytes = f.read(INES_HEADER_SIZE)
            
            if len(header_bytes) < INES_HEADER_SIZE:
                print(f'{relative_path}: File too short (less than {INES_HEADER_SIZE} bytes)')
                return False
            
            # Parse header
            header = parse_ines_header(header_bytes)
            
            if not header:
                print(f'{relative_path}: Failed to parse header')
                return False
            
            # Apply filters
            if not matches_filters(header, filter_trainer, filter_mapper, filter_mirroring,
                                 min_prg_size, max_prg_size, min_chr_size, max_chr_size):
                return False
            
            print(f'{relative_path}: {format_header_info(header, show_all_fields)}')
            return True
            
    except Exception as e:
        print(f'{relative_path}: Error reading file: {e}')
        return False


def process_archive(archive_path: Path, base_path: Path, 
                   filter_trainer: bool = False,
                   show_all_fields: bool = False,
                   filter_mapper: int = None,
                   filter_mirroring: str = None,
                   min_prg_size: int = None,
                   max_prg_size: int = None,
                   min_chr_size: int = None,
                   max_chr_size: int = None) -> int:
    """
    Process an archive (.7z, .zip, or .rar) and display ROM information for all files.
    
    Args:
        archive_path: Path to the archive
        base_path: Base path for relative path display
        
    Returns:
        Number of successfully processed files in the archive
    """
    if not LIBARCHIVE_AVAILABLE:
        return 0
    
    relative_path = archive_path.relative_to(base_path)
    nes_files_found = 0
    processed_count = 0
    
    try:
        # Open file first, then pass to libarchive to avoid repeated stat() calls
        with open(archive_path, 'rb') as f:
            with libarchive.fd_reader(f.fileno()) as archive:
                # Process all file entries (skip directories)
                for entry in archive:
                    if entry.isfile:
                        # Only process .nes files
                        entry_name = entry.name.lower()
                        if not entry_name.endswith('.nes'):
                            continue
                        
                        nes_files_found += 1
                        
                        # Read header bytes
                        header_bytes = read_header_from_blocks(entry)
                        
                        if not header_bytes:
                            print(f'{relative_path}:{entry.name}: File too short (less than {INES_HEADER_SIZE} bytes)')
                            continue
                        
                        # Parse header
                        header = parse_ines_header(header_bytes)
                        
                        if not header:
                            print(f'{relative_path}:{entry.name}: Failed to parse header')
                            continue
                        
                        # Apply filters
                        if not matches_filters(header, filter_trainer, filter_mapper, filter_mirroring,
                                             min_prg_size, max_prg_size, min_chr_size, max_chr_size):
                            continue
                        
                        print(f'{relative_path}:{entry.name}: {format_header_info(header, show_all_fields)}')
                        processed_count += 1
                
                # Report if no .nes files found at all (not filtered, but actually missing)
                if nes_files_found == 0:
                    print(f'{relative_path}: No .nes files found in archive')
                
                return processed_count
                
    except Exception as e:
        print(f'{relative_path}: Error reading archive: {e}')
        return 0


def process_file(file_path: Path, base_path: Path, 
                filter_trainer: bool = False,
                show_all_fields: bool = False,
                filter_mapper: int = None,
                filter_mirroring: str = None,
                min_prg_size: int = None,
                max_prg_size: int = None,
                min_chr_size: int = None,
                max_chr_size: int = None) -> int:
    """
    Process a file based on its extension.
    
    Args:
        file_path: Path to the file
        base_path: Base path for relative path display
        filter_trainer: If True, only show files with trainer
        show_all_fields: If True, show additional header fields
        
    Returns:
        Number of successfully processed ROM files (1 for .nes, N for archives)
    """
    ext = file_path.suffix.lower()
    
    if ext == '.nes':
        return 1 if process_nes_file(file_path, base_path, filter_trainer, show_all_fields,
                                     filter_mapper, filter_mirroring, 
                                     min_prg_size, max_prg_size, min_chr_size, max_chr_size) else 0
    elif ext in ARCHIVE_EXTENSIONS:
        return process_archive(file_path, base_path, filter_trainer, show_all_fields,
                              filter_mapper, filter_mirroring,
                              min_prg_size, max_prg_size, min_chr_size, max_chr_size)
    else:
        return 0


def scan_directory(directory: Path, 
                  filter_trainer: bool = False, 
                  show_all_fields: bool = False,
                  filter_mapper: int = None,
                  filter_mirroring: str = None,
                  min_prg_size: int = None,
                  max_prg_size: int = None,
                  min_chr_size: int = None,
                  max_chr_size: int = None) -> int:
    """
    Scan a directory for ROM files and archives, and process them.
    
    Searches for .nes, .7z, and .zip files recursively.
    
    Args:
        directory: Directory to scan
        filter_trainer: If True, only show files with trainer
        show_all_fields: If True, show additional header fields
        
    Returns:
        Number of successfully processed ROM files (counts individual ROMs in archives)
    """
    # Collect all supported files
    all_files = []
    for ext in SUPPORTED_EXTENSIONS:
        all_files.extend(directory.rglob(f'*{ext}'))
    
    # Sort by path for consistent output
    all_files.sort()
    
    if not all_files:
        extensions_str = ', '.join(sorted(SUPPORTED_EXTENSIONS))
        print(f"No files found with extensions {extensions_str} in {directory}", file=sys.stderr)
        return 0
    
    processed_count = 0
    
    try:
        for file_path in all_files:
            processed_count += process_file(file_path, directory, filter_trainer, show_all_fields,
                                          filter_mapper, filter_mirroring,
                                          min_prg_size, max_prg_size, min_chr_size, max_chr_size)
                
    except KeyboardInterrupt:
        print('\n\nInterrupted by user', file=sys.stderr)
        return processed_count
    
    return processed_count


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    # Build supported file types string from SUPPORTED_EXTENSIONS
    supported_types = ", ".join(sorted(SUPPORTED_EXTENSIONS))
    if not LIBARCHIVE_AVAILABLE:
        supported_types += " (libarchive not available - archive support disabled)"
    
    parser = argparse.ArgumentParser(
        prog='scan_roms.py',
        description='Scan and analyze iNES ROM files from directories and archives',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported file types: {supported_types}

Examples:
  %(prog)s
  %(prog)s /path/to/roms
  %(prog)s /path/to/roms --verbose
        """
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default=DEFAULT_ARCHIVE_PATH,
        help=f'Directory containing ROM files (default: {DEFAULT_ARCHIVE_PATH})'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--has-trainer',
        action='store_true',
        help='Show only ROMs with trainer'
    )
    parser.add_argument(
        '--show-all',
        action='store_true',
        help='Show all header fields (trainer, battery, etc.)'
    )
    parser.add_argument(
        '--mapper',
        type=int,
        metavar='N',
        help='Filter by mapper number (e.g., --mapper 1)'
    )
    parser.add_argument(
        '--mirroring',
        choices=['H', 'V', 'F'],
        metavar='TYPE',
        help='Filter by mirroring type: H (horizontal), V (vertical), F (four-screen)'
    )
    parser.add_argument(
        '--min-prg',
        type=int,
        metavar='KB',
        help='Minimum PRG ROM size in KB'
    )
    parser.add_argument(
        '--max-prg',
        type=int,
        metavar='KB',
        help='Maximum PRG ROM size in KB'
    )
    parser.add_argument(
        '--min-chr',
        type=int,
        metavar='KB',
        help='Minimum CHR ROM size in KB'
    )
    parser.add_argument(
        '--max-chr',
        type=int,
        metavar='KB',
        help='Maximum CHR ROM size in KB'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the script.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    args = parse_arguments()
    
    # Validate directory
    directory_path = Path(args.directory)
    
    if not directory_path.exists():
        print(f"Error: Directory does not exist: {args.directory}", file=sys.stderr)
        return 1
    
    if not directory_path.is_dir():
        print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
        return 1
    
    # Scan and process files
    if args.verbose:
        extensions_str = ', '.join(sorted(SUPPORTED_EXTENSIONS))
        print(f"Scanning directory: {directory_path}", file=sys.stderr)
        print(f"Looking for: {extensions_str}", file=sys.stderr)
        if not LIBARCHIVE_AVAILABLE:
            archive_types = ", ".join(sorted(ALL_ARCHIVE_FORMATS))
            print(f"Warning: libarchive not available - archive support ({archive_types}) disabled", file=sys.stderr)
        
        # Show active filters
        filters = []
        if args.has_trainer:
            filters.append("has trainer")
        if args.mapper is not None:
            filters.append(f"mapper={args.mapper}")
        if args.mirroring:
            filters.append(f"mirroring={args.mirroring}")
        if args.min_prg is not None:
            filters.append(f"PRG>={args.min_prg}k")
        if args.max_prg is not None:
            filters.append(f"PRG<={args.max_prg}k")
        if args.min_chr is not None:
            filters.append(f"CHR>={args.min_chr}k")
        if args.max_chr is not None:
            filters.append(f"CHR<={args.max_chr}k")
        
        if filters:
            print(f"Filters: {', '.join(filters)}", file=sys.stderr)
        print()
    
    processed_count = scan_directory(directory_path, 
                                    filter_trainer=args.has_trainer,
                                    show_all_fields=args.show_all,
                                    filter_mapper=args.mapper,
                                    filter_mirroring=args.mirroring,
                                    min_prg_size=args.min_prg,
                                    max_prg_size=args.max_prg,
                                    min_chr_size=args.min_chr,
                                    max_chr_size=args.max_chr)
    
    if args.verbose:
        print(f"\nProcessed {processed_count} ROM files", file=sys.stderr)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

