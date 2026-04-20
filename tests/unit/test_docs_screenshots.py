"""Checks for the documentation screenshot harness."""

##############################################################################
# Python imports.
import re
from pathlib import Path
from runpy import run_path

##############################################################################
# Local imports.
from hike.startup import OpenOptions

##############################################################################
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DOCS_SOURCE = _REPO_ROOT / "docs" / "source"


##############################################################################
def test_basic_app_uses_explicit_runtime_context() -> None:
    """The docs screenshot app should stay aligned with the typed open API."""
    module_globals = run_path(str(_REPO_ROOT / "docs" / "screenshots" / "basic_app.py"))
    app = module_globals["app"]
    options = app._arguments

    assert isinstance(options, OpenOptions)
    assert options.target == str((_REPO_ROOT / "README.md").resolve())
    assert options.navigation is False
    assert options.runtime_context is not None
    assert options.runtime_context.cwd == _REPO_ROOT
    assert options.runtime_context.config_path == (
        _REPO_ROOT / "docs" / "screenshots" / "config.yaml"
    )


##############################################################################
def test_all_executed_bash_blocks_render_as_ansi() -> None:
    """Executable bash blocks should opt into ANSI rendering on the docs site."""
    for path in _DOCS_SOURCE.rglob("*.md"):
        contents = path.read_text(encoding="utf-8")
        for match in re.finditer(
            r'^```bash exec="on".*$', contents, flags=re.MULTILINE
        ):
            assert 'result="ansi"' in match.group(0), (
                f'Executable bash block in {path.name} must declare result="ansi"'
            )
            if "width=" in match.group(0):
                assert re.search(r'width="\d+"', match.group(0)), (
                    f"Executable bash block in {path.name} must quote width="
                )


##############################################################################
def test_command_docs_do_not_use_alias_admonitions() -> None:
    """Alias metadata should stay inline instead of rendering weak admonitions."""
    contents = (_DOCS_SOURCE / "commands.md").read_text(encoding="utf-8")

    assert "!!! alias" not in contents
    assert "!!! aliases" not in contents


##############################################################################
def test_configuration_nav_includes_split_guides() -> None:
    """The docs nav should expose the focused configuration sub-pages."""
    mkdocs = (_REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    for entry in (
        '"Overview": configuration.md',
        '"Files, Environment & Schemas": configuration-files-and-environment.md',
        '"Keybindings": configuration-keybindings.md',
        '"File Browser & Startup": configuration-file-browser-and-startup.md',
        '"UI, Layout & Content": configuration-ui-and-content.md',
    ):
        assert entry in mkdocs


##############################################################################
def test_getting_started_installs_from_fork_main() -> None:
    """The getting started page should install the fork from main."""
    contents = (_DOCS_SOURCE / "index.md").read_text(encoding="utf-8")

    assert "mise use -g python@3.13 uv@latest" in contents
    assert (
        'uv tool install --force "git+https://github.com/tobiashochguertel/hike.git@main"'
        in contents
    )
