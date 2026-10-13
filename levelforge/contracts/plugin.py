"""Plugin protocol definitions.

Every plugin ships a ``MANIFEST`` dict that validates against
``PluginManifest``, plus one class implementing the matching protocol.
"""

from __future__ import annotations

from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field

from levelforge.contracts.level import Level
from levelforge.contracts.rng import ForgeRNG


class PluginKind(str, Enum):
    GENERATOR = "generator"
    DECORATOR = "decorator"
    VALIDATOR = "validator"
    RENDERER = "renderer"


class PluginManifest(BaseModel):
    """Validated plugin manifest. Rejected at load time if any field is bad."""

    id: str = Field(pattern=r"^[a-z][a-z0-9_]{2,48}$")
    name: str
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    author: str
    entry: str  # "package.module:ClassName"
    kind: PluginKind
    api_version: str = "0.6"
    description: str = ""
    tags: list[str] = Field(default_factory=list)


@runtime_checkable
class GeneratorPlugin(Protocol):
    """Produces a fresh ``Level`` from a seed and parameters."""

    manifest: PluginManifest

    def generate(self, rng: ForgeRNG, params: dict[str, object]) -> Level: ...


@runtime_checkable
class DecoratorPlugin(Protocol):
    """Mutates an existing level in place (adds props, carves rooms, etc.)."""

    manifest: PluginManifest

    def decorate(self, level: Level, rng: ForgeRNG) -> None: ...


@runtime_checkable
class ValidatorPlugin(Protocol):
    """Checks a level against a rule. Returns a list of violation strings."""

    manifest: PluginManifest

    def validate(self, level: Level) -> list[str]: ...


@runtime_checkable
class RendererPlugin(Protocol):
    """Renders a level to the playable preview surface."""

    manifest: PluginManifest

    def render(self, level: Level, surface_id: int) -> None: ...