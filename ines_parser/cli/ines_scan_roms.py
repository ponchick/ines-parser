#!/usr/bin/env python3
"""
Scan and analyze iNES ROM files from directories and archives.

This script scans one or more directories for ROM files (.nes) and archives
(.7z, .zip, .rar), extracts and analyzes ROM headers, displaying information
about mapper, mirroring, ROM sizes, and other header fields. Supports filtering
and detailed output, plus export to HTML/CSV/JSON.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import html
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

# Repo root on path when running this file directly (not via pip console_scripts)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import libarchive
except ImportError:
    libarchive = None  # type: ignore

from ines_parser import parse_ines_header, INESHeader, INES_HEADER_SIZE

from ines_parser.cli.rom_fs import (
    ALL_ARCHIVE_FORMATS,
    ARCHIVE_EXTENSIONS,
    LIBARCHIVE_AVAILABLE,
    DEFAULT_ARCHIVE_PATH,
    SUPPORTED_EXTENSIONS,
    collect_supported_files,
    read_header_from_blocks,
)

# Path columns always first, then header fields for the selected detail level.
_PATH_COLUMNS = ("path", "archive_member")

# Default (short) list. Size fields use the same names as full, but values are KiB.
_BASIC_COLUMNS = (
    "mapper",
    "mapper_name",
    "mirroring",
    "has_bus_conflicts",
    "prg_rom_size",
    "chr_rom_size",
)

# --show-all (long) list: size fields in bytes.
_FULL_COLUMNS = (
    "format",
    "valid",
    "prg_rom_size",
    "chr_rom_size",
    "prg_ram_size",
    "prg_nvram_size",
    "chr_ram_size",
    "chr_nvram_size",
    "tv_system",
    "mapper",
    "submapper",
    "submapper_name",
    "mapper_name",
    "mapper_alternates",
    "mapper_notes",
    "mirroring",
    "has_battery",
    "has_trainer",
    "four_screen",
    "is_vs_unisystem",
    "is_playchoice_10",
    "console_type",
    "cpu_timing",
    "vs_ppu_type",
    "vs_ppu_type_name",
    "vs_hw_type",
    "vs_hw_type_name",
    "extended_console_type",
    "extended_console_type_name",
    "misc_rom_count",
    "expansion_device",
    "expansion_device_name",
    "has_bus_conflicts",
)

# Human-facing labels for text / CSV / HTML (JSON keeps internal keys).
_COLUMN_LABELS = {
    "path": "Path",
    "archive_member": "Archive Member",
    "format": "Format",
    "valid": "Valid",
    "prg_rom_size": "PRG ROM Size",
    "chr_rom_size": "CHR ROM Size",
    "prg_ram_size": "PRG RAM Size",
    "prg_nvram_size": "PRG NVRAM Size",
    "chr_ram_size": "CHR RAM Size",
    "chr_nvram_size": "CHR NVRAM Size",
    "tv_system": "TV System",
    "mapper": "Mapper",
    "submapper": "Submapper",
    "submapper_name": "Submapper Name",
    "mapper_name": "Mapper Name",
    "mapper_alternates": "Mapper Alternates",
    "mapper_notes": "Mapper Notes",
    "mirroring": "Mirroring",
    "has_battery": "Has Battery",
    "has_trainer": "Has Trainer",
    "four_screen": "Four Screen",
    "is_vs_unisystem": "Vs Unisystem",
    "is_playchoice_10": "PlayChoice-10",
    "console_type": "Console Type",
    "cpu_timing": "CPU Timing",
    "vs_ppu_type": "Vs PPU Type",
    "vs_ppu_type_name": "Vs PPU Type Name",
    "vs_hw_type": "Vs Hardware Type",
    "vs_hw_type_name": "Vs Hardware Type Name",
    "extended_console_type": "Extended Console Type",
    "extended_console_type_name": "Extended Console Type Name",
    "misc_rom_count": "Misc ROM Count",
    "expansion_device": "Expansion Device",
    "expansion_device_name": "Expansion Device Name",
    "has_bus_conflicts": "Has Bus Conflicts",
}

# Numeric id + companion name key (paired in text export like mapper).
_ID_NAME_PAIRS = {
    "mapper": "mapper_name",
    "submapper": "submapper_name",
    "vs_ppu_type": "vs_ppu_type_name",
    "vs_hw_type": "vs_hw_type_name",
    "extended_console_type": "extended_console_type_name",
    "expansion_device": "expansion_device_name",
}


def _is_size_key(key: str) -> bool:
    """True for header size fields (bytes in to_dict; KiB in short mode)."""
    return key.endswith("_size")


def _friendly_label(key: str) -> str:
    """Human-readable column / field label (Title Case, no underscores)."""
    if key in _COLUMN_LABELS:
        return _COLUMN_LABELS[key]
    return key.replace("_", " ").title()


def _header_columns(show_all: bool) -> tuple[str, ...]:
    return _FULL_COLUMNS if show_all else _BASIC_COLUMNS


def _flatten_cell(value: Any) -> str:
    """Convert a cell value to a string suitable for CSV/TSV/HTML."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return "; ".join(str(item) for item in value)
    return str(value)


def _collect_columns(rows: Sequence[dict[str, Any]], show_all: bool) -> list[str]:
    """Return column names in stable order for the selected field set."""
    header_cols = _header_columns(show_all)
    if not show_all:
        # Fixed headers so basic CSV always has the same shape as text summary.
        return list(_PATH_COLUMNS) + list(header_cols)

    columns = list(_PATH_COLUMNS)
    for key in header_cols:
        if any(key in row and row[key] is not None for row in rows):
            columns.append(key)
    known = set(_PATH_COLUMNS) | set(header_cols)
    extras = sorted({k for row in rows for k in row if k not in known})
    columns.extend(extras)
    return columns


def _write_csv(
    rows: Sequence[dict[str, Any]],
    out: TextIO,
    show_all: bool,
    *,
    delimiter: str = ",",
) -> None:
    columns = _collect_columns(rows, show_all)
    labels = [_friendly_label(col) for col in columns]
    writer = csv.DictWriter(out, fieldnames=labels, delimiter=delimiter, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {_friendly_label(col): _flatten_cell(row.get(col)) for col in columns}
        )


def _write_json(rows: Sequence[dict[str, Any]], out: TextIO, show_all: bool) -> None:
    columns = _collect_columns(rows, show_all)
    payload = []
    for row in rows:
        item: dict[str, Any] = {}
        for key in columns:
            if key not in row:
                continue
            value = row[key]
            if value is None:
                continue
            item[key] = value
        payload.append(item)
    json.dump(payload, out, indent=2, ensure_ascii=False)
    out.write("\n")


def _write_html(rows: Sequence[dict[str, Any]], out: TextIO, show_all: bool) -> None:
    columns = _collect_columns(rows, show_all)
    out.write("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n")
    out.write('<meta charset="utf-8">\n')
    out.write("<title>iNES ROM scan</title>\n")
    out.write("<style>\n")
    out.write(
        "body{font-family:system-ui,sans-serif;margin:1.5rem;"
        "background:#f8f9fa;color:#212529}\n"
    )
    out.write("h1{font-size:1.25rem;margin:0 0 1rem}\n")
    out.write(
        "table{border-collapse:collapse;width:100%;background:#fff;"
        "box-shadow:0 1px 3px rgba(0,0,0,.08)}\n"
    )
    out.write(
        "th,td{border:1px solid #dee2e6;padding:.4rem .55rem;"
        "text-align:left;vertical-align:top;font-size:.875rem}\n"
    )
    out.write("th{background:#e9ecef;position:sticky;top:0}\n")
    out.write("tr:nth-child(even){background:#f1f3f5}\n")
    out.write("caption{text-align:left;margin-bottom:.5rem;color:#495057}\n")
    out.write("</style>\n</head>\n<body>\n")
    out.write("<h1>iNES ROM scan</h1>\n")
    out.write(f"<table>\n<caption>{len(rows)} ROM(s)</caption>\n<thead>\n<tr>\n")
    for col in columns:
        out.write(f"<th>{html.escape(_friendly_label(col))}</th>\n")
    out.write("</tr>\n</thead>\n<tbody>\n")
    for row in rows:
        out.write("<tr>\n")
        for col in columns:
            out.write(f"<td>{html.escape(_flatten_cell(row.get(col)))}</td>\n")
        out.write("</tr>\n")
    out.write("</tbody>\n</table>\n</body>\n</html>\n")


def _resolve_delimiter(value: str) -> str | None:
    """Return a one-character delimiter, or None if *value* is invalid."""
    if value.lower() == "tab" or value == "\\t":
        return "\t"
    if len(value) == 1:
        return value
    return None


def write_export(
    fmt: str,
    rows: Sequence[dict[str, Any]],
    out: TextIO,
    show_all: bool = False,
    delimiter: str = ",",
) -> None:
    """Dispatch to the appropriate format writer."""
    if fmt == "text":
        _write_text(rows, out, show_all)
    elif fmt == "csv":
        _write_csv(rows, out, show_all, delimiter=delimiter)
    elif fmt == "json":
        _write_json(rows, out, show_all)
    elif fmt == "html":
        _write_html(rows, out, show_all)
    else:
        raise ValueError(f"Unsupported export format: {fmt}")


def _write_text(
    rows: Sequence[dict[str, Any]], out: TextIO, show_all: bool
) -> None:
    for row in rows:
        path = row.get("path", "")
        member = row.get("archive_member") or ""
        body = _format_row_text(row, show_all)
        if member:
            out.write(f"{path}:{member}: {body}\n")
        else:
            out.write(f"{path}: {body}\n")


def open_export_stream(path: str | None, fmt: str):
    """
    Open output file or yield stdout.

    CSV uses utf-8-sig so Excel on Windows recognizes Unicode correctly.
    """
    encoding = "utf-8-sig" if fmt == "csv" else "utf-8"

    @contextlib.contextmanager
    def _cm():
        if path is None:
            if fmt == "csv":
                sys.stdout.write("\ufeff")
            yield sys.stdout
        else:
            with open(path, "w", encoding=encoding, newline="") as f:
                yield f

    return _cm()


def _format_row_text(row: dict[str, Any], show_all: bool = False) -> str:
    """Render a collected row as a human-readable comma-separated line."""
    parts: list[str] = []
    skip: set[str] = set()

    for key in _header_columns(show_all):
        if key in skip:
            continue

        name_key = _ID_NAME_PAIRS.get(key)
        if name_key is not None:
            id_value = row.get(key)
            name = row.get(name_key)
            if id_value is None:
                continue
            label = _friendly_label(key)
            if name:
                parts.append(f"{label}: {id_value} ({name})")
                skip.add(name_key)
            else:
                parts.append(f"{label}: {id_value}")
            continue

        value = row.get(key)
        if value is None:
            continue
        if value == "" or value == []:
            continue

        label = _friendly_label(key)

        if _is_size_key(key):
            if not isinstance(value, int):
                continue
            if not show_all:
                if key == "chr_rom_size" and not value:
                    continue
                if key == "prg_rom_size":
                    parts.append(f"PRG: {value} KiB")
                elif key == "chr_rom_size":
                    parts.append(f"CHR: {value} KiB")
                elif value:
                    parts.append(f"{label}: {value} KiB")
            else:
                if key not in ("prg_rom_size", "chr_rom_size") and not value:
                    continue
                parts.append(f"{label}: {value} bytes")
        elif isinstance(value, bool):
            if value:
                short = (
                    key.removeprefix("is_")
                    .removeprefix("has_")
                    .replace("_", " ")
                    .title()
                )
                parts.append(short)
        else:
            parts.append(f"{label}: {_flatten_cell(value)}")

    return ", ".join(parts)


def matches_filters(
    header: INESHeader,
    filter_trainer: bool = False,
    filter_mapper: int | None = None,
    filter_mirroring: str | None = None,
    min_prg_size: int | None = None,
    max_prg_size: int | None = None,
    min_chr_size: int | None = None,
    max_chr_size: int | None = None,
) -> bool:
    """
    Check if ROM header matches all specified filters.

    Args:
        header: Parsed iNES header
        filter_trainer: If True, only accept ROMs with trainer
        filter_mapper: If specified, only accept this mapper number
        filter_mirroring: If specified, only accept this mirroring type (H/V/F)
        min_prg_size: Minimum PRG ROM size in KiB
        max_prg_size: Maximum PRG ROM size in KiB
        min_chr_size: Minimum CHR ROM size in KiB
        max_chr_size: Maximum CHR ROM size in KiB

    Returns:
        True if ROM matches all filters
    """
    if not header.is_valid():
        return False

    if filter_trainer and not header.has_trainer:
        return False

    if filter_mapper is not None and header.mapper != filter_mapper:
        return False

    if filter_mirroring is not None and header.mirroring.value != filter_mirroring:
        return False

    prg_size_kib = header.prg_rom_size // 1024
    if min_prg_size is not None and prg_size_kib < min_prg_size:
        return False
    if max_prg_size is not None and prg_size_kib > max_prg_size:
        return False

    chr_size_kib = header.chr_rom_size // 1024
    if min_chr_size is not None and chr_size_kib < min_chr_size:
        return False
    if max_chr_size is not None and chr_size_kib > max_chr_size:
        return False

    return True


def _emit_message(message: str) -> None:
    """Print a status/error line to stderr (keeps stdout clean for -o)."""
    print(message, file=sys.stderr)


def _row_from_header(
    path: str,
    header: INESHeader,
    archive_member: str = "",
    show_all: bool = False,
) -> dict[str, Any]:
    data = header.to_dict()
    row: dict[str, Any] = {"path": path, "archive_member": archive_member}
    for key in _header_columns(show_all):
        if key not in data:
            continue
        value = data[key]
        # Short mode: all size fields as KiB (same keys, // 1024).
        if not show_all and _is_size_key(key) and isinstance(value, int):
            value = value // 1024
        row[key] = value
    return row


def process_nes_file(
    file_path: Path,
    base_path: Path,
    filter_trainer: bool = False,
    filter_mapper: int | None = None,
    filter_mirroring: str | None = None,
    min_prg_size: int | None = None,
    max_prg_size: int | None = None,
    min_chr_size: int | None = None,
    max_chr_size: int | None = None,
    *,
    rows: list[dict[str, Any]] | None = None,
    show_all: bool = False,
) -> bool:
    """
    Process a plain .nes file and display or collect ROM information.

    Returns:
        True if processing succeeded (and matched filters), False otherwise
    """
    relative_path = file_path.relative_to(base_path)
    rel = str(relative_path)

    try:
        with open(file_path, "rb") as f:
            header_bytes = f.read(INES_HEADER_SIZE)

            if len(header_bytes) < INES_HEADER_SIZE:
                _emit_message(
                    f"{rel}: File too short (less than {INES_HEADER_SIZE} bytes)",
                )
                return False

            header = parse_ines_header(header_bytes)

            if not header:
                _emit_message(f"{rel}: Failed to parse header")
                return False

            if not matches_filters(
                header,
                filter_trainer,
                filter_mapper,
                filter_mirroring,
                min_prg_size,
                max_prg_size,
                min_chr_size,
                max_chr_size,
            ):
                return False

            assert rows is not None
            rows.append(_row_from_header(rel, header, show_all=show_all))
            return True

    except Exception as e:
        _emit_message(f"{rel}: Error reading file: {e}")
        return False


def process_archive(
    archive_path: Path,
    base_path: Path,
    filter_trainer: bool = False,
    filter_mapper: int | None = None,
    filter_mirroring: str | None = None,
    min_prg_size: int | None = None,
    max_prg_size: int | None = None,
    min_chr_size: int | None = None,
    max_chr_size: int | None = None,
    *,
    rows: list[dict[str, Any]] | None = None,
    show_all: bool = False,
) -> int:
    """
    Process an archive and display or collect ROM information for all .nes files.

    Returns:
        Number of successfully processed files in the archive
    """
    if not LIBARCHIVE_AVAILABLE:
        return 0

    relative_path = archive_path.relative_to(base_path)
    rel = str(relative_path)
    nes_files_found = 0
    processed_count = 0

    try:
        with open(archive_path, "rb") as f:
            with libarchive.fd_reader(f.fileno()) as archive:
                for entry in archive:
                    if entry.isfile:
                        entry_name = entry.name.lower()
                        if not entry_name.endswith(".nes"):
                            continue

                        nes_files_found += 1

                        header_bytes = read_header_from_blocks(entry)

                        if not header_bytes:
                            _emit_message(
                                f"{rel}:{entry.name}: File too short "
                                f"(less than {INES_HEADER_SIZE} bytes)",
                            )
                            continue

                        header = parse_ines_header(header_bytes)

                        if not header:
                            _emit_message(
                                f"{rel}:{entry.name}: Failed to parse header",
                            )
                            continue

                        if not matches_filters(
                            header,
                            filter_trainer,
                            filter_mapper,
                            filter_mirroring,
                            min_prg_size,
                            max_prg_size,
                            min_chr_size,
                            max_chr_size,
                        ):
                            continue

                        assert rows is not None
                        rows.append(
                            _row_from_header(
                                rel,
                                header,
                                archive_member=entry.name,
                                show_all=show_all,
                            )
                        )
                        processed_count += 1

                if nes_files_found == 0:
                    _emit_message(
                        f"{rel}: No .nes files found in archive",
                    )

                return processed_count

    except Exception as e:
        _emit_message(f"{rel}: Error reading archive: {e}")
        return 0


def process_file(
    file_path: Path,
    base_path: Path,
    filter_trainer: bool = False,
    filter_mapper: int | None = None,
    filter_mirroring: str | None = None,
    min_prg_size: int | None = None,
    max_prg_size: int | None = None,
    min_chr_size: int | None = None,
    max_chr_size: int | None = None,
    *,
    rows: list[dict[str, Any]] | None = None,
    show_all: bool = False,
) -> int:
    """
    Process a file based on its extension.

    Returns:
        Number of successfully processed ROM files (1 for .nes, N for archives)
    """
    ext = file_path.suffix.lower()

    if ext == ".nes":
        return (
            1
            if process_nes_file(
                file_path,
                base_path,
                filter_trainer,
                filter_mapper,
                filter_mirroring,
                min_prg_size,
                max_prg_size,
                min_chr_size,
                max_chr_size,
                rows=rows,
                show_all=show_all,
            )
            else 0
        )
    if ext in ARCHIVE_EXTENSIONS:
        return process_archive(
            file_path,
            base_path,
            filter_trainer,
            filter_mapper,
            filter_mirroring,
            min_prg_size,
            max_prg_size,
            min_chr_size,
            max_chr_size,
            rows=rows,
            show_all=show_all,
        )
    return 0


def scan_directory(
    directory: Path,
    filter_trainer: bool = False,
    filter_mapper: int | None = None,
    filter_mirroring: str | None = None,
    min_prg_size: int | None = None,
    max_prg_size: int | None = None,
    min_chr_size: int | None = None,
    max_chr_size: int | None = None,
    *,
    rows: list[dict[str, Any]] | None = None,
    show_all: bool = False,
) -> int:
    """
    Scan a directory for ROM files and archives, and process them.

    Returns:
        Number of successfully processed ROM files (counts individual ROMs in archives)
    """
    all_files = collect_supported_files(directory)

    if not all_files:
        extensions_str = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        print(
            f"No files found with extensions {extensions_str} in {directory}",
            file=sys.stderr,
        )
        return 0

    processed_count = 0

    for file_path in all_files:
        processed_count += process_file(
            file_path,
            directory,
            filter_trainer,
            filter_mapper,
            filter_mirroring,
            min_prg_size,
            max_prg_size,
            min_chr_size,
            max_chr_size,
            rows=rows,
            show_all=show_all,
        )

    return processed_count


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    supported_types = ", ".join(sorted(SUPPORTED_EXTENSIONS))
    if not LIBARCHIVE_AVAILABLE:
        supported_types += " (libarchive not available - archive support disabled)"

    parser = argparse.ArgumentParser(
        prog="ines_scan_roms.py",
        description="Scan and analyze iNES ROM files from directories and archives",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported: {supported_types}

Examples:
  %(prog)s /path/to/roms
  %(prog)s /path/to/roms --mapper 4 --show-all
  %(prog)s /path/to/roms --format csv -o roms.csv
  %(prog)s /path/to/roms --format csv -d ';' -o roms.csv
  %(prog)s /path/to/roms --format csv --show-all -o roms-full.csv
        """,
    )
    parser.add_argument(
        "directories",
        nargs="*",
        default=[DEFAULT_ARCHIVE_PATH],
        metavar="DIR",
        help=f"Scan roots (default: {DEFAULT_ARCHIVE_PATH})",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose progress on stderr",
    )
    parser.add_argument(
        "--has-trainer",
        action="store_true",
        help="Only ROMs with trainer",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Full header fields (all output formats)",
    )
    parser.add_argument(
        "--mapper",
        type=int,
        metavar="N",
        help="Filter by mapper number",
    )
    parser.add_argument(
        "--mirroring",
        choices=["H", "V", "F"],
        metavar="TYPE",
        help="Filter mirroring: H, V, or F",
    )
    parser.add_argument(
        "--min-prg",
        type=int,
        metavar="KiB",
        help="Min PRG ROM size (KiB)",
    )
    parser.add_argument(
        "--max-prg",
        type=int,
        metavar="KiB",
        help="Max PRG ROM size (KiB)",
    )
    parser.add_argument(
        "--min-chr",
        type=int,
        metavar="KiB",
        help="Min CHR ROM size (KiB)",
    )
    parser.add_argument(
        "--max-chr",
        type=int,
        metavar="KiB",
        help="Max CHR ROM size (KiB)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "html", "csv", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        metavar="SEP",
        default=",",
        help="CSV field delimiter (default: ,). Use ';' for Excel RU, tab for TSV",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="Write output to PATH (all formats)",
    )

    return parser


def main() -> int:
    """
    Main entry point for the script.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = build_argument_parser()
    args = parser.parse_args()

    if (
        args.min_prg is not None
        and args.max_prg is not None
        and args.min_prg > args.max_prg
    ):
        print(
            "Error: --min-prg cannot be greater than --max-prg",
            file=sys.stderr,
        )
        parser.print_help()
        return 1

    if (
        args.min_chr is not None
        and args.max_chr is not None
        and args.min_chr > args.max_chr
    ):
        print(
            "Error: --min-chr cannot be greater than --max-chr",
            file=sys.stderr,
        )
        parser.print_help()
        return 1

    delimiter = _resolve_delimiter(args.delimiter)
    if delimiter is None:
        print(
            "Error: --delimiter must be a single character, or 'tab'",
            file=sys.stderr,
        )
        return 1

    if args.format != "csv" and args.delimiter != ",":
        print(
            "Error: --delimiter is only valid with --format csv",
            file=sys.stderr,
        )
        return 1


    scan_roots: list[Path] = []
    for raw in args.directories:
        directory_path = Path(raw)
        if not directory_path.exists():
            print(f"Error: Directory does not exist: {raw}", file=sys.stderr)
            parser.print_help()
            return 1
        if not directory_path.is_dir():
            print(f"Error: Not a directory: {raw}", file=sys.stderr)
            parser.print_help()
            return 1
        scan_roots.append(directory_path)

    rows: list[dict[str, Any]] = []
    processed_count = 0

    if args.verbose:
        extensions_str = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        print(
            f"Scanning {len(scan_roots)} director"
            f"{'ies' if len(scan_roots) != 1 else 'y'}:",
            file=sys.stderr,
        )
        for root in scan_roots:
            print(f"  {root}", file=sys.stderr)
        print(f"Looking for: {extensions_str}", file=sys.stderr)
        if not LIBARCHIVE_AVAILABLE:
            archive_types = ", ".join(sorted(ALL_ARCHIVE_FORMATS))
            print(
                f"Warning: libarchive not available - archive support "
                f"({archive_types}) disabled",
                file=sys.stderr,
            )

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
        print(f"Format: {args.format}", file=sys.stderr)
        if args.show_all:
            print("Fields: full", file=sys.stderr)
        print(file=sys.stderr)

    try:
        for directory_path in scan_roots:
            processed_count += scan_directory(
                directory_path,
                filter_trainer=args.has_trainer,
                filter_mapper=args.mapper,
                filter_mirroring=args.mirroring,
                min_prg_size=args.min_prg,
                max_prg_size=args.max_prg,
                min_chr_size=args.min_chr,
                max_chr_size=args.max_chr,
                rows=rows,
                show_all=args.show_all,
            )

        with open_export_stream(args.output, args.format) as out:
            write_export(
                args.format,
                rows,
                out,
                show_all=args.show_all,
                delimiter=delimiter,
            )
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130

    if args.verbose:
        print(f"\nProcessed {processed_count} ROM files", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
