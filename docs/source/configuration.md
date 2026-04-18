# Introduction

The way that Hike works can be configured using a configuration file. This
section will describe what can be configured and how.

!!! note

At the moment some configuration can be done via Hike's UI; other things
require that you edit the configuration file using your preferred text
editor. Hike now ships a typed CLI for this too, so the most useful starting
points are:

```sh
hike config init
hike config show --format yaml
hike bindings list
```

The active configuration file is resolved in this order:

1. A path passed with `--config` / `HIKE_CONFIG_PATH`
2. `./hike.config.yaml` in the current working directory, if it exists
3. `~/.config/hike/config.yaml`
4. Legacy config files such as `~/.config/hike/configuration.json`

If you want to use a different configuration file for a specific workflow, you
can point Hike at it with:

```sh
hike --config ~/.config/hike/work-docs.yaml open
```

## Command line location

By default Hike's command line appears at the bottom of the screen, above
the footer of the application. It can be moved to the top of the screen,
below the application header, with the `Change Command Line Location`
command ([`ChangeCommandLineLocation`](#bindable-commands), bound to
<kbd>Ctrl</kbd>+<kbd>Up</kbd> by default).

```{.textual path="docs/screenshots/basic_app.py" title="Command line on top" lines=40 columns=120 press="tab,d,ctrl+up,tab"}
```

## Front matter display

By default Hike will show an expandable display of [YAML front
matter](https://jekyllrb.com/docs/front-matter/), if it exists in the
document being viewed. If you aren't ever interested in seeing the front
matter this can be turned off with:

```json
"show_front_matter": false
```

## Keyboard bindings

Hike allows for a degree of configuration of its keyboard bindings;
providing a method for setting up replacement bindings for the commands that
appear in the [command palette](index.md#the-command-palette).

### Bindable commands

The following commands can have their keyboard bindings set:

```bash exec="on"
hike bindings list
```

### Changing a binding

If you wish to change the binding for a command, edit the configuration file
and add the binding to the `bindings` value. For example, if you wanted to
change the binding used to create a bookmark, changing it from
<kbd>ctrl</kbd>+<kbd>b</kbd> to <kbd>F6</kbd>, and you also wanted to use
<kbd>Shift</kbd>+<kbd>F6</kbd> to jump to the bookmarks, you would set
`bindings` to this:

```yaml
bindings:
  BookmarkLocation: f6
  JumpToBookmarks: shift+f6
```

You can also update a single binding from the CLI:

```sh
hike config set bindings.BookmarkLocation f6
```

The designations used for keys is based on the internal system used by
[Textual](https://textual.textualize.io); as such [its caveats about what
works where
apply](https://textual.textualize.io/FAQ/#why-do-some-key-combinations-never-make-it-to-my-app).
The main modifier keys to know are `shift`, `ctrl`, `alt`, `meta`, `super`
and `hyper`; letter keys are their own letters; shifted letter keys are
their upper-case versions; function keys are simply <kbd>f1</kbd>,
<kbd>f2</kbd>, etc; symbol keys (the likes of `#`, `@`, `*`, etc...)
generally use a name (`number_sign`, `at`, `asterisk`, etc...).

!!! tip

    If you want to test and discover all of the key names and combinations
    that will work, you may want to install
    [`textual-dev`](https://github.com/Textualize/textual-dev) and use the
    `textual keys` command.

    If you need help with keyboard bindings [please feel free to
    ask](index.md#questions-and-feedback).

## Allow for traditional quit keystroke

Because Hike is built with Textual, and some of Textual's widgets use
<kbd>ctrl</kbd>+<kbd>c</kbd> to copy text to the clipboard, in all other
situations <kbd>ctrl</kbd>+<kbd>c</kbd> will pop up a notification reminding
you what the actual binding is to quit the application.

Hike now enables the traditional quit behaviour by default, so
<kbd>ctrl</kbd>+<kbd>c</kbd> exits immediately unless a widget is handling copy
selection itself. The default configuration value is:

```yaml
allow_traditional_quit: true
```

If you would prefer Textual's default reminder/help behaviour instead, set it to
`false`:

```yaml
allow_traditional_quit: false
```

With that setting disabled, Hike falls back to Textual's normal
<kbd>ctrl</kbd>+<kbd>c</kbd> handling, including copy-friendly behaviour in
widgets that support text selection.

## Local file system start location

By default Hike's local file system browser (the tree that appears in the
navigation panel) starts from the current working directory when you launch
`hike open` without an explicit target. If you prefer that it starts somewhere
else, you can change this value in the configuration file.

```json
"local_start_location": ".",
```

For example, if you wanted it to always start in a dedicated docs directory, you
could change it to this:

```json
"local_start_location": "~/notes/docs",
```

## Startup auto-open

When Hike starts from a directory (including `hike open` with no target), it
can automatically open a preferred Markdown file and select it in the local
browser.

```json
"startup_auto_open": true,
"startup_auto_open_patterns": [
    "INDEX.md",
    "README.md",
    "getting-started*.md"
],
```

Patterns are checked in order. Plain filenames are matched against each file's
basename; patterns containing a slash are matched against the file's path
relative to the local browser root. If no configured pattern matches, Hike
falls back to the first visible Markdown file in local-browser order. Set
`"startup_auto_open": false` if you want startup to stay in the sidebar instead
of auto-opening a document.
```

## Local file browser discovery

The local browser's discovery defaults can also be configured. The following
settings control whether ignore files are used, whether dotfiles are shown,
and which extra exclude globs should always be applied:

```json
"local_use_ignore_files": true,
"local_show_hidden": false,
"local_exclude_patterns": [
    "generated/",
    "node_modules/"
],
```

## Main forge branches

When Hike looks for the README file of a repository in a git forge, by
default it first looks in the `main` branch and then as a backup in
`master`. If you wish to change this you can edit the list in the
configuration file.

For example: if you wanted to add `staging` and `production` to the list of
branches checked, you could change this:

```json
"main_branches": [
    "main",
    "master"
],
```

to be this:

```json
"main_branches": [
    "main",
    "master",
    "staging",
    "production"
],
```

## Markdown content types

When deciding what remote content is likely a Markdown document Hike
considers the following content types as good candidates:

- text/plain
- text/markdown
- text/x-markdown

If you wish to change this list you can edit this option in the
configuration file and add to the list:

```json
"markdown_content_types": [
    "text/plain",
    "text/markdown",
    "text/x-markdown"
],
```

## Markdown file extensions

By default Hike considers files with either a `.md` or a `.markdown`
extension to be Markdown files. If you wish to change that you can edit this
option in the configuration file.

For example, if you also wanted to recognise files with the `.mkdn`
extension as Markdown files, you could change this:

```json
"markdown_extensions": [
    ".md",
    ".markdown"
],
```

to be this:

```json
"markdown_extensions": [
    ".md",
    ".markdown",
    ".mkdn"
],
```

## Navigation panel

### Visibility

You can show or hide the navigation panel. This can be done in Hike with the
`Toggle Navigation` ([`ToggleNavigation`](#bindable-commands), bound to
<kbd>F2</kbd> by default) command.

!!! tip

    You can force navigation [visible](index.md#-navigation) or
    [hidden](index.md#-no-navigation) via [the command
    line](index.md#command-line-options).
    Note that this *also* configures the visibility of the navigation panel
    for future runs of Hike.

Here is Hike with the navigation panel visible:

```{.textual path="docs/screenshots/basic_app.py" title="Visible navigation panel" lines=40 columns=120 press="tab,d,ctrl+t"}
```

and with it hidden:

```{.textual path="docs/screenshots/basic_app.py" title="Hidden navigation panel" lines=40 columns=120 press="tab,d"}
```

### Location

When [visible](#visibility), the navigation panel can be located on the left
or the right of the screen; this is toggled using the `Change Navigation
Side` command ([`ChangeNavigationSide`](#bindable-commands), bound to
<kbd>Shift</kbd>+<kbd>F2</kbd> by default).

Here is Hike with the navigation panel visible on the right:

```{.textual path="docs/screenshots/basic_app.py" title="Navigation panel on the right" lines=40 columns=120 press="tab,d,ctrl+t,shift+f2"}
```

### Responsive layout and sidebar sizing

The navigation panel can also be tuned so it takes less room on wider screens
and automatically switches to a single-pane layout on narrower terminals.

```json
"sidebar_default_width_percent": 22,
"sidebar_min_width": 24,
"sidebar_max_width": 80,
"sidebar_max_width_percent": 45,
"sidebar_auto_fit": true,
"responsive_auto_switch_narrow": true,
"responsive_narrow_width": 100,
"responsive_narrow_mode": "content-only"
```

- `sidebar_default_width_percent` controls the normal split-view width.
- `sidebar_min_width` and `sidebar_max_width` clamp the sidebar when auto-fit is active.
- `sidebar_max_width_percent` prevents the sidebar from consuming too much of the
  terminal even when deep trees or long flat-list entries need more room.
- `sidebar_auto_fit` enables content-aware sizing for the active navigation pane.
- `responsive_auto_switch_narrow` enables the narrow-terminal single-pane mode.
- `responsive_narrow_width` is the width threshold where the single-pane layout kicks in.
- `responsive_narrow_mode` controls the default narrow-screen pane; valid values are
  `"content-only"` and `"sidebar-only"`.

When Hike is in single-pane mode, use `JumpToSidebarView`
([`JumpToSidebarView`](#bindable-commands), bound to <kbd>Ctrl</kbd>+<kbd>N</kbd>
by default) to switch to the active sidebar view, and `JumpToDocument`
([`JumpToDocument`](#bindable-commands), bound to <kbd>Ctrl</kbd>+<kbd>G</kbd>
by default) to return to the markdown content.

## Local browser mode

The local browser can render either as a directory tree or as a flat list of
relative paths rooted at the current local browser directory.

```json
"local_browser_view_mode": "flat-list"
```

Valid values are `"tree"` and `"flat-list"`.

Use `ToggleLocalBrowserMode`
([`ToggleLocalBrowserMode`](#bindable-commands), bound to
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>L</kbd> by default) to switch between the
two modes. When the flat list is active, selecting a directory changes the root
of the local browser to that directory.

## Obsidian vaults location

The command for quickly browsing [Obsidian](https://obsidian.md) vaults in
the local filesystem will, by default, look in `~/Library/Mobile
Documents/iCloud~md~obsidian/Documents`.

!!! note

    I use Obsidian in the Apple ecosystem and use iCloud to sync my vaults; hence this default.

If you wish to change this to a default that makes sense for you, edit this
setting in the configuration file:

```json
"obsidian_vaults": "~/Library/Mobile Documents/iCloud~md~obsidian/Documents",
```

## Theme

Hike has a number of themes available. You can select a theme using the
`Change Theme` ([`ChangeTheme`](#bindable-commands), bound to <kbd>F9</kbd>
by default) command. The available themes include:

```bash exec="on"
hike --theme=? | sed 's/^/- /'
```

!!! tip

    You can also [set the theme via the command line](index.md#-t-theme). This can
    be useful if you want to ensure that Hike runs up with a specific theme.
    Note that this *also* configures the theme for future runs of Hike.

Here's a sample of some of the themes:

```{.textual path="docs/screenshots/basic_app.py" title="textual-light" lines=40 columns=120 press="tab,d,ctrl+t,f9,t,e,x,t,u,a,l,-,l,i,g,h,t,enter"}
```

```{.textual path="docs/screenshots/basic_app.py" title="nord" lines=40 columns=120 press="tab,d,ctrl+t,f9,n,o,r,d,enter"}
```

```{.textual path="docs/screenshots/basic_app.py" title="catppuccin-latte" lines=40 columns=120 press="tab,d,ctrl+t,f9,c,a,t,p,p,u,c,c,i,n,-,l,a,t,t,e,enter"}
```

```{.textual path="docs/screenshots/basic_app.py" title="dracula" lines=40 columns=120 press="tab,d,ctrl+t,f9,d,r,a,c,u,l,a,enter"}
```

[//]: # (configuration.md ends here)
