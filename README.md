# iNES Parser

Lightweight Python library and CLI tools for working with NES ROMs in iNES/NES 2.0 format.

Supported versions: Python 3.10-3.14.

## Quick Start

```bash
pip install ines-parser
```

Optional extra for archive formats (`.7z`/`.zip`/`.rar`): `pip install "ines-parser[archive]"`. Otherwise the library has no extra dependencies.

## What It Does

- parses ROM headers (`mapper`, PRG/CHR sizes, mirroring, and more)
- scans ROM directories with filters
- splits ROM files into `PRG` and `CHR` binaries

## CLI

Tools live in **`ines_parser/cli/`** as **`ines_scan_roms.py`** and **`ines_split_rom.py`**. The names match **`pip install`** entry points on your `PATH`: **`ines_scan_roms.py`** and **`ines_split_rom.py`**.

**Without installing**, from the repository root you can use either `-m` or the path to the same files:

```bash
python -m ines_parser.cli.ines_scan_roms /path/to/roms
python ines_parser/cli/ines_scan_roms.py /path/to/roms

python -m ines_parser.cli.ines_split_rom game.nes
python ines_parser/cli/ines_split_rom.py game.nes
```

**After `pip install`,** run the same logical names as commands (they are small wrappers, not copies of the sources):

```bash
ines_scan_roms.py /path/to/roms
ines_split_rom.py game.nes
```

### Scan ROMs

```bash
ines_scan_roms.py /path/to/roms
ines_scan_roms.py /path/a /path/b
ines_scan_roms.py /path/to/roms --mapper 4
ines_scan_roms.py /path/to/roms --show-all
```

Useful filters:

- `--mapper N`
- `--mirroring H|V|F`
- `--has-trainer`
- `--min-prg KiB`, `--max-prg KiB`
- `--min-chr KiB`, `--max-chr KiB`

### Split ROM (PRG / CHR)

```bash
ines_split_rom.py game.nes
ines_split_rom.py roms.7z
ines_split_rom.py game.nes --force
```

By default, existing output files are not overwritten without confirmation.

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
