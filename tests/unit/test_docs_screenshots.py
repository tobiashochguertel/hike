"""Checks for the documentation screenshot harness."""

##############################################################################
# Python imports.
from pathlib import Path
from runpy import run_path

##############################################################################
# Local imports.
from hike.startup import OpenOptions

##############################################################################
_REPO_ROOT = Path(__file__).resolve().parents[2]


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
