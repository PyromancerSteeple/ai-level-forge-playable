# Security Policy

## Scope

`ai-level-forge-playable` runs third-party plugin code inside the host
process. Plugins are Python modules and are **not** sandboxed by the
default runtime. Treat any plugin you install the same way you'd treat
any package you `pip install`.

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Email `security@levelforge.dev` with a description, a minimal plugin
or seed that reproduces, and the forge version. We aim to acknowledge
within 72 hours.

Do not open a public issue for anything that lets a plugin escape the
plugin contract boundary, write outside `forge.paths.WORKSPACE_ROOT`,
or cause the host to load a module without going through the registry.

## Plugin trust model

- Plugin discovery reads `forge_plugins/` and any path in
  `FORGE_PLUGIN_PATH`.
- The host does **not** verify plugin signatures in 0.6.x. Signing lands
  in 0.7. Until then, pin plugin versions in your `plugins.lock`.
- Plugins run with the host's permissions. Run untrusted plugins in a
  container or a dedicated user account.

## What we consider a vulnerability

- Arbitrary code execution triggered by loading a `.lvlpack` file.
- Path traversal via a plugin's `output_path` argument.
- Registry bypass that loads a module not declared in a manifest.

## What we don't

- A plugin that generates bad levels. That's a bug report, not a CVE.
- A plugin that crashes the host. Also a bug report.