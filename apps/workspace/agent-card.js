/* One agent's business-framing card: the decision it owns, the leak(s) it
 * closes, its archetype and authority, the financial line(s) it can move and
 * at what evidence class, how much of its method pack is actually
 * instrumented, and its own honest limit.
 *
 * Shared between the persona page (one card per agent that carries one,
 * rendered beneath the role's governing question) and the value page (AGT-19's
 * card, which has no persona to render it on). One renderer, so the two
 * screens cannot draw the same field two different ways -- see design doc
 * docs/superpowers/specs/2026-08-17-value-framing-and-agent-cards-design.md
 * section 2.
 *
 * AUTHORITY IS DECLARED, NOT ENFORCED. See AgentCard's own docstring in
 * mining_agents/catalog/definitions.py. Every card says so in words next to
 * the authority line, not as a footnote a reader can miss: the failure mode
 * this guards against is a reader assuming the platform stops an agent at its
 * stated level, and it does not -- there is no authority engine in this build.
 *
 * COVERAGE MUST READ AS WHAT IT IS. A card at 0 of N drivers instrumented
 * renders the same row, in the same place, as a card at 5 of 7 -- never
 * blank, never styled as a fault. That is the distinction
 * mining_agents/tools/run_diagnostic.py already draws for a single
 * not_instrumented driver ("a SUCCESSFUL call, not a failure"); this is the
 * same distinction at the level of a whole pack.
 */
if (typeof require !== "undefined" && typeof window === "undefined") {
  Object.assign(globalThis, require("../shared/shell.js"));
}

/** The share bar plus its own label, present whichever way the numbers fall.
 *
 *  A card with no pack at all (no `coverage` field) renders no coverage row —
 *  that is a different fact ("this agent has no method pack") from a pack that
 *  exists and instruments none of its drivers, which renders the row with
 *  "0 of N". The two must not collapse into the same blank.
 */
function _coverageRow(coverage) {
  if (!coverage) return "";
  var pct = coverage.total ? (coverage.instrumented / coverage.total) * 100 : 0;
  var zero = coverage.instrumented === 0;
  return (
    '<div class="ac-row ac-coverage">' +
    '<span class="ac-label">Coverage</span>' +
    '<div class="ac-coverage-body">' +
    '<div class="share-bar" role="img" aria-hidden="true">' +
    '<span style="width:' + pct.toFixed(1) + '%"></span></div>' +
    '<p class="ac-coverage-label' + (zero ? " ac-coverage-zero" : "") + '">' +
    num(coverage.instrumented) + " of " + num(coverage.total) +
    " drivers instrumented" +
    (zero
      ? " — every driver in this pack is declared, not instrumented; each " +
        "names the data it would need. This is a stated gap, not a fault."
      : "") +
    "</p></div></div>"
  );
}

function renderAgentCard(card) {
  var leaks = (card.leaks || [])
    .map(function (l) { return '<span class="badge b-info">' + esc(l) + "</span>"; })
    .join(" ");
  var lines = (card.financial_lines || [])
    .map(function (fl) {
      return (
        "<li>" + esc(fl.line) +
        ' <span class="badge b-idle">Class ' + esc(fl.evidence_class) + "</span></li>"
      );
    })
    .join("");
  return (
    '<div class="agent-card">' +
    '<div class="ac-head">' +
    '<span class="ac-id mono">' + esc(card.agent_id) + "</span>" +
    '<span class="ac-name">' + esc(card.display_name) + "</span>" +
    "</div>" +
    '<p class="ac-decision">' + esc(card.decision) + "</p>" +
    '<div class="ac-row"><span class="ac-label">Leak' +
    ((card.leaks || []).length > 1 ? "s" : "") + "</span>" + leaks + "</div>" +
    '<div class="ac-row"><span class="ac-label">Archetype</span>' +
    "<span>" + esc(card.archetype) + "</span></div>" +
    '<div class="ac-row"><span class="ac-label">Authority</span>' +
    "<span>" + esc(card.authority) +
    // The caveat sits on every card, not once on the page, so a reader who
    // meets only one card still meets it.
    ' <span class="ac-caveat">— a label this card carries, not a limit the ' +
    "platform enforces</span></span></div>" +
    '<div class="ac-row ac-lines"><span class="ac-label">Financial line' +
    ((card.financial_lines || []).length > 1 ? "s" : "") + "</span>" +
    "<ul>" + lines + "</ul></div>" +
    _coverageRow(card.coverage) +
    '<p class="ac-limit"><span class="ac-label">Honest limit</span> ' +
    esc(card.honest_limit) + "</p>" +
    "</div>"
  );
}

if (typeof module !== "undefined") {
  module.exports = { renderAgentCard, _coverageRow };
}
