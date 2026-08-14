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
