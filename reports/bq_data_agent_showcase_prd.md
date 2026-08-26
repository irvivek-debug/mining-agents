# BigQuery Data Agent Showcase — PRD & Prompt Scripts

**What this is.** Four demo scenarios run *entirely inside BigQuery Data
Agents* — conversational prompts over `mining_data`, no custom agents, no
code. The star is BigQuery: grounded answers, native forecasting/anomaly
detection, and multi-table reasoning, live.

**Format per scenario:** the business setup a presenter says aloud, the
prompt script (typed verbatim into the data agent), the data it exercises,
impact and feasibility ratings, and the demo-day cross-check (a ground-truth
query whose numbers the agent's answers must reconcile with — computed live,
never memorised).

---

## S1 · Grade Reconciliation — "Where is the block model lying to us?"
*(catalogue A1 · Impact: $5–15M/yr class · Complexity: L2 multi-table reconciliation)*

**Setup line.** "The block model told us what we'd dig. The assay lab told
us what we actually dug. The gap between them is misclassified ore — sent
to the wrong destination at real cost. Watch the data agent find it."

**Prompt script**
1. `How many blocks are in geological_block_models and what is the average estimated copper grade percentage by lithology_type?`
2. `From drill_assay_logs, what is the average actual copper_grade_pct by geology_code?`
3. `Compare the estimated grade by lithology against the assayed grade for the matching geology code. Which lithology shows the largest gap between estimate and actual, in percentage points?`
4. `For that lithology, how many blocks are affected and what is the total estimated contained metal at risk if the actual grade applies? Show your calculation.`
5. `Summarize in three sentences for a mine general manager: what is misestimated, by how much, and what should we do first?`

**Data:** `geological_block_models` (1,000) ⟷ `drill_assay_logs` (295) via lithology/geology code.
**Feasibility:** HIGH — both tables populated, shared categorical key, simple aggregates.
**Cross-check:** est-vs-actual mean grade per lithology; the gap the agent names must match SQL to 2dp.

---

## S2 · Live Anomaly Hunt — "25,946 sensor readings, one question"
*(catalogue C2 · Impact: $2–10M/yr class · Complexity: L3 native anomaly detection)*

**Setup line.** "This is the largest table on the site — every sensor
reading from the plant. Nobody reads it. The data agent does."

**Prompt script**
1. `What metrics exist in telemetry_stream and how many readings does each have?`
2. `For the metric with the most readings, plot the daily average over time. Any visible drift?`
3. `Find anomalous readings in telemetry_stream: values more than 3 standard deviations from the mean for their metric_name. How many are there, and which assets produce the most?`
4. `Take the asset with the most anomalies: show its anomalous readings in time order. Are they clustered — and does the cluster look like a developing fault or a sensor problem? Justify from the data.`
5. `Draft the one-paragraph shift-handover note a plant supervisor should read tomorrow morning.`

**Data:** `telemetry_stream` (25,946).
**Feasibility:** HIGH — single wide table; statistical outliers verified to exist before demo.
**Cross-check:** outlier count at z>3 per metric; the agent's count must match SQL.

---

## S3 · Parts-to-Failure Graph — "Which stock-out stops which machine?"
*(catalogue D2 · Impact: $2–8M/yr class · Complexity: L4 graph traversal in SQL)*

**Setup line.** "This is a graph question: parts connect to work orders,
work orders connect to machines. A stock-out on a $200 part can idle a
$20M asset. The agent walks the graph."

**Prompt script**
1. `Which parts in spares_inventory are at_or_below_reorder right now? List part_number, stock_level, lead_time_days.`
2. `Using work_order_parts_edge, which historical work orders consumed those at-risk parts?`
3. `Join through to erp_work_orders: which assets did those work orders repair, and what was the total repair_cost per asset?`
4. `So: rank the assets most exposed to a parts stock-out today — combine the number of at-risk parts they depend on, the historical repair cost, and the longest lead_time_days among their at-risk parts. Explain the ranking.`
5. `If we could expedite only three purchase orders this week, which parts, and why those three?`

**Data:** `spares_inventory` (105) → `work_order_parts_edge` (186) → `erp_work_orders` (500).
**Feasibility:** MEDIUM-HIGH — the two-hop chain is verified non-empty; graph is shallow (186 edges) so depth is honest, not implied.
**Cross-check:** exposed-asset list from the two-hop SQL join; agent's ranking keys must appear in it.

---

## S4 · Pit-to-Port Cascade — "Crusher down six hours: who pays at the port?"
*(catalogue G1 · Impact: $5–20M/event class · Complexity: L5 four-hop cross-domain chain)*

**Setup line.** "One machine hiccups at the pit; three weeks later a ship
owner sends a demurrage invoice. Four systems apart. Watch one question
walk the whole chain."

**Prompt script**
1. `From crusher_states, what is the average feed_rate_tph, and how many hours of readings show the bypass_valve_open?`
2. `If the crusher stops for 6 hours at that average feed rate, how many tonnes of production are lost?`
3. `From stockpiles, how many hours of reclaim can each stockpile sustain at its reclaim_rate_tph before running empty? Which run out first?`
4. `Trace forward: using rail_schedules, which consists load from those at-risk stockpiles, and using port_vessels (consist_ids contains the consist), which vessels do they feed?`
5. `Those vessels: what are their demurrage_days and loaded_tonnes? Estimate the demurrage exposure if loading slips by one day, stating your assumption for the daily demurrage rate as a range.`
6. `Write the five-line brief for the logistics manager: the chain from crusher to vessel, the first bottleneck, and the single action that buys the most time.`

**Data:** `crusher_states` (167) → `stockpiles` (60) → `rail_schedules` (120) → `port_vessels` (via `UNNEST(consist_ids)`).
**Feasibility:** MEDIUM — the chain is real (array join verified); the 6-hour outage is a stated hypothetical, and the prompt makes the agent state its rate assumption as a range rather than invent a price.
**Cross-check:** the stockpile→consist→vessel chain from SQL; every vessel the agent names must appear in the chain, and demurrage_days must match.

---

## Evaluation gates (per scenario, before demo day)
1. **Unit tests** (`tests/showcase/test_bq_scenarios.py`): tables populated,
   join paths non-empty, signal exists (a gap / outliers / exposed assets /
   a complete chain), ground truth computable. No hardcoded expectations —
   properties only, computed live.
2. **Business-lens review**: run the ground truth, read the actual numbers,
   and answer: would a GM/plant super/logistics manager act on this? If the
   numbers are trivial or absurd, the scenario is rewritten before it is
   ever demoed.

---

## Validation results (gates run 2026-08-26 — recompute live on demo day)

**Unit tests: 10/10 pass** (`tests/showcase/test_bq_scenarios.py`). One data
defect found and repaired en route: `rail_schedules.origin_stockpile_id`
carried unpadded IDs (`SP-01-1`) against zero-padded stockpiles (`SP-01-01`)
— the stockpile deepening re-minted IDs and the rail table never followed.
The four-hop cascade was silently empty until the key was canonicalised.

**Business-lens verdicts (live numbers at validation):**

- **S1 — CREDIBLE.** The model *underestimates* BASALT: 1.087% est vs
  1.192% assayed across 182 blocks (~10% relative). Story: ore risked
  being routed as waste — the right direction of error for a demo, and a
  believable magnitude.
- **S2 — CREDIBLE.** 37 vibration_hz readings beyond 3σ, concentrated on
  one asset — reads as a developing mechanical fault, not sensor noise.
- **S3 — ACTIONABLE.** CRUSHER-03 tops the exposure ranking: 5 at-risk
  parts, ~$277k historical repair cost through those parts, 14-day worst
  lead time. A maintenance manager would expedite exactly this.
- **S4 — THE DEMO MOMENT.** SP-02-01 holds 6.2 hours of reclaim buffer —
  against the scenario's 6-hour crusher outage. Razor-thin by nature, not
  by design. It feeds 9 vessels with 10 demurrage-days already on record
  downstream. The presenter's line writes itself: *"your buffer is six
  hours; the outage is six hours."*

All four proceed. Prompts are demo-ready as written.
