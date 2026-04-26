# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-26

### Changed

- Improved overwrite checks in `split_rom.py` so only output files that will actually be written are considered.
- Clarified ROM extraction behavior when extra trailing bytes are present after required PRG/CHR data.
- Simplified and made `README.md` easier to read.

### Fixed

- Updated readability check in `split_rom.py`.
- Narrowed exception handling in `parse_ines_header()` to avoid masking unrelated errors.
- Corrected typing annotation in `mappers.py` from `any` to `Any`.
