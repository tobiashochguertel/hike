# Getting Started

```{.textual path="docs/screenshots/basic_app.py" title="Hike" lines=40 columns=120 press="tab,d,ctrl+t"}
```

Hike is a [Markdown](https://commonmark.org/help/) browser for the terminal.
This repository is the Tobias Hochguertel fork of the original
[davep/hike](https://github.com/davep/hike) project, and the canonical install
target for this fork is now the `main` branch of
[`tobiashochguertel/hike`](https://github.com/tobiashochguertel/hike).

## Install this fork

### Recommended: `mise` + `uv`

Use [`mise`](https://mise.jdx.dev/) to manage Python and `uv`, then install
the CLI from this fork's `main` branch:

```sh
mise use -g python@3.13 uv@latest
uv tool install --force "git+https://github.com/tobiashochguertel/hike.git@main"
```

### Recommended: `uv`

If you already have [`uv`](https://docs.astral.sh/uv/getting-started/installation/),
install the tool directly from GitHub:

```sh
uv tool install --force "git+https://github.com/tobiashochguertel/hike.git@main"
```

### Alternatives

#### `pipx`

If you prefer [`pipx`](https://pypa.github.io/pipx/), install the fork from
GitHub instead of PyPI:

```sh
pipx install "git+https://github.com/tobiashochguertel/hike.git@main"
```

#### From a local checkout

If you want to work from source:

```sh
git clone https://github.com/tobiashochguertel/hike.git
cd hike
git switch main
uv sync --group dev
uv run hike --help
```

## First commands

Once installed, these are good starting points:

```sh
hike open
hike open README.md
hike open docs/
hike open https://example.com/README.md
hike themes list
hike bindings sets
hike config init
hike --version
```

For the full command tree, subcommands, and option reference, see
[CLI Reference](cli.md).

## What `hike open` does

`hike open` is the main entry point into the TUI. If the target is a file, it
opens immediately. If it is a directory, the local browser is rooted there and
Hike tries to auto-open a preferred document. If it is a URL, it is loaded
directly. With no target, `hike open` starts from the configured local browser
root (the current working directory by default) and uses the same auto-open
rules.

By default Hike prefers `INDEX.md`, then `README.md`, then the first visible
Markdown file in local-browser order. You can change or disable that behavior
through the configuration file.

### Responsive navigation

On narrower terminals Hike now switches to a single-pane layout automatically.
Use <kbd>Ctrl</kbd>+<kbd>N</kbd> to show the active sidebar view and
<kbd>Ctrl</kbd>+<kbd>G</kbd> to return to the markdown content. The existing
<kbd>F2</kbd> navigation toggle still works, and the sidebar will return to the
normal split layout once the terminal is wide enough again.

### Local browser modes

The local browser can now switch between a tree and a flat list of relative
paths. Use <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>L</kbd> (or `m` while the local
browser has focus) to toggle modes. The flat list uses paths relative to the
current local-browser root, selecting a directory changes that root, and empty
directories are automatically hidden in flat-list mode.

## Getting help

A great way to get to know Hike is to read the help screen. Once in the
application you can see this by pressing <kbd>F1</kbd>.

```{.textual path="docs/screenshots/basic_app.py" title="The Hike Help Screen" press="f1" lines=50 columns=120}
```

The help will adapt to which part of the screen has focus, providing extra
detail where appropriate; so while the example shown above shows the help
related to [Hike's in-app command line](commands.md), here's the help when the
markdown document has focus:

```{.textual path="docs/screenshots/basic_app.py" title="Markdown Document Help" press="tab,f1" lines=50 columns=120}
```

### The command palette

Another way of discovering commands and keys in Hike is to use the command
palette (by default you can call it with <kbd>ctrl</kbd>+<kbd>p</kbd> or
<kbd>meta</kbd>+<kbd>x</kbd>).

```{.textual path="docs/screenshots/basic_app.py" title="The Hike Command Palette" press="ctrl+p" lines=50 columns=120}
```

## Questions and feedback

If you have any questions about Hike, or you have ideas for how it might be
improved in this fork, please [open an
issue](https://github.com/tobiashochguertel/hike/issues) on GitHub.

When doing so, please do search [issues current
and previous](https://github.com/tobiashochguertel/hike/issues) to make sure
I've not
already dealt with this, or don't have your proposed change already flagged
as something to do.

[//]: # (index.md ends here)
