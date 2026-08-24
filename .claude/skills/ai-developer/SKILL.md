---
name: ai-developer
description: Use when building agents that must actually read data (ADK/Vertex Agent Engine) — covers the six grounding layers, instruction design, verification that proves grounding rather than liveness, and determinism.
---

# AI Developer — patterns from the mining-agents engagement

## The six layers of a grounded agent
All six must hold; each fails silently and the symptom of every one is a
plausible answer: (1) model resolvable from the engine's region, (2)
pinned runtime versions, (3) tools actually attached, (4) no credential in
the artifact, (5) a real runtime identity, (6) that identity holding both
job and data roles. 100 agents shipped with no tools and answered
confidently for weeks.

## Tell the agent where its data lives
No instruction named the BigQuery project, so every agent guessed —
passing the dataset as a project id, omitting mandatory project_id,
trying a project called "test". Median 7 tool calls per query fell to 2
after one preamble: project, dataset, fully-qualified form, and the
sentence "X is the dataset, never the project."

## Shared preambles must reach custom-instruction branches
`instruction = custom or composed` means agents with a custom instruction
silently skip every shared demand. AGT-19 answered a pricing scenario
with flawless maths computed entirely from the question's own numbers —
because the reconciliation demand lived only in the composed branch.
Prepend shared preambles to BOTH branches.

## Demand reconciliation, not just citation
"Cite your table" is satisfiable by citing nothing when nothing is read.
Require: reconcile every assumption supplied in the question against the
declared tables, state where they differ and which was used, and never
present a figure computed only from the question as grounded.

## Verify grounding, never liveness
"Reply with the single word: ok" proves an engine is alive; a toolless
agent passes it perfectly. Verification must send the agent's real probe
and require (a) tool calls occurred and (b) the number matches live
source, with ground truth computed by SQL at test time, never stored.

## An agent that cannot be checked is not an agent that passed
Five agents had no probe because their tables had no numeric column — so
nothing could ever verify them, and they sat inside every clean score.
Give such agents a count-only probe; treat "unverifiable" as a failure
state that must be said out loud.

## Grounding is a fact, not a probability — prove it
Determinism trial: N agents × 5 identical probes. Healthy agents match
the live answer every time by different tool paths (3–8 calls). A single
FAIL cannot distinguish a broken agent from a bad minute: retry once and
classify transient/persistent, keeping the first attempt as evidence.
