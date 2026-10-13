"""Playable preview session.

A ``ForgeSession`` owns a registry, a working level, and a small command
queue so the CLI, the headless batch tool, and the pygame preview can
all drive the same object.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from levelforge.contracts.level import Level, LevelMeta
from levelforge.contracts.plugin import PluginKind
from levelforge.contracts.rng import ForgeRNG
from levelforge.host.registry import PluginRegistry

log = logging.getLogger(__name__)


@dataclass
class ForgeSession:
    registry: PluginRegistry
    seed: int = 1
    params: dict[str, object] = field(default_factory=dict)
    level: Level | None = None

    def generate(self, generator_id: str) -> Level:
        entry = self.registry.get(generator_id)
        if entry.manifest.kind is not PluginKind.GENERATOR:
            raise ValueError(f"{generator_id} is not a generator plugin")
        rng = ForgeRNG(self.seed)
        level = entry.instance.generate(rng, self.params)
        self.level = level
        log.info(
            "generated level %r via %s (seed=%d)",
            level.meta.name,
            generator_id,
            self.seed,
        )
        return level

    def decorate(self, decorator_id: str) -> None:
        if self.level is None:
            raise RuntimeError("no level loaded; call generate() first")
        entry = self.registry.get(decorator_id)
        if entry.manifest.kind is not PluginKind.DECORATOR:
            raise ValueError(f"{decorator_id} is not a decorator plugin")
        entry.instance.decorate(self.level, ForgeRNG(self.seed ^ 0xF0F0))

    def validate(self) -> list[str]:
        if self.level is None:
            raise RuntimeError("no level loaded; call generate() first")
        problems: list[str] = []
        for entry in self.registry.by_kind(PluginKind.VALIDATOR):
            problems.extend(
                f"[{entry.manifest.id}] {msg}"
                for msg in entry.instance.validate(self.level)
            )
        return problems

    def save(self, path: Path) -> None:
        if self.level is None:
            raise RuntimeError("no level loaded; call generate() first")
        from levelforge.services.pack_writer import write_pack

        write_pack(self.level, path)

    @classmethod
    def load(cls, registry: PluginRegistry, path: Path) -> "ForgeSession":
        from levelforge.services.pack_writer import read_pack

        level = read_pack(path)
        session = cls(registry=registry, seed=level.meta.seed)
        session.level = level
        return session

    def empty_level(self, name: str, width: int, height: int) -> Level:
        from levelforge.contracts.level import TileLayer

        meta = LevelMeta(name=name, seed=self.seed)
        level = Level(meta=meta)
        level.add_layer(TileLayer.empty("base", width, height))
        self.level = level
        return level