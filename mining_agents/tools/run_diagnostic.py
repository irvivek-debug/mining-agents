"""Execute a driver's fixed query, returning the diagnostic result.

`method_lookup` hands the agent its driver tree but withholds each driver's
SQL, on the reasoning that a model handed a query will paraphrase or mutate the
diagnostic.  `run_diagnostic` closes the loop: the agent names a driver by id,
the runtime resolves the SQL, runs it under the declared-table constraint, and
returns the result.  The diagnostic that ships is the diagnostic that runs, and
`method/sql/p6/*.sql` is executed in production rather than only in tests.

Why not `@tool`?  `@tool` fixes `tables_read` at decoration time, but the
tables this tool reads depend on which driver is asked for.  The alternative —
declaring all tables from all drivers at decoration — would widen access to
every query in the pack regardless of which driver the agent named, defeating
the declared-table constraint that the provenance panel relies on.  Instead,
the tables are derived from the SQL text at call time via `_TABLE_REF`, passed
to `run_query` directly, and returned in `meta.tables_read` so the panel shows
the real sources.  If `_TABLE_REF` under-extracts, the BigQuery dry run fails
loudly rather than silently widening access — BigQuery is the control.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from mining_agents.envelope import fail, ok
from mining_agents.tools.bq_query import run_query
from mining_agents.tools.method_lookup import PACK_DIR, PACKS, load_pack

# Matches `mining_data.<name>` references inside backticks, following the same
# pattern as bqml_predict._TABLE_REF.  The regex is a declaration, not a
# security control; the dry run is the control.
_TABLE_REF = re.compile(r"`?(?:[\w-]+\.)?(mining_data\.\w+)`?")

LOG = logging.getLogger(__name__)


def _referenced_tables(sql: str) -> list[str]:
    """Extract distinct mining_data table references from a SQL string."""
    return sorted(set(_TABLE_REF.findall(sql)))


def make_run_diagnostic(persona: str):
    """Build a run_diagnostic tool bound to one persona's pack."""

    def run_diagnostic(driver_id: str):
        """Execute the fixed diagnostic query for a named driver.

        Returns the result rows, the driver's status, and the guard that
        fences any recommendation.  Never returns the SQL text or file path.
        """
        name = PACKS.get(persona)
        if name is None:
            return fail(
                "NO_METHOD_PACK",
                f"no method pack exists for persona {persona!r}",
                {"persona": persona},
                [],
            )
        try:
            pack = load_pack(PACK_DIR / name)
        except Exception:  # noqa: BLE001 — must never propagate as a traceback
            return fail(
                "NO_METHOD_PACK",
                f"method pack for persona {persona!r} could not be loaded",
                {"persona": persona, "pack_file": name},
                [],
            )

        driver_by_id = {d.id: d for d in pack.drivers}
        if driver_id not in driver_by_id:
            valid = sorted(driver_by_id.keys())
            return fail(
                "NO_SUCH_DRIVER",
                f"driver {driver_id!r} does not exist; valid ids are {valid}",
                {"requested": driver_id, "valid_ids": valid},
                [],
            )

        driver = driver_by_id[driver_id]
        if not driver.sql:
            # DRIVER_NOT_INSTRUMENTED is a first-class answer: the agent can
            # report the driver exists and the data is not available, rather
            # than silence, which would imply the tree was fully explored.
            return fail(
                "DRIVER_NOT_INSTRUMENTED",
                f"driver {driver_id!r} has no diagnostic query",
                {"status": driver.status, "question": driver.question},
                [],
            )

        sql_path = PACK_DIR / driver.sql
        sql = sql_path.read_text()
        tables = _referenced_tables(sql)

        try:
            rows, scanned = run_query(sql, driver.params, tables)
        except Exception as exc:  # noqa: BLE001 — boundary with BigQuery
            # str(exc) is deliberately NOT returned. BigQuery echoes fragments
            # of the failing statement in its error text, so passing it through
            # would hand the model the SQL by the back door — the one thing
            # this tool and method_lookup exist to prevent. The type name is
            # enough for the agent to know the diagnostic did not run; the
            # detail belongs in the server log, where it is not a leak.
            LOG.exception("diagnostic %s failed for persona %s", driver_id, persona)
            return fail(
                "QUERY_FAILED",
                f"the {driver_id!r} diagnostic could not be completed",
                {"driver": driver_id, "reason": type(exc).__name__},
                tables,
            )

        return ok(
            {
                "driver": driver_id,
                "status": driver.status,
                "guard": driver.guard,
                "rows": rows,
            },
            tables,
            scanned,
        )

    return run_diagnostic
