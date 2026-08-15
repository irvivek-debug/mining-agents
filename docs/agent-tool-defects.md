# Agent tool defects observed in production

Three tool calls fail every time they are made. All three were captured from
live runs of S01 against the deployed agents on `genial-union-475913-i7`, with
the agent's own error text quoted verbatim from the technical drawer on
`persona.html`.

These are **agent-layer defects, not frontend ones**, and they are recorded
here rather than fixed alongside the workspace changes: the frontend's job is
to report a failed step in the reader's language, which it now does, and
preventing the failure is a separate workstream.

They matter more than their count suggests. S01 reported BLOCKED and rated its
own confidence low on a question it should be able to answer — "which assets
are closest to unplanned downtime right now" — because all three of its routes
to the data are broken. The agents behaved correctly; the tools did not.

## D1 — `graph_traverse` rejects the traversal the catalogue advertises

```
error.code:    INVALID_ARGUMENT
error.message: traversal 'blast_radius' requires ['asset_id']
```

The agent asks for the `blast_radius` traversal without an `asset_id` because
it does not have one yet — it is trying to discover which assets are at risk,
which is the question that would produce the ID. Under its standing directive
never to invent an asset ID, it cannot satisfy the parameter and stops.

Either the traversal needs a form that takes no seed and returns the ranked
set, or the catalogue should not offer it to an agent that has no ID in hand.

## D2 — `bqml_predict` is called with a column the model does not have

```
error.code:    QUERY_FAILED
error.message: Column lead_time_days is not found in the input data to the
               PREDICT function. at [1:15]
```

The model `downtime_regression_model` is invoked with `lead_time_days`, which
is not among its input features. This is a mismatch between the model's
training schema and what the tool passes, so it fails on every call rather
than intermittently.

## D3 — `bq_query` refuses a literal the agent has no way to parameterise

```
SQL_INTERPOLATION: literal value in a predicate; use an @parameter instead
```

The guard that blocks literal values in predicates is correct in intent — it
is what keeps a generated query from being injected into. But the agent has no
route to supply an `@parameter` binding through the tool's current interface,
so a legitimate filtered query cannot be expressed at all.

## What the reader sees while these are broken

Nothing in the list above. The activity log says *"Couldn't trace what else
stops if this stops — that lookup failed"*, the answer carries *"This part of
the answer is incomplete"*, and every string quoted on this page sits inside
the collapsed **Technical detail** drawer at the foot of the answer.

That is the intended behaviour: the gap is reported honestly, in the reader's
words, and the engineer's evidence is one click away rather than deleted.
