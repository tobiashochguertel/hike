"""Tests for layout state helpers."""

##############################################################################
# Local imports.
from hike.data.config import Configuration
from hike.data.layout import (
    LayoutMode,
    LayoutPolicy,
    ResponsiveLayoutPolicy,
    SidebarSizingPolicy,
    effective_layout_state,
)


##############################################################################
def test_effective_layout_state_defaults_to_split_with_navigation() -> None:
    """Default configuration should keep the split layout visible."""
    state = effective_layout_state(Configuration(), terminal_width=160)

    assert state.mode is LayoutMode.SPLIT
    assert state.navigation_visible is True
    assert state.sidebar_visible is True
    assert state.content_visible is True
    assert state.sidebar_width == 35


##############################################################################
def test_effective_layout_state_hides_navigation_when_overridden() -> None:
    """An explicit navigation override should collapse to content-only."""
    state = effective_layout_state(
        Configuration(),
        terminal_width=160,
        navigation_override=False,
    )

    assert state.mode is LayoutMode.CONTENT_ONLY
    assert state.navigation_visible is False
    assert state.sidebar_visible is False
    assert state.content_visible is True


##############################################################################
def test_effective_layout_state_supports_mode_override() -> None:
    """An explicit mode override should win over the default split mode."""
    state = effective_layout_state(
        Configuration(),
        terminal_width=160,
        mode_override=LayoutMode.SIDEBAR_ONLY,
    )

    assert state.mode is LayoutMode.SIDEBAR_ONLY
    assert state.navigation_visible is True
    assert state.sidebar_visible is True
    assert state.content_visible is False


##############################################################################
def test_effective_layout_state_supports_responsive_policy() -> None:
    """Responsive narrow-screen policy should be calculable in pure code."""
    state = effective_layout_state(
        Configuration(),
        terminal_width=80,
        policy=LayoutPolicy(
            responsive=ResponsiveLayoutPolicy(
                auto_switch_narrow=True,
                narrow_width=100,
                narrow_mode=LayoutMode.CONTENT_ONLY,
            )
        ),
    )

    assert state.mode is LayoutMode.CONTENT_ONLY
    assert state.navigation_visible is False


##############################################################################
def test_sidebar_sizing_policy_clamps_width() -> None:
    """Sidebar width should respect the configured min/max caps."""
    policy = SidebarSizingPolicy(
        default_width_percent=30,
        min_width=20,
        max_width=40,
        auto_fit=False,
    )

    assert policy.default_width(30) == 20
    assert policy.default_width(120) == 36
    assert policy.default_width(200) == 40


##############################################################################
def test_sidebar_sizing_policy_prefers_content_width_when_auto_fit_enabled() -> None:
    """Auto-fit should size the sidebar to the active navigation content."""
    policy = SidebarSizingPolicy(
        default_width_percent=30,
        min_width=20,
        max_width=40,
        auto_fit=True,
        content_padding=4,
    )

    assert policy.preferred_width(160, content_width=12) == 20
    assert policy.preferred_width(160, content_width=26) == 30
    assert policy.preferred_width(160, content_width=80) == 40


##############################################################################
def test_sidebar_sizing_policy_avoids_small_resize_jitter() -> None:
    """Tiny width differences should keep the current sidebar size stable."""
    policy = SidebarSizingPolicy(
        min_width=20,
        max_width=60,
        auto_fit=True,
        content_padding=4,
        jitter_threshold=2,
    )

    assert policy.preferred_width(160, content_width=30, current_width=35) == 35


### test_layout.py ends here
