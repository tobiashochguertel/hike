"""Helpers for discovering version/build metadata for the CLI."""

##############################################################################
# Python imports.
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import cache
from importlib.metadata import Distribution, PackageNotFoundError, distribution
from json import JSONDecodeError, loads
from pathlib import Path
from subprocess import CalledProcessError, check_output
from typing import Any


##############################################################################
@dataclass(frozen=True, slots=True)
class BuildInfo:
    """User-facing version and build metadata."""

    version: str
    git_sha: str | None = None
    git_branch: str | None = None
    build_timestamp: str | None = None


##############################################################################
def _package_distribution() -> Distribution | None:
    """Return the installed package distribution, if available."""
    try:
        return distribution("hike")
    except PackageNotFoundError:
        return None


##############################################################################
def _metadata_path(dist: Any, filename: str) -> Path | None:
    """Locate a metadata file within a distribution."""
    files = dist.files or ()
    for file in files:
        if Path(str(file)).name == filename:
            return Path(dist.locate_file(file))
    return None


##############################################################################
def _iso_timestamp(path: Path | None) -> str | None:
    """Return an ISO timestamp for a file's modification time."""
    if path is None or not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat()


##############################################################################
def _find_repo_root(start: Path) -> Path | None:
    """Walk upwards looking for a git repository root."""
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


##############################################################################
def _git_output(repo_root: Path, *args: str) -> str | None:
    """Return stdout from a git command, or `None` if it fails."""
    try:
        return check_output(
            ["git", *args],
            cwd=repo_root,
            text=True,
        ).strip()
    except (CalledProcessError, FileNotFoundError):
        return None


##############################################################################
def _build_info_from_distribution() -> BuildInfo | None:
    """Derive build metadata from installed package metadata."""
    if (dist := _package_distribution()) is None:
        return None

    git_sha: str | None = None
    git_branch: str | None = None
    if direct_url_text := dist.read_text("direct_url.json"):
        try:
            direct_url = loads(direct_url_text)
        except JSONDecodeError:
            direct_url = {}
        vcs_info = direct_url.get("vcs_info", {})
        git_sha = vcs_info.get("commit_id")
        git_branch = vcs_info.get("requested_revision")

    metadata_timestamp = _iso_timestamp(
        _metadata_path(dist, "direct_url.json") or _metadata_path(dist, "METADATA")
    )
    return BuildInfo(
        version=dist.version,
        git_sha=git_sha,
        git_branch=git_branch,
        build_timestamp=metadata_timestamp,
    )


##############################################################################
def _build_info_from_repo() -> BuildInfo | None:
    """Derive build metadata from the current git checkout."""
    if (dist := _package_distribution()) is None:
        return None
    if (repo_root := _find_repo_root(Path(__file__).resolve())) is None:
        return None
    return BuildInfo(
        version=dist.version,
        git_sha=_git_output(repo_root, "rev-parse", "--short=12", "HEAD"),
        git_branch=_git_output(repo_root, "rev-parse", "--abbrev-ref", "HEAD"),
        build_timestamp=_git_output(repo_root, "show", "-s", "--format=%cI", "HEAD"),
    )


##############################################################################
@cache
def build_info() -> BuildInfo:
    """Return the best available build metadata for this Hike installation."""
    installed = _build_info_from_distribution()
    repo = _build_info_from_repo()
    if repo is not None:
        return BuildInfo(
            version=repo.version,
            git_sha=repo.git_sha or (installed.git_sha if installed else None),
            git_branch=repo.git_branch or (installed.git_branch if installed else None),
            build_timestamp=repo.build_timestamp
            or (installed.build_timestamp if installed else None),
        )
    if installed is not None:
        return installed
    return BuildInfo(version="unknown")


### build_info.py ends here
