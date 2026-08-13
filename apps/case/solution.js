/* Screen 1.4 — how the hundred agents are assembled. */

mountNav("case", "solution.html");

const catalog = DATA.catalog;
const byId = Object.fromEntries(catalog.agents.map((a) => [a.agent_id, a]));
const personas = DATA.personas.personas;

function name(id) {
  return byId[id] ? byId[id].display_name : id;
}

/* Swarms as a table rather than twelve cards: the interesting thing is that the
   shape repeats exactly twelve times, and a table shows repetition where a grid
   of cards hides it. */
el("swarms").innerHTML =
  '<table class="data"><thead><tr>' +
  "<th>Swarm</th><th>Coordinator — the door</th><th>Specialists</th><th>Critic</th>" +
  "</tr></thead><tbody>" +
  Object.entries(catalog.swarms)
    .map(
      ([id, s]) =>
        "<tr>" +
        `<td class="mono">${esc(id)}</td>` +
        `<td>${esc(name(s.coordinator))}` +
        (byId[s.coordinator] && byId[s.coordinator].hitl_required
          ? ' <span class="badge b-warn">Approval</span>'
          : "") +
        "</td>" +
        `<td class="mono" style="font-size:11px;color:var(--fg-muted)">${esc(
          s.specialists.join(" ")
        )}</td>` +
        `<td class="mono" style="font-size:11px;color:var(--fg-muted)">${esc(
          s.critic || "—"
        )}</td>` +
        "</tr>"
    )
    .join("") +
  "</tbody></table>";

/* The five tools, sized by how many entry points hold each. This is the honest
   summary of what these agents can actually do: mostly they read the warehouse. */
const TOOL_NOTE = {
  bq_query: "Reads the warehouse. Every agent that answers with evidence uses it.",
  request_approval: "Stops and waits for a named human. Present on exactly the gated agents.",
  operational_math: "Deterministic arithmetic, so a rate or a ratio is computed, not generated.",
  graph_traverse: "Walks a property graph — blast radius, stockout exposure, fatigue to incident.",
  bqml_predict: "Calls a trained model in BigQuery ML rather than guessing a forecast.",
};

const toolMax = Math.max(...Object.values(catalog.tool_usage));
el("tools").innerHTML =
  '<div class="card c12"><div class="card-cap">Five tools, across all ' +
  esc(catalog.counts.entrypoints) +
  " entry points</div>" +
  Object.entries(catalog.tool_usage)
    .map(
      ([tool, n]) =>
        '<div class="bar-row">' +
        `<div class="name mono">${esc(tool)}</div>` +
        `<div class="bar"><span style="width:${(n / toolMax) * 100}%"></span></div>` +
        `<div class="n">${esc(n)}</div>` +
        "</div>" +
        `<div style="font-size:12.5px;color:var(--fg-muted);margin:-4px 0 12px">${esc(
          TOOL_NOTE[tool] || ""
        )}</div>`
    )
    .join("") +
  "</div>";

/* The gated agents, named. "14 require approval" is a statistic; naming them is
   a commitment someone can check. */
const gated = catalog.agents.filter((a) => a.is_entrypoint && a.hitl_required);

el("hitl-lede").innerHTML =
  `${esc(gated.length)} of the ${esc(catalog.counts.entrypoints)} entry points cannot ` +
  "act on their own conclusion. They assemble the case, show their reasoning and the " +
  "telemetry behind it, and then stop until a named person holds the confirm control down. " +
  "The other " +
  esc(catalog.counts.entrypoints - gated.length) +
  " answer questions; these change something.";

el("hitl").innerHTML = gated
  .map(
    (a) =>
      "<tr>" +
      `<td class="mono">${esc(a.agent_id)}</td>` +
      `<td>${esc(a.display_name)}</td>` +
      `<td>${esc(a.persona)} · ${esc(personas[a.persona] ? personas[a.persona].title : "—")}</td>` +
      `<td><span class="badge ${a.pattern === "A" ? "b-info" : "b-idle"}">Pattern ${esc(
        a.pattern
      )}</span></td>` +
      "</tr>"
  )
  .join("");

/* Deployment facts. The service account count and the platform are architecture
   decisions recorded in the engagement notes, not derivable from the catalog,
   so they are labelled as the stated design rather than as counted output. */
const DEPLOY = [
  { n: catalog.counts.entrypoints, label: "Cloud Run services",
    sub: "One per entry point. A specialist runs inside its coordinator's service." },
  { n: 3, label: "Service accounts",
    sub: "Per tier, not per agent. A hundred identities would be a hundred things to rotate." },
  { n: Object.keys(catalog.tool_usage).length, label: "Tools in the whole estate",
    sub: "An agent can only call what its catalog entry grants it." },
  { n: new Set(catalog.agents.flatMap((a) => a.source_tables)).size,
    label: "Distinct tables read",
    sub: "Each agent is bound at build time to its own subset." },
];

el("deploy").innerHTML =
  DEPLOY.map(
    (d) =>
      '<div class="card c3 stat"><div>' +
      `<div class="metric">${num(d.n)}</div>` +
      `<div class="metric-sub">${esc(d.label)}</div></div>` +
      `<div style="color:var(--fg-muted);font-size:12.5px;margin-top:10px">${esc(d.sub)}</div>` +
      "</div>"
  ).join("") +
  '<div class="card c12"><div class="note info" style="margin:0"><strong>Model tiers</strong><br>' +
  Object.entries(
    catalog.agents.reduce((acc, a) => {
      acc[a.model_tier] = (acc[a.model_tier] || 0) + 1;
      return acc;
    }, {})
  )
    .sort((a, b) => b[1] - a[1])
    .map(([tier, n]) => `<span class="mono">${esc(tier)}</span> ${esc(n)}`)
    .join(" · ") +
  " — across all " +
  esc(catalog.counts.agent_nodes) +
  " agent nodes. A critic does not need the model a coordinator needs, and paying " +
  "for one everywhere is how a demo becomes too expensive to run twice." +
  "</div></div>";

el("prov").innerHTML = provenance(
  "<dt>Service accounts</dt><dd>Three-tier model, an architecture decision recorded in " +
    "the engagement notes rather than counted from the catalog.</dd>"
);
