"""Plugin loader.

Discovers plugin packages on ``FORGE_PLUGIN_PATH`` (plus the bundled
``forge_plugins/`` directory), imports each one, validates its
``MANIFEST``, instantiates the entry class, and registers it.

A plugin whose manifest fails validation is skipped with a warning — the
host never crashes because one plugin is malformed.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys
from pathlib import Path

from levelforge.contracts.plugin import PluginManifest
from levelforge.host.registry import PluginRegistry, RegisteredPlugin

log = logging.getLogger(__name__)

BUNDLED_PLUGIN_DIR = Path(__file__).resolve().parents[2] / "forge_plugins"


class PluginLoader:
    def __init__(self, registry: PluginRegistry) -> None:
        self.registry = registry

    def search_paths(self) -> list[Path]:
        paths: list[Path] = []
        env = os.environ.get("FORGE_PLUGIN_PATH", "")
        for raw in env.split(os.pathsep):
            if raw.strip():
                paths.append(Path(raw).expanduser().resolve())
        if BUNDLED_PLUGIN_DIR.is_dir():
            paths.append(BUNDLED_PLUGIN_DIR)
        return paths

    def discover(self) -> list[Path]:
        found: list[Path] = []
        for root in self.search_paths():
            for child in sorted(root.iterdir()):
                if child.is_dir() and (child / "__init__.py").is_file():
                    found.append(child)
        return found

    def load_all(self) -> int:
        loaded = 0
        for pkg_dir in self.discover():
            try:
                self._load_one(pkg_dir)
                loaded += 1
            except Exception as exc:  # noqa: BLE001 — one bad plugin must not kill the host
                log.warning("skipping plugin at %s: %s", pkg_dir.name, exc)
        return loaded

    def _load_one(self, pkg_dir: Path) -> None:
        module_name = f"forge_plugins.{pkg_dir.name}"
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            spec = importlib.util.spec_from_file_location(
                module_name, pkg_dir / "__init__.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"cannot build spec for {pkg_dir}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

        raw_manifest = getattr(module, "MANIFEST", None)
        if raw_manifest is None:
            raise ValueError("plugin has no MANIFEST dict")
        manifest = PluginManifest.model_validate(raw_manifest)

        entry_ref = manifest.entry
        if ":" not in entry_ref:
            raise ValueError(f"bad entry ref {entry_ref!r}; expected 'module:Class'")
        cls_module_name, cls_name = entry_ref.split(":", 1)
        cls_module = importlib.import_module(cls_module_name)
        cls = getattr(cls_module, cls_name)
        instance = cls()
        instance.manifest = manifest

        self.registry.register(
            RegisteredPlugin(
                manifest=manifest,
                instance=instance,
                module_path=str(pkg_dir),
            )
        )