/* SC-5 — the shift handover brief. One agent, no controls, and a print button.
 *
 * Every other screen in this application is a place to ask something. This one
 * is not: the Shift Supervisor reads it at the change of shift, decides what to
 * carry forward, and often walks away with it on paper. So there is no rail, no
 * parameter, nothing to click that changes what is on the page, and the whole
 * document is written to survive being printed.
 *
 * The brief has four parts because the swarm has four working nodes. Three
 * summarisers each own a domain — availability, production, safety — and the
 * fourth is the Omission Critic, whose entire job is to name what the other
 * three did not cover. That band renders on every load, including when it has
 * nothing to report, and the reason is in P8's own words further down the page:
 * a brief that was useless because it missed the crusher event is
 * indistinguishable, to its reader, from a brief that had nothing to miss. A
 * band that appears only when there is something to say cannot be trusted to be
 * silent for the right reason.
 */

mountNav("workspace", "handover.html");

const S12 = AGENTS.S12;
const swarm = CAT.swarms.S12;
const members = ["S12", ...swarm.specialists, swarm.critic];
const supervisor = PERSONAS[S12.persona] || {};

document.title = `${S12.display_name} — Mining Agents workspace`;
el("title").textContent = "Shift handover brief";
el("lede").innerHTML =
  `<span class="mono">S12</span> ${esc(S12.display_name)}. ` +
  `Three summarisers cover availability, production and safety across ` +
  `${S12.source_tables.length} tables; a fourth node, the Omission Critic, ` +
  "reports what they left out. " +
  (S12.hitl_required
    ? "This brief requires approval before it is issued."
    : "This brief commits nothing and requires no approval — it is read, not actioned.");

/* The shift window is a site fact, not a repository fact. Nobody here knows
   whether this mine runs two twelves or three eights, and inventing 06:00–18:00
   because it is the common case would put a fabricated number at the top of the
   one screen that leaves the building on paper. */
function window_() {
  return (
    '<div class="card"><div class="card-cap">Shift window</div>' +
    '<div class="run-state">' +
    clientInput() +
    "<div><div>The shift pattern this brief covers.</div>" +
    '<div class="dim" style="font-size:12.5px;margin-top:4px">Whether this site ' +
    "runs two twelve-hour shifts or three eights, and when they change, is a " +
    "site roster fact. This repository does not hold one, and a plausible " +
    "window printed here would be read as the real one.</div></div>" +
    "</div></div>"
  );
}

/* One section per summariser. The section is the deliverable and the section is
   real: which node writes it, and which tables it is entitled to draw on, are
   both facts of the deployed catalog. Only the sentences are missing, and the
   block that says so is the same one every other screen uses. */
function section(id, index) {
  const a = AGENTS[id];
  return (
    '<div class="card" style="margin-top:16px">' +
    `<div class="card-cap">${index} · ${esc(a.display_name)}</div>` +
    `<div class="mono dim" style="font-size:11px;margin-bottom:12px">${esc(id)} · ` +
    `reads ${a.source_tables.length} tables</div>` +
    notConnected(
      `The ${a.display_name.toLowerCase()} writes this section in prose from the ` +
        "tables below. It has not run."
    ) +
    '<div style="margin-top:14px">' +
    inputs(id) +
    "</div></div>"
  );
}

/* The Omission Critic, always drawn, never conditional.
 *
 * It gets the loudest treatment on the page — the same 2px critical border the
 * approval sheet uses — because on a handover the thing that hurts is not the
 * item that was reported badly, it is the item that was not reported at all. */
function omission() {
  const critic = AGENTS[swarm.critic];
  return (
    '<div class="unverified" style="margin-top:16px">' +
    '<div class="unverified-cap"><span class="badge b-crit">⚠ OMISSION CRITIC</span>' +
    `<span>${esc(critic.display_name)} · ${esc(swarm.critic)}</span></div>` +
    "<ul><li><strong>Coverage has not been checked for this window.</strong>" +
    '<div class="dim mono">' +
    esc(WS.runtime.reason) +
    "</div>" +
    '<div class="remedy">This band is never empty and never hidden. When the ' +
    "critic runs and finds nothing, it says it found nothing — which is a " +
    "different statement from saying nothing, and only one of the two can be " +
    "relied on.</div></li>" +
    `<li><strong>What it checks against</strong><div class="dim mono">${esc(
      critic.source_tables.join(", ")
    )}</div>` +
    '<div class="remedy">The critic reads the source tables directly rather ' +
    "than reading the three summaries, so an event none of the summarisers " +
    "picked up is still visible to it.</div></li></ul></div>"
  );
}

/* Why this screen has an Omission Critic at all, in the supervisor's own
   recorded words. The quote is transcribed with its source line, which is what
   makes it quotable: it is evidence from the interview, not a justification
   written afterwards to fit the design. */
function why() {
  const quote = (supervisor.pain_points || []).find((q) => /missed|useless/i.test(q.quote));
  if (!quote) return "";
  return (
    '<div class="card" style="margin-top:16px"><div class="card-cap">Why the fourth node exists</div>' +
    '<blockquote class="verbatim">' +
    esc(quote.quote.trim()) +
    `<cite>${esc(supervisor.title || S12.persona)} · docs/personas-and-value-tree.md line ${esc(
      quote.source_line
    )}</cite></blockquote>` +
    "</div>"
  );
}

el("brief").innerHTML =
  '<div style="margin-top:16px">' +
  window_() +
  "</div>" +
  omission() +
  swarm.specialists.map((id, i) => section(id, i + 1)).join("") +
  why() +
  '<div style="margin-top:16px">' +
  unverified(members) +
  "</div>";

/* Print is one of the two ways this screen is read, so it is a control on the
   page and not something the reader has to know a keyboard shortcut for.
 *
 * A collapsed <details> prints as an empty box: its contents are not rendered,
 * so a reader on paper would get thirteen bordered rectangles where the tables
 * should be. Every disclosure is opened before the print dialog and restored
 * afterwards, so the screen the supervisor was reading is the screen they get
 * back. The hook is on the events rather than on the button because Ctrl-P is
 * how most people will actually print this. */
let reclose = [];

addEventListener("beforeprint", () => {
  reclose = [...document.querySelectorAll("details:not([open])")];
  reclose.forEach((d) => (d.open = true));
});

addEventListener("afterprint", () => {
  reclose.forEach((d) => (d.open = false));
  reclose = [];
});

el("print").addEventListener("click", () => window.print());

el("prov").innerHTML = provenance(
  `<dt>Swarm</dt><dd class="mono">${esc(members.join(" · "))}</dd>` +
    `<dt>Reader</dt><dd>${esc(supervisor.title || S12.persona)}</dd>` +
    `<dt>Runtime</dt><dd>${esc(WS.runtime.reason)}</dd>`
);
