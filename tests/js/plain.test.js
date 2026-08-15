const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

const P = require("../../apps/shared/plain.js");

// The bundle is a browser file: `window.MINING_DATA = {...};`. Node has no
// window, so the object is cut out and parsed rather than required.
function loadData() {
  const file = path.join(__dirname, "..", "..", "apps", "shared", "data", "bundle.js");
  const text = fs.readFileSync(file, "utf8");
  return JSON.parse(text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1));
}

test("bareTable strips the dataset prefix and backticks", () => {
  assert.equal(P.bareTable("mining_data.telemetry_stream"), "telemetry_stream");
  assert.equal(P.bareTable("`mining_data.telemetry_stream`"), "telemetry_stream");
  assert.equal(P.bareTable("telemetry_stream"), "telemetry_stream");
});

test("the map covers every tool, traversal and table in the catalogue", () => {
  const missing = P.unmapped(loadData());
  assert.deepEqual(missing, { tables: [], tools: [], traversals: [] });
});

test("a bq_query naming a table composes verb plus noun", () => {
  const line = P.callLine("bq_query", {
    sql: "SELECT * FROM `mining_data.telemetry_stream` LIMIT 10",
  });
  assert.equal(line, "Reading the sensor readings");
});

test("a graph_traverse names the traversal it runs", () => {
  assert.equal(
    P.callLine("graph_traverse", { traversal: "blast_radius" }),
    "Tracing what else stops if this stops"
  );
});

test("a call with no recognisable noun degrades to the tool verb alone", () => {
  assert.equal(P.callLine("operational_math", { expression: "1+1" }),
    "Working out the numbers");
  assert.equal(P.callLine("bq_query", {}), "Looking up records");
});

test("an unknown id renders its raw value rather than a guess", () => {
  assert.equal(P.plainTable("no_such_table"), "no_such_table");
  assert.equal(P.plainTool("no_such_tool"), "no_such_tool");
  assert.equal(P.plainTraversal("no_such_traversal"), "no_such_traversal");
  assert.equal(P.callLine("no_such_tool", {}), "no_such_tool");
});

test("a failed response names what failed", () => {
  assert.equal(
    P.failLine("graph_traverse", { traversal: "blast_radius" }),
    "Couldn't trace what else stops if this stops — that lookup failed."
  );
  assert.equal(
    P.failLine("bq_query", { sql: "SELECT 1 FROM `mining_data.assets`" }),
    "Couldn't read the machine register — that lookup failed."
  );
});

test("failLine bq_query on a non-articled table still carries the article", () => {
  assert.equal(
    P.failLine("bq_query", { sql: "SELECT * FROM `mining_data.telemetry_stream` LIMIT 10" }),
    "Couldn't read the sensor readings — that lookup failed."
  );
});

test("callLine bq_query on an articled table does not double the article", () => {
  assert.equal(
    P.callLine("bq_query", { sql: "SELECT * FROM `mining_data.assets` LIMIT 10" }),
    "Reading the machine register"
  );
});

test("a table phrase that is a relative clause is framed without an article", () => {
  // "Reading the which parts each supplier quoted" is not English. Five of the
  // twenty-five table phrases are clauses, not noun phrases.
  assert.equal(P.articleFor("machine register"), "the ");
  assert.equal(P.articleFor("which parts each supplier quoted"), "");
  assert.equal(P.articleFor("who was involved in each incident"), "");
  assert.equal(
    P.callLine("bq_query", { sql: "SELECT * FROM `mining_data.bid_parts_edge`" }),
    "Reading which parts each supplier quoted"
  );
  assert.equal(
    P.failLine("bq_query", { sql: "SELECT * FROM `mining_data.incident_involvements`" }),
    "Couldn't read who was involved in each incident — that lookup failed."
  );
});

test("every tool has a bare-verb phrase for the ability frame", () => {
  for (const id of Object.keys(P.TOOLS)) {
    assert.notEqual(P.TOOL_ABILITY[id], undefined, `${id} has no ability phrase`);
    assert.equal(P.plainToolAbility(id), P.TOOL_ABILITY[id]);
  }
  assert.equal(P.plainToolAbility("no_such_tool"), "no_such_tool");
});

test("tableFromSql finds the first qualified table and nothing else", () => {
  assert.equal(
    P.tableFromSql("SELECT a FROM `mining_data.assets` JOIN `mining_data.maintenance_logs`"),
    "assets"
  );
  assert.equal(P.tableFromSql("SELECT 1"), "");
  assert.equal(P.tableFromSql(undefined), "");
});

test("jargon substitutions are available to the copy rewrite", () => {
  assert.equal(P.plainJargon("entrypoint"), "agent you can talk to");
  assert.equal(P.plainJargon("blast radius"), "what else stops");
  assert.equal(P.plainJargon("not a jargon term"), "not a jargon term");
});

/* The screens do not write all of their own copy. Three of them print a
 * persona's accountable_for straight out of the catalogue, and that prose was
 * written by the people who built the estate, in their words: "must approve or
 * decline HITL prompts from D37 and S11". A de-jargoning pass that rewrites
 * every sentence a screen composes and prints that one untouched has not
 * finished. */
test("the prose the catalogue supplies is said in the reader's words too", () => {
  const said = P.plainProse(
    "The HSE Lead must approve or decline HITL prompts from D37 and S11."
  );
  assert.equal(
    said,
    "The HSE Lead must approve or decline sign-off requests from D37 and S11."
  );
  assert.equal(
    P.plainProse("is also the HITL approver for crusher setpoint changes"),
    "is also the sign-off authority for crusher setpoint changes"
  );
  assert.equal(P.plainProse(""), "");
  assert.equal(P.plainProse(undefined), "");
});

/* The graph screen prints three lines the build wrote — "All 5 assets and all 3
 * dependency edges. Nothing filtered." — on the one screen whose whole subject
 * is edges and nodes. The rewriter that was supposed to fix them knew the word
 * "traversal" and neither of the other two, so it ran over every line and
 * changed nothing on any of them. */
test("plainScope says the three structural words in the reader's terms", () => {
  assert.equal(
    P.plainScope("All 5 assets and all 3 dependency edges. Nothing filtered."),
    "All 5 assets and all 3 dependency links. Nothing filtered."
  );
  assert.equal(
    P.plainScope("The traversal returns one row per node it reaches."),
    "The connection trace returns one row per machine it reaches."
  );
  // A leading capital belongs to the sentence, not to the word, so it survives.
  assert.equal(P.plainScope("Edges only."), "Links only.");
  assert.equal(P.plainScope(""), "");
  assert.equal(P.plainScope(undefined), "");
});

test("plainScope substitutes, and never quietly drops", () => {
  // Same shape as the prose test below: strike the jargon out of the original
  // and its replacement out of the rewrite, and the remainders must be
  // identical. A rewriter that deleted the sentence would satisfy "no edges
  // left" and fail here.
  const lines = Object.values(loadData().graph.graphs).map((g) => g.scope);
  assert.ok(lines.length >= 3, "the graph export no longer carries scope lines");
  const terms = [
    ["traversals?", "connection traces?"],
    ["edges?", "links?"],
    ["nodes?", "machines?"],
  ];
  for (const before of lines) {
    const after = P.plainScope(before);
    assert.ok(
      !/\b(traversals?|edges?|nodes?)\b/i.test(after),
      `still the build's words: ${after}`
    );
    const strip = (text) =>
      terms
        .reduce((t, [jargon, plain]) => t.replace(new RegExp(`\\b(${jargon}|${plain})\\b`, "gi"), ""), text)
        .replace(/\s+/g, " ")
        .trim();
    assert.equal(strip(after), strip(before), `text lost rewriting: ${before}`);
  }
});

/* plainType and plainLink are what stop "FatigueLog" and "REPLACED_PART"
 * reaching a reader who opened this screen to avoid exactly that. They are here
 * rather than in graph.js because the estate has one vocabulary, and a second
 * copy of it inside one screen is a copy free to drift. */
test("every record type and link the graph draws has a plain name", () => {
  const graphs = loadData().graph.graphs;
  for (const [name, g] of Object.entries(graphs)) {
    for (const label of Object.keys(g.node_types)) {
      assert.notEqual(P.NODE_TYPES[label], undefined, `${name}: ${label} unnamed`);
      assert.equal(P.plainType(label), P.NODE_TYPES[label]);
      assert.ok(!/[A-Z_]/.test(P.plainType(label)), `${name}: ${label} still reads as a label`);
    }
    for (const label of Object.keys(g.edge_labels)) {
      assert.notEqual(P.LINK_LABELS[label], undefined, `${name}: ${label} unnamed`);
      assert.equal(P.plainLink(label), P.LINK_LABELS[label]);
      assert.ok(!/[A-Z_]/.test(P.plainLink(label)), `${name}: ${label} still reads as a label`);
    }
  }
});

test("an unnamed record type or link renders its raw label rather than nothing", () => {
  // Blank is worse than the label: an empty cell in the estate table reads as
  // "this graph has no such records", which is a false statement about the mine.
  assert.equal(P.plainType("NoSuchLabel"), "NoSuchLabel");
  assert.equal(P.plainLink("NO_SUCH_EDGE"), "NO_SUCH_EDGE");
  assert.equal(P.plainType(undefined), "");
});

test("rewriting the catalogue's prose substitutes, and never quietly drops", () => {
  const data = loadData();
  const personas = data.personas.personas || data.personas;
  for (const [code, persona] of Object.entries(personas)) {
    const before = String(persona.accountable_for || "");
    const after = P.plainProse(before);
    assert.ok(!/\bHITL\b/i.test(after), `${code} still says HITL: ${after}`);
    // Substitution, not deletion: strike the jargon out of the original and the
    // replacement out of the rewrite, and what is left has to be identical. A
    // rewriter that dropped the clause would pass the check above and fail this
    // one, which is the failure worth having.
    const strip = (text) =>
      text
        .replace(/HITL prompts?/gi, "")
        .replace(/HITL approver/gi, "")
        .replace(/sign-off requests?/gi, "")
        .replace(/sign-off authority/gi, "")
        .replace(/\s+/g, " ")
        .trim();
    assert.equal(strip(after), strip(before), `${code} lost text in the rewrite`);
  }
});
