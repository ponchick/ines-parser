"""Tests for ines_parser.filename: GoodTools and No-Intro naming conventions."""

import pytest

from ines_parser.filename import (
    DumpStatus,
    expected_tv_system,
    parse_rom_filename,
)


class TestGoodToolsRegions:
    @pytest.mark.parametrize(
        ("token", "region"),
        [
            ("J", "Japan"),
            ("U", "USA"),
            ("E", "Europe"),
            ("F", "France"),
            ("G", "Germany"),
            ("I", "Italy"),
            ("S", "Spain"),
            ("K", "Korea"),
            ("C", "China"),
            ("A", "Australia"),
            ("B", "Brazil"),
            ("SW", "Sweden"),
        ],
    )
    def test_single_letter_region(self, token, region):
        info = parse_rom_filename(f"Game ({token}).nes")
        assert info.title == "Game"
        assert info.regions == (region,)
        assert info.unknown_tokens == ()

    def test_multi_letter_region(self):
        info = parse_rom_filename("Super Mario Bros. (JU) [!].nes")
        assert info.title == "Super Mario Bros."
        assert info.regions == ("Japan", "USA")
        assert info.verified is True
        assert info.dump_status is DumpStatus.VERIFIED

    def test_three_letter_region(self):
        info = parse_rom_filename("Game (JUE).nes")
        assert info.regions == ("Japan", "USA", "Europe")

    def test_usa_is_not_split_into_letters(self):
        # "USA" is a No-Intro region name, not U+S+A GoodTools letters.
        info = parse_rom_filename("Game (USA).nes")
        assert info.regions == ("USA",)

    def test_region_groups_merge(self):
        info = parse_rom_filename("Game (G) (I) (S).nes")
        assert info.regions == ("Germany", "Italy", "Spain")


class TestGoodToolsMarkers:
    @pytest.mark.parametrize(
        ("token", "field"),
        [
            ("VS", "is_vs"),
            ("PC10", "is_playchoice"),
            ("NP", "is_nintendo_power"),
            ("Unl", "is_unlicensed"),
            ("PD", "is_public_domain"),
        ],
    )
    def test_marker(self, token, field):
        info = parse_rom_filename(f"Game ({token}).nes")
        assert getattr(info, field) is True

    def test_multipart(self):
        info = parse_rom_filename("Game (M3).nes")
        assert info.multipart_index == 3


class TestGoodToolsDumpFlags:
    @pytest.mark.parametrize(
        ("token", "status"),
        [
            ("!", DumpStatus.VERIFIED),
            ("b", DumpStatus.BAD),
            ("b1", DumpStatus.BAD),
            ("a", DumpStatus.ALTERNATE),
            ("a2", DumpStatus.ALTERNATE),
            ("o1", DumpStatus.OVERDUMP),
            ("t", DumpStatus.TRUNCATED),
            ("x", DumpStatus.BAD_CHECKSUM),
            ("c", DumpStatus.CRACKED),
            ("f1", DumpStatus.FIXED),
        ],
    )
    def test_flag(self, token, status):
        info = parse_rom_filename(f"Game (U) [{token}].nes")
        assert info.dump_status is status

    def test_worst_flag_wins(self):
        info = parse_rom_filename("Game (U) [b] [!].nes")
        assert info.dump_status is DumpStatus.BAD
        assert info.verified is True

    def test_verified_is_also_a_flag(self):
        info = parse_rom_filename("Game (U) [!].nes")
        assert info.dump_flags == ("verified",)

    def test_plus_combined_flags(self):
        info = parse_rom_filename("Game (J) [b1]+[T-Rus].nes")
        assert info.title == "Game"
        assert info.dump_status is DumpStatus.BAD
        assert info.is_translation is True
        assert info.translation_language == "Rus"
        assert info.translation_is_newer is False

    def test_dump_combo_inside_one_bracket(self):
        info = parse_rom_filename("Game (J) [b+c].nes")
        assert info.dump_flags == ("bad dump", "cracked")


class TestHacksAndTranslations:
    def test_bare_hack(self):
        info = parse_rom_filename("Game (J) [h].nes")
        assert info.is_hack is True
        assert info.hack_tag is None

    def test_hack_with_group(self):
        info = parse_rom_filename("Game (J) [hIR].nes")
        assert info.is_hack is True
        assert info.hack_tag == "IR"

    def test_translation_newer(self):
        info = parse_rom_filename("Game (J) [T+Rus].nes")
        assert info.is_translation is True
        assert info.translation_is_newer is True
        assert info.translation_language == "Rus"

    def test_translation_older(self):
        info = parse_rom_filename("Game (J) [T-Fre].nes")
        assert info.is_translation is True
        assert info.translation_is_newer is False
        assert info.translation_language == "Fre"


class TestNoIntro:
    def test_region_with_revision(self):
        info = parse_rom_filename("Castlevania (Europe) (Rev A).nes")
        assert info.title == "Castlevania"
        assert info.regions == ("Europe",)
        assert info.revision == "A"

    def test_numeric_revision(self):
        info = parse_rom_filename("Game (USA) (Rev 2).nes")
        assert info.revision == "2"

    def test_multi_region(self):
        info = parse_rom_filename("Zelda (USA, Japan) (v1.0).nes")
        assert info.regions == ("USA", "Japan")
        assert info.version == "1.0"

    def test_uppercase_version(self):
        info = parse_rom_filename("Game (U) (V1.1).nes")
        assert info.version == "1.1"

    def test_language_group(self):
        info = parse_rom_filename("Jeux (Europe) (En,Fr,De).nes")
        assert info.regions == ("Europe",)
        assert info.languages == ("En", "Fr", "De")

    def test_single_language_group(self):
        info = parse_rom_filename("Game (Japan) (En).nes")
        assert info.languages == ("En",)

    def test_world(self):
        info = parse_rom_filename("Game (World).nes")
        assert info.regions == ("World",)

    @pytest.mark.parametrize(
        ("token", "prerelease", "index"),
        [
            ("Beta", "Beta", None),
            ("Beta 1", "Beta", 1),
            ("Proto", "Proto", None),
            ("Prototype", "Proto", None),
            ("Sample", "Sample", None),
            ("Demo 2", "Demo", 2),
            ("Aftermarket", "Aftermarket", None),
            ("Homebrew", "Homebrew", None),
            ("Pirate", "Pirate", None),
        ],
    )
    def test_prerelease(self, token, prerelease, index):
        info = parse_rom_filename(f"Game (USA) ({token}).nes")
        assert info.prerelease == prerelease
        assert info.prerelease_index == index


class TestUnknownTokens:
    def test_unknown_paren_and_bracket(self):
        info = parse_rom_filename("Game (XYZ) [q].nes")
        assert info.unknown_tokens == ("(XYZ)", "[q]")

    def test_title_words_stay_title(self):
        info = parse_rom_filename("Some Odd (Thing).nes")
        assert info.title == "Some Odd"
        assert info.unknown_tokens == ("(Thing)",)

    def test_unknown_letters_not_partial(self):
        # R is not a GoodTools region letter: all-or-nothing.
        info = parse_rom_filename("Game (JUR).nes")
        assert info.regions == ()
        assert info.unknown_tokens == ("(JUR)",)

    def test_empty_groups(self):
        info = parse_rom_filename("Game () [].nes")
        assert info.unknown_tokens == ("()", "[]")

    def test_sw_not_split(self):
        info = parse_rom_filename("Game (SW).nes")
        assert info.regions == ("Sweden",)


class TestTitlesAndExtensions:
    def test_leading_the_with_comma(self):
        info = parse_rom_filename("Legend of Zelda, The (JU) [!].nes")
        assert info.title == "Legend of Zelda, The"

    def test_no_extension(self):
        info = parse_rom_filename("game")
        assert info.title == "game"

    def test_title_dot_kept_without_extension(self):
        info = parse_rom_filename("Super Mario Bros.")
        assert info.title == "Super Mario Bros."

    def test_zip_extension(self):
        info = parse_rom_filename("Game (U).zip")
        assert info.title == "Game"
        assert info.regions == ("USA",)

    def test_long_suffix_is_title(self):
        # "Nesdev" is too long for an extension: part of the title.
        info = parse_rom_filename("Something.Nesdev")
        assert info.title == "Something.Nesdev"

    def test_path_input(self):
        from pathlib import Path

        info = parse_rom_filename(Path("/roms/Super Mario Bros. (W).nes"))
        assert info.title == "Super Mario Bros."

    def test_whitespace_collapsed(self):
        info = parse_rom_filename("Game   (U)    [!].nes")
        assert info.title == "Game"


class TestExpectedTVSystem:
    @pytest.mark.parametrize(
        ("regions", "expected"),
        [
            (("Japan", "USA"), "NTSC"),
            (("USA",), "NTSC"),
            (("Japan", "Korea"), "NTSC"),
            (("Europe",), "PAL"),
            (("France", "Germany"), "PAL"),
            (("Japan", "Europe"), None),  # mixed
            ((), None),
            (("World",), None),
            (("Brazil",), None),  # PAL-M, not decisive
            (("Russia",), None),
        ],
    )
    def test_expectation(self, regions, expected):
        assert expected_tv_system(regions) == expected

    def test_via_parse(self):
        info = parse_rom_filename("Game (JU).nes")
        assert info.to_dict()["expected_tv_system"] == "NTSC"


class TestToDict:
    def test_omits_defaults_and_adds_tv(self):
        info = parse_rom_filename("Game (E) [b].nes")
        d = info.to_dict()
        assert d["regions"] == ("Europe",)
        assert d["dump_status"] == "bad dump"
        assert d["dump_flags"] == ("bad dump",)
        assert d["expected_tv_system"] == "PAL"
        assert "is_hack" not in d
        assert "verified" not in d

    def test_plain_title(self):
        d = parse_rom_filename("game.nes").to_dict()
        assert d == {"title": "game", "expected_tv_system": None}
