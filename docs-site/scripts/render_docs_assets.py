from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from textual._doc import take_svg_screenshot

_REPO_ROOT = Path(__file__).resolve().parents[2]
_APP_PATH = str(_REPO_ROOT / "docs" / "screenshots" / "basic_app.py")
_OUTPUT_DIR = _REPO_ROOT / "docs-site" / "src" / "assets" / "generated" / "screenshots"
_SCREENSHOT_CONFIG = _REPO_ROOT / "docs" / "screenshots" / "config.yaml"


@dataclass(frozen=True)
class ScreenshotSpec:
    slug: str
    title: str
    press: tuple[str, ...]
    columns: int
    lines: int


SCREENSHOT_SPECS: tuple[ScreenshotSpec, ...] = (
    ScreenshotSpec(
        slug="hike-overview",
        title="Hike",
        press=("tab", "d", "ctrl+t"),
        columns=120,
        lines=40,
    ),
    ScreenshotSpec(
        slug="hike-help",
        title="The Hike Help Screen",
        press=("f1",),
        columns=120,
        lines=50,
    ),
    ScreenshotSpec(
        slug="markdown-help",
        title="Markdown Document Help",
        press=("tab", "f1"),
        columns=120,
        lines=50,
    ),
    ScreenshotSpec(
        slug="command-palette",
        title="The Hike Command Palette",
        press=("ctrl+p",),
        columns=120,
        lines=50,
    ),
    ScreenshotSpec(
        slug="commands-enter-file",
        title="Entering a file's location",
        press=("~", "/", "m", "y", "a", "p", "p", "/", "R", "E", "A", "D", "M", "E", ".", "m", "d"),
        columns=80,
        lines=25,
    ),
    ScreenshotSpec(
        slug="commands-enter-url",
        title="Entering a URL to view",
        press=(
            "h",
            "t",
            "t",
            "p",
            "s",
            ":",
            "/",
            "/",
            "r",
            "a",
            "w",
            ".",
            "g",
            "i",
            "t",
            "h",
            "u",
            "b",
            "u",
            "s",
            "e",
            "r",
            "c",
            "o",
            "n",
            "t",
            "e",
            "n",
            "t",
            ".",
            "c",
            "o",
            "m",
            "/",
            "d",
            "a",
            "v",
            "e",
            "p",
            "/",
            "2",
            "b",
            "i",
            "t",
            ".",
            "e",
            "l",
            "/",
            "r",
            "e",
            "f",
            "s",
            "/",
            "h",
            "e",
            "a",
            "d",
            "s",
            "/",
            "m",
            "a",
            "i",
            "n",
            "/",
            "R",
            "E",
            "A",
            "D",
            "M",
            "E",
            ".",
            "m",
            "d",
        ),
        columns=80,
        lines=25,
    ),
    ScreenshotSpec(
        slug="commands-enter-directory",
        title="Entering a directory to browse",
        press=("~", "/", "d", "e", "v", "e", "l", "o", "p", "/", "p", "y", "t", "h", "o", "n", "/", "h", "i", "k", "e", "/", "d", "o", "c", "s", "/", "s", "o", "u", "r", "c", "e"),
        columns=80,
        lines=25,
    ),
    ScreenshotSpec(
        slug="commands-browse-file",
        title="Browsing for a file to open",
        press=("~", "/", "d", "e", "v", "e", "l", "o", "p", "/", "p", "y", "t", "h", "o", "n", "/", "h", "i", "k", "e", "/", "d", "o", "c", "s", "/", "s", "o", "u", "r", "c", "e", "enter"),
        columns=120,
        lines=40,
    ),
)


def render_screenshots(output_dir: Path = _OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    original_config = _SCREENSHOT_CONFIG.read_bytes()
    try:
        for spec in SCREENSHOT_SPECS:
            svg = take_svg_screenshot(
                app_path=_APP_PATH,
                press=spec.press,
                title=spec.title,
                terminal_size=(spec.columns, spec.lines),
            )
            (output_dir / f"{spec.slug}.svg").write_text(svg, encoding="utf-8")
    finally:
        _SCREENSHOT_CONFIG.write_bytes(original_config)


if __name__ == "__main__":
    render_screenshots()
