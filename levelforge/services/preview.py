"""Playable preview runtime.

Renders a level to a pygame surface and lets you walk a little glyph
around it with WASD. This is the "playable" half of the repo — the
generator produces a level, and this service proves it's walkable.

Pygame is an optional dependency (``pip install -e .[play]``). If it
isn't installed, ``run_preview`` raises ``PreviewUnavailable`` with a
clear message instead of an ImportError traceback.
"""

from __future__ import annotations

import logging

from levelforge.contracts.level import Level, TileKind

log = logging.getLogger(__name__)

TILE_PX = 16

COLORS: dict[int, tuple[int, int, int]] = {
    int(TileKind.VO