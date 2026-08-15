# iNES Parser

Python library and CLI for NES ROMs in iNES / NES 2.0 format. Requires Python 3.10+.

```bash
pip install ines-parser
# optional: .7z / .zip / .rar support
pip install "ines-parser[archive]"
```

## CLI

After install, three tools are on your `PATH`. From a checkout you can also run them as modules or scripts:

```bash
ines_scan_roms.py /path/to/roms
# or: python -m ines_parser.cli.ines_scan_roms /path/to/roms
# or: python ines_parser/cli/ines_scan_roms.py /path/to/roms
```

Same pattern for `ines_rom_stats.py` and `ines_split_rom.py`.

**Scan** — list headers, filter, optionally export:

```bash
ines_scan_roms.py /path/to/roms
ines_scan_roms.py /a /b --mapper 4 --show-all
ines_scan_roms.py /path/to/roms --format csv -o roms.csv
ines_scan_roms.py /path/to/roms --format html -o report.html
```

Filters: `--mapper`, `--mirroring H|V|F`, `--has-trainer`, `--min-prg` / `--max-prg`, `--min-chr` / `--max-chr` (sizes in KiB).

`--format` is `text` (default), `html`, `csv`, `tsv`, or `json`. Use `-o` to write a file. CSV is UTF-8 with a BOM so Excel opens it correctly.

**Stats** — mapper counts (archives if libarchive is installed):

```bash
ines_rom_stats.py /path/to/roms
ines_rom_stats.py /path/to/roms --json
```

**Split** — extract PRG/CHR (prompts before overwrite unless `--force`):

```bash
ines_split_rom.py game.nes
ines_split_rom.py roms.7z
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
