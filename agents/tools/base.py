"""The @tool decorator: the only place a tool envelope is constructed."""
from __future__ import annotations

import functools
import logging

from agents.envelope import fail, ok

log = logging.getLogger(__name__)


class ToolFailure(Exception):
    """An expected failure. Becomes an RFC 7807 error envelope."""

    def __init__(self, code: str, message: str, **details):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def tool(tables_read: list[str]):
    """Wrap a function returning (data, rows_scanned) into the SOP envelope.

    tables_read is declared at decoration time so that it is present even when
    the call fails before touching BigQuery.
    """
    if not tables_read:
        raise ValueError(
            "every tool must declare a non-empty tables_read; "
            "meta.tables_read feeds the UX provenance panel"
        )

    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                data, rows_scanned = fn(*args, **kwargs)
            except ToolFailure as exc:
                return fail(exc.code, exc.message, exc.details, tables_read)
            except Exception as exc:  # noqa: BLE001 - boundary: nothing escapes a tool
                log.exception("unhandled error in tool %s", fn.__name__)
                return fail("INTERNAL", str(exc), {"tool": fn.__name__}, tables_read)
            return ok(data, tables_read, rows_scanned)

        wrapper.tables_read = list(tables_read)
        return wrapper

    return decorate
