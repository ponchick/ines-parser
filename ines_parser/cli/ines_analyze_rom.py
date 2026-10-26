#!/usr/bin/env python3
"""
Full analysis of a single iNES ROM file.

Combines three sources of information about one ROM:

- the file itself (size),
- the iNES / NES 2.0 header,
- the filename's naming-convention tags (GoodTools / No-Intro style),

and cross-checks them against each other: file size vs. header sizes,
filename region vs. header TV system, (VS)/(PC10) markers vs. header console
type, [!] verified marker vs. header validity.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ines_parser import (
    INES_HEADER_SIZE,
    INES_TRAINER_SIZE,
    ConsoleType,
    INESFormat,
    INESHeader,
    parse_ines_header,
)
from ines_parser.filename import RomFilenameInfo, expected_tv_system, parse_rom_filename


def format_size(size_bytes: int) -> str:
    return f"{size_bytes} bytes ({size_bytes / 1024:.1f} KiB)"


def analyze_file(path: Path) -> dict[str, Any]:
    """Build the full report dict for one ROM file."""
    file_size = path.stat().st_size
    with open(path, "rb") as f:
        raw_header = f.read(INES_HEADER_SIZE)

    header: INESHeader | None = None
    header_dict: dict[str, Any] | None
    if len(raw_header) < INES_HEADER_SIZE:
        header_dict = {
            "valid": False,
            "error": f"file too short for a {INES_HEADER_SIZE}-byte header",
        }
    else:
        header = parse_ines_header(raw_header)
        header_dict = header.to_dict() if header is not None else None

    name_info = parse_rom_filename(path.name)

    return {
        "schema_version": 1,
        "file": {
            "path": str(path),
            "size_bytes": file_size,
        },
        "filename": name_info.to_dict(),
        "header": header_dict,
        "cross_checks": build_cross_checks(name_info, header, file_size),
        # Runtime-only helpers for the text renderer; stripped from JSON output.
        "_filename_info": name_info,
        "_header_object": header,
    }


def _check(name: str, status: str, detail: str) -> dict[str, str]:
    return {"check": name, "status": status, "detail": detail}


def build_cross_checks(
    name_info: RomFilenameInfo,
    header: INESHeader | None,
    file_size: int,
) -> list[dict[str, str]]:
    """Compare filename facts, header fields and the actual file size."""
    checks: list[dict[str, str]] = []
    header_valid = header is not None and header.is_valid()

    # --- File size vs sizes declared in the header ---
    if header is not None and header.is_valid():
        expected = (
            INES_HEADER_SIZE
            + (INES_TRAINER_SIZE if header.has_trainer else 0)
            + header.prg_rom_size
            + header.chr_rom_size
        )
        parts = [
            f"{INES_HEADER_SIZE} header",
            f"{header.prg_rom_size} PRG",
            f"{header.chr_rom_size} CHR",
        ]
        if header.has_trainer:
            parts.insert(1, f"{INES_TRAINER_SIZE} trainer")
        composition = " + ".join(parts)
        if header.misc_rom_count:
            checks.append(_check(
                "file size vs header",
                "skipped",
                "header declares miscellaneous ROMs of unstated size",
            ))
        elif file_size == expected:
            checks.append(_check(
                "file size vs header", "ok", f"exactly {composition}"
            ))
        elif file_size > expected:
            checks.append(_check(
                "file size vs header",
                "warning",
                f"{file_size - expected} trailing byte(s) beyond {composition}",
            ))
        else:
            checks.append(_check(
                "file size vs header",
                "warning",
                f"file is {expected - file_size} byte(s) shorter than {composition}",
            ))

        # --- Filename region vs header TV system ---
        tv_system = header.tv_system
        if tv_system is not None:
            note = "" if header.format == INESFormat.NES_2_0 else \
                " (iNES 1.0 TV bits are unofficial)"
            expected_tv = expected_tv_system(name_info.regions)
            if not name_info.regions:
                checks.append(_check(
                    "filename region vs TV system",
                    "skipped",
                    "no region tags in the filename",
                ))
            elif expected_tv is None:
                checks.append(_check(
                    "filename region vs TV system",
                    "skipped",
                    f"regions {', '.join(name_info.regions)} do not imply a single TV system",
                ))
            elif tv_system.value not in ("NTSC", "PAL"):
                checks.append(_check(
                    "filename region vs TV system",
                    "skipped",
                    f"header TV system {tv_system.value} is not directly comparable",
                ))
            elif expected_tv == tv_system.value:
                checks.append(_check(
                    "filename region vs TV system",
                    "ok",
                    f"{', '.join(name_info.regions)} imply {expected_tv}; "
                    f"header says {tv_system.value}{note}",
                ))
            else:
                checks.append(_check(
                    "filename region vs TV system",
                    "warning",
                    f"{', '.join(name_info.regions)} imply {expected_tv}, "
                    f"but header says {tv_system.value}{note}",
                ))

        # --- (VS) / (PC10) filename markers vs header console type ---
        header_is_vs = (
            header.console_type == ConsoleType.VS_SYSTEM or header.is_vs_unisystem
        )
        if name_info.is_vs or header_is_vs:
            both = name_info.is_vs and header_is_vs
            checks.append(_check(
                "Vs. System marker vs header console type",
                "ok" if both else "warning",
                "filename (VS) and header console type agree"
                if both
                else "filename (VS) marker" if name_info.is_vs
                else "header console type says Vs. System",
            ))

        header_is_pc10 = (
            header.console_type == ConsoleType.PLAYCHOICE_10 or header.is_playchoice_10
        )
        if name_info.is_playchoice or header_is_pc10:
            both = name_info.is_playchoice and header_is_pc10
            checks.append(_check(
                "PlayChoice-10 marker vs header console type",
                "ok" if both else "warning",
                "filename (PC10) and header console type agree"
                if both
                else "filename (PC10) marker" if name_info.is_playchoice
                else "header console type says PlayChoice-10",
            ))

    # --- [!] verified dump vs header validity ---
    if name_info.verified:
        if header_valid:
            checks.append(_check(
                "verified dump marker vs header",
                "ok",
                "[!] claims a verified dump; header is a valid iNES image",
            ))
        else:
            checks.append(_check(
                "verified dump marker vs header",
                "warning",
                "[!] claims a verified dump, but the header is not a valid iNES image",
            ))

    return checks


def filename_lines(info: RomFilenameInfo) -> list[tuple[str, str]]:
    """(label, value) pairs for the text report; only non-default facts."""
    lines: list[tuple[str, str]] = []

    def add(label: str, value: str) -> None:
        lines.append((label, value))

    if info.regions:
        add("Regions", ", ".join(info.regions))
    if info.languages:
        add("Languages", ", ".join(info.languages))
    add("Dump status", info.dump_status.value)
    extra_flags = [f for f in info.dump_flags if f != info.dump_status.value]
    if extra_flags:
        add("Dump flags", ", ".join(extra_flags))
    if info.is_hack:
        add("Hack", f"yes ({info.hack_tag})" if info.hack_tag else "yes")
    if info.is_translation:
        marker = "+" if info.translation_is_newer else "-"
        language = info.translation_language or "?"
        add("Translation", f"[T{marker}{language}]")
    if info.is_unlicensed:
        add("Unlicensed", "yes")
    if info.is_public_domain:
        add("Public domain", "yes")
    if info.is_vs:
        add("Vs. System", "yes")
    if info.is_playchoice:
        add("PlayChoice-10", "yes")
    if info.is_nintendo_power:
        add("Nintendo Power", "yes")
    if info.multipart_index is not None:
        add("Multipart", str(info.multipart_index))
    if info.prerelease:
        suffix = f" {info.prerelease_index}" if info.prerelease_index else ""
        add("Prerelease", f"{info.prerelease}{suffix}")
    if info.revision:
        add("Revision", info.revision)
    if info.version:
        add("Version", info.version)
    return lines


def print_text_report(report: dict[str, Any]) -> None:
    file_info = report["file"]
    print(f"File: {file_info['path']}")
    print(f"Size: {format_size(file_info['size_bytes'])}")

    name_dict = report["filename"]
    print("\nFilename analysis")
    print(f"  {'Title:':16} {name_dict['title']}")
    for label, value in filename_lines(report["_filename_info"]):
        print(f"  {label + ':':16} {value}")
    if name_dict.get("unknown_tokens"):
        print(f"  {'Unknown tokens:':16} {' '.join(name_dict['unknown_tokens'])}")

    print("\niNES header")
    header_dict = report["header"]
    if header_dict is None:
        print("  no header (file too short)")
    elif not header_dict.get("valid"):
        detail = header_dict.get("error") or header_dict.get("format", "unknown")
        print(f"  not a valid iNES image ({detail})")
    else:
        print(f"  {report['_header_object'].detailed_str()}")

    print("\nCross-checks")
    checks = report["cross_checks"]
    if not checks:
        print("  (none; header not valid or nothing to compare)")
        return
    for check in checks:
        print(f"  {check['status'].upper():8} {check['check']}: {check['detail']}")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ines_analyze_rom.py",
        description="Full analysis of a single ROM: header, filename tags, cross-checks",
    )
    parser.add_argument("rom", metavar="ROM", help="Path to the ROM file (.nes)")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of the text report",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    path = Path(args.rom)
    if not path.exists():
        print(f"Error: File does not exist: {args.rom}", file=sys.stderr)
        return 1
    if not path.is_file():
        print(f"Error: Not a file: {args.rom}", file=sys.stderr)
        return 1

    try:
        report = analyze_file(path)
    except OSError as exc:
        print(f"Error: Cannot read {args.rom}: {exc}", file=sys.stderr)
        return 1

    if args.json:
        public = {k: v for k, v in report.items() if not k.startswith("_")}
        print(json.dumps(public, indent=2))
    else:
        print_text_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
