---
name: ux-persona
description: Use when designing persona-driven workspaces or screens for AI/agent products — covers grounding UX in real data, business-language layering over technical flows, design-language consistency, and subtle motion.
---

# UX & Persona — patterns from the mining-agents engagement

## No AI slop
Every screen must be deliberately designed and grounded in real data from
the working system — real table names, real agent outputs, real numbers.
A mockup with invented data is indistinguishable from a broken product in
an executive review.

## Personas anchor everything
Each workspace belongs to a named persona with a governing metric (e.g.
unit cost per tonne of contained metal). Screens answer that persona's
question, not the system's structure. Add a persona image — abstraction
without a face doesn't stick.

## Business language layered over technical flow
For every agent, render the decision flow in five business-readable
stages: **trigger → reads → decides → approval → lands** — and give every
stage a one-line business flavour ("reads: last night's shift telemetry,
not a stale report"). The CEO-appropriate logic lives beside, not instead
of, the technical truth.

## Design language is a contract
Once established, every increment conforms: same palette, same type
hierarchy, same spacing. Renames ("Governance & Safety" → "Logical
Architecture") keep the visual system untouched.

## Motion is seasoning
Motion must be *very* subtle: reveal, don't perform. If a reviewer
notices the animation before the content, remove it.

## Deep links or it didn't happen
Every reference to an agent carries a link to the live agent (Gemini
Enterprise deep link). A screen that names an agent the user cannot click
is documentation, not a product.
