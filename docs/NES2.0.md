# NES 2.0

**NES 2.0** extends the iNES single file cart format to better describe NES/Famicom-compatible cartridge hardware. Some of its purpose include:

- Removing the need to use ROM checksums, or other information outside the header, to disambiguate emulation behavior not encoded by iNES.
- Making room for new mapper allocation.
- Allowing for larger ROM sizes.
- Supporting other than standard NES/Famicom console types such as the Nintendo Vs. System and enhanced Famiclones.
- Providing additional information such as the region-specific CPU/PPU type and default expansion port devices.
- Replaces the deprecated UNIF format.

The format is backwards-compatible to iNES, so that ROM images with a NES 2.0 header run in non-NES-2.0-compliant emulators as long as they do not require NES-2.0-exclusive features.

## Identification

A file is a NES 2.0 ROM image file if it begins with "NES\<EOF\>" (same as iNES) and, additionally, the byte at offset 7 has bit 2 clear and bit 3 set:

```c
bool iNESFormat=false;
if (header[0]=='N' && header[1]=='E' && header[2]=='S' && header[3]==0x1A)
        iNESFormat=true;

bool NES20Format=false;
if (iNESFormat==true && (header[7]&0x0C)==0x08)
        NES20Format=true;
```

## File Structure

A NES 2.0 file contains a sixteen-byte header, followed by Trainer, PRG-ROM, CHR-ROM and Miscellaneous ROM data.

### Header

```text
Offset Meaning
--------------
0-3    Identification String. Must be "NES<EOF>".

4      PRG-ROM size LSB
5      CHR-ROM size LSB

6      Flags 6
       D~7654 3210
         ---------
         NNNN FTBM
         |||| |||+-- Hard-wired nametable layout
         |||| |||     0: Vertical arrangement ("mirrored horizontally") or mapper-controlled
         |||| |||     1: Horizontal arrangement ("mirrored vertically")
         |||| ||+--- "Battery" and other non-volatile memory
         |||| ||      0: Not present
         |||| ||      1: Present
         |||| |+--- 512-byte Trainer
         |||| |      0: Not present
         |||| |      1: Present between Header and PRG-ROM data
         |||| +---- Alternative nametables
         ||||        0: No
         ||||        1: Yes
         ++++------ Mapper Number D3..D0

7      Flags 7
       D~7654 3210
         ---------
         NNNN 10TT
         |||| ||++- Console type
         |||| ||     0: Nintendo Entertainment System/Family Computer
         |||| ||     1: Nintendo Vs. System
         |||| ||     2: Nintendo Playchoice 10
         |||| ||     3: Extended Console Type
         |||| ++--- NES 2.0 identifier
         ++++------ Mapper Number D7..D4

8      Mapper MSB/Submapper
       D~7654 3210
         ---------
         SSSS NNNN
         |||| ++++- Mapper number D11..D8
         ++++------ Submapper number

9      PRG-ROM/CHR-ROM size MSB
       D~7654 3210
         ---------
         CCCC PPPP
         |||| ++++- PRG-ROM size MSB
         ++++------ CHR-ROM size MSB

10     PRG-RAM/EEPROM size
       D~7654 3210
         ---------
         pppp PPPP
         |||| ++++- PRG-RAM (volatile) shift count
         ++++------ PRG-NVRAM/EEPROM (non-volatile) shift count
       If the shift count is zero, there is no PRG-(NV)RAM.
       If the shift count is non-zero, the actual size is
       "64 << shift count" bytes, i.e. 8192 bytes for a shift count of 7.

11     CHR-RAM size
       D~7654 3210
         ---------
         cccc CCCC
         |||| ++++- CHR-RAM size (volatile) shift count
         ++++------ CHR-NVRAM size (non-volatile) shift count
       If the shift count is zero, there is no CHR-(NV)RAM.
       If the shift count is non-zero, the actual size is
       "64 << shift count" bytes, i.e. 8192 bytes for a shift count of 7.

12     CPU/PPU Timing
       D~7654 3210
         ---------
         .... ..VV
                ++- CPU/PPU timing mode
                     0: RP2C02 ("NTSC NES")
                     1: RP2C07 ("Licensed PAL NES")
                     2: Multiple-region
                     3: UA6538 ("Dendy")

13     When Byte 7 AND 3 =1: Vs. System Type
       D~7654 3210
         ---------
         MMMM PPPP
         |||| ++++- Vs. PPU Type
         ++++------ Vs. Hardware Type

       When Byte 7 AND 3 =3: Extended Console Type
       D~7654 3210
         ---------
         .... CCCC
              ++++- Extended Console Type

14     Miscellaneous ROMs
       D~7654 3210
         ---------
         .... ..RR
                ++- Number of miscellaneous ROMs present

15     Default Expansion Device
       D~7654 3210
         ---------
         ..DD DDDD
           ++-++++- Default Expansion Device
```

### Trainer Area

The Trainer Area follows the 16-byte Header and precedes the PRG-ROM area if bit 2 of Header byte 6 is set. It is always 512 bytes in size if present, and contains data to be loaded into CPU memory at $7000. It is only used by some games that were modified to run on different hardware from the original cartridges, such as early RAM cartridges and emulators, and which put some additional compatibility code into those address ranges.

### PRG-ROM Area

The PRG-ROM Area follows the 16-byte Header and the Trainer Area and precedes the CHR-ROM Area. Header byte 4 (LSB) and bits 0-3 of Header byte 9 (MSB) together specify its size.

If the MSB nibble is $0-E, LSB and MSB together simply specify the PRG-ROM size in 16 KiB units:

```text
   ++++----------- Header byte 9 D3..D0
   |||| ++++-++++- Header byte 4
 D~BA98 7654 3210
   --------------
   BBBB BBBB BBBB
   ++++-++++-++++- PRG-ROM size in 16 KiB units,
                   values $000-$EFF for 0..62,898,176 bytes
```

If the MSB nibble is $F, an exponent-multiplier notation is used:

```text
   ++++----------- Header byte 9 D3..D0
   |||| ++++-++++- Header byte 4
 D~BA98 7654 3210
   --------------
   1111 EEEE EEMM
        |||| ||++- Multiplier, actual value is MM*2+1 (1,3,5,7)
        ++++-++--- Exponent (2^E), 0-63

 The actual PRG-ROM size is 2^E *(MM*2+1) bytes.
```

The exponent-multiplier form may only be used if the PRG-ROM size cannot be specified correctly using the simpler notation. If the PRG-ROM data has an odd size that cannot be represented in either notation, the data must be padded to a size that can be represented.

In Vs. Dual System ROM images, the first half block of the specified PRG-ROM size belongs to the first unit, and the second half block of PRG-ROM belongs to the the second unit. 24 KiB (half-)blocks are mapped to $A000-$FFFF both in Vs. Unisystem and Vs. Dual System.

An exception is granted for two oddly-sized Vs. System ROM images with a total of 40 KiB PRG-ROM, which are defined to represent 32 KiB +8 KiB instead:

- *Vs. Gumshoe*, Vs. Hardware type #0:
  - First 32 KiB represent the entire CPU $8000-$FFFF area, including the CPU $8000-$9FFF area with $4016 D2=0;
  - Second 8 KiB represent the CPU $8000-$9FFF area with $4016 D2=1.
- *Vs. Raid on Bungeling Bay*, Vs. Hardware type #6:
  - First 32 KiB represent the first unit's PRG-ROM at CPU $8000-$FFFF;
  - Second 8 KiB represent the second unit's PRG-ROM at CPU $E000-$FFFF.
  - The second unit only executes a dummy program that does nothing except set a flag in the shared WRAM at $6000-$67FF.

### CHR-ROM Area

The CHR-ROM Area, if present, follows the Trainer and PRG-ROM Areas and precedes the Miscellaneous ROM Area. Header byte 5 (LSB) and bits 4-7 of Header byte 9 (MSB) specify its size. If the MSB nibble is $0-E, LSB and MSB together simply specify the CHR-ROM size in 8 KiB units:

```text
   ++++----------- Header byte 9 D7..D4
   |||| ++++-++++- Header byte 5
 D~BA98 7654 3210
   --------------
   BBBB BBBB BBBB
   ++++-++++-++++- CHR-ROM size in 8 KiB units,
                   values $000-$EFF for 0..31,449,088 bytes
```

If the MSB nibble is $F, an exponent-multiplier notation is used:

```text
   ++++----------- Header byte 9 D7..D4
   |||| ++++-++++- Header byte 5
 D~BA98 7654 3210
   --------------
   1111 EEEE EEMM
        |||| ||++- Multiplier, actual value is MM*2+1 (1,3,5,7)
        ++++-++--- Exponent (2^E), 0-63

 The actual CHR-ROM size therefore becomes 2^E * (MM*2+1).
```

The exponent-multiplier form may only be used if the CHR-ROM size cannot be specified correctly using the simpler notation. If the CHR-ROM data has an odd size that cannot be represented by either notation, the data must be padded to a size that can be represented.

For Vs. Dual System ROM images, if the CHR-ROM size is 32 KiB, the first 16 KiB belong to the first unit, and the second 16 KiB of CHR-ROM belong to the second unit. If the CHR-ROM size is 16 KiB, the both units use the same bank-switched 16 KiB CHR-ROM data.

### Miscellaneous ROM Area

The Miscellaneous ROM Area, if present, follows the CHR-ROM area and occupies the remainder of the file. Its size is not explicitly denoted in the header, and can be deduced by subtracting the 16-byte Header, Trainer, PRG-ROM and CHR-ROM Area sizes from the total file size. The meaning of this data depends on the console type and mapper type; Header byte 14 is used to denote the presence of the Miscellaneous ROM Area and the number of ROM chips in case any disambiguation is needed. Currently, miscellaneous ROMs are defined for the following situations:

- on console type Playchoice 10, an 8 KiB INST ROM, 16 bytes of PROM Data, 16 bytes of PROM Counter Out data, for a total of "3" miscellaneous ROMs;
- on console type VT369, 4 KiB of ROM that is embedded into the NES-on-a-chip itself;
- on INES Mapper 086 submapper 1, a single miscellaneous ROM containing speech data;
- on NES 2.0 Mapper 355, the embedded ROM of the PIC16C54 microcontroller that the games use for protection purposes.
- on NES 2.0 Mapper 561 and NES 2.0 Mapper 562 to deliver trainers that do not match the iNES trainer conventions in size (512 byte) or location ($7000).

## Notes

### Backwards Compatibility to iNES

- Bytes 0-7 have the same meaning as in iNES, so that NES-2.0-headered games will still run in emulators that do not support NES 2.0 unless the header specifies features that those older emulators did not support anyway.
- The NES 2.0 identifier (Byte 7 D3..D2) has been chosen so that it does not collide with any valid iNES header nor with any known ROM image that has garbage in bytes 7-15 such as "DiskDude!".

### Nametable layout

Byte 6 (Flags 6) contains two bits to describe the nametable layout of the cartridge.

```text
  D~7654 3210
    ---------
    .... F..M
         |  +-- Horizontal/vertical hard-wired mirroring.
         +----- All other nametable layout variations
```

- Bit 0 is normally relevant only if the mapper does not allow the mirroring type to be switched. It should be set to zero otherwise.
- For some mappers, bit 3 means that 4 KiB of RAM are present at PPU $2000-2FFF, exclusive to that region, and cannot be banked, replaced, or rearranged. This applies to:
  - Mapper 4 (MMC3)
  - Mapper 206 (DxROM, etc. MMC3-like subset)
  - Mapper 262 (Street Heroes)
- Several mappers use bit 3 to mean something different:
  - Mapper 30 (UNROM 512) - This board can be wired for H/V fixed, 1-screen, or 4-screen.
  - Mapper 218 (Magic Floor) - This experimental board has 4 configurations that allow the internal 2k CIRAM to be used for both CHR and nametables at once.

### PRG-(NV)RAM/EEPROM

The PRG-(NV)RAM/EEPROM fields specify the sizes of...

- Memory that is mapped into CPU address space, regardless of whether that memory is internal to a mapper chip or in a separate RAM chip;
- EEPROM even if it is not mapped into CPU address space.

They do not specify the sizes of...

- Mapper-chip-internal memory that is not mapped into CPU address space, even if battery-backed, such as the Namco 163's wavetable RAM which some games use to store saved game data. The size of such memory is part of the Mapper definition instead. The Battery bit (Header byte 6 bit 1) denotes whether such memory is battery-backed. The MMC5's EXRAM is not included in the PRG-RAM size, as it can be mapped by software to CPU, PPU, or no address space at all;
- self-flashable PRG-ROM;
- external storage such as cassette tape or the ASCII Turbo File.

When the upper nibble (PRG-NVRAM/EEPROM) has a non-zero value, the Battery bit (Header byte 6 bit 1) must always be set for compatibility with iNES. Conversely, if the Battery bit is set, the upper nibble must have a non-zero value, unless the only battery-backed memory is either mapper-chip-internal memory that is not mapped into CPU address space, such as the Namco 163's wavetable RAM, or the PRG-ROM is self-flashable.

For cartridges with self-flashable PRG-ROM, the Battery bit is only set if the game actually uses that capability, be it for saving high scores or game progress. It is not set merely because the board hardware *could* flash PRG-ROM; that capability will already be implied in the mapper number.

### CHR-(NV)RAM

- In the presence of a NES 2.0 Header, an emulator must not assume that if a ROM image specifies no CHR-ROM, the game will automatically have 8 KiB of CHR-RAM; all CHR-RAM must instead be explicitly specified in Header byte 11.
- Memory that is permanently mapped into the nametable address space (PPU $2000-$2FFF) is not included in the CHR-RAM size. Setting the hard-wired four-screen mode bit in Header byte 6 bit 3 therefore does not entail a 4 KiB increase of the CHR-RAM size.
- The MMC5's EXRAM is not included in the CHR-RAM size, as it can be mapped by software to CPU, PPU, or no address space at all.

### CPU/PPU Timing

For non-homebrew NES/Famicom games, this field's value is always a function of the region in which a game was released:

| Value | Meaning     | Regions                                                              |
|-------|-------------|----------------------------------------------------------------------|
| 0     | RP2C02      | North America, Japan, South Korea, Taiwan, Hong Kong, South America  |
| 1     | RP2C07      | Western Europe, Australia, South Africa                              |
| 2     | Multiple    | Multiple                                                             |
| 3     | UA6538      | Eastern Europe (including Russia), Mainland China, India, North Africa, Saudi Arabia |

Value 2 ("multiple-region") is used either if a game was released with identical ROM content in both NTSC and PAL countries, such as Nintendo's early games, or if the game detects the console's timing and adjusts itself. Emulators should implement this value by either switching to a user-specified "Default Region" or by keeping the previously-set region.

V.R. Technology Famiclones only come with RP2C02 or UA6538 timing, so games with such a console type can only bear values 0 or 3.

### Vs. System Type

When the console type in Header byte 7 D1..D0 is 1 (Vs. System), the lower nibble of Header byte 13 specifies the Vs. PPU type, and the upper nibble the non-PPU-based protection type and whether the ROM is for the Vs. Unisystem or the Vs. Dual System.

**Vs. PPU types (Header byte 13 D3..D0):**

- $0: Any RP2C03/RC2C03 variant
- $1: reserved
- $2: RP2C04-0001
- $3: RP2C04-0002
- $4: RP2C04-0003
- $5: RP2C04-0004
- $6: reserved
- $7: reserved
- $8: RC2C05-01 (signature unknown)
- $9: RC2C05-02 ($2002 AND $3F =$3D)
- $A: RC2C05-03 ($2002 AND $1F =$1C)
- $B: RC2C05-04 ($2002 AND $1F =$1B)
- $C: reserved
- $D-F: reserved

For copy protection purposes, these PPU types have different palettes; the RC2C05 PPUs furthermore swap PPU registers $2000 and $2001 and return a signature in the lower bits of $2002. If a game uses the DIP switches to select different PPU models, this field represents the correct PPU model when those DIP switches are all set to zero. The sole known game to use RC2C05-01, 忍者じゃじゃ丸くん (Ninja Jajamaru-kun), does not check $2002 for a signature.

**Vs. Hardware type (Header byte 13 D7..D4):**

- $0: Vs. Unisystem (normal)
- $1: Vs. Unisystem (RBI Baseball protection)
- $2: Vs. Unisystem (TKO Boxing protection)
- $3: Vs. Unisystem (Super Xevious protection)
- $4: Vs. Unisystem (Vs. Ice Climber Japan protection)
- $5: Vs. Dual System (normal)
- $6: Vs. Dual System (Raid on Bungeling Bay protection)

Refer to the Vs. System entry for more information.

### Extended Console Type

When the console type in Header byte 7 D1..D0 is 3 (Extended), the lower nibble of Header byte 13 specifies the type of console on which the ROM image is supposed to be run.

- $0: [Regular NES/Famicom/Dendy]
- $1: [Nintendo Vs. System]
- $2: [Playchoice 10]
- $3: Regular Famiclone, but with CPU that supports Decimal Mode
- $4: Regular NES/Famicom with EPSM module or plug-through cartridge
- $5: V.R. Technology VT01 with red/cyan STN palette
- $6: V.R. Technology VT02
- $7: V.R. Technology VT03
- $8: V.R. Technology VT09
- $9: V.R. Technology VT32
- $A: V.R. Technology VT369
- $B: UMC UM6578
- $C: Famicom Network System
- $D-$F: reserved

Values $0-$2 are not used for the extended console type, as they can be expressed by only using Header byte 7 D1..D0. They are reserved here so that emulators can fold the information in Header Byte 7 D1..D0 and Header byte 13 into one "console type" variable without recoding the values.

### Default Expansion Device

Header byte 15 indicates that the ROM expects a specific set of devices accessible at CPU $4016/$4017. For an emulator that wishes to automatically provide selection of needed peripherals, this gives the required information directly within the header.

Value $00 is reserved for compatibility with older versions of this specification and indicates no information on the default input device.

In almost all cases, this byte will specify *the* device without which the game cannot be played at all, such as the NES Zapper or Power Pad. If a game supports an *optional* expansion port device, and having that device connected does not preclude using the normal controllers with that game, this byte will specify that device, such as the ASCII Turbo File or the Arkanoid Vaus Controller. For games that support multiple combinations of expansion devices, this byte will denote the game's default selection.

This byte does not denote devices that connect to a cartridge; such devices are part of the respective Mapper's definition.

**Common Device Values:**

- $00: Unspecified
- $01: Standard NES/Famicom controllers
- $02: NES Four Score/Satellite with two additional standard controllers
- $03: Famicom Four Players Adapter with two additional standard controllers using the "simple" protocol
- $04: Vs. System (1P via $4016)
- $05: Vs. System (1P via $4017)
- $07: Vs. Zapper
- $08: Zapper ($4017)
- $09: Two Zappers
- $0A: Bandai Hyper Shot Lightgun
- $0B: Power Pad Side A
- $0C: Power Pad Side B
- $0D: Family Trainer Side A
- $0E: Family Trainer Side B
- $0F: Arkanoid Vaus Controller (NES)
- $10: Arkanoid Vaus Controller (Famicom)
- $13: Coconuts Pachinko Controller
- $14: Exciting Boxing Punching Bag (Blowup Doll)
- $19: Miracle Piano Keyboard
- $1C: Double-Fisted (Requires or allows use of two controllers by one player)
- $1D: Famicom 3D System
- $1F: R.O.B. Gyromite
- $21: ASCII Turbo File
- $29: SNES Mouse ($4016)
- $2A: Multicart
- $2B: Two SNES controllers replacing the two standard NES controllers
- $2E: R.O.B. Stack-Up

(See full specification for complete device list)

### Notes on Specific Values

- The Famicom Four Players Adapter ($03) is denoted only if the additional controllers provide *independent* 3P/4P input, not if they just alias the built-in 1P/2P controllers.
- For Vs. System games that do not care which stick is used and therefore could be denoted either with value $04 or $05, use value $04.
- "Double-Fisted" ($1C) means Player 1 takes controller 1 into the left hand and controller 2 into the right hand, and player 2 takes controller 3 into the left hand and controller 4 into the right hand, each rotated 90 degrees clockwise, so that the D-Pad is on top. This assumes a Four Score is connected, which allows two players to use two controllers at once (Smash T.V.) if the game supports two players.
- "Multicart" ($2A) is only used if any game on that multicart actually uses expansion port devices. As these will be mostly Zapper games, emulating an expansion port Zapper together with two standard controllers is the simplest way of implementing this value.

## Version History

- **2006-09-18** - Original version of specification by kevtris.
  - [NES 2.0 "Official" Specification](https://forums.nesdev.org/viewtopic.php?p=17727#p17727)
- **2019-01-02** - Additions by NewRisingSun.
  - [Additions proposal by NewRisingSun](https://forums.nesdev.org/viewtopic.php?f=3&t=17213&start=45#p220624)
  - Flags 7: adds Extended Console Type value
  - Flags 12: adds Dendy value
  - Flags 13: adds Extended Console Type field
  - Flags 14: adds miscellaneous ROM specifier
  - Flags 15: adds Default Expansion Device

## See Also

- NES 2.0 submappers - disambiguation for mappers that were under-specified in iNES 1
- NES 2.0 header for ca65 - macro header generator for ca65 assembly
- NES 2.0 header for cc65 - macro header generator for cc65 C code

## References

- [Original proposal by kevtris](https://forums.nesdev.org/viewtopic.php?p=17727#p17727)
- [Additions proposal by NewRisingSun](https://forums.nesdev.org/viewtopic.php?f=3&t=17213&start=45#p220624)
- [NES 2.0 XML Database, with link to Python script for applying it to a ROM files collection](https://forums.nesdev.org/viewtopic.php?t=19940)

---

**Original source:** [NESdev Wiki - NES 2.0](https://www.nesdev.org/wiki/NES_2.0)
