"""Read/write ``.lvlpack`` files.

A ``.lvlpack`` is a JSON document (gzip-compressed by default) holding
one serialized ``Level``. The format is versioned in the header so a
future host can migrate old packs.
"""

from __future__ import annotations

import gzip
import json
import logging
from pathlib import Path

from levelforge.contracts.level import Level

log = logging.getLogger(__name__)

PACK_MAGIC = "LFPK"
PACK_VERSION = 1


def write_pack(level: Level, path: Path) -> None:
    payload = {
        "magic": PACK_MAGIC,
        "version": PACK_VERSION,
        "level": level.to_pack(),
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb", compresslevel=6) as fh:
        fh.write(raw)
    log.info("wrote pack %s (%d bytes raw)", path, len(raw))


def read_pack(path: Path) -> Level:
    with gzip.open(path, "rb") as fh:
        payload = json.loads(fh.read().decode("utf-8"))
    if payload.get("magic") != PACK_MAGIC:
        raise ValueError(f"{path}: not a levelforge pack")
    version = int(payload.get("version", 0))
    if version > PACK_VERSION:
        raise ValueError(
            f"{path}: pack version {version} is newer than this host supports ({PACK_VERSION})"
        )
    return Level.from_pack(payload["level"])