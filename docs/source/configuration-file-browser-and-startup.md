# Configuration: File Browser & Startup

This page covers how Hike chooses the initial local root, how it auto-opens
documents, and how local file discovery is filtered.

## Local browser root

When you run `hike open` without an explicit target, Hike starts from the
current working directory by default. You can change that with:

```yaml
local_start_location: ~/notes/docs
```

## Startup auto-open

When Hike starts from a directory, it can automatically open a preferred
document and select it in the local browser.

```yaml
startup_auto_open: true
startup_auto_open_patterns:
  - INDEX.md
  - README.md
  - getting-started*.md
```

Patterns are checked in order. Plain filenames are matched against each file's
basename. Patterns containing a slash are matched against the file's path
relative to the local browser root.

If you want startup to stay in the sidebar instead of opening a document:

```yaml
startup_auto_open: false
```

## Local discovery defaults

The local browser can also be tuned for hidden files, ignore-file handling, and
extra excludes:

```yaml
local_use_ignore_files: true
local_show_hidden: false
local_exclude_patterns:
  - generated/
  - node_modules/
```

At launch time, the related CLI flags are documented in the
[CLI Reference](cli.md#hike-open).

## Local browser mode

Hike can render the local browser either as the original tree or as a flat list
of relative paths:

```yaml
local_browser_view_mode: flat-list
```

or:

```yaml
local_browser_view_mode: tree
```

In flat-list mode, selecting a directory changes the local browser root. When a
parent exists, Hike also exposes `../`, and <kbd>Backspace</kbd> moves to the
parent directory directly.

## Forge fallback branches

When Hike loads a README from a forge, it checks the configured list of default
branches in order:

```yaml
main_branches:
  - main
  - master
  - staging
  - production
```

[//]: # (configuration-file-browser-and-startup.md ends here)
