"""Reusable generation passes.

These are the primitives that most generator plugins end up wanting:
carve N rooms into a grid, connect them with corridors, scatter props.
They are pure functions over numpy arrays so they compose cleanly.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from levelforge.contracts.level import TileKind
from levelforge.contracts.rng import ForgeRNG


@dataclass(frozen=True, slots=True)
class Room:
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)

    def overlaps(self, other: "Room", pad: int = 1) -> bool:
        return not (
            self.x + self.w + pad <= other.x
            or other.x + other.w + pad <= self.x
            or self.y + self.h + pad <= other.y
            or other.y + other.h + pad <= self.y
        )


def carve_rooms(
    grid: NDArray[np.int16],
    rng: ForgeRNG,
    *,
    attempts: int = 240,
    min_size: int = 5,
    max_size: int = 14,
    stream: str = "rooms",
) -> list[Room]:
    """Carve up to ``attempts`` non-overlapping rooms. Returns the accepted set."""
    height, width = grid.shape
    rooms: list[Room] = []
    for _ in range(attempts):
        w = rng.randint(stream, min_size, max_size + 1)
        h = rng.randint(stream, min_size, max_size + 1)
        if w >= width - 2 or h >= height - 2:
            continue
        x = rng.randint(stream, 1, width - w - 1)
        y = rng.randint(stream, 1, height - h - 1)
        candidate = Room(x, y, w, h)
        if any(candidate.overlaps(r, pad=2) for r in rooms):
            continue
        grid[y : y + h, x : x + w] = int(TileKind.FLOOR)
        rooms.append(candidate)
    return rooms


def connect_rooms(
    grid: NDArray[np.int16],
    rooms: list[Room],
    rng: ForgeRNG,
    *,
    stream: str = "corridors",
) -> None:
    """Connect rooms with L-shaped corridors in room order."""
    if len(rooms) < 2:
        return
    order = list(range(len(rooms)))
    rng.stream(stream).shuffle(order)
    for i in range(len(order) - 1):
        a = rooms[order[i]].center
        b = rooms[order[i + 1]].center
        _carve_corridor(grid, a, b)


def _carve_corridor(
    grid: NDArray[np.int16],
    a: tuple[int, int],
    b: tuple[int, int],
) -> None:
    (ax, ay), (bx, by) = a, b
    step_x = 1 if bx >= ax else -1
    for x in range(ax, bx + step_x, step_x):
        grid[ay, x] = int(TileKind.FLOOR)
    step_y = 1 if by >= ay else -1
    for y in range(ay, by + step_y, step_y):
        grid[y, bx] = int(TileKind.FLOOR)


def scatter_props(
    grid: NDArray[np.int16],
    rng: ForgeRNG,
    *,
    prop: TileKind = TileKind.CHEST,
    density: float = 0.02,
    stream: str = "props",
) -> int:
    """Scatter ``prop`` on floor tiles at the given density. Returns count placed."""
    floor_mask = grid == int(TileKind.FLOOR)
    ys, xs = np.nonzero(floor_mask)
    if ys.size == 0:
        return 0
    picks = rng.stream(stream).random(ys.size) < density
    placed = 0
    for y, x, hit in zip(ys.tolist(), xs.tolist(), picks.tolist()):
        if hit:
            grid[y, x] = int(prop)
            placed += 1
    return placed