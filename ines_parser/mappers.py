"""
Backward-compatible re-exports of mapper lookups.

Prefer ``ines_parser.tables`` for all header lookup tables (mappers,
submappers, Vs. types, expansion devices, etc.).
"""

from .tables import (
    MAPPER_DATABASE,
    get_mapper_alternate_names,
    get_mapper_info,
    get_mapper_name,
    get_mapper_notes,
    is_known_mapper,
)

__all__ = [
    "MAPPER_DATABASE",
    "get_mapper_name",
    "get_mapper_alternate_names",
    "get_mapper_notes",
    "get_mapper_info",
    "is_known_mapper",
]
