# iNES Parser

Lightweight Python library and CLI tools for working with NES ROMs in iNES/NES 2.0 format.

Supported versions: Python 3.10-3.14.

## Quick Start

```bash
git clone https://github.com/ponchick/ines-parser.git
cd ines-parser
```

The `ines_parser` core has no external dependencies.  
Archive support (`.7z/.zip/.rar`) requires `libarchive-c`.

## What It Does

- parses ROM headers (`mapper`, PRG/CHR sizes, mirroring, and more)
- scans ROM directories with filters
- splits ROM files into `PRG` and `CHR` binaries

## CLI

### `scan_roms.py` - scan ROM files

```bash
# Basic scan
./scripts/scan_roms.py /path/to/roms

# Only mapper 4
./scripts/scan_roms.py /path/to/roms --mapper 4

# Show more fields
./scripts/scan_roms.py /path/to/roms --show-all
```

Useful filters:

- `--mapper N`
- `--mirroring H|V|F`
- `--has-trainer`
- `--min-prg KB`, `--max-prg KB`
- `--min-chr KB`, `--max-chr KB`

### `split_rom.py` - extract PRG/CHR

```bash
# From a .nes file
./scripts/split_rom.py game.nes

# From an archive (uses first .nes found)
./scripts/split_rom.py roms.7z

# Overwrite output files without prompt
./scripts/split_rom.py game.nes --force
```

By default, the script protects existing output files from accidental overwrite.

## Library Usage

```python
from ines_parser import parse_ines_header

with open("game.nes", "rb") as f:
    header = parse_ines_header(f.read(16))

if header and header.is_valid():
    print(header)  # compact output
    print(header.detailed_str())  # full output
```

## Format Docs

- Details: `docs/iNES.md`
- Spec: [NESdev iNES](https://www.nesdev.org/wiki/INES)
- NES 2.0: [NESdev NES 2.0](https://www.nesdev.org/wiki/NES_2.0)

## License

MIT, see `LICENSE`.
