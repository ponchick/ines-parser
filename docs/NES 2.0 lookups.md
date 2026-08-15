# NES 2.0 Header Lookups

Human-readable names for selected NES 2.0 header fields, mirrored from
`ines_parser/tables.py`. Numeric values remain in `INESHeader` / `to_dict()`;
companion `*_name` keys use these tables.

See also [`List of iNES mappers.md`](List%20of%20iNES%20mappers.md) for mappers
and submappers, and [`NES2.0.md`](NES2.0.md) for the header layout.

## Vs. PPU Type

Header byte 13, low nibble, when console type is Vs. System
(`INESHeader.vs_ppu_type`).

|Value|Name|
|---|---|
|`$0` (0)|RP2C03/RC2C03 (any)|
|`$1` (1)|Reserved|
|`$2` (2)|RP2C04-0001|
|`$3` (3)|RP2C04-0002|
|`$4` (4)|RP2C04-0003|
|`$5` (5)|RP2C04-0004|
|`$6` (6)|Reserved|
|`$7` (7)|Reserved|
|`$8` (8)|RC2C05-01|
|`$9` (9)|RC2C05-02|
|`$A` (10)|RC2C05-03|
|`$B` (11)|RC2C05-04|
|`$C` (12)|Reserved|
|`$D` (13)|Reserved|
|`$E` (14)|Reserved|
|`$F` (15)|Reserved|

## Vs. Hardware Type

Header byte 13, high nibble, when console type is Vs. System
(`INESHeader.vs_hw_type`).

|Value|Name|
|---|---|
|`$0` (0)|Vs. Unisystem (normal)|
|`$1` (1)|Vs. Unisystem (RBI Baseball protection)|
|`$2` (2)|Vs. Unisystem (TKO Boxing protection)|
|`$3` (3)|Vs. Unisystem (Super Xevious protection)|
|`$4` (4)|Vs. Unisystem (Vs. Ice Climber Japan protection)|
|`$5` (5)|Vs. Dual System (normal)|
|`$6` (6)|Vs. Dual System (Raid on Bungeling Bay protection)|

## Extended Console Type

Header byte 13, low nibble, when console type is Extended
(`INESHeader.extended_console_type`). Values `$0`–`$2` are unused in this
field (they are already expressed by byte 7).

|Value|Name|
|---|---|
|`$0` (0)|Regular NES/Famicom/Dendy (unused)|
|`$1` (1)|Nintendo Vs. System (unused)|
|`$2` (2)|PlayChoice-10 (unused)|
|`$3` (3)|Famiclone with decimal mode|
|`$4` (4)|NES/Famicom with EPSM|
|`$5` (5)|V.R. Technology VT01 (STN palette)|
|`$6` (6)|V.R. Technology VT02|
|`$7` (7)|V.R. Technology VT03|
|`$8` (8)|V.R. Technology VT09|
|`$9` (9)|V.R. Technology VT32|
|`$A` (10)|V.R. Technology VT369|
|`$B` (11)|UMC UM6578|
|`$C` (12)|Famicom Network System|
|`$D` (13)|Reserved|
|`$E` (14)|Reserved|
|`$F` (15)|Reserved|

## Default Expansion Device

Header byte 15, bits 0–5 (`INESHeader.expansion_device`).
`misc_rom_count` (byte 14) is a simple count (0–3) and has no name table.

|Value|Name|
|---|---|
|`$0` (0)|Unspecified|
|`$1` (1)|Standard NES/Famicom controllers|
|`$2` (2)|NES Four Score/Satellite|
|`$3` (3)|Famicom Four Players Adapter (simple)|
|`$4` (4)|Vs. System (1P via $4016)|
|`$5` (5)|Vs. System (1P via $4017)|
|`$6` (6)|Reserved|
|`$7` (7)|Vs. Zapper|
|`$8` (8)|Zapper ($4017)|
|`$9` (9)|Two Zappers|
|`$A` (10)|Bandai Hyper Shot Lightgun|
|`$B` (11)|Power Pad Side A|
|`$C` (12)|Power Pad Side B|
|`$D` (13)|Family Trainer Side A|
|`$E` (14)|Family Trainer Side B|
|`$F` (15)|Arkanoid Vaus Controller (NES)|
|`$10` (16)|Arkanoid Vaus Controller (Famicom)|
|`$11` (17)|Two Vaus Controllers plus Famicom Data Recorder|
|`$12` (18)|Konami Hyper Shot Controller|
|`$13` (19)|Coconuts Pachinko Controller|
|`$14` (20)|Exciting Boxing Punching Bag|
|`$15` (21)|Jissen Mahjong Controller|
|`$16` (22)|Yonezawa Party Tap|
|`$17` (23)|Oeka Kids Tablet|
|`$18` (24)|Sunsoft Barcode Battler|
|`$19` (25)|Miracle Piano Keyboard|
|`$1A` (26)|Pokkun Moguraa Tap-tap Mat|
|`$1B` (27)|Top Rider|
|`$1C` (28)|Double-Fisted|
|`$1D` (29)|Famicom 3D System|
|`$1E` (30)|Doremikko Keyboard|
|`$1F` (31)|R.O.B. Gyromite|
|`$20` (32)|Famicom Data Recorder (silent keyboard)|
|`$21` (33)|ASCII Turbo File|
|`$22` (34)|IGS Storage Battle Box|
|`$23` (35)|Family BASIC Keyboard plus Famicom Data Recorder|
|`$24` (36)|Dongda PEC Keyboard|
|`$25` (37)|Bit Corp. Bit-79 Keyboard|
|`$26` (38)|Subor Keyboard|
|`$27` (39)|Subor Keyboard plus Macro Winners Mouse|
|`$28` (40)|Subor Keyboard plus Subor Mouse via $4016|
|`$29` (41)|SNES Mouse ($4016)|
|`$2A` (42)|Multicart|
|`$2B` (43)|Two SNES controllers|
|`$2C` (44)|RacerMate Bicycle|
|`$2D` (45)|U-Force|
|`$2E` (46)|R.O.B. Stack-Up|
|`$2F` (47)|City Patrolman Lightgun|
|`$30` (48)|Sharp C1 Cassette Interface|
|`$31` (49)|Standard Controller (swapped axes/buttons)|
|`$32` (50)|Excalibur Sudoku Pad|
|`$33` (51)|ABL Pinball|
|`$34` (52)|Golden Nugget Casino extra buttons|
|`$35` (53)|Keda Keyboard|
|`$36` (54)|Subor Keyboard plus Subor Mouse via $4017|
|`$37` (55)|Port test controller|
|`$38` (56)|Bandai Multi Game Player Gamepad buttons|
|`$39` (57)|Venom TV Dance Mat|
|`$3A` (58)|LG TV Remote Control|
|`$3B` (59)|Famicom Network Controller|
|`$3C` (60)|King Fishing Controller|
|`$3D` (61)|Croaky Karaoke Controller|
|`$3E` (62)|Kingwon Keyboard|
|`$3F` (63)|Zecheng Keyboard|
|`$40` (64)|Subor Keyboard plus L90-rotated PS/2 mouse via $4017|
|`$41` (65)|PS/2 Keyboard (UM6578) plus PS/2 Mouse via $4017|
|`$42` (66)|PS/2 Mouse (UM6578)|
|`$43` (67)|Yuxing Mouse via $4016|
|`$44` (68)|Subor Keyboard plus Yuxing Mouse via $4016|
|`$45` (69)|Gigggle TV Pump|
|`$46` (70)|BBK Keyboard plus R90-rotated PS/2 mouse via $4017|
|`$47` (71)|Magical Cooking|
|`$48` (72)|SNES Mouse ($4017)|
|`$49` (73)|Zapper ($4016)|
|`$4A` (74)|Arkanoid Vaus Controller (Prototype)|
|`$4B` (75)|TV Mahjong Game Controller|
|`$4C` (76)|Mahjong Gekitou Densetsu Controller|
|`$4D` (77)|Subor Keyboard plus X-inverted PS/2 mouse via $4017|
|`$4E` (78)|IBM PC/XT Keyboard|
|`$4F` (79)|Subor Keyboard plus Mega Book Mouse|

---

## Sources

- NESdev Wiki: [NES 2.0](https://www.nesdev.org/wiki/NES_2.0)
- NESdev Wiki: [NES 2.0 submappers](https://www.nesdev.org/wiki/NES_2.0_submappers)
