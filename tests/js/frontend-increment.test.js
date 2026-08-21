/* Guards on the increment that added persona portraits, agent launch links,
 * business logic + decision flow on the deep dive, and the Screen 5 logical
 * and data architecture.
 *
 * These read the generated and hand-authored data files directly rather than
 * booting the page: the failures worth catching here are data failures --
 * an agent with no invoke URL, a chip token nothing substitutes, a graph edge
 * pointing at a table that is not in the graph -- and each of those renders as
 * a plausible-looking screen rather than an error.
 */
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const FRONTEND = path.join(__dirname, "..", "..", "apps", "frontend");

function loadFrontendGlobals() {
  const sandbox = { window: {}, document: undefined };
  vm.createContext(sandbox);
  for (const file of ["data.js", "data-static.js", "data-graph.js"]) {
    vm.runInContext(fs.readFileSync(path.join(FRONTEND, file), "utf8"), sandbox, { filename: file });
  }
  return sandbox.window;
}

const W = loadFrontendGlobals();
const AGENTS = Object.values(W.agentCatalogData);
const read = (f) => fs.readFileSync(path.join(FRONTEND, f), "utf8");

/* -------------------------------------------------- agent launch links -- */

test("every agent carries both a workspace link and its own invoke endpoint", () => {
  assert.equal(AGENTS.length, 101);
  for (const a of AGENTS) {
    assert.ok(/^https:\/\//.test(a.geminiUrl), `${a.id} has no Gemini Enterprise URL`);
    assert.ok(/^https:\/\//.test(a.invokeUrl), `${a.id} has no invoke URL`);
  }
});

test("the invoke URL addresses the agent it sits on, and the workspace URL does not", () => {
  // The whole reason both links exist: one is per-agent, one is shared. If the
  // invoke URL ever stopped carrying the agent's own id, the launch button
  // would quietly become a second copy of the workspace button.
  for (const a of AGENTS) {
    assert.ok(a.invokeUrl.endsWith("/" + a.id.toLowerCase()),
      `${a.id} invoke URL does not end in its own id: ${a.invokeUrl}`);
  }
  const workspaces = new Set(AGENTS.map((a) => a.geminiUrl));
  assert.equal(workspaces.size, 1, "the Gemini Enterprise workspace should be one shared URL");
});

test("the deep dive states that the workspace link is shared, so nobody reads it as per-agent", () => {
  const app = read("app.js");
  assert.match(app, /Gemini Enterprise opens the shared workspace/);
});

/* ------------------------------------------------------ business logic -- */

const BIZ_KEYS = ["owns", "boardStake", "answersTo", "plMove", "cannot", "onFailure"];

test("every agent has a complete business-logic block", () => {
  for (const a of AGENTS) {
    assert.ok(a.business, `${a.id} has no business block`);
    for (const k of BIZ_KEYS) {
      assert.ok(a.business[k] && a.business[k].length > 15,
        `${a.id}.business.${k} is missing or too short to be a sentence`);
    }
  }
});

test("the business block reads as business language, not as enum values", () => {
  // A regression here means a lexicon lookup was replaced by a raw field and
  // the card is showing L2_BOUNDED_ACTION to a chief executive.
  for (const a of AGENTS) {
    for (const k of BIZ_KEYS) {
      assert.doesNotMatch(a.business[k], /[A-Z]{2,}_[A-Z]/,
        `${a.id}.business.${k} leaks a raw enum: ${a.business[k]}`);
    }
  }
});

test("what an agent cannot do always names the limit, never leaves it implied", () => {
  for (const a of AGENTS) {
    assert.match(a.business.cannot, /cannot|no write access|Recommends only/i,
      `${a.id} does not state a limit: ${a.business.cannot}`);
  }
});

/* ------------------------------------------------------- decision flow -- */

test("every agent has the same five-stage decision flow, in order", () => {
  const expected = ["trigger", "reads", "decides", "approval", "lands"];
  for (const a of AGENTS) {
    assert.deepEqual((a.flow || []).map((s) => s.key), expected, `${a.id} flow is wrong`);
    for (const stage of a.flow) {
      assert.ok(stage.value && stage.detail, `${a.id} stage ${stage.key} is incomplete`);
    }
  }
});

test("the flow's reads stage lists the tables the agent actually declares", () => {
  for (const a of AGENTS) {
    const reads = a.flow.find((s) => s.key === "reads");
    const declared = a.provenance.map((p) => p.name);
    assert.match(reads.value, new RegExp("^" + declared.length + " grounding table"),
      `${a.id} reads stage disagrees with its provenance count`);
    for (const t of declared) {
      assert.ok(reads.detail.includes(t), `${a.id} reads stage omits ${t}`);
    }
  }
});

test("an agent needing human release says so in both the approval and the landing stage", () => {
  for (const a of AGENTS) {
    const approval = a.flow.find((s) => s.key === "approval");
    const lands = a.flow.find((s) => s.key === "lands");
    if (a.hitl) {
      assert.match(approval.value, /Human release required/, `${a.id}`);
      assert.match(lands.value, /ERP staging buffer/, `${a.id}`);
    } else {
      assert.match(approval.value, /Advisory/, `${a.id}`);
    }
    assert.match(lands.detail, /Never a PLC|Nothing reaches plant control/, `${a.id}`);
  }
});

/* --------------------------------------------------- persona portraits -- */

test("every persona has a portrait and no two personas share one", () => {
  const personas = Object.entries(W.personaPRDData);
  assert.equal(personas.length, 8);
  const seen = new Map();
  for (const [key, p] of personas) {
    assert.ok(p.avatar && /^https:\/\//.test(p.avatar), `${key} has no portrait`);
    assert.ok(!seen.has(p.avatar), `${key} reuses ${seen.get(p.avatar)}'s portrait`);
    seen.set(p.avatar, key);
  }
});

test("the portrait has an initials fallback behind it, because it loads from a remote host", () => {
  assert.match(read("index.html"), /id="persona-hero-initials"/);
  assert.match(read("app.css"), /\.persona-avatar-fallback/);
});

/* ------------------------------------------- Screen 5: logical stack ---- */

test("the architecture runs the whole way from the screen to the source", () => {
  const keys = W.architectureModel.layers.map((l) => l.key);
  assert.equal(keys[0], "experience", "the stack must start where a person is");
  assert.equal(keys[keys.length - 1], "sources", "the stack must end at the data's origin");
  assert.ok(keys.includes("platform"), "the data platform layer is missing");
});

test("every layer declares both directions of traffic", () => {
  for (const l of W.architectureModel.layers) {
    assert.ok(l.request && l.evidence, `${l.key} does not say what travels through it`);
    assert.ok(l.chips.length > 0, `${l.key} has no chips`);
  }
});

test("every chip token has something to substitute it", () => {
  // An unsubstituted {token} renders its own braces onto a customer-facing
  // screen. The renderer's token set is the contract; this is the check that
  // the content and the renderer still agree.
  const supplied = new Set(
    (read("app.js").match(/^\s{8}(\w+):/gm) || []).map((m) => m.trim().replace(":", ""))
  );
  for (const l of W.architectureModel.layers) {
    for (const chip of l.chips) {
      for (const m of chip.matchAll(/\{(\w+)\}/g)) {
        assert.ok(supplied.has(m[1]), `chip token {${m[1]}} on layer ${l.key} has no source`);
      }
    }
  }
});

test("the controls are cross-cutting, and the OT boundary is one of them", () => {
  const controls = W.architectureModel.controls;
  assert.ok(controls.length >= 4);
  const boundary = controls.find((c) => c.key === "boundary");
  assert.ok(boundary, "the OT boundary is not declared as a control");
  assert.match(boundary.rule, /no agent holds write access/i);
  for (const c of controls) {
    assert.match(c.spans, /→/, `${c.key} does not say which layers it spans`);
  }
});

test("Screen 5 no longer carries the retired governance blocks", () => {
  const html = read("index.html");
  for (const dead of ["gov-stack-steps", "gov-staging-steps", "gov-provenance-steps"]) {
    assert.ok(!html.includes(dead), `${dead} survived the Screen 5 rewrite`);
  }
  assert.match(html, /id="arch-stack"/);
  assert.match(html, /id="datagraph-svg"/);
});

/* -------------------------------------------- Screen 5: data graph ------ */

test("the graph is built from the real dataset, not an illustration", () => {
  const m = W.dataGraph.meta;
  assert.equal(m.dataset, "mining_data");
  assert.ok(m.tableCount > 30, "too few tables to be the real dataset");
  assert.equal(m.tableCount, W.dataGraph.nodes.length);
  assert.equal(m.edgeCount, W.dataGraph.edges.length);
});

test("snapshot and probe copies are excluded and counted, never silently dropped", () => {
  const ids = W.dataGraph.nodes.map((n) => n.id);
  for (const id of ids) {
    assert.doesNotMatch(id, /_original_\d{8}$/, `${id} is a snapshot copy`);
    assert.doesNotMatch(id, /_probe$/, `${id} is a probe table`);
  }
  assert.ok(W.dataGraph.meta.excludedCount > 0);
  assert.equal(W.dataGraph.meta.excluded.length, W.dataGraph.meta.excludedCount);
});

test("every edge joins two tables that are in the graph", () => {
  const ids = new Set(W.dataGraph.nodes.map((n) => n.id));
  for (const e of W.dataGraph.edges) {
    assert.ok(ids.has(e.source), `edge references missing table ${e.source}`);
    assert.ok(ids.has(e.target), `edge references missing table ${e.target}`);
    assert.ok(e.keys.length > 0, `${e.source}->${e.target} has no join key`);
  }
});

test("every node carries the columns and counts the detail panel reads", () => {
  for (const n of W.dataGraph.nodes) {
    assert.equal(n.columns.length, n.columnCount, `${n.id} column count disagrees with its columns`);
    assert.ok(typeof n.rows === "number", `${n.id} has no row count`);
    assert.ok(n.layerLabel && n.domainLabel, `${n.id} is unclassified`);
    assert.ok(Array.isArray(n.readBy), `${n.id} has no readBy list`);
  }
});

test("every layer and domain the chrome offers has at least one table behind it", () => {
  const layers = new Set(W.dataGraph.nodes.map((n) => n.layer));
  const domains = new Set(W.dataGraph.nodes.map((n) => n.domain));
  for (const l of W.dataGraph.layers) assert.ok(layers.has(l.key), `layer ${l.key} has no tables`);
  for (const d of W.dataGraph.domains) assert.ok(domains.has(d.key), `domain ${d.key} has no tables`);
});

test("at least one table records which agents declare it", () => {
  // A generator that silently failed to import the catalogue produced a graph
  // where nothing was read by anything, which looked fine on screen.
  const withReaders = W.dataGraph.nodes.filter((n) => n.readBy.length > 0);
  assert.ok(withReaders.length > 0, "no table names a single agent that reads it");
});

/* ------------------------------------------------- interaction guards --- */

test("a press only becomes a drag after travelling, so a click can still inspect", () => {
  // Without the threshold the drag handler captured the pointer and the click
  // landed on the canvas, deselecting instead of opening the table.
  const app = read("app.js");
  assert.match(app, /DRAG_THRESHOLD/);
  assert.match(app, /if \(pending && !dragging\)/);
});

test("a deep dive asked for an unknown agent shows nothing rather than a stranger", () => {
  const app = read("app.js");
  assert.match(app, /var a = agentId \? all\[agentId\] : all\[ids\[0\]\];/);
});

test("squad members the registry does not hold are labelled, not linked", () => {
  // Two personas name L1 arbiters that are not registered agents. A launch
  // link on those cards would point at an endpoint that does not exist.
  const app = read("app.js");
  assert.match(app, /Not in the agent registry/);
  const squadIds = Object.values(W.personaPRDData).flatMap((p) => p.squad.map((s) => s.id));
  const unregistered = squadIds.filter((id) => !W.agentCatalogData[id]);
  assert.ok(unregistered.length > 0,
    "no unregistered squad member left -- if the registry gained them, drop this guard");
});
