"""Plugin registry — the single source of truth for what's loaded.

The registry is thread-safe for lookups; registration happens once at
startup under a lock. Lookups are lock-free reads of an immutable map
that gets swapped on registration.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

from levelforge.contracts.plugin import PluginKind, PluginManifest

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RegisteredPlugin:
    manifest: PluginManifest
    instance: Any
    module_path: str


class PluginRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_id: dict[str, RegisteredPlugin] = {}
        self._by_kind: dict[PluginKind, list[str]] = {k: [] for k in PluginKind}

    def register(self, entry: RegisteredPlugin) -> None:
        with self._lock:
            if entry.manifest.id in self._by_id:
                raise ValueError(f"plugin id already registered: {entry.manifest.id}")
            self._by_id[entry.manifest.id] = entry
            self._by_kind[entry.manifest.kind].append(entry.manifest.id)
            log.info(
                "registered plugin %s (%s) from %s",
                entry.manifest.id,
                entry.manifest.kind.value,
                entry.module_path,
            )

    def get(self, plugin_id: str) -> RegisteredPlugin:
        try:
            return self._by_id[plugin_id]
        except KeyError as exc:
            raise KeyError(f"no such plugin: {plugin_id}") from exc

    def by_kind(self, kind: PluginKind) -> list[RegisteredPlugin]:
        return [self._by_id[pid] for pid in self._by_kind[kind]]

    def ids(self) -> list[str]:
        return sorted(self._by_id.keys())

    def __len__(self) -> int:
        return len(self._by_id)