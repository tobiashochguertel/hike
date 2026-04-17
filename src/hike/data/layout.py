"""Helpers for Hike's layout and responsive state."""

##############################################################################
# Python imports.
from dataclasses import dataclass, field
from enum import StrEnum

##############################################################################
# Local imports.
from .config import Configuration


##############################################################################
class LayoutMode(StrEnum):
    """The high-level layout modes Hike can render."""

    SPLIT = "split"
    CONTENT_ONLY = "content-only"
    SIDEBAR_ONLY = "sidebar-only"


##############################################################################
@dataclass(frozen=True, slots=True)
class SidebarSizingPolicy:
    """Policy for the navigation/sidebar width."""

    default_width_percent: int = 22
    min_width: int = 24
    max_width: int = 60
    auto_fit: bool = True
    content_padding: int = 4
    jitter_threshold: int = 2

    def default_width(self, terminal_width: int) -> int:
        """Calculate the default sidebar width for a terminal width."""
        calculated = round(terminal_width * (self.default_width_percent / 100))
        return self.clamp_width(calculated)

    def clamp_width(self, width: int) -> int:
        """Clamp a width to the configured min/max caps."""
        return max(self.min_width, min(width, self.max_width))

    def preferred_width(
        self,
        terminal_width: int,
        *,
        content_width: int | None = None,
        current_width: int | None = None,
    ) -> int:
        """Calculate the effective sidebar width for the current conditions."""
        width = self.default_width(terminal_width)
        if self.auto_fit and content_width is not None:
            width = self.clamp_width(content_width + self.content_padding)
        if (
            current_width is not None
            and abs(width - current_width) < self.jitter_threshold
        ):
            return current_width
        return width


##############################################################################
@dataclass(frozen=True, slots=True)
class ResponsiveLayoutPolicy:
    """Policy for responsive layout switching."""

    auto_switch_narrow: bool = False
    narrow_width: int = 100
    narrow_mode: LayoutMode = LayoutMode.CONTENT_ONLY


##############################################################################
@dataclass(frozen=True, slots=True)
class LayoutPolicy:
    """The effective layout policy."""

    sidebar: SidebarSizingPolicy = field(default_factory=SidebarSizingPolicy)
    responsive: ResponsiveLayoutPolicy = field(default_factory=ResponsiveLayoutPolicy)


##############################################################################
@dataclass(frozen=True, slots=True)
class LayoutState:
    """The effective layout state for a given render pass."""

    mode: LayoutMode = LayoutMode.SPLIT
    navigation_visible: bool = True
    navigation_dock_right: bool = False
    command_line_on_top: bool = False
    sidebar_visible: bool = True
    content_visible: bool = True
    sidebar_width: int = 38


##############################################################################
def effective_layout_state(
    configuration: Configuration,
    *,
    terminal_width: int,
    navigation_override: bool | None = None,
    mode_override: LayoutMode | None = None,
    sidebar_content_width: int | None = None,
    current_sidebar_width: int | None = None,
    policy: LayoutPolicy | None = None,
) -> LayoutState:
    """Build the effective layout state for the current runtime conditions."""
    policy = policy or LayoutPolicy()
    navigation_visible = (
        configuration.navigation_visible
        if navigation_override is None
        else navigation_override
    )
    if mode_override is not None:
        mode = mode_override
    else:
        mode = LayoutMode.SPLIT if navigation_visible else LayoutMode.CONTENT_ONLY
        if (
            navigation_visible
            and policy.responsive.auto_switch_narrow
            and terminal_width < policy.responsive.narrow_width
        ):
            mode = policy.responsive.narrow_mode
    if mode is LayoutMode.CONTENT_ONLY:
        navigation_visible = False
    elif mode in (LayoutMode.SPLIT, LayoutMode.SIDEBAR_ONLY):
        navigation_visible = True
    return LayoutState(
        mode=mode,
        navigation_visible=navigation_visible,
        navigation_dock_right=configuration.navigation_on_right,
        command_line_on_top=configuration.command_line_on_top,
        sidebar_visible=mode in (LayoutMode.SPLIT, LayoutMode.SIDEBAR_ONLY),
        content_visible=mode in (LayoutMode.SPLIT, LayoutMode.CONTENT_ONLY),
        sidebar_width=policy.sidebar.preferred_width(
            terminal_width,
            content_width=sidebar_content_width,
            current_width=current_sidebar_width,
        ),
    )


### layout.py ends here
