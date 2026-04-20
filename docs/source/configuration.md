# Configuration Overview

Hike now has a typed configuration model built around three surfaces:

1. **CLI runtime overrides** such as `--config` and `--env-file`
2. **A YAML configuration file** for persistent behavior
3. **An optional `.env` file and JSON schemas** for runtime and validation

The configuration workflow is no longer just "edit one file by hand". You can
bootstrap files, inspect them, validate them, and export schemas directly from
the CLI.

## Quick start

```sh
hike config init
hike config show --format yaml
hike env init
hike schema list
```

## Resolution order

The active configuration file is resolved in this order:

1. A path passed with `--config`
2. The `HIKE_CONFIG_PATH` environment variable
3. `./hike.config.yaml` in the current working directory, if it exists
4. `~/.config/hike/config.yaml`
5. Legacy config files such as `~/.config/hike/configuration.json`

The active environment file follows the same pattern through `--env-file` and
`HIKE_ENV_PATH`.

## Prefer YAML for persistent configuration

Hike still knows how to migrate legacy JSON-shaped config files, but the
current configuration format is YAML. The examples in these docs therefore use
YAML rather than the older JSON snippets.

For example, a small but realistic starting point looks like this:

```yaml
theme: textual-dark
binding_set: mnemonic
local_browser_view_mode: flat-list
startup_auto_open: true
startup_auto_open_patterns:
  - INDEX.md
  - README.md
```

## Configuration guides

Use the following sub-pages depending on what you want to change:

- [Files, Environment & Schemas](configuration-files-and-environment.md)
- [Keybindings](configuration-keybindings.md)
- [File Browser & Startup](configuration-file-browser-and-startup.md)
- [UI, Layout & Content](configuration-ui-and-content.md)

## Common workflows

| Goal | Recommended command flow |
| --- | --- |
| Create a new config file | `hike config init` |
| Inspect current saved values | `hike config show --format yaml` |
| Override a setting for one launch | `hike --config custom.yaml open ...` |
| Set up runtime environment variables | `hike env init` |
| Validate config or env files | `hike config validate` / `hike env validate` |
| Export schemas for editor integration | `hike schema export --out .schemas` |

[//]: # (configuration.md ends here)
