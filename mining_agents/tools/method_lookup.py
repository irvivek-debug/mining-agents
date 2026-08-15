"""Return the driver tree for a persona's governing metric.

This tool reads no site data, so it does not use the @tool decorator: that
decorator refuses an empty tables_read, correctly, because a tool that reads
BigQuery must declare what it read. This one returns METHOD, and naming a
table here would put a false entry in the provenance panel.

The SQL behind each driver is deliberately withheld. The agent asks for a
diagnostic by driver id; handing it the query text invites it to edit the
method it is supposed to be following.
"""
from __future__ import annotations

from pathlib import Path

from mining_agents.envelope import fail, ok
from mining_agents.method.pack import PackError, load_pack

PACK_DIR = Path(__file__).resolve().parents[2] / "method"

#: Only P6 has a pack. The others are sequenced in the spec, and a persona
#: without one must fail loudly rather than return an empty tree.
PACKS = {"P6": "p6-metallurgist.yaml"}


def make_method_lookup(persona: str):
    """Build a method_lookup tool bound to one persona's pack."""

    def method_lookup():
        """Return the governing metric and the ordered driver tree."""
        name = PACKS.get(persona)
        if name is None:
            return fail(
                "NO_METHOD_PACK",
                f"no method pack exists for persona {persona}",
                {"persona": persona},
                [],
            )
        try:
            pack = load_pack(PACK_DIR / name)
        except (OSError, PackError) as exc:
            return fail("NO_METHOD_PACK", str(exc), {"persona": persona}, [])
        return ok(
            {
                "metric": pack.metric,
                "root": pack.root,
                "drivers": [
                    {
                        "id": d.id,
                        "question": d.question,
                        "status": d.status,
                        "controllable": d.controllable,
                        "guard": d.guard,
                        "doc_query": d.doc_query,
                    }
                    for d in pack.drivers
                ],
            },
            [],
            0,
        )

    return method_lookup
