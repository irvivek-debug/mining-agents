/* One vocabulary, two consumers.
 *
 * The live activity log (chat.js) and the static copy (every screen) both name
 * the same machinery. A screen that calls graph_traverse "a connection trace"
 * while the stream calls it "a traversal" would be worse than either alone, so
 * both read this file.
 *
 * Nothing here guesses. An id absent from a map renders as itself, and
 * unmapped() exists so a test can prove the maps still cover the catalogue as
 * the catalogue grows.
 */

/* The noun phrase for a tool, used in prose. */
var TOOLS = {
  bq_query: "looking up records",
  bqml_predict: "running a prediction",
  graph_traverse: "tracing connections",
  operational_math: "working out the numbers",
  request_approval: "asking for your sign-off",
};

/* The present-participle headline for a tool, used in the activity log where a
 * line reads as something happening now. */
var TOOL_DOING = {
  bq_query: "Looking up records",
  bqml_predict: "Running a prediction",
  graph_traverse: "Tracing connections",
  operational_math: "Working out the numbers",
  request_approval: "Asking for your sign-off",
};

/* The bare-verb phrase for a tool, used after a modal — "It can look up
 * records". TOOLS is the gerund and reads wrong in that position. */
var TOOL_ABILITY = {
  bq_query: "look up records",
  bqml_predict: "run a prediction",
  graph_traverse: "trace connections",
  operational_math: "work out the numbers",
  request_approval: "ask for your sign-off",
};

/* The verb for the composed form, "Reading the sensor readings". Only the two
 * tools that take a noun need one. The article is not part of the verb: see
 * articleFor. */
var TOOL_VERB = { bq_query: "Reading", graph_traverse: "Tracing" };
var TOOL_FAILED = { bq_query: "Couldn't read", graph_traverse: "Couldn't trace" };

var TRAVERSALS = {
  blast_radius: "what else stops if this stops",
  fatigue_to_incident: "how crew fatigue connects to incidents",
  stockout_exposure: "what runs out if this part runs out",
};

var TABLES = {
  asset_dependencies: "which machines depend on which others",
  assets: "machine register",
  bid_parts_edge: "which parts each supplier quoted",
  biometric_fatigue_logs: "crew fatigue readings",
  crusher_states: "crusher run states",
  drill_assay_logs: "drill sample assays",
  drill_holes: "drill hole records",
  erp_work_orders: "work orders in the ERP",
  fatigue_logs_node: "crew fatigue records",
  fleet_vehicles: "truck and loader fleet",
  geological_block_models: "ore body block model",
  haulage_routes: "haul routes",
  incident_involvements: "who was involved in each incident",
  inventory_levels: "parts on hand",
  maintenance_logs: "maintenance history",
  metallurgical_recovery: "plant recovery records",
  operator_vehicle_assignments: "who drove what",
  operators_node: "operator roster",
  procurement_bids: "supplier bids",
  radio_communications: "radio traffic",
  rfp_items: "items out to tender",
  safety_incidents: "safety incidents",
  simulation_runs: "scenario simulation runs",
  telemetry_stream: "sensor readings",
  work_order_parts_edge: "parts each work order needs",
};

/* Used by the copy rewrite. Keys are lowercased as they appear on screen. */
var JARGON = {
  entrypoint: "agent you can talk to",
  hitl: "needs your sign-off",
  "human-in-the-loop": "needs your sign-off",
  swarm: "agent team",
  traversal: "connection trace",
  "pattern a": "team agent",
  "pattern b": "specialist agent",
  "value branch": "where the money is",
  "apqc code": "standard process area",
  provenance: "where this came from",
  p90: "the best day",
  median: "the ordinary day",
  node: "machine",
  edge: "link",
  "blast radius": "what else stops",
};

function bareTable(id) {
  if (!id) return "";
  return String(id).replace(/`/g, "").replace(/^mining_data\./, "");
}

function plainTable(id) {
  var bare = bareTable(id);
  return TABLES[bare] || bare;
}

function plainTool(id) {
  return TOOLS[id] || String(id || "");
}

function plainToolAbility(id) {
  return TOOL_ABILITY[id] || plainTool(id);
}

/* The article a table phrase needs from whatever frames it, and the one place
 * that decides. Most phrases here are noun phrases and read as "the machine
 * register". A few are relative clauses — they begin with which/who/what and
 * are already complete — and "the which parts each supplier quoted" is not
 * English. The phrases themselves carry no article so that a frame which wants
 * none ("Show me who drove what") can have none. */
function articleFor(phrase) {
  return /^(?:which|who|what)\b/i.test(String(phrase || "")) ? "" : "the ";
}

function plainTraversal(id) {
  return TRAVERSALS[id] || String(id || "");
}

function plainJargon(term) {
  var key = String(term || "").toLowerCase();
  return JARGON[key] || String(term || "");
}

/* Prose the screens print but did not write.
 *
 * A persona's accountable_for is a paragraph out of the catalogue, and three
 * screens print it whole: the cockpit under each role, the role page as its
 * lede, and the sign-off sheet under "Who is accountable". It was written by
 * the people who built the estate, so it says "must approve or decline HITL
 * prompts". Every sentence around it now says "needs your sign-off", and one
 * paragraph in the reader's own screen still using the acronym undoes the
 * lesson the rest of the page is teaching.
 *
 * The rule is a phrase substitution and not a word one, because "HITL" is never
 * alone: it qualifies a noun, and which noun decides what reads well in its
 * place. Longest first, so "HITL approval request" is not left as "sign-off
 * request request". The list is deliberately short — every entry was checked
 * against the actual occurrences in the catalogue rather than imagined.
 *
 * What this is NOT applied to is a quotation. A journey summary and a pain
 * point are printed with a source line against them, and prose carrying a
 * citation has to be the prose at that line. Where those still use the estate's
 * words, the fix is to the document, not to a regex on the way to the screen.
 */
var PROSE = [
  [/\bHITL approval (?:request|prompt|step)s?\b/gi, "sign-off request"],
  [/\bHITL (?:approval )?prompts\b/gi, "sign-off requests"],
  [/\bHITL (?:approval )?prompt\b/gi, "sign-off request"],
  [/\bHITL approver\b/gi, "sign-off authority"],
  [/\bHITL approvals?\b/gi, "sign-off"],
  [/\bHITL\b/gi, "sign-off"],
];

function plainProse(text) {
  var out = String(text || "");
  for (var i = 0; i < PROSE.length; i++) {
    out = out.replace(PROSE[i][0], PROSE[i][1]);
  }
  return out;
}

/* The observed bq_query argument is a literal SELECT naming its table in
 * backticks. Only the first qualified name is taken: a join names two, and the
 * first is the one the query is about. */
function tableFromSql(sql) {
  var found = /mining_data\.([a-z0-9_]+)/i.exec(String(sql || ""));
  return found ? found[1] : "";
}

/* The noun a call is about, if the arguments carry one. Any string argument may
 * hold the SQL, and any argument may name a traversal, because the argument
 * names differ by tool and guessing a key is how this breaks silently. */
function _noun(name, args) {
  var values = Object.keys(args || {}).map(function (k) { return args[k]; });
  var i;
  if (name === "bq_query") {
    for (i = 0; i < values.length; i++) {
      var table = tableFromSql(values[i]);
      if (table) return { kind: "table", plain: plainTable(table) };
    }
  }
  for (i = 0; i < values.length; i++) {
    if (typeof values[i] === "string" && TRAVERSALS[values[i]]) {
      return { kind: "traversal", plain: TRAVERSALS[values[i]] };
    }
  }
  return null;
}

/* A traversal phrase is a clause and never takes an article; a table phrase
 * takes whichever articleFor says. */
function _framed(verb, noun) {
  var article = noun.kind === "table" ? articleFor(noun.plain) : "";
  return verb + " " + article + noun.plain;
}

function callLine(name, args) {
  var noun = _noun(name, args);
  if (noun && TOOL_VERB[name]) return _framed(TOOL_VERB[name], noun);
  return TOOL_DOING[name] || String(name || "");
}

function failLine(name, args) {
  var noun = _noun(name, args);
  var head = noun && TOOL_FAILED[name]
    ? _framed(TOOL_FAILED[name], noun)
    : "Couldn't finish " + (TOOLS[name] || String(name || ""));
  return head + " — that lookup failed.";
}

/* The honesty check. Every tool, traversal and table the catalogue declares
 * must have a plain phrase, or the activity log will print an identifier at a
 * reader who came here to avoid identifiers. */
function unmapped(DATA) {
  var tables = {}, tools = {}, traversals = {};
  (DATA.catalog.agents || []).forEach(function (agent) {
    (agent.source_tables || []).forEach(function (t) {
      var bare = bareTable(t);
      if (!TABLES[bare]) tables[bare] = true;
    });
    (agent.tools || []).forEach(function (t) { if (!TOOLS[t]) tools[t] = true; });
    (agent.traversals || []).forEach(function (t) {
      if (!TRAVERSALS[t]) traversals[t] = true;
    });
  });
  return {
    tables: Object.keys(tables).sort(),
    tools: Object.keys(tools).sort(),
    traversals: Object.keys(traversals).sort(),
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    TOOLS, TOOL_ABILITY, TRAVERSALS, TABLES, JARGON,
    bareTable, plainTable, plainTool, plainToolAbility, plainTraversal, plainJargon,
    plainProse,
    articleFor, tableFromSql, callLine, failLine, unmapped,
  };
}
