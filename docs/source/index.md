# Introduction

```{.textual path="docs/screenshots/basic_app.py" title="Hike" lines=40 columns=120 press="tab,d,ctrl+t"}
```

Hike is a [Markdown](https://commonmark.org/help/) browser for the terminal.
It provides the ability to browse for and view local Markdown files, as well
as Markdown files that can be downloaded from the web. It also has shortcuts
that make it easy to view Markdown files on popular
[git](https://git-scm.com/doc)
[forges](https://en.wikipedia.org/wiki/Forge_(software)) such as
[GitHub](https://github.com/), [GitLab](https://about.gitlab.com),
[Codeberg](https://codeberg.org) and [Bitbucket](https://bitbucket.org).

## Installation

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

The following installation methods have been provided by third parties.

!!! warning

    Please note that I don't maintain any of these installation
    methods and so can't vouch for them myself. I can't guarantee that they
    are up-to-date, neither can I guarantee that they install the original code.

    **Use them at your own risk**.

#### X-CMD

The application can be installed using [`x-cmd`](https://x-cmd.com):

```sh
x install hike
```

## Running Hike

Once you've installed Hike using one of the [above methods](#installation),
you can run the application using the `hike` command.

### CLI commands

Hike now exposes a structured CLI. The most useful entry points are:

```sh
hike open README.md
hike bindings list
hike themes list
hike config init
hike schema list
hike env init
```

#### `-h`, `--help`

Prints the help for the `hike` command.

```sh
hike --help
```
```bash exec="on" result="text"
hike --help
```

#### `license`

Prints a summary of Hike's license.

```sh
hike license
```

#### `open --navigation`

Starts Hike with the navigation panel visible; this overrides and modifies
the saved state of the navigation panel.

#### `open --no-navigation`

Starts Hike with the navigation panel hidden; this overrides and modifies
the saved state of the navigation panel.

#### `open -t`, `open --theme`

Sets Hike's theme; this overrides and changes any previous theme choice made
[via the user interface](configuration.md#theme).

To see a list of available themes use `?` as the theme name:

```sh
hike --theme=?
```
```bash exec="on" result="text"
hike --theme=?
```

#### `open -v`, `open --version`

Prints the version number of Hike.

```sh
hike --version
```
```bash exec="on" result="text"
hike --version
```

#### `open --config`

Use an alternate configuration file.

#### `open --root`

Sets the initial root directory for the local browser.

#### `open --ignore`

Enables ignore-file filtering in the local browser.

#### `open --no-ignore`

Disables ignore-file filtering in the local browser.

#### `open --hidden`

Shows dotfiles in the local browser.

#### `open --no-hidden`

Hides dotfiles in the local browser.

#### `open --exclude`

Adds an exclude glob for the local browser. The option can be repeated.

#### `open -c`, `open --command`

Run a command through Hike's [internal command line](commands.md) on startup.
Use this when you want startup behavior that is richer than opening a local
file, directory or URL.

```sh
hike open --command "gh davep/org-davep-2bit"
```

#### Startup targets

Use the `open` subcommand for startup targets. If the target is a file, it is
opened immediately. If it is a directory, the local browser is rooted there.
If it is a URL, it is loaded directly.

To open a file:

```sh
hike open view-this.md
```

To start in a specific directory:

```sh
hike open docs/source/
```

To open a URL directly:

```sh
hike open https://example.com/README.md
```

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
related to [Hike's command line](commands.md), here's the help when the
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
improved, do please feel free to [visit the discussion
area](https://github.com/davep/hike/discussions) and [ask your
question](https://github.com/davep/hike/discussions/categories/q-a) or
[suggest an
improvement](https://github.com/davep/hike/discussions/categories/ideas).

When doing so, please do search past discussions and also [issues current
and previous](https://github.com/davep/hike/issues) to make sure I've not
already dealt with this, or don't have your proposed change already flagged
as something to do.

[//]: # (index.md ends here)
