"""Level quality metrics used by validators and by the CLI report."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from levelforge.contracts.level import Level, TileKind


@dataclass(frozen=True, slots=True)
class LevelMetrics:
    width: int
    height: int
    floor_ratio: float
    wall_ratio: float
    reachable_floor_ratio: float
    room_count: int
    connected_components: int


def compute_metrics(level: Level) -> LevelMetrics:
    layer = level.primary()
    grid = layer.grid
    total = grid.size or 1
    floor = int(np.count_nonzero(grid == int(TileKind.FLOOR)))
    wall = int(np.count_nonzero(grid == int(TileKind.WALL)))
    components, reachable = _components(grid)
    return LevelMetrics(
        width=layer.width,
        height=layer.height,
        floor_ratio=floor / total,
        wall_ratio=wall / total,
        reachable_floor_ratio=reachable / max(floor, 1),
        room_count=int(level.meta.extra.get("room_count", 0)),
        connected_components=components,
    )


def _components(grid: np.ndarray) -> tuple[int, int]:
    """Return (component_count, size_of_largest) over floor-connected tiles."""
    floor = grid == int(TileKind.FLOOR)
    h, w = floor.shape
    seen = np.zeros_like(floor, dtype=bool)
    largest = 0
    count = 0
    for y0 in range(h):
        for x0 in range(w):
            if not floor[y0, x0] or seen[y0, x0]:
                continue
            count += 1
            stack = [(y0, x0)]
            seen[y0, x0] = True
            size = 0
            while stack:
                y, x = stack.pop()
                size += 1
                for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= ny < h and 0 <= nx < w and floor[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            largest = max(largest, size)
    return count, largest