"""End-to-end tests for Hike running inside tmux."""

##############################################################################
# Python imports.
from __future__ import annotations

import shlex
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import uuid4

##############################################################################
# Pytest imports.
import pytest

##############################################################################
# Third-party imports.
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from libtmux import Server
from libtmux.pane import Pane

##############################################################################
# Local imports.
from hike import __version__

##############################################################################
pytestmark = [
    pytest.mark.tmux,
    pytest.mark.skipif(shutil.which("tmux") is None, reason="tmux is required"),
]

_HEADER = f"Hike v{__version__}"
_TMUX_RENDER_TIMEOUT = 6.0
_CASE_IDS = (
    "no-target",
    "dot-target",
    "changelog-file",
    "docs-directory",
    "parent-directory",
    "home-directory",
    "explicit-readme",
    "root-override",
    "config-docs-root",
    "config-readme-priority",
    "missing-file",
    "glob-expansion-error",
)


##############################################################################
@dataclass(frozen=True, slots=True)
class TmuxCapture:
    """Captured output from a tmux-driven Hike session."""

    command: str
    screen_text: str
    normal_text: str
    alternate_text: str
    used_alternate_screen: bool
    render_seconds: float


##############################################################################
@dataclass(frozen=True, slots=True)
class TmuxOpenCase:
    """One startup scenario to exercise through tmux."""

    id: str
    shell_cwd: str
    command_template: str
    expected_substrings: tuple[str, ...]
    unexpected_substrings: tuple[str, ...] = ()
    expect_tui: bool = True


##############################################################################
@dataclass(frozen=True, slots=True)
class TmuxProject:
    """Filesystem layout used by the tmux startup tests."""

    root: Path
    docs: Path
    docs_nested: Path
    home: Path
    docs_root_config: Path
    readme_first_config: Path


##############################################################################
class TmuxHarnessFactory(Protocol):
    """Callable protocol for creating fresh tmux harnesses."""

    def __call__(self, *, cwd: Path, home: Path) -> TmuxHarness:
        """Create a new harness for one tmux-backed test case."""


##############################################################################
class TmuxHarness:
    """Small helper around an isolated tmux server and a single shell pane."""

    def __init__(self, *, server: Server, pane: Pane) -> None:
        self._server = server
        self._pane = pane

    def close(self) -> None:
        """Terminate the isolated tmux server."""
        if self._server.is_alive():
            self._server.kill()

    def run(
        self,
        command: str,
        *,
        expected_substrings: tuple[str, ...],
        expect_tui: bool,
        timeout: float = _TMUX_RENDER_TIMEOUT,
    ) -> TmuxCapture:
        """Run a shell command inside tmux and wait for the expected screen."""
        started = time.monotonic()
        self._pane.send_keys(command, enter=True)

        last_normal = self._capture_normal()
        last_alternate = ""
        while True:
            alternate_on = self._display("#{alternate_on}") == "1"
            last_normal = self._capture_normal()
            last_alternate = self._capture_alternate() if alternate_on else ""
            screen_text = last_normal

            if all(expected in screen_text for expected in expected_substrings):
                return TmuxCapture(
                    command=command,
                    screen_text=screen_text,
                    normal_text=last_normal,
                    alternate_text=last_alternate,
                    used_alternate_screen=alternate_on,
                    render_seconds=time.monotonic() - started,
                )

            if time.monotonic() - started > timeout:
                raise AssertionError(
                    "Timed out waiting for tmux output.\n"
                    f"command: {command}\n"
                    f"expect_tui: {expect_tui}\n"
                    f"expected: {expected_substrings}\n"
                    f"alternate_on: {alternate_on}\n"
                    f"normal screen:\n{last_normal}\n\n"
                    f"alternate screen:\n{last_alternate}"
                )

            time.sleep(0.1)

    def _capture_normal(self) -> str:
        """Capture the current normal-screen pane contents."""
        return "\n".join(
            self._pane.capture_pane(join_wrapped=True, trim_trailing=True)
        ).strip()

    def _capture_alternate(self) -> str:
        """Capture the current alternate-screen pane contents."""
        return "\n".join(
            self._pane.cmd(
                "capture-pane",
                "-p",
                "-J",
                "-a",
                target=self._pane.pane_id,
            ).stdout
        ).strip()

    def _display(self, format_string: str) -> str:
        """Evaluate a tmux format string for the active pane."""
        stdout = self._pane.cmd(
            "display-message",
            "-p",
            format_string,
            target=self._pane.pane_id,
        ).stdout
        return stdout[0] if stdout else ""


##############################################################################
def _write_markdown(path: Path, marker: str) -> None:
    """Create a markdown file with a unique visible marker."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {marker}\n\n{marker}\n", encoding="utf-8")


##############################################################################
def _populate_large_home_tree(home: Path) -> None:
    """Create a large markdown-heavy home tree for startup regressions."""
    for workspace in range(180):
        for section in range(15):
            _write_markdown(
                home
                / f"workspace-{workspace:03d}"
                / f"section-{section:02d}"
                / "page.md",
                f"LARGE_HOME_{workspace:03d}_{section:02d}",
            )


##############################################################################
def _shell_path(root: Path, relative_path: str) -> Path:
    """Resolve a case-specific shell working directory."""
    return (root / relative_path).resolve()


##############################################################################
def _quoted(path: Path) -> str:
    """Return a shell-escaped filesystem path."""
    return shlex.quote(str(path))


##############################################################################
def _open_cases(project: TmuxProject, hike_bin: Path) -> tuple[TmuxOpenCase, ...]:
    """Build the tmux startup matrix."""
    command_prefix = _quoted(hike_bin)
    docs_root_config = _quoted(project.docs_root_config)
    readme_first_config = _quoted(project.readme_first_config)
    docs_root = _quoted(project.docs)

    return (
        TmuxOpenCase(
            id="no-target",
            shell_cwd=".",
            command_template=f"{command_prefix} open",
            expected_substrings=(_HEADER, "ROOT_INDEX_MARKER"),
            unexpected_substrings=("ROOT_README_MARKER",),
        ),
        TmuxOpenCase(
            id="dot-target",
            shell_cwd=".",
            command_template=f"{command_prefix} open .",
            expected_substrings=(_HEADER, "ROOT_INDEX_MARKER"),
            unexpected_substrings=("ROOT_README_MARKER",),
        ),
        TmuxOpenCase(
            id="changelog-file",
            shell_cwd=".",
            command_template=f"{command_prefix} open CHANGELOG.md",
            expected_substrings=(_HEADER, "CHANGELOG_MARKER"),
        ),
        TmuxOpenCase(
            id="docs-directory",
            shell_cwd=".",
            command_template=f"{command_prefix} open ./docs",
            expected_substrings=(_HEADER, "DOCS_INDEX_MARKER"),
        ),
        TmuxOpenCase(
            id="parent-directory",
            shell_cwd="docs/nested",
            command_template=f"{command_prefix} open ../",
            expected_substrings=(_HEADER, "DOCS_INDEX_MARKER"),
        ),
        TmuxOpenCase(
            id="home-directory",
            shell_cwd=".",
            command_template=f"{command_prefix} open ~",
            expected_substrings=(_HEADER, "HOME_README_MARKER"),
        ),
        TmuxOpenCase(
            id="explicit-readme",
            shell_cwd=".",
            command_template=f"{command_prefix} open README.md",
            expected_substrings=(_HEADER, "ROOT_README_MARKER"),
            unexpected_substrings=("ROOT_INDEX_MARKER",),
        ),
        TmuxOpenCase(
            id="root-override",
            shell_cwd=".",
            command_template=f"{command_prefix} open --root {docs_root}",
            expected_substrings=(_HEADER, "DOCS_INDEX_MARKER"),
        ),
        TmuxOpenCase(
            id="config-docs-root",
            shell_cwd=".",
            command_template=f"{command_prefix} --config {docs_root_config} open",
            expected_substrings=(_HEADER, "DOCS_INDEX_MARKER"),
        ),
        TmuxOpenCase(
            id="config-readme-priority",
            shell_cwd=".",
            command_template=f"{command_prefix} --config {readme_first_config} open .",
            expected_substrings=(_HEADER, "ROOT_README_MARKER"),
            unexpected_substrings=("ROOT_INDEX_MARKER",),
        ),
        TmuxOpenCase(
            id="missing-file",
            shell_cwd=".",
            command_template=f"{command_prefix} open not-existing-file.md",
            expected_substrings=(_HEADER, "Could not locate"),
        ),
        TmuxOpenCase(
            id="glob-expansion-error",
            shell_cwd=".",
            command_template=f"{command_prefix} open *.md",
            expected_substrings=("Got unexpected extra argument", "Usage: hike open"),
            unexpected_substrings=(_HEADER,),
            expect_tui=False,
        ),
    )


##############################################################################
def _assert_real_capture(case: TmuxOpenCase, capture: TmuxCapture) -> None:
    """Assert that the captured output matches the expected execution mode."""
    assert capture.screen_text.strip()
    assert capture.used_alternate_screen is case.expect_tui
    if case.expect_tui:
        assert _HEADER in capture.screen_text

    for unexpected in case.unexpected_substrings:
        assert unexpected not in capture.screen_text


##############################################################################
@pytest.fixture
def hike_bin() -> Path:
    """Return the current virtualenv's `hike` entrypoint."""
    repo_root = Path(__file__).resolve().parents[2]
    local_hike = repo_root / ".venv" / "bin" / "hike"
    if local_hike.is_file():
        return local_hike
    installed_hike = shutil.which("hike")
    assert installed_hike is not None
    return Path(installed_hike).resolve()


##############################################################################
@pytest.fixture
def tmux_project(tmp_path: Path) -> TmuxProject:
    """Create an isolated project tree for tmux-based startup tests."""
    root = tmp_path / "project"
    docs = root / "docs"
    docs_nested = docs / "nested"
    home = tmp_path / "home"
    configs = tmp_path / "configs"

    _write_markdown(root / "INDEX.md", "ROOT_INDEX_MARKER")
    _write_markdown(root / "README.md", "ROOT_README_MARKER")
    _write_markdown(root / "CHANGELOG.md", "CHANGELOG_MARKER")
    _write_markdown(docs / "INDEX.md", "DOCS_INDEX_MARKER")
    _write_markdown(docs / "README.md", "DOCS_README_MARKER")
    _write_markdown(home / "README.md", "HOME_README_MARKER")
    docs_nested.mkdir(parents=True, exist_ok=True)
    configs.mkdir(parents=True, exist_ok=True)

    docs_root_config = configs / "docs-root.yaml"
    docs_root_config.write_text("local_start_location: docs\n", encoding="utf-8")

    readme_first_config = configs / "readme-first.yaml"
    readme_first_config.write_text(
        "startup_auto_open_patterns:\n  - README.md\n  - INDEX.md\n",
        encoding="utf-8",
    )

    return TmuxProject(
        root=root,
        docs=docs,
        docs_nested=docs_nested,
        home=home,
        docs_root_config=docs_root_config,
        readme_first_config=readme_first_config,
    )


##############################################################################
@pytest.fixture
def tmux_harness_factory() -> TmuxHarnessFactory:
    """Create isolated tmux harness instances backed by unique sockets."""

    def _create(*, cwd: Path, home: Path) -> TmuxHarness:
        socket_name = f"hike-e2e-{uuid4().hex}"
        server = Server(socket_name=socket_name)
        session = server.new_session(
            session_name=f"hike-session-{uuid4().hex}",
            kill_session=True,
            attach=False,
            start_directory=str(cwd),
            window_command="/bin/sh",
            x=120,
            y=40,
            environment={
                "HOME": str(home),
            },
        )
        pane = session.windows[0].active_pane
        assert pane is not None
        pane.send_keys("clear", enter=True)
        return TmuxHarness(server=server, pane=pane)

    return _create


##############################################################################
@pytest.mark.parametrize("case_id", _CASE_IDS, ids=_CASE_IDS)
def test_tmux_open_startup_matrix(
    case_id: str,
    tmux_project: TmuxProject,
    hike_bin: Path,
    tmux_harness_factory: TmuxHarnessFactory,
) -> None:
    """Fresh tmux sessions should render real output for startup variants."""
    case = next(
        case for case in _open_cases(tmux_project, hike_bin) if case.id == case_id
    )
    harness = tmux_harness_factory(
        cwd=_shell_path(tmux_project.root, case.shell_cwd),
        home=tmux_project.home,
    )

    try:
        capture = harness.run(
            case.command_template,
            expected_substrings=case.expected_substrings,
            expect_tui=case.expect_tui,
        )
    finally:
        harness.close()

    _assert_real_capture(case, capture)


##############################################################################
@settings(
    max_examples=4,
    deadline=None,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow,
    ],
    derandomize=True,
)
@given(
    stem=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz",
        min_size=3,
        max_size=10,
    ).filter(lambda value: value not in {"index", "readme", "changelog"}),
)
def test_tmux_open_generated_markdown_file_renders_content(
    stem: str,
    tmux_project: TmuxProject,
    hike_bin: Path,
    tmux_harness_factory: TmuxHarnessFactory,
) -> None:
    """Generated markdown filenames should still render inside tmux."""
    marker = f"HYPOTHESIS_{stem.upper()}_MARKER"
    relative_name = f"{stem}.md"
    _write_markdown(tmux_project.root / relative_name, marker)

    harness = tmux_harness_factory(cwd=tmux_project.root, home=tmux_project.home)
    try:
        capture = harness.run(
            f"{_quoted(hike_bin)} open {shlex.quote(relative_name)}",
            expected_substrings=(_HEADER, marker),
            expect_tui=True,
        )
    finally:
        harness.close()

    assert capture.used_alternate_screen is True
    assert marker in capture.screen_text


##############################################################################
def test_tmux_large_home_flat_list_renders_before_recursive_scan_finishes(
    tmp_path: Path,
    hike_bin: Path,
    tmux_harness_factory: TmuxHarnessFactory,
) -> None:
    """Large `~` roots in flat-list mode should no longer blank the first frame."""
    home = tmp_path / "large-home"
    _populate_large_home_tree(home)
    config_path = tmp_path / "large-home-flat.yaml"
    config_path.write_text(
        "local_start_location: '~'\n"
        "local_browser_view_mode: flat-list\n"
        "startup_auto_open: false\n",
        encoding="utf-8",
    )

    harness = tmux_harness_factory(cwd=tmp_path, home=home)
    try:
        capture = harness.run(
            f"{_quoted(hike_bin)} --config {_quoted(config_path)} open",
            expected_substrings=(_HEADER,),
            expect_tui=True,
            timeout=4.0,
        )
    finally:
        harness.close()

    assert capture.used_alternate_screen is True
    assert (
        "Loading local files..." in capture.screen_text
        or "workspace-000/" in capture.screen_text
        or "Enter a directory, file, path or command" in capture.screen_text
    )


### test_tmux_e2e.py ends here
