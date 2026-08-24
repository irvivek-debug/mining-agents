---
name: back-end
description: Use when writing services, tools, and data pipelines behind agent systems — covers envelope patterns, silent-empty failures, accumulate-vs-replace, centralized selection logic, and incremental durability.
---

# Back End — patterns from the mining-agents engagement

## Silent-empty is the deadliest failure shape
Four incidents shared one shape: a lookup failed and the code carried on
as though there was nothing to find — a swallowed import returning `{}`,
a 401 rendered as "0 agents", a JS error rendered as an empty reply, an
overwritten file rendered as "no work to do". Any code path where
"not found" and "nothing to do" are the same branch is where the next
one lives. Raise; never return an empty default from an error.

## Accumulating datasets merge, never replace
A probe registry rewritten wholesale per group silently erased every
other group's entries; downstream consumers skipped the missing agents
without a word. Files that record "what we know" only ever grow;
deletions are explicit, encoded decisions (a DEREGISTERED set), not
hand-edits that the next writer reverts.

## Selection logic lives in one tested function
Three hand-rolled copies of "which agents belong to group X" existed;
two were wrong (IDs are `S08-1-WATER` but also `D26` — no separator, so
naive startswith either misses a class or lets `S01` swallow `S12`).
Centralize, test the ID-shape edge cases, and make every caller import it.

## Flush results per item, not at the end
A results file written only after the whole run lost every record when
the run died mid-way — and the report kept describing a smaller, cleaner
world. Append + flush after each unit of work, after any retry/classify
step so the durable record is the final verdict.

## Tools return envelopes with provenance
Tool responses carry `success`, data, and `meta.tables_read`. Tests then
assert the envelope reports the source faithfully — against the live
source, not a pinned literal (a pinned row count of 5 went stale the day
the table was deliberately deepened to 88).

## Long-lived processes refresh their own credentials
A token fetched once at startup 401s when the run outlives it (~1h);
the failure lands on whichever items run last and reads as *their*
defect. Cache with a TTL well inside the token lifetime, and raise
loudly on an empty token ("run gcloud auth login") instead of sending
`Bearer <nothing>`.
