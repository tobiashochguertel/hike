"""Shared local filesystem indexing for startup and sidebar views."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

##############################################################################
# Python imports.
from dataclasses import dataclass
from fnmatch import fnmatch
from os import cpu_count
from pathlib import Path
from threading import Event

##############################################################################
# Pydantic imports.
from pydantic import BaseModel, ConfigDict, Field

##############################################################################
# Local imports.
from ..compat import StrEnum
from .discovery import LocalDiscoveryOptions, should_include_path


##############################################################################
class LocalIndexStatus(StrEnum):
    """The lifecycle state of a local index snapshot."""

    LOADING = "loading"
    READY = "ready"


##############################################################################
class LocalIndexNode(BaseModel):
    """A view-neutral indexed filesystem node."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    path: Path
    relative_path: Path
    is_dir: bool
    children: tuple[LocalIndexNode, ...] = Field(default_factory=tuple)


##############################################################################
class LocalIndexSnapshot(BaseModel):
    """The indexed local filesystem snapshot for one root/options pair."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    root: Path
    status: LocalIndexStatus = LocalIndexStatus.READY
    nodes: tuple[LocalIndexNode, ...] = Field(default_factory=tuple)


##############################################################################
@dataclass(frozen=True)
class LocalIndexBuildRequest:
    """One cancellable local-index build request."""

    root: Path
    options: LocalDiscoveryOptions
    cancel_event: Event


##############################################################################
class LocalIndexService:
    """Shared local index configuration and snapshot builder."""

    def __init__(self, root: Path, options: LocalDiscoveryOptions) -> None:
        self._root = root.expanduser().resolve()
        self._options = options
        self._cancel_event = Event()

    @property
    def root(self) -> Path:
        """Return the configured root for the next snapshot build."""
        return self._root

    @property
    def options(self) -> LocalDiscoveryOptions:
        """Return the configured discovery options."""
        return self._options

    def set_root(self, root: Path) -> None:
        """Update the root used by subsequent snapshot builds."""
        self._root = root.expanduser().resolve()

    def configure(self, options: LocalDiscoveryOptions) -> None:
        """Update the discovery options used by subsequent snapshot builds."""
        self._options = options

    def begin_build(self) -> LocalIndexBuildRequest:
        """Cancel any current build and create a new cancellable build request."""
        self.cancel()
        self._cancel_event = Event()
        return LocalIndexBuildRequest(
            root=self._root,
            options=self._options,
            cancel_event=self._cancel_event,
        )

    def cancel(self) -> None:
        """Request cancellation of the current build, if any."""
        self._cancel_event.set()

    def loading_snapshot(self, root: Path | None = None) -> LocalIndexSnapshot:
        """Return the immediate loading placeholder snapshot."""
        return LocalIndexSnapshot(
            root=self._root if root is None else root,
            status=LocalIndexStatus.LOADING,
        )

    def build_snapshot(
        self,
        request: LocalIndexBuildRequest | None = None,
    ) -> LocalIndexSnapshot | None:
        """Build the current root snapshot."""
        active_request = request or LocalIndexBuildRequest(
            root=self._root,
            options=self._options,
            cancel_event=self._cancel_event,
        )
        return build_local_index_snapshot(
            active_request.root,
            active_request.options,
            cancel_event=active_request.cancel_event,
        )


##############################################################################
def _cancelled(cancel_event: Event | None) -> bool:
    """Return `True` when a local-index build has been cancelled."""
    return cancel_event is not None and cancel_event.is_set()


##############################################################################
def _safe_is_dir(path: Path) -> bool:
    """Return `True` if a path is a directory without surfacing OS errors."""
    try:
        return path.is_dir()
    except OSError:
        return False


##############################################################################
def _scan_directory(
    current: Path,
    *,
    root: Path,
    options: LocalDiscoveryOptions,
    cancel_event: Event | None = None,
) -> tuple[list[Path], list[Path]]:
    """Scan and partition one directory into visible directories and files."""
    if _cancelled(cancel_event):
        return [], []
    try:
        paths = sorted(
            current.iterdir(),
            key=lambda path: (not _safe_is_dir(path), path.name.casefold()),
        )
    except OSError:
        return [], []

    directories: list[Path] = []
    files: list[Path] = []
    for path in paths:
        if _cancelled(cancel_event):
            return [], []
        try:
            if not should_include_path(path, root=root, options=options):
                continue
        except OSError:
            continue
        if _safe_is_dir(path):
            directories.append(path)
        else:
            files.append(path)
    return directories, files


##############################################################################
def _build_directory_node(
    directory: Path,
    *,
    root: Path,
    options: LocalDiscoveryOptions,
    cancel_event: Event | None = None,
) -> LocalIndexNode | None:
    """Build one indexed directory subtree."""
    if _cancelled(cancel_event):
        return None
    directories, files = _scan_directory(
        directory,
        root=root,
        options=options,
        cancel_event=cancel_event,
    )
    if _cancelled(cancel_event):
        return None

    child_nodes: list[LocalIndexNode] = []
    for child_directory in directories:
        if _cancelled(cancel_event):
            return None
        if child_node := _build_directory_node(
            child_directory,
            root=root,
            options=options,
            cancel_event=cancel_event,
        ):
            child_nodes.append(child_node)
    for file_path in files:
        if _cancelled(cancel_event):
            return None
        child_nodes.append(
            LocalIndexNode(
                path=file_path,
                relative_path=file_path.relative_to(root),
                is_dir=False,
            )
        )

    if not child_nodes:
        return None
    return LocalIndexNode(
        path=directory,
        relative_path=directory.relative_to(root),
        is_dir=True,
        children=tuple(child_nodes),
    )


##############################################################################
def build_local_index_snapshot(
    root: Path,
    options: LocalDiscoveryOptions,
    *,
    cancel_event: Event | None = None,
) -> LocalIndexSnapshot | None:
    """Build a shared indexed snapshot for one local browser root."""
    if _cancelled(cancel_event):
        return None
    resolved_root = root.expanduser().resolve()
    if not resolved_root.is_dir():
        return LocalIndexSnapshot(root=resolved_root)

    directories, files = _scan_directory(
        resolved_root,
        root=resolved_root,
        options=options,
        cancel_event=cancel_event,
    )
    if _cancelled(cancel_event):
        return None
    directory_nodes: list[LocalIndexNode] = []

    if directories:
        max_workers = min(len(directories), max(1, cpu_count() or 1))
        executor = ThreadPoolExecutor(max_workers=max_workers)
        cancelled = False
        try:
            futures = [
                (
                    directory,
                    executor.submit(
                        _build_directory_node,
                        directory,
                        root=resolved_root,
                        options=options,
                        cancel_event=cancel_event,
                    ),
                )
                for directory in directories
            ]
            for _directory, future in futures:
                if _cancelled(cancel_event):
                    cancelled = True
                    break
                if node := future.result():
                    directory_nodes.append(node)
        finally:
            if cancelled or _cancelled(cancel_event):
                executor.shutdown(wait=False, cancel_futures=True)
            else:
                executor.shutdown(wait=True, cancel_futures=False)
        if _cancelled(cancel_event):
            return None

    file_nodes: list[LocalIndexNode] = []
    for file_path in files:
        if _cancelled(cancel_event):
            return None
        file_nodes.append(
            LocalIndexNode(
                path=file_path,
                relative_path=file_path.relative_to(resolved_root),
                is_dir=False,
            )
        )
    return LocalIndexSnapshot(
        root=resolved_root,
        nodes=tuple((*directory_nodes, *file_nodes)),
    )


##############################################################################
def iter_flat_index_nodes(snapshot: LocalIndexSnapshot) -> tuple[LocalIndexNode, ...]:
    """Project a snapshot into the flat-list ordering used by the sidebar."""

    flattened: list[LocalIndexNode] = []

    def visit(nodes: tuple[LocalIndexNode, ...]) -> None:
        deferred_children: list[tuple[LocalIndexNode, ...]] = []
        for node in nodes:
            if node.is_dir:
                flattened.append(node)
                deferred_children.append(node.children)
            else:
                flattened.append(node)
        for children in deferred_children:
            visit(children)

    visit(snapshot.nodes)
    return tuple(flattened)


##############################################################################
def children_for_path(
    snapshot: LocalIndexSnapshot,
    path: Path,
) -> tuple[LocalIndexNode, ...]:
    """Return the indexed children for a given directory path."""
    resolved = path.expanduser().resolve()
    if resolved == snapshot.root.resolve():
        return snapshot.nodes
    if (node := find_index_node(snapshot, resolved)) and node.is_dir:
        return node.children
    return ()


##############################################################################
def find_index_node(
    snapshot: LocalIndexSnapshot,
    path: Path,
) -> LocalIndexNode | None:
    """Look up one indexed node by path."""
    resolved = path.expanduser().resolve()
    stack = list(snapshot.nodes)
    while stack:
        node = stack.pop()
        if node.path.resolve() == resolved:
            return node
        stack.extend(reversed(node.children))
    return None


##############################################################################
def preferred_startup_path(
    snapshot: LocalIndexSnapshot,
    patterns: tuple[str, ...],
) -> Path | None:
    """Select the preferred startup file from an indexed snapshot."""
    first_visible: Path | None = None
    matched_patterns: dict[str, Path] = {}

    for node in iter_flat_index_nodes(snapshot):
        if node.is_dir:
            continue
        if first_visible is None:
            first_visible = node.path
        for pattern in patterns:
            if pattern not in matched_patterns and _matches_pattern(node, pattern):
                matched_patterns[pattern] = node.path
        if patterns and patterns[0] in matched_patterns:
            return matched_patterns[patterns[0]]

    for pattern in patterns:
        if pattern in matched_patterns:
            return matched_patterns[pattern]
    return first_visible


##############################################################################
def _matches_pattern(node: LocalIndexNode, pattern: str) -> bool:
    """Return `True` if a node matches a startup-selection pattern."""
    candidate = node.relative_path.as_posix()
    if "/" in pattern or "\\" in pattern:
        return fnmatch(candidate, pattern.replace("\\", "/"))
    return fnmatch(node.path.name, pattern)


### local_index.py ends here
