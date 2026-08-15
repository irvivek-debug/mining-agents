/* The site cockpit.
 *
 * The one job of this screen is to get a person to the right agent without them
 * having to know the catalog. Three groupings are offered rather than one
 * because the three are genuinely different questions: a supervisor arrives
 * knowing their role, a process owner arrives knowing their process area, and
 * an executive arrives knowing which part of the cost base is under pressure.
 * Picking one and calling it the taxonomy would serve one of the three and
 * quietly fail the others.
 *
 * Every group, count and roster below is read off DATA.catalog, which the build
 * derives from the module that constructs the agents. Nothing is typed here.
 */

mountNav("workspace", "index.html");
runState(el("runtime"));

const C = CAT.counts;

/* Every team is one lead, some specialists and one reviewer. The sentence below
   says so, so the shape is read rather than asserted — and if the catalogue
   ever holds two shapes, the screen stops rather than describing one of them as
   though it were both. */
const TEAM_SPECIALISTS = (() => {
  const sizes = [...new Set(Object.values(CAT.swarms).map((s) => s.specialists.length))];
  if (sizes.length !== 1) {
    throw new Error("the agent teams are no longer one shape; this screen says they are");
  }
  return sizes[0];
})();

el("lede").textContent =
  "Not every agent here takes questions. The ones that do are listed below; " +
  "behind each of them sit specialists and a reviewer you never address " +
  "directly. They are grouped three ways — by the person accountable, by " +
  "standard process area, and by where the money is — because which grouping " +
  "helps depends entirely on why you came here.";

el("counts").innerHTML = [
  [C.entrypoints, "agents you can talk to", "of " + C.agent_nodes + " in the teams behind them", true],
  [
    C.swarms,
    "agent teams",
    "a lead, " + TEAM_SPECIALISTS + " specialists and a reviewer",
    false,
  ],
  [C.deep_agents, "agents working alone", "one question each, no team behind them", false],
  [C.hitl_entrypoints, "need your sign-off", "before anything is committed", false],
]
  .map(
    ([value, label, sub, accent]) =>
      '<div class="card c3 stat">' +
      `<div class="metric${accent ? " accent" : ""}">${num(value)}</div>` +
      `<div><div style="font-size:13.5px;margin-top:8px">${esc(label)}</div>` +
      `<div class="metric-sub">${esc(sub)}</div></div></div>`
  )
  .join("");

/* How many agents are filed under more than one process area. The old copy said
   "seven" and nothing checked it. */
const SPANNERS = CAT.agents.filter(
  (a) => a.is_entrypoint && a.apqc_names.length > 1
).length;

/* What a group's line under its heading says. It used to be a count and a
   fragment glued together — "12 you can talk to", and on the money axis "where
   the branches meet · 1 you can talk to" — which is a card with no article, no
   noun and no verb in it. Each group has something to say about what its agents
   have in common, so it says it, in a sentence that survives a group of one.
   The verb is given in the plural and takes its "s" for the singular, which is
   true of every verb these lines need. */
function agentsWhich(n, verb, rest) {
  return (n === 1 ? "One agent " + verb + "s" : n + " agents " + verb) + " " + rest + ".";
}

/* The three axes. Each names where its groups come from and what a group means,
   because "where the money is" is not self-explanatory to someone who has not
   seen the cost tree, and a tab whose contents surprise you is a tab you stop
   using. */
const AXES = [
  {
    key: "persona",
    tab: "By person",
    head: "By the person accountable",
    lede:
      "One group per role on this site. It is the same grouping the role page " +
      "uses: you open your own page and find every agent that answers a " +
      "question you are answerable for.",
    groups: () =>
      Object.entries(CAT.by_persona).map(([code, g]) => ({
        title: (PERSONAS[code] || {}).title || code,
        sub: agentsWhich(g.count, "take", "questions from this role"),
        /* The paragraph is the catalogue's, not this screen's, and it was
           written in the estate's own words. It is printed without a citation
           against it, so it is description rather than quotation, and it is
           said the way the rest of this screen says it. */
        detail: plainProse((PERSONAS[code] || {}).accountable_for),
        agents: g.agents,
        href: "persona.html?p=" + encodeURIComponent(code),
        hrefLabel: "Open this role's page",
      })),
  },
  {
    key: "process",
    tab: "By process",
    head: "By standard process area",
    lede:
      "The standard process area each agent works in — the same list a process " +
      "owner already works from. " +
      SPANNERS +
      " agents sit in two areas at once and are counted in both, so these " +
      "groups add up to more than the number of agents. A fatigue agent that " +
      "also touches logistics genuinely belongs to both, and filing it under " +
      "one would flatter the coverage of neither.",
    groups: () =>
      Object.entries(CAT.by_apqc_code).map(([code, g]) => ({
        title: CAT.apqc_names[code] || code,
        sub: agentsWhich(g.count, "work", "in this process area"),
        detail: null,
        agents: g.agents,
      })),
  },
  {
    key: "branch",
    tab: "By where the money is",
    head: "By where the money is",
    lede:
      "Which part of the cost of running this site an agent works on. The tree " +
      "these come from is rooted on all-in sustaining cost per tonne. Every " +
      "agent you can talk to sits in exactly one part of it, or in the layer " +
      "above where the parts meet, and the build refuses to publish a tree " +
      "whose parts do not add back to the catalog's own count.",
    groups: () =>
      Object.entries(CAT.by_value_branch).map(([branch, g]) => {
        const b = DATA.value_tree.branches.find((x) => x.branches.includes(branch));
        return {
          title: branch.replace(/_/g, " "),
          sub: b
            ? agentsWhich(g.count, "work", "on this part of the cost")
            : agentsWhich(g.count, "sit", "above the parts, where they meet"),
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

/* An agent that leads a team opens that team's page. An agent that works on its
   own has no page of its own — it is reached through the page of the role
   answerable for it, which is where a question can actually be put to it. The
   role is declared on every agent in the catalog, so this is a lookup, not a
   guess. */
function chip(id) {
  const a = AGENTS[id];
  const href =
    a.pattern === "A"
      ? "swarm.html?s=" + id
      : "persona.html?p=" + encodeURIComponent(a.persona);
  return (
    `<a class="chip${a.hitl_required ? " signoff" : ""}" href="${href}" ` +
    `title="${esc(a.display_name)}${a.hitl_required ? " — needs your sign-off" : ""}">` +
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

const GATED = CAT.agents.filter((a) => a.is_entrypoint && a.hitl_required);

el("signoff-lede").textContent =
  GATED.length +
  " of the " +
  C.entrypoints +
  " agents you can talk to cannot act on what they conclude. Each one puts " +
  "the case together, shows the evidence behind it, and then stops: it needs " +
  "your sign-off before anything moves. There is no other route by which a " +
  "recommendation reaches a system of record. The agent can only ask; only a " +
  "person can commit.";

el("signoff").innerHTML = GATED.map((a) => a.agent_id).map(chip).join("");

/* Everything the copy above stopped naming, in one place: the code each agent
   is filed under, the process area it maps to, the part of the cost tree it
   serves, the model tier it runs on, and the table an approval is written to.
   None of it is needed to find an agent, and all of it is needed to check one. */
function drawerBody() {
  const rows = CAT.agents
    .filter((a) => a.is_entrypoint)
    .map(
      (a) =>
        `<dt class="mono">${esc(a.agent_id)}</dt>` +
        `<dd>${esc(a.display_name)}<br>` +
        `<span class="mono">${esc(a.persona)} · ${esc(a.apqc_code)} · ` +
        `${esc(branchList(a.value_branch).join(", "))} · ${esc(a.model_tier)}` +
        (a.hitl_required ? " · hitl_required" : "") +
        "</span></dd>"
    )
    .join("");
  return (
    "<p>One row per agent you can talk to: its id, the role it is filed " +
    "under, its process code, the branch of the cost tree it serves and the " +
    "model tier it runs on. An agent marked <span class=\"mono\">hitl_required" +
    "</span> is bound to the <span class=\"mono\">request_approval</span> tool, " +
    "which writes a single row with <span class=\"mono\">decision = PENDING</span> " +
    "and can write nothing else.</p>" +
    `<dl>${rows}</dl>` +
    `<dl><dt>Approvals are written to</dt><dd class="mono">${esc(WS.approval.table)}</dd>` +
    `<dt>Process codes</dt><dd class="mono">${esc(
      Object.keys(CAT.by_apqc_code).join(" · ")
    )}</dd></dl>` +
    connectionDetail()
  );
}

/* value_branch is a string on most agents and a list on a few. Reading it
   directly is how a screen comes to print "s,u,p,p,l,y". Named apart from
   persona-data.js's branchesOf on purpose: two top-level declarations of one
   name in classic scripts is the later one, silently. */
function branchList(value) {
  return [].concat(value || []);
}

el("prov").innerHTML =
  technicalDrawer(drawerBody(), "agent ids, process codes, model tiers") +
  provenance(`<dt>Runtime</dt><dd>${runtimeNote()}</dd>`);
