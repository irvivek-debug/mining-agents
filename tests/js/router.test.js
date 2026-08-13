const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

const R = require("../../apps/workspace/router.js");

function loadData() {
  const file = path.join(__dirname, "..", "..", "apps", "shared", "data", "bundle.js");
  const text = fs.readFileSync(file, "utf8");
  return JSON.parse(text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1));
}

const DATA = loadData();
const CODES = Object.keys(DATA.personas.personas).sort();

test("there are eight personas, so the table-driven tests below cover them all", () => {
  assert.deepEqual(CODES, ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]);
});

test("branchesOf normalises a bare string and a list alike", () => {
  assert.deepEqual(R.branchesOf("asset_reliability"), ["asset_reliability"]);
  assert.deepEqual(R.branchesOf(["supply_chain", "procurement"]),
    ["supply_chain", "procurement"]);
  assert.deepEqual(R.branchesOf(undefined), []);
});

test("every persona's routing stays inside that persona's own agents", () => {
  const questions = [
    "Which assets are most at risk right now?",
    "What runs out if this part runs out?",
    "Show me crew fatigue against incidents",
    "How is recovery tracking against the ordinary day?",
    "What should I sign off before the shift ends?",
  ];
  for (const code of CODES) {
    const allowed = new Set(DATA.personas.personas[code].agents);
    for (const q of questions) {
      const pick = R.route(q, code, DATA);
      assert.ok(allowed.has(pick.agent_id),
        `${code} routed "${q}" to ${pick.agent_id}, which is not one of its agents`);
      assert.ok(pick.reason.length > 0, `${code} gave no reason for "${q}"`);
      for (const up of pick.runners_up) {
        assert.ok(allowed.has(up.agent_id));
        assert.notEqual(up.agent_id, pick.agent_id);
      }
    }
  }
});

test("P8 has one agent, so it names it and offers nothing to change to", () => {
  assert.deepEqual(DATA.personas.personas.P8.agents, ["S12"]);
  const pick = R.route("What happened on the last shift?", "P8", DATA);
  assert.equal(pick.agent_id, "S12");
  assert.ok(pick.reason.length > 0);
  assert.deepEqual(pick.runners_up, []);
});

test("P4's list-valued value_branch does not throw", () => {
  assert.deepEqual(DATA.personas.personas.P4.value_branch,
    ["supply_chain", "procurement"]);
  const pick = R.route("Which suppliers quoted for this part?", "P4", DATA);
  assert.ok(DATA.personas.personas.P4.agents.includes(pick.agent_id));
});

test("a question of pure stop-words still returns a valid agent", () => {
  for (const code of CODES) {
    const pick = R.route("the and of a to is it", code, DATA);
    assert.ok(DATA.personas.personas[code].agents.includes(pick.agent_id));
    assert.ok(pick.reason.length > 0);
  }
});

test("an empty question returns a valid agent", () => {
  const pick = R.route("", "P1", DATA);
  assert.ok(DATA.personas.personas.P1.agents.includes(pick.agent_id));
});

test("identical inputs give identical output", () => {
  const a = R.route("Which assets are most at risk right now?", "P1", DATA);
  const b = R.route("Which assets are most at risk right now?", "P1", DATA);
  assert.deepEqual(a, b);
});

test("every persona gets exactly three starter questions", () => {
  for (const code of CODES) {
    const starters = R.starterQuestions(code, DATA);
    assert.equal(starters.length, 3, `${code} produced ${starters.length}`);
    assert.equal(new Set(starters).size, 3, `${code} repeated a starter`);
    for (const q of starters) assert.ok(q.trim().length > 0);
  }
});

test("a starter always routes to the agent it was derived from", () => {
  for (const code of CODES) {
    const items = R._starterItems(code, DATA);
    for (const item of items) {
      const pick = R.route(item.q, code, DATA);
      assert.ok(DATA.personas.personas[code].agents.includes(pick.agent_id),
        `${code}: starter "${item.q}" routed outside the persona`);
      if (!item.isGeneric) {
        // The core guarantee: the starter must route to the exact agent it was
        // derived from, not merely any agent in the persona.
        assert.strictEqual(pick.agent_id, item.agent.agent_id,
          `${code}: starter "${item.q}" was derived from ${item.agent.agent_id} ` +
          `but routed to ${pick.agent_id}`);
      }
    }
  }
});

test("a starter never names a capability its agent does not have", () => {
  const P = require("../../apps/shared/plain.js");
  const phrases = Object.values(P.TABLES)
    .concat(Object.values(P.TRAVERSALS))
    .concat(Object.values(P.TOOLS));
  for (const code of CODES) {
    const items = R._starterItems(code, DATA);
    for (const item of items) {
      if (item.isGeneric) {
        // Generic backstops name no capability by construction — assert that
        // explicitly rather than passing vacuously through the phrase loop.
        for (const phrase of phrases) {
          assert.ok(!item.q.toLowerCase().includes(phrase.toLowerCase()),
            `${code}: generic starter "${item.q}" contains capability phrase "${phrase}"`);
        }
        continue;
      }
      const pick = R.route(item.q, code, DATA);
      const agent = DATA.catalog.agents.find((a) => a.agent_id === pick.agent_id);
      const owned = new Set(
        (agent.source_tables || []).map((t) => P.plainTable(t))
          .concat((agent.traversals || []).map((t) => P.plainTraversal(t)))
          .concat((agent.tools || []).map((t) => P.plainTool(t)))
      );
      for (const phrase of phrases) {
        if (item.q.toLowerCase().includes(phrase.toLowerCase())) {
          assert.ok(owned.has(phrase),
            `${code}: starter "${item.q}" names "${phrase}", which ${pick.agent_id} does not have`);
        }
      }
    }
  }
});
