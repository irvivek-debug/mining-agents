/* SC-1 — the site cockpit.
 *
 * The one job of this screen is to get a person to the right agent out of 52
 * without them having to know the catalog. Three groupings are offered rather
 * than one because the three are genuinely different questions: a supervisor
 * arrives knowing their role, a process owner arrives knowing their APQC
 * number, and an executive arrives knowing which line of the value tree is
 * under pressure. Picking one and calling it the taxonomy would serve one of
 * the three and quietly fail the others.
 *
 * Every group, count and roster below is read off DATA.catalog, which the build
 * derives from the module that constructs the agents. Nothing is typed here.
 */

mountNav("workspace", "index.html");
runState(el("runtime"));

const C = CAT.counts;

el("counts").innerHTML = [
  [C.entrypoints, "callable entrypoints", "of " + C.agent_nodes + " agent nodes", true],
  [C.swarms, "swarms", "coordinator, 3 specialists, 1 critic", false],
  [C.deep_agents, "deep agents", "single-agent, one question each", false],
  [C.hitl_entrypoints, "need human approval", "before any action is committed", false],
]
  .map(
    ([value, label, sub, accent]) =>
      '<div class="card c3 stat">' +
      `<div class="metric${accent ? " accent" : ""}">${num(value)}</div>` +
      `<div><div style="font-size:13.5px;margin-top:8px">${esc(label)}</div>` +
      `<div class="metric-sub">${esc(sub)}</div></div></div>`
  )
  .join("");

/* The three axes. Each names where its groups come from and what a group means,
   because "by value branch" is not self-explanatory to someone who has not read
   the value tree, and a tab whose contents surprise you is a tab you stop
   using. */
const AXES = [
  {
    key: "persona",
    tab: "By person",
    head: "By the person accountable",
    lede:
      "Eight roles, from the catalog's persona field. This is the grouping the " +
      "role page uses: a person opens their own page and finds every agent " +
      "that answers a question they are accountable for.",
    groups: () =>
      Object.entries(CAT.by_persona).map(([code, g]) => ({
        title: (PERSONAS[code] || {}).title || code,
        sub: code + " · " + g.count + " entrypoints",
        detail: (PERSONAS[code] || {}).accountable_for,
        agents: g.agents,
        href: "persona.html?p=" + encodeURIComponent(code),
        hrefLabel: "Open this role's page",
      })),
  },
  {
    key: "apqc",
    tab: "By process",
    head: "By APQC process",
    lede:
      "The APQC Process Classification Framework code each agent is filed " +
      "under. Seven agents span two domains and are counted in both, so these " +
      "counts sum above 52 by design — a fatigue agent that also touches " +
      "logistics belongs to both processes and hiding that would flatter the " +
      "coverage of neither.",
    groups: () =>
      Object.entries(CAT.by_apqc_code).map(([code, g]) => ({
        title: CAT.apqc_names[code] || code,
        sub: code + " · " + g.count + " entrypoints",
        detail: null,
        agents: g.agents,
      })),
  },
  {
    key: "branch",
    tab: "By value branch",
    head: "By value branch",
    lede:
      "The branch of the CEO value tree an agent serves, rooted on all-in " +
      "sustaining cost per tonne. Every entrypoint lands in exactly one branch " +
      "or in the convergence layer above them, and the build refuses to " +
      "publish a tree whose parts do not add back to 52.",
    groups: () =>
      Object.entries(CAT.by_value_branch).map(([branch, g]) => {
        const b = DATA.value_tree.branches.find((x) => x.branches.includes(branch));
        return {
          title: branch.replace(/_/g, " "),
          sub: (b ? b.code + " · " : "convergence · ") + g.count + " entrypoints",
          detail: b ? b.mechanism : DATA.value_tree.convergence.note,
          agents: g.agents,
        };
      }),
  },
];

let axis = AXES[0];

el("axes").innerHTML = AXES.map(
  (a) =>
    `<button role="tab" data-key="${a.key}" aria-selected="${a === axis}">${esc(a.tab)}</button>`
).join("");

el("axes").addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  axis = AXES.find((a) => a.key === button.dataset.key);
  [...el("axes").children].forEach((b) =>
    b.setAttribute("aria-selected", String(b.dataset.key === axis.key))
  );
  renderAxis();
});

/* A team agent opens its own team console. A specialist agent has no screen of
   its own — it is reached through the page of the role that is accountable for
   it, which is where a question can actually be put to it. The persona field is
   declared on every agent in the catalog, so this is a lookup, not a guess. */
function chip(id) {
  const a = AGENTS[id];
  const href =
    a.pattern === "A"
      ? "swarm.html?s=" + id
      : "persona.html?p=" + encodeURIComponent(a.persona);
  return (
    `<a class="chip${a.hitl_required ? " hitl" : ""}" href="${href}" ` +
    `title="${esc(a.display_name)}${a.hitl_required ? " — needs approval" : ""}">` +
    `${esc(id)}</a>`
  );
}

function renderAxis() {
  el("axis-head").textContent = axis.head;
  el("axis-lede").textContent = axis.lede;
  el("groups").innerHTML = axis
    .groups()
    .map(
      (g) =>
        '<div class="group c4">' +
        `<h3>${esc(g.title)}</h3>` +
        `<div class="group-sub">${esc(g.sub)}</div>` +
        (g.detail
          ? `<p style="font-size:13px;margin:0 0 12px">${esc(g.detail.trim())}</p>`
          : "") +
        `<div class="chips">${g.agents.map(chip).join("")}</div>` +
        (g.href
          ? `<div class="btn-row" style="margin-top:12px">` +
            `<a class="btn" href="${g.href}">${esc(g.hrefLabel)}</a></div>`
          : "") +
        "</div>"
    )
    .join("");
}

renderAxis();

el("hitl").innerHTML = CAT.agents
  .filter((a) => a.is_entrypoint && a.hitl_required)
  .map((a) => a.agent_id)
  .map(chip)
  .join("");

el("prov").innerHTML = provenance(
  `<dt>Runtime</dt><dd>${runtimeNote()}</dd>` +
    `<dt>Approvals</dt><dd class="mono">${esc(WS.approval.table)}</dd>`
);
