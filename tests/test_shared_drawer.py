"""Gate: one collapsible component, shared by both applications.

The `details.tbl` rules were written in workspace.css, which apps/case never
loads. Moving them is the whole of this task, and the failure mode if they move
back is silent: the case screens keep working, they just render an unstyled
disclosure triangle and a 20px touch target. Asserting the location is cheaper
than noticing that on a phone.
"""
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
SHARED_CSS = REPO / "apps" / "shared" / "app.css"
WORKSPACE_CSS = REPO / "apps" / "workspace" / "workspace.css"
SHELL_JS = REPO / "apps" / "shared" / "shell.js"


def test_the_collapsible_lives_in_the_shared_stylesheet():
    css = SHARED_CSS.read_text()
    assert ".tbl > summary" in css
    assert "min-height: 44px" in css, "the touch target moved with the rules or was lost"
    assert ":focus-visible" in css, "the focus ring moved with the rules or was lost"


def test_the_workspace_stylesheet_no_longer_redefines_it():
    """Two definitions of one component is how they drift apart."""
    css = WORKSPACE_CSS.read_text()
    assert ".tbl > summary {" not in css
    assert "\n.tbl {" not in css
    # The genuinely workspace-specific parts stay.
    assert ".tbl-desc" in css
    assert ".col-meaning" in css


def test_both_applications_load_the_shared_stylesheet():
    for screen in sorted((REPO / "apps").glob("*/*.html")) + [REPO / "apps" / "index.html"]:
        assert "shared/app.css" in screen.read_text() or "app.css" in screen.read_text(), (
            f"{screen.relative_to(REPO)} does not load the shared stylesheet, so it "
            "cannot render the technical drawer"
        )


def test_one_helper_renders_the_drawer_for_every_screen():
    shell = SHELL_JS.read_text()
    assert "function technicalDrawer(" in shell
    assert "Technical detail" in shell


def test_the_workspace_nav_points_at_the_persona_page():
    shell = SHELL_JS.read_text()
    assert "workbench.html" not in shell
    assert '{ href: "persona.html", label: "My role" }' in shell
