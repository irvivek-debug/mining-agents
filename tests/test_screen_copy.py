"""Gate: every screen speaks plainly, and hides its machinery at the end.

The instruction was explicit — a functional reader gets plain language and
tables, and technical detail goes at the end behind a collapsible. Both halves
are checkable: the jargon is a fixed list, and the drawer is a fixed component.

The check is on the *visible* text of each screen — what the markup shows and
what the JS puts on the page — and it deliberately excludes two things.

The first is the technical drawer, which is where the jargon is supposed to be.
That means the ``technicalDrawer(...)`` call and the ``drawerBody()`` function
each screen writes to fill it. Excluding only the call, as an earlier draft of
this file did, was wrong in a way that mattered: every screen composes its
drawer as ``technicalDrawer(drawerBody(), hint)``, so the jargon the drawer is
built to hold lives in that function and nowhere near the call.

The second is everything that never reaches a reader — comments, and, in JS,
identifiers. ``row.p90``, ``g.traversal`` and ``catalog.by_apqc_code`` are field
names in window.MINING_DATA. A screen cannot rename them and a reader never
sees them, so the JS half of a screen is scanned through its string literals,
with ``${...}`` interpolations removed. HTML is scanned whole, because an id or
a class name there is cheap to keep plain and a title or a placeholder attribute
is read out loud by a screen reader.

Absence is only half a gate. A screen can satisfy "no jargon" by deleting the
fact, or by inventing a private synonym for it, and both are worse than the
jargon. So two further checks run alongside: the plain phrases must be the ones
apps/shared/plain.js publishes, and the drawer must still name what the body
gave up.
"""
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
APPS = REPO / "apps"
PLAIN_JS = APPS / "shared" / "plain.js"

SCREENS = {
    "apps/index.html": ["apps/landing.js"],
    "apps/case/index.html": ["apps/case/proposition.js"],
    "apps/case/scenario.html": ["apps/case/scenario.js"],
    "apps/case/value.html": ["apps/case/value.js"],
    "apps/case/solution.html": ["apps/case/solution.js"],
    "apps/case/graph.html": ["apps/case/graph.js"],
    # hitl.js is the sign-off sheet. It is raised from the agent-teams screen
    # and is never navigated to, so its copy has no screen of its own to be
    # checked on — and it was the one surface in this application still
    # explaining itself in column names.
    "apps/workspace/index.html": ["apps/workspace/cockpit.js"],
    "apps/workspace/swarm.html": ["apps/workspace/swarm.js", "apps/workspace/hitl.js"],
    # chat.js writes most of what a reader of the role page actually reads.
    "apps/workspace/persona.html": [
        "apps/workspace/persona.js",
        "apps/workspace/persona-panel.js",
        "apps/workspace/chat.js",
    ],
    "apps/workspace/handover.html": ["apps/workspace/handover.js"],
}

CASE_SCREENS = [s for s in SCREENS if not s.startswith("apps/workspace/")]

# Words a functional reader should not have to meet in body copy. Each is
# allowed inside the technical drawer, which is what the drawer is for.
JARGON = [
    "entrypoint", "HITL", "human-in-the-loop", "traversal",
    "Pattern A", "Pattern B", "value branch", "APQC", "blast radius",
    "p90", "model tier",
]

# Which jargon each screen carried, and therefore which plain phrase from
# apps/shared/plain.js has to be doing that word's job now. Keys are the JARGON
# map's own keys, so the phrases are never retyped here: a screen that invents
# its own synonym fails, and so does a screen that simply deleted the idea.
PLAIN_INSTEAD = {
    "apps/index.html": ["p90", "median"],
    "apps/case/index.html": ["hitl"],
    "apps/case/scenario.html": ["p90", "median"],
    "apps/case/value.html": ["apqc code", "value branch"],
    "apps/case/solution.html": ["swarm", "pattern a", "pattern b", "hitl"],
    "apps/case/graph.html": ["traversal", "blast radius", "node", "edge"],
    "apps/workspace/index.html": ["entrypoint", "hitl", "apqc code", "value branch"],
    # "swarm" is not on the banned list above, because swarm.html is a file
    # name and by_swarm is a field of the catalogue. What can be demanded is
    # that the screen calls the thing what the nav calls it.
    "apps/workspace/swarm.html": ["swarm", "traversal", "hitl"],
    "apps/workspace/handover.html": ["swarm"],
}

# What each drawer must still name. These are the expressions that put the fact
# on the page, not the fact itself: asserting on "D01" or on "4.6.1" would pass
# on a comment, and asserting on a rendered figure would pin a measurement this
# repository is free to regenerate.
DRAWER_KEEPS = {
    "apps/index.html": ["r.source", "b.id"],
    "apps/case/index.html": ["b.url", "quote.source_line"],
    "apps/case/scenario.html": ["r.source", "p.code"],
    "apps/case/value.html": ["b.apqc", "b.code", "info.agents"],
    "apps/case/solution.html": ["a.pattern", "a.model_tier", "a.agent_id", "s.specialists"],
    "apps/case/graph.html": ["g.sql", "g.traversal", "g.bigquery_graph"],
    "apps/workspace/index.html": ["a.persona", "a.apqc_code", "a.model_tier", "WS.approval.table"],
    "apps/workspace/swarm.html": ["coord.apqc_code", "a.model_tier", "method(current)", "swarmInputs()"],
    "apps/workspace/handover.html": ["S12.apqc_code", "a.model_tier", "a.source_tables"],
    "apps/workspace/persona.html": ["a.model_tier", "a.apqc_code", "branchesOf("],
}

# Counts belong to the catalogue, not to a heading. Spelling one out in an <h1>
# is the same defect as typing it as a digit, and harder to notice going stale.
# "one" is left out: "one point of recovery" is a unit, not a tally.
COUNT_WORDS = (
    "two three four five six seven eight nine ten eleven twelve thirteen "
    "fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty "
    "fifty sixty seventy eighty ninety hundred"
).split()


# ---------------------------------------------------------------- extraction

def _strip_js_comments(text):
    """Block comments and whole-line // comments.

    Only lines that *begin* with // are taken, so the `https://` inside a
    benchmark URL survives — it is on screen, and it should be checked.
    """
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", text)


def _strip_balanced_call(text, opener):
    """Remove every `opener…)` span, matching the parenthesis rather than guessing.

    A regex stopping at the first `)` would leave the arguments of
    `technicalDrawer(drawerBody(), hint)` behind, which is most of the point.
    """
    out = []
    i = 0
    while True:
        at = text.find(opener, i)
        if at < 0:
            out.append(text[i:])
            return "".join(out)
        out.append(text[i:at])
        depth = 0
        j = at + len(opener) - 1
        while j < len(text):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        i = j + 1


STRING_LITERAL = re.compile(
    r"'(?:[^'\\\n]|\\.)*'"
    r"|\"(?:[^\"\\\n]|\\.)*\""
    r"|`(?:[^`\\]|\\.)*`",
    re.S,
)


def _interpolations_out(chunk):
    """`${esc(row.label)}` is an identifier, not a word the reader meets."""
    previous = None
    while previous != chunk:
        previous = chunk
        chunk = re.sub(r"\$\{[^{}]*\}", " ", chunk)
    return chunk


def visible_js(text):
    text = _strip_js_comments(text)
    text = _strip_balanced_call(text, "technicalDrawer(")
    # The drawer's own contents. Every screen writes them in one top-level
    # function, which in this codebase closes on a brace in column one.
    text = re.sub(r"(?ms)^function drawerBody\b.*?^\}", " ", text)
    # Joined on a single space, not on a newline. A sentence in this codebase is
    # routinely built as `"…records. The " + "best day is the …"`, and a
    # separator that breaks lines would hide every phrase that spans a `+`.
    return " ".join(
        _interpolations_out(m.group(0)[1:-1]) for m in STRING_LITERAL.finditer(text)
    )


def visible_html(text):
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.S)
    return re.sub(r"<details[^>]*class=\"[^\"]*tbl[^\"]*\".*?</details>", " ", text, flags=re.S)


def visible_text(paths):
    """Everything the screen shows, minus what is inside a technical drawer.

    Whitespace is collapsed last, so a phrase broken across a line of markup
    reads as the one phrase it is on the page.
    """
    parts = []
    for path in paths:
        source = (REPO / path).read_text()
        parts.append(visible_html(source) if path.endswith(".html") else visible_js(source))
    return re.sub(r"\s+", " ", " ".join(parts))


def drawer_text(paths):
    """The other half: only what the drawer holds.

    Exactly the two regions visible_text() takes out — the drawerBody function
    and the technicalDrawer call — so the two halves cannot both be satisfied by
    a fact sitting in neither.
    """
    parts = []
    for path in paths:
        source = _strip_js_comments((REPO / path).read_text())
        parts.extend(re.findall(r"(?ms)^function drawerBody\b.*?^\}", source))
        rest = re.sub(r"(?ms)^function drawerBody\b.*?^\}", " ", source)
        for match in re.finditer(r"technicalDrawer\(", rest):
            depth = 0
            j = match.end() - 1
            while j < len(rest):
                if rest[j] == "(":
                    depth += 1
                elif rest[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            parts.append(rest[match.start() : j + 1])
    return "\n".join(parts)


def plain_map():
    """The JARGON map out of apps/shared/plain.js, parsed rather than retyped."""
    source = PLAIN_JS.read_text()
    block = re.search(r"var JARGON = \{(.*?)\n\};", source, re.S)
    assert block, "apps/shared/plain.js no longer declares a JARGON map"
    pairs = re.findall(r"(?m)^\s*\"?([a-z0-9 -]+?)\"?:\s*\"([^\"]+)\"", block.group(1))
    assert pairs, "the JARGON map parsed to nothing"
    return dict(pairs)


# -------------------------------------------------------------------- checks

def test_every_screen_ends_with_exactly_one_technical_drawer():
    for screen, scripts in SCREENS.items():
        sources = "\n".join((REPO / p).read_text() for p in [screen] + scripts)
        count = sources.count("technicalDrawer(")
        assert count == 1, f"{screen} has {count} technical drawers; it must have exactly one"


def test_the_drawer_is_the_last_thing_on_the_screen():
    """Concatenated with the footer, in one expression, so it cannot float up.

    Counting the drawers says nothing about where they are. The one structural
    fact worth pinning is that the drawer and the provenance footer are written
    together — a drawer emitted halfway up a screen is a screen that has put its
    machinery back in the reader's way.
    """
    for screen, scripts in SCREENS.items():
        sources = "\n".join((REPO / p).read_text() for p in [screen] + scripts)
        assert re.search(r"technicalDrawer\([^;]*provenance\(", sources, re.S), (
            f"{screen} does not render its drawer immediately before the footer"
        )


def test_no_jargon_survives_outside_the_drawer():
    problems = []
    for screen, scripts in SCREENS.items():
        text = visible_text([screen] + scripts)
        for term in JARGON:
            if re.search(rf"\b{re.escape(term)}\b", text, re.I):
                problems.append(f"{screen}: {term}")
    assert not problems, "jargon left in body copy:\n" + "\n".join(problems)


def test_the_plain_words_are_the_shared_ones():
    """Deleting an idea also removes its jargon. This is what stops that.

    The phrases are read out of apps/shared/plain.js, so a screen that reaches
    for its own wording — "agent squad", "impact trace" — fails here even though
    it passes the check above. Two vocabularies for one estate is the thing
    plain.js exists to prevent.
    """
    words = plain_map()
    problems = []
    for screen, keys in PLAIN_INSTEAD.items():
        text = visible_text([screen] + SCREENS[screen])
        for key in keys:
            assert key in words, f"plain.js has no entry for {key!r}"
            if words[key].lower() not in text.lower():
                problems.append(f"{screen}: says nothing about {key!r} ({words[key]!r})")
    assert not problems, "the plain phrase never replaced the jargon:\n" + "\n".join(problems)


def test_the_drawer_keeps_what_the_body_gave_up():
    """Nothing is dropped to make a page plain; it is moved."""
    problems = []
    for screen, keeps in DRAWER_KEEPS.items():
        held = drawer_text([screen] + SCREENS[screen])
        for expression in keeps:
            if expression not in held:
                problems.append(f"{screen}: the drawer no longer renders {expression}")
    assert not problems, "facts lost rather than demoted:\n" + "\n".join(problems)


def test_the_screen_codes_are_gone_from_headings():
    for screen, scripts in SCREENS.items():
        text = visible_text([screen] + scripts)
        assert not re.search(r"\bSC-[1-4]\b", text), f"{screen} still labels itself SC-n"


def test_no_heading_counts_the_estate_for_itself():
    """A headline that says how many of a thing there are is a hardcoded figure.

    "Two patterns, a hundred agents, fifty-two doors" was three of them in one
    line, and none came from the catalogue. Spelled out, they read as prose and
    survive a rebuild that moves the count underneath them.
    """
    problems = []
    for screen in CASE_SCREENS:
        html = visible_html((REPO / screen).read_text())
        for heading in re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html, re.S):
            words = re.findall(r"[a-z]+", heading.lower())
            for word in words:
                if word in COUNT_WORDS:
                    problems.append(f"{screen}: <h> counts the estate — {heading.strip()!r}")
                    break
            if re.search(r"\d", heading):
                problems.append(f"{screen}: <h> carries a digit — {heading.strip()!r}")
    assert not problems, "counts typed into headings:\n" + "\n".join(problems)


def nav_labels():
    """The workspace nav, read out of apps/shared/shell.js rather than retyped.

    Reading it is the point. If the nav is renamed and the screens are not, the
    parse below moves with the nav and the screens fail, which is the failure
    worth having.
    """
    source = shell_js()
    block = re.search(r"const WORK_NAV = \[(.*?)\n\];", source, re.S)
    assert block, "apps/shared/shell.js no longer declares WORK_NAV"
    pairs = re.findall(r'href:\s*"([^"]+)".*?label:\s*"([^"]+)"', block.group(1))
    assert len(pairs) >= 4, f"WORK_NAV parsed to {pairs}"
    return dict(pairs)


def shell_js():
    return (APPS / "shared" / "shell.js").read_text()


def test_a_screen_calls_itself_what_the_nav_calls_it():
    """A nav that says one thing and a heading that says another.

    The tab reads "Agent teams" and the screen it opens read "Swarm console",
    which teaches a reader that the words on these screens are arbitrary — and
    once that is learned, every other plain phrase on them is discounted too.
    The nav label has to survive the click.
    """
    problems = []
    for href, label in nav_labels().items():
        screen = f"apps/workspace/{href}"
        if screen not in SCREENS:
            continue
        text = visible_text([screen] + SCREENS[screen])
        if label.lower() not in text.lower():
            problems.append(f"{screen}: the nav calls this {label!r} and the screen does not")
    assert not problems, "the nav and the screen disagree:\n" + "\n".join(problems)


def test_the_corner_pill_names_the_two_counts_the_reader_needs():
    """52 and 100 are a distinction, not a pair of numbers.

    "52 entrypoints · 100 agents" invites the reading that there are a hundred
    things to talk to. The distinction the reader needs is that fifty-two of
    them take questions and the rest work behind those. Both figures still come
    from the catalogue: a pill that spells either one out has stopped being a
    reading of the estate and become a claim about it.
    """
    source = shell_js()
    block = re.search(r"workspace:\s*\{(.*?)\n  \},", source, re.S)
    assert block, "apps/shared/shell.js no longer declares the workspace nav"
    pill = re.search(r"pill:\s*\(\)\s*=>\s*\((.*?)\}\),", block.group(1), re.S)
    assert pill, "the workspace nav no longer builds a pill"
    text = pill.group(1)

    # The pill counts, so it says the published phrase in the plural. The
    # pattern is built from apps/shared/plain.js rather than retyped, so a pill
    # that invents its own wording still fails; only the plural 's' is forgiven.
    words = plain_map()
    head, rest = words["entrypoint"].split(" ", 1)
    phrase = re.compile(re.escape(head) + "s? " + re.escape(rest))
    said = phrase.search(text)
    assert said, f"the pill does not say {words['entrypoint']!r}; it says {text!r}"
    assert "in the teams behind them" in text, (
        "the pill counts the other agents without saying what they are"
    )
    # Order matters as much as wording: the phrase belongs to the smaller
    # figure, and swapping them says the estate has a hundred front doors.
    first = text.index("counts.entrypoints")
    second = text.index("counts.agent_nodes")
    assert first < second, "the pill puts the whole estate behind the plain phrase"
    assert first < said.start(), "the count and its phrase are the wrong way round"
    assert not re.search(r"\b(52|100)\b", text), "the pill types a count it could read"


def test_the_copy_stays_commodity_neutral():
    metals = ["copper", "gold", "nickel", "iron ore", "bauxite", "zinc", "lithium"]
    for screen, scripts in SCREENS.items():
        text = "\n".join((REPO / p).read_text() for p in [screen] + scripts)
        for metal in metals:
            assert not re.search(rf"\b{metal}\b", text, re.I), (
                f"{screen} names {metal}; the copy says 'contained metal'"
            )


def test_the_only_money_figure_is_the_one_the_repository_establishes():
    """Every other magnitude is [CLIENT INPUT REQUIRED], and ranges, not points."""
    for screen, scripts in SCREENS.items():
        text = "\n".join((REPO / p).read_text() for p in [screen] + scripts)
        for hit in re.findall(r"\$[\d,]+", text):
            assert False, f"{screen} prints the literal money figure {hit}"
