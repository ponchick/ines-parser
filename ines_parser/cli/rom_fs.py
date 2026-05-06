"""
Filesystem discovery for iNES CLI tools (recursive file list, archive header peek).
"""

from pathlib import Path
from typing import Optional

try:
    import libarchive  # noqa: F401
    LIBARCHIVE_AVAILABLE = True
except ImportError:
    LIBARCHIVE_AVAILABLE = False

from ines_parser import INES_HEADER_SIZE

DEFAULT_ARCHIVE_PATH = "nes_archive/"
ALL_ARCHIVE_FORMATS = frozenset({".7z", ".zip", ".rar"})
ARCHIVE_EXTENSIONS: frozenset[str] = (
    ALL_ARCHIVE_FORMATS if LIBARCHIVE_AVAILABLE else frozenset()
)
SUPPORTED_EXTENSIONS = ARCHIVE_EXTENSIONS | {".nes"}


def collect_supported_files(directory: Path) -> list[Path]:
    """
    Walk ``directory`` once and collect files whose extension matches a supported type.

    Case-insensitive suffix match; skips entries that are not regular files or cannot be stat'd.
    """
    suffixes = {ext.lower() for ext in SUPPORTED_EXTENSIONS}
    paths: list[Path] = []
    for path in directory.rglob("*"):
        try:
            if not path.is_file():
                continue
        except OSError:
            continue
        if path.suffix.lower() in suffixes:
            paths.append(path)
    paths.sort()
    return paths


def read_header_from_blocks(entry) -> Optional[bytes]:
    """Read the first ``INES_HEADER_SIZE`` bytes from a libarchive entry."""
    blocks = []
    total_size = 0

    for block in entry.get_blocks():
        blocks.append(block)
        total_size += len(block)
        if total_size >= INES_HEADER_SIZE:
            break

    header_bytes = b"".join(blocks)
    return header_bytes[:INES_HEADER_SIZE] if len(header_bytes) >= INES_HEADER_SIZE else None
