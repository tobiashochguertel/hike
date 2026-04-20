"""Runtime context helpers shared by CLI and TUI code."""

##############################################################################
# Python imports.
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from pathlib import Path

##############################################################################
_runtime_context: ContextVar[RuntimeContext | None] = ContextVar(
    "hike_runtime_context", default=None
)


##############################################################################
@dataclass(frozen=True)
class RuntimeContext:
    """Explicit runtime path overrides and resolution base information."""

    cwd: Path
    config_path: Path | None = None
    env_path: Path | None = None


##############################################################################
def _normalize_path(path: str | Path, *, cwd: Path) -> Path:
    """Normalise a path relative to the runtime working directory."""
    normalized = Path(path).expanduser()
    if not normalized.is_absolute():
        normalized = cwd / normalized
    return normalized


##############################################################################
def resolve_runtime_context(
    config_path: str | Path | None = None,
    env_path: str | Path | None = None,
    *,
    cwd: Path | None = None,
) -> RuntimeContext:
    """Create an explicit runtime context from CLI or test inputs."""
    resolved_cwd = (Path.cwd() if cwd is None else cwd).expanduser().resolve()
    return RuntimeContext(
        cwd=resolved_cwd,
        config_path=(
            None
            if config_path is None
            else _normalize_path(config_path, cwd=resolved_cwd)
        ),
        env_path=(
            None if env_path is None else _normalize_path(env_path, cwd=resolved_cwd)
        ),
    )


##############################################################################
def current_runtime_context() -> RuntimeContext | None:
    """Return the current runtime context, if one is active."""
    return _runtime_context.get()


##############################################################################
@contextmanager
def use_runtime_context(context: RuntimeContext | None) -> Iterator[None]:
    """Temporarily activate a runtime context for nested config lookups."""
    token: Token[RuntimeContext | None] = _runtime_context.set(context)
    try:
        yield
    finally:
        _runtime_context.reset(token)


### runtime_context.py ends here
