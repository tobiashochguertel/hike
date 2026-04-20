# Configuration Files, Environment & Schemas

This page covers the operational side of Hike configuration: where settings
live, how to override them, and how to validate them.

## Configuration file management

```bash exec="on" result="ansi" width="120"
hike config --help
```

The `config` command group is the best entry point for persistent
configuration. Typical workflows are:

```sh
hike config init
hike config show --format yaml
hike config validate
hike config path
```

## Environment file management

```bash exec="on" result="ansi" width="120"
hike env --help
```

Use the environment file when you want machine- or workspace-specific runtime
values without baking them into the main YAML config.

Common workflows:

```sh
hike env init
hike env show
hike env validate
hike env path
```

## Supported runtime environment variables

```bash exec="on" result="ansi" width="120"
hike env list
```

The two most important top-level overrides are:

- `HIKE_CONFIG_PATH` for the active YAML config file
- `HIKE_ENV_PATH` for the active `.env` file

## Schema support

Hike can inspect, print, validate, and export JSON schemas for both config and
env files.

```bash exec="on" result="ansi" width="120"
hike schema --help
```

```bash exec="on" result="ansi" width="120"
hike schema list
```

Useful schema workflows:

```sh
hike schema show config
hike schema validate --type config hike.config.yaml
hike schema export --out .schemas
```

## Example layout

One practical split is to keep persistent behavior in YAML and runtime-specific
paths or debug toggles in the environment file:

```yaml
# hike.config.yaml
theme: nord
binding_set: mnemonic
startup_auto_open: true
local_browser_view_mode: flat-list
```

```dotenv
# .env
HIKE_DEBUG=1
HIKE_SCHEMA_STORE_PATH=.schemas
```

## Legacy config migration

If you still have an older `configuration.json`, Hike can migrate it onto the
modern YAML path:

```sh
hike config init --force
```

That command keeps the modern commented YAML format as the source of truth.

[//]: # (configuration-files-and-environment.md ends here)
