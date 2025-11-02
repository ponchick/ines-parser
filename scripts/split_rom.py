#!/usr/bin/env python3
"""
Split iNES ROM files into PRG and CHR components.

This script extracts PRG ROM and CHR ROM from iNES format files,
supporting both plain .nes files and .7z archives.
"""

import argparse
import io
import sys
from pathlib import Path
from typing import BinaryIO

# Add parent directory to path for ines_parser package import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import libarchive - make it optional
try:
    import libarchive
    LIBARCHIVE_AVAILABLE = True
except ImportError:
    LIBARCHIVE_AVAILABLE = False

# Import from ines_parser package
from ines_parser import parse_ines_header, INES_HEADER_SIZE, INES_TRAINER_SIZE

# Constants
SUPPORTED_EXTENSIONS = {'.nes'}
if LIBARCHIVE_AVAILABLE:
    ARCHIVE_EXTENSIONS = {'.7z', '.zip', '.rar'}
else:
    ARCHIVE_EXTENSIONS = set()


class ROMExtractionError(Exception):
    """Exception raised when ROM extraction fails."""
    pass


def generate_output_filenames(input_filename: str) -> tuple[str, str]:
    """
    Generate output filenames for PRG and CHR ROM files.
    
    Args:
        input_filename: Input file name
        
    Returns:
        Tuple of (prg_filename, chr_filename)
    """
    path = Path(input_filename)
    
    if path.suffix in SUPPORTED_EXTENSIONS:
        base_name = path.stem
    else:
        base_name = path.name
    
    prg_fname = f"{base_name}.prg.bin"
    chr_fname = f"{base_name}.chr.bin"
    
    return prg_fname, chr_fname


def extract_rom_data(file_name: str, nes_file: BinaryIO) -> None:
    """
    Extract PRG and CHR ROM data from an iNES file.
    
    Args:
        file_name: Name of the ROM file (for output naming)
        nes_file: File-like object containing the ROM data
        
    Raises:
        ROMExtractionError: If extraction fails
    """
    # Parse header
    header_data = nes_file.read(INES_HEADER_SIZE)
    if len(header_data) < INES_HEADER_SIZE:
        raise ROMExtractionError(f"File too short: only {len(header_data)} bytes")
    
    header = parse_ines_header(header_data)
    if not header or not header.is_valid():
        raise ROMExtractionError(f"Not a valid iNES file")
    
    # Generate output filenames
    prg_fname, chr_fname = generate_output_filenames(file_name)
    
    # Calculate expected file size from header
    trainer_size = INES_TRAINER_SIZE if header.has_trainer else 0
    expected_file_size = INES_HEADER_SIZE + trainer_size + header.prg_rom_size + header.chr_rom_size
    
    # Seek to start of ROM data (skip header and optional trainer)
    nes_file.seek(INES_HEADER_SIZE + trainer_size, 0)
    
    # Extract PRG ROM
    if header.prg_rom_size > 0:
        prg_data = nes_file.read(header.prg_rom_size)
        if len(prg_data) < header.prg_rom_size:
            raise ROMExtractionError(
                f"EOF reached while reading PRG part: expected {header.prg_rom_size} bytes, got {len(prg_data)}"
            )
        with open(prg_fname, 'wb') as prg:
            prg.write(prg_data)
        print(f"Extracted PRG ROM: {prg_fname} ({header.prg_rom_size} bytes)")
    
    # Extract CHR ROM
    if header.chr_rom_size > 0:
        chr_data = nes_file.read(header.chr_rom_size)
        if len(chr_data) < header.chr_rom_size:
            raise ROMExtractionError(
                f"EOF reached while reading CHR part: expected {header.chr_rom_size} bytes, got {len(chr_data)}"
            )
        with open(chr_fname, 'wb') as chr_file:
            chr_file.write(chr_data)
        print(f"Extracted CHR ROM: {chr_fname} ({header.chr_rom_size} bytes)")
    
    # Verify we've read the expected amount of data
    actual_position = nes_file.tell()
    if actual_position != expected_file_size:
        raise ROMExtractionError(
            f"File size mismatch: expected {expected_file_size} bytes, got {actual_position} bytes"
        )


def process_archive(filename: str) -> None:
    """
    Process an archive (.7z, .zip, or .rar) and extract the first .nes ROM file.
    
    Args:
        filename: Path to the archive
        
    Raises:
        ROMExtractionError: If processing fails or libarchive not available
    """
    if not LIBARCHIVE_AVAILABLE:
        raise ROMExtractionError("libarchive not available - archive support disabled")
    
    with open(filename, 'rb') as f:
        with libarchive.fd_reader(f.fileno()) as archive:
            # First pass: collect all .nes files
            nes_files = []
            for entry in archive:
                if entry.isfile:
                    entry_path = Path(entry.name)
                    if entry_path.suffix.lower() == '.nes':
                        nes_files.append(entry.name)
            
            if not nes_files:
                raise ROMExtractionError("No .nes files found in archive")
            
            # Warn if multiple .nes files found
            if len(nes_files) > 1:
                print(f"Warning: Found {len(nes_files)} .nes files in archive:", file=sys.stderr)
                for nes_file in nes_files:
                    print(f"  - {nes_file}", file=sys.stderr)
                print(f"Processing only the first file: {nes_files[0]}", file=sys.stderr)
                print(file=sys.stderr)  # Empty line for readability
    
    # Second pass: extract the first .nes file
    with open(filename, 'rb') as f:
        with libarchive.fd_reader(f.fileno()) as archive:
            for entry in archive:
                if entry.isfile:
                    entry_path = Path(entry.name)
                    if entry_path.suffix.lower() == '.nes':
                        # Read all data from the entry efficiently
                        blocks = []
                        for block in entry.get_blocks():
                            blocks.append(block)
                        data = b''.join(blocks)
                        
                        # Create BytesIO object and extract
                        bio = io.BytesIO(data)
                        extract_rom_data(entry.name, bio)
                        return


def process_nes_file(filename: str) -> None:
    """
    Process a plain .nes file.
    
    Args:
        filename: Path to the .nes file
    """
    with open(filename, "rb") as nes_file:
        extract_rom_data(filename, nes_file)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    # Build supported formats string from constants
    all_extensions = SUPPORTED_EXTENSIONS | ARCHIVE_EXTENSIONS
    supported_formats = ", ".join(sorted(all_extensions))
    if not LIBARCHIVE_AVAILABLE:
        supported_formats += " (libarchive not available - archive support disabled)"
    
    parser = argparse.ArgumentParser(
        prog='split_rom.py',
        description='Split iNES ROM files into PRG and CHR components',
        epilog=f"Supported formats: {supported_formats}"
    )
    parser.add_argument(
        'filename',
        help='Input file (.nes or archive)'
    )
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the script.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = parse_arguments()
    
    # Validate input file
    input_path = Path(args.filename)
    
    if not input_path.exists():
        print(f"Error: File does not exist: {args.filename}", file=sys.stderr)
        return 1
    
    if not input_path.is_file():
        print(f"Error: Not a file: {args.filename}", file=sys.stderr)
        return 1
    
    if not input_path.stat().st_mode & 0o400:  # Check read permission
        print(f"Error: File is not readable: {args.filename}", file=sys.stderr)
        return 1
    
    # Process file based on extension
    try:
        file_ext = input_path.suffix.lower()
        
        if file_ext in ARCHIVE_EXTENSIONS:
            if not LIBARCHIVE_AVAILABLE:
                print(f"Error: Cannot process archive files - libarchive not available", file=sys.stderr)
                print("Install libarchive-c: pip install libarchive-c", file=sys.stderr)
                return 1
            process_archive(args.filename)
        elif file_ext == '.nes':
            process_nes_file(args.filename)
        else:
            print(f"Error: Unsupported file extension: {file_ext}", file=sys.stderr)
            all_extensions = SUPPORTED_EXTENSIONS | ARCHIVE_EXTENSIONS
            supported_formats = ", ".join(sorted(all_extensions))
            print(f"Supported formats: {supported_formats}", file=sys.stderr)
            return 1
        
        return 0
        
    except ROMExtractionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
