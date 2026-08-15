# iNES Mapper List

The following tables mirror `MAPPER_DATABASE` and `SUBMAPPER_DATABASE` in
`ines_parser/tables.py`. Mapper IDs include many NES 2.0 numbers beyond the
classic 8-bit range. Submapper names cover allocations documented on the
NESdev Wiki; unknown `(mapper, submapper)` pairs are reported at runtime as
`Unknown (N)`.

## Mappers

|iNES Mapper|Common designation(s)|Notes|
|---|---|---|
|0|NROM||
|1|MMC1, SxROM||
|2|UxROM||
|3|CNROM||
|4|MMC3, TxROM, MMC6||
|5|MMC5, ExROM|Contains expansion sound|
|6|FFE4 Board||
|7|AxROM||
|8|FFE3 Board||
|9|MMC2, PxROM||
|10|MMC4, FxROM||
|11|Color Dreams||
|12|Rexsoft DBZ5||
|13|CPROM||
|14|Rexsoft SL1632||
|15|100-in-1 Contra Function 16|Multicart|
|16|Bandai EPROM (24C02)||
|17|FFE8 Board||
|18|Jaleco SS8806||
|19|Namco 163|Contains expansion sound|
|21|VRC4, VRC4a, VRC4c||
|22|VRC2, VRC2a||
|23|VRC2/VRC4, VRC2b, VRC4e||
|24|VRC6, VRC6a|Contains expansion sound|
|25|VRC4, VRC4b, VRC4d||
|26|VRC6, VRC6b|Contains expansion sound|
|27|Unlicensed CC21|Mihunche, but previously used for World Hero|
|28|Unlicensed ACTION53|Multi-discrete PCB designed by Tepples for Action 53|
|29|Sealie Cufrom|homebrew PCB used by Glider|
|30|Sealie UNROM512|UNROM 512 + Flash|
|31|Unlicensed 2A03PURITANS|PCB designed by infinitelives & rainwarrior for 2A03 Puritans Album|
|32|Irem G101||
|33|Taito TC0190FMC||
|34|BNROM, NINA-001||
|35|Unlicensed SC127||
|36|TXC Strikew||
|37|PAL ZZ||
|38|Discrete logic 74X161X138||
|39|Unlicensed Studyngame||
|40|Bootleg SMB2JA||
|41|Caltron 6IN1||
|42|Bootleg Mariobaby|ai senshi nicole too, changed by crc_hack|
|43|Unlicensed SMB2J||
|44|Multicart Superbig 7IN1||
|45|Multicart HIK8IN1||
|46|Rumblestation Board||
|47|NES QJ||
|48|Taito TC0190FMCP||
|49|Multicart Superhik 4IN1||
|50|Bootleg SMB2JB||
|51|Multicart Ballgames 11IN1||
|52|Multicart Gold 7IN1||
|53|SVISION16 Board||
|54|Multicart 21IN1|duplicate of mapper 201, though possibly should be "Unused"|
|55|Unlicensed Mmalee|Genius SMB|
|56|Kaiser KS202||
|57|Multicart GKA||
|58|Multicart GKB||
|59|Multicart VT5201|and BMC-T3H53, BMC-D1038|
|60|Multicart 4IN1RESET||
|61|RCM TF9IN1||
|62|Multicart Super 700IN1||
|63|Multicart TH22913|Powerful 250/255|
|64|RAMBO-1|MMC3 clone with extra features|
|65|Irem H3001||
|66|GxROM, MxROM||
|67|Sunsoft 3||
|68|After Burner|ROM-based nametables|
|69|Sunsoft FME-7, Sunsoft 5B|The 5B is the FME-7 with expansion sound|
|70|Discrete logic 74X161X161X32||
|71|Camerica/Codemasters|Similar to UNROM|
|72|Jaleco JF17||
|73|VRC3||
|74|Pirate MMC3 derivative|Has both CHR ROM and CHR RAM (2k)|
|75|VRC1||
|76|Namco 109 variant||
|77|Irem LROG017||
|78|Irem Holydivr||
|79|NINA-03/NINA-06|It's either 003 or 006, we don't know right now|
|80|Taito X1 005||
|81|Nanjing / NTDEC N715021|81 Super Gun|
|82|Taito X1-017|Old mis-ordered PRG dumps; see also mapper 552|
|83|Cony Board||
|85|VRC7|Contains expansion sound|
|86|JALECO-JF-13||
|87|Discrete logic 74X139X74||
|88|Namcot 34X3||
|89|Sunsoft 2||
|90|Jycompany A||
|91|Unlicensed JY830623C||
|92|Jaleco JF19||
|93|Sunsoft 2||
|94|Senjou no Ookami||
|95|Namcot 3425||
|96|Bandai Oekakids||
|97|Irem TAM S1||
|103|Unlicensed 2708|103 Bootleg cart 2708 (Doki Doki Panic - FDS Conversion)|
|104|Camerica Goldenfive||
|105|NES-EVENT|Similar to MMC1|
|106|Bootleg SMB3||
|107|Magicseries MD||
|108|Unlicensed LH28 LH54|108 has 4 variant boards|
|111|GTROM|Also historically used for Ninja Ryukenden Chinese MMC1 variant|
|112|Nanjing / NTDEC Asder||
|113|HES NTD-8|For multicarts including mapper 79 games|
|114|Supergame Lionking||
|115|Kasing Board||
|116|Somari SL12||
|117|Futuremedia Board||
|118|TxSROM, MMC3|MMC3 with independent mirroring control|
|119|TQROM, MMC3|Has both CHR ROM and CHR RAM|
|120|Bootleg Tobidase||
|121|KAY Board||
|123|Unlicensed H2288||
|125|Unlicensed LH32|Monty no Doki Doki Daidassou - FDS Conversion|
|126|Multicart PJOY84||
|127|Bootleg Double Dragon II|Japan pirate|
|132|TXC 22211||
|133|Sachen SA72008||
|134|Multicart Family 4646||
|136|Sachen TCU02||
|137|Sachen 8259D||
|138|Sachen 8259B||
|139|Sachen 8259C||
|140|Jaleco JF11||
|141|Sachen 8259A||
|142|Kaiser KS7032||
|143|Sachen TCA01||
|144|Agci 50282||
|145|Sachen SA72007||
|146|AVE NINA06|basically same as Mapper 79 (Nina006)|
|147|Sachen TCU01||
|148|Sachen SA0037||
|149|Sachen SA0036||
|150|Sachen 74LS374||
|152|Discrete logic 74X161X161X32||
|153|Bandai LZ93||
|154|Namcot 34X3||
|155|MMC1A, SxROM|same as mapper 1 but forces the use of MMC1A|
|156|Opencorp DAOU306||
|157|Bandai Datach|Datach Reader games -> must go in the Datach subslot|
|158|Tengen 800037||
|159|Bandai EPROM (24C01)||
|160|Sachen SA009||
|162|Waixing FS304|not confirmed, but a lot of chinese releases use it like this...|
|163|Nanjing Board||
|164|Waixing FFV||
|165|Waixing SH2||
|166|SUBOR||
|167|SUBOR||
|168|Unlicensed Racermate||
|170|Fujiya|Shiko Game Syu|
|171|Kaiser KS7058||
|172|TXC Dumaracing||
|173|TXC Mjblock||
|174|Multicart 2751||
|175|Kaiser KS7022||
|176|Unlicensed Xiaozy||
|177|Hengg Srich||
|178|Waixing Sgzlz||
|179|Hengg Xhzs||
|180|Crazy Climber|Variation of UNROM, fixed first bank at $8000|
|182|Supergame Lionking|duplicate of mapper 114|
|183|Bootleg Shuiguan||
|184|Sunsoft 1||
|185|CNROM with protection diodes||
|186|Fukutake Board||
|187|Unlicensed KOF96||
|188|Bandai Karaoke||
|189|TXC TW||
|190|Zemina Board||
|191|Waixing Type B||
|192|Pirate MMC3 derivative|Has both CHR ROM and CHR RAM (4k)|
|193|Nanjing / NTDEC Fightinghero||
|194|Waixing Type D||
|195|Waixing Type E||
|196|Bootleg SBROS11||
|197|Unlicensed SF3||
|198|Waixing Type F||
|199|Waixing Type F1||
|200|Multicart 36IN1||
|201|Multicart 21IN1||
|202|Multicart 150IN1||
|203|Multicart 35IN1||
|204|Multicart 64IN1||
|205|Multicart 15IN1||
|206|DxROM, Namco 118, MIMIC-1|Simplified MMC3 predecessor lacking some features|
|207|Taito X1 005||
|208|Gouder 37017||
|209|Jycompany C||
|210|Namco 175 and 340|Namco 163 with different mirroring|
|211|Jycompany B||
|212|Multicart Superhik 300IN1||
|213|Multicart GKB|duplicate of mapper 58|
|214|Multicart Supergun 20IN1||
|215|Unlicensed 8237|and UNL_8237A|
|216|RCM GS2015||
|217|Multicart 500IN1||
|218|Nocash Nochr||
|219|Unlicensed A9746||
|221|Unlicensed N625092||
|222|Bootleg Dragonninja||
|223|Waixing Type I|(according to NEStopia source, it's MMC3 with more WRAM)|
|224|Waixing Type J|(according to NEStopia source, it's MMC3 with more WRAM)|
|225|Multicart 72IN1||
|226|Multicart 76IN1||
|227|Multicart 1200IN1||
|228|Action 52||
|229|Multicart 31IN1||
|230|Multicart 22GAMES||
|231|Multicart 20IN1||
|232|Camerica/Codemasters Quattro|Multicarts|
|233|Multicart 42IN1RESET||
|234|AVE MAXI15||
|235|Multicart GOLD260|235 Golden Game x-in-1 games|
|236|Multicart 70IN1||
|237|Multicart Teletubbies||
|238|Unlicensed 603 5052||
|240|CNE Shlz||
|241|TXC Commandos||
|242|Waixing Wxzs||
|243|Sachen 74LS374 ALT||
|244|CNE Decathlon||
|245|Waixing Type H||
|246|CNE FSB||
|249|Waixing Security||
|250|Nitra TDA||
|252|Waixing SGZ||
|253|Hengg SHJY3||
|254|Bootleg PIKACHUY2K||
|255|Multicart 72IN1|duplicate of mapper 225|
|256|OneBus, UNL-OneBus, BMC-OneBus|OneBus Famiclones|
|258|Unlicensed 158B||
|259|Multicart F15||
|260|HP10xx/HP20xx|Multicarts; predecessor to FK23C|
|261|Multicart 810544C||
|262|Sachen Shero||
|263|Unlicensed KOF97||
|264|Yoko Board||
|265|Multicart T262||
|266|Unlicensed Cityfight||
|267|Multicart EL861121C||
|268|SMD133 Board||
|272|Bootleg Akumajo Special|Boku Dracula-kun bootleg|
|274|Multicart 80013B||
|283|RCM GS2004|and RCM_GS2013|
|285|Multicart A65AS||
|286|Multicart Benshieng||
|287|Multicart 411120C||
|288|Multicart GKCXIN1||
|289|Multicart 60311C||
|290|Multicart NTD 03||
|291|Multicart NT639||
|292|Unlicensed BMW8544|Dragon Fighter by Flying Star|
|294|Multicart Family 4646|FIXME: is this really exactly the same as mapper 134?|
|297|TXC 22110|2-in-1 Uzi Lightgun|
|298|Unlicensed TF1201|Lethal Weapon (Enforcers) pirate|
|299|Multicart 11160||
|300|Multicart 190IN1||
|301|Multicart 8157||
|302|Kaiser KS7057|Gyruss FDS conversion|
|303|Kaiser KS7017|Almana no Kiseki FDS conversion|
|304|Bootleg 09034A|various FDS conversions|
|305|Kaiser KS7031|Dracula II FDS conversion|
|306|Kaiser KS7016|Exciting Basket FDS conversion|
|307|Kaiser KS7037|Metroid FDS conversion|
|308|Unlicensed TH21311|Batman (Sunsoft) pirate on VRC2 clone hardware|
|309|Unlicensed LH51|Ai Senshi Nicol alt FDS conversion|
|312|Kaiser KS7013B|Highway Star Kaiser bootleg|
|313|Multicart Resettxrom||
|314|Multicart 64IN1NR||
|319|Multicart HP898F||
|320|Multicart 830425C||
|322|Multicart K3033||
|323|Farid SLROM8IN1|homebrew 8-in-1|
|324|Farid UNROM8IN1|homebrew 8-in-1|
|325|Unlicensed Malisb|Super Mali Splash Bomb pirate hack|
|326|Bootleg Contraj||
|328|Unlicensed RT01|test cart (Russia)|
|329|Unlicensed EDU2K||
|330|Bootleg L001|Sangokushi II bootleg (retitled part III)|
|331|Multicart 12IN1||
|332|Multicart WS||
|333|Multicart 8IN1||
|334|Multicart 5IN1 1993||
|335|Multicart CTC09||
|336|Multicart K3046||
|337|Multicart CTC 12IN1||
|338|Multicart SA005A||
|339|Multicart K3006||
|340|Multicart K3036||
|341|Multicart TJ03||
|345|Multicart L6IN1||
|346|Kaiser KS7012|Zanac alt FDS conversion|
|347|Kaiser KS7030|Doki Doki Panic alt FDS conversion|
|348|Multicart 830118C||
|349|Multicart G146||
|350|Multicart 891227||
|351|Multicart TECHLINE9IN1||
|352|Kaiser KS106C|4-in-1|
|353|Multicart 810305C|Super Mario Family multicart|
|354|Multicart FAM250||
|355|Hwang Shinwei 3D-BLOCK|PIC16C54 protection|
|356|Multicart JY208||
|361|Multicart YY841101C||
|362|Multicart 830506C||
|364|Multicart 830832C||
|366|Multicart GN45||
|368|Bootleg YUNG08|SMB2 FDS conversion|
|370|Multicart F600|Golden Mario Party II multicart|
|372|Multicart SFC12||
|374|Multicart Resetsxrom||
|376|Multicart YY841155C||
|377|Multicart EL860947C||
|380|Multicart 970630C||
|381|Unlicensed KN42|2-in-1 Big Nose games|
|382|Multicart 830928C||
|389|Caltron 9IN1||
|392|Multicart 00202650||
|393|Multicart 820720C||
|396|Multicart 850437C||
|399|Batmap 000|homebrew game Star Versus|
|400|retroUSB 8-bit XMAS 2017|Sealie/retroUSB homebrew multicart|
|401|Multicart KC885||
|404|Multicart JY012005||
|405|UMC UM6578|NES-on-a-chip / PnP|
|408|Konami PnP|Konami Collector's Series Advance Arcade|
|409|Sealie Dpcmcart|A Winner is You homebrew music cart|
|410|Multicart JY302||
|411|Multicart A88S1||
|413|Batmap Srrx|homebrew game Super Russian Roulette|
|415|Bootleg 0353|Lucky (Roger) Rabbit FDS conversion|
|416|Multicart N32 4IN1||
|417|Bootleg Batmanfs|"Fine Studio" Batman bootleg|
|418|Unlicensed LH42|Highway Star Whirlwind Manu bootleg|
|428|Multicart TF2740||
|431|Multicart GN91B||
|433|Multicart NC20MB||
|434|Multicart S009||
|437|Multicart TH2348||
|438|Multicart K3071||
|446|Mindkids SMD172B_FPGA|Pixel Games / Retro-Bit multicarts|
|447|Multicart KL06||
|452|Multicart DS927||
|512|Sachen Zgdh||
|513|Sachen SA9602B||
|515|Family Noraebang|Korean karaoke; YM2413 + mic|
|516|Cocoma Board||
|517|Kkachi-wa Nolae Chingu|Korean karaoke with mic|
|519|Unlicensed EH8813A|Dr Mario II Chinese pirate|
|520|Bootleg 2YUDB||
|521|Dreamtech Board|Korean Igo|
|522|Unlicensed LH10|Fuuun Shaolin Kyo FDS conversion|
|523|Jncota Fengshenbang|Waixing FS005-like; hard-wired mirroring|
|524|Bootleg 900218|Lord of King pirate|
|525|Kaiser KS7021A|GetsuFumaDen pirate (and maybe a Contra?)|
|526|Bootleg Sangokushi, UNL-BJ-56|Namco Sangokushi: Chugen no Hasha bootleg|
|527|Unlicensed AX40G|Fudou Myouou Den pirate|
|528|Multicart 831128C|1995 New Series Super 2-in-1|
|529|Unlicensed T230|Datach Dragon Ball Z IV bootleg|
|530|Unlicensed AX5705|Super Mario Bros Pocker Mali|
|533|Sachen 3014|Dong Dong Nao II|
|534|ING-022 / TEC9719|MMC3 multicart ASIC; related to mappers 126 and 422|
|535|Unlicensed LH53|Nazo no Murasamejo FDS conversion|
|538|Bootleg 60-1064-16L|Exciting Soccer / Super Soccer Champion FDS conversion|
|539|Bootleg Palthena|Hikari Shinwa (Kid Icarus) FDS conversion|
|540|Mapper 359 CHR 2K variant|2 KiB CHR banks for 512 KiB CHR-RAM|
|541|Multicart LITTLECOM160||
|543|Multicart Srpg 5IN1||
|544|Waixing FS306|Bawang de Dalu / Sangokushi II translation|
|547|Konami QTa, KONAMI-QTAI|VRC5-based QTa adapter|
|548|Co Tung CTC-15|Almana no Kiseki FDS conversion|
|549|Kaiser KS7016B|Meikyuu Jiin Dababa alt FDS conversion|
|550|Multicart JY820845C||
|551|Jncota KT1001||
|552|Taito X1 017||
|553|Sachen 3013|Dong Dong Nao 1|
|554|Kaiser KS7010|Akumajo Dracula FDS conversion|
|555|NES-EVENT 2||
|557|Unlicensed LG25|Moero TwinBee FDS conversion|
|558|Yancheng YC-03-09|Related to mappers 162-164|
|559|Unused|No documented assignment (MAME)|

## NES 2.0 Submappers

Submapper `0` is usually the default / iNES-compatible behaviour for that
mapper. Only pairs present in `SUBMAPPER_DATABASE` are listed here.

|Mapper|Submapper|Name|
|---|---|---|
|1|0|Normal|
|1|1|SUROM (deprecated)|
|1|2|SOROM (deprecated)|
|1|3|MMC1A (deprecated, use mapper 155)|
|1|4|SXROM (deprecated)|
|1|5|Fixed 32 KiB PRG (SEROM/SHROM/SH1ROM)|
|1|6|2ME (Famicom Network System)|
|2|0|Default iNES behaviour|
|2|1|No bus conflicts|
|2|2|AND bus conflicts|
|3|0|Default iNES behaviour|
|3|1|No bus conflicts|
|3|2|AND bus conflicts|
|4|0|Sharp MMC3|
|4|1|MMC6|
|4|2|MMC3C hard-wired mirroring|
|4|3|MC-ACC|
|4|4|NEC MMC3|
|4|5|T9552 scrambling|
|7|0|Default iNES behaviour|
|7|1|No bus conflicts|
|7|2|AND bus conflicts|
|16|0|Unspecified (FCG-1/2 + LZ93D50)|
|16|1|LZ93D50 + 24C01 (deprecated, use 159)|
|16|2|Datach (deprecated, use 157)|
|16|3|8 KiB WRAM (deprecated, use 153)|
|16|4|FCG-1/2|
|16|5|LZ93D50 (no/24C02 EEPROM)|
|19|0|Default (expansion volume unspecified)|
|19|1|Deprecated (internal battery RAM, no expansion sound)|
|19|2|No expansion sound|
|19|3|N163 sound 11.0–13.0 dB|
|19|4|N163 sound 16.0–17.0 dB|
|19|5|N163 sound 18.0–19.5 dB|
|21|0|Combined addressing (VRC4)|
|21|1|VRC4a|
|21|2|VRC4c|
|21|3|VRC2 (lower addressing)|
|21|4|VRC2 (higher addressing)|
|23|0|Combined addressing (VRC4)|
|23|1|VRC4f|
|23|2|VRC4e|
|23|3|VRC2b|
|23|4|VRC2 (higher addressing)|
|25|0|Combined addressing (VRC4)|
|25|1|VRC4b|
|25|2|VRC4d|
|25|3|VRC2c|
|25|4|VRC2 (higher addressing)|
|32|0|Normal (H/V mirroring)|
|32|1|Major League (fixed one-screen)|
|34|0|Normal (combined)|
|34|1|NINA-001|
|34|2|BNROM|
|68|0|Normal|
|68|1|Sunsoft Dual Cartridge System (NTB-ROM)|
|71|0|Hardwired H/V mirroring|
|71|1|Fire Hawk (mapper-controlled 1-screen)|
|78|0|Unspecified|
|78|1|Cosmo Carrier (single-screen)|
|78|2|Deprecated|
|78|3|Holy Diver (H/V mirroring)|
|85|0|Unspecified|
|85|1|VRC7b (Tiny Toon)|
|85|2|VRC7a (Lagrange Point)|
|91|0|YY830624C/JY830848C|
|91|1|EJ-006-1|
|114|0|Lion King / Aladdin scrambling|
|114|1|Boogerman scrambling|
|178|0|No infrared sensor|
|178|1|Gameinis Infrared Sensor|
|185|0|CHR enable bank unknown|
|185|4|CHR enable if latch 0..1 = 0|
|185|5|CHR enable if latch 0..1 = 1|
|185|6|CHR enable if latch 0..1 = 2|
|185|7|CHR enable if latch 0..1 = 3|
|206|0|Namcot 118 (normal PRG banking)|
|206|1|Unbanked 32 KiB PRG (3407/3417/3451)|
|210|0|Unspecified (175 if PRG-RAM/battery else 340)|
|210|1|Namco 175|
|210|2|Namco 340|
|215|0|UNL-8237|
|215|1|UNL-8237A|
|232|0|Normal|
|232|1|Aladdin Deck Enhancer|
|256|0|Normal|
|256|1|Waixing VT03|
|256|2|Power Joy Supermax|
|256|3|Zechess/Hummer Team|
|256|4|Qishenglong|
|256|5|Waixing VT02|
|256|11|Vibes|
|256|12|Cheertone|
|256|13|Taikee|
|256|14|Karaoto|
|256|15|Jungletac|
|268|0|Coolboy|
|268|1|Mindkids|

---

## Sources

- NESdev Wiki, short summary table: [List of mappers](https://www.nesdev.org/wiki/List_of_mappers)
- NESdev Wiki, per-mapper articles (category): [INES Mappers](https://www.nesdev.org/wiki/Category:INES_Mappers)
- NESdev Wiki: [NES 2.0 submappers](https://www.nesdev.org/wiki/NES_2.0_submappers)
- MAME `mmc_list` in [`nes_ines.hxx`](https://github.com/mamedev/mame/blob/master/src/devices/bus/nes/nes_ines.hxx) (PCB identifiers and file comments; extended mapper IDs)
- Curated names and notes from the NESdev summary are preserved in `ines_parser` where they overlap; remaining mapper rows follow the MAME mapping.
- Related NES 2.0 field lookups (Vs. System, extended console, expansion device): [`NES 2.0 lookups.md`](NES%202.0%20lookups.md)
