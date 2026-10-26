# iNES Parser

Python library and CLI for NES ROMs in iNES / NES 2.0 format: parse headers and ROM filename tags, scan collections, export reports, summarize mappers, analyze single ROMs, and split PRG/CHR. Requires Python 3.10+.

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

Same idea for `ines_rom_stats.py`, `ines_split_rom.py`, and `ines_analyze_rom.py`.

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

### Analyze

```bash
ines_analyze_rom.py game.nes
ines_analyze_rom.py game.7z            # GoodTools-style one-ROM archive (needs libarchive-c)
ines_analyze_rom.py game.nes --json
```

Full report for one ROM file: file size, iNES header, and naming-convention tags parsed from the filename — GoodTools style (`(JU) [!] [b] [hIR] [T+Rus] (VS) (PC10)`) and No-Intro style (`(USA) (Rev A) (Beta 1) (En,Fr,De)`) — plus cross-checks between them: file size vs. header, filename region vs. TV system, `(VS)`/`(PC10)` vs. console type, `[!]` vs. header validity. For archives, tags come from the inner `.nes` name and sizes refer to the uncompressed ROM. Unrecognised tags are listed as unknown, never guessed.

## Library

```python
from ines_parser import parse_ines_header, parse_rom_filename

with open("game.nes", "rb") as f:
    header = parse_ines_header(f.read(16))

if header and header.is_valid():
    print(header)
    print(header.detailed_str())

info = parse_rom_filename("Super Mario Bros. (JU) [!].nes")
print(info.title)        # Super Mario Bros.
print(info.regions)      # ('Japan', 'USA')
print(info.verified)     # True
print(info.to_dict())    # JSON-friendly; adds expected_tv_system
```

## Docs

- `docs/iNES.md` — iNES header notes
- `docs/NES2.0.md` — NES 2.0 header layout
- `docs/List of iNES mappers.md` — mapper and submapper name tables (from `ines_parser/tables.py`)
- `docs/NES 2.0 lookups.md` — Vs. PPU/hardware, extended console, expansion device names
- [NESdev iNES](https://www.nesdev.org/wiki/INES)
- [NESdev NES 2.0](https://www.nesdev.org/wiki/NES_2.0)

## License

MIT — see `LICENSE`.
