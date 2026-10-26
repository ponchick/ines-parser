"""
ROM filename conventions parser.

Extracts region, dump status, hack/translation and revision information from
GoodTools-style and No-Intro-style filenames, e.g.::

    Super Mario Bros. (JU) [!].nes
    Castlevania (Europe) (Rev A).nes

GoodTools uses short letter codes in parentheses (``J`` Japan, ``U`` USA,
``E`` Europe, ...) plus bracket flags (``[!]`` verified dump, ``[b]`` bad
dump, ``[h...]`` hack, ``[T+Rus]`` translation, ...). No-Intro spells out
region names (``(USA)``, ``(Europe)``), allows comma-separated multi-region
and language groups (``(En,Fr,De)``), and marks revisions and prereleases
(``(Rev A)``, ``(Beta 1)``).

The parser is a pure function: string in, :class:`RomFilenameInfo` out.
Tokens it does not recognise are preserved verbatim in ``unknown_tokens``
rather than guessed at.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, fields
from enum import Enum
from pathlib import Path

__all__ = [
    "DumpStatus",
    "RomFilenameInfo",
    "expected_tv_system",
    "parse_rom_filename",
]


class DumpStatus(Enum):
    """Overall dump quality derived from GoodTools bracket flags."""

    UNKNOWN = "unknown"
    VERIFIED = "verified"
    FIXED = "fixed"
    CRACKED = "cracked"
    ALTERNATE = "alternate"
    BAD_CHECKSUM = "bad checksum"
    OVERDUMP = "overdump"
    TRUNCATED = "truncated"
    BAD = "bad dump"


# Worst status first: several flags may coexist in one name.
_DUMP_STATUS_PRECEDENCE = (
    DumpStatus.BAD,
    DumpStatus.TRUNCATED,
    DumpStatus.OVERDUMP,
    DumpStatus.BAD_CHECKSUM,
    DumpStatus.ALTERNATE,
    DumpStatus.CRACKED,
    DumpStatus.FIXED,
    DumpStatus.VERIFIED,
)

# GoodTools single-letter region codes; "SW" is a two-letter code of its own.
_GOODTOOLS_REGIONS = {
    "A": "Australia",
    "B": "Brazil",
    "C": "China",
    "E": "Europe",
    "F": "France",
    "G": "Germany",
    "H": "Netherlands",
    "I": "Italy",
    "J": "Japan",
    "K": "Korea",
    "S": "Spain",
    "SW": "Sweden",
    "U": "USA",
}

# No-Intro region names, matched case-insensitively, kept in canonical spelling.
_NO_INTRO_REGIONS = frozenset({
    "Africa", "America", "Asia", "Australia", "Austria", "Belgium", "Brazil",
    "Canada", "China", "Croatia", "Denmark", "Europe", "Finland", "France",
    "Germany", "Greece", "Hong Kong", "Hungary", "Ireland", "Israel", "Italy",
    "Japan", "Korea", "Mexico", "Netherlands", "New Zealand", "Norway",
    "Poland", "Portugal", "Romania", "Russia", "Serbia", "Singapore",
    "Slovakia", "South Africa", "South Korea", "Spain", "Sweden", "Switzerland",
    "Taiwan", "Thailand", "Turkey", "Ukraine", "United Arab Emirates",
    "United Kingdom", "Unknown", "USA", "Venezuela", "Vietnam", "World",
})
_NO_INTRO_REGIONS_MAP = {name.lower(): name for name in _NO_INTRO_REGIONS}

# No-Intro language tags: parenthesised groups of these two-letter codes.
_NO_INTRO_LANGUAGES = {
    "ar": "Ar", "bg": "Bg", "cs": "Cs", "da": "Da", "de": "De", "en": "En",
    "es": "Es", "fi": "Fi", "fr": "Fr", "gr": "Gr", "he": "He", "hr": "Hr",
    "hu": "Hu", "it": "It", "ja": "Ja", "ko": "Ko", "nl": "Nl", "no": "No",
    "pl": "Pl", "pt": "Pt", "ro": "Ro", "ru": "Ru", "sk": "Sk", "sv": "Sv",
    "tr": "Tr", "uk": "Uk", "zh": "Zh",
}

# Region -> TV system implied by the region alone.
# Brazil is PAL-M (60 Hz) and World/Asia span mixed regions: both stay out.
_REGION_TV = {
    "USA": "NTSC",
    "Japan": "NTSC",
    "Canada": "NTSC",
    "China": "NTSC",
    "Taiwan": "NTSC",
    "Korea": "NTSC",
    "South Korea": "NTSC",
    "Europe": "PAL",
    "France": "PAL",
    "Germany": "PAL",
    "Italy": "PAL",
    "Spain": "PAL",
    "Netherlands": "PAL",
    "Sweden": "PAL",
    "Australia": "PAL",
    "United Kingdom": "PAL",
    "Austria": "PAL",
    "Belgium": "PAL",
    "Denmark": "PAL",
    "Finland": "PAL",
    "Greece": "PAL",
    "Hungary": "PAL",
    "Ireland": "PAL",
    "Norway": "PAL",
    "Poland": "PAL",
    "Portugal": "PAL",
    "Switzerland": "PAL",
}

# GoodTools parenthesised console/release markers -> RomFilenameInfo fields.
_MARKERS = {
    "VS": "is_vs",
    "PC10": "is_playchoice",
    "NP": "is_nintendo_power",
    "UNL": "is_unlicensed",
    "PD": "is_public_domain",
}

# GoodTools bracket dump codes -> flag names.
_DUMP_FLAGS = {
    "a": "alternate",
    "b": "bad dump",
    "c": "cracked",
    "f": "fixed",
    "o": "overdump",
    "t": "truncated",
    "x": "bad checksum",
}

# Prerelease/release descriptors; "Prototype" is the No-Intro spelling.
_PRERELEASE = {
    "beta": "Beta",
    "proto": "Proto",
    "prototype": "Proto",
    "sample": "Sample",
    "demo": "Demo",
    "aftermarket": "Aftermarket",
    "homebrew": "Homebrew",
    "pirate": "Pirate",
}

_RE_TOKEN = re.compile(r"\(([^()]*)\)|\[([^\[\]]*)\]")
_RE_REVISION = re.compile(r"[Rr]ev\.?\s*(.+)")
_RE_VERSION = re.compile(r"[vV]\.?\s*(\d+(?:\.\d+)*)")
_RE_MULTIPART = re.compile(r"[Mm](\d+)")
_RE_HACK = re.compile(r"[hH](.*)")
_RE_TRANSLATION = re.compile(r"[Tt]([+-])(.*)")
_RE_DUMP_PART = re.compile(r"([abcfoxt])(\d*)")
_RE_PRERELEASE = re.compile(r"([A-Za-z]+)\s*(\d*)")


@dataclass(frozen=True)
class RomFilenameInfo:
    """Structured facts extracted from a ROM filename."""

    title: str
    regions: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    dump_flags: tuple[str, ...] = ()
    dump_status: DumpStatus = DumpStatus.UNKNOWN
    verified: bool = False
    is_hack: bool = False
    hack_tag: str | None = None
    is_translation: bool = False
    translation_language: str | None = None
    translation_is_newer: bool | None = None
    is_unlicensed: bool = False
    is_public_domain: bool = False
    is_vs: bool = False
    is_playchoice: bool = False
    is_nintendo_power: bool = False
    multipart_index: int | None = None
    prerelease: str | None = None
    prerelease_index: int | None = None
    revision: str | None = None
    version: str | None = None
    unknown_tokens: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        """JSON-friendly view; omits fields left at their defaults."""
        result: dict[str, object] = {"title": self.title}
        for f in fields(self):
            value = getattr(self, f.name)
            if f.name != "title" and value != f.default:
                result[f.name] = value.value if isinstance(value, DumpStatus) else value
        result["expected_tv_system"] = expected_tv_system(self.regions)
        return result


def expected_tv_system(regions: tuple[str, ...] | list[str]) -> str | None:
    """
    TV system implied by a set of region names, or None when the regions are
    absent, mixed (NTSC + PAL together), or not decisive (World, Brazil, ...).
    """
    systems = {_REGION_TV[r] for r in regions if r in _REGION_TV}
    return systems.pop() if len(systems) == 1 else None


def _strip_extension(name: str) -> str:
    """Drop the file extension, but only a dot after the last (...) / [...] group."""
    last_group = max(name.rfind(")"), name.rfind("]"))
    dot = name.rfind(".")
    if dot > last_group:
        extension = name[dot + 1:]
        if extension and len(extension) <= 4 and extension.isalnum():
            return name[:dot].rstrip()
    return name


def _split_tokens(name: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Split an extension-less name into a title and ordered (kind, token) pairs.

    ``kind`` is ``"paren"`` or ``"bracket"``. A ``+`` between adjacent groups
    (GoodTools combines flags like ``[b1]+[T-Rus]``) is dropped rather than
    treated as title text.
    """
    title_parts: list[str] = []
    tokens: list[tuple[str, str]] = []
    pos = 0
    for match in _RE_TOKEN.finditer(name):
        between = name[pos:match.start()].strip()
        if between and between != "+":
            title_parts.append(between)
        pos = match.end()
        paren, bracket = match.groups()
        if paren is not None:
            tokens.append(("paren", paren.strip()))
        else:
            tokens.append(("bracket", (bracket or "").strip()))
    tail = name[pos:].strip()
    if tail:
        title_parts.append(tail)
    return " ".join(" ".join(title_parts).split()), tokens


def _parse_paren(token: str, info: dict) -> None:
    """Classify one parenthesised token into ``info``."""
    marker = token.upper().replace(" ", "")
    if marker in _MARKERS:
        info[_MARKERS[marker]] = True
        return

    pieces = [piece.strip() for piece in token.split(",")]
    if all(piece.lower() in _NO_INTRO_REGIONS_MAP for piece in pieces):
        info["regions"] += tuple(_NO_INTRO_REGIONS_MAP[piece.lower()] for piece in pieces)
        return
    if all(
        re.fullmatch(r"[A-Za-z]{2}", piece) and piece.lower() in _NO_INTRO_LANGUAGES
        for piece in pieces
    ):
        info["languages"] += tuple(_NO_INTRO_LANGUAGES[piece.lower()] for piece in pieces)
        return

    if token in _GOODTOOLS_REGIONS:  # exact match keeps two-letter codes like "SW" intact
        info["regions"] += (_GOODTOOLS_REGIONS[token],)
        return
    if token and len(token) <= 3 and token.isalpha() and all(
        ch in _GOODTOOLS_REGIONS for ch in token
    ):
        info["regions"] += tuple(_GOODTOOLS_REGIONS[ch] for ch in token)
        return

    revision = _RE_REVISION.fullmatch(token)
    if revision:
        info["revision"] = revision.group(1).strip()
        return
    version = _RE_VERSION.fullmatch(token)
    if version:
        info["version"] = version.group(1)
        return
    multipart = _RE_MULTIPART.fullmatch(token)
    if multipart:
        info["multipart_index"] = int(multipart.group(1))
        return
    prerelease = _RE_PRERELEASE.fullmatch(token)
    if prerelease and prerelease.group(1).lower() in _PRERELEASE:
        info["prerelease"] = _PRERELEASE[prerelease.group(1).lower()]
        index = prerelease.group(2)
        info["prerelease_index"] = int(index) if index else None
        return

    info["unknown_tokens"] += (f"({token})",)


def _parse_bracket(token: str, info: dict) -> None:
    """Classify one bracketed token into ``info``."""
    if token == "!":
        info["verified"] = True
        info["dump_flags"] += ("verified",)
        return

    translation = _RE_TRANSLATION.fullmatch(token)
    if translation:
        info["is_translation"] = True
        info["translation_is_newer"] = translation.group(1) == "+"
        info["translation_language"] = translation.group(2) or None
        return

    hack = _RE_HACK.fullmatch(token)
    if hack:
        info["is_hack"] = True
        info["hack_tag"] = hack.group(1) or None
        return

    codes: list[str] = []
    for part in token.split("+"):
        match = _RE_DUMP_PART.fullmatch(part)
        if match is None:
            codes = []
            break
        codes.append(_DUMP_FLAGS[match.group(1)])
    if codes:
        info["dump_flags"] += tuple(codes)
        return

    info["unknown_tokens"] += (f"[{token}]",)


def parse_rom_filename(filename: str | Path) -> RomFilenameInfo:
    """
    Parse naming-convention tags out of a ROM filename.

    Recognises the common subset of the GoodTools and No-Intro conventions;
    anything unrecognised lands in ``unknown_tokens`` verbatim. The file
    extension (a final short alphanumeric suffix after the last tag group)
    is ignored; dots inside the title are kept.
    """
    if isinstance(filename, Path):
        filename = filename.name
    name = _strip_extension(str(filename))
    title, tokens = _split_tokens(name)

    info: dict = {
        "regions": (),
        "languages": (),
        "dump_flags": (),
        "verified": False,
        "is_hack": False,
        "hack_tag": None,
        "is_translation": False,
        "translation_language": None,
        "translation_is_newer": None,
        "is_unlicensed": False,
        "is_public_domain": False,
        "is_vs": False,
        "is_playchoice": False,
        "is_nintendo_power": False,
        "multipart_index": None,
        "prerelease": None,
        "prerelease_index": None,
        "revision": None,
        "version": None,
        "unknown_tokens": (),
    }

    for kind, token in tokens:
        if not token:
            info["unknown_tokens"] += ("()",) if kind == "paren" else ("[]",)
            continue
        if kind == "paren":
            _parse_paren(token, info)
        else:
            _parse_bracket(token, info)

    status = DumpStatus.UNKNOWN
    flag_names = set(info["dump_flags"])
    for candidate in _DUMP_STATUS_PRECEDENCE:
        if candidate.value in flag_names:
            status = candidate
            break

    return RomFilenameInfo(title=title, dump_status=status, **info)
