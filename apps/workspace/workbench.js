/* SC-3 — the departmental workbench. Eight configurations, one per persona.
 *
 * This is the screen a person opens every day, and the only one of the five
 * that is organised around a job rather than around the architecture. The
 * cockpit files 52 entrypoints three ways; the swarm console draws a topology;
 * this screen answers a narrower question — what can I ask, what will it read,
 * and what will it not be able to tell me.
 *
 * So the department comes first and the agent second. The rail holds only the
 * entrypoints this person is accountable for, and the friction the department
 * carries is stated in the person's own recorded words, with the line of
 * docs/personas-and-value-tree.md they were transcribed from. Nothing on this
 * screen is written on the persona's behalf either: the quotes are theirs, the
 * jobs are theirs, and where an agent's answer would go, the reason it is
 * absent goes instead.
 */

mountNav("workspace", "workbench.html");

const DEPARTMENTS = Object.keys(CAT.by_persona).sort();

/* Two ways in, and they have to agree. A chip on the cockpit deep-links to one
   agent (?a=D02); the department button links to a person (?p=P1). An agent
   names its own persona, so the agent wins and the department follows from it
   rather than the two being carried independently and drifting apart. */
const wanted = param("a");
const agent = AGENTS[wanted] && AGENTS[wanted].is_entrypoint ? wanted : null;
const dept = agent
  ? AGENTS[agent].persona
  : DEPARTMENTS.includes(param("p"))
    ? param("p")
    : DEPARTMENTS[0];

const roster = CAT.by_persona[dept].agents;
const current = agent || roster[0];
const a = AGENTS[current];
const persona = PERSONAS[dept] || {};

/* A7: the Mine Controller reads this from the control room's overhead display
   rather than at a desk, where the audit measured 14px body text as illegible.
   The whole department steps up 1.5×, applied by persona so that the person
   does not have to know to ask for it. */
if (dept === "P7") {
  el("wrap").classList.add("scale-lg");
  el("scale-note").textContent =
    "Overhead type scale (1.5×) — this department is read from the control " +
    "room display rather than at a desk.";
}

document.title = `${persona.title || dept} workbench — Mining Agents workspace`;
el("title").textContent = persona.title || dept;

const hitlCount = roster.filter((id) => AGENTS[id].hitl_required).length;
el("lede").textContent =
  `${roster.length} of the ${CAT.counts.entrypoints} callable entrypoints answer ` +
  `to this role` +
  (hitlCount
    ? `, and ${hitlCount} of them cannot act without this person approving it. `
    : `, and none of them can commit an action. `) +
  (persona.accountable_for || "").trim();

el("departments").innerHTML = DEPARTMENTS.map(
  (code) =>
    `<a href="workbench.html?p=${encodeURIComponent(code)}"` +
    (code === dept ? ' aria-current="page"' : "") +
    `>${esc((PERSONAS[code] || {}).title || code)}</a>`
).join("");

el("rail-cap").textContent = `${roster.length} entrypoints`;
el("rail").innerHTML = roster
  .map((id) => agentRow(id, "workbench.html?a=" + encodeURIComponent(id), current))
  .join("");

/* The department's own words. These are transcribed quotes with the source line
   recorded, which is why they can be shown as quotes: nobody wrote them for
   this screen. jobs_to_be_done sits in a disclosure because it is reference
   material a person consults, where the pain points are the framing they read
   once — but both are on the page, and neither is behind a hover. */
function department() {
  const pains = (persona.pain_points || [])
    .map(
      (q) =>
        '<blockquote class="verbatim">' +
        `${esc(q.quote.trim())}` +
        `<cite>${esc(persona.title || dept)} · docs/personas-and-value-tree.md line ${esc(
          q.source_line
        )}</cite></blockquote>`
    )
    .join("");

  const jobs = (persona.jobs_to_be_done || [])
    .map((j) => `<li>${esc(j.trim())}</li>`)
    .join("");

  return (
    '<div class="card"><div class="card-cap">The friction this department carries</div>' +
    (pains || '<p class="dim">No pain points are recorded for this role.</p>') +
    (jobs
      ? "<details class='tbl'><summary>" +
        `<span>What this person is trying to get done (${persona.jobs_to_be_done.length})</span>` +
        "</summary><ul class='tight'>" +
        jobs +
        "</ul></details>"
      : "") +
    "</div>"
  );
}

/* What the selected entrypoint is, before what it does. Pattern is the fact
   that changes how the answer arrives — a deep agent answers on its own, a
   coordinator fans the question across four more nodes — so it is stated here
   rather than left to be inferred from the tool list. */
function identity() {
  const kind =
    a.pattern === "A"
      ? `Swarm coordinator — dispatches ${swarmSize(a.swarm_id) - 2} specialists and one critic`
      : "Deep agent — answers on its own, with no specialists beneath it";
  return (
    '<div class="card"><div class="card-cap">The entrypoint</div>' +
    `<h3 style="margin:0 0 6px">${esc(a.display_name)}</h3>` +
    `<div class="mono dim" style="font-size:11.5px;margin-bottom:12px">${esc(current)} · ` +
    `${esc(a.apqc_names.join(" / "))} (${esc(a.apqc_code)}) · ` +
    `${esc(a.value_branch.replace(/_/g, " "))}</div>` +
    `<p style="margin:0 0 12px;font-size:13.5px">${esc(kind)}.</p>` +
    /* Tools as plain text, not as chips: a chip in this suite is a link to an
       agent, and a tool name that looks tappable but is not is a small lie
       repeated 52 times. */
    `<div class="node-tools">tools: ${esc(a.tools.join(" · "))}</div>` +
    (a.hitl_required
      ? '<p style="margin:12px 0 0;font-size:13px">' +
        stateBadge("blocked", "human approval required") +
        " Nothing this entrypoint proposes reaches a system of record until " +
        `the ${esc(persona.title || dept)} approves it.</p>`
      : "") +
    (a.pattern === "A"
      ? '<div class="btn-row" style="margin-top:14px">' +
        `<a class="btn" href="swarm.html?s=${encodeURIComponent(current)}">` +
        "See how this swarm is wired</a></div>"
      : "") +
    (current === "S12"
      ? '<div class="btn-row" style="margin-top:14px">' +
        '<a class="btn" href="handover.html">Open the shift handover</a></div>'
      : "") +
    "</div>"
  );
}

el("work").innerHTML =
  department() +
  '<div style="margin-top:16px">' +
  identity() +
  "</div>" +
  journeyForBlock() +
  '<div class="card" style="margin-top:16px"><div class="card-cap">Method</div>' +
  method(current) +
  "</div>" +
  '<div class="card" style="margin-top:16px"><div class="card-cap">Inputs — table and column, not "the data"</div>' +
  inputs(current) +
  "</div>" +
  '<div class="card" style="margin-top:16px"><div class="card-cap">Execution trace</div>' +
  notConnected(
    "A real trace lists every tool call this entrypoint made, with the " +
      "statement sent and the row count returned. None was made."
  ) +
  "</div>" +
  '<div style="margin-top:16px">' +
  unverified([current]) +
  "</div>" +
  (a.hitl_required
    ? '<div class="btn-row" style="margin-top:16px">' +
      '<button class="btn primary" id="review">Review the approval this agent would raise</button>' +
      "</div>"
    : "");

function journeyForBlock() {
  const block = journeyFor(current);
  return block ? `<div style="margin-top:16px">${block}</div>` : "";
}

if (a.hitl_required) {
  el("review").addEventListener("click", () => openApproval(current));
}

el("prov").innerHTML = provenance(
  `<dt>Department</dt><dd>${esc(persona.title || dept)} · ${esc(dept)} · ` +
    `<span class="mono">${esc(roster.join(" · "))}</span></dd>` +
    `<dt>Runtime</dt><dd>${esc(WS.runtime.reason)}</dd>`
);
