/* apps/workspace/value.html -- rendered the way a browser runs it, via
 * tests/js/screen-render.js, so these tests see what the reader sees rather
 * than what the source merely contains.
 */
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

const { renderScreen } = require("./screen-render.js");

const ROOT = path.join(__dirname, "..", "..");

function bundle() {
  const file = path.join(ROOT, "apps", "shared", "data", "bundle.js");
  const text = fs.readFileSync(file, "utf8");
  return JSON.parse(text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1));
}

const DATA = bundle();

async function renderedHtml() {
  const draw = renderScreen("apps/workspace/value.html");
  for (let i = 0; i < 5; i += 1) await new Promise((r) => setImmediate(r));
  return draw();
}

test("the page's leak counts equal the catalog's, so page and build cannot disagree", async () => {
  const html = await renderedHtml();
  for (const leak of DATA.catalog.leaks) {
    const count = DATA.catalog.leak_counts[leak];
    const re = new RegExp(
      `<span class="lk-count">${count}</span>\\s*<span class="lk-count-sub">agent`
    );
    assert.match(html, re, `${leak}'s count on the page does not read ${count}`);
  }
});

test("every leak named on the page is one of the catalog's five, and all five appear", async () => {
  const html = await renderedHtml();
  const named = [...html.matchAll(/<h3 class="lk-name">([^<]+)<\/h3>/g)].map((m) => m[1]);
  assert.deepEqual(named.sort(), [...DATA.catalog.leaks].sort());
});

// The structural guarantee the whole band rests on: none of the five leaks is
// claimed by zero agents. If this regresses, the page would render a leak
// card with a count of 0, which is a silent claim that nothing in the build
// addresses it.
test("no leak on the page reads a count of zero", async () => {
  const html = await renderedHtml();
  for (const leak of DATA.catalog.leaks) {
    assert.ok(DATA.catalog.leak_counts[leak] > 0, `${leak} has no agent behind it`);
  }
  assert.ok(!/<span class="lk-count">0<\/span>/.test(html), "a leak card reads a count of zero");
});

// No absolute currency figure may appear anywhere on this page (design §1,
// band 2). Regex for a currency symbol immediately followed by a digit --
// the shape a typed-in dollar amount takes, and the shape the range/percent
// figures on this page never take.
test("no currency figure appears anywhere on the rendered page", async () => {
  const html = await renderedHtml();
  assert.ok(
    !/[$€£]\s?\d/.test(html),
    "a currency symbol followed by a digit reached the rendered page"
  );
});

test("the addressable pool is stated as a percentage range, not a dollar amount", async () => {
  const html = await renderedHtml();
  assert.match(html, /4\.1%/, "the conservative percentage is missing");
  assert.match(html, /9\.0%/, "the stretch percentage is missing");
  assert.match(html, /CLIENT.{0,20}INPUT.{0,20}REQUIRED/s, "the opex denominator is not marked client-supplied");
});

test("the evidence ladder states all three classes and the funding rule", async () => {
  const html = await renderedHtml();
  ["Cash-verifiable", "Metric-verifiable", "Risk-adjusted"].forEach((name) =>
    assert.ok(html.includes(name), `${name} is missing from the ladder`)
  );
  assert.match(html, /Class A/);
  assert.match(html, /Class B/);
  assert.match(html, /Class C/);
  assert.match(html, /never.{0,20}booked|hurdle rate/i, "the funding rule is not stated");
});

// AGT-19's pack is under active instrumentation by a parallel workstream
// while this suite runs, so its exact coverage is not pinned here -- only
// that the number on the page is the number the export computed, whatever it
// currently is. The "0 renders visibly" guarantee itself is proved against a
// synthetic card in tests/js/agent-card.test.js and
// tests/js/persona-panel.test.js, decoupled from any one pack's progress.
test("AGT-19's card is surfaced with its computed coverage", async () => {
  const html = await renderedHtml();
  const agt19 = DATA.catalog.group_agents["AGT-19"];
  assert.ok(html.includes("AGT-19"), "AGT-19 is not named on the page");
  assert.match(
    html,
    new RegExp(`${agt19.coverage.instrumented} of ${agt19.coverage.total} drivers instrumented`),
    "AGT-19's card does not show the coverage the export computed"
  );
});

test("there is deliberately no archetype band on this page", async () => {
  // The design doc is explicit that the archetype taxonomy was cut from this
  // screen. It still appears once, inside an agent card's own "Archetype"
  // row (design §2) -- what must not exist is a section presenting the six
  // archetypes as a taxonomy of their own.
  const html = await renderedHtml();
  assert.ok(
    !/archetype taxonomy|the six archetypes/i.test(html),
    "an archetype band reached the value page"
  );
});

test("the drawer is the only collapsible on the page", async () => {
  const html = await renderedHtml();
  const details = [...html.matchAll(/<details\b[^>]*>/g)];
  assert.equal(details.length, 1, `expected exactly one <details>, found ${details.length}`);
  assert.match(html, /Technical detail/);
});
