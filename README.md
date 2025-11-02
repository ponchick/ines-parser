# iNES Parser Library

A Python library and utilities for parsing and working with iNES format NES ROM files. Supports both iNES 1.0 and NES 2.0 formats, with tools for extracting ROM information and splitting ROM files into components.

## Installation

### Basic Installation

```bash
git clone https://github.com/ponchick/ines-parser.git
cd ines-parser
```

The core `ines_parser.py` library has no dependencies and works with Python 3.10+.

## Library Usage

### Basic Example

```python
from ines_parser import parse_ines_header

# Read and parse an iNES header
with open('game.nes', 'rb') as f:
    header_data = f.read(16)
    header = parse_ines_header(header_data)
    
if header and header.is_valid():
    print(f"Mapper: {header.mapper}")
    print(f"PRG ROM: {header.prg_rom_size // 1024}KB")
    print(f"CHR ROM: {header.chr_rom_size // 1024}KB")
    print(f"Mirroring: {header.mirroring.value}")
    print(f"Format: {header.format.value}")
```

### Detailed Information

```python
from ines_parser import parse_ines_header

with open('game.nes', 'rb') as f:
    header = parse_ines_header(f.read(16))
    
# Get full details
print(header.detailed_str())  # Full verbose output

# Get minimal info
print(str(header))  # Just mapper, PRG, CHR

# Access individual fields
if header.has_trainer:
    print("ROM has a 512-byte trainer")
    
if header.has_battery:
    print("ROM has battery-backed save RAM")
```

## Command-Line Tools

### scan_roms.py - ROM Scanner and Analyzer

Scan directories for ROM files and display their information.

```bash
# Scan a directory
./scripts/scan_roms.py /path/to/roms/

# Filter by mapper
./scripts/scan_roms.py /path/to/roms/ --mapper 4

# Find ROMs with trainers
./scripts/scan_roms.py /path/to/roms/ --has-trainer

# Filter by size (in KB)
./scripts/scan_roms.py /path/to/roms/ --min-prg 256 --max-chr 128

# Show detailed information
./scripts/scan_roms.py /path/to/roms/ --show-all

# Verbose mode with filters
./scripts/scan_roms.py /path/to/roms/ --verbose --mapper 1 --mirroring H
```

**Available Filters:**

- `--mapper N` - Filter by mapper number
- `--mirroring {H,V,4}` - Filter by mirroring type (Horizontal, Vertical, Four-screen)
- `--has-trainer` - Only show ROMs with trainers
- `--min-prg KB` - Minimum PRG ROM size in KB
- `--max-prg KB` - Maximum PRG ROM size in KB
- `--min-chr KB` - Minimum CHR ROM size in KB
- `--max-chr KB` - Maximum CHR ROM size in KB
- `--show-all` - Show all header fields (not just mapper/sizes)
- `--verbose` - Show scanning progress and statistics

**Output Format:**

Default (minimal):

```text
game.7z:game.nes: mapper: 1, PRG: 128k, CHR: 128k
```

With `--show-all`:

```text
game.7z:game.nes: mapper: 1, mirroring: H, PRG ROM: 128k, CHR ROM: 128k, Bus Conflicts: False
```

### split_rom.py - ROM Component Extractor

Extract PRG and CHR ROM data from iNES files.

```bash
# Split a .nes file
./scripts/split_rom.py game.nes
# Creates: game.prg.bin, game.chr.bin

# Extract from archive
./scripts/split_rom.py roms.7z
# Extracts first .nes file from archive
```

**Features:**

- Automatically skips iNES header and trainer (if present)
- Generates clean PRG and CHR binary files
- Validates ROM structure and reports errors
- Warns when archives contain multiple ROM files

**Output:**

```text
Extracted PRG ROM: game.prg.bin (131072 bytes)
Extracted CHR ROM: game.chr.bin (131072 bytes)
```

For archives with multiple files:

```text
Warning: Found 7 .nes files in archive:
  - game1.nes
  - game2.nes
  ...
Processing only the first file: game1.nes
```

## File Format Documentation

See [docs/iNES.md](docs/iNES.md) for detailed information about the iNES file format specification.

Original source: [NESdev Wiki - iNES](https://www.nesdev.org/wiki/INES)

## Examples

### Find All MMC3 (Mapper 4) ROMs

```bash
./scripts/scan_roms.py /roms/ --mapper 4 > mmc3_roms.txt
```

### Find Large ROMs (>256KB PRG)

```bash
./scripts/scan_roms.py /roms/ --min-prg 256 --verbose
```

### Extract Components from Archive

```bash
./scripts/split_rom.py my_collection.7z
```

### Combine Filters

```bash
# Find all mapper 1 ROMs with horizontal mirroring and at least 128KB PRG
./scripts/scan_roms.py /roms/ --mapper 1 --mirroring H --min-prg 128
```

## License

MIT License - See LICENSE file for details

## Links

- **GitHub Repository**: [https://github.com/ponchick/ines-parser](https://github.com/ponchick/ines-parser)
- **Issues**: [https://github.com/ponchick/ines-parser/issues](https://github.com/ponchick/ines-parser/issues)
- **Releases**: [https://github.com/ponchick/ines-parser/releases](https://github.com/ponchick/ines-parser/releases)

## See Also

- [NESdev Wiki](https://www.nesdev.org/)
- [iNES Format Specification](https://www.nesdev.org/wiki/INES)
- [NES 2.0 Format](https://www.nesdev.org/wiki/NES_2.0)
