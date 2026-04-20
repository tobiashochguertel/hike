# CLI Reference

This page documents Hike's external Typer-based CLI. For the in-app command
line inside the TUI, see [In-App Command Line](commands.md).

## `hike`

The root command exposes global options and the main command groups.

```bash exec="on" result="ansi" width=120
hike --help
```

### Global options

| Option | Purpose |
| --- | --- |
| `--config PATH` | Use an alternate configuration file for this invocation. |
| `--env-file PATH` | Use an alternate `.env` file for runtime settings. |
| `--version` | Print version/build metadata and exit. |
| `--license`, `--licence` | Print license and fork attribution information and exit. |
| `--help` | Show root help. |

### Root commands

| Command | Purpose |
| --- | --- |
| `hike license` | Show the fork-aware license summary. |
| `hike open` | Launch the TUI against a file, directory, URL, or startup command. |
| `hike config` | Manage configuration files and values. |
| `hike schema` | Inspect and export schemas for config and env files. |
| `hike env` | Manage runtime environment values. |
| `hike bindings` | Inspect configurable keybindings and keybinding sets. |
| `hike themes` | List available Textual themes. |

## Hike open

`open` is the main TUI launcher and accepts the most startup options.

```bash exec="on" result="ansi" width=120
hike open --help
```

### Startup targets

| Form | Behavior |
| --- | --- |
| `hike open` | Start in the configured local browser root and auto-open a preferred document if possible. |
| `hike open README.md` | Open a local file directly. |
| `hike open docs/` | Root the local browser at a directory and auto-open from there. |
| `hike open https://example.com/file.md` | Open a remote Markdown URL directly. |
| `hike open --command "gh tobiashochguertel/hike"` | Run an in-app command at startup. |

### Key `open` options

| Option | Purpose |
| --- | --- |
| `--command`, `-c` | Run an in-app command instead of opening a direct target. |
| `--navigation`, `--no-navigation` | Force the sidebar visible or hidden at startup. |
| `--theme`, `-t` | Override the configured theme for this launch. |
| `--binding-set` | Override the active named keybinding set for this launch. |
| `--root PATH` | Override the initial local browser root. |
| `--ignore`, `--no-ignore` | Enable or disable `.gitignore` / `.ignore` filtering. |
| `--hidden`, `--no-hidden` | Show or hide dotfiles in the local browser. |
| `--exclude TEXT` | Add one or more exclude globs. |

## `hike config`

The configuration command group manages the active YAML configuration file.

```bash exec="on" result="ansi" width=120
hike config --help
```

### `config` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike config init` | Create a commented default config file. | `--force` overwrites after creating a backup. |
| `hike config show` | Print the current config. | `--format yaml|json` |
| `hike config get` | Read one config value. | `<property-path>` |
| `hike config set` | Update one config value. | `<property-path> <value>` |
| `hike config unset` | Remove one config value. | `<property-path>` |
| `hike config validate` | Validate the active config file. | No extra options. |
| `hike config path` | Print the effective config path. | No extra options. |

## `hike schema`

The schema command group works with JSON schemas for config and env files.

```bash exec="on" result="ansi" width=120
hike schema --help
```

### `schema` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike schema list` | List supported schema types. | No extra options. |
| `hike schema show` | Print a schema to stdout. | `<config|env>` |
| `hike schema validate` | Validate a file against a schema type. | `<file> --type config|env` |
| `hike schema export` | Write schema files to disk. | `--out PATH` |
| `hike schema path` | Print the default export path. | `<config|env>` |

## `hike env`

The env command group manages the optional `.env` file used for runtime
overrides.

```bash exec="on" result="ansi" width=120
hike env --help
```

### `env` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike env init` | Create a commented `.env` file. | `--force`, `--example` |
| `hike env show` | Print the current env file contents. | `--reveal` to show raw values |
| `hike env list` | List supported environment variables. | No extra options. |
| `hike env get` | Read one environment variable. | `<VARIABLE>` |
| `hike env set` | Update one environment variable. | `<VARIABLE> <VALUE>` |
| `hike env unset` | Remove one environment variable. | `<VARIABLE>` |
| `hike env validate` | Validate the current env file. | No extra options. |
| `hike env path` | Print the effective env-file path. | No extra options. |

## `hike bindings`

The bindings command group shows configurable commands and named keybinding
sets.

```bash exec="on" result="ansi" width=120
hike bindings --help
```

### `bindings` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike bindings list` | List commands with configurable bindings. | No extra options. |
| `hike bindings sets` | List built-in and custom binding sets. | No extra options. |

## `hike themes`

The themes command group prints the available Textual themes.

```bash exec="on" result="ansi" width=120
hike themes --help
```

### `themes` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike themes list` | Print the available themes. | No extra options. |

[//]: # (cli.md ends here)
