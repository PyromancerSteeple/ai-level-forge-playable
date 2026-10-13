# Contributing to ai-level-forge-playable

Thanks for wanting to build on the Forge. This is a plugin-host level
generator: a core host process that loads extension modules which
contribute generators, decorators, validators, and renderers. If you
can write a Python class and register it, you can ship a plugin.

## Ground rules

- One feature per PR. Small diffs review fast.
- Every plugin must register through `forge.core.registry.PluginRegistry`
  and expose a `MANIFEST` dict at module top.
- New generator plugins must ship a golden-seed test under
  `tests/` that pins the RNG output for at least three seeds.
- Do not import `forge.host` from a plugin. Plugins talk to the host
  through `forge.contracts` only. That boundary is load-bearing.
- Type hints required on all public functions. `mypy --strict` runs in CI.
- Format with `black -l 100` and `ruff check .` before pushing.

## Plugin layout

```
forge_plugins/
  my_generator/
    __init__.py
    manifest.py
    generator.py
    rules.py
```

`manifest.py` exports `MANIFEST` with keys: `id`, `name`, `version`,
`author`, `entry`, `kind` (one of `generator`, `decorator`, `validator`,
`renderer`), `api_version`.

## Testing a plugin locally

```
python -m levelforge.cli list-plugins
python -m levelforge.cli generate --plugin my_generator --seed 1337 --out ./generated_levels
python -m pytest tests/ -k my_generator
```

## Commit style

`forge(<area>): <imperative summary>` — e.g.
`forge(generators): add cave-carver cellular automata pass`.

## Reporting bugs

Open an issue with: forge version (`python -m levelforge.cli version`),
plugin list, seed, and the `.lvlpack` that misbehaved if you can share it.