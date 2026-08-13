"""Gate: the persona page exists, replaces the workbench, and claims nothing extra.

This is a static check of the page's sources, not of its rendering — the
rendering is checked in a browser at the end of the plan. What is worth pinning
here is the set of claims the markup and the panel are allowed to make, because
those are the ones that go wrong quietly: a heading that says "your machines"
when no persona-to-asset mapping exists, or a screen that outlives the workbench
it replaced.
"""
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
WORKSPACE = REPO / "apps" / "workspace"


def test_the_persona_page_and_its_two_scripts_exist():
    for name in ("persona.html", "persona.js", "persona-panel.js"):
        assert (WORKSPACE / name).is_file(), f"{name} is missing"


def test_the_workbench_is_gone_and_nothing_still_links_to_it():
    assert not (WORKSPACE / "workbench.html").exists()
    assert not (WORKSPACE / "workbench.js").exists()
    for source in sorted((REPO / "apps").rglob("*.html")) + sorted((REPO / "apps").rglob("*.js")):
        assert "workbench" not in source.read_text(), (
            f"{source.relative_to(REPO)} still refers to the workbench"
        )


def test_the_page_loads_every_module_the_panel_needs():
    html = (WORKSPACE / "persona.html").read_text()
    for script in ("../shared/shell.js", "../shared/plain.js", "persona-data.js",
                   "router.js", "persona-panel.js", "persona.js"):
        assert script in html, f"persona.html does not load {script}"
    # Order matters: these are classic scripts, and a module that calls into
    # another must be loaded after it.
    assert html.index("../shared/plain.js") < html.index("router.js")
    assert html.index("router.js") < html.index("persona-data.js")
    assert html.index("persona-data.js") < html.index("persona-panel.js")


def test_the_machines_block_does_not_claim_the_machines_are_the_readers():
    """No persona-to-asset mapping exists, so the heading says "this site"."""
    panel = (WORKSPACE / "persona-panel.js").read_text()
    assert "this site instruments" in panel
    assert "your machines" not in panel.lower()


def test_the_panel_handles_all_three_evidence_kinds():
    panel = (WORKSPACE / "persona-panel.js").read_text()
    for kind in ("series", "distribution", "share"):
        assert f'"{kind}"' in panel, (
            f"the panel does not switch on the {kind} evidence kind, so at least "
            "one persona renders nothing"
        )


def test_the_panel_renders_the_gap_caveats_verbatim():
    panel = (WORKSPACE / "persona-panel.js").read_text()
    for field in ("caveat", "excluded", "method", "caption"):
        assert field in panel, f"gap.{field} is never rendered"


def test_the_page_ends_with_one_technical_drawer():
    panel = (WORKSPACE / "persona-panel.js").read_text() + (WORKSPACE / "persona.js").read_text()
    assert panel.count("technicalDrawer(") == 1


def test_no_measurement_is_typed_into_the_page():
    """Every figure comes from the bundle. A literal here is a number nobody can check.

    The two shapes a measurement takes in this data are a decimal (92.32,
    1149.552, 8.5433) and a magnitude of four digits or more (145000, 1996,
    3340). Neither has any business in rendering code. Small integers do — SVG
    geometry, percentages, array bounds — so they are left alone.
    """
    import re

    for name in ("persona.js", "persona-panel.js"):
        source = (WORKSPACE / name).read_text()
        body = "\n".join(
            line for line in source.splitlines() if not line.strip().startswith(("*", "//", "/*"))
        )
        decimals = re.findall(r"(?<![\w.])\d+\.\d+(?![\w.])", body)
        assert decimals == [], (
            f"{name} contains the decimal literal(s) {decimals}; every measurement "
            "on this screen must come from window.MINING_DATA"
        )
        big = [n for n in re.findall(r"(?<![\w.])\d{4,}(?![\w.])", body)]
        assert big == [], (
            f"{name} contains the literal magnitude(s) {big}; every figure on this "
            "screen must come from window.MINING_DATA"
        )
