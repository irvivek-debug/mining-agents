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

---

# Revision — messaging and positioning

**Date:** 2026-08-13, after review of the two built screens.

The build landed but the copy argues like an architect. "100 agent nodes", "52
callable entrypoints", "APQC 11.0.3", "3 property graphs" prove the estate
exists; none of them say why it is worth owning. The reader is a mining CEO, and
they are being handed the evidence that convinced the engineer.

## The thesis

**Best practice. Every shift.**

Not "the best performing worker". A worker is a headcount claim, and a headcount
claim in mining is a union and political conversation that this screen cannot
win and does not need to have. Best practice is a *standard*, and unlike a worker
it has a number attached in the client's own data.

The mechanism line is **optimal decisions, 24/7**: the same standard applied at
3am, across a handover, and on the days the best people are not on site.

## Why the thesis is defensible rather than a slogan

The gap between this site's p90 day and its median day, measured over the 167
days the warehouse actually covers, sits inside the range the published research
gives as the available prize:

| Quantity | p90 day vs median day, this site | Published |
|---|---|---|
| Metallurgical recovery | +1.96 pp (92.32 → 94.28 %) | +1–3 pp |
| Crusher feed rate | +8.5 % | throughput +4–8 % |
| Truck payload | +9.1 % | AHS productivity +20 % (WA) |
| Conveyor load | +10.7 % | — |

So the argument runs: the best day is not a capability that has to be bought. It
is already on record, achieved by this site, with this plant and these people.
What is missing is repetition. That reframes the sale from *buy a new capability*
to *stop losing the one you already have*, which is a materially easier thing for
a CEO to believe and a materially harder thing for a competitor to dispute.

**The honesty constraint.** Not all of the gap is capturable — some of it is ore
variability, weather and scheduled work. The screen therefore presents the gap as
the size of the opportunity space, never as a promised recovery, and says so in
the copy. PUMP-104A is excluded from the gap table: its +45 % is a bearing
degrading, not a good day, and it belongs to the downtime story instead.

## External benchmarks

Every external figure carries its publication title, publisher and year on
screen, and lives in a reviewable source file rather than in prose, so a claim
can be traced to a document without reading the markup. Verified figures only:
anything that could not be confirmed against a primary source is recorded in the
source file as excluded, with the reason, so nobody re-adds it later.

Rendered so that external evidence is visibly distinct from the client's own
data. A benchmark is a third party's claim about the industry; a measurement is
this warehouse's claim about this site. Merging the two visually would let a
reader carry McKinsey's authority onto our number, which is the exact move that
makes a CEO stop trusting a deck.

## Progressive disclosure of technical detail

Technical specificity ramps across the five case screens rather than appearing at
full strength on screen 1:

| Screen | Carries | Does not carry |
|---|---|---|
| 1 Proposition | the thesis, the industry condition | any implementation noun |
| 2 The mine today | the measured gap, benchmarks | architecture |
| 3 Value unlock | six value pools, MECE, RoI | entrypoint counts above the fold |
| 4 The solution | swarms, human-in-the-loop, orchestration | SQL |
| 5 The graph | the property graph, the traversals, the SQL | — |

MECE survives the reframe unchanged, because MECE is the consultancy's own house
method rather than a technical artifact — a CEO reads a strict partition as
rigour. What changes is what the partition is *of*: value pools first, with the
entrypoint counts demoted to a supporting figure inside each pool.

## Screen changes

**Landing.** Hero carries the thesis. The three-fact list per door drops
`agent nodes`, `property graphs` and `callable entrypoints` in favour of value
language. The five-machine strip stays — it is the proof that a real plant is
being read — recaptioned as evidence rather than as a feature.

**Value.** Leads with the gap: the site's own number beside the published number.
Each of the six branches is recast as a value pool carrying its mechanism, its
measured gap, its benchmark and its RoI line. A small calculator lets the reader
supply throughput and price and see what one recovery point is worth to them —
every input labelled as theirs, so the screen still never asserts a magnitude it
cannot source. The 52-cell partition and the APQC table move below the value
argument as supporting detail.

## The calculator, as built

The value screen prices a recovery point, and the design of that panel is where
the honesty constraint had to be made structural rather than editorial.

A recovery point is not money until three quantities are known: how much ore
goes through the mill, what the ore carries, and what the metal sells for. The
site's own record settles exactly one of them — 167 days of concentrator feed
assays give a median of 1.08 % copper — and is silent on the other two. So the
panel publishes the one conversion it can derive, **108 t of contained copper
per million tonnes milled per point of recovery**, and stops. Throughput and
price are entered by the reader, are never defaulted, and each carries a label
saying whose figure it is and why this repository does not hold it. Until both
are supplied the result reads `[CLIENT INPUT REQUIRED]`.

The panel is laid out in two columns for that reason and not for balance: *what
this site's record settles* on the left, *what only you hold* on the right. The
split is the argument.

Three further constraints, each of which cost a defect before it was found:

- **Contained, not payable.** Smelter payability and treatment and refining
  charges take a cut this repository has no terms for. The figure is stated as
  contained metal and the omission is printed, because an upper bound that
  admits it is one is more useful to a CEO than a number that quietly is not.
- **The working is printed whether or not it evaluates.** A calculator that
  shows only its answer asks to be trusted; this one is meant to be checked.
- **The arithmetic on screen must reproduce.** The panel multiplies by the gap
  the reader can see, not by the float behind it — printing "1.96 points" and
  then returning a total that is not 1.96 × the unit rate is the same defect as
  a gap table whose columns do not subtract.

## Printed precision

Related, and the source of two defects caught in review: a figure's precision is
chosen so the reader's own arithmetic comes out.

Rounding by magnitude alone gave `92.3 %`, `94.3 %` and a gap of `+1.96 pts`,
which the first person to subtract the two columns catches. Where a gap is an
absolute difference, the gap sets the precision for the whole row, and the row
then widens until the displayed columns subtract to the displayed delta. This
lives in `shell.js` rather than per screen, because the landing and the value
screen quote the same recovery gap and a measurement printed two ways across two
screens is the same failure in slower motion.
