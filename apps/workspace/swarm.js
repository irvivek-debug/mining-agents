/* SC-2 — the swarm console. One archetype, twelve configurations.
 *
 * The reading this screen has to get right is the shape of the swarm. Four
 * agents run under a coordinator, but they are not four peers: three
 * specialists work the question in parallel and the critic works on what they
 * produced. Drawing the critic beside the specialists — which is what a flat
 * roster does — says the critic is a fourth opinion, when what it actually is
 * is the stage that challenges the other three. So the stages are rows, only
 * the specialist row fans sideways, and the critic sits below what it audits.
 *
 * The configuration is entirely catalog-driven: swap ?s= and the same code
 * renders a different swarm, because there is no per-swarm content here to go
 * stale.
 */

mountNav("workspace", "swarm.html");

const SWARM_IDS = CAT.agents
  .filter((a) => a.swarm_role === "coordinator")
  .map((a) => a.agent_id)
  .sort();

const current = SWARM_IDS.includes(param("s")) ? param("s") : SWARM_IDS[0];
const coord = AGENTS[current];
const swarm = CAT.swarms[coord.swarm_id];
const members = [current, ...swarm.specialists, swarm.critic];

/* A7: P7 reads the control room's overhead display from several metres back,
   where the audit measured 14px body text as illegible. Their configurations —
   and only theirs — step the whole screen up 1.5×. Applying it by persona
   rather than by a toggle is the point: the person does not have to know to
   ask for it. */
if (coord.persona === "P7") {
  el("wrap").classList.add("scale-lg");
  el("scale-note").textContent =
    "Overhead type scale (1.5×) — this configuration serves the Mine Controller, " +
    "who reads it from the control room display rather than at a desk.";
}

el("rail").innerHTML = SWARM_IDS.map((id) =>
  agentRow(id, "swarm.html?s=" + encodeURIComponent(id), current)
).join("");

const persona = PERSONAS[coord.persona] || {};
document.title = `${current} ${coord.display_name} — Mining Agents workspace`;
el("title").textContent = coord.display_name;
el("lede").innerHTML =
  `<span class="mono">${esc(current)}</span> coordinates ` +
  `${swarm.specialists.length} specialists and one critic — ` +
  `${members.length} of the ${CAT.counts.agent_nodes} agent nodes. ` +
  `Accountable persona: ${esc(persona.title || coord.persona)}. ` +
  `Process: ${esc(coord.apqc_names.join(" / "))} (${esc(coord.apqc_code)}). ` +
  (coord.hitl_required
    ? "Nothing this swarm proposes reaches a system of record without a human approving it."
    : "This swarm reports; it commits nothing.");

/* Every node is WAITING, and that is the truthful state rather than a
   placeholder: nothing has run because nothing can be reached. The state
   vocabulary is still exercised in full here — glyph, word and colour on every
   badge — so that a reader learns it now and recognises it when a real run
   fills it in. */
function nodeCard(id, cls) {
  const a = AGENTS[id];
  return (
    `<div class="node${cls ? " " + cls : ""}">` +
    `<div class="node-id">${esc(id)}</div>` +
    `<div class="node-name">${esc(a.display_name)}</div>` +
    stateBadge("waiting", "not connected") +
    `<div class="node-tools" style="margin-top:8px">${esc(a.tools.join(" · "))}</div>` +
    (a.traversals.length
      ? `<div class="node-tools">traversal: ${esc(a.traversals.join(", "))}</div>`
      : "") +
    (a.models.length ? `<div class="node-tools">model: ${esc(a.models.join(", "))}</div>` : "") +
    "</div>"
  );
}

const blockers = flagsFor(members);

el("work").innerHTML =
  journeyFor(current) +

  '<div class="card" style="margin-top:16px"><div class="card-cap">Stages</div>' +
  '<div class="stage"><div class="stage-cap">1 · Coordinator</div>' +
  `<div class="fan">${nodeCard(current)}</div></div>` +
  '<div class="flow">↓ dispatches in parallel</div>' +
  `<div class="stage"><div class="stage-cap">2 · Specialists (${swarm.specialists.length}, concurrent)</div>` +
  `<div class="fan">${swarm.specialists.map((id) => nodeCard(id)).join("")}</div></div>` +
  '<div class="flow">↓ challenges what stage 2 produced</div>' +
  '<div class="stage"><div class="stage-cap">3 · Critic</div>' +
  `<div class="fan">${nodeCard(swarm.critic, "critic")}</div></div>` +
  (coord.hitl_required
    ? '<div class="flow">↓ nothing is committed until a person approves</div>' +
      '<div class="stage"><div class="stage-cap">4 · Human approval</div>' +
      '<div class="fan"><div class="node" style="border-color:var(--warning)">' +
      '<div class="node-id">SC-4</div>' +
      `<div class="node-name">${esc(persona.title || coord.persona)} approves, modifies or refuses</div>` +
      stateBadge("waiting", "no request pending") +
      `<div class="node-tools" style="margin-top:8px">writes ${esc(WS.approval.table)}</div>` +
      "</div></div></div>"
    : "") +
  "</div>" +

  /* Blocked is a first-class state, so its band is a standing part of the
     screen rather than something that appears when a run fails. It renders
     even when empty, for the same reason the omission critic does on SC-5: a
     band that only appears when there is something to say cannot be trusted to
     be silent for the right reason. */
  '<div class="card" style="margin-top:16px"><div class="card-cap">Blocked — what stands between this swarm and a run</div>' +
  (blockers.length
    ? "<ul class='tight'>" +
      blockers
        .map(
          (b) =>
            `<li>${stateBadge("blocked")} <strong>${esc(b.what)}</strong>` +
            `<div class="dim mono" style="font-size:11.5px">${esc(b.detail)}</div>` +
            `<div class="remedy">Remedy: ${esc(b.remedy)}</div></li>`
        )
        .join("") +
      "</ul>"
    : `<p>${stateBadge("done")} Nothing outstanding. Every source table is ` +
      "present, every model is verified, and the endpoint answers.</p>") +
  "</div>" +

  '<div class="card" style="margin-top:16px"><div class="card-cap">Execution trace</div>' +
  notConnected(
    "A real trace lists each tool call the coordinator and its specialists made, " +
      "with the statement sent and the rows returned. None was made."
  ) +
  "</div>" +

  '<div class="card" style="margin-top:16px"><div class="card-cap">Method</div>' +
  method(current) +
  "</div>" +

  '<div class="card" style="margin-top:16px"><div class="card-cap">Inputs — every table this swarm reads</div>' +
  '<p class="dim" style="font-size:12.5px;margin:0 0 12px">' +
  "Union across all " +
  members.length +
  " members. Expand a table for its columns and, where it has been written, " +
  "what each column means.</p>" +
  swarmInputs() +
  "</div>" +

  '<div style="margin-top:16px">' +
  unverified(members) +
  "</div>" +

  (coord.hitl_required
    ? '<div class="btn-row" style="margin-top:16px">' +
      `<button class="btn primary" id="review">Review the approval this swarm would raise</button>` +
      "</div>"
    : "");

function swarmInputs() {
  const tables = [...new Set(members.flatMap((id) => AGENTS[id].source_tables))].sort();
  /* inputs() is written against one agent, and the swarm reads the union. A
     synthetic agent record is the smallest way to reuse it without giving the
     component a second signature it would only ever be called with once. */
  AGENTS.__swarm__ = { source_tables: tables };
  return inputs("__swarm__");
}

if (coord.hitl_required) {
  el("review").addEventListener("click", () => openApproval(current));
}

el("prov").innerHTML = provenance(
  `<dt>Swarm</dt><dd class="mono">${esc(members.join(" · "))}</dd>` +
    `<dt>Runtime</dt><dd>${runtimeNote()}</dd>`
);
