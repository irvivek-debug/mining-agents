/* Screen 1.1 — the proposition. */

mountNav("case", "index.html");

const facts = DATA.facts;
const counts = DATA.catalog.counts;

el("anchor").textContent =
  "$" + facts.mill_downtime_usd_per_hour.toLocaleString("en-US");
el("anchor-src").textContent = facts.mill_downtime_source;

/* The scale tiles. Each reads a counted field; none carries a literal, so a
   catalog change moves the screen rather than contradicting it. */
const TILES = [
  { n: counts.agent_nodes, label: "Agent nodes deployed",
    sub: "Coordinators, specialists, critics and deep agents" },
  { n: counts.entrypoints, label: "Externally callable entry points",
    sub: "A specialist is reachable only through its coordinator" },
  { n: counts.swarms, label: "Swarms",
    sub: "Coordinator, three specialists and a critic apiece" },
  { n: counts.deep_agents, label: "Departmental deep agents",
    sub: "One role, one process, one question at a time" },
  { n: counts.hitl_entrypoints, label: "Gated on human approval",
    sub: "The agent proposes; a named person commits" },
  { n: Object.keys(DATA.personas.personas).length, label: "Personas served",
    sub: "Each with the agents they own and the branch they answer for" },
  { n: Object.keys(DATA.catalog.by_value_branch).length, label: "Value branches",
    sub: "Where the work lands on the value tree" },
  { n: Object.keys(DATA.catalog.apqc_names).length, label: "APQC processes",
    sub: "The process taxonomy the catalog maps onto" },
];

el("scale").innerHTML = TILES.map(
  (t) =>
    '<div class="card c3 stat"><div>' +
    `<div class="metric">${num(t.n)}</div>` +
    `<div class="metric-sub">${esc(t.label)}</div></div>` +
    `<div style="color:var(--fg-muted);font-size:12.5px;margin-top:10px">${esc(t.sub)}</div>` +
    "</div>"
).join("");

/* The "today" column quotes people, not marketing. Only quotes that are about
   the cost of assembling an answer belong on this screen; the rest of each
   persona's pain is on their own screen in application 2. */
const ORIENTATION_PAIN = [
  ["P1", "I need three systems open at once just to answer one question."],
  ["P1", "Half my day is data wrangling, not engineering."],
  ["P2", null],
  ["P4", null],
];

const picked = [];
for (const [code, wanted] of ORIENTATION_PAIN) {
  const persona = DATA.personas.personas[code];
  if (!persona) continue;
  const hit = wanted
    ? persona.pain_points.find((p) => p.quote === wanted)
    : persona.pain_points[0];
  if (hit) picked.push({ persona, quote: hit });
}

/* A quote that no longer exists in the source must not silently vanish: the
   screen would just look thinner and no one would know why. */
if (picked.length !== ORIENTATION_PAIN.length) {
  picked.push({
    persona: { code: "—", title: "Missing quote" },
    quote: {
      quote:
        "A quote this screen names is no longer in docs/persona-profiles.yaml. " +
        "Re-run scripts/build_app_data.py and reconcile.",
      source_line: 0,
    },
  });
}

el("today").innerHTML = picked
  .map(
    (p) =>
      '<blockquote class="verbatim">' +
      esc(p.quote.quote) +
      `<cite>${esc(p.persona.code)} · ${esc(p.persona.title)}` +
      (p.quote.source_line
        ? ` · personas-and-value-tree.md:${esc(p.quote.source_line)}`
        : "") +
      "</cite></blockquote>"
  )
  .join("");

el("prov").innerHTML = provenance(
  `<dt>Site figures</dt><dd class="mono">${esc(facts.generated_at)}</dd>` +
    `<dt>Latency</dt><dd>D01 timed end to end on 2026-08-12; see /tmp/time_agents.py in the working notes</dd>`
);
