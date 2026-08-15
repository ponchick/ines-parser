<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2026-08-15

### Added

- **`ines_parser.tables`:** unified header lookup tables — mapper names plus Vs. PPU/hardware types, extended console types, default expansion devices, and known NES 2.0 submappers; exposed via `get_*_name` helpers and `INESHeader.to_dict()` (`*_name` fields).
- **`ines_scan_roms.py`:** human-readable field labels in text/CSV/HTML (Title Case, spaces instead of underscores); text pairs numeric ids with names (submapper, Vs., expansion, etc.).
- **Docs:** `docs/List of iNES mappers.md` includes a NES 2.0 submappers table; new `docs/NES 2.0 lookups.md` documents Vs./console/expansion name tables (both mirror `ines_parser/tables.py`).

### Changed

- Mapper database moved into `ines_parser.tables`; `ines_parser.mappers` remains a thin re-export for compatibility.

## [1.3.0] - 2026-08-15

### Added

- **`ines_rom_stats.py`:** summarize mapper usage across directories (and archives); optional `--json`.
- **`ines_scan_roms.py`:** scan multiple directories; export via `--format {text,html,csv,json}` and optional `-o`; CSV `--delimiter` / `-d` (e.g. `;` for Excel RU, `tab` for TSV-style); UTF-8 BOM for CSV; `--show-all` selects the full header field set for every format. Short mode reports sizes in KiB; `--show-all` uses bytes.
- **`ines_parser.mappers`:** names for previously unknown mapper IDs found in the wild (82, 111, 127, 170, 256, 260, 272, 355, 400, 405, 408, 446, 515, 517, 523, 526, 534, 538, 540, 544, 547, 548, 558, 559).

### Deprecated

- **`INESHeader.to_dict()`:** `prg_rom_size_kib` and `chr_rom_size_kib` — use `prg_rom_size // 1024` and `chr_rom_size // 1024` instead. Kept through 1.x; planned removal in 2.0.

## [1.2.1] - 2026-05-03

### Changed

- **`ines_parser.mappers`:** `MAPPER_DATABASE` now covers all mapper numbers listed in MAME’s `nes_ines.hxx` `mmc_list` (plus curated NESdev-style names where they overlap), including many NES 2.0 mapper IDs.
- **Docs:** `docs/List of iNES mappers.md` is a full table aligned with `MAPPER_DATABASE`, with a **Sources** section (NESdev, MAME).

## [1.2.0] - 2026-05-02

### Changed

- **CLI layout:** tools live under `ines_parser.cli` as `ines_scan_roms.py` and `ines_split_rom.py`. `pip install` registers those names on `PATH`; they replace the previous entry points **`ines-scan-roms`** and **`ines-split-rom`**. Without installing, use `python -m ines_parser.cli.…` or run those `.py` files (see `README.md`). The old top-level `scripts` package is removed.
- **`ines_scan_roms.py` (scanner):** show full `--help` when the target path is missing or not a directory; validate PRG and CHR min/max size pairs; discover `.nes`/archive files in one recursive pass with case-insensitive extensions; resolve `__file__` when prepending the repo root to `sys.path`.
- **Terminology:** PRG/CHR sizes in `INESHeader` text output and in `docs/iNES.md` use **KiB** (binary kibibytes) instead of **KB**; CLI help text for size flags uses `KiB` in line with the implementation.

### Fixed

- **`ines_parser.__version__`** now matches the released package version (was out of date).

## [1.1.0] - 2026-04-26

### Changed

- Improved overwrite checks in `split_rom.py` so only output files that will actually be written are considered.
- Clarified ROM extraction behavior when extra trailing bytes are present after required PRG/CHR data.
- Simplified and made `README.md` easier to read.

### Fixed

- Updated readability check in `split_rom.py`.
- Narrowed exception handling in `parse_ines_header()` to avoid masking unrelated errors.
- Corrected typing annotation in `mappers.py` from `any` to `Any`.

[1.4.0]: https://github.com/ponchick/ines-parser/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/ponchick/ines-parser/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/ponchick/ines-parser/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/ponchick/ines-parser/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ponchick/ines-parser/releases/tag/v1.1.0
