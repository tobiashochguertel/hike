# Configuration: Keybindings

Hike supports configurable keybindings through a combination of built-in
binding sets, custom named sets, and one-off per-command overrides.

## Available binding sets

```bash exec="on" result="ansi" width="120"
hike bindings sets
```

The built-in sets are:

- `default` — keeps the original Hike layout
- `mnemonic` — moves toward more mnemonic, non-function-key defaults

## Commands that can be rebound

```bash exec="on" result="ansi" width="120"
hike bindings list
```

## Selecting a binding set

```yaml
binding_set: default
```

or:

```yaml
binding_set: mnemonic
```

## Defining your own set

```yaml
binding_set: work
binding_sets:
  work:
    ToggleNavigation: ctrl+shift+n
    Edit: ctrl+e
    Quit: ctrl+q
```

## Per-command overrides

Per-command `bindings` overrides are applied after the selected `binding_set`,
which makes them the right place for local tweaks on top of a built-in or
custom preset.

```yaml
bindings:
  BookmarkLocation: f6
  JumpToBookmarks: shift+f6
```

You can also update a single binding from the CLI:

```sh
hike config set bindings.BookmarkLocation f6
```

## Key naming rules

Hike uses Textual's key naming model. The main modifiers to know are:

- `shift`
- `ctrl`
- `alt`
- `meta`
- `super`
- `hyper`

Letters are written as their own letters, function keys as `f1`, `f2`, and so
on, and symbols often use names such as `number_sign`, `at`, or `asterisk`.

!!! tip

    If you want to discover which key names your terminal actually sends, install
    [`textual-dev`](https://github.com/Textualize/textual-dev) and use
    `textual keys`.

[//]: # (configuration-keybindings.md ends here)
