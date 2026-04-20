# CLI Reference

This page documents Hike's external Typer CLI. For the command line that lives
inside the TUI itself, see [In-App Command Line](commands.md).

## `hike`

The root command exposes shared runtime options plus the top-level command
groups.

```bash exec="on" result="ansi" width="120"
hike --help
```

### Global options

| Option | Purpose |
| --- | --- |
| `--config PATH` | Use an alternate configuration file for this invocation. |
| `--env-file PATH` | Use an alternate `.env` file for runtime settings. |
| `--version` | Print version and build metadata, then exit. |
| `--license`, `--licence` | Print fork-aware license information, then exit. |
| `--install-completion` | Install shell completion for the current shell. |
| `--show-completion` | Print the completion script for the current shell. |
| `--help` | Show root help. |

### Root commands

| Command | Purpose |
| --- | --- |
| `hike license` | Show Hike's full license text in the terminal. |
| `hike open` | Launch the TUI against a file, directory, URL, or startup command. |
| `hike config` | Manage configuration files and values. |
| `hike schema` | Inspect and export schemas for config and env files. |
| `hike env` | Manage runtime environment values. |
| `hike bindings` | Inspect configurable keybindings and keybinding sets. |
| `hike themes` | List available Textual themes. |

### Fast metadata commands

The root metadata flags do **not** launch the TUI:

- `hike --version`
- `hike --license`
- `hike license`

## `hike open`

`open` is the main TUI launcher and accepts the most startup options.

```bash exec="on" result="ansi" width="120"
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

### Important `open` options

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

## `hike license`

The dedicated `license` command prints the full GPL text plus the fork-specific
attribution summary. Use it when you want the actual license body, not just the
short root metadata flag.

See also the separate [License](license.md) page for a short web-friendly
summary and links back to the repository license file.

## `hike config`

The configuration command group manages the active YAML configuration file.

```bash exec="on" result="ansi" width="120"
hike config --help
```

### `config` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike config init` | Create a commented default configuration file. | `--force` overwrites after creating a backup. |
| `hike config show` | Display the current configuration. | `--format yaml|json` |
| `hike config get` | Read a single configuration property. | `<property-path>` |
| `hike config set` | Set a configuration property. | `<property-path> <value>` |
| `hike config unset` | Unset a configuration property. | `<property-path>` |
| `hike config validate` | Validate the active configuration file. | No extra options. |
| `hike config path` | Print the effective configuration file path. | No extra options. |

## `hike schema`

The schema command group works with JSON schemas for config and env files.

```bash exec="on" result="ansi" width="120"
hike schema --help
```

### `schema` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike schema list` | List the available schema types. | No extra options. |
| `hike schema show` | Print a JSON schema to stdout. | `<config|env>` |
| `hike schema validate` | Validate a file against one of Hike's schema types. | `<file> --type config|env` |
| `hike schema export` | Export all supported schemas as JSON files. | `--out PATH` |
| `hike schema path` | Print the default export path for a schema type. | `<config|env>` |

## `hike env`

The env command group manages the optional `.env` file used for runtime
overrides.

```bash exec="on" result="ansi" width="120"
hike env --help
```

### `env` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike env init` | Create a commented environment file. | `--force`, `--example` |
| `hike env show` | Display the current environment file contents. | `--reveal` to show raw values |
| `hike env list` | List supported environment variables. | No extra options. |
| `hike env get` | Get a value from the environment file. | `<VARIABLE>` |
| `hike env set` | Set a value in the environment file. | `<VARIABLE> <VALUE>` |
| `hike env unset` | Unset a value in the environment file. | `<VARIABLE>` |
| `hike env validate` | Validate the current environment file. | No extra options. |
| `hike env path` | Print the effective environment-file path. | No extra options. |

## `hike bindings`

The bindings command group shows configurable commands and named keybinding
sets.

```bash exec="on" result="ansi" width="120"
hike bindings --help
```

### `bindings` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike bindings list` | List commands that support keybinding overrides. | No extra options. |
| `hike bindings sets` | List the built-in and custom keybinding sets. | No extra options. |

## `hike themes`

The themes command group prints the available Textual themes.

```bash exec="on" result="ansi" width="120"
hike themes --help
```

### `themes` subcommands

| Command | Purpose | Important options / arguments |
| --- | --- | --- |
| `hike themes list` | List available themes. | No extra options. |

[//]: # (cli.md ends here)
