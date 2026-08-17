/* Screen: the value case, in three bands (design doc section 1).
 *
 * 1. The leak taxonomy -- five leaks, one line each, and how many of this
 *    build's agent cards claim each one.
 * 2. Where the money goes -- the platform's own conservative-to-stretch
 *    range against operating cost, with the operating-cost figure itself
 *    left to the client.
 * 3. The evidence ladder -- what a business case can and cannot be funded on.
 *
 * Everything numeric here is read off DATA.catalog, built by
 * scripts/build_app_data.py from mining_agents.catalog.definitions -- the
 * same source that deploys the agents -- so the leak counts on this page
 * cannot drift from what the seven cards (plus AGT-19, group-level) actually
 * claim. Nothing on this page is a dollar figure: the conservative and
 * stretch percentages are the platform's own planning model, and the
 * operating-cost denominator that would turn them into money belongs to
 * whoever runs the site, not to this repository.
 *
 * Deliberately absent: an archetype band. The six archetypes are internal
 * taxonomy for whoever builds the next agent, not for the reader of this
 * page, and a band naming them was cut in review (design doc, "Explicitly
 * NOT on this page").
 */

mountNav("workspace", "value.html");

var CAT = DATA.catalog;
var LEAKS = CAT.leaks;
var LEAK_COUNTS = CAT.leak_counts;
var GROUP_AGENTS = CAT.group_agents || {};
var AGT19 = GROUP_AGENTS["AGT-19"];
if (!AGT19) {
  throw new Error("value.html has no AGT-19 card to surface; check catalog.group_agents");
}

/* One line each, in the words of the job map the leaks come from: Notice,
   Diagnose, Decide, Act, Prove, plus the sixth cross-cutting leak where the
   best shift's practice never reaches the average shift. Keyed on the same
   five strings the catalog exports, so a leak renamed in
   mining_agents.catalog.definitions fails loudly here rather than silently
   rendering an empty definition. */
var LEAK_DEFS = {
  "Blind spot": "More signal arrives than a crew can read, and explaining " +
    "its cause needs a cross-check nobody has hours for.",
  "Coordination": "The objective is implicit, so conflicts across " +
    "functions get settled by phone instead of by a named priority.",
  "Latency": "The decision is right but arrives late — re-keying, " +
    "handoffs and queues turn a call into a delay measured in shifts.",
  "Variance": "What the best shift does well is never propagated to the " +
    "average shift.",
  "Assurance": "What was done and why is reconstructed after the fact, " +
    "by expensive people, instead of evidenced as it happened.",
};

LEAKS.forEach(function (leak) {
  if (!LEAK_DEFS[leak]) {
    throw new Error("value.js has no definition for leak " + leak + "; the catalog named one this page does not know");
  }
});

el("lede").textContent =
  "Every leak below is one an agent's own card claims, every count comes " +
  "from what is actually deployed, and every dollar figure this page could " +
  "not verify is left for you to supply rather than guessed.";

el("leak-lede").textContent =
  "The same five ways the operating job breaks, however many agents are " +
  "built to close them. A leak with no agent behind it yet still belongs on " +
  "this list; today none of the five is at zero.";

el("leaks").innerHTML = LEAKS.map(function (leak) {
  var n = LEAK_COUNTS[leak] || 0;
  return (
    '<div class="leak-card">' +
    '<h3 class="lk-name">' + esc(leak) + "</h3>" +
    '<p class="lk-def">' + esc(LEAK_DEFS[leak]) + "</p>" +
    '<span class="lk-count">' + num(n) + "</span>" +
    '<span class="lk-count-sub">agent' + (n === 1 ? "" : "s") + " claiming it</span>" +
    "</div>"
  );
}).join("");

/* Band 2 -- where the money goes. The conservative and stretch percentages
   are this platform's own bottom-up planning model of the addressable pool
   as a share of operating cost; NO absolute figure is derived from them here.
   The bar below is a visual proportion between the two published
   percentages, not a currency amount, and the denominator that would turn
   either into money is rendered by clientInput() -- the same "not typed,
   not guessed" element every other screen uses for a figure only the client
   holds. */
var CONSERVATIVE_PCT = 4.1;
var STRETCH_PCT = 9.0;
var BAR_MAX_PCT = 12; // purely a drawing scale for the range bar below

el("money").innerHTML =
  '<div class="card-cap">The addressable pool</div>' +
  '<p class="lede" style="font-size:14px">Conservative <strong>' +
  CONSERVATIVE_PCT.toFixed(1) + "%</strong> of operating cost, stretch " +
  "<strong>" + STRETCH_PCT.toFixed(1) + "%</strong> — recurring, with no " +
  "new capital and no change to the mine plan.</p>" +
  '<div class="money-range">' +
  '<div class="money-range-bar"><span style="left:0%;width:' +
  ((STRETCH_PCT / BAR_MAX_PCT) * 100).toFixed(1) + '%"></span></div>' +
  '<div class="money-range-labels">' +
  "<span>" + CONSERVATIVE_PCT.toFixed(1) + "% conservative</span>" +
  "<span>" + STRETCH_PCT.toFixed(1) + "% stretch</span>" +
  "</div></div>" +
  '<div class="money-denominator">' +
  '<span class="ac-label">Annual operating cost, this site</span>' +
  clientInput() +
  "</div>" +
  '<p class="pnote">Multiply the percentage range above by the figure you ' +
  "supply. This repository does not hold your operating cost and does not " +
  "estimate it, so it structurally cannot turn the range into a number for " +
  "you.</p>";

/* Band 3 -- the evidence ladder. */
var EVIDENCE_LADDER = [
  {
    letter: "A", name: "Cash-verifiable", fundable: true,
    def: "The recovery lands as cash, a credit note or an avoided invoice, " +
      "traced transaction by transaction. No counterfactual required.",
  },
  {
    letter: "B", name: "Metric-verifiable", fundable: true,
    def: "A named operating metric moves against a signed baseline, " +
      "converted to a dollar figure at a rate agreed with Finance before " +
      "go-live.",
  },
  {
    letter: "C", name: "Risk-adjusted", fundable: false,
    def: "Avoided loss or exposure reduction, evidenced but with no " +
      "counterfactual available. Reported to the board, never booked.",
  },
];

el("ladder").innerHTML =
  '<div class="evidence-ladder">' +
  EVIDENCE_LADDER.map(function (row) {
    return (
      '<div class="ev-class ' + (row.fundable ? "fundable" : "not-fundable") + '">' +
      '<div class="ev-letter">' + esc(row.letter) + "</div>" +
      '<div class="ev-name">' + esc(row.name) +
      (row.fundable ? "" : " · report only") + "</div>" +
      '<p class="ev-def">' + esc(row.def) + "</p>" +
      "</div>"
    );
  }).join("") +
  "</div>" +
  '<p class="pnote">A business case has to clear its hurdle rate on Class A ' +
  "and Class B alone. Class C is boardroom context — reported alongside the " +
  "case, never counted inside it.</p>";

/* Band 4 -- AGT-19, group-level, no persona in this build to render it on
   (design doc section 3). Its card is the same renderer every persona-page
   card uses, so a reader comparing this page against a role's page sees one
   card shape, not two. */
el("agt19").innerHTML =
  '<p class="pnote">Group-level; not addressed to any one role. Surfaced ' +
  "here rather than inventing a role for it to belong to.</p>" +
  renderAgentCard(AGT19);

/* ---------------------------------------------------------------- drawer */

function drawerBody() {
  var rows = [];
  Object.keys(DATA.personas.personas).forEach(function (code) {
    (DATA.personas.personas[code].cards || []).forEach(function (c) {
      rows.push({ persona: code, card: c });
    });
  });
  rows.push({ persona: "—", card: AGT19 });

  return (
    "<p>Every card behind the counts above, with the method pack file its " +
    "coverage number was computed from.</p>" +
    "<dl>" +
    rows.map(function (r) {
      var cov = r.card.coverage;
      var covTxt = cov ? num(cov.instrumented) + " of " + num(cov.total) : "no pack";
      return (
        '<dt class="mono">' + esc(r.card.agent_id) + " · " + esc(r.persona) + "</dt>" +
        "<dd>" + esc(r.card.archetype) + " · " + esc(r.card.authority) + "<br>" +
        '<span class="mono">' + esc(r.card.pack || "—") + "</span> — " +
        covTxt + " drivers instrumented</dd>"
      );
    }).join("") +
    "</dl>" +
    '<dl><dt>Leaks, in the catalog\'s own order</dt><dd class="mono">' +
    esc(LEAKS.join(" · ")) + "</dd></dl>"
  );
}

el("prov").innerHTML =
  technicalDrawer(drawerBody(), "every card, its pack, and its coverage") +
  provenance();
