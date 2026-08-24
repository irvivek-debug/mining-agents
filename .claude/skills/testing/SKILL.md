---
name: testing
description: Use when writing or reviewing tests for agent/data systems — covers testing properties not literals, mutation-checking every gate, evidence-first failure records, retry classification, and denominator honesty.
---

# Testing — patterns from the mining-agents engagement

## Test the property, not the literal
A test pinning "assets has 5 rows" broke the day the table was
deliberately deepened; a test pinning "17 stockout SKUs" likewise. The
number was never the point — the first guarded faithful reporting
(assert against the live count), the second guarded a boundary (a query
using < instead of <= drops SKUs sitting exactly at their reorder point
— assert the boundary directly). Rewrite stale pins as the property they
were protecting; rename tests whose names promise counts they no longer
assert.

## Mutation-check every gate
A test that cannot fail is not a gate. For each new check, revert the fix
(or break the SQL/logic) and confirm the suite goes red, then restore.
This session's mutations caught: a merge quietly reverting to replace, a
grounding gate reverting to a liveness ping, a <= flipped to <, a retry
that stopped classifying, and a buffered write returning.

## Verify the property you claim, not a proxy
A UAT that checked whether answers *looked* right scored 98/100 against
an estate where no agent could read anything. "Verified: ok" from a
liveness ping is not grounding. Name checks by what they prove, and make
the log line say exactly that ("GROUNDED", not "verified").

## A failure without evidence is a fresh investigation
Store the reply, the tool names, tool-side error payloads, the question,
and latency with every result. The stall signature (1–3 tool calls at
70s+ vs 5–8 at ~25s healthy) was only diagnosable because evidence was
recorded.

## Retry once, classify, keep the first attempt
A single FAIL cannot distinguish broken from unlucky. Retry once:
pass → `transient` (nothing to fix); fail → `persistent` (real). Two
UAT-blocking "failures" were transient stalls; 18 genuinely toolless
agents were persistent. The classification decided the work.

## Denominators must be honest
An agent with no probe, a group erased from a file, a run that died
half-way — all produce clean scores over shrunken denominators. Every
skipped item is printed by name (`SKIP X: not registered`); "unverifiable"
is a reported state, never an absence.

## Suite hygiene
- Run the FULL suite after adding tests: a stub assigned onto a shared
  module (instead of monkeypatch) leaked into another file's tests.
- A permanently red suite hides the next real failure — fix or quarantine
  known-stale tests fast.
- Two consecutive clean passes before declaring done; one clean pass is
  exactly what a truncated run produces.
