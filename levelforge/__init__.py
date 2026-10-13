"""ai-level-forge-playable — plugin-host AI level generator.

The package is split into three rings:

* ``levelforge.contracts`` — the frozen plugin API. No host imports.
* ``levelforge.core``      — pure generation logic, host-agnostic.
* ``levelforge.host``      — the running host: loader, registry, services.

Plugins may import ``contracts`` and ``core``. They must not import
``host``. That boundary is what lets the same generator run inside the
CLI, the playable preview, and the headless batch tool.
"""

__version__ = "0.6.3"
__all__ = ["__version__"]