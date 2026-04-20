# Configuration: UI, Layout & Content

This page covers presentation-related settings: themes, navigation layout,
responsive behavior, front matter, and Markdown detection rules.

## Theme selection

```bash exec="on" result="ansi" width="120"
hike themes list
```

Set your preferred Textual theme in YAML:

```yaml
theme: nord
```

For one-off launches without changing the saved config:

```sh
hike open --theme nord README.md
```

## Navigation panel and command line

These settings control where the navigation panel and command line start:

```yaml
navigation_visible: true
navigation_on_right: false
command_line_on_top: false
```

If you prefer Hike to start with the navigation panel hidden:

```yaml
navigation_visible: false
```

## Sidebar sizing and responsive behavior

The navigation/sidebar width can be tuned with defaults and caps:

```yaml
sidebar_default_width_percent: 22
sidebar_min_width: 24
sidebar_max_width: 80
sidebar_max_width_percent: 45
sidebar_auto_fit: true
```

Hike can also switch to a single-pane layout on narrower terminals:

```yaml
responsive_auto_switch_narrow: true
responsive_narrow_width: 100
responsive_narrow_mode: content-only
```

Use `sidebar-only` if you want the navigation panel to take focus first on
smaller terminals.

## Front matter and quit behavior

```yaml
show_front_matter: true
allow_traditional_quit: true
```

Set `show_front_matter: false` if you never want the YAML front matter panel,
or `allow_traditional_quit: false` if you prefer Textual's default
<kbd>Ctrl</kbd>+<kbd>C</kbd> reminder/copy behavior.

## Markdown detection rules

Hike uses both filename extensions and content types to decide what counts as
Markdown:

```yaml
markdown_extensions:
  - .md
  - .markdown
  - .mkdn

markdown_content_types:
  - text/plain
  - text/markdown
  - text/x-markdown
```

These settings mainly matter when opening remote content or scanning local
directories with custom conventions.

[//]: # (configuration-ui-and-content.md ends here)
