# Hike

[![Hike](https://raw.githubusercontent.com/davep/hike/refs/heads/main/.images/hike-social-banner.png)](https://tobiashochguertel.github.io/hike/)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/tobiashochguertel/hike/style-lint-and-test.yaml)](https://github.com/tobiashochguertel/hike/actions)
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/tobiashochguertel/hike/latest)](https://github.com/tobiashochguertel/hike/commits/main/)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/tobiashochguertel/hike)](https://github.com/tobiashochguertel/hike/issues)
[![GitHub Release Date](https://img.shields.io/github/release-date/tobiashochguertel/hike)](https://github.com/tobiashochguertel/hike/releases)
[![PyPI - License](https://img.shields.io/pypi/l/hike)](https://github.com/tobiashochguertel/hike/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hike)](https://github.com/tobiashochguertel/hike/blob/main/pyproject.toml)
[![PyPI - Version](https://img.shields.io/pypi/v/hike)](https://pypi.org/project/hike/)

## Introduction

Hike is a [Markdown](https://commonmark.org/help/) browser for the terminal.
It provides the ability to browse for and view local Markdown files, as well
as Markdown files that can be downloaded from the web. It also has shortcuts
that make it easy to view Markdown files on popular git forges.

## Installing

### pipx

The application can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
pipx install hike
```

### uv

The package can be install using [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv tool install hike
```

If you don't have `uv` installed you can use [uvx.sh](https://uvx.sh) to
perform the installation. For GNU/Linux or macOS or similar:

```sh
curl -LsSf uvx.sh/hike/install.sh | sh
```

or on Windows:

```sh
powershell -ExecutionPolicy ByPass -c "irm https://uvx.sh/hike/install.ps1 | iex"
```

### Other installation methods

The following installation methods have been provided by third parties;
please note that I can't vouch for them myself so use them at your own risk.

#### X-CMD

The application can be installed using [`x-cmd`](https://x-cmd.com):

```sh
x install hike
```

## Using Hike

Once you've installed Hike using one of the above methods, you can run the
application using the `hike` command.

Common startup patterns include:

```sh
hike open
hike open --command "gh davep/hike"
hike open README.md
hike open docs/
hike open https://example.com/README.md
hike --config ~/.config/hike/work-docs.yaml open --root docs
hike open --root docs --exclude generated/ --hidden
hike open --no-ignore
```

When you start Hike without an explicit file target, it now roots the local
browser at the configured start location (the current working directory by
default), then auto-opens a preferred document if one is available. The default
preference order is `INDEX.md`, then `README.md`, then the first visible
Markdown file in local-browser order. You can tune this with
`startup_auto_open`, `startup_auto_open_patterns`, and `local_start_location`
in the config file.

The structured CLI now also includes:

```sh
hike --version
hike --license
hike bindings list
hike bindings sets
hike themes list
hike config init
hike config show --format yaml
hike config set binding_set mnemonic
hike config set bindings.JumpToBookmarks shift+f6
hike schema list
hike schema export
hike env init
hike env validate
```

`hike --version` now includes the package version plus the best available build
metadata, including git commit, branch, and build/install timestamp.

If you still have a legacy `~/.config/hike/configuration.json`, running
`hike config init --force` now migrates you onto the modern YAML config path.
By default, <kbd>Ctrl</kbd>+<kbd>C</kbd> now quits the TUI immediately so a bad
draw state can't leave your shell stuck in raw mode.
If you want Textual's reminder/copy-first behavior instead, set
`allow_traditional_quit: false` in your Hike config file.

The best way to get to know Hike is to read the help screen. Once in the
application you can see this by pressing <kbd>F1</kbd>.

![Hike Help](https://raw.githubusercontent.com/davep/hike/refs/heads/main/.images/hike-help.png)

Commands can also be discovered via the command palette
(<kbd>ctrl</kbd>+<kbd>p</kbd>):

![The command palette](https://raw.githubusercontent.com/davep/hike/refs/heads/main/.images/hike-command-palette.png)

On narrower terminals Hike automatically switches to a single-pane layout. Use
<kbd>Ctrl</kbd>+<kbd>N</kbd> to show the active sidebar view and
<kbd>Ctrl</kbd>+<kbd>G</kbd> to return to the markdown content.

The local browser can also switch between a tree and a flat list of relative
paths. Use <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>L</kbd> to toggle the local
browser mode. In the local browser, press <kbd>Backspace</kbd> to move the
browser root to the parent directory; in flat-list mode the first entry also
becomes `../` when a parent directory is available.

For more information and details on configuring Hike, see [the online
documentation](https://tobiashochguertel.github.io/hike/). The documentation's
Textual screenshots are rendered automatically during `make docs` and the
GitHub Pages workflow.

## Taskfile workflow

This fork includes a `Taskfile.yml` for the "all requested features" workflow.

List the available tasks:

```sh
task --list
```

Run the full validation suite:

```sh
task check
```

Merge a feature branch into `feature/all-requested-features`, validate the
merged branch, and push it:

```sh
task merge-all-requested-features SOURCE_BRANCH=feat/local-browser-modes
```

Install Hike from `feature/all-requested-features`:

```sh
task install-all-requested-features
```

Or do the full merge + validate + push + install flow in one step:

```sh
task refresh-all-requested-features SOURCE_BRANCH=feat/local-browser-modes
```

## Features

- A command line where file names, URLs and commands can be entered.
- A local file browser that respects `.gitignore` and `.ignore` files, with
  CLI toggles for hidden files, ignore handling and extra excludes.
- A smaller, auto-fitting navigation sidebar with responsive single-pane
  behavior for narrow terminals.
- A switchable local browser that can render either as a tree or as a flat list
  of relative paths, automatically hiding empty directories in flat-list mode.
- A simple bookmarking system.
- A browsing history.
- The ability to edit markdown documents in the local filesystem, either
  using your editor of choice or a simple builtin editor.
- Commands for quickly loading and viewing files held on GitHub, GitLab,
  Codeberg and Bitbucket.
- A command palette to make it easy to discover commands and their keys.
- A rich help screen to make it easy to discover commands and their keys.
- [Possibly more as time goes on](https://github.com/tobiashochguertel/hike/issues?q=is%3Aissue+is%3Aopen+label%3ATODO).

### Editing

As mentioned above, Hike has support for editing markdown documents you're
viewing from the local filesystem. While a builtin editor is provided, use
of your own choice of editor is supported. If Hike finds that `$VISUAL` or
`$EDITOR` are set in your environment then the resulting command will be
used to edit the document (with `$VISUAL` being tried first, followed by
`$EDITOR`).

## File locations

Hike stores files in a `hike` directory within both
[`$XDG_DATA_HOME` and
`$XDG_CONFIG_HOME`](https://specifications.freedesktop.org/basedir-spec/latest/).
If you wish to fully remove anything to do with Hike you will need to
remove those directories too.

Expanding for the common locations, the files normally created are:

- `./hike.config.yaml` -- A project-local configuration file, if present.
- `~/.config/hike/config.yaml` -- The default user configuration file.
- `~/.config/hike/.env` -- Optional runtime environment settings.
- `~/.local/share/hike/*.json` -- The locally-held data.

## Getting help

If you need help, or have any ideas, please feel free to [raise an
issue](https://github.com/tobiashochguertel/hike/issues).

## TODO

See [the TODO tag in
issues](https://github.com/tobiashochguertel/hike/issues?q=is%3Aissue+is%3Aopen+label%3ATODO)
to see what I'm planning.

[//]: # (README.md ends here)
