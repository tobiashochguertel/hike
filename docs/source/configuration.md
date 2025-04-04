# Introduction

The way that Hike works can be configured using a configuration file. This
section will describe what can be configured and how.

!!! note

    At the moment some configuration can be done via Hike's UI; other things
    require that you edit the configuration file using your preferred text
    editor. Eventually I aim to make everything that can be configured
    configurable within Hike itself.

The location of the configuration file will depend on how your system is
configured; but by default it is looked for in
[`$XDG_CONFIG_HOME`](https://specifications.freedesktop.org/basedir-spec/latest/),
in a `hike` subdirectory. Mostly this will translate to the file being
called `~/.config/hike/configuration.json`.

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
`Toggle Navigation` (`ToggleNavigation`) command (bound to <kbd>F2</kbd> by
default).

!!! tip

    You can force nagivation [visible](index.md#-navigation) or
    [hidden](index.md#-no-navigation) via [the command
    line](index.md#command-line-options).
    Note that this *also* configures the visability of the navigation panel
    for future runs of Hike.

Here is Hike with the navigation panel visible:

```{.textual path="docs/screenshots/basic_app.py" title="Hike" lines=40 columns=120 press="tab,d,ctrl+t"}
```

and with it hidden:

```{.textual path="docs/screenshots/basic_app.py" title="Hike" lines=40 columns=120 press="tab,d"}
```

### Location

When [visible](#visibility), the navigation panel can be located on the left
or the right of the screen; this is toggled using the `Change Navigation
Side` command (`ChangeNavigationSide`) which is found to
<kbd>Shift</kbd>+<kbd>F2</kbd> by default.

Here is Hike with the navigation panel visible on the right:

```{.textual path="docs/screenshots/basic_app.py" title="Hike" lines=40 columns=120 press="tab,d,ctrl+t,shift+f2"}
```

## Theme

Hike has a number of themes available. You can select a theme using the
`Change Theme` (`ChangeTheme`) command (bound to <kbd>F9</kbd> by default).
The available themes include:

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
