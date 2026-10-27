#!/usr/bin/env python3
"""
Split iNES ROM files into PRG and CHR components.

This script extracts PRG ROM and CHR ROM from iNES format files,
supporting both plain .nes files and .7z archives. Outputs can be cloned
up to a target size (e.g. an EPROM like 27C512) with --pad-prg / --pad-chr.
"""

import argparse
import io
import os
import sys
from pathlib import Path
from typing import BinaryIO, Optional, Tuple

# Repo root on path when running this file directly (not via pip console_scripts)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Try to import libarchive - make it optional
try:
    import libarchive
except ImportError:
    libarchive = None  # type: ignore

# Import from ines_parser package
from ines_parser import parse_ines_header, INES_HEADER_SIZE, INES_TRAINER_SIZE

# Constants
SUPPORTED_EXTENSIONS = {'.nes'}
ALL_ARCHIVE_EXTENSIONS = {'.7z', '.zip', '.rar'}
ARCHIVE_EXTENSIONS = ALL_ARCHIVE_EXTENSIONS if libarchive is not None else set()


class ROMExtractionError(Exception):
    """Exception raised when ROM extraction fails."""
    pass


def mirror_to(data: bytes, target_size: int, label: str) -> bytes:
    """
    Repeat ``data`` until it fills ``target_size``.

    Useful when burning onto a larger EPROM: with the image cloned across the
    whole chip, the data is the same whatever the upper address lines read.
    The target must be an integer multiple of the image size (or equal to it).
    """
    if target_size < len(data):
        raise ROMExtractionError(
            f"{label} is {len(data)} bytes; cannot pad down to {target_size}"
        )
    if target_size == len(data):
        return data
    if target_size % len(data) != 0:
        raise ROMExtractionError(
            f"{label} is {len(data)} bytes; {target_size} is not an integer multiple, "
            "cannot mirror evenly"
        )
    return data * (target_size // len(data))


def apply_padding(data: bytes, target_kib: int, label: str) -> Tuple[bytes, str]:
    """Clone ``data`` up to ``target_kib``; returns (data, output note)."""
    result = mirror_to(data, target_kib * 1024, label)
    if len(result) == len(data):
        return result, ""
    return result, f", mirrored to {len(result)}"


def generate_output_filenames(input_filename: str) -> Tuple[str, str]:
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


def check_overwrite_permission(prg_fname: str, chr_fname: str, force: bool,
                              write_prg: bool = True, write_chr: bool = True) -> bool:
    """
    Check if output files exist and get user permission to overwrite.
    
    Args:
        prg_fname: PRG output filename
        chr_fname: CHR output filename
        force: If True, skip confirmation and allow overwrite
        write_prg: If True, PRG output file will be written
        write_chr: If True, CHR output file will be written
        
    Returns:
        True if overwrite is allowed, False otherwise
    """
    prg_exists = write_prg and Path(prg_fname).exists()
    chr_exists = write_chr and Path(chr_fname).exists()
    
    if not (prg_exists or chr_exists):
        return True  # No files to overwrite
    
    if force:
        return True  # Force overwrite
    
    # Check if we're in an interactive terminal
    if not sys.stdin.isatty():
        # Not interactive, print error and exit
        existing_files = []
        if prg_exists:
            existing_files.append(prg_fname)
        if chr_exists:
            existing_files.append(chr_fname)
        print(f"Error: Output files already exist: {', '.join(existing_files)}", file=sys.stderr)
        print("Use --force to overwrite existing files", file=sys.stderr)
        return False
    
    # Interactive mode - ask for confirmation
    existing_files = []
    if prg_exists:
        existing_files.append(prg_fname)
    if chr_exists:
        existing_files.append(chr_fname)
    
    print(f"Warning: Output files already exist: {', '.join(existing_files)}", file=sys.stderr)
    try:
        response = input("Overwrite existing files? [y/N]: ").strip().lower()
    except KeyboardInterrupt:
        # User pressed Ctrl-C, exit gracefully
        print(file=sys.stderr)  # New line after ^C
        sys.exit(130)  # Standard exit code for SIGINT
    
    return response in ('y', 'yes')


def extract_rom_data(
    file_name: str,
    nes_file: BinaryIO,
    force: bool = False,
    pad_prg_kib: Optional[int] = None,
    pad_chr_kib: Optional[int] = None,
) -> None:
    """
    Extract PRG and CHR ROM data from an iNES file.

    Args:
        file_name: Name of the ROM file (for output naming)
        nes_file: File-like object containing the ROM data
        force: If True, overwrite existing files without confirmation
        pad_prg_kib: Clone the PRG output up to this size in KiB (None keeps it as-is)
        pad_chr_kib: Clone the CHR output up to this size in KiB (None keeps it as-is)

    Raises:
        ROMExtractionError: If extraction fails or overwrite denied
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
    
    # Check if files exist and get permission to overwrite
    if not check_overwrite_permission(
        prg_fname,
        chr_fname,
        force,
        write_prg=header.prg_rom_size > 0,
        write_chr=header.chr_rom_size > 0
    ):
        raise ROMExtractionError("Overwrite cancelled by user")
    
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
        prg_note = ""
        if pad_prg_kib is not None:
            prg_data, prg_note = apply_padding(prg_data, pad_prg_kib, "PRG ROM")
        with open(prg_fname, 'wb') as prg:
            prg.write(prg_data)
        print(f"Extracted PRG ROM: {prg_fname} ({header.prg_rom_size} bytes{prg_note})")
    elif pad_prg_kib is not None:
        raise ROMExtractionError("--pad-prg given, but this ROM has no PRG ROM")

    # Extract CHR ROM
    if header.chr_rom_size > 0:
        chr_data = nes_file.read(header.chr_rom_size)
        if len(chr_data) < header.chr_rom_size:
            raise ROMExtractionError(
                f"EOF reached while reading CHR part: expected {header.chr_rom_size} bytes, got {len(chr_data)}"
            )
        chr_note = ""
        if pad_chr_kib is not None:
            chr_data, chr_note = apply_padding(chr_data, pad_chr_kib, "CHR ROM")
        with open(chr_fname, 'wb') as chr_file:
            chr_file.write(chr_data)
        print(f"Extracted CHR ROM: {chr_fname} ({header.chr_rom_size} bytes{chr_note})")
    elif pad_chr_kib is not None:
        raise ROMExtractionError("--pad-chr given, but this ROM has no CHR ROM (CHR-RAM game?)")
    
    # Verify we've read at least the expected amount of data.
    # Extra trailing data is allowed, but we report it for visibility.
    actual_position = nes_file.tell()
    if actual_position < expected_file_size:
        raise ROMExtractionError(
            f"File ended early: expected to read {expected_file_size} bytes, read {actual_position} bytes"
        )
    extra_data = nes_file.read(1)
    if extra_data:
        print(
            "Warning: Required ROM data was read successfully, "
            "but file contains additional trailing bytes",
            file=sys.stderr
        )


def process_archive(
    filename: str,
    force: bool = False,
    pad_prg_kib: Optional[int] = None,
    pad_chr_kib: Optional[int] = None,
) -> None:
    """
    Process an archive (.7z, .zip, or .rar) and extract the first .nes ROM file.

    Args:
        filename: Path to the archive
        force: If True, overwrite existing files without confirmation
        pad_prg_kib: Clone the PRG output up to this size in KiB (None keeps it as-is)
        pad_chr_kib: Clone the CHR output up to this size in KiB (None keeps it as-is)

    Raises:
        ROMExtractionError: If processing fails or libarchive not available
    """
    if libarchive is None:
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
                        extract_rom_data(entry.name, bio, force, pad_prg_kib, pad_chr_kib)
                        return


def process_nes_file(
    filename: str,
    force: bool = False,
    pad_prg_kib: Optional[int] = None,
    pad_chr_kib: Optional[int] = None,
) -> None:
    """
    Process a plain .nes file.

    Args:
        filename: Path to the .nes file
        force: If True, overwrite existing files without confirmation
        pad_prg_kib: Clone the PRG output up to this size in KiB (None keeps it as-is)
        pad_chr_kib: Clone the CHR output up to this size in KiB (None keeps it as-is)
    """
    with open(filename, "rb") as nes_file:
        extract_rom_data(filename, nes_file, force, pad_prg_kib, pad_chr_kib)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    # Build supported formats string from constants
    all_extensions = SUPPORTED_EXTENSIONS | ARCHIVE_EXTENSIONS
    supported_formats = ", ".join(sorted(all_extensions))
    if libarchive is None:
        supported_formats += " (libarchive not available - archive support disabled)"
    
    parser = argparse.ArgumentParser(
        prog='ines_split_rom.py',
        description='Split iNES ROM files into PRG and CHR components',
        epilog=f"Supported formats: {supported_formats}"
    )
    parser.add_argument(
        'filename',
        help='Input file (.nes or archive)'
    )
    parser.add_argument(
        '--force',
        '-f',
        action='store_true',
        help='Overwrite existing output files without confirmation'
    )
    parser.add_argument(
        '--pad-prg',
        type=int,
        metavar='KIB',
        help=(
            'Clone the PRG image up to this size in KiB (e.g. 64 for a 27C512 EPROM); '
            'the target must be an integer multiple of the image size, never truncates'
        )
    )
    parser.add_argument(
        '--pad-chr',
        type=int,
        metavar='KIB',
        help=(
            'Clone the CHR image up to this size in KiB (e.g. 64 for a 27C512 EPROM); '
            'the target must be an integer multiple of the image size, never truncates'
        )
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
    
    if not os.access(input_path, os.R_OK):
        print(f"Error: File is not readable: {args.filename}", file=sys.stderr)
        return 1
    
    # Process file based on extension
    try:
        file_ext = input_path.suffix.lower()
        
        if file_ext in ALL_ARCHIVE_EXTENSIONS:
            if libarchive is None:
                print(f"Error: Unsupported file extension: {file_ext}", file=sys.stderr)
                print("For archive format support, install libarchive-c: pip install libarchive-c", file=sys.stderr)
                return 1
            process_archive(
                args.filename,
                force=args.force,
                pad_prg_kib=args.pad_prg,
                pad_chr_kib=args.pad_chr,
            )
        elif file_ext == '.nes':
            process_nes_file(
                args.filename,
                force=args.force,
                pad_prg_kib=args.pad_prg,
                pad_chr_kib=args.pad_chr,
            )
        else:
            print(f"Error: Unsupported file extension: {file_ext}", file=sys.stderr)
            all_extensions = SUPPORTED_EXTENSIONS | ARCHIVE_EXTENSIONS
            supported_formats = ", ".join(sorted(all_extensions))
            print(f"Supported formats: {supported_formats}", file=sys.stderr)
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        # User pressed Ctrl-C, exit gracefully
        print(file=sys.stderr)  # New line after ^C
        return 130  # Standard exit code for SIGINT
    except ROMExtractionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
