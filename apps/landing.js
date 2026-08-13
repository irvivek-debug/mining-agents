/* The front door. Two cards, and every figure on both read off the catalog.
 *
 * There is no navigation bar here on purpose: this page is a fork in the road
 * and the two applications each own their own chrome. A third nav would imply a
 * place above them that a reader can return to, and there is nothing there.
 */

const C = DATA.catalog.counts;
const HITL = DATA.catalog.agents.filter((a) => a.is_entrypoint && a.hitl_required).length;

const APPS = [
  {
    href: "case/index.html",
    eyebrow: "Application 1 · five screens",
    title: "The case for change",
    lede:
      "Why the estate is worth building, told in the order a decision is made: " +
      "the proposition, the mine as this demo holds it, where the value is " +
      "unlocked, how the answer is assembled, and the property graph the " +
      "traversals actually run over.",
    facts: [
      [C.agent_nodes + " agent nodes", "counted from the module that builds them"],
      [
        DATA.value_tree.branches.length + " value branches",
        "rooted on all-in sustaining cost per tonne",
      ],
      [
        Object.keys(DATA.graph.graphs).length + " property graphs",
        "drawn, traversable, with the SQL on screen",
      ],
    ],
    cta: "Read the case",
  },
  {
    href: "workspace/index.html",
    eyebrow: "Application 2 · five screens",
    title: "The site workspace",
    lede:
      "What a person does with the estate once it exists: find the right " +
      "entrypoint out of " +
      C.entrypoints +
      ", see how a swarm is wired, work the entrypoints one role is " +
      "accountable for, approve what cannot act alone, and read the handover " +
      "at shift change.",
    facts: [
      [C.entrypoints + " callable entrypoints", "of the " + C.agent_nodes + " nodes"],
      [HITL + " need a human", "bound to request_approval by the catalog"],
      [C.swarms + " swarms · " + C.deep_agents + " deep agents", "one console each"],
    ],
    cta: "Open the workspace",
  },
];

el("apps").innerHTML = APPS.map(
  (a) =>
    '<div class="card c6">' +
    `<div class="card-cap">${esc(a.eyebrow)}</div>` +
    `<h2 style="margin:0 0 8px">${esc(a.title)}</h2>` +
    `<p style="font-size:14px;margin:0 0 16px">${esc(a.lede)}</p>` +
    '<dl class="kv">' +
    a.facts
      .map(
        ([head, sub]) =>
          `<dt>${esc(head.split(" ")[0])}</dt>` +
          `<dd>${esc(head.split(" ").slice(1).join(" "))} — ` +
          `<span class="dim">${esc(sub)}</span></dd>`
      )
      .join("") +
    "</dl>" +
    '<div class="btn-row" style="margin-top:16px">' +
    `<a class="btn primary" href="${a.href}">${esc(a.cta)}</a></div>` +
    "</div>"
).join("");

el("prov").innerHTML = provenance(
  "<dt>Applications</dt><dd>Both read one bundle; neither holds a figure of its own.</dd>"
);
