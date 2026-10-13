"""Deterministic RNG wrapper.

Plugins must draw randomness through ``ForgeRNG`` so that a level is
reproducible from its seed. Using ``random`` or ``numpy.random`` directly
inside a plugin breaks the golden-seed tests and CI will reject the PR.
"""

from __future__ import annotations

import hashlib
from typing import Sequence

import numpy as np


class ForgeRNG:
    """Splitmix-style deterministic RNG with named sub-streams."""

    __slots__ = ("_seed", "_streams")

    def __init__(self, seed: int) -> None:
        self._seed = int(seed) & 0xFFFFFFFFFFFFFFFF
        self._streams: dict[str, np.random.Generator] = {}

    @property
    def seed(self) -> int:
        return self._seed

    def stream(self, name: str) -> np.random.Generator:
        """Return a stable sub-generator for ``name``."""
        gen = self._streams.get(name)
        if gen is None:
            digest = hashlib.blake2b(
                f"{self._seed}:{name}".encode("utf-8"), digest_size=8
            ).digest()
            sub_seed = int.from_bytes(digest, "little")
            gen = np.random.default_rng(sub_seed)
            self._streams[name] = gen
        return gen

    def choice(self, name: str, items: Sequence[object]) -> object:
        if not items:
            raise ValueError("choice() called with empty sequence")
        idx = int(self.stream(name).integers(0, len(items)))
        return items[idx]

    def randint(self, name: str, low: int, high: int) -> int:
        return int(self.stream(name).integers(low, high))

    def uniform(self, name: str, low: float, high: float) -> float:
        return float(self.stream(name).uniform(low, high))

    def fork(self, name: str) -> "ForgeRNG":
        """Derive a child RNG so parallel passes don't share a stream."""
        digest = hashlib.blake2b(
            f"{self._seed}:fork:{name}".encode("utf-8"), digest_size=8
        ).digest()
        return ForgeRNG(int.from_bytes(digest, "little"))