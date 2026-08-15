# iNES Parser

Python library and CLI for NES ROMs in iNES / NES 2.0 format: parse headers, scan collections, export reports, summarize mappers, and split PRG/CHR. Requires Python 3.10+.

```bash
pip install ines-parser
pip install "ines-parser[archive]"   # optional: .7z / .zip / .rar
```

## CLI

After install the tools are on your `PATH`. From a checkout:

```bash
ines_scan_roms.py /path/to/roms
# or: python -m ines_parser.cli.ines_scan_roms /path/to/roms
```

Same idea for `ines_rom_stats.py` and `ines_split_rom.py`.

### Scan

```bash
ines_scan_roms.py /path/to/roms
ines_scan_roms.py /a /b --mapper 4 --show-all
ines_scan_roms.py /path/to/roms --format csv -o roms.csv
ines_scan_roms.py /path/to/roms --format csv -d ';' -o roms.csv
ines_scan_roms.py /path/to/roms --format csv --show-all -o roms-full.csv
```

Filters: `--mapper`, `--mirroring H|V|F`, `--has-trainer`, `--min-prg` / `--max-prg`, `--min-chr` / `--max-chr` (KiB).

`--format text|html|csv|json` (default text). `-o` writes to a file. `--show-all` adds full header fields. For CSV, `-d` / `--delimiter` sets the separator (default `,`; use `;` for Excel with Russian locale, `tab` for TSV-style).

### Stats

```bash
ines_rom_stats.py /path/to/roms
ines_rom_stats.py /path/to/roms --json
```

### Split

```bash
ines_split_rom.py game.nes
ines_split_rom.py roms.7z          # prompts before overwrite; use --force to skip
```

## Library

```python
from ines_parser import parse_ines_header

with open("game.nes", "rb") as f:
    header = parse_ines_header(f.read(16))

if header and header.is_valid():
    print(header)
    print(header.detailed_str())
```

## Docs

- `docs/iNES.md`
- [NESdev iNES](https://www.nesdev.org/wiki/INES)
- [NESdev NES 2.0](https://www.nesdev.org/wiki/NES_2.0)

## License

MIT — see `LICENSE`.
