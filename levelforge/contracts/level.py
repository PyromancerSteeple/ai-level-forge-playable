"""Level data model — the wire format every plugin speaks."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

import numpy as np
from numpy.typing import NDArray


class TileKind(IntEnum):
    """Canonical tile palette. Plugins may add kinds via ``LevelMeta.extra_tiles``."""

    VOID = 0
    FLOOR = 1
    WALL = 2
    DOOR = 3
    STAIRS_UP = 4
    STAIRS_DOWN = 5
    WATER = 6
    LAVA = 7
    SPAWN = 8
    GOAL = 9
    CHEST = 10
    TRAP = 11


@dataclass(slots=True)
class TileLayer:
    """A single 2D tile grid. ``grid[y, x]`` holds a ``TileKind`` value."""

    name: str
    grid: NDArray[np.int16]
    z: int = 0

    @classmethod
    def empty(cls, name: str, width: int, height: int, z: int = 0) -> "TileLayer":
        return cls(name=name, grid=np.zeros((height, width), dtype=np.int16), z=z)

    @property
    def width(self) -> int:
        return int(self.grid.shape[1])

    @property
    def height(self) -> int:
        return int(self.grid.shape[0])


@dataclass(slots=True)
class LevelMeta:
    """Metadata carried alongside a level. Free-form ``extra`` is for plugins."""

    name: str
    author: str = "forge"
    seed: int = 0
    generator_id: str = ""
    tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Level:
    """A generated level: one or more tile layers plus metadata."""

    meta: LevelMeta
    layers: list[TileLayer] = field(default_factory=list)

    def primary(self) -> TileLayer:
        if not self.layers:
            raise ValueError("level has no layers")
        return self.layers[0]

    def add_layer(self, layer: TileLayer) -> None:
        self.layers.append(layer)

    def to_pack(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict for ``.lvlpack`` writing."""
        return {
            "meta": {
                "name": self.meta.name,
                "author": self.meta.author,
                "seed": self.meta.seed,
                "generator_id": self.meta.generator_id,
                "tags": list(self.meta.tags),
                "extra": dict(self.meta.extra),
            },
            "layers": [
                {"name": l.name, "z": l.z, "grid": l.grid.tolist()}
                for l in self.layers
            ],
        }

    @classmethod
    def from_pack(cls, blob: dict[str, Any]) -> "Level":
        meta_raw = blob["meta"]
        meta = LevelMeta(
            name=meta_raw["name"],
            author=meta_raw.get("author", "forge"),
            seed=int(meta_raw.get("seed", 0)),
            generator_id=meta_raw.get("generator_id", ""),
            tags=list(meta_raw.get("tags", [])),
            extra=dict(meta_raw.get("extra", {})),
        )
        layers = [
            TileLayer(
                name=l["name"],
                z=int(l.get("z", 0)),
                grid=np.asarray(l["grid"], dtype=np.int16),
            )
            for l in blob["layers"]
        ]
        return cls(meta=meta, layers=layers)