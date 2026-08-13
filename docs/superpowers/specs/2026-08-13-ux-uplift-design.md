# UX uplift — design

**Date:** 2026-08-13
**Scope:** two screens — `apps/index.html` (the chooser) and `apps/case/value.html`
(value unlock). If they land, the same language rolls across the other nine.

## The complaint and its cause

The screens were called "super static and boring". That is two faults, and the
second causes the first.

**Nothing moves and nothing responds.** Six of eleven screens carry zero event
listeners. Every element paints at once on load. Cards do not react to a cursor.
One accent colour does all the work, so a page of six branches looks like a page
of one thing repeated six times.

**Nothing is shown.** The repository holds 25,946 telemetry readings, 1,000
block-model cells, 3,340 fatigue readings and 500 work orders, and not one of
them reaches a screen. The value screen's only chart renders *agent counts* as
2px hairlines. A screen whose most interesting figure is "how many agents are in
this branch" will feel inert no matter what it is styled like, because the reader
is being shown an org chart when they came for a mine.

The fix is therefore substantive first and cosmetic second: put the real signal
on the screen, then let motion serve it.

## Principles

**Google and Apple design language, reconciled with the existing system.**
The system is matte, 1px-bordered, zero-radius, no drop shadows, and that stays.
What is added is what Material 3 and Apple actually contribute in a dark theme:

- **Radius scale.** `--r-sm 8px / --r-md 12px / --r-lg 20px`. Cards and surfaces
  soften; tables, consoles and the graph canvas stay square, because a square
  edge is what reads as "this is data, not chrome".
- **Tonal elevation, not shadow.** A raised surface is a lighter tone
  (`--surface` → `--surface-high`) plus a brighter border. No gloss, no gradient,
  no shadow. This is Material 3's dark-theme rule and it happens to be the rule
  the existing system already follows.
- **Emphasized easing.** `--ease-emph: cubic-bezier(0.2, 0, 0, 1)` for entrances
  and `--ease-std: cubic-bezier(0.4, 0, 0.2, 1)` for state changes; durations
  `--dur-1 180ms`, `--dur-2 320ms`, `--dur-3 560ms`. One curve family everywhere.
- **Motion is functional only.** Things enter in the reading order. Numbers count
  up so the eye lands on the figure changing. Bars grow from zero so the
  comparison is drawn rather than asserted. Nothing loops, nothing decorates,
  nothing moves that is not carrying meaning.
- **Six branch hues.** Six branches get six hues, so the value screen reads as a
  partition at a glance instead of a list. Hues are desaturated to sit on the
  matte background and each is used for exactly one branch on every surface it
  appears — bar, card edge, sparkline, legend.

**Every figure remains sourced.** No new number appears that is not counted from
`data/generated/*.parquet` or `mining_agents.catalog.definitions`. Unknown
magnitudes stay `[CLIENT INPUT REQUIRED]`. A sparkline appears only where a real
series exists; where the evidence is a proportion or a distribution it is drawn
as a proportion or a distribution and labelled as such. Inventing a trend line
for a figure that has no time axis would be exactly the failure this project
keeps refusing.

**Accessibility.** Every motion rule is wrapped in
`@media (prefers-reduced-motion: no-preference)`; the reduced-motion path is the
final state painted immediately, never a degraded one. Hue is never the only
carrier of meaning — every coloured element also carries its code as text.

## MECE: what the value screen actually argues

This is the centrepiece and the reason the screen exists.

**The value tree is a strict partition.** Six branches hold 13, 6, 7, 6, 10 and 9
entrypoints = 51. S12, the convergence agent, holds the 52nd. Every entrypoint
lands in exactly one place; nothing is counted twice and nothing is left over.
`build_value_tree` already refuses to emit a tree that does not reconcile, so the
claim is enforced by the build rather than asserted by the copy.

**The APQC view is deliberately not exclusive.** Seven entrypoints carry a
compound code spanning two processes and are counted under both, so that table
sums *above* 52 on purpose.

Showing both, and naming which is which, is the argument. The screen therefore
gets a single **52-cell partition strip** as its hero: 52 cells, six colours plus
the convergence cell, filling left to right as the counts count up, with a
running total that lands on exactly 52. Underneath, the APQC table carries an
explicit "overlapping by design — sums to N, not 52" caption. A reader who sees
one exhaustive view and one overlapping view, each labelled, learns more than a
reader shown one tidy chart.

## UX flow

The chooser is the fork; each application owns its own path. The uplift makes the
path visible rather than adding to it.

- **Landing** — hero, then the site as it was actually recorded, then the two
  applications. A reader learns there is a real mine behind this before they are
  asked which door to take.
- **Case** — proposition → the mine today → **value unlock** → the solution →
  the graph. Value is screen 3, the pivot: everything before it is context and
  everything after is mechanism. The value screen's own order is therefore
  *partition first* (what the 52 are), *branch by branch* second (what each one
  does and what evidence exists for it), *process view* third (how it maps to the
  framework the client already runs).
- Each screen keeps its existing Back / Next pair. No new navigation.

## What gets built

### 1. Signal export — `scripts/build_app_data.py` → `signals.json`

New payload in the bundle. Nothing else in the export changes.

```
signals = {
  generated_at, source, window: {from, to, buckets},
  assets: [                      # the landing strip, five assets
    {asset_id, metric, unit, points: [...], min, max, readings, source}
  ],
  branch_evidence: {             # one entry per CEO_TREE branch code
    B1: {kind: "series",       label, unit, points, min, max, caption, source},
    B2: {kind: "distribution", label, unit, bins, edges, n,   caption, source},
    B3: {kind: "series",       ...},
    B4: {kind: "series",       ...},
    B5: {kind: "share",        label, part, whole,             caption, source},
    B6: {kind: "series",       ...}
  }
}
```

Series are downsampled by equal-width time bucketing with a mean per bucket —
stated in `caption` so nobody reads a 48-point line as 48 readings. Assignments:

| Branch | Evidence | Source |
|---|---|---|
| B1 Asset availability | MILL-01 `power_draw_mw`, series | `telemetry_stream.parquet` |
| B2 Ore realisation | `gold_grade_gpt_est` distribution over 1,000 blocks | `geological_block_models.parquet` |
| B3 Processing recovery | `recovery_rate_pct`, daily series | `metallurgical_recovery.parquet` |
| B4 Haulage | TRUCK-08 `payload_tons`, series | `telemetry_stream.parquet` |
| B5 Materials | 17 of 105 SKUs at or below reorder point, share | `inventory_levels.parquet` |
| B6 Safety | fatigue alerts per bucket, series | `fatigue_logs_node.parquet` |

B2 and B5 get a distribution and a share rather than a line because neither has a
time axis. That asymmetry is the honest shape of the data and is left visible.

### 2. Tokens — `docs/ux/tokens.css`

Radius, easing and duration tokens; six branch hues; `.card` gains radius and a
hover lift (tone + border, no shadow); a `.reveal` / `.reveal.in` pair for
scroll entrances; `.bar` grows from 2px hairline to a 24px track with a rounded
fill; `.metric` gains `font-variant-numeric: tabular-nums` so a counting number
does not jitter.

### 3. Motion helpers — `apps/shared/motion.js`

Three functions, shared by both screens and reusable by the other nine later:

- `reveal(root)` — IntersectionObserver adding `.in` to `.reveal` elements in
  document order with a small stagger.
- `countUp(node, to, opts)` — animates a number to its final value.
- `sparkline(values, opts)` — returns inline SVG for a series, with an
  optional draw-in animation.

All timing uses `setInterval`, not `requestAnimationFrame`: rAF does not fire in
the verification browser (`document.visibilityState === "hidden"`), so an
rAF-based animation is one that cannot be checked before it ships.

### 4. Landing — `apps/index.html` + `apps/landing.js`

Hero; a **recorded-window strip** showing the five assets with their real series
and a playhead that sweeps the 2026-01-01 → 2026-06-16 window on an interval,
updating each asset's value to its real reading at that point. It is labelled
"recorded window · replaying" — a scrubber over history, never presented as live.
Then the two application cards, which lift on hover and count their figures up.

### 5. Value — `apps/case/value.html` + `apps/case/value.js`

The 52-cell partition strip as hero, with the running total counting to 52 and
the convergence cell called out. Six branch cards in six hues, each carrying its
mechanism, its magnitude (`$145,000/hr` for B1, `[CLIENT INPUT REQUIRED]` for the
rest, unchanged) and its evidence chart with the source underneath. The APQC
table gains its "overlapping by design" caption and a hue-matched code column.

## Verification

Both screens loaded in the browser at 360 / 414 / 768 / 1024 / 1440, asserting no
container overflow, no console errors, and that every animated value reaches its
final state. `prefers-reduced-motion: reduce` checked separately. Screenshots at
1440 and 414. The build re-run and the bundle regenerated before any of it.

## Out of scope

Rolling the language across the other nine screens; any change to the workspace
application; any new data generation; any change to the catalog or the value
tree's membership.
