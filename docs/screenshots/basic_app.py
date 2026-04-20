from pathlib import Path

from hike.data.runtime_context import resolve_runtime_context
from hike.hike import Hike
from hike.startup import OpenOptions

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCREENSHOT_CONFIG = _REPO_ROOT / "docs" / "screenshots" / "config.yaml"

app = Hike(
    OpenOptions(
        target=str((_REPO_ROOT / "README.md").resolve()),
        navigation=False,
        runtime_context=resolve_runtime_context(
            cwd=_REPO_ROOT,
            config_path=_SCREENSHOT_CONFIG,
        ),
    )
)
if __name__ == "__main__":
    app.run()
