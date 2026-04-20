"""Checks for the documentation screenshot harness and Astro docs site."""

##############################################################################
# Python imports.
import json
from pathlib import Path
from runpy import run_path

##############################################################################
# Local imports.
from hike.startup import OpenOptions

##############################################################################
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DOCS_SITE = _REPO_ROOT / "docs-site"
_DOCS_CONTENT = _DOCS_SITE / "src" / "content" / "docs"


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
def test_docs_asset_renderer_defines_expected_screenshots() -> None:
    """The Astro docs asset renderer should keep the expected screenshot set."""
    module_globals = run_path(str(_DOCS_SITE / "scripts" / "render_docs_assets.py"))
    screenshot_specs = module_globals["SCREENSHOT_SPECS"]

    assert len(screenshot_specs) == 8
    assert {spec.slug for spec in screenshot_specs} == {
        "hike-overview",
        "hike-help",
        "markdown-help",
        "command-palette",
        "commands-enter-file",
        "commands-enter-url",
        "commands-enter-directory",
        "commands-browse-file",
    }


##############################################################################
def test_docs_asset_renderer_restores_screenshot_config(tmp_path: Path) -> None:
    """Rendering docs assets should not persist config changes back to the repo."""
    module_globals = run_path(str(_DOCS_SITE / "scripts" / "render_docs_assets.py"))
    render_screenshots = module_globals["render_screenshots"]
    screenshot_config = _REPO_ROOT / "docs" / "screenshots" / "config.yaml"
    before = screenshot_config.read_bytes()

    render_screenshots(tmp_path)

    assert screenshot_config.read_bytes() == before


##############################################################################
def test_docs_site_uses_astro_starlight_and_base_path() -> None:
    """The docs site should target Astro/Starlight on the GitHub Pages subpath."""
    package = json.loads((_DOCS_SITE / "package.json").read_text(encoding="utf-8"))
    astro_config = (_DOCS_SITE / "astro.config.mjs").read_text(encoding="utf-8")

    assert package["dependencies"]["astro"].startswith("^6.1.")
    assert "@astrojs/starlight" in package["dependencies"]
    assert "base: '/hike'" in astro_config
    assert "Start Here" in astro_config
    assert "CLI Reference" in astro_config
    assert "Configuration" in astro_config


##############################################################################
def test_docs_content_no_longer_uses_mkdocs_exec_or_textual_fences() -> None:
    """The Starlight content should not depend on MkDocs-only fenced extensions."""
    for path in _DOCS_CONTENT.rglob("*.mdx"):
        contents = path.read_text(encoding="utf-8")
        assert '```bash exec="on"' not in contents, path.name
        assert "```{.textual" not in contents, path.name


##############################################################################
def test_getting_started_installs_from_fork_main() -> None:
    """The getting started guide should install the fork from main."""
    contents = (_DOCS_CONTENT / "guides" / "getting-started.mdx").read_text(
        encoding="utf-8"
    )

    assert "mise use -g python@3.13 uv@latest" in contents
    assert (
        'uv tool install --force "git+https://github.com/tobiashochguertel/hike.git@main"'
        in contents
    )


##############################################################################
def test_mkdocs_config_has_been_removed() -> None:
    """MkDocs should no longer be the source-of-truth docs site."""
    assert not (_REPO_ROOT / "mkdocs.yml").exists()
