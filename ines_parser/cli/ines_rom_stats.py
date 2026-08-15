#!/usr/bin/env python3
"""
Aggregate statistics for iNES ROMs found under directories (and inside archives when libarchive is installed).

Currently reports counts per mapper number; the JSON output shape is intended to grow with more metrics later.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import libarchive
except ImportError:
    libarchive = None  # type: ignore

from ines_parser import INES_HEADER_SIZE, parse_ines_header
from ines_parser.tables import get_mapper_name

from ines_parser.cli.rom_fs import (
    ALL_ARCHIVE_FORMATS,
    ARCHIVE_EXTENSIONS,
    LIBARCHIVE_AVAILABLE,
    DEFAULT_ARCHIVE_PATH,
    SUPPORTED_EXTENSIONS,
    collect_supported_files,
    read_header_from_blocks,
)


@dataclass
class RomStats:
    """Counters for one stats run (possibly spanning multiple root directories)."""

    mapper_counts: Counter = field(default_factory=Counter)
    too_short: int = 0
    parse_failed: int = 0
    invalid_format: int = 0
    read_error: int = 0

    def record_header_bytes(self, header_bytes: bytes | None) -> None:
        if header_bytes is None or len(header_bytes) < INES_HEADER_SIZE:
            self.too_short += 1
            return
        header = parse_ines_header(header_bytes)
        if header is None:
            self.parse_failed += 1
            return
        if not header.is_valid():
            self.invalid_format += 1
            return
        self.mapper_counts[header.mapper] += 1

    @property
    def valid_images(self) -> int:
        return int(sum(self.mapper_counts.values()))


def tally_nes_file(file_path: Path, stats: RomStats) -> None:
    try:
        with open(file_path, "rb") as f:
            stats.record_header_bytes(f.read(INES_HEADER_SIZE))
    except OSError:
        stats.read_error += 1


def tally_archive(archive_path: Path, stats: RomStats) -> None:
    if not LIBARCHIVE_AVAILABLE or libarchive is None:
        return
    try:
        with open(archive_path, "rb") as f:
            with libarchive.fd_reader(f.fileno()) as archive:
                for entry in archive:
                    if not entry.isfile:
                        continue
                    if not entry.name.lower().endswith(".nes"):
                        continue
                    stats.record_header_bytes(read_header_from_blocks(entry))
    except OSError:
        stats.read_error += 1
    except Exception:
        stats.read_error += 1


def tally_file(file_path: Path, stats: RomStats) -> None:
    ext = file_path.suffix.lower()
    if ext == ".nes":
        tally_nes_file(file_path, stats)
    elif ext in ARCHIVE_EXTENSIONS:
        tally_archive(file_path, stats)


def tally_directory(directory: Path, stats: RomStats) -> None:
    try:
        paths = collect_supported_files(directory)
        for path in paths:
            tally_file(path, stats)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        raise


def build_report(
    stats: RomStats,
    sort: Literal["count", "mapper"],
    directories: list[str],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for mapper, count in stats.mapper_counts.items():
        rows.append(
            {
                "mapper": mapper,
                "name": get_mapper_name(mapper),
                "count": count,
            }
        )
    if sort == "count":
        rows.sort(key=lambda r: (-r["count"], r["mapper"]))
    else:
        rows.sort(key=lambda r: r["mapper"])

    return {
        "schema_version": 1,
        "directories": directories,
        "totals": {
            "valid_images": stats.valid_images,
            "skipped_too_short": stats.too_short,
            "skipped_parse_failed": stats.parse_failed,
            "skipped_invalid_format": stats.invalid_format,
            "skipped_read_error": stats.read_error,
        },
        "by_mapper": rows,
    }


def print_text_report(report: dict[str, Any]) -> None:
    totals = report["totals"]
    rows = report["by_mapper"]
    print(
        f"Directories: {', '.join(report['directories'])}\n"
        f"Valid iNES images counted: {totals['valid_images']}\n"
        f"Skipped - too short: {totals['skipped_too_short']}, "
        f"parse failed: {totals['skipped_parse_failed']}, "
        f"invalid format: {totals['skipped_invalid_format']}, "
        f"read/archive error: {totals['skipped_read_error']}\n"
    )
    if not rows:
        print("No valid ROM headers found.")
        return
    print(f"{'Mapper':>8}  {'Count':>8}  Name")
    print(f"{'-' * 8}  {'-' * 8}  {'-' * 40}")
    for r in rows:
        print(f"{r['mapper']:>8}  {r['count']:>8}  {r['name']}")


def build_argument_parser() -> argparse.ArgumentParser:
    supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
    if not LIBARCHIVE_AVAILABLE:
        supported += " (libarchive not installed — archive members not scanned)"

    parser = argparse.ArgumentParser(
        prog="ines_rom_stats.py",
        description="Statistics for iNES ROMs under one or more directories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Supported file types: {supported}",
    )
    parser.add_argument(
        "directories",
        nargs="*",
        default=[DEFAULT_ARCHIVE_PATH],
        metavar="DIR",
        help=(
            "Directories to scan recursively (includes archives as containers when supported); "
            f"default if omitted: {DEFAULT_ARCHIVE_PATH}"
        ),
    )
    parser.add_argument(
        "--sort",
        choices=("count", "mapper"),
        default="count",
        help="Sort breakdown by descending count or by mapper number (default: count)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON (includes fields suitable for future extensions)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Log scan roots and extension list to stderr",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    scan_roots: list[Path] = []
    display_dirs: list[str] = []
    for raw in args.directories:
        p = Path(raw)
        if not p.exists():
            print(f"Error: Directory does not exist: {raw}", file=sys.stderr)
            parser.print_help()
            return 1
        if not p.is_dir():
            print(f"Error: Not a directory: {raw}", file=sys.stderr)
            parser.print_help()
            return 1
        scan_roots.append(p)
        display_dirs.append(raw)

    if args.verbose:
        print(f"Scanning {len(scan_roots)} root(s):", file=sys.stderr)
        for r in scan_roots:
            print(f"  {r}", file=sys.stderr)
        print(f"Extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}", file=sys.stderr)
        if not LIBARCHIVE_AVAILABLE:
            print(
                f"Note: without libarchive, archives {sorted(ALL_ARCHIVE_FORMATS)} are ignored.",
                file=sys.stderr,
            )

    stats = RomStats()
    try:
        for root in scan_roots:
            tally_directory(root, stats)
    except KeyboardInterrupt:
        return 130

    report = build_report(stats, args.sort, display_dirs)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text_report(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
