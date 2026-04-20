# In-App Command Line

Central to Hike's user interface is a command line; similar to a shell's
command line. It has a history (use the <kbd>up</kbd> and <kbd>down</kbd>
keys to navigate) as well as history auto-completion (use <kbd>right</kbd>
to accept a suggestion).

If you want to run one of these commands at startup, use
`hike open --command "..."`. To launch the TUI against a file, directory, or
URL, use the explicit `open` subcommand as well.

!!! tip

    Full help for all of the commands is [available inside Hike itself](index.md#getting-help) by
    pressing <kbd>F1</kbd> while the command line has focus.

## Command overview

| Command | Aliases | Area | Purpose |
| --- | --- | --- | --- |
| `bookmarks` | `b`, `bm` | Navigation | Jump to bookmarks and open the navigation panel if needed. |
| `contents` | `c`, `toc` | Navigation | Jump to the current document's table of contents. |
| `history` | `h` | Navigation | Jump to document history. |
| `local` | `l` | Navigation | Jump to the local file browser. |
| `bitbucket` | `bb` | Forges | Open Markdown from Bitbucket. |
| `codeberg` | `cb` | Forges | Open Markdown from Codeberg. |
| `github` | `gh` | Forges | Open Markdown from GitHub. |
| `gitlab` | `gl` | Forges | Open Markdown from GitLab. |
| `chdir <dir>` | `cd`, `dir`, `ls` | Local files | Change the local browser root. |
| `changelog` | `cl` | Help | Open Hike's change log. |
| `help` | `?` | Help | Open the in-app help dialog. |
| `obsidian` | `obs` | Local files | Jump to the configured Obsidian vault root. |
| `readme` | — | Help | Open Hike's README. |

## Opening content

There are three different ways to open a file for viewing, from the command
line; they are:

#### With a file name

To open a local file, type in the name (including the path to it if it's not
in the current working directory).

```{.textual path="docs/screenshots/basic_app.py" title="Entering a file's location" lines=25 columns=80 press="~,/,m,y,a,p,p,/,R,E,A,D,M,E,.,m,d"}
```

#### With a URL

To open a file that is hosted on a website, type in the URL:

```{.textual path="docs/screenshots/basic_app.py" title="Entering a URL to view" lines=25 columns=80 press="h,t,t,p,s,:,/,/,r,a,w,.,g,i,t,h,u,b,u,s,e,r,c,o,n,t,e,n,t,.,c,o,m,/,d,a,v,e,p,/,2,b,i,t,.,e,l,/,r,e,f,s,/,h,e,a,d,s,/,m,a,i,n,/,R,E,A,D,M,E,.,m,d"}
```

#### Via a file opening dialog

To open a file opening dialog at a specific directory, type in the directory
you want to start browsing at:

```{.textual path="docs/screenshots/basic_app.py" title="Entering a directory to browse" lines=25 columns=80 press="~,/,d,e,v,e,l,o,p,/,p,y,t,h,o,n,/,h,i,k,e,/,d,o,c,s,/,s,o,u,r,c,e"}
```

and after you get <kbd>Enter</kbd> the dialog will open:

```{.textual path="docs/screenshots/basic_app.py" title="Browsing for a file to open" lines=40 columns=120 press="~,/,d,e,v,e,l,o,p,/,p,y,t,h,o,n,/,h,i,k,e,/,d,o,c,s,/,s,o,u,r,c,e,enter"}
```

## Navigation panel commands

The local browser filters out ignored paths using `.gitignore` and `.ignore`
files found in the browser root and its ancestors. You can override that
behavior at startup with `--no-ignore`, `--hidden` and `--exclude`.

#### `bookmarks`

**Aliases:** `b`, `bm`

Ensures that the navigation panel is opened and then jumps to the bookmarks.

#### `contents`

**Aliases:** `c`, `toc`

Ensures that the navigation panel is opened and then jumps to the Markdown
document's table of contents.

#### `history`

**Alias:** `h`

Ensures that the navigation panel is opened and then jumps to the document
history.

#### `local`

**Alias:** `l`

Ensures that the navigation panel is opened and then jumps to the local file
system browser.

## Viewing files on forges

Hike supports quickly viewing Markdown documents hosted on popular forges, the available commands are:

| Command | Alias | Host |
| --- | --- | --- |
| `bitbucket` | `bb` | [Bitbucket](https://bitbucket.org/) |
| `codeberg` | `cb` | [Codeberg](https://codeberg.org/) |
| `github` | `gh` | [GitHub](https://github.com/) |
| `gitlab` | `gl` | [GitLab](https://gitlab.com/) |

Each command loads and views a Markdown file from the corresponding forge.

#### Specifying the file to view

When using the forge commands listed above, a number of methods of
specifying the file to view are supported:

| Format                           | Effect                                                      |
|----------------------------------|-------------------------------------------------------------|
| `<owner>/<repo>`                 | Open `README.md` from a repository                          |
| `<owner> <repo>`                 | Open `README.md` from a repository                          |
| `<owner>/<repo> <file>`          | Open a specific file from a repository                      |
| `<owner> <repo> <file>`          | Open a specific file from a repository                      |
| `<owner>/<repo>:<branch>`        | Open `README.md` from a specific branch of a repository     |
| `<owner> <repo>:<branch>`        | Open `README.md` from a specific branch of a repository     |
| `<owner>/<repo>:<branch> <file>` | Open a specific file from a specific branch of a repository |
| `<owner> <repo>:<branch> <file>` | Open a specific file from a specific branch of a repository |

So, for example, if you want to view this fork's README:

```
gh tobiashochguertel/hike
```

Or if you want to view this fork's change log:

```
gh tobiashochguertel/hike ChangeLog.md
```

If you wanted to view the README file but in a feature branch called `revamp-readme`:

```
gh tobiashochguertel/hike:revamp-readme
```

etc.

## Other commands

Other useful commands include:

#### `chdir <dir>`

**Aliases:** `cd`, `dir`, `ls`

Where `<dir>` is the path to a directory. This will change the root
directory of the tree in the local file system browser in the navigation
panel.

#### `changelog`

**Alias:** `cl`

Loads and views Hike's [ChangeLog](changelog.md).

#### `help`

**Alias:** `?`

Shows Hike's help dialog.

#### `obsidian`

**Alias:** `obs`

Changes the root directory of the tree in the local file system browser in
the navigation panel so that it points to the root directory of your
Obsidian vaults (obviously only useful if you are an
[Obsidian](https://obsidian.md/) user).

#### `readme`

Loads and views Hike's README.

[//]: # (commands.md ends here)
